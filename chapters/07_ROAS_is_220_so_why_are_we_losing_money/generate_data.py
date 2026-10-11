"""ROAS Is 220%, So Why Are We Losing Money? — example data generator for the unit economics practice.

Produces three raw, unprocessed logs. The practice is to compute the tables
completed in the chapter directly from these logs and reproduce them.

  - marketing_costs : month x channel marketing cost (media cost / other cost split)
  - users           : roster of acquired users (channel, signup date — includes users who never paid)
  - payments        : one row per payment (user, payment date, amount = revenue)

Planted answers (the targets the practice reproduces — all values from the chapter's tables):
  - 2025-04 paid acquisitions 2,500 users — search 40% / display 20% / retargeting 10% / brand 30%
  - Fully-loaded CAC by channel: 11,500 / 5,700 / 3,600 / 28,000 KRW
    → paid-total CAC: media-cost basis 12,000 KRW → fully-loaded 14,500 KRW
  - LTV by channel (contribution margin, 12-month actual — same one-year basis as Chapter 4): 33,000 / 5,900 / 24,000 / 24,000 KRW
    (organic 26,000 KRW) → paid-total LTR about 37,000 KRW, LTV about 24,000 KRW
  - 2025-04 search cohort payback curve: 0.37 / 0.70 / 1.02 / 1.30 / 1.57 / 1.80
    (monthly contribution margin 4.2M / 3.9M / 3.6M / 3.3M / 3.0M / 2.7M KRW → payback in month 3)

The 65% contribution margin ratio (35% variable cost) is the chapter's 2.1 assumption and is used as a constant in the notebook.
All amounts in the logs are 'revenue'; the conversion to contribution margin is done in the practice itself.

The seed is fixed, so everyone who runs this gets exactly the same data.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

# Prevent non-ASCII output from being garbled under cp949 when stdout is piped
sys.stdout.reconfigure(encoding="utf-8")

SEED = 42
BASE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(SEED)

CM_RATIO = 0.65        # contribution margin ratio (chapter 2.1: 35% variable cost)
HORIZON = 12           # LTV measurement horizon (months) — mature cohorts fill this window (same one-year basis as Chapter 4)
DATA_END = pd.Period("2026-06", "M")   # last month of the payment log

# ---------------------------------------------------------------------------
# 1) Per-channel 'monthly contribution margin per user' schedule (KRW, months 0-11 after acquisition)
#    — monotonically decreasing curves reverse-engineered so the 12-month sum equals the
#      LTV (contribution margin) in the chapter's channel table
# ---------------------------------------------------------------------------

SCHEDULES: dict[str, list[float]] = {
    # search: 12-month sum 33,000 — April cohort pays back in month 3 (M+2); March cohort (quality 0.93) in month 4
    "search": [4200, 3900, 3600, 3300, 3000, 2700, 2450, 2250, 2050, 1900, 1850, 1800],
    # display: sum 5,900 — barely clears its CAC of 5,700 only in month 12
    "display": [800, 700, 620, 550, 500, 460, 430, 400, 380, 360, 350, 350],
    # retargeting: heavily front-loaded (the last-click-attribution overstatement story, sum 24,000)
    "retargeting": [7000, 4800, 3300, 2300, 1600, 1150, 850, 700, 600, 600, 550, 550],
    # brand/other: gentle curve (sum 24,000 — falls short of its CAC of 28,000)
    "brand": [2600, 2450, 2300, 2150, 2050, 1950, 1900, 1850, 1800, 1700, 1650, 1600],
    # organic: baseline (sum 26,000)
    "organic": [3800, 3300, 2900, 2550, 2300, 2100, 1950, 1800, 1650, 1300, 1200, 1150],
}
for ch, sched in SCHEDULES.items():
    assert len(sched) == HORIZON, ch

# ---------------------------------------------------------------------------
# 2) Monthly acquisition volume (users) — a scenario where marketing ramped up sharply in Mar-Apr 2025
#    The 40/20/10/30 mix holds exactly in 2025-04 (search 1,000 users = the chapter's payback curve table)
# ---------------------------------------------------------------------------

PAID = ["search", "display", "retargeting", "brand"]

def _mix(total_paid: int) -> dict[str, int]:
    """Split paid acquisitions in a 40/20/10/30 mix."""
    return {
        "search": int(total_paid * 0.4),
        "display": int(total_paid * 0.2),
        "retargeting": int(total_paid * 0.1),
        "brand": int(total_paid * 0.3),
    }

COHORTS: dict[pd.Period, dict[str, int]] = {}
# Mature window (2024-01 to 2024-12: cohorts that are 12+ months past acquisition as of the 2025-04 reference month) plus bridging months on either side
for m in pd.period_range("2023-07", "2024-12", freq="M"):
    COHORTS[m] = {**_mix(300), "organic": 120}
# 2025: peak-season ramp-up in Mar-Apr
for m, paid, org in [("2025-01", 900, 315), ("2025-02", 1000, 350),
                     ("2025-03", 2175, 700), ("2025-04", 2500, 800),
                     ("2025-05", 1300, 450), ("2025-06", 1200, 420)]:
    COHORTS[pd.Period(m, "M")] = {**_mix(paid), "organic": org}

# ---------------------------------------------------------------------------
# 3) Marketing costs (marketing_costs.csv)
#    Target fully-loaded CAC x acquisitions = total cost. Split into media cost / other cost.
# ---------------------------------------------------------------------------

CAC_TARGET = {"search": 11500, "display": 5700, "retargeting": 3600, "brand": 28000}
MEDIA_SHARE = {"search": 0.86, "display": 0.88, "retargeting": 0.90, "brand": 0.80}

# Cohort quality multiplier — the 2025-03 cohort is slightly weaker than April's
# (a device to show that payback speed differs by cohort even within the same channel:
#  for search, the March cohort breaks even in month 4, the April cohort in month 3)
QUALITY = {pd.Period("2025-03", "M"): 0.93}

cost_rows = []
for month, sizes in COHORTS.items():
    focal = month in (pd.Period("2025-04", "M"), pd.Period("2025-03", "M"))
    total_paid = sum(sizes[c] for c in PAID)
    for ch in PAID:
        n = sizes[ch]
        # The answer month (2025-04) uses the target CAC as-is; other months get +/-3% noise
        cac = CAC_TARGET[ch] if focal else CAC_TARGET[ch] * rng.normal(1, 0.03)
        fully = cac * n
        if focal and month == pd.Period("2025-04", "M") and ch == "brand":
            # For 2025-04, set brand media cost as the remainder so that the paid-total
            # media-cost CAC comes out to exactly 12,000 KRW (total minus the other channels' media cost)
            media_others = sum(CAC_TARGET[c] * sizes[c] * MEDIA_SHARE[c] for c in PAID[:-1])
            media = 12000 * total_paid - media_others
        else:
            media = fully * MEDIA_SHARE[ch]
        focal = month == pd.Period("2025-04", "M")   # rounding precision: to the won only for April
        cost_rows.append({
            "month": month.to_timestamp().date(),
            "channel": ch,
            "media_cost_krw": int(round(media, -3)) if not focal else int(round(media)),
            "other_cost_krw": int(round(fully - media)) if focal else int(round(fully - media, -3)),
        })
costs = pd.DataFrame(cost_rows)

# ---------------------------------------------------------------------------
# 4) User roster (users.csv) + payment log (payments.csv)
#    For each cohort (channel x acquisition month) x elapsed month, convert the
#    'average contribution margin per user' schedule into a revenue total, then
#    draw individual payments that sum to that total.
# ---------------------------------------------------------------------------

# Per-channel payment participation probability (by elapsed month) and order-size multiplier — controls the number of payments
PART = {  # (participation probability for the first 6 months, probability for months 7-12)
    "search": ([0.90, 0.55, 0.40, 0.25, 0.20, 0.17], 0.12),
    "display": ([0.30, 0.20, 0.18, 0.14, 0.13, 0.10], 0.05),
    "retargeting": ([0.95, 0.70, 0.55, 0.40, 0.32, 0.25], 0.10),
    "brand": ([0.45, 0.35, 0.30, 0.26, 0.23, 0.20], 0.13),
    "organic": ([0.80, 0.50, 0.38, 0.24, 0.20, 0.17], 0.11),
}

user_rows, pay_rows = [], []
uid = 0
month_days = {}  # for spreading payment dates

for month, sizes in sorted(COHORTS.items()):
    for ch, n in sizes.items():
        if n == 0:
            continue
        ids = np.arange(uid, uid + n)
        uid += n
        # Signup date: spread uniformly within the month
        days = rng.integers(0, month.days_in_month, n)
        signup = month.to_timestamp() + pd.to_timedelta(days, unit="D")
        for i, s in zip(ids, signup):
            user_rows.append({"user_id": f"u{i:06d}", "channel": ch,
                              "signup_date": s.date()})
        # Generate payments by elapsed month (nothing after the end of observation)
        head, tail_p = PART[ch]
        for k in range(HORIZON):
            pay_month = month + k
            if pay_month > DATA_END:
                break
            q = QUALITY.get(month, 1.0)
            target_rev = SCHEDULES[ch][k] * q / CM_RATIO * n   # total revenue this cohort generates this month
            if month != pd.Period("2025-04", "M"):           # the answer month (chapter's payback table) gets no noise
                target_rev *= rng.normal(1, 0.004)         # very mild noise
            p = head[k] if k < 6 else tail_p
            payers = ids[rng.random(n) < p]
            if len(payers) == 0:
                payers = rng.choice(ids, 1)
            # Order amounts: draw from a lognormal, then scale to hit the total exactly
            amounts = rng.lognormal(0, 0.35, len(payers))
            amounts = amounts / amounts.sum() * target_rev
            pdays = rng.integers(0, pay_month.days_in_month, len(payers))
            base_ts = pay_month.to_timestamp()
            for u, a, d in zip(payers, amounts, pdays):
                pay_rows.append({
                    "user_id": f"u{int(u):06d}",
                    "payment_date": (base_ts + pd.Timedelta(days=int(d))).date(),
                    "amount_krw": max(500, int(round(a, -2))),
                })

users = pd.DataFrame(user_rows)
payments = pd.DataFrame(pay_rows).sort_values(["payment_date", "user_id"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 5) Save + print summary
# ---------------------------------------------------------------------------

out = os.path.join(BASE, "data")
os.makedirs(out, exist_ok=True)
costs.to_csv(os.path.join(out, "marketing_costs.csv"), index=False)
users.to_csv(os.path.join(out, "users.csv"), index=False)
payments.to_csv(os.path.join(out, "payments.csv"), index=False)

print(f"marketing_costs : {len(costs):>9,} rows (month x channel cost)")
print(f"users           : {len(users):>9,} rows (acquired users)")
print(f"payments        : {len(payments):>9,} rows (payments)")
apr = costs[costs.month.astype(str) == "2025-04-01"]
n_apr = sum(COHORTS[pd.Period('2025-04', 'M')][c] for c in PAID)
print(f"2025-04 paid acquisitions {n_apr:,} users / fully-loaded cost "
      f"{(apr.media_cost_krw + apr.other_cost_krw).sum():,} KRW "
      f"(CAC {round((apr.media_cost_krw + apr.other_cost_krw).sum() / n_apr):,} KRW)")
