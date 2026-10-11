-- 6.3.3. Classify each payment as new / renew / reactivation
-- renew if the interval from the previous payment is within one cycle (about 30 days), reactivation if longer.
-- [Applying to your data] If the subscription is not monthly, adjust the 32-day threshold to the billing cycle.
-- (The notebook turns this result into the classified view, which the MRR decomposition reuses)
WITH orders AS (
    SELECT
        split_part(order_number, '..', 1)  AS pid
      , order_charged_date
      , product_id
      , sales_amount_krw
      , row_number() OVER (PARTITION BY split_part(order_number, '..', 1)
                           ORDER BY order_charged_date) AS order_cnt
      , lag(order_charged_date) OVER (
            PARTITION BY split_part(order_number, '..', 1)
            ORDER BY order_charged_date) AS prev_date
    FROM sales
)
SELECT *
     , CASE WHEN order_cnt = 1 THEN 'new'
            WHEN order_charged_date - prev_date < 32
                 THEN 'renew'
            ELSE 'reactivation' END AS pay_type
FROM orders
