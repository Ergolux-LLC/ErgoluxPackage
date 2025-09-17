from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, EmailSignup
import os
import logging
import string
import random
import httpx
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError

DATABASE_URL = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("account_service")

router = APIRouter()

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

import base64

def generate_code(length=8):
	# Generate a random url-safe code
	random_bytes = os.urandom(length)
	code = base64.urlsafe_b64encode(random_bytes).decode("utf-8").rstrip("=")
	return code[:length]


class SignupRequest(BaseModel):
	"""
	Request body for signing up a new account.
	- email: The email address to sign up.
	- workspace_id: Optional workspace ID to associate with the signup.
	"""
	email: EmailStr
	workspace_id: int | None = None


class ConfirmRequest(BaseModel):
	"""
	Request body for confirming a signup code.
	- code: The code received by email.
	"""
	code: str




@router.post(
	"/signup",
	summary="Sign up a new account",
	response_description="Signup result with code or error",
	tags=["Account"],
	response_model=dict,
	description="""
	Accepts an email address and optional workspace ID. Returns status and email_confirmation_status. In dev mode, does not hit the DB.
	"""
)
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
	logger.info(f"Signup attempt: {data}")
	
	# Validate email
	try:
		valid = validate_email(data.email)
		email = valid.email
	except EmailNotValidError as e:
		logger.warning(f"Invalid email: {data.email} - {str(e)}")
		signup = EmailSignup(email=data.email, code="", status="invalid", is_valid=False, last_email_result=str(e), workspace_id=data.workspace_id)
		db.add(signup)
		db.commit()
		return {
			"success": False,
			"status": "invalid_email",
			"message": f"Invalid email address: {data.email}. Reason: {str(e)}",
			"email_confirmation_status": "invalid"
		}

	signup = db.query(EmailSignup).filter(EmailSignup.email == email).first()
	if signup:
		if getattr(signup, 'status', None) == "confirmed":
			logger.info(f"Email already confirmed: {email}")
			return {
				"success": True,
				"status": "already_confirmed",
				"message": f"Email {email} is already confirmed.",
				"email_confirmation_status": "already_confirmed"
			}
		else:
			logger.info(f"Email already exists: {email}, not confirmed")
			return {
				"success": True,
				"status": "pending",
				"message": f"Email {email} is already registered but not confirmed.",
				"email_confirmation_status": "pending"
			}
	code = generate_code()
	signup = EmailSignup(email=email, code=code, status="pending", workspace_id=data.workspace_id)
	db.add(signup)
	try:
		db.commit()
	except IntegrityError as e:
		db.rollback()
		logger.error(f"IntegrityError during signup for {email}: {str(e)}")
		return {
			"success": False,
			"status": "db_error",
			"message": f"Database error during signup for {email}: {str(e)}",
			"email_confirmation_status": "pending"
		}
	logger.info(f"Signup created: {email} with code {code}")
	# TODO: Integrate with email sending API here
	setattr(signup, 'last_email_result', "pending_email_api")
	db.commit()
	return {
		"success": True,
		"status": "ok",
		"message": f"Signup successful for {email}. Confirmation code generated.",
		"email_confirmation_status": "pending"
	}

	# Catch-all (should never hit)
	return {
		"success": False,
		"status": "unknown_error",
		"message": "An unknown error occurred during signup.",
		"email_confirmation_status": "error"
	}



# New route to get email by code
@router.get(
	"/email-for-code/{code}",
	summary="Get email for a signup code",
	response_description="Email address for the provided code",
	tags=["Account"],
	response_model=dict,
	description="""
	Internal endpoint. Provide a code to retrieve the associated email address. Returns success and the email if found, otherwise success false and email null. Useful for debugging and internal lookups.
	"""
)
def get_email_for_code(code: str, db: Session = Depends(get_db)):
	logger.info(f"Email retrieval for code: {code}")
	signup = db.query(EmailSignup).filter(EmailSignup.code == code).first()
	if not signup:
		logger.info(f"No email found for code: {code}")
		return {"success": False, "email": None}
	return {"success": True, "email": signup.email}

## Email sending emulation removed. Integrate with real email API here in the future.


@router.post(
	"/confirm",
	summary="Confirm a signup code",
	response_description="Confirmation result",
	tags=["Account"],
	response_model=dict,
	description="""
	Provide a code to confirm a signup. If valid, marks the signup as confirmed and returns the associated email and workspace_id. In dev mode, does not hit the DB.
	"""
)
def confirm_code(data: ConfirmRequest, db: Session = Depends(get_db)):
	logger.info(f"Code confirmation attempt: {data.code}")
	
	# Normal DB flow
	signup = db.query(EmailSignup).filter(EmailSignup.code == data.code).first()
	if not signup:
		logger.warning(f"Invalid code: {data.code}")
		return {
			"success": False,
			"status": "invalid_code",
			"message": f"No signup found for code: {data.code}",
			"email": None,
			"workspace_id": None
		}
	setattr(signup, 'status', "confirmed")
	db.commit()
	logger.info(f"Code confirmed for email: {getattr(signup, 'email', None)}")
	return {
		"success": True,
		"status": "ok",
		"message": f"Code confirmed for email: {getattr(signup, 'email', None)}",
		"email": getattr(signup, 'email', None),
		"workspace_id": getattr(signup, 'workspace_id', None)
	}

@router.get(
	"/status/{email}",
	summary="Get signup status for an email",
	response_description="Signup status and details",
	tags=["Account"],
	response_model=dict,
	description="""
	Returns the status, last email result, and validity for a given email address. If not found, returns status not_found. Logs all lookups.
	"""
)
def email_status(email: str, db: Session = Depends(get_db)):
	logger.info(f"Status check for email: {email}")
	signup = db.query(EmailSignup).filter(EmailSignup.email == email).first()
	if not signup:
		logger.info(f"No record for email: {email}")
		return {
			"success": False,
			"status": "not_found",
			"message": f"No signup found for email: {email}"
		}
	return {
		"success": True,
		"status": getattr(signup, 'status', None),
		"last_email_result": getattr(signup, 'last_email_result', None),
		"is_valid": getattr(signup, 'is_valid', None),
		"message": f"Signup status for {email} is {getattr(signup, 'status', None)}."
	}

@router.get(
	"/emails",
	summary="List all email signups",
	response_description="List of all signups and their details",
	tags=["Account"],
	response_model=list,
	description="""
	Returns a list of all email signups, including email, status, validity, last email result, and workspace_id. Internal use only. Logs all accesses.
	"""
)
def list_emails(db: Session = Depends(get_db)):
	logger.info("Listing all emails")
	signups = db.query(EmailSignup).all()
	return [
		{
			"email": s.email,
			"status": s.status,
			"is_valid": s.is_valid,
			"last_email_result": s.last_email_result,
			"workspace_id": s.workspace_id
		} for s in signups
	]

# --- Development-only endpoint to get signup code for an email ---
def dev_get_code(email: str, db: Session = Depends(get_db)):
	"""
	Development-only endpoint. Returns the signup code for a given email address. Do not enable in production.
	"""
	signup = db.query(EmailSignup).filter(EmailSignup.email == email).first()
	if not signup:
		return {"success": False, "code": None}
	return {"success": True, "code": signup.code}

# Register the dev route only if DEV_MODE is set
if os.getenv("DEV_MODE") == "true":
	router.add_api_route(
		"/dev/get-code/{email}",
		dev_get_code,
		methods=["GET"],
		summary="(DEV ONLY) Get signup code for email",
		description="Development-only endpoint. Returns the signup code for a given email address. Do not enable in production.",
		tags=["Development"],
		response_model=dict,
	)
