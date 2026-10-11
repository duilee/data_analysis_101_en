-- Track segment change after N days: where are the users who were heavy 30 days ago today?
-- mart_user_segment must be loaded for multiple dates (see the loading query in notebook section 1.3.3).
-- (Change past.user_seg = 'new' to see how users who were in their first week 30 days ago settled in)

SELECT
  past.user_seg AS seg_30days_ago,
  curr.user_seg AS seg_today,
  count(*) AS users,
  round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM mart_user_segment AS past
LEFT JOIN mart_user_segment AS curr
  ON past.user_id = curr.user_id
 AND curr.target_date = DATE '2026-05-20'
WHERE past.target_date = DATE '2026-05-20' - INTERVAL 30 DAY
  AND past.user_seg = 'heavy'
GROUP BY past.user_seg, curr.user_seg
ORDER BY users DESC;
