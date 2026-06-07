from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import numpy as np

app = FastAPI()

# CORS configuration that other IITM students reported working
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Access-Control-Allow-Origin"],
)

DATA_FILE = Path(__file__).parent.parent / "q-vercel-latency.json"

with open(DATA_FILE, "r") as f:
    DATA = json.load(f)


class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/")
def metrics(req: RequestBody):
    regions = {}

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        regions[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(
                1 for latency in latencies
                if latency > req.threshold_ms
            ),
        }

    return {
        "regions": regions
    }