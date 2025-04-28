import uvicorn
from fastapi import FastAPI
from controllers.webhook_controller import router as webhook_router
from dotenv import load_dotenv
import os

load_dotenv()  # Load env variables from .env

# Environment Variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 3006))

app = FastAPI(
    title="WhatsApp Webhook Service",
    version="1.0.0",
)

app.include_router(webhook_router)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=True)
