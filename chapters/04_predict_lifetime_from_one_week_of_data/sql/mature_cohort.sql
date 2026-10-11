-- Case 3. Direct measurement on a mature cohort
-- Rescale the measured lifetime of a mature cohort from a year ago by the ratio of the new cohort's D1~D7 area.
--   lifetime_new ≈ lifetime_mature × (new D1~D7 area / mature D1~D7 area)
-- The mature cohort's two aggregates are passed in as pre-computed constants (a params CTE instead of a DECLARE statement).

WITH params AS (
  SELECT
    51.5  AS lifetime_mature,    -- the mature cohort's measured 1-year lifetime = SUM(retention) over D1~D365
    1.875 AS area_d1_d7_mature   -- the mature cohort's D1~D7 area = SUM(retention) over D1~D7
),
new_area AS (
  SELECT SUM(retention) AS area_d1_d7_new
  FROM cohort_retention
  WHERE day BETWEEN 1 AND 7
)
SELECT
  p.lifetime_mature,
  p.area_d1_d7_mature,
  ROUND(n.area_d1_d7_new, 4) AS area_d1_d7_new,
  ROUND(n.area_d1_d7_new / p.area_d1_d7_mature, 4) AS scaling_factor,
  ROUND(p.lifetime_mature * n.area_d1_d7_new / p.area_d1_d7_mature, 2)
    AS lifetime_estimate
FROM new_area AS n CROSS JOIN params AS p;
