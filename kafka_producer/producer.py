import json
import time
import pandas as pd
from kafka import KafkaProducer
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("Loading transaction data...")
df = pd.read_csv("data/raw/train_transaction.csv", nrows=10000)
df = df.fillna(0)
print(f"✅ Loaded {len(df)} transactions")

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: str(k).encode("utf-8"),
)

TOPIC = "raw-transactions"

def send_transaction(row: dict, index: int):
    row["event_timestamp"] = datetime.utcnow().isoformat()
    row["TransactionID"] = int(row.get("TransactionID", index))
    producer.send(
        TOPIC,
        key=str(row["TransactionID"]),
        value=row,
    )

print(f"🚀 Streaming to Kafka topic: {TOPIC}")
print("Press Ctrl+C to stop\n")

sent = 0
try:
    while True:
        row = df.sample(1).iloc[0].to_dict()
        send_transaction(row, sent)
        sent += 1

        if sent % 100 == 0:
            producer.flush()
            print(f"📤 Sent {sent} | ID: {int(row['TransactionID'])} | Fraud: {int(row.get('isFraud', 0))}")

        time.sleep(0.05)  # 20 transactions/second

except KeyboardInterrupt:
    print(f"\n⛔ Stopped. Total sent: {sent}")
    producer.flush()
    producer.close()
