-- Case 1. Churn-rate heuristic
-- Estimate lifetime by adding an infinite geometric-series tail beyond D7 to the new cohort's D1~D7 area.
--   lifetime ≈ (D1 + D2 + ... + D7) + D7 × r / (1 − r)
-- r is the average of the day-over-day retention ratios over the last few days (D5/D4, D6/D5, D7/D6).
-- 1) daily_ratios: compute the day-over-day ratio for all 8 days with LAG
-- 2) stats: get the observed area (sum of D1~D7), D7, and r (mean ratio over days 5~7) in one pass with conditional aggregation (CASE WHEN).

WITH daily_ratios AS (
  SELECT day, retention,
         retention / LAG(retention) OVER (ORDER BY day) AS ratio
  FROM cohort_retention
),
-- Aggregate the observed area, D7, and the late-window survival ratio r in one pass
stats AS (
  SELECT
    SUM(CASE WHEN day BETWEEN 1 AND 7 THEN retention END) AS area_d1_d7,
    MAX(CASE WHEN day = 7 THEN retention END)             AS d7,
    AVG(CASE WHEN day BETWEEN 5 AND 7 THEN ratio END)     AS r
  FROM daily_ratios
)
SELECT
  ROUND(area_d1_d7, 3)                    AS observed_d1_d7_area,
  ROUND(d7, 3)                            AS d7,
  ROUND(r, 4)                             AS estimated_r,
  ROUND(d7 * r / (1 - r), 2)              AS extrapolated_tail_area,
  ROUND(area_d1_d7 + d7 * r / (1 - r), 2) AS lifetime_estimate
FROM stats;
