-- 1.3.2.2. Classify into 5 segments by fixed rules (as of today, target date 2026-05-20)
--
-- Takes the 3 metrics in the user_metrics table built by the previous step (build_metrics.sql)
-- and classifies each user into one of 5 segments (new / heavy / light / risk / dormant) with a single CASE WHEN.

SELECT
  *,
  CASE
    WHEN days_since_signup < 7           THEN 'new'
    WHEN active_day_count >= 5           THEN 'heavy'
    WHEN active_day_count BETWEEN 1 AND 4 THEN 'light'
    -- active_day_count = 0 means no record in the last 7 days, so
    -- risk vs. dormant only needs to check whether the last record is within 30 days.
    WHEN last_active_date >= DATE '2026-05-20' - INTERVAL 30 DAY THEN 'risk'
    ELSE 'dormant'
  END AS user_seg
FROM user_metrics
ORDER BY user_id;
