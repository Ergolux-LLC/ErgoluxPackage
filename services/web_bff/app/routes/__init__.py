from fastapi import FastAPI
from .account_setup import router as account_setup_router

app = FastAPI()

# Include the account setup router in the main application
app.include_router(account_setup_router, prefix="/account-setup")
