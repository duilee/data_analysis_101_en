-- 1.3.2.1. Build the derived metrics (as of today, target date 2026-05-20)
--
-- LEFT JOIN user_master with user_activity, aggregate per user, and compute the 3 metrics
-- days_since_signup / active_day_count / last_active_date (+ d0_active for the DAU cross-tab),
-- saved to the user_metrics table. (Input for the next step, classify_segment.sql)
-- The signup day always has a record (signup = first record), so no user has zero activity rows.
-- Prerequisite: the two source CSVs are registered as tables (notebook step 0)
--   CREATE TABLE user_master   AS SELECT * FROM read_csv_auto('data/user_master.csv');
--   CREATE TABLE user_activity AS SELECT * FROM read_csv_auto('data/user_activity.csv');

CREATE OR REPLACE TABLE user_metrics AS
SELECT
  m.user_id,
  -- 1. Days since signup (first record) (signup day = 0)
  datediff('day', m.first_active_date, DATE '2026-05-20') AS days_since_signup,
  -- 2. Number of days with a record in the last 7 days (including the target date)
  count_if(a.event_date BETWEEN DATE '2026-05-20' - INTERVAL 6 DAY
                            AND DATE '2026-05-20') AS active_day_count,
  -- 3. Last record date (always present, since the signup day is guaranteed to have a record)
  max(CASE WHEN a.event_date <= DATE '2026-05-20'
      THEN a.event_date END) AS last_active_date,
  -- (+) Logged something today?
  max(CASE WHEN a.event_date = DATE '2026-05-20'
      THEN 1 ELSE 0 END) AS d0_active
FROM user_master m LEFT JOIN user_activity a USING (user_id)
GROUP BY m.user_id, m.first_active_date;
