from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
return {"message": "Marketplace working on Vercel"}


handler = app
