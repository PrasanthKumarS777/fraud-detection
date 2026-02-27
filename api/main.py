import mlflow
import mlflow.xgboost
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time
import os

# ── MLflow setup ──────────────────────────────────────────
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

print("🔄 Loading model from MLflow...")
model = mlflow.xgboost.load_model("models:/fraud-detector@production")
print("✅ Model loaded from Production stage")

# Load API sample for feature schema
print("🔄 Loading feature schema...")
X_ref = pd.read_parquet("data/processed/api_sample.parquet")
FEATURE_COLS = X_ref.columns.tolist()
print(f"✅ Feature schema loaded: {len(FEATURE_COLS)} features")

# ── FastAPI app ───────────────────────────────────────────
app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud scoring powered by XGBoost + MLflow",
    version="1.0.0"
)

# ── Prometheus metrics ────────────────────────────────────
REQUEST_COUNT = Counter("fraud_api_requests_total", "Total prediction requests")
FRAUD_COUNT   = Counter("fraud_api_fraud_detected_total", "Total fraud detected")
LATENCY       = Histogram("fraud_api_latency_seconds", "Prediction latency")

# ── Request schema ────────────────────────────────────────
class TransactionRaw(BaseModel):
    features: dict

# ── Helper — build clean feature vector ──────────────────
def build_feature_vector(features: dict) -> pd.DataFrame:
    """
    Takes raw feature dict (may contain strings, nulls, extra cols).
    Returns a clean float64 DataFrame aligned to training columns.
    """
    df = pd.DataFrame([features])

    # Add missing training columns with 0
    for col in FEATURE_COLS:
        if col not in df.columns:
            df[col] = 0.0

    # Keep only training columns in correct order
    df = df[FEATURE_COLS]

    # Convert everything to numeric — strings/nulls become 0
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.fillna(0.0)
    df = df.astype(np.float64)

    return df

# ── Endpoints ─────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "running",
        "model": "fraud-detector",
        "stage": "Production",
        "features": len(FEATURE_COLS)
    }

@app.get("/health")
def health():
    return {"status": "healthy", "feature_count": len(FEATURE_COLS)}

@app.post("/predict")
def predict(transaction: TransactionRaw):
    start = time.time()
    REQUEST_COUNT.inc()

    try:
        features = transaction.features

        # If only TransactionID or empty — use random real sample row
        non_id_features = {
            k: v for k, v in features.items()
            if k not in {"TransactionID", "event_timestamp"}
        }

        if len(non_id_features) == 0:
            input_df = X_ref.sample(n=1).astype(np.float64)
        else:
            input_df = build_feature_vector(features)

        proba      = float(model.predict_proba(input_df)[0][1])
        prediction = int(proba >= 0.5)

        if prediction == 1:
            FRAUD_COUNT.inc()

        latency = time.time() - start
        LATENCY.observe(latency)

        return {
            "transaction_id": features.get("TransactionID", "unknown"),
            "is_fraud": prediction,
            "fraud_probability": round(proba, 4),
            "latency_ms": round(latency * 1000, 2),
            "model_stage": "Production"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
