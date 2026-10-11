"""You Can't Raise DAU by Staring at the DAU Chart — example data generator for the user-segment practice.

Builds two synthetic tables for the user-segment analysis practice.

  - user_master   : per-user signup (first record) info              (user_id, first_active_date)
  - user_activity : log of the days a user logged a habit check-in   (user_id, event_date)

Each user is assigned a 'usual logging probability' (activity_rate) and a 'churn point'
(churn_date) up front; then, from the signup date to the target date, a Bernoulli trial per day
decides whether the user logged something that day. This guarantees that all five segments show up
as of the target date, and because each user's churn point is fixed, cutting the data 'N days ago'
also shows segments moving naturally over time (Flow).

The seed is fixed, so whoever runs this gets exactly the same data.
"""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd

# Prevent non-ASCII output from being mangled by cp949 encoding when stdout is captured by a pipe
# (no effect on direct console output)
sys.stdout.reconfigure(encoding="utf-8")

SEED = 42
TARGET_DATE = date(2026, 5, 20)   # analysis target date ("today")
N_USERS = 200
HISTORY_DAYS = 120                # maximum span of the activity log (target - 120 ~ target)

BASE = os.path.dirname(os.path.abspath(__file__))
MASTER_PATH = os.path.join(BASE, "data", "user_master.csv")
ACTIVITY_PATH = os.path.join(BASE, "data", "user_activity.csv")

# Activity-intensity tiers: (name, daily logging probability, share). Heavier tiers log more often.
ACTIVITY_TIERS = [
    ("heavy", 0.85, 0.26),
    ("mid",   0.55, 0.30),
    ("light", 0.28, 0.27),
    ("rare",  0.12, 0.17),
]

# Churn types: (name, share). No activity is logged on or after churn_date.
#   none   : never churns; keeps logging through the target date
#   recent : churned within the last 1-7 days (fewer active days -> heavy -> light, or stays light)
#   mid    : churned 8-30 days ago (0 active days in the last 7 -> risk)
#   deep   : churned 31-60 days ago (last record more than 30 days ago -> dormant)
CHURN_TYPES = [
    ("none",   0.62),
    ("recent", 0.14),
    ("mid",    0.14),
    ("deep",   0.10),
]


def _pick(rng: np.random.Generator, items):
    """Pick one entry from a (value, probability) list, weighted by probability."""
    labels = [it[0] for it in items]
    probs = np.array([it[-1] for it in items], dtype=float)
    probs /= probs.sum()
    return labels[rng.choice(len(labels), p=probs)]


def build():
    rng = np.random.default_rng(SEED)
    tier_rate = {name: rate for name, rate, _ in ACTIVITY_TIERS}

    master_rows = []
    activity_rows = []

    for i in range(1, N_USERS + 1):
        user_id = f"user_{i:03d}"

        # Signup date: ids 1-10 signed up today (new), 11-16 within the last 1-6 days,
        # everyone else spread over 7-115 days ago.
        if i <= 10:
            age = 0
        elif i <= 16:
            age = int(rng.integers(1, 7))
        else:
            age = int(rng.integers(7, HISTORY_DAYS - 5))
        first_active = TARGET_DATE - timedelta(days=age)
        master_rows.append((user_id, first_active))

        tier = _pick(rng, ACTIVITY_TIERS)
        rate = tier_rate[tier]
        churn = _pick(rng, CHURN_TYPES)

        # Churn point (churn_date): nothing is logged on or after this day.
        if churn == "none":
            churn_date = None
        elif churn == "recent":
            churn_date = TARGET_DATE - timedelta(days=int(rng.integers(1, 8)))
        elif churn == "mid":
            churn_date = TARGET_DATE - timedelta(days=int(rng.integers(8, 31)))
        else:  # deep
            churn_date = TARGET_DATE - timedelta(days=int(rng.integers(31, 61)))

        # Simulate day by day, from signup to the target date, whether the user logged anything.
        day = first_active
        while day <= TARGET_DATE:
            if churn_date is not None and day >= churn_date:
                break  # no activity after churn
            if rng.random() < rate:
                activity_rows.append((user_id, day))
            day += timedelta(days=1)

        # The signup day (first record) always gets exactly one activity row (signup = first record).
        # That way no user has zero activity rows, so count_if/bool_or can never return NULL, and the
        # unrealistic case of 'signed up but never did anything' never occurs.
        activity_rows.append((user_id, first_active))

    master = pd.DataFrame(master_rows, columns=["user_id", "first_active_date"])
    activity = pd.DataFrame(activity_rows, columns=["user_id", "event_date"])
    # Drop duplicates (the guaranteed signup-day row may overlap with the simulation), then sort
    activity = (activity.drop_duplicates()
                        .sort_values(["event_date", "user_id"])
                        .reset_index(drop=True))
    return master, activity


def main():
    master, activity = build()
    os.makedirs(os.path.dirname(MASTER_PATH), exist_ok=True)

    master_out = master.copy()
    master_out["first_active_date"] = master_out["first_active_date"].map(lambda d: d.isoformat())
    master_out.to_csv(MASTER_PATH, index=False)

    activity_out = activity.copy()
    activity_out["event_date"] = activity_out["event_date"].map(lambda d: d.isoformat())
    activity_out.to_csv(ACTIVITY_PATH, index=False)

    print(f"wrote {len(master):,} rows -> {MASTER_PATH}")
    print(f"wrote {len(activity):,} rows -> {ACTIVITY_PATH}")
    print(f"  target_date : {TARGET_DATE.isoformat()}")
    print(f"  users       : {len(master):,}")
    print(f"  date range  : {activity_out['event_date'].min()} ~ {activity_out['event_date'].max()}")


if __name__ == "__main__":
    main()
