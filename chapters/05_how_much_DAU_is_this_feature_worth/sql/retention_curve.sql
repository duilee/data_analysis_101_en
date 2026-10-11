-- New-user retention curve (input for 5.8.2)
--
-- Reads the example CSV (data/active_daily.csv) with DuckDB and builds the retention curve.
-- Key pattern: self-join the install cohort (installs) with all activity (base) on the same user_id
-- and compute the retention rate for each day_diff (days since install).
--
-- Standalone use: run the two CREATE VIEW statements (base, installs) first, then the main query
-- (identical to the two cells in notebook section 5.8.2).

CREATE VIEW base AS
  SELECT date AS event_date, user_id, platform, install_flag
  FROM read_csv_auto('data/active_daily.csv');

-- Keep only install (= new acquisition) events. basis_month is the monthly cohort bucket
CREATE VIEW installs AS
  SELECT event_date AS install_date, user_id, platform,
         DATE_TRUNC('month', event_date) AS basis_month
  FROM base
  WHERE install_flag = TRUE;

-- Self-join installing users (i) with their later visits (b) -> number of returning users per day_diff since install
WITH daily_stat AS (
  SELECT i.basis_month, i.platform, i.install_date,
         DATE_DIFF('day', i.install_date, b.event_date) AS day_diff,
         COUNT(*) AS retained_users
  FROM installs AS i
  JOIN base AS b
    ON i.user_id = b.user_id AND b.event_date > i.install_date
  WHERE DATE_DIFF('day', i.install_date, b.event_date) BETWEEN 1 AND 28
  GROUP BY 1, 2, 3, 4
),
-- Denominator per cohort (install date, platform): number of installing users
population AS (
  SELECT basis_month, platform, install_date, COUNT(DISTINCT user_id) AS total_user
  FROM installs
  GROUP BY 1, 2, 3
)
-- Average each cohort's (retained / denominator) by day_diff and platform to form the retention curve
SELECT d.basis_month, d.platform, d.day_diff,
       AVG(d.retained_users / p.total_user) AS avg_retention
FROM daily_stat AS d
JOIN population AS p USING (basis_month, platform, install_date)
GROUP BY 1, 2, 3
ORDER BY 2, 1, 3;
