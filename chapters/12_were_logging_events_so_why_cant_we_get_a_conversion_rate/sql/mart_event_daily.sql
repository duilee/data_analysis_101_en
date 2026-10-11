-- Daily event mart: event and user counts by date, platform, and event
SELECT CAST(event_time AS DATE) AS event_date,
       platform,
       event_name,
       COUNT(*)               AS event_cnt,
       COUNT(DISTINCT user_id) AS user_cnt
FROM event_log
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
