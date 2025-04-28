import uvicorn
from fastapi import FastAPI
from controllers.webhook_controller import router as webhook_router
from dotenv import load_dotenv
import os

load_dotenv()  # Load env variables from .env

app = FastAPI(
    title="WhatsApp Webhook Service",
    version="1.0.0",
)

app.include_router(webhook_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3006, reload=True)
