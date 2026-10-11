"""How Much DAU Is This Feature Worth? — example data generator.

Builds synthetic data for the retention-analysis practice. Modeled on a daily active-user log,
it records one user's install date and each later return visit as rows.
Each platform's retention is generated to follow a *known* power law (y = a * d^b), so you can
confirm that curve_fit in the practice notebook recovers b (almost) exactly.

Columns: date, user_id, platform, country_code, install_flag
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

# Prevent non-ASCII output from being mangled by cp949 encoding when stdout is piped (no effect on direct console output)
sys.stdout.reconfigure(encoding="utf-8")

SEED = 42
START_DATE = pd.Timestamp("2026-01-01")
N_COHORT_DAYS = 90        # ~3 months of daily cohorts -> 3 basis_months
NEW_USERS_PER_DAY = 100   # new users per day per platform (Poisson variation)
MAX_DAY_DIFF = 28         # the query only uses day_diff 1~28, so simulate up to 28 days only

# The "true" retention curve parameters per platform: y(d) = a * d^b
# a is the starting point of the curve (≈ D1 retention), b is its shape (more negative = faster decay).
PLATFORM_PARAMS = {
    "ios":     {"a": 0.42, "b": -0.45},
    "android": {"a": 0.35, "b": -0.50},
}
COUNTRIES = ["KR", "US", "JP", "IN"]

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "active_daily.csv")


def true_retention(day: np.ndarray, a: float, b: float) -> np.ndarray:
    """Return the power-law retention probability y(d) = a * d^b, clipped to 0~1."""
    return np.clip(a * np.power(day, b), 0.0, 1.0)


def generate() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    days = np.arange(1, MAX_DAY_DIFF + 1)

    rows = []
    uid = 0
    for platform, params in PLATFORM_PARAMS.items():
        base_ret = true_retention(days, params["a"], params["b"])  # retention probability for day 1~28

        for d in range(N_COHORT_DAYS):
            install_date = START_DATE + pd.Timedelta(days=d)
            n_users = rng.poisson(NEW_USERS_PER_DAY)  # slight variation in the number of new users per day

            for _ in range(n_users):
                uid += 1
                user_id = f"u{uid:07d}"
                country = COUNTRIES[rng.integers(len(COUNTRIES))]

                # Install day: active + install_flag=True
                rows.append((install_date, user_id, platform, country, True))

                # For each of day_diff 1~28, return with the retention probability (with per-cohort noise)
                noise = rng.uniform(0.85, 1.15, size=MAX_DAY_DIFF)
                probs = np.clip(base_ret * noise, 0.0, 1.0)
                returned = rng.random(MAX_DAY_DIFF) < probs
                for offset in days[returned]:
                    visit_date = install_date + pd.Timedelta(days=int(offset))
                    rows.append((visit_date, user_id, platform, country, False))

    df = pd.DataFrame(
        rows, columns=["date", "user_id", "platform", "country_code", "install_flag"]
    )
    df = df.sort_values(["date", "platform", "user_id"]).reset_index(drop=True)
    return df


def main() -> None:
    df = generate()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    n_install = int(df["install_flag"].sum())

    out = df.copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    # Write lowercase true/false so DuckDB auto-infers the column as BOOLEAN
    out["install_flag"] = out["install_flag"].map({True: "true", False: "false"})
    out.to_csv(OUT_PATH, index=False)

    print(f"wrote {len(df):,} rows -> {OUT_PATH}")
    print(f"  installs   : {n_install:,}")
    print(f"  platforms  : {sorted(df['platform'].unique())}")
    print(f"  date range : {out['date'].min()} ~ {out['date'].max()}")


if __name__ == "__main__":
    main()
