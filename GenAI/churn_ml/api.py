"""FastAPI deployment surface for the trained churn model."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from .predict import predict_frame

MODEL_PATH = Path(os.getenv("CHURN_MODEL_PATH", "models/churn_model.joblib"))
app = FastAPI(title="Churn Prediction API", version="0.1.0")


class ChurnRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    tenure_months: float
    monthly_charges: float
    total_charges: float
    contract_type: str
    payment_method: str
    internet_service: str
    support_tickets: float
    senior_citizen: int


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "Churn Prediction API",
        "status": "ok",
        "endpoints": ["/health", "/predict"],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_loaded": str(MODEL_PATH.exists()).lower()}


@app.post("/predict")
def predict(request: ChurnRequest) -> dict[str, Any]:
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=503, detail=f"Model not found at {MODEL_PATH}")
    features = pd.DataFrame([request.model_dump()])
    result = predict_frame(MODEL_PATH, features).iloc[0]
    return {
        "churn_prediction": int(result["churn_prediction"]),
        "churn_probability": float(result["churn_probability"]),
    }
