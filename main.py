from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONFIG
# =========================
ADMIN_API_KEY = "indiaismycountry143"
FILE = "data.json"

# =========================
# DEFAULT DATA
# =========================
mcx = {
    "gold": 72450,
    "silver": 88900
}

premium = {
    "gold": {"rtgs": 1200, "retail": 1800, "bulk": 900},
    "silver": {"rtgs": 2500, "retail": 3200, "bulk": 1800}
}

# 🔥 FULL CONTROL VISIBILITY
visibility = {
    "gold": {"rtgs": True, "retail": True, "bulk": True},
    "silver": {"rtgs": True, "retail": True, "bulk": True}
}

# 🔥 CACHE
last_fetch_time = 0
CACHE_DURATION = 15


# =========================
# SCRAPER
# =========================
def fetch_mcx_prices():
    try:
        url = "https://mcxlive.org/"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.find_all("tr")

        gold = None
        silver = None

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            name = cols[0].get_text(strip=True).lower()
            price_text = cols[1].get_text(strip=True).replace(",", "")

            try:
                price = float(price_text)
            except:
                continue

            if "gold" in name and "mini" not in name and gold is None:
                gold = price

            if "silver" in name and silver is None:
                silver = price

        if gold is not None and silver is not None:
            return int(gold), int(silver)

        return None, None

    except Exception as e:
        print("Scraping error:", e)
        return None, None


# =========================
# LOAD DATA
# =========================
def load_data():
    global mcx, premium, visibility
    try:
        with open(FILE, "r") as f:
            data = json.load(f)
            mcx = data.get("mcx", mcx)
            premium = data.get("premium", premium)
            visibility = data.get("visibility", visibility)
            print("Data loaded")
    except:
        print("No saved data found")

load_data()


# =========================
# GET RATES
# =========================
@app.get("/rates")
def get_rates():
    global mcx, last_fetch_time

    current_time = time.time()

    # Cache-controlled scraping
    if current_time - last_fetch_time > CACHE_DURATION:
        g, s = fetch_mcx_prices()

        if g is not None and s is not None:
            mcx["gold"] = g
            mcx["silver"] = s
            last_fetch_time = current_time
        else:
            print("Using old prices")

    gold = mcx["gold"]
    silver = mcx["silver"]

    return {
        "gold": {
            "mcx": gold,
            "rtgs": gold + premium["gold"]["rtgs"] if visibility["gold"]["rtgs"] else None,
            "retail": gold + premium["gold"]["retail"] if visibility["gold"]["retail"] else None,
            "bulk": gold + premium["gold"]["bulk"] if visibility["gold"]["bulk"] else None
        },
        "silver": {
            "mcx": silver,
            "rtgs": silver + premium["silver"]["rtgs"] if visibility["silver"]["rtgs"] else None,
            "retail": silver + premium["silver"]["retail"] if visibility["silver"]["retail"] else None,
            "bulk": silver + premium["silver"]["bulk"] if visibility["silver"]["bulk"] else None
        },
        "visibility": visibility,
        "lastUpdated": datetime.now(timezone.utc).isoformat()
    }


# =========================
# UPDATE (ADMIN)
# =========================
@app.post("/update")
def update_rates(data: dict, x_api_key: str = Header(None)):
    global premium, visibility

    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Update premiums only
    premium["gold"] = data["gold_premium"]
    premium["silver"] = data["silver_premium"]

    # 🔥 Full visibility control
    visibility = data.get("visibility", visibility)

    # Save
    with open(FILE, "w") as f:
        json.dump({
            "mcx": mcx,
            "premium": premium,
            "visibility": visibility
        }, f)

    return {"status": "updated"}
