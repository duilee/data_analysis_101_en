-- 6.3.2. Identify the user (pid) and cumulative payment number (order_cnt) from order_number
-- The prefix (the part before '..') identifies the user; row_number() gives the payment number.
-- Assumes the real store-report structure: no suffix on the first payment, '..1', '..2' on renewals.
-- (The notebook turns this result into the orders view, which later steps reuse)
SELECT
    split_part(order_number, '..', 1)  AS pid
  , order_charged_date
  , product_id
  , sales_amount_krw
  , row_number() OVER (PARTITION BY split_part(order_number, '..', 1)
                       ORDER BY order_charged_date) AS order_cnt
FROM sales
