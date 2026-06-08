from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
return {"message": "Marketplace is working"}

handler = app
