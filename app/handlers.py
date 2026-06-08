from app.llm import parse_message
from app.database import save_set, get_report

def handle_message(text: str) -> str:
    result = parse_message(text)
    intent = result["intent"]
    data = result["data"]

    if intent == "register_workout":
        replies = []
        for item in data["exercises"]:
            reply = save_set(
                exercise=item["exercise"],
                weight_kg=item.get("weight_kg"),
                series=item.get("series"),
                reps=item.get("reps"),
            )
            replies.append(reply)
        return "\n\n".join(replies)

    elif intent == "query_report":
        return get_report(
            muscle_group=data.get("muscle_group"),
            period=data.get("period"),
        )

    elif intent == "set_goal":
        return "🎯 Goals coming soon!"

    else:
        return result.get("reply", "I didn't understand that. Try: 'Did bench press 30kg, 4x10'")