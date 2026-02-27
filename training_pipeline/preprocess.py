import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os
import pickle

print("📂 Loading datasets...")
train_txn = pd.read_csv("data/raw/train_transaction.csv")
train_id = pd.read_csv("data/raw/train_identity.csv")

print(f"✅ Transactions: {train_txn.shape}")
print(f"✅ Identity: {train_id.shape}")

# Merge on TransactionID
df = train_txn.merge(train_id, on="TransactionID", how="left")
print(f"✅ Merged shape: {df.shape}")

# Drop columns with >80% missing values
threshold = 0.8
missing_pct = df.isnull().mean()
cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
df = df.drop(columns=cols_to_drop)
print(f"✅ Dropped {len(cols_to_drop)} high-null columns. Remaining: {df.shape[1]}")

# Separate target
y = df["isFraud"]
df = df.drop(columns=["isFraud", "TransactionID"])

# Encode categorical columns
cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = df[col].astype(str)
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

print(f"✅ Encoded {len(cat_cols)} categorical columns")

# Fill remaining nulls with median
df = df.fillna(df.median(numeric_only=True))

print(f"✅ Final feature shape: {df.shape}")
print(f"✅ Fraud rate: {y.mean():.4f} ({y.sum()} fraud out of {len(y)})")

# Save processed data
os.makedirs("data/processed", exist_ok=True)
df.to_parquet("data/processed/features.parquet", index=False)
y.to_frame().to_parquet("data/processed/labels.parquet", index=False)

# Save encoders
with open("data/processed/encoders.pkl", "wb") as f:
    pickle.dump(encoders, f)

print("\n✅ Saved to data/processed/")
print("   - features.parquet")
print("   - labels.parquet")
print("   - encoders.pkl")
