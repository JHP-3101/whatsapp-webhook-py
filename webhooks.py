import os 
import logging
from fastapi import FastAPI, Request, HTTPException
import httpx
from pydantic import BaseModel

from services.whatsapp_service import send_message, send_menu
from controllers.webhook_controller import webhook_verifier_handler, webhook_handler

# Configure Logging Stage
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 3006))

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "service whatsapp"}

@app.get("/webhook")
async def webhook_verify(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    return await webhook_verifier_handler(hub_mode, hub_challenge, hub_verify_token)

@app.post("/webhook")
async def webhook(payload: dict):
    return await webhook_handler(payload)

@app.get("/health")
async def health_check():
    return {"message": "service running..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
