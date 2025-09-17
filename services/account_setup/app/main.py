from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
import os

load_dotenv()

app = FastAPI()

# Import routes (skeleton)
from routes import router
app.include_router(router)

@app.get("/status")
def status():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
