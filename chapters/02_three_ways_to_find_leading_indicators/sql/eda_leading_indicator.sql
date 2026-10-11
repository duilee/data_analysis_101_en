-- 2.5.2) Finding leading-indicator candidates with EDA
-- Label newly installed (D0) users as D7 retained / churned, then compare the share of users
-- who performed each D0~D1 behavior and its average count (avg_event_count) across the two cohorts.
--
-- Prerequisite: the event_log table must be registered (same as the notebook's setup cell):
--   CREATE OR REPLACE TABLE event_log AS SELECT * FROM read_csv_auto('data/event_log.csv');
-- The shared views below (installs, d7_label) are repeated in each of the 2.5.2~2.5.4 sql files so that any file runs on its own.

-- Install (D0) time: each user's first system_app_install
CREATE OR REPLACE VIEW installs AS
  SELECT user_id, MIN(event_timestamp) AS install_ts, MIN(event_date) AS install_date
  FROM event_log WHERE event_name = 'system_app_install' GROUP BY 1;

-- D7 retention label: 1 if there is any activity on day 7 after install. 2.5.2~2.5.4 all use this view
CREATE OR REPLACE VIEW d7_label AS
  SELECT i.user_id, i.install_ts, i.install_date,
         MAX(CASE WHEN date_diff('day', i.install_date, e.event_date) = 7 THEN 1 ELSE 0 END) AS d7_retention_flag
  FROM installs AS i LEFT JOIN event_log AS e ON i.user_id = e.user_id
  GROUP BY 1, 2, 3;

WITH log_data AS (   -- aggregate the raw log into counts per (user, event, screen, date)
    SELECT event_date, event_name, screen_name, user_id,
           SUM(event_count) AS event_count, MAX(description) AS description
    FROM event_log
    GROUP BY 1, 2, 3, 4
),
event_stat AS (      -- D0~D1 behaviors per cohort (retained / churned): users who did it and their average count
    SELECT r.d7_retention_flag, l.event_name, l.screen_name,
           COUNT(DISTINCT r.user_id) AS user_cnt, AVG(l.event_count) AS avg_event_count
    FROM d7_label AS r
    LEFT JOIN log_data AS l
      ON r.user_id = l.user_id AND l.event_date >= r.install_date
     AND date_diff('day', r.install_date, l.event_date) <= 1
    GROUP BY 1, 2, 3
),
population AS (SELECT d7_retention_flag, COUNT(*) AS total_user_cnt FROM d7_label GROUP BY 1),
cohort_info AS (     -- share (%) of users within the cohort who performed that behavior
    SELECT e.*, (e.user_cnt * 1.0 / p.total_user_cnt) * 100 AS share
    FROM event_stat AS e LEFT JOIN population AS p USING (d7_retention_flag)
)
SELECT event_name, screen_name,
       MAX(CASE WHEN d7_retention_flag = 0 THEN share           END) AS d7_ret0_share,
       MAX(CASE WHEN d7_retention_flag = 0 THEN avg_event_count END) AS d7_ret0_avg_cnt,
       MAX(CASE WHEN d7_retention_flag = 1 THEN share           END) AS d7_ret1_share,
       MAX(CASE WHEN d7_retention_flag = 1 THEN avg_event_count END) AS d7_ret1_avg_cnt,
       d7_ret1_share - d7_ret0_share     AS share_diff,
       d7_ret1_avg_cnt - d7_ret0_avg_cnt AS event_cnt_diff
FROM cohort_info
WHERE event_name IS NOT NULL
GROUP BY 1, 2
HAVING d7_ret1_share >= 10 OR d7_ret0_share >= 10
ORDER BY share_diff DESC;
