# Chapter 12. We're Logging Events, So Why Can't We Get a Conversion Rate?

Even when the taxonomy document is right, logs break quietly after a release — an event stops arriving, arrives twice, or arrives with
an empty value. Using 30 days of logs from a fictional content app (five incidents planted in the 3.5.0 release on August 25 — all five are
caught by the standard thresholds), this practice code builds daily marts, compares against one week earlier to catch anomalies, and assembles a one-page report to send to Slack.

- **12.7.2. Build the daily marts.** From the raw log, build an event mart (counts by date, platform, and event) and a property fill-rate mart with DuckDB.
- **12.7.3. Detect event-count anomalies.** Compare the basis date (D-2) with one week earlier (D-9), find events that cross the ±60% / at-least-50-events thresholds, and plot their 30-day trend.
- **12.7.4. Detect missing-property anomalies.** Find (event, property) pairs whose not-null ratio dropped by more than 60%.
- **12.7.5. Build the report.** Assemble the results into Slack-formatted text (sending is a one-line comment).

## How to run

```bash
python generate_data.py              # generate example data (3 CSVs under data/, fixed seed)
jupyter notebook log_monitoring.ipynb  # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Generator for 30 days of synthetic logs + two taxonomy documents. Plants five release incidents on 8/25 (see the header comment — all five are caught) |
| `data/event_log.csv` | `event_time, user_id, platform, app_version, event_name, screen_name, properties(JSON)` — about 170K rows |
| `data/taxonomy_events.csv` | Event document (name, type, source, platform, screen, description, status, lifetime, version added) |
| `data/taxonomy_properties.csv` | Property document (name, scope event/user, type, allowed values, description, attached events) |
| `sql/mart_event_daily.sql` | Daily event mart (same as the notebook inline query) |
| `sql/mart_event_param_daily.sql` | Daily property fill-rate mart |
| `sql/event_count_anomaly.sql` | Event-count anomaly detection, D-2 vs D-9 (basis date, threshold, and minimum count in the `params` CTE) |
| `sql/param_null_anomaly.sql` | Property fill-rate anomaly detection |
| `img/` | Two trend figures saved by the notebook (for the book text) |
| `extra/taxonomy_check.py`, `extra/sql/` | Appendix: taxonomy document rule checks + document-vs-log comparison (book section 12.6.1). Run from inside `extra/` |
| `log_monitoring.ipynb` | Notebook for 12.7.2 to 12.7.5 |
