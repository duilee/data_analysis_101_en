-- 6.3.4. Monthly MRR decomposition: new / renew / reactivation / expansion / contraction / churn
-- Aggregate payments per user x month, then FULL OUTER JOIN with the previous month:
--   present on both sides = continuing subscriber (renew + up/downgrade change), previous month only = churn.
-- Requirement: runs standalone with only the sales table (data/subscription_sales.csv).
-- (Full standalone query -- the notebook stages the same computation as the view chain
--  orders/classified/monthly/paired and computes the 'paid in both months' condition once as the stayed flag)
WITH payments AS (
    SELECT
        split_part(order_number, '..', 1)  AS pid
      , date_trunc('month', order_charged_date) AS month
      , sales_amount_krw                   AS amt
      , CASE WHEN row_number() OVER (PARTITION BY split_part(order_number, '..', 1)
                                     ORDER BY order_charged_date) = 1 THEN 'new'
             WHEN order_charged_date
                  - lag(order_charged_date) OVER (PARTITION BY split_part(order_number, '..', 1)
                                                  ORDER BY order_charged_date) < 32 THEN 'renew'
             ELSE 'reactivation' END AS pay_type
    FROM sales
),
classified AS (   -- user x month aggregate: collapse multiple payments in the same month (e.g. a mid-month plan change) into one row
    SELECT
        pid
      , month
      , sum(amt) AS amt
      -- pay_type priority: new > reactivation > renew (happens to match alphabetical order)
      , min(pay_type) AS pay_type
    FROM payments
    GROUP BY pid, month
),
paired AS (
    SELECT
        coalesce(c.month, p.month + INTERVAL 1 MONTH) AS month
      , c.amt AS amt             -- this month's payment (NULL = churned)
      , p.amt AS prev_amt        -- previous month's payment (NULL = new/returning)
      , c.amt - p.amt AS delta   -- change (used for expansion/contraction)
      , c.pay_type
      , c.amt IS NOT NULL AND p.amt IS NOT NULL AS stayed  -- paid in both months
    FROM classified c
    FULL OUTER JOIN classified p
      ON c.pid = p.pid AND p.month = c.month - INTERVAL 1 MONTH
)
SELECT
    month
  , sum(amt)                                            AS mrr
  , sum(CASE pay_type WHEN 'new' THEN amt END)          AS new_mrr
  , sum(CASE pay_type WHEN 'reactivation' THEN amt END) AS reactivation_mrr
  , sum(CASE WHEN stayed THEN least(amt, prev_amt) END) AS renew_mrr
  , sum(CASE WHEN stayed THEN greatest(delta, 0) END)   AS expansion_mrr
  , sum(CASE WHEN stayed THEN greatest(-delta, 0) END)  AS contraction_mrr
  , sum(CASE WHEN amt IS NULL THEN prev_amt END)        AS churn_mrr
  , sum(prev_amt)                                       AS baseline_mrr
FROM paired
-- Drop the 'ghost month' that appears after the last month (rows with only a previous month)
WHERE month <= (SELECT max(month) FROM classified)
GROUP BY month
ORDER BY month
