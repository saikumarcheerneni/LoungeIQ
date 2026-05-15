"""
LoungeIQ — Week 1
Synthetic Data Generator
Generates realistic airport lounge occupancy data for ML training
"""

import pandas as pd
import numpy as np
import os

# Set seed so results are reproducible
np.random.seed(42)

LOUNGES = ["Lounge_A", "Lounge_B", "Lounge_C", "Lounge_D"]
SEASONS = ["spring", "summer", "autumn", "winter"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def base_occupancy(hour, day, season):
    """
    Returns a base occupancy % based on time patterns.
    Morning rush: 6-9am
    Lunch peak: 12-2pm
    Evening rush: 5-8pm
    """
    # Hour pattern
    if 6 <= hour <= 9:
        base = np.random.uniform(65, 90)   # morning rush
    elif 10 <= hour <= 11:
        base = np.random.uniform(40, 60)   # mid morning
    elif 12 <= hour <= 14:
        base = np.random.uniform(55, 75)   # lunch
    elif 15 <= hour <= 16:
        base = np.random.uniform(35, 55)   # afternoon dip
    elif 17 <= hour <= 20:
        base = np.random.uniform(70, 95)   # evening rush
    elif 21 <= hour <= 23:
        base = np.random.uniform(20, 45)   # late night
    else:
        base = np.random.uniform(5, 20)    # overnight (0-5am)

    # Weekend adjustment — slightly lower business travel
    if day in ["Saturday", "Sunday"]:
        base *= np.random.uniform(0.7, 0.9)

    # Season adjustment
    if season == "summer":
        base *= np.random.uniform(1.1, 1.25)   # peak travel
    elif season == "winter":
        base *= np.random.uniform(0.85, 1.0)
    elif season == "spring":
        base *= np.random.uniform(0.95, 1.1)
    else:  # autumn
        base *= np.random.uniform(0.9, 1.05)

    return round(min(base, 100), 2)  # cap at 100%


def generate_dataset(num_days=180):
    """Generate num_days worth of hourly lounge data across all lounges."""
    records = []

    for lounge in LOUNGES:
        capacity = np.random.randint(80, 200)  # each lounge has different capacity

        for day_num in range(num_days):
            day_of_week = DAYS[day_num % 7]
            is_weekend = 1 if day_of_week in ["Saturday", "Sunday"] else 0
            season = SEASONS[(day_num // 45) % 4]  # change season every 45 days
            has_major_event = 1 if np.random.random() < 0.05 else 0  # 5% chance of event

            for hour in range(24):
                occ = base_occupancy(hour, day_of_week, season)

                # Flight delay spike — if delay occurs, occupancy jumps
                flight_delay = 1 if np.random.random() < 0.12 else 0
                if flight_delay:
                    occ = min(occ + np.random.uniform(10, 25), 100)

                # Major event spike
                if has_major_event:
                    occ = min(occ + np.random.uniform(15, 30), 100)

                # Add small random noise
                occ = max(0, min(occ + np.random.uniform(-3, 3), 100))

                records.append({
                    "lounge_id": lounge,
                    "capacity": capacity,
                    "day_num": day_num,
                    "day_of_week": day_of_week,
                    "is_weekend": is_weekend,
                    "hour": hour,
                    "season": season,
                    "flight_delay": flight_delay,
                    "has_major_event": has_major_event,
                    "occupancy_pct": round(occ, 2)
                })

    df = pd.DataFrame(records)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/lounge_occupancy.csv", index=False)
    print(f"Dataset generated: {len(df)} rows")
    print(df.head(10))
    print("\nOccupancy stats:")
    print(df["occupancy_pct"].describe())
    return df


if __name__ == "__main__":
    df = generate_dataset(num_days=180)
