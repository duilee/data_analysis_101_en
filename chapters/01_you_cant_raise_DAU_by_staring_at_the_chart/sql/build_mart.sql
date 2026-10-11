-- 1.3.3. (2) Build the user segment mart (mart_user_segment)
--
-- Apply the same CASE as classify_segment.sql (1.3.2.2) to the daily metrics built by
-- build_metrics_daily.sql to get each day's segment (user_seg); yesterday's segment (user_seg_from)
-- comes from the same user's previous-date row via the window function lag. A user who signed up
-- today has no previous row, so it is NULL.
-- When changing thresholds (new window, heavy cut, boundary days), update the CASE in both classify_segment.sql and this file identically.
-- Run build_metrics_daily.sql first.

CREATE OR REPLACE TABLE mart_user_segment AS
WITH seg AS (
  SELECT target_date, user_id,
    CASE
      WHEN days_since_signup < 7           THEN 'new'
      WHEN active_day_count >= 5           THEN 'heavy'
      WHEN active_day_count BETWEEN 1 AND 4 THEN 'light'
      WHEN last_active_date >= target_date - INTERVAL 30 DAY THEN 'risk'
      ELSE 'dormant'
    END AS user_seg
  FROM user_metrics_daily
)
SELECT
  target_date, user_id,
  lag(user_seg) OVER (PARTITION BY user_id ORDER BY target_date)
    AS user_seg_from,
  user_seg
FROM seg;
