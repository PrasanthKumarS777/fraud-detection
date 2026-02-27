import json
import redis
import requests
import time
from kafka import KafkaConsumer
from datetime import datetime

# ── Connections ───────────────────────────────────────────
KAFKA_BROKER = "localhost:9092"
TOPIC        = "raw-transactions"
API_URL      = "http://localhost:8000/predict"
REDIS_HOST   = "localhost"
REDIS_PORT   = 6379
REDIS_TTL    = 3600

# Columns to exclude — not part of model training features
EXCLUDE_COLS = {"isFraud", "event_timestamp", "TransactionID"}

# ── Setup ─────────────────────────────────────────────────
print("🔄 Connecting to Redis...")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
r.ping()
print("✅ Redis connected")

print("🔄 Connecting to Kafka...")
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="fraud-consumer-group-v2",
    consumer_timeout_ms=1000,
)
print(f"✅ Kafka consumer connected — listening to topic: {TOPIC}")
print("Press Ctrl+C to stop\n")

# ── Counters ──────────────────────────────────────────────
processed  = 0
fraud_count = 0
error_count = 0
start_time  = time.time()

try:
    while True:
        for message in consumer:
            tx = message.value

            # Extract TransactionID before cleaning
            tx_id = tx.get("TransactionID", f"unknown_{processed}")

            # Clean features — remove non-training columns
            features = {k: v for k, v in tx.items() if k not in EXCLUDE_COLS}

            # Call FastAPI scoring endpoint
            try:
                response = requests.post(
                    API_URL,
                    json={"features": features},
                    timeout=5
                )
                response.raise_for_status()
                result = response.json()
            except requests.exceptions.Timeout:
                print(f"⚠️  Timeout on TX: {tx_id}")
                error_count += 1
                continue
            except Exception as e:
                print(f"⚠️  API error on TX {tx_id}: {e}")
                error_count += 1
                continue

            is_fraud   = result.get("is_fraud", 0)
            proba      = result.get("fraud_probability", 0.0)
            latency_ms = result.get("latency_ms", 0.0)

            # Store result in Redis with TTL
            redis_key = f"fraud:tx:{tx_id}"
            redis_val = json.dumps({
                "transaction_id": tx_id,
                "is_fraud": is_fraud,
                "fraud_probability": round(proba, 4),
                "scored_at": datetime.utcnow().isoformat(),
                "latency_ms": latency_ms,
            })
            r.setex(redis_key, REDIS_TTL, redis_val)

            processed += 1

            # Alert on fraud
            if is_fraud == 1:
                fraud_count += 1
                print(
                    f"🚨 FRAUD ALERT | TX: {tx_id} | "
                    f"Prob: {proba:.4f} | Latency: {latency_ms}ms"
                )

            # Progress log every 100 messages
            if processed % 100 == 0:
                elapsed    = time.time() - start_time
                rate       = processed / elapsed
                fraud_rate = fraud_count / processed * 100
                print(
                    f"📊 Processed: {processed} | "
                    f"Fraud: {fraud_count} ({fraud_rate:.1f}%) | "
                    f"Errors: {error_count} | "
                    f"Rate: {rate:.1f} tx/s"
                )

except KeyboardInterrupt:
    elapsed = time.time() - start_time
    print(f"\n⛔ Stopped.")
    print(f"   Total processed : {processed}")
    print(f"   Fraud detected  : {fraud_count} ({fraud_count/max(processed,1)*100:.1f}%)")
    print(f"   Errors          : {error_count}")
    print(f"   Elapsed         : {elapsed:.1f}s")
    print(f"   Avg throughput  : {processed/max(elapsed,1):.1f} tx/s")

finally:
    consumer.close()
    print("✅ Consumer closed cleanly")
