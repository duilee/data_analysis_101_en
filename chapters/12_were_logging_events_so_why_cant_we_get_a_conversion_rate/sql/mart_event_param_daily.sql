-- Daily property mart: the share of events where each property that is supposed to be attached is actually filled in
WITH keys AS (
  SELECT property_name AS param_key,
         unnest(string_split(events, '|')) AS event_name
  FROM taxonomy_properties
  WHERE scope = 'event' AND events <> ''
),
vals AS (
  SELECT CAST(l.event_time AS DATE) AS event_date,
         l.platform, l.event_name, k.param_key,
         json_extract_string(l.properties, '$.' || k.param_key) AS val
  FROM event_log l
  JOIN keys k USING (event_name)
)
SELECT event_date, platform, event_name, param_key,
       COUNT(*) AS event_cnt,
       COUNT(val) AS not_null_event_cnt,
       COUNT(val) * 1.0 / COUNT(*) AS not_null_ratio
FROM vals
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2, 3, 4;
