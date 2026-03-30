from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import json

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_API_KEY = "indiaismycountry143"

FILE = "data.json"

# Default data (fallback)
mcx = {
    "gold": 72450,
    "silver": 88900
}

premium = {
    "gold": {"rtgs": 1200, "retail": 1800, "bulk": 900},
    "silver": {"rtgs": 2500, "retail": 3200, "bulk": 1800}
}

# Load saved data
def load_data():
    global mcx, premium
    try:
        with open(FILE, "r") as f:
            data = json.load(f)
            mcx = data["mcx"]
            premium = data["premium"]
            print("Data loaded")
    except:
        print("No saved data found")

load_data()

@app.get("/rates")
def get_rates():
    gold = mcx["gold"]
    silver = mcx["silver"]

    return {
        "gold": {
            "mcx": gold,
            "rtgs": gold + premium["gold"]["rtgs"],
            "retail": gold + premium["gold"]["retail"],
            "bulk": gold + premium["gold"]["bulk"]
        },
        "silver": {
            "mcx": silver,
            "rtgs": silver + premium["silver"]["rtgs"],
            "retail": silver + premium["silver"]["retail"],
            "bulk": silver + premium["silver"]["bulk"]
        },
        "lastUpdated": time.strftime("%H:%M:%S")
    }

@app.post("/update")
def update_rates(data: dict, x_api_key: str = Header(None)):
    global mcx, premium

    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    mcx["gold"] = data["gold"]
    mcx["silver"] = data["silver"]

    premium["gold"] = data["gold_premium"]
    premium["silver"] = data["silver_premium"]

    # ✅ SAVE DATA HERE (correct place)
    with open(FILE, "w") as f:
        json.dump({"mcx": mcx, "premium": premium}, f)

    return {"status": "updated"}
