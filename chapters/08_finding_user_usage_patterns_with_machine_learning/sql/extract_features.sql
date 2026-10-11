-- Per-user weekday usage features (input for 8.5.2.1)
--
-- Aggregates the daily alarm log (alarm_daily) to the user level. Domain knowledge is baked right in:
--   - Weekdays (Mon-Fri) only (weekday and weekend patterns differ sharply)
--   - Average over the period to suppress day-to-day noise
--   - Features one level deeper: alarm count, interval, wake-up time, missions
--   - A separate _cluster version with extreme values clipped for the clustering input (clip macro)
-- (Alarm times are expressed as integer minutes, 0-1439)
--
-- Standalone run: execute the CREATE MACRO / CREATE VIEW statements first, then the main query
-- (identical to the two cells of notebook section 8.5.2.1).

CREATE OR REPLACE MACRO clip(x, lim, cap) AS CASE WHEN x > lim THEN cap ELSE x END;  -- clip extreme values

-- Daily alarm log -> daily derived metrics. Weekdays (Mon-Fri) only (weekday and weekend patterns differ sharply)
CREATE OR REPLACE VIEW daily_stat AS
  SELECT local_date, user_id, scheduled_cnt,
         (last_scheduled_min - first_scheduled_min) / NULLIF(scheduled_cnt - 1, 0) AS avg_interval,
         snooze_alarm_cnt      / scheduled_cnt AS avg_snooze,
         mission_used_cnt      / scheduled_cnt AS used_mission_per_alarm,
         mission_attempt_cnt   / scheduled_cnt AS mission_attempt_per_alarm,
         total_time_to_dismiss / scheduled_cnt AS avg_time_to_dismiss,
         first_ring_to_last_dismiss
  FROM read_csv_auto('data/alarm_daily.csv')
  WHERE isodow(CAST(local_date AS DATE)) BETWEEN 1 AND 5   -- DuckDB isodow: Mon=1
    AND scheduled_cnt > 0
    AND first_ring_to_last_dismiss > 0;

WITH user_features AS (   -- suppress day-to-day noise by averaging over the period
  SELECT user_id,
         AVG(scheduled_cnt)                AS scheduled_cnt,
         AVG(COALESCE(avg_interval, 0))    AS avg_interval,
         AVG(avg_snooze)                   AS avg_snooze,
         AVG(used_mission_per_alarm)       AS used_mission_per_alarm,
         AVG(mission_attempt_per_alarm)    AS mission_attempt_per_alarm,
         AVG(avg_time_to_dismiss)          AS avg_time_to_dismiss,
         AVG(first_ring_to_last_dismiss)   AS first_ring_to_last_dismiss
  FROM daily_stat
  GROUP BY user_id
)
SELECT m.new_flag, m.retained_d7, u.*,
       -- Clustering input: version with extreme values clipped -- clip(value, limit, replacement)
       clip(scheduled_cnt, 10, 11)                AS scheduled_cnt_cluster,
       clip(avg_interval, 60, 65)                 AS avg_interval_cluster,
       clip(avg_snooze, 10, 11)                   AS avg_snooze_cluster,
       clip(used_mission_per_alarm, 10, 11)       AS used_mission_cluster,
       clip(mission_attempt_per_alarm, 10, 11)    AS mission_attempt_cluster,
       clip(avg_time_to_dismiss, 120, 125)        AS avg_time_to_dismiss_cluster,
       clip(first_ring_to_last_dismiss, 120, 125) AS first_ring_to_last_dismiss_cluster
FROM user_features AS u
LEFT JOIN read_csv_auto('data/user_master.csv') AS m USING (user_id)
ORDER BY user_id;
