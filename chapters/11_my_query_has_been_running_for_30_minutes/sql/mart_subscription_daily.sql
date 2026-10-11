-- 11.6.5) mart — aggregate by date × platform × country × SKU × trial flag (one partition = one batch run)
--
-- Example of the notebook's MART_SQL with {partition_date} expanded to 2026-06-14. The batch repeats this statement with a different date each time.
-- Prerequisite: the facts and dimensions from 11.6.4 must exist; run the CREATE TABLE below first.
-- Prerequisite: run from the chapter folder (read_csv_auto paths are relative to data/)

CREATE OR REPLACE TABLE mart_subscription_daily (
  date DATE, platform VARCHAR, country VARCHAR, sku_id VARCHAR, is_trial BOOLEAN,
  new_count BIGINT, renewal_count BIGINT, cancel_count BIGINT, refund_count BIGINT,
  revenue_usd DOUBLE, active_subscribers BIGINT
);

DELETE FROM mart_subscription_daily WHERE date = DATE '2026-06-14';
INSERT INTO mart_subscription_daily
WITH ev AS (                                  -- that day's subscription events
  SELECT f.event_date AS date, d.platform, d.country, f.sku_id, f.is_trial,
         f.event_type, f.price_usd, NULL AS active_user
  FROM fact_subscription_events f
  JOIN dim_user_daily d ON d.user_id = f.user_id AND d.date = f.event_date
  WHERE f.event_date = DATE '2026-06-14'
),
act AS (                                      -- that day's active subscribers
  SELECT a.date, d.platform, d.country, a.sku_id, a.is_trial,
         NULL AS event_type, 0 AS price_usd, a.user_id AS active_user
  FROM fact_subscriber_daily a
  JOIN dim_user_daily d ON d.user_id = a.user_id AND d.date = a.date
  WHERE a.date = DATE '2026-06-14'
)
SELECT date, platform, country, sku_id, is_trial,
       COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) AS new_count,
       COUNT(CASE WHEN event_type = 'renewal'  THEN 1 END) AS renewal_count,
       COUNT(CASE WHEN event_type = 'cancel'   THEN 1 END) AS cancel_count,
       COUNT(CASE WHEN event_type = 'refund'   THEN 1 END) AS refund_count,
       SUM(price_usd)                                      AS revenue_usd,
       COUNT(DISTINCT active_user)                         AS active_subscribers
FROM (SELECT * FROM ev UNION ALL SELECT * FROM act)
GROUP BY ALL;
