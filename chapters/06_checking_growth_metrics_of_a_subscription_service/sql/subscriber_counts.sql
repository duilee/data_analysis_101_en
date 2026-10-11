-- [Notebook extra] The same logic in units of 'number of people' -- upgrades/downgrades do not change the subscriber count
WITH payments AS (
    SELECT
        split_part(order_number, '..', 1)  AS pid
      , date_trunc('month', order_charged_date) AS month
      , CASE WHEN row_number() OVER (PARTITION BY split_part(order_number, '..', 1)
                                     ORDER BY order_charged_date) = 1 THEN 'new'
             WHEN order_charged_date
                  - lag(order_charged_date) OVER (PARTITION BY split_part(order_number, '..', 1)
                                                  ORDER BY order_charged_date) < 32 THEN 'renew'
             ELSE 'reactivation' END AS pay_type
    FROM sales
),
classified AS (   -- user x month aggregate: even with several payments in the same month, the subscriber counts as 1
    SELECT
        pid
      , month
      , min(pay_type) AS pay_type   -- priority new > reactivation > renew (happens to match alphabetical order)
    FROM payments
    GROUP BY pid, month
),
paired AS (
    SELECT
        coalesce(c.month, p.month + INTERVAL 1 MONTH) AS month
      , c.pid  AS cur_pid
      , p.pid  AS prev_pid
      , c.pay_type
    FROM classified c
    FULL OUTER JOIN classified p
      ON c.pid = p.pid AND p.month = c.month - INTERVAL 1 MONTH
)
SELECT
    month
  , count(cur_pid)                                                  AS subscribers
  , count(CASE WHEN pay_type = 'new'          THEN 1 END)           AS new_subs
  , count(CASE WHEN pay_type = 'reactivation' THEN 1 END)           AS reactivation_subs
  , count(CASE WHEN cur_pid IS NULL THEN 1 END)                     AS churned_subs
FROM paired
WHERE month <= (SELECT max(month) FROM classified)
GROUP BY month
ORDER BY month
