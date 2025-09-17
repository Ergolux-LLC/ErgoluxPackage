import os
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
import base64


# Load environment variables from .env
load_dotenv()

# Initialize Argon2 hasher
_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return _hasher.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its Argon2 hash."""
    try:
        return _hasher.verify(hashed, password)
    except VerifyMismatchError:
        return False

def generate_token(byte_length: int = 32) -> str:
    """Generate a secure URL-safe token with exact byte entropy."""
    token = secrets.token_bytes(byte_length)
    return base64.urlsafe_b64encode(token).rstrip(b'=').decode('ascii')