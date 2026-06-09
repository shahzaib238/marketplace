from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def home():
    return {"status": "working"}

handler = app
