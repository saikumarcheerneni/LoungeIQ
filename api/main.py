"""
LoungeIQ — Week 3
FastAPI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pickle
import pandas as pd
import numpy as np
import os
import sys
import json
from groq import Groq as GroqClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="LoungeIQ API",
    description="Airport Lounge Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "../models/occupancy_model.pkl")
    enc_path = os.path.join(os.path.dirname(__file__), "../models/encoders.pkl")
    if os.path.exists(model_path) and os.path.exists(enc_path):
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        with open(enc_path, "rb") as f:
            encoders = pickle.load(f)
        return model, encoders
    return None, None

model, encoders = load_model()
groq_client = GroqClient(api_key=os.environ.get("GROQ_API_KEY", ""))

LOUNGES_DB = {
    "Lounge_A": {"name": "Premier Business Lounge", "terminal": "T1", "gate_zone": "A", "capacity": 120, "amenities": ["wifi", "shower", "bar", "buffet"], "eligible": ["business", "first", "platinum"]},
    "Lounge_B": {"name": "Executive Lounge", "terminal": "T1", "gate_zone": "B", "capacity": 150, "amenities": ["wifi", "snacks", "bar"], "eligible": ["business", "first", "platinum", "gold"]},
    "Lounge_C": {"name": "Comfort Lounge", "terminal": "T2", "gate_zone": "C", "capacity": 200, "amenities": ["wifi", "snacks"], "eligible": ["business", "first", "platinum", "gold", "silver"]},
    "Lounge_D": {"name": "Sky Lounge", "terminal": "T2", "gate_zone": "D", "capacity": 80, "amenities": ["wifi", "shower", "spa", "bar", "buffet"], "eligible": ["first", "platinum"]},
}

LIVE_OCCUPANCY = {
    "Lounge_A": 72.5,
    "Lounge_B": 45.0,
    "Lounge_C": 88.3,
    "Lounge_D": 31.0,
}

class PredictRequest(BaseModel):
    lounge_id: str
    hour: int
    day_of_week: str
    season: str
    flight_delay: int = 0
    has_major_event: int = 0

class RecommendRequest(BaseModel):
    ticket_class: str
    loyalty_tier: str
    gate: str
    hour: int
    day_of_week: str
    season: str = "summer"
    flight_delay: int = 0

class ChatRequest(BaseModel):
    message: str

def get_occupancy_status(pct):
    if pct < 40: return "quiet"
    elif pct < 70: return "moderate"
    elif pct < 90: return "busy"
    else: return "full"

def is_eligible(ticket_class, loyalty_tier, lounge_id):
    lounge = LOUNGES_DB.get(lounge_id)
    if not lounge: return False
    return ticket_class in lounge["eligible"] or loyalty_tier in lounge["eligible"]

def gate_zone(gate: str):
    return gate[0].upper() if gate else "A"

@app.get("/")
def root():
    return {"message": "Welcome to LoungeIQ API", "version": "1.0.0", "status": "running"}

@app.post("/predict")
def predict_occupancy(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Run train_model.py first.")
    lounge = LOUNGES_DB.get(req.lounge_id)
    if not lounge:
        raise HTTPException(status_code=404, detail=f"Lounge {req.lounge_id} not found")
    try:
        day_enc = encoders["day"].transform([req.day_of_week])[0]
        season_enc = encoders["season"].transform([req.season])[0]
        lounge_enc = encoders["lounge"].transform([req.lounge_id])[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Encoding error: {str(e)}")
    features = np.array([[req.hour, 1 if req.day_of_week in ["Saturday", "Sunday"] else 0,
        req.flight_delay, req.has_major_event, day_enc, season_enc, lounge_enc, lounge["capacity"]]])
    prediction = round(min(max(float(model.predict(features)[0]), 0), 100), 2)
    return {"lounge_id": req.lounge_id, "lounge_name": lounge["name"],
            "predicted_occupancy_pct": prediction, "status": get_occupancy_status(prediction),
            "estimated_available_spots": int(lounge["capacity"] * (1 - prediction / 100))}

@app.post("/recommend")
def recommend_lounge(req: RecommendRequest):
    passenger_zone = gate_zone(req.gate)
    eligible_lounges = []
    for lounge_id, info in LOUNGES_DB.items():
        if is_eligible(req.ticket_class, req.loyalty_tier, lounge_id):
            live_occ = LIVE_OCCUPANCY.get(lounge_id, 50.0)
            zone_bonus = 20 if info["gate_zone"] == passenger_zone else 0
            score = (100 - live_occ) + zone_bonus
            eligible_lounges.append({
                "lounge_id": lounge_id, "name": info["name"],
                "terminal": info["terminal"], "gate_zone": info["gate_zone"],
                "occupancy_pct": live_occ, "status": get_occupancy_status(live_occ),
                "amenities": info["amenities"],
                "available_spots": int(info["capacity"] * (1 - live_occ / 100)), "score": score
            })
    if not eligible_lounges:
        raise HTTPException(status_code=404, detail="No eligible lounges found")
    eligible_lounges.sort(key=lambda x: x["score"], reverse=True)
    best = eligible_lounges[0]
    return {"recommendation": best, "all_eligible": eligible_lounges,
            "message": f"We recommend {best['name']} — currently {best['status']} ({best['occupancy_pct']}% full)"}

@app.get("/status")
def all_lounge_status():
    result = []
    for lounge_id, info in LOUNGES_DB.items():
        occ = LIVE_OCCUPANCY.get(lounge_id, 0)
        result.append({"lounge_id": lounge_id, "name": info["name"], "terminal": info["terminal"],
                       "occupancy_pct": occ, "status": get_occupancy_status(occ),
                       "available_spots": int(info["capacity"] * (1 - occ / 100)), "capacity": info["capacity"]})
    return {"lounges": result, "total": len(result)}

@app.get("/status/{lounge_id}")
def lounge_status(lounge_id: str):
    lounge = LOUNGES_DB.get(lounge_id)
    if not lounge:
        raise HTTPException(status_code=404, detail="Lounge not found")
    occ = LIVE_OCCUPANCY.get(lounge_id, 0)
    return {"lounge_id": lounge_id, "name": lounge["name"], "occupancy_pct": occ,
            "status": get_occupancy_status(occ), "amenities": lounge["amenities"],
            "available_spots": int(lounge["capacity"] * (1 - occ / 100))}

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    lounge_context = json.dumps([{
        "lounge_id": lid, "name": info["name"],
        "occupancy_pct": LIVE_OCCUPANCY.get(lid, 0),
        "status": get_occupancy_status(LIVE_OCCUPANCY.get(lid, 0)),
        "eligible": info["eligible"]
    } for lid, info in LOUNGES_DB.items()])

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"You are LoungeIQ Assistant. Help passengers find the best airport lounge. Current lounge data: {lounge_context}"},
            {"role": "user", "content": req.message}
        ]
    )
    return {"reply": response.choices[0].message.content}