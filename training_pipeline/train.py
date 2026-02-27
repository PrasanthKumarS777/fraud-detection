import pandas as pd
import numpy as np
import mlflow
import mlflow.xgboost
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score, precision_score, recall_score,
    roc_auc_score, classification_report
)
from imblearn.over_sampling import SMOTE

# ── MLflow setup ──────────────────────────────────────────
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("fraud-detection")

print("📂 Loading processed data...")
X = pd.read_parquet("data/processed/features.parquet")
y = pd.read_parquet("data/processed/labels.parquet")["isFraud"]

print(f"✅ Features: {X.shape}")
print(f"✅ Fraud rate: {y.mean():.4f}")

# ── Train/test split ──────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✅ Train: {X_train.shape} | Test: {X_test.shape}")

# ── SMOTE on 50K sample to avoid memory error on Windows ──
print("⚙️  Applying SMOTE oversampling (sampled 50K)...")
X_sample = X_train.sample(n=50000, random_state=42)
y_sample = y_train.loc[X_sample.index]

smote = SMOTE(random_state=42)
X_train_sm, y_train_sm = smote.fit_resample(X_sample, y_sample)
print(f"✅ After SMOTE — Shape: {X_train_sm.shape} | Fraud rate: {y_train_sm.mean():.4f}")

# ── Hyperparameters ───────────────────────────────────────
params = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "scale_pos_weight": 1,
    "eval_metric": "auc",
    "random_state": 42,
    "n_jobs": -1,
    "tree_method": "hist",
}

# ── Train with MLflow tracking ────────────────────────────
print("\n🚀 Starting MLflow run...")
with mlflow.start_run(run_name="xgboost-smote-v1"):

    mlflow.log_params(params)

    model = XGBClassifier(**params)
    model.fit(
        X_train_sm, y_train_sm,
        eval_set=[(X_test, y_test)],
        verbose=50,
    )

    # ── Predictions ───────────────────────────────────────
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # ── Metrics ───────────────────────────────────────────
    f1        = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall    = recall_score(y_test, y_pred)
    roc_auc   = roc_auc_score(y_test, y_proba)

    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("roc_auc", roc_auc)

    print(f"\n📊 Results:")
    print(f"   F1 Score  : {f1:.4f}")
    print(f"   Precision : {precision:.4f}")
    print(f"   Recall    : {recall:.4f}")
    print(f"   ROC-AUC   : {roc_auc:.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Legit','Fraud'])}")

    # ── Log model to MLflow ───────────────────────────────
    mlflow.xgboost.log_model(
        model,
        artifact_path="fraud-model",
        registered_model_name="fraud-detector",
        input_example=X_test.iloc[:1],
    )
    print("✅ Model logged and registered in MLflow")
    print(f"✅ Check results at: http://localhost:5000")
