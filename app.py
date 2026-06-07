import streamlit as st
import json
import os
from datetime import datetime
import uuid

st.set_page_config(page_title="Marketplace", page_icon="🏪", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white; text-align: center;">
    <h1>🏪 Local Marketplace</h1>
    <p>List items for sale • Chat with buyers</p>
</div>
""", unsafe_allow_html=True)

# Files
LISTINGS_FILE = 'listings.json'
CHATS_FILE = 'chats.json'

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

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]
if 'username' not in st.session_state:
    st.session_state.username = f"User_{st.session_state.user_id[:4]}"

# Sidebar
st.sidebar.title("Menu")
username = st.sidebar.text_input("Your name", value=st.session_state.username)
st.session_state.username = username if username else "Guest"

menu = st.sidebar.radio("Go to", ["Browse Items", "Sell Item", "My Items", "My Chats"])

# SELL ITEM
if menu == "Sell Item":
    st.header("List an item")
    
    with st.form("sell"):
        title = st.text_input("Item name")
        price = st.number_input("Price (Rs.)", min_value=0, step=100)
        location = st.text_input("Location")
        phone = st.text_input("Phone number")
        desc = st.text_area("Description")
        submitted = st.form_submit_button("Post")
        
        if submitted and title and price and location and phone:
            listings = load_listings()
            listings.insert(0, {
                "id": str(uuid.uuid4())[:8],
                "title": title,
                "price": int(price),
                "location": location,
                "phone": phone,
                "desc": desc,
                "seller_id": st.session_state.user_id,
                "seller_name": st.session_state.username,
                "status": "available",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            save_listings(listings)
            st.success("Posted!")

# BROWSE ITEMS
elif menu == "Browse Items":
    st.header("Items for sale")
    
    listings = load_listings()
    available = [x for x in listings if x['status'] == 'available']
    
    if not available:
        st.info("No items yet. Sell something!")
    else:
        for item in available:
            with st.container():
                st.markdown(f"### {item['title']}")
                st.markdown(f"**Rs. {item['price']:,}** | 📍 {item['location']}")
                st.markdown(f"{item['desc']}")
                st.caption(f"Posted by {item['seller_name']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Message", key=f"msg_{item['id']}"):
                        st.session_state.chat_item = item
                        st.session_state.go_to_chat = True
                with col2:
                    if st.button(f"Show phone", key=f"phone_{item['id']}"):
                        st.info(f"📞 {item['phone']}")
                st.divider()

# MY ITEMS
elif menu == "My Items":
    st.header("Your listings")
    
    listings = load_listings()
    my = [x for x in listings if x['seller_id'] == st.session_state.user_id]
    
    if not my:
        st.info("No items yet")
    else:
        for item in my:
            col1, col2, col3 = st.columns([3,1,1])
            col1.markdown(f"**{item['title']}** - Rs. {item['price']} - {item['status']}")
            if col2.button(f"Sold", key=f"sold_{item['id']}"):
                listings = load_listings()
                for l in listings:
                    if l['id'] == item['id']:
                        l['status'] = 'sold'
                save_listings(listings)
                st.rerun()
            if col3.button(f"Delete", key=f"del_{item['id']}"):
                listings = load_listings()
                listings = [l for l in listings if l['id'] != item['id']]
                save_listings(listings)
                st.rerun()

# MY CHATS
elif menu == "My Chats":
    st.header("Messages")
    
    chats = load_chats()
    my_chats = {}
    
    for chat_id, data in chats.items():
        if st.session_state.user_id in [data.get('buyer_id'), data.get('seller_id')]:
            my_chats[chat_id] = data
    
    if not my_chats:
        st.info("No messages yet")
    else:
        chat_ids = list(my_chats.keys())
        chat_labels = []
        for cid in chat_ids:
            data = my_chats[cid]
            other = data.get('buyer_name') if data.get('seller_id') == st.session_state.user_id else data.get('seller_name')
            chat_labels.append(f"{data.get('item_title', 'Item')} - with {other}")
        
        selected = st.selectbox("Select chat", range(len(chat_labels)), format_func=lambda x: chat_labels[x])
        
        if selected is not None:
            chat_id = chat_ids[selected]
            chat_data = my_chats[chat_id]
            
            for msg in chat_data.get('messages', []):
                if msg['sender_id'] == st.session_state.user_id:
                    st.markdown(f"<div style='text-align:right; background:#0084ff; color:white; padding:10px; border-radius:15px; margin:5px'>{msg['text']}<br><small>{msg['time']}</small></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:left; background:#e4e6eb; padding:10px; border-radius:15px; margin:5px'><b>{msg['sender_name']}:</b> {msg['text']}<br><small>{msg['time']}</small></div>", unsafe_allow_html=True)
            
            new_msg = st.text_input("Type message")
            if st.button("Send"):
                if new_msg:
                    chats = load_chats()
                    if 'messages' not in chats[chat_id]:
                        chats[chat_id]['messages'] = []
                    chats[chat_id]['messages'].append({
                        "sender_id": st.session_state.user_id,
                        "sender_name": st.session_state.username,
                        "text": new_msg,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    save_chats(chats)
                    st.rerun()

# Handle message button
if 'go_to_chat' in st.session_state and st.session_state.go_to_chat:
    item = st.session_state.chat_item
    chats = load_chats()
    chat_id = f"{item['seller_id']}_{st.session_state.user_id}_{item['id']}"
    
    if chat_id not in chats:
        chats[chat_id] = {
            "item_id": item['id'],
            "item_title": item['title'],
            "seller_id": item['seller_id'],
            "seller_name": item['seller_name'],
            "buyer_id": st.session_state.user_id,
            "buyer_name": st.session_state.username,
            "messages": []
        }
        save_chats(chats)
    
    st.session_state.go_to_chat = False
    st.session_state.menu = "My Chats"
    st.rerun()
