-- 2.5.3) Per-user behavior feature matrix + D7 retention label
-- Aggregate the first (D0) session's behaviors into per-user features and attach the D7 retention label.
-- An LGBM model is trained on this matrix, and SHAP decomposes each behavior's contribution.
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

WITH d0_session AS (   -- install-day (D0) session events only. Mixing in D1+ behavior leaks future information
    SELECT e.user_id, e.event_name, e.event_count, e.event_timestamp
    FROM installs AS i
    JOIN event_log AS e ON i.user_id = e.user_id AND date_diff('day', i.install_date, e.event_date) = 0
),
feat AS (
    SELECT user_id,
           MAX(CASE WHEN event_name = 'tap_tutorial_complete' THEN 1 ELSE 0 END) AS tap_tutorial_complete,
           MAX(CASE WHEN event_name = 'system_push_permission_granted'        THEN 1 ELSE 0 END) AS system_push_permission_granted,
           COUNT(*) FILTER (WHERE event_name = 'page_view_content_detail')      AS page_view_content_detail,
           COUNT(*) FILTER (WHERE event_name = 'tap_like_button')      AS tap_like_button,
           COUNT(*) FILTER (WHERE event_name = 'tap_search_button')       AS tap_search_button,
           COUNT(*) FILTER (WHERE event_name = 'tap_share_button')     AS tap_share_button,
           COUNT(*) FILTER (WHERE event_name = 'page_view_profile') AS page_view_profile,
           COUNT(*) FILTER (WHERE event_name = 'page_view_settings')     AS page_view_settings,
           COUNT(*) FILTER (WHERE event_name = 'view_error_popup')       AS view_error_popup,
           -- install-session length (seconds): first event to last event
           date_diff('second', MIN(event_timestamp), MAX(event_timestamp)) AS session_duration_sec
    FROM d0_session
    GROUP BY 1
)
SELECT l.d7_retention_flag, f.*
FROM d7_label AS l JOIN feat AS f USING (user_id)
ORDER BY user_id   -- fix the row order so the train/test split (and therefore accuracy) is the same on every run;
