from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok", "msg": "Workout Bot running!"}