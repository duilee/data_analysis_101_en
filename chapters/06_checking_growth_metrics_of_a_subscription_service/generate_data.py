"""Checking the Growth Metrics of a Subscription Service — example data generator for the MRR analysis practice.

Builds a single 'payment log' table shaped like a Google Play Sales Report.

  - subscription_sales : per-payment log (order_number, order_charged_date,
                         product_id, sales_amount_krw)

Key design: a user ID column is deliberately NOT provided. As with a real store
report, the practice starts with identifying users by parsing the prefix of
order_number (same user) and its suffix (renewal number). The first payment has
no suffix, and renewals carry a "..1", "..2" style suffix (how Google's reports
actually behave).

Answers planted in advance (to be recovered at the end of the practice):
  - Monthly churn rate (CHURN_RATE) 5% -> the churn rate computed in the practice converges near this value
  - Expected subscription lifetime approximated as 1 / churn rate ~ 20 months (the LTV rule of thumb in the chapter's wrap-up)
  - A small number of plan upgrades/downgrades are planted so that a gap opens between GRR and NRR

The seed is fixed, so everyone who runs this gets exactly the same data.
"""

from __future__ import annotations

import os
import sys
from datetime import date

import numpy as np
import pandas as pd

# Keep stdout UTF-8 even when output is captured through a pipe (no effect on direct console output)
sys.stdout.reconfigure(encoding="utf-8")

SEED = 42
START = (2025, 1)          # sign-up month of the first cohort
END = (2026, 6)            # last payment month (data is generated through this month)
BASE_NEW_USERS = 60        # new paid subscribers in the first month
NEW_USER_GROWTH = 1.05     # monthly growth rate of new paid subscribers

PLANS = {"monthly_basic": 4900, "monthly_plus": 9900}
P_START_PLUS = 0.25        # probability of choosing the plus plan at first subscription

CHURN_RATE = 0.05          # * planted answer: 5% monthly churn
P_UPGRADE = 0.015          # probability of basic -> plus at renewal (source of expansion MRR)
P_DOWNGRADE = 0.010        # probability of plus -> basic at renewal (source of contraction MRR)
P_REACTIVATE = 0.015       # probability that a churned user re-subscribes in a given month

BASE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(SEED)


def month_seq(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Sequence of (year, month) from start through end, inclusive."""
    out, (y, m) = [], start
    while (y, m) <= end:
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def make_order_number(prefix: str, k: int) -> str:
    """Google-style order number. The first payment (k=0) has no suffix; renewals get '..k'."""
    return prefix if k == 0 else f"{prefix}..{k}"


MONTHS = month_seq(START, END)
rows = []
uid = 0

for i, (cy, cm) in enumerate(MONTHS):
    # number of new paid subscribers arriving this month (gentle growth + noise)
    n_new = int(BASE_NEW_USERS * NEW_USER_GROWTH ** i + rng.integers(-5, 6))
    for _ in range(n_new):
        uid += 1
        # user-unique prefix that looks like a real Google order number
        prefix = "GPA.{:04d}-{:04d}-{:04d}-{:05d}".format(
            rng.integers(1000, 9999), rng.integers(1000, 9999),
            rng.integers(1000, 9999), 10000 + uid)
        plan = "monthly_plus" if rng.random() < P_START_PLUS else "monthly_basic"
        anniversary = int(rng.integers(1, 29))    # billing day (1-28, guaranteed to exist in every month)

        # Walk month by month from the sign-up month to END, simulating payment / churn / reactivation
        k = 0                  # cumulative payment number (order_number suffix)
        active = True
        inactive_months = 0    # months elapsed since churn (re-subscription only after a gap of at least a month)
        for (y, m) in month_seq((cy, cm), END):
            if active:
                rows.append({
                    "order_number": make_order_number(prefix, k),
                    "order_charged_date": date(y, m, anniversary),
                    "product_id": plan,
                    "sales_amount_krw": PLANS[plan],
                })
                k += 1
                # decide whether to renew next month (* planted answer: 5% churn)
                if rng.random() < CHURN_RATE:
                    active = False
                    inactive_months = 0
                else:
                    r = rng.random()
                    if plan == "monthly_basic" and r < P_UPGRADE:
                        plan = "monthly_plus"          # expansion
                    elif plan == "monthly_plus" and r < P_DOWNGRADE:
                        plan = "monthly_basic"         # contraction
            else:
                # Churned state -> after a gap of at least one month, re-subscribe with low probability.
                # (Returning in the month right after churning would be indistinguishable from renew, so a gap is guaranteed)
                inactive_months += 1
                if inactive_months >= 2 and rng.random() < P_REACTIVATE:
                    active = True
                    anniversary = int(rng.integers(3, 29))
                    rows.append({
                        "order_number": make_order_number(prefix, k),
                        "order_charged_date": date(y, m, anniversary),
                        "product_id": plan,
                        "sales_amount_krw": PLANS[plan],
                    })
                    k += 1
                    if rng.random() < CHURN_RATE:
                        active = False
                        inactive_months = 0

sales = pd.DataFrame(rows).sort_values(["order_charged_date", "order_number"])

os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
out = os.path.join(BASE, "data", "subscription_sales.csv")
sales.to_csv(out, index=False)

print(f"Done: {out}")
print(f"  {len(sales):,} payments / {uid:,} users / period {MONTHS[0]} ~ {MONTHS[-1]}")
print(f"  Planted answer: {CHURN_RATE:.0%} monthly churn (expected lifetime ~ {1/CHURN_RATE:.0f} months)")
