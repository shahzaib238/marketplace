from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client
import os
import uuid

app = FastAPI()

templates = Jinja2Templates(directory="templates")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
SUPABASE_URL,
SUPABASE_KEY
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
return templates.TemplateResponse(
"index.html",
{"request": request}
)

@app.get("/api/listings")
async def get_listings():
response = (
supabase.table("listings")
.select("*")
.eq("status", "available")
.execute()
)

```
return response.data
```

@app.post("/api/listings")
async def create_listing(
title: str = Form(...),
price: float = Form(...),
category: str = Form(...),
location: str = Form(...),
phone: str = Form(...),
description: str = Form(...),
seller_name: str = Form(...)
):
listing = {
"title": title,
"price": price,
"category": category,
"location": location,
"phone": phone,
"description": description,
"seller_name": seller_name,
"seller_id": str(uuid.uuid4())[:8],
"status": "available"
}

```
supabase.table("listings").insert(
    listing
).execute()

return {
    "success": True
}
```

@app.get("/health")
async def health():
return {
"status": "ok"
}

handler = app
