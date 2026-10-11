-- Compare the three lifetime-estimation methods side by side in a single SQL query (for standalone use)
--
-- The notebook builds its comparison table in pandas by reusing the results computed in the
-- earlier steps (heuristic / catalog_match / mature); use this query when you want to see all
-- three at once with SQL alone.
-- (The cohort_retention table and the lifetime_catalog registration must already be in place.)
-- The heuristic's r is computed in its own CTE — nesting a window function inside an aggregate
-- does not run in DuckDB, and applying WHERE before the window would change r.

WITH params AS (
  SELECT 51.5 AS lifetime_mature, 1.875 AS area_d1_d7_mature
),
obs AS (
  SELECT
    SUM(CASE WHEN day BETWEEN 1 AND 7 THEN retention END) AS area_d1_d7,
    MAX(CASE WHEN day = 1 THEN retention END)         AS d1,
    MAX(CASE WHEN day = 3 THEN retention END)         AS d3,
    MAX(CASE WHEN day = 7 THEN retention END)         AS d7
  FROM cohort_retention
),
daily_ratios AS (
  SELECT day, retention / LAG(retention) OVER (ORDER BY day) AS ratio
  FROM cohort_retention
),
r_estimate AS (
  SELECT AVG(ratio) AS r FROM daily_ratios WHERE day BETWEEN 5 AND 7
),
heuristic AS (
  SELECT obs.area_d1_d7 + obs.d7 * r.r / (1 - r.r) AS lifetime_estimate
  FROM obs, r_estimate r
),
lookup_match AS (
  SELECT cat.lifetime AS lifetime_estimate
  FROM lifetime_catalog AS cat, obs
  ORDER BY POWER(cat.D1 - obs.d1, 2) + POWER(cat.D3 - obs.d3, 2) + POWER(cat.D7 - obs.d7, 2)
  LIMIT 1
),
mature_extrap AS (
  SELECT p.lifetime_mature * obs.area_d1_d7 / p.area_d1_d7_mature AS lifetime_estimate
  FROM params p, obs
)
SELECT 'Case 1. Churn-rate heuristic'          AS method, ROUND(lifetime_estimate, 2) AS lifetime FROM heuristic
UNION ALL
SELECT 'Case 2. Retention catalog matching',   ROUND(lifetime_estimate, 2)           FROM lookup_match
UNION ALL
SELECT 'Case 3. Mature cohort direct measure', ROUND(lifetime_estimate, 2)           FROM mature_extrap;
