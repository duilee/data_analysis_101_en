"""Finding User Usage Patterns with Machine Learning -- example data generator.

Builds synthetic data modeled on the daily usage log of alarm-app users.
Four personas (usage types) are 'planted' and each user is unrolled into two weeks of daily rows,
so you can confirm that the KMeans in the practice recovers these personas (almost) exactly.

- data/alarm_daily.csv : daily alarm features (input to the feature-engineering SQL)
- data/user_master.csv : user_id, new_flag (new/existing), retained_d7 (D7 retention; for the KPI)

Alarm times are expressed as integer minutes (0-1439).
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np
import pandas as pd

# Keep stdout UTF-8 when it is captured through a pipe with a non-UTF-8 locale (no effect on direct console output)
sys.stdout.reconfigure(encoding="utf-8")

SEED = 42
START = pd.Timestamp("2024-09-02")  # a Monday
N_DAYS = 14                          # 2 weeks (10 weekdays + 4 weekend days)

# 'True' centroid per persona (planted to match the cluster result of a real service).
#   alarms          : alarm count (daily average)
#   snooze/used/attempt : per-alarm values (the SQL converts ..._cnt / scheduled_cnt)
#   ttd             : time to dismiss (minutes, per alarm)
#   wake            : time from first ring to last dismiss (minutes)
#   interval        : interval between alarms (minutes) -- target mean that accounts for single-alarm days counting as 0
#   count           : number of users in the persona (shares 4.12/57.86/13.00/25.02% fitted to N=2400)
PERSONAS = [
    dict(name="weak_minimalist", count=99,  retention=0.30, new_prob=0.30,
         alarms=1.42, interval=8.73, snooze=0.91, used=0.91, attempt=1.27, ttd=68.42, wake=75.18),
    dict(name="minimalist",      count=1389, retention=0.58, new_prob=0.25,
         alarms=1.19, interval=3.08, snooze=0.52, used=0.95, attempt=1.31, ttd=6.14,  wake=8.0),
    dict(name="weak_maximalist", count=312, retention=0.40, new_prob=0.60,
         alarms=2.81, interval=47.92, snooze=0.38, used=0.78, attempt=0.91, ttd=8.36, wake=84.27),
    dict(name="trying_maximalist", count=600, retention=0.55, new_prob=0.55,
         alarms=2.17, interval=18.44, snooze=0.55, used=0.83, attempt=1.18, ttd=12.07, wake=41.33),
]

BASE = os.path.dirname(os.path.abspath(__file__))


def _noisy(rng, mean, rel=0.08, lo=0.0):
    """Positive value around mean with relative noise (rel)."""
    return max(lo, rng.normal(mean, abs(mean) * rel + 1e-9))


def _stoch_round(rng, x):
    """Stochastic rounding: keeps the mean at x while limiting the variance to +-1.
    (round(x) biases the mean for small values, and Poisson has too much variance and scatters the clusters)"""
    f = math.floor(x)
    return int(f + (1 if rng.random() < (x - f) else 0))


def main() -> None:
    rng = np.random.default_rng(SEED)

    daily_rows = []
    master_rows = []
    dates = [START + pd.Timedelta(days=d) for d in range(N_DAYS)]

    uid = 0
    for p in PERSONAS:
        mu = p["alarms"]
        lam = max(mu - 1.0, 0.0)                 # daily alarm count = 1 + Poisson(mu-1)
        q = 1.0 - math.exp(-lam) if lam > 0 else 0.0   # P(alarms > 1)
        # Single-alarm days (interval 0) averaged via COALESCE give q*gap, so back out gap = target interval / q
        gap = p["interval"] / q if q > 0 else 0.0

        for _ in range(p["count"]):
            uid += 1
            user_id = f"u{uid:05d}"
            new_flag = bool(rng.random() < p["new_prob"])
            retained = bool(rng.random() < p["retention"])
            master_rows.append((user_id, new_flag, retained))

            for dt in dates:
                cnt = 1 + int(rng.poisson(lam))

                first_min = int(rng.normal(390, 25))                 # start of the wake-up alarms (minutes)
                if cnt > 1:
                    g = max(1.0, rng.normal(gap, gap * 0.15 + 1e-9))
                    last_min = first_min + int(round(g * (cnt - 1)))
                else:
                    last_min = first_min                             # single alarm -> no interval

                # Count features use stochastic rounding (keeps the mean, minimal variance -> clusters don't scatter)
                snooze_cnt = _stoch_round(rng, p["snooze"] * cnt)
                mission_used = _stoch_round(rng, p["used"] * cnt)
                mission_attempt = mission_used + _stoch_round(rng, max(0.0, p["attempt"] - p["used"]) * cnt)
                total_ttd = round(_noisy(rng, p["ttd"]) * cnt, 1)    # time to dismiss (per alarm) x cnt
                wake = round(_noisy(rng, p["wake"]), 1)              # first ring to last dismiss (minutes)

                daily_rows.append((
                    dt.strftime("%Y-%m-%d"), user_id, cnt, first_min, last_min,
                    snooze_cnt, mission_used, mission_attempt, total_ttd, wake,
                ))

    daily = pd.DataFrame(daily_rows, columns=[
        "local_date", "user_id", "scheduled_cnt", "first_scheduled_min", "last_scheduled_min",
        "snooze_alarm_cnt", "mission_used_cnt", "mission_attempt_cnt",
        "total_time_to_dismiss", "first_ring_to_last_dismiss",
    ])
    master = pd.DataFrame(master_rows, columns=["user_id", "new_flag", "retained_d7"])
    # Lowercase true/false so DuckDB infers BOOLEAN
    for col in ["new_flag", "retained_d7"]:
        master[col] = master[col].map({True: "true", False: "false"})

    out_dir = os.path.join(BASE, "data")
    os.makedirs(out_dir, exist_ok=True)
    daily.to_csv(os.path.join(out_dir, "alarm_daily.csv"), index=False)
    master.to_csv(os.path.join(out_dir, "user_master.csv"), index=False)

    n_users = sum(p["count"] for p in PERSONAS)
    print(f"alarm_daily.csv : {len(daily):,} rows ({n_users:,} users x {N_DAYS} days)")
    print(f"user_master.csv : {len(master):,} rows")
    print("persona mix     :", {p["name"]: p["count"] for p in PERSONAS})


if __name__ == "__main__":
    main()
