# ✈ LoungeIQ — Airport Lounge Intelligence Platform

> Predictive lounge management powered by AI — built by Saikumar Cheerneni

---

## What is LoungeIQ?

LoungeIQ is a full-stack AI platform that helps airports and airlines manage lounge occupancy intelligently and gives passengers a smart assistant to find the best lounge for them.

**Three core capabilities:**
1. **Predict** lounge occupancy using Machine Learning (Random Forest)
2. **Recommend** the best lounge per passenger (ticket class + loyalty tier + gate)
3. **Assist** passengers via an agentic AI chatbot with real-time tool calling

---

## Project Structure

```
LoungeIQ/
│
├── data/
│   └── generate_data.py      ← Week 1: synthetic data generator
│
├── models/
│   └── train_model.py        ← Week 2: ML training + drift detection
│
├── api/
│   └── main.py               ← Week 3: FastAPI backend
│
├── chatbot/
│   └── agent.py              ← Week 4: agentic chatbot (Claude API)
│
├── dashboard/
│   └── src/App.jsx           ← Week 5: React dashboard
│
├── requirements.txt
├── Dockerfile                ← Week 6: deployment
└── README.md
```

---

## Quick Start (Windows)

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Generate training data
```bash
cd data
python generate_data.py
```

### Step 3 — Train the ML model
```bash
cd models
python train_model.py
```

### Step 4 — Start the API
```bash
uvicorn api.main:app --reload
```
Open: http://localhost:8000/docs

### Step 5 — Run the chatbot
```bash
set ANTHROPIC_API_KEY=your-key-here
python chatbot/agent.py
```

### Step 6 — Start the dashboard
```bash
cd dashboard
npm install
npm start
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/status` | All lounge live occupancy |
| GET | `/status/{lounge_id}` | Single lounge status |
| POST | `/predict` | Predict occupancy for time/conditions |
| POST | `/recommend` | Best lounge for a passenger |
| POST | `/chat` | Agentic chatbot endpoint |

---

## Tech Stack

- **ML**: Python, Pandas, Scikit-learn, XGBoost, SciPy (KS-test)
- **Backend**: FastAPI, MongoDB, Pydantic, JWT
- **AI**: Claude API (Anthropic) with tool calling
- **Frontend**: React, Recharts
- **Cloud**: Azure App Service, Docker, GitHub Actions CI/CD

---

## Built by

**Saikumar Cheerneni**  
MEng Computer Science — Concordia University, Montreal  
github.com/saikumarcheerneni
