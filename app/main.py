from fastapi import FastAPI, Form, Response
from app.handlers import handle_message
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

twilio = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN"),
)

@app.get("/")
def health():
    return {"status": "ok", "msg": "Workout Bot is running!"}

@app.post("/webhook")
async def webhook(From: str = Form(...), Body: str = Form(...)):
    reply = handle_message(Body)

    twilio.messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
        to=From,
        body=reply,
    )

    # Twilio expects an empty 200 response
    return Response(content="", media_type="text/xml")

@app.get("/debug")
def debug():
    return {
        "supabase_url": os.getenv("SUPABASE_URL", "NOT FOUND"),
        "gemini": "ok" if os.getenv("GEMINI_API_KEY") else "NOT FOUND",
        "twilio": "ok" if os.getenv("TWILIO_ACCOUNT_SID") else "NOT FOUND",
    }