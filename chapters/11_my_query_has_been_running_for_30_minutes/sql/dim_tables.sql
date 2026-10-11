-- 11.6.4) dimension — user daily snapshot · SKU
--
-- Slowly changing attributes (country, app version) are stacked as daily snapshots; the 'current state' is read through the _latest view.
-- Prerequisite: run stg_views.sql first.
-- Prerequisite: run from the chapter folder (read_csv_auto paths are relative to data/)

-- dim: user × date snapshot — slowly changing attributes are simply captured every day
CREATE OR REPLACE TABLE dim_user_daily AS
SELECT snapshot_date AS date, user_id, platform, country, app_version, install_date,
       snapshot_date - install_date AS days_since_install
FROM stg_user_snapshots;

CREATE OR REPLACE VIEW dim_user_latest AS                 -- for when you need the 'current state'
SELECT * FROM dim_user_daily
QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date DESC) = 1;

CREATE OR REPLACE TABLE dim_sku AS SELECT * FROM stg_sku;
