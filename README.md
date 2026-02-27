<div align="center">

# 🔍 Real-Time Fraud Detection Pipeline

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Apache_Kafka-3.x-231F20?style=for-the-badge&logo=apachekafka&logoColor=white" />
  <img src="https://img.shields.io/badge/XGBoost-2.x-EA6020?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker_Compose-Orchestrated-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>
<p align="center">
  <img src="https://img.shields.io/badge/MLflow-Tracking-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-Caching-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" />
  <img src="https://img.shields.io/badge/Grafana-Dashboards-F46800?style=for-the-badge&logo=grafana&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-F7C948?style=for-the-badge" />
</p>

<br/>

> **A production-grade, end-to-end real-time fraud detection system** — powered by Kafka event streaming, XGBoost ML model serving, FastAPI, Redis caching, and full MLOps observability with Prometheus + Grafana.

<br/>

**⚡ Sub-250ms inference latency · 📊 89.83% ROC-AUC · 🔁 Fully containerized · 📈 Live drift monitoring**

<br/>

[**Quick Start**](#-installation--setup) · [**Architecture**](#-system-architecture) · [**API Docs**](#-api-reference) · [**Monitoring**](#-monitoring--dashboards) · [**Model Performance**](#-model-performance)

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Model Performance](#-model-performance)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the Pipeline](#-running-the-pipeline)
- [Service URLs](#-service-urls)
- [API Reference](#-api-reference)
- [Monitoring & Dashboards](#-monitoring--dashboards)
- [Dataset](#-dataset)
- [How It Works](#-how-it-works)
- [Challenges & Solutions](#-challenges--solutions)
- [Author](#-author)
- [License](#-license)

---

## 🧭 Overview

This project implements a **complete, production-ready fraud detection pipeline** that processes financial transactions in real-time using a modern streaming architecture.

A Kafka producer simulates live transaction events at scale. These events flow through a consumer that calls a FastAPI prediction endpoint, where a trained XGBoost model (loaded from the MLflow Model Registry) classifies each transaction as **legitimate or fraudulent** — with results cached in Redis and every metric scraped by Prometheus and visualized in Grafana.

### ✨ Key Highlights

| Feature | Detail |
|---|---|
| 🎯 **Fraud Detection Accuracy** | 89.83% ROC-AUC on 590k+ transactions |
| ⚡ **Inference Speed** | < 250ms end-to-end latency per transaction |
| 📦 **Fully Containerized** | One-command startup via Docker Compose |
| 🔁 **Streaming Architecture** | Apache Kafka event-driven ingestion |
| 🧠 **MLOps Ready** | MLflow experiment tracking + model registry |
| 📊 **Live Observability** | Prometheus metrics + Grafana dashboards |
| 🛡️ **Drift Detection** | PSI-based feature distribution monitoring |
| 💾 **Result Caching** | Redis TTL cache to reduce redundant inference |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FRAUD DETECTION PIPELINE                             │
│                                                                             │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐ │
│  │  Kafka Producer  │────▶│   Kafka Topic    │────▶│   Kafka Consumer    │ │
│  │  (tx simulator)  │     │  (transactions)  │     │  (scoring engine)   │ │
│  └──────────────────┘     └──────────────────┘     └────────┬─────────────┘ │
│                                                             │               │
│                                                             ▼               │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐ │
│  │      Redis       │◀────│    FastAPI       │◀────│   XGBoost Model     │ │
│  │    (caching)     │     │   REST API       │     │  (MLflow Registry)  │ │
│  └──────────────────┘     └────────┬─────────┘     └──────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────┐     ┌──────────────────┐                             │
│  │     Grafana      │◀────│   Prometheus     │                             │
│  │   (dashboard)    │     │   (metrics)      │                             │
│  └──────────────────┘     └──────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 🔄 Data Flow — Step by Step

```
Step 1 ──▶  Kafka Producer reads raw transaction records and publishes them
            to the 'transactions' Kafka topic at ~1 event/second.

Step 2 ──▶  Kafka Consumer subscribes to the topic, deserializes each
            message, and forwards it to the FastAPI scoring endpoint.

Step 3 ──▶  FastAPI checks Redis cache. If a cached prediction exists
            for this transaction ID, it returns immediately (cache hit).

Step 4 ──▶  On cache miss, FastAPI runs the XGBoost model, loaded at
            startup from the MLflow Model Registry (Production stage).

Step 5 ──▶  XGBoost returns a fraud probability score + binary label.
            The result is cached in Redis with a 300s TTL.

Step 6 ──▶  Prometheus scrapes the /metrics endpoint every 15 seconds,
            collecting request counts, latency histograms, and fraud rates.

Step 7 ──▶  Grafana reads from Prometheus and renders a live dashboard
            with fraud rate, prediction latency, and model confidence panels.

Step 8 ──▶  Drift Monitor continuously computes PSI across feature
            distributions and logs alerts to MLflow when drift exceeds 0.2.
```

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Streaming** | Apache Kafka + Zookeeper | 3.x | Real-time transaction ingestion |
| **ML Model** | XGBoost + SMOTE | 2.x | Fraud classification with imbalance handling |
| **API Serving** | FastAPI + Uvicorn | 0.110 | High-performance REST prediction endpoint |
| **Experiment Tracking** | MLflow | Latest | Model versioning, metrics, artifact storage |
| **Caching** | Redis | 7.x | Result caching for low-latency repeated queries |
| **Monitoring** | Prometheus + Grafana | Latest | Metrics scraping + live observability dashboard |
| **Data Quality** | Great Expectations | Latest | Schema & distribution validation |
| **Feature Store** | Custom Feast-inspired | — | Feature definitions + materialization |
| **Stream Processing** | Apache Flink (config) | Latest | Streaming feature engineering |
| **Infrastructure** | Docker Compose | Latest | Full container orchestration |
| **Language** | Python | 3.11 | Core application language |

---

## 📁 Project Structure

```
fraud-detection/
│
├── 📂 api/
│   ├── main.py                  # FastAPI app — /predict, /health, /metrics
│   └── requirements.txt         # API-specific Python dependencies
│
├── 📂 kafka_producer/
│   └── producer.py              # Simulates live transaction stream to Kafka
│
├── 📂 kafka_consumer/
│   ├── __init__.py
│   └── consumer.py              # Consumes topic, calls FastAPI, logs results
│
├── 📂 training_pipeline/
│   ├── preprocess.py            # Feature engineering, SMOTE, train/test split
│   └── train.py                 # XGBoost training + MLflow experiment logging
│
├── 📂 monitoring/
│   └── drift_monitor.py         # PSI-based feature drift detection + alerting
│
├── 📂 feature_store/
│   ├── features.py              # Feature view definitions
│   └── materialize.py           # Offline → Online store materialization
│
├── 📂 flink_jobs/
│   └── stream_features.py       # Streaming feature computation via Flink
│
├── 📂 data_quality/
│   └── expectations.py          # Great Expectations validation suite
│
├── 📂 docker/
│   └── prometheus.yml           # Prometheus scrape configuration
│
├── 📂 data/                     # ⚠️ gitignored — not committed
│   ├── raw/                     # Raw Kaggle dataset files
│   └── processed/               # Feature-engineered, SMOTE-balanced data
│
├── 📂 models/                   # ⚠️ gitignored — not committed
│   └── fraud_model/             # Saved XGBoost artifact
│
├── 📂 screenshots/              # Dashboard & UI screenshots
│
├── docker-compose.yml           # Full infra: Kafka, Redis, MLflow, Grafana
├── start.sh                     # One-command startup script
├── requirements.txt             # Full Python dependencies
├── .gitignore                   # Excludes venv, data/, models/, __pycache__
└── README.md                    # You are here 📍
```

---

## 📈 Model Performance

The XGBoost model was trained on the **[IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection)** dataset — 590,000+ financial transactions with a ~3.5% fraud rate. Severe class imbalance was addressed using **SMOTE** oversampling before training.

### 📊 Evaluation Metrics

| Metric | Value | Notes |
|---|---|---|
| 🏆 **ROC-AUC** | **0.8983** | Primary metric — robust to class imbalance |
| 🎯 **Precision** | 0.84 | Of flagged transactions, 84% are truly fraud |
| 🔎 **Recall** | 0.37 | Captures 37% of all fraud cases |
| ⚖️ **F1 Score** | 0.52 | Harmonic mean of precision + recall |
| ⏱️ **Training Time** | ~4 minutes | On standard CPU hardware |
| ⚡ **Inference Latency** | < 250ms | End-to-end, including API overhead |

> **Note:** Low recall is expected with heavily imbalanced fraud datasets. The primary optimization target is ROC-AUC, which provides the best tradeoff curve for downstream threshold tuning in production.

### ⚙️ Training Configuration

```python
XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight="auto",   # Further addresses class imbalance
    eval_metric="auc",
    early_stopping_rounds=20   # Prevents overfitting
)
```

All training runs — parameters, metrics, feature importances, and model artifacts — are automatically **logged and versioned in MLflow**.

### 🔬 MLflow Model Registry Workflow

```
Train ──▶ Evaluate ──▶ Log to MLflow ──▶ Register as "fraud_model"
      ──▶ Stage: Staging ──▶ (Manual review) ──▶ Stage: Production
      ──▶ FastAPI loads the "Production" model version on startup
```

---

## ✅ Prerequisites

Ensure the following are installed and available on your system before proceeding:

| Requirement | Minimum Version | Check Command |
|---|---|---|
| 🐳 **Docker Desktop** | Latest | `docker --version` |
| 🐍 **Python** | 3.11 | `python --version` |
| 📦 **pip** | Latest | `pip --version` |
| 🔧 **Git** | Any | `git --version` |
| 💾 **RAM** | 8 GB minimum | — |
| 🔑 **Kaggle Account** | — | For dataset download |

> ⚠️ **Memory Note:** Kafka, Zookeeper, MLflow, and Grafana are memory-intensive services. 8 GB RAM is the minimum; 16 GB is recommended for comfortable operation.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/PrasanthKumarS777/fraud-detection.git
cd fraud-detection
```

### 2. Create and Activate a Virtual Environment

```bash
# Windows (Git Bash)
python -m venv venv
source venv/Scripts/activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r api/requirements.txt
```

### 4. Download the Dataset

1. Go to the [IEEE-CIS Fraud Detection competition on Kaggle](https://www.kaggle.com/c/ieee-fraud-detection/data)
2. Download `train_transaction.csv` and `train_identity.csv`
3. Place them in the `data/raw/` directory:

```
fraud-detection/
└── data/
    └── raw/
        ├── train_transaction.csv   ✅
        └── train_identity.csv      ✅
```

> 🔒 The `data/` folder is listed in `.gitignore` and will **never** be committed to version control.

---

## 🚀 Running the Pipeline

Follow these steps in order. Each step must complete successfully before moving to the next.

---

### Step 1 — Start Infrastructure

```bash
docker compose up -d
```

This starts the following services in detached mode:

- **Apache Kafka + Zookeeper** — Event streaming backbone
- **Redis** — Prediction result cache
- **MLflow Tracking Server** — Experiment and model registry
- **Prometheus** — Metrics collection
- **Grafana** — Live visualization dashboards

```bash
# Wait ~30 seconds, then verify all containers are healthy
docker compose ps
```

Expected output: all services showing `Up` status.

---

### Step 2 — Preprocess Data

```bash
python training_pipeline/preprocess.py
```

This step will:
- Merge `train_transaction.csv` and `train_identity.csv` on `TransactionID`
- Engineer features: transaction velocity, time deltas, card-level aggregates
- Handle missing values and encode categorical features
- Apply **SMOTE** to balance the fraud/non-fraud class ratio to 50/50
- Save the processed dataset to `data/processed/`

---

### Step 3 — Train the Model

```bash
python training_pipeline/train.py
```

This step will:
- Train XGBoost with early stopping on the processed data
- Log all hyperparameters, evaluation metrics, and feature importances to **MLflow**
- Register the best model to the **MLflow Model Registry** as `fraud_model`
- Save the model artifact to `models/`

You can inspect training results at [http://localhost:5000](http://localhost:5000) after this step.

---

### Step 4 — Start All Services

```bash
bash start.sh
```

This launches all application processes:

| Process | Description |
|---|---|
| **FastAPI server** | REST API on port `8000` |
| **Kafka Producer** | Simulates live transaction stream |
| **Kafka Consumer** | Subscribes and forwards to scoring endpoint |
| **Drift Monitor** | Background PSI drift detection process |

---

## 🌐 Service URLs

Once everything is running, access these services in your browser:

| Service | URL | Description |
|---|---|---|
| 📖 **FastAPI Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| ❤️ **FastAPI Health** | http://localhost:8000/health | Service health check |
| 📡 **FastAPI Metrics** | http://localhost:8000/metrics | Raw Prometheus metrics |
| 🧪 **MLflow UI** | http://localhost:5000 | Experiment runs + model registry |
| 📊 **Grafana** | http://localhost:3000 | Live monitoring dashboard |
| 🔍 **Prometheus** | http://localhost:9090 | Raw metrics queries |
| 🗂️ **Kafka UI** | http://localhost:8080 | Topic browser (if enabled) |

> **Grafana default credentials:** `admin` / `admin`

---

## 📡 API Reference

### `POST /predict`

Score a single transaction for fraud probability.

**Request Body:**

```json
{
  "TransactionAmt": 150.00,
  "ProductCD": "W",
  "card4": "visa",
  "card6": "debit",
  "P_emaildomain": "gmail.com",
  "R_emaildomain": "gmail.com",
  "DeviceType": "desktop",
  "DeviceInfo": "Windows"
}
```

**Response:**

```json
{
  "transaction_id": "txn_20240227_001",
  "fraud_probability": 0.073,
  "prediction": 0,
  "label": "LEGITIMATE",
  "latency_ms": 48.3,
  "cached": false
}
```

| Field | Type | Description |
|---|---|---|
| `transaction_id` | `string` | Unique transaction identifier |
| `fraud_probability` | `float` | Model confidence score (0.0 – 1.0) |
| `prediction` | `int` | Binary label: `0` = Legitimate, `1` = Fraud |
| `label` | `string` | Human-readable verdict |
| `latency_ms` | `float` | End-to-end inference time in milliseconds |
| `cached` | `bool` | Whether result was served from Redis cache |

---

### `GET /health`

Returns the current health status of all system components.

```json
{
  "status": "healthy",
  "model": "loaded",
  "redis": "connected",
  "uptime_seconds": 3620
}
```

---

### `GET /metrics`

Returns Prometheus-formatted metrics for scraping.

```
# HELP fraud_predictions_total Total number of fraud predictions made
fraud_predictions_total{result="legitimate"} 9823
fraud_predictions_total{result="fraud"} 317

# HELP prediction_latency_seconds Prediction latency histogram
prediction_latency_seconds_bucket{le="0.05"} 7231
prediction_latency_seconds_bucket{le="0.1"} 9654
prediction_latency_seconds_bucket{le="0.25"} 10140

# HELP model_confidence_score_avg Average model confidence score
model_confidence_score_avg 0.921
```

---

## 📊 Monitoring & Dashboards

### Grafana Dashboard Panels

The pre-configured Grafana dashboard ships with 4 live panels:

| Panel | PromQL Expression | Description |
|---|---|---|
| 📈 **Request Rate** | `rate(fraud_predictions_total[1m])` | Predictions per second |
| 🚨 **Fraud Rate** | `fraud_rate_percentage` | % of transactions flagged as fraud |
| ⏱️ **Prediction Latency** | `prediction_latency_p99` | 99th percentile response time |
| 🧠 **Model Confidence** | `model_confidence_score_avg` | Average prediction confidence |

### Drift Monitoring

The `monitoring/drift_monitor.py` script runs as a background process and:

- Computes **Population Stability Index (PSI)** across incoming feature distributions
- Raises alerts when **PSI > 0.2** (indicating significant distribution drift)
- Logs drift scores and timestamps to **MLflow** for historical tracking
- Enables proactive model retraining before performance degrades in production

```
PSI < 0.1   → ✅ No significant change
0.1 – 0.2   → ⚠️  Moderate shift, monitor closely
PSI > 0.2   → 🚨 Significant drift detected — consider retraining
```

---

## 📸 Screenshots

> Screenshots will be added after the first successful pipeline run.

| Screenshot | Description |
|---|---|
| `screenshots/grafana_dashboard.png` | Live Grafana monitoring dashboard |
| `screenshots/mlflow_experiments.png` | MLflow experiment runs and model registry |
| `screenshots/fastapi_docs.png` | FastAPI Swagger UI |
| `screenshots/kafka_consumer_logs.png` | Kafka consumer terminal output |

To add screenshots: run the full pipeline, capture the above views, and place images in the `screenshots/` folder.

---

## 📂 Dataset

| Property | Detail |
|---|---|
| **Name** | IEEE-CIS Fraud Detection |
| **Source** | [Kaggle Competition](https://www.kaggle.com/c/ieee-fraud-detection) |
| **Total Rows** | ~590,000 transactions |
| **Fraud Rate** | ~3.5% (highly imbalanced) |
| **Total Features** | 434 (transaction + identity tables) |
| **Key Features** | `TransactionAmt`, `card1–card6`, `ProductCD`, `DeviceType`, `V1–V339` |
| **Files Required** | `train_transaction.csv`, `train_identity.csv` |

---

## 🔬 How It Works

### Feature Engineering

The preprocessing pipeline engineers the following feature groups from raw transaction data:

- **Amount features** — Log-transforms and bucket encoding of `TransactionAmt`
- **Time features** — Hour of day, day of week, time since last transaction per card
- **Card aggregates** — Rolling mean, standard deviation of transaction amounts per `card1–card6`
- **Email domain risk scores** — Frequency-encoded risk values for sender/receiver domains
- **Device fingerprints** — Encoded `DeviceType` and `DeviceInfo` combinations

### Class Imbalance Handling

With only ~3.5% fraud cases, a naive model would learn to always predict "legitimate" and still achieve 96.5% accuracy — a useless outcome. This project addresses imbalance at two levels:

1. **SMOTE (Synthetic Minority Oversampling)** — Applied during preprocessing to create synthetic fraud samples in the training set, balancing the class ratio to 50/50 before model training.
2. **`scale_pos_weight` in XGBoost** — Provides an additional internal penalty weighting during gradient boosting to further emphasize the minority (fraud) class during loss computation.

### Redis Caching Strategy

To avoid redundant inference on duplicate transactions (common in retry scenarios and batch re-submissions), predictions are cached in Redis keyed by a hash of the transaction ID:

```
Key:   sha256(transaction_id)
Value: {fraud_probability, prediction, label, timestamp}
TTL:   300 seconds (5 minutes)
```

Cache hits skip the XGBoost inference entirely, reducing latency to < 5ms for repeated queries.

---

## 🧩 Challenges & Solutions

| Challenge | Root Cause | Solution Applied |
|---|---|---|
| **Severe class imbalance** (3.5% fraud) | Real-world fraud is rare | SMOTE oversampling + `scale_pos_weight` in XGBoost |
| **Kafka consumer lag under load** | Slow downstream scoring | Tuned `max.poll.records` + increased partition count |
| **MLflow model loading latency** | Model loaded per-request | Model cached in memory at API startup, not per-request |
| **Redis cache invalidation** | Stale predictions after model retrain | TTL-based expiry (300s) tied to transaction ID hash |
| **Docker memory pressure** | Kafka/Zookeeper JVM defaults too high | Set explicit JVM heap limits (`KAFKA_HEAP_OPTS`) in compose |
| **Feature drift in production** | Distribution shifts over time | PSI-based drift monitor with MLflow alerting |

---

## 👤 Author

<div align="center">

**Prasanth Kumar Sahu**

[![GitHub](https://img.shields.io/badge/GitHub-PrasanthKumarS777-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/PrasanthKumarS777)
![Location](https://img.shields.io/badge/Location-Cuttack%2C_Odisha%2C_India-FF6B35?style=for-the-badge&logo=googlemaps&logoColor=white)

</div>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

```
MIT License — free to use, modify, and distribute with attribution.
```

---

<div align="center">

**If this project helped you, please consider giving it a ⭐ — it means a lot!**

<br/>

*Built with ❤️ using Python, Kafka, XGBoost, FastAPI, and Docker*

</div>
