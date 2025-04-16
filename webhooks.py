import os 
import logging
from fastapi import FastAPI
from dotenv import load_dotenv  # ✅ Load .env
from controllers.webhook_controller import WebhookController

# Load environment variables
load_dotenv()

# Configure Logging Stage
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 3006))

# FastAPI instance
app = FastAPI()
print("FASTAPI APP LOADED ✅")

@app.get("/")
async def home():
    return {"message": "service whatsapp"}

from fastapi import Query

# Load Webhook Controller
webhook_controller = WebhookController()

@app.get("/webhook")
async def webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    return await webhook_controller.verify(hub_mode, hub_challenge, hub_verify_token)

@app.post("/webhook")
async def webhook(payload: dict):
    return await webhook_controller.handle_webhook(payload)

@app.get("/health")
async def health_check():
    return {"message": "service running..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
