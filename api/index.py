from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os
import uuid
from datetime import datetime
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# File paths
LISTINGS_FILE = '/tmp/listings.json'
CHATS_FILE = '/tmp/chats.json'

# Initialize files
if not os.path.exists(LISTINGS_FILE):
    with open(LISTINGS_FILE, 'w') as f:
        json.dump([], f)
if not os.path.exists(CHATS_FILE):
    with open(CHATS_FILE, 'w') as f:
        json.dump({}, f)

def load_listings():
    with open(LISTINGS_FILE, 'r') as f:
        return json.load(f)

def save_listings(listings):
    with open(LISTINGS_FILE, 'w') as f:
        json.dump(listings, f, indent=2)

def load_chats():
    with open(CHATS_FILE, 'r') as f:
        return json.load(f)

def save_chats(chats):
    with open(CHATS_FILE, 'w') as f:
        json.dump(chats, f, indent=2)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/listings")
async def get_listings():
    listings = load_listings()
    # Return only available items (not deleted/sold)
    available = [l for l in listings if l.get('status') == 'available']
    return available

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
    listings = load_listings()
    new_listing = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "price": price,
        "category": category,
        "location": location,
        "phone": phone,
        "description": description,
        "seller_name": seller_name,
        "seller_id": str(uuid.uuid4())[:8],
        "status": "available",
        "created_at": datetime.now().isoformat()
    }
    listings.append(new_listing)
    save_listings(listings)
    return {"success": True, "id": new_listing["id"]}

@app.delete("/api/listings/{item_id}")
async def delete_listing(item_id: str, seller_id: str):
    listings = load_listings()
    for item in listings:
        if item['id'] == item_id and item['seller_id'] == seller_id:
            item['status'] = 'deleted'
            save_listings(listings)
            return {"success": True}
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/api/chats/{user_id}")
async def get_user_chats(user_id: str):
    chats = load_chats()
    user_chats = {}
    for chat_id, chat in chats.items():
        if user_id in [chat.get('buyer_id'), chat.get('seller_id')]:
            user_chats[chat_id] = chat
    return user_chats

@app.post("/api/chats")
async def create_or_get_chat(
    item_id: str = Form(...),
    buyer_id: str = Form(...),
    buyer_name: str = Form(...),
    seller_id: str = Form(...),
    seller_name: str = Form(...),
    item_title: str = Form(...)
):
    chats = load_chats()
    chat_id = f"{item_id}_{buyer_id}"
    
    if chat_id not in chats:
        chats[chat_id] = {
            "id": chat_id,
            "item_id": item_id,
            "item_title": item_title,
            "buyer_id": buyer_id,
            "buyer_name": buyer_name,
            "seller_id": seller_id,
            "seller_name": seller_name,
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        save_chats(chats)
    
    return {"chat_id": chat_id, "chat": chats[chat_id]}

@app.post("/api/chats/{chat_id}/messages")
async def send_message(
    chat_id: str,
    sender_id: str = Form(...),
    sender_name: str = Form(...),
    message: str = Form(...)
):
    chats = load_chats()
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    new_message = {
        "id": str(uuid.uuid4())[:6],
        "sender_id": sender_id,
        "sender_name": sender_name,
        "message": message,
        "time": datetime.now().strftime("%I:%M %p"),
        "date": datetime.now().isoformat()
    }
    chats[chat_id]["messages"].append(new_message)
    save_chats(chats)
    return {"success": True, "message": new_message}

handler = app
