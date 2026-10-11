-- 1.3.3. (1) Daily derived metrics (user_metrics_daily)
--
-- Same metric definitions as build_metrics.sql (1.3.2.1), plus a date axis. Join a calendar
-- (generate_series, 2026-04-20 ~ 2026-05-20, 31 days) with the user master to compute the 3 metrics
-- per date x user; users who had not signed up yet on a given date are filtered out by the join
-- condition (first_active_date <= target_date).
-- When changing the 'last 7 days' activity window, update INTERVAL 6 DAY in both build_metrics.sql and this file.
-- Prerequisite: the two source CSVs are registered as tables (notebook step 0)
--   CREATE TABLE user_master   AS SELECT * FROM read_csv_auto('data/user_master.csv');
--   CREATE TABLE user_activity AS SELECT * FROM read_csv_auto('data/user_activity.csv');

CREATE OR REPLACE TABLE user_metrics_daily AS
SELECT
  d.target_date::DATE AS target_date, m.user_id,
  datediff('day', m.first_active_date, d.target_date) AS days_since_signup,
  count_if(a.event_date BETWEEN d.target_date - INTERVAL 6 DAY
                            AND d.target_date) AS active_day_count,
  max(CASE WHEN a.event_date <= d.target_date
      THEN a.event_date END) AS last_active_date
FROM generate_series(DATE '2026-04-20', DATE '2026-05-20', INTERVAL 1 DAY)
     AS d(target_date)
JOIN user_master m ON m.first_active_date <= d.target_date
LEFT JOIN user_activity a USING (user_id)
GROUP BY d.target_date, m.user_id, m.first_active_date;
