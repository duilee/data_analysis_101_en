# Chapter 1. You Can't Raise DAU by Staring at the DAU Chart

Practice code for user-segment analysis. We split the DAU of a fictional habit-tracker app, "RoutineLog," into 5 user segments
and diagnose the health of the service from several angles using the movement between segments (Flow) and ratio metrics.

- **1.3.2.** Build 3 derived metrics (`user_metrics`) from the two source tables (`user_master`, `user_activity`) and classify them by fixed rules into 5 segments (new / heavy / light / risk / dormant). Cross segments with "logged today?" to see the composition of DAU.
- **1.3.3.** Stack a month of date x user segment snapshots and attach yesterday's segment with `lag` to build a mart that can track segment changes.
- **1.3.4.** Analyze that mart from three angles: distribution (Stock), transition matrix (Flow), and ratio metrics (HURR/CURR/Heavy Loss/Light Loss/Reactivation).
- **1.3.5.** Self-join the month of mart data to track where users who were heavy or new 30 days ago ended up today (N-day change).

## How to run

```bash
python generate_data.py               # generate example data (data/user_master.csv, user_activity.csv)
jupyter notebook dau_segment.ipynb    # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Synthetic example data generator for the segment practice (fixed seed) |
| `data/user_master.csv` | Per-user signup info (`user_id, first_active_date`) |
| `data/user_activity.csv` | Log of the days a user logged a habit check-in (`user_id, event_date`) |
| `sql/build_metrics.sql` | Compute the 3 derived metrics (+ `d0_active` for the DAU cross-tab) -> `user_metrics` table (as of today) |
| `sql/classify_segment.sql` | Classify the 3 metrics in `user_metrics` into 5 segments |
| `sql/build_metrics_daily.sql` | Compute the 3 derived metrics per calendar day (31 days) x user -> `user_metrics_daily` table |
| `sql/build_mart.sql` | Build the mart: daily segment classification + yesterday's segment via `lag` (one month) |
| `sql/stock_distribution.sql` | Daily segment distribution (Stock) |
| `sql/transition_matrix.sql` | Segment transition matrix (Flow) |
| `sql/segment_kpi.sql` | The 5 transition-based ratio metrics |
| `sql/nday_tracking.sql` | Track segment change after N days |
| `dau_segment.ipynb` | Practice notebook for section 1.3 (1.3.1-1.3.5) |
