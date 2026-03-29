from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Live data (editable)
mcx = {
    "gold": 72450,
    "silver": 88900
}

premium = {
    "gold": {"rtgs": 1200, "retail": 1800, "bulk": 900},
    "silver": {"rtgs": 2500, "retail": 3200, "bulk": 1800}
}

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
def update_rates(data: dict):
    global mcx, premium

    mcx["gold"] = data["gold"]
    mcx["silver"] = data["silver"]

    premium["gold"] = data["gold_premium"]
    premium["silver"] = data["silver_premium"]

    return {"status": "updated"}