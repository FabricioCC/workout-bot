import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)

def save_set(exercise: str, weight_kg: float, series: int, reps: int) -> str:
    # Get or create today's workout
    from datetime import date
    today = date.today().isoformat()

    workout = supabase.table("workouts").select("id").eq("workout_date", today).execute()

    if workout.data:
        workout_id = workout.data[0]["id"]
    else:
        new_workout = supabase.table("workouts").insert({"workout_date": today}).execute()
        workout_id = new_workout.data[0]["id"]

    # Save the set
    supabase.table("sets").insert({
        "workout_id": workout_id,
        "exercise": exercise,
        "weight_kg": weight_kg,
        "series": series,
        "reps": reps,
    }).execute()

    # Check previous session for comparison
    previous = (
        supabase.table("sets")
        .select("weight_kg")
        .eq("exercise", exercise)
        .neq("workout_id", workout_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    msg = f"✅ Logged: {exercise} {weight_kg}kg × {series}×{reps}"

    if previous.data:
        prev_weight = float(previous.data[0]["weight_kg"])
        diff = round(float(weight_kg) - prev_weight, 1)
        if diff > 0:
            msg += f"\n📈 +{diff}kg from last time ({prev_weight}kg)"
        elif diff < 0:
            msg += f"\n📉 {diff}kg from last time ({prev_weight}kg)"
        else:
            msg += f"\n➡️ Same weight as last time"

    return msg

def get_report(muscle_group: str = None, period: str = None) -> str:
    from datetime import date, timedelta

    query = supabase.table("sets").select(
        "exercise, weight_kg, series, reps, workouts(workout_date)"
    )

    if period == "week":
        cutoff = (date.today() - timedelta(days=7)).isoformat()
        query = query.gte("created_at", cutoff)
    elif period == "month":
        cutoff = date.today().replace(day=1).isoformat()
        query = query.gte("created_at", cutoff)

    result = query.order("created_at", desc=True).limit(100).execute()

    if not result.data:
        return "No workouts logged yet. Send your first one!"

    # Group by date
    workouts = {}
    for row in result.data:
        date_str = row["workouts"]["workout_date"]
        if date_str not in workouts:
            workouts[date_str] = []
        workouts[date_str].append(row)

    lines = ["📋 *Workout history:*\n"]
    for workout_date, sets in sorted(workouts.items(), reverse=True):
        lines.append(f"📅 *{workout_date}*")
        for s in sets:
            weight = f"{s['weight_kg']}kg " if s["weight_kg"] else ""
            series_reps = f"{s['series']}×{s['reps']}" if s["series"] and s["reps"] else ""
            lines.append(f"  • {s['exercise'].title()} {weight}{series_reps}")
        lines.append("")  # linha em branco entre treinos

    return "\n".join(lines)

def save_goal(exercise: str, target_weight_kg: float, deadline: str = None) -> str:
    supabase.table("goals").insert({
        "exercise": exercise,
        "target_weight_kg": target_weight_kg,
        "deadline": deadline,
    }).execute()

    msg = f"🎯 Goal set: {exercise.title()} → {target_weight_kg}kg"
    if deadline:
        msg += f" by {deadline}"
    return msg


def get_goals() -> str:
    goals = supabase.table("goals").select("*").eq("achieved", False).execute()

    if not goals.data:
        return "No goals set yet. Try: 'I want to bench press 100kg by December'"

    lines = ["🎯 *Your goals:*\n"]
    for goal in goals.data:
        exercise = goal["exercise"]
        target = goal["target_weight_kg"]

        # Current weight for this exercise
        current = (
            supabase.table("sets")
            .select("weight_kg")
            .eq("exercise", exercise)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if current.data and current.data[0]["weight_kg"]:
            current_weight = float(current.data[0]["weight_kg"])
            pct = round((current_weight / float(target)) * 100)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            lines.append(f"*{exercise.title()}*")
            lines.append(f"{bar} {pct}%")
            lines.append(f"Now: {current_weight}kg → Target: {target}kg")
            if goal.get("deadline"):
                lines.append(f"Deadline: {goal['deadline']}")
        else:
            lines.append(f"*{exercise.title()}*: target {target}kg")
            if goal.get("deadline"):
                lines.append(f"Deadline: {goal['deadline']}")

        lines.append("")

    return "\n".join(lines)