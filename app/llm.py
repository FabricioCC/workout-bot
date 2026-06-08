import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a personal workout tracking assistant.
Analyze the user's message and respond ONLY with valid JSON, no extra text.

JSON structure:
{
  "intent": "<register_workout | query_report | set_goal | other>",
  "data": { ... },
  "reply": "<friendly response to the user>"
}

Intents:
- register_workout: user is logging one or more exercises
  data: { "exercises": [ { "exercise": "name", "weight_kg": 0.0, "series": 0, "reps": 0 } ] }

- query_report: user wants to see history or progress
  data: { "muscle_group": "chest|back|legs|shoulders|arms|null", "period": "week|month|null" }

- set_goal: user wants to set a goal
  data: { "exercise": "name", "target_weight_kg": 0.0, "deadline": "YYYY-MM-DD|null" }

- other: anything else
  data: {}

Rules:
- Always use a list in "exercises", even if there is only one exercise
- Normalize exercise names to lowercase english (e.g. "bench press", "squat")
- If weight is not mentioned, use null
- Keep the reply short and friendly
- If key info is missing (e.g. weight), ask for it in the reply and use intent "other"
"""

def parse_message(message: str) -> dict:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\nUser message: {message}",
    )

    text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    return json.loads(text)