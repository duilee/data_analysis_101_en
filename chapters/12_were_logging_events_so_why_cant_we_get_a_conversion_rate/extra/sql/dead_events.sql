-- Events documented as Live but with zero rows in the log
SELECT t.event_name, t.event_type, t.version_added, t.description
FROM taxonomy_events t
LEFT JOIN event_log l ON l.event_name = t.event_name
WHERE t.status = 'Live'
GROUP BY 1, 2, 3, 4
HAVING COUNT(l.event_name) = 0
ORDER BY 1;
