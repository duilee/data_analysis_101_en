-- Segment transitions (Flow): yesterday (user_seg_from) -> today (user_seg)
-- Build mart_user_segment with build_mart.sql first.

SELECT user_seg_from, user_seg, count(*) AS users
FROM mart_user_segment
WHERE target_date = DATE '2026-05-20'
  AND user_seg_from IS NOT NULL   -- exclude users who signed up today (yesterday is NULL)
GROUP BY user_seg_from, user_seg;
