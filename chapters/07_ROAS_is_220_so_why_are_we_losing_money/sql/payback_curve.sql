-- Payback curve: cumulative contribution margin by elapsed month for a cohort (channel x acquisition month) ÷ total CAC
-- Implements the five plotting steps from 7.3.1 as-is (example: the 2025-04 search cohort)
-- (The notebook wraps this query in a payback_df function that takes channel and acquisition month, reused by the table and the chart)
WITH cohort AS (
    SELECT user_id FROM users
    WHERE channel = 'search'
      AND date_trunc('month', signup_date) = DATE '2025-04-01'
),
cost AS (
    SELECT SUM(media_cost_krw + other_cost_krw) AS cac_total
    FROM marketing_costs
    WHERE channel = 'search' AND month = DATE '2025-04-01'
)
SELECT date_diff('month', DATE '2025-04-01',
                 date_trunc('month', p.payment_date))  AS elapsed
     , SUM(p.amount_krw) * 0.65                        AS monthly_contrib
     , SUM(SUM(p.amount_krw) * 0.65) OVER (ORDER BY date_trunc('month', p.payment_date))
       / (SELECT cac_total FROM cost)                  AS cum_ratio
FROM payments p
JOIN cohort USING (user_id)
GROUP BY date_trunc('month', p.payment_date)
ORDER BY 1;
