#!/bin/bash
echo "🚀 Starting Fraud Detection Pipeline..."

# Step 1 — Start Docker infrastructure
docker compose up -d
echo "⏳ Waiting for services to start..."
sleep 20

# Step 2 — Activate venv
source venv/Scripts/activate

# Step 3 — Start FastAPI in background
echo "🔄 Starting FastAPI..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
sleep 5

# Step 4 — Start Kafka Producer in background
echo "🔄 Starting Kafka Producer..."
python kafka_producer/producer.py &
sleep 3

# Step 5 — Start Kafka Consumer in background
echo "🔄 Starting Kafka Consumer..."
python kafka_consumer/consumer.py &

echo ""
echo "✅ All services running!"
echo "   MLflow    → http://localhost:5000"
echo "   FastAPI   → http://localhost:8000"
echo "   Prometheus → http://localhost:9090"
echo "   Grafana   → http://localhost:3000"
echo ""
echo "Run 'docker ps' to verify containers"
