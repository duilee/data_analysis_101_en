-- 11.6.2) Pulling straight from raw — answering with one query and no mart
--
-- Joins the CSVs directly to get active subscribers and revenue (USD) by date, platform and country.
-- Deduplication, currency cleanup, period expansion, the snapshot join and the exchange-rate join are all inside one query.
-- Prerequisite: run from the chapter folder (read_csv_auto paths are relative to data/)

WITH sub AS (                     -- subscription events: dedupe + normalize names/currency + attach SKU duration
  SELECT s.user_id, LOWER(s.event_type) AS event_type, s.sku_id,
         CAST(s.event_time AS TIMESTAMP) AS event_time,
         s.price_local, UPPER(s.currency) AS currency,
         CAST(CASE WHEN s.is_trial THEN k.trial_days ELSE k.duration_days END AS INTEGER) AS period_days
  FROM read_csv_auto('data/subscription_events.csv') s
  JOIN read_csv_auto('data/sku.csv') k USING (sku_id)
  QUALIFY ROW_NUMBER() OVER (PARTITION BY s.sub_event_id ORDER BY s.received_time) = 1
),
periods AS (                      -- one purchase/renewal = one subscription period
  SELECT user_id, CAST(event_time AS DATE) AS start_date,
         CAST(event_time AS DATE) + period_days - 1 AS end_date
  FROM sub WHERE event_type IN ('purchase', 'renewal')
),
ends AS (                         -- cancel/refund ends the subscription that day
  SELECT user_id, MIN(CAST(event_time AS DATE)) AS end_date
  FROM sub WHERE event_type IN ('cancel', 'refund') GROUP BY user_id
),
expanded AS (                     -- expand each period into individual dates
  SELECT user_id, CAST(UNNEST(generate_series(start_date, end_date, INTERVAL 1 DAY)) AS DATE) AS date
  FROM periods
),
active AS (
  SELECT DISTINCT x.user_id, x.date
  FROM expanded x LEFT JOIN ends e USING (user_id)
  WHERE (e.end_date IS NULL OR x.date < e.end_date) AND x.date <= DATE '2026-06-29'
),
snap AS (                         -- user attributes as of that day
  SELECT snapshot_date, user_id, platform, UPPER(country) AS country
  FROM read_csv_auto('data/user_snapshots.csv')
),
revenue AS (                      -- that day's payments converted to USD (refunds are negative)
  SELECT CAST(s.event_time AS DATE) AS date, s.user_id,
         SUM(s.price_local * r.rate_to_usd) AS revenue_usd
  FROM sub s
  JOIN read_csv_auto('data/exchange_rates.csv') r
    ON r.date = CAST(s.event_time AS DATE) AND r.currency = s.currency
  GROUP BY 1, 2
)
SELECT a.date, sn.platform, sn.country,
       COUNT(DISTINCT a.user_id)        AS active_subscribers,
       COALESCE(SUM(rv.revenue_usd), 0) AS revenue_usd
FROM active a
JOIN snap sn ON sn.user_id = a.user_id AND sn.snapshot_date = a.date
LEFT JOIN revenue rv ON rv.user_id = a.user_id AND rv.date = a.date
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
