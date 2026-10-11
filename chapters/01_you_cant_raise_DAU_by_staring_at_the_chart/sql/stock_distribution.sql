-- Daily segment distribution (Stock)
-- Build mart_user_segment with build_mart.sql first.
-- (Segment ordering is handled by pandas reindex in the notebook)

SELECT user_seg, count(*) AS users
FROM mart_user_segment
WHERE target_date = DATE '2026-05-20'
GROUP BY user_seg;
