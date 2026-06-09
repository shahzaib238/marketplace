from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def home():
return {
"status": "running",
"supabase_url_exists": bool(os.getenv("SUPABASE_URL")),
"supabase_key_exists": bool(os.getenv("SUPABASE_KEY"))
}

handler = app
