-- 11.6.4) fact 1 — subscription events (one row per purchase/renewal/cancel/refund)
--
-- Attaches price_usd through the exchange-rate join and the duration (trial_days for trials) through the SKU join.
-- Prerequisite: run stg_views.sql and dim_tables.sql first.
-- Prerequisite: run from the chapter folder (read_csv_auto paths are relative to data/)

-- fact 1: subscription events (grain: one row per purchase/renewal/cancel/refund event)
CREATE OR REPLACE TABLE fact_subscription_events AS
SELECT s.sub_event_id, s.event_date, s.received_date, s.user_id, s.sku_id, s.event_type, s.is_trial,
       s.event_time, s.price_local, s.currency,
       s.price_local * r.rate_to_usd AS price_usd,                            -- exchange-rate join
       CAST(CASE WHEN s.is_trial THEN k.trial_days ELSE k.duration_days END AS INTEGER) AS period_days
FROM stg_subscription_events s
LEFT JOIN stg_exchange_rates r ON r.date = s.event_date AND r.currency = s.currency
JOIN dim_sku k USING (sku_id);
