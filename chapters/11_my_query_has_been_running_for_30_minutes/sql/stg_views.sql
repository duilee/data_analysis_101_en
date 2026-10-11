-- 11.6.3) staging — one view per source
--
-- Only normalizes names and types, drops re-sent duplicates and excludes system events. No joins, aggregation or business logic.
-- Prerequisite: run from the chapter folder (read_csv_auto paths are relative to data/)

CREATE OR REPLACE VIEW stg_events AS
SELECT event_id, user_id, event_name, session_id,
       CAST(event_time AS TIMESTAMP)    AS event_time,
       CAST(received_time AS TIMESTAMP) AS received_time,
       CAST(event_time AS DATE)         AS event_date,
       CAST(received_time AS DATE)      AS received_date,
       properties
FROM read_csv_auto('data/events.csv')
WHERE user_id IS NOT NULL
  AND event_name NOT LIKE 'system%'                                            -- drop system events
  AND event_name <> 'heartbeat'
QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY received_time) = 1;  -- drop re-sent duplicates

CREATE OR REPLACE VIEW stg_subscription_events AS
SELECT sub_event_id, user_id, LOWER(event_type) AS event_type, sku_id, is_trial,
       CAST(event_time AS TIMESTAMP)    AS event_time,
       CAST(received_time AS TIMESTAMP) AS received_time,
       CAST(event_time AS DATE)         AS event_date,
       CAST(received_time AS DATE)      AS received_date,
       price_local, UPPER(currency) AS currency
FROM read_csv_auto('data/subscription_events.csv')
QUALIFY ROW_NUMBER() OVER (PARTITION BY sub_event_id ORDER BY received_time) = 1;

CREATE OR REPLACE VIEW stg_user_snapshots AS
SELECT snapshot_date, user_id, LOWER(platform) AS platform, UPPER(country) AS country,
       app_version, install_date
FROM read_csv_auto('data/user_snapshots.csv');

CREATE OR REPLACE VIEW stg_sku AS
SELECT sku_id, duration_days, trial_days, base_price_usd FROM read_csv_auto('data/sku.csv');

CREATE OR REPLACE VIEW stg_exchange_rates AS
SELECT date, UPPER(currency) AS currency, rate_to_usd FROM read_csv_auto('data/exchange_rates.csv');
