-- 2.5.4) Install-session step transitions + D7 retention per transition (Sankey input)
-- The notebook's CONFIG constants are expanded to values here: MAX_STEPS=10, TOP_K=6, MIN_USERS=20
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

-- Events within 1 hour of install, in order (consecutive duplicates removed) -> step number per user
CREATE OR REPLACE VIEW user_steps AS
  WITH session_events AS (
    SELECT i.user_id, e.event_name, e.event_timestamp,
           LAG(e.event_name) OVER (PARTITION BY i.user_id ORDER BY e.event_timestamp) AS prev_event
    FROM installs AS i
    JOIN event_log AS e
      ON i.user_id = e.user_id
     AND e.event_timestamp >= i.install_ts
     AND e.event_timestamp <= i.install_ts + INTERVAL 1 HOUR
  )
  SELECT user_id, event_name, event_timestamp,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_timestamp) AS step_num
  FROM session_events
  WHERE prev_event IS NULL OR event_name != prev_event
  QUALIFY step_num <= 10;

WITH event_volume AS (   -- rank events by frequency at each step
    SELECT step_num, event_name, COUNT(DISTINCT user_id) AS user_cnt,
           ROW_NUMBER() OVER (PARTITION BY step_num ORDER BY COUNT(DISTINCT user_id) DESC) AS rnk
    FROM user_steps
    GROUP BY 1, 2
),
steps_resolved AS (     -- lump events outside the top K into ETC
    SELECT s.user_id, s.step_num,
           CASE WHEN v.rnk <= 6 THEN s.event_name ELSE 'ETC' END AS event_name
    FROM user_steps AS s JOIN event_volume AS v USING (step_num, event_name)
),
transitions AS (        -- step N -> N+1 transitions
    SELECT a.user_id, a.step_num AS from_step,
           CAST(a.step_num AS VARCHAR) || '-' || a.event_name AS source,
           CAST(b.step_num AS VARCHAR) || '-' || b.event_name AS target
    FROM steps_resolved AS a
    JOIN steps_resolved AS b ON a.user_id = b.user_id AND b.step_num = a.step_num + 1
)
SELECT t.from_step, t.source, t.target,
       COUNT(DISTINCT t.user_id) AS user_count,
       COUNT(DISTINCT CASE WHEN r.d7_retention_flag = 1 THEN t.user_id END) * 100.0
         / NULLIF(COUNT(DISTINCT t.user_id), 0) AS d7_retention
FROM transitions AS t LEFT JOIN d7_label AS r USING (user_id)
GROUP BY 1, 2, 3
HAVING COUNT(DISTINCT t.user_id) >= 20
ORDER BY from_step, user_count DESC;
