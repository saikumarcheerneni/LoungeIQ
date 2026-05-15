"""
LoungeIQ — Week 2
ML Model Training + Drift Detection
Trains a Random Forest to predict lounge occupancy
and implements KS-test drift detection
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

os.makedirs("models", exist_ok=True)

# ─── LOAD DATA ───────────────────────────────────────────────
def load_data():
    df = pd.read_csv("data/lounge_occupancy.csv")
    print(f"Loaded {len(df)} rows")
    return df

# ─── FEATURE ENGINEERING ─────────────────────────────────────
def prepare_features(df):
    le_day = LabelEncoder()
    le_season = LabelEncoder()
    le_lounge = LabelEncoder()

    df["day_encoded"] = le_day.fit_transform(df["day_of_week"])
    df["season_encoded"] = le_season.fit_transform(df["season"])
    df["lounge_encoded"] = le_lounge.fit_transform(df["lounge_id"])

    # Save encoders for API use later
    with open("models/encoders.pkl", "wb") as f:
        pickle.dump({"day": le_day, "season": le_season, "lounge": le_lounge}, f)

    features = [
        "hour", "is_weekend", "flight_delay",
        "has_major_event", "day_encoded",
        "season_encoded", "lounge_encoded", "capacity"
    ]
    X = df[features]
    y = df["occupancy_pct"]
    return X, y, features

# ─── TRAIN MODEL ─────────────────────────────────────────────
def train(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"\n Model Performance:")
    print(f"  MAE  : {mae:.2f}%")
    print(f"  RMSE : {rmse:.2f}%")
    print(f"  R²   : {r2:.4f}")

    # Save model
    with open("models/occupancy_model.pkl", "wb") as f:
        pickle.dump(model, f)

    # Save training feature distribution for drift detection
    X_train.to_csv("models/train_distribution.csv", index=False)

    print("\n Model saved to models/occupancy_model.pkl")

    # Feature importance chart
    importances = pd.Series(model.feature_importances_, index=X.columns)
    importances.sort_values().plot(kind="barh", figsize=(8, 5), color="steelblue")
    plt.title("Feature Importance — LoungeIQ Occupancy Model")
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.savefig("models/feature_importance.png")
    plt.close()
    print(" Feature importance chart saved")

    return model, X_test, y_test

# ─── DRIFT DETECTION ─────────────────────────────────────────
def detect_drift(current_data: pd.DataFrame, threshold=0.05):
    """
    Compares current incoming data distribution against training data.
    Uses Kolmogorov-Smirnov test — if p-value < threshold, drift detected.
    This is what happens when flight delays suddenly spike.
    """
    train_dist = pd.read_csv("models/train_distribution.csv")

    drift_report = {}
    for col in current_data.columns:
        if col in train_dist.columns:
            stat, p_value = stats.ks_2samp(
                train_dist[col].dropna(),
                current_data[col].dropna()
            )
            drift_detected = p_value < threshold
            drift_report[col] = {
                "ks_statistic": round(stat, 4),
                "p_value": round(p_value, 4),
                "drift_detected": drift_detected
            }

    any_drift = any(v["drift_detected"] for v in drift_report.values())
    if any_drift:
        print("\n⚠️  DRIFT DETECTED — Model retraining recommended!")
    else:
        print("\n✅  No significant drift detected")

    return drift_report, any_drift


if __name__ == "__main__":
    df = load_data()
    X, y, features = prepare_features(df)
    model, X_test, y_test = train(X, y)

    # Simulate drift: create data with high flight_delay (like a sudden storm)
    print("\n--- Simulating Flight Delay Spike (Drift Test) ---")
    drifted_data = X_test.copy()
    drifted_data["flight_delay"] = 1  # all flights delayed
    drifted_data["hour"] = np.random.randint(17, 22, len(drifted_data))  # evening chaos
    drift_report, has_drift = detect_drift(drifted_data)
    print(pd.DataFrame(drift_report).T)
