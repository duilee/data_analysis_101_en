-- Mature cohort backtest: actual LTR of users 12+ months past acquisition → LTV (contribution margin)
-- No extrapolation or discounting — uses only 'the record of a game already finished'
-- Prerequisite: mature_cohort.sql (the mature view) · Setup: register the payments table (data/payments.csv)
-- Contribution margin ratio 0.65 = the variable-cost assumption in 7.2.1 (35% total)
WITH rev AS (  -- 12-month cumulative payment per user (non-payers count as 0)
  SELECT m.channel, m.user_id, COALESCE(SUM(p.amount_krw), 0) AS ltr_12m
  FROM mature m
  LEFT JOIN payments p
    ON p.user_id = m.user_id
   AND p.payment_date < m.cohort_month + INTERVAL 12 MONTH
  GROUP BY 1, 2
)
SELECT channel
     , COUNT(*) AS users
     , ROUND(AVG(ltr_12m)) AS ltr
     , ROUND(AVG(ltr_12m) * 0.65) AS ltv_cm
FROM rev
GROUP BY channel
ORDER BY ltv_cm DESC;
