"""Example data generator for the lifetime-estimation practice.

Writes the new cohort's 7-day observed retention (D0~D7) to data/cohort_retention.csv.
In a real production setting this would be one cohort's slice of a cohort-retention mart
that is aggregated daily from the raw event log. Here, for reproducibility, we fix the
observed values of a hypothetical cohort that signed up 7 days ago as constants.

- D0 = 1.0 (by definition, everyone is active on signup day)
- D1~D7 = one realistic curve with a first-day cliff followed by a gentle deceleration

These values deliberately do NOT sit exactly on a point of the power-law catalog grid.
That is why Case 2 (catalog matching) returns a small non-zero SSE rather than 0.
"""

import os
import sys

import pandas as pd

# Force UTF-8 so output is not garbled (cp949) when captured through a pipe; no effect on direct console output
sys.stdout.reconfigure(encoding="utf-8")

# The new cohort's 7-day observed retention (day, retention)
COHORT_RETENTION = [
    (0, 1.000),
    (1, 0.341),
    (2, 0.295),
    (3, 0.273),
    (4, 0.260),
    (5, 0.252),
    (6, 0.247),
    (7, 0.244),
]


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)

    df = pd.DataFrame(COHORT_RETENTION, columns=["day", "retention"])
    out_path = os.path.join(out_dir, "cohort_retention.csv")
    df.to_csv(out_path, index=False)

    print(f"Done: {out_path} ({len(df)} rows)")
    print(f"  D1~D7 area = {df.loc[df['day'].between(1, 7), 'retention'].sum():.3f}")


if __name__ == "__main__":
    main()
