-- 11.6.4) fact 2 — daily active-subscription snapshot (one row per subscribed user × date)
--
-- Expands each purchase/renewal period into dates and excludes everything after a cancel/refund. The source of the semi-additive 'active subscribers' count.
-- Prerequisite: run fact_subscription_events.sql first.
-- Prerequisite: run from the chapter folder (read_csv_auto paths are relative to data/)

-- fact 2: daily active-subscription snapshot (grain: one row per subscribed user × date)
CREATE OR REPLACE TABLE fact_subscriber_daily AS
WITH periods AS (
  SELECT user_id, sku_id, is_trial, event_date AS start_date,
         event_date + period_days - 1 AS end_date
  FROM fact_subscription_events WHERE event_type IN ('purchase', 'renewal')
),
ends AS (
  SELECT user_id, MIN(event_date) AS end_date
  FROM fact_subscription_events WHERE event_type IN ('cancel', 'refund') GROUP BY user_id
),
expanded AS (
  SELECT user_id, sku_id, is_trial,
         CAST(UNNEST(generate_series(start_date, end_date, INTERVAL 1 DAY)) AS DATE) AS date
  FROM periods
)
SELECT x.date, x.user_id, x.sku_id, x.is_trial
FROM expanded x LEFT JOIN ends e USING (user_id)
WHERE (e.end_date IS NULL OR x.date < e.end_date) AND x.date <= DATE '2026-06-29'
QUALIFY ROW_NUMBER() OVER (PARTITION BY x.date, x.user_id ORDER BY x.is_trial) = 1;   -- unique key (date, user_id)
