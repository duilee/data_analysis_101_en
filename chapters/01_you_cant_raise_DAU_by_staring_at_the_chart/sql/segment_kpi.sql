-- The 5 transition-based ratio metrics (HURR / CURR / Heavy Loss / Light Loss / Reactivation)
-- In the notebook, current = ('heavy', 'light') is inserted as a Python string constant.
-- Wrap denominators in nullif(..., 0) to guard against division by zero.

SELECT
  round(100.0 * count_if(user_seg_from = 'heavy' AND user_seg = 'heavy')
    / nullif(count_if(user_seg_from = 'heavy'), 0), 1) AS hurr_pct,
  round(100.0 * count_if(user_seg_from IN ('heavy', 'light') AND user_seg IN ('heavy', 'light'))
    / nullif(count_if(user_seg_from IN ('heavy', 'light')), 0), 1) AS curr_pct,
  round(100.0 * count_if(user_seg_from = 'heavy' AND user_seg = 'light')
    / nullif(count_if(user_seg_from = 'heavy'), 0), 1) AS heavy_loss_pct,
  round(100.0 * count_if(user_seg_from = 'light' AND user_seg = 'risk')
    / nullif(count_if(user_seg_from = 'light'), 0), 1) AS light_loss_pct,
  round(100.0 * count_if(user_seg_from = 'risk' AND user_seg = 'light')
    / nullif(count_if(user_seg_from = 'risk'), 0), 1) AS reactivation_pct
FROM mart_user_segment
WHERE target_date = DATE '2026-05-20';
