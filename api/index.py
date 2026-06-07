from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
import os
import uuid
from datetime import datetime

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# File paths
LISTINGS_FILE = 'listings.json'

if not os.path.exists(LISTINGS_FILE):
    with open(LISTINGS_FILE, 'w') as f:
        json.dump([], f)

def load_listings():
    with open(LISTINGS_FILE, 'r') as f:
        return json.load(f)

def save_listings(listings):
    with open(LISTINGS_FILE, 'w') as f:
        json.dump(listings, f, indent=2)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    listings = load_listings()
    available = [l for l in listings if l.get('status') == 'available']
    return templates.TemplateResponse("index.html", {
        "request": request,
        "listings": available
    })

@app.post("/add-item")
async def add_item(
    title: str = Form(...),
    price: float = Form(...),
    location: str = Form(...),
    phone: str = Form(...),
    description: str = Form(...),
    seller_name: str = Form(...)
):
    listings = load_listings()
    new_item = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "price": price,
        "location": location,
        "phone": phone,
        "description": description,
        "seller_name": seller_name,
        "status": "available",
        "created_at": datetime.now().isoformat()
    }
    listings.append(new_item)
    save_listings(listings)
    return {"status": "success", "id": new_item["id"]}

@app.get("/api/listings")
async def get_listings():
    listings = load_listings()
    return [l for l in listings if l.get('status') == 'available']
