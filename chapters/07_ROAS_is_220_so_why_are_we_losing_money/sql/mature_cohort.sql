-- Mature cohort view: users 12+ months past acquisition (acquired 2024-01 to 2024-12) — same one-year basis as Chapter 4
-- Reused by ltv_backtest.sql and notebook section 7.4.6 (CAC guideline) — run this first
-- Setup: register the users table (data/users.csv)
CREATE OR REPLACE VIEW mature AS
SELECT user_id, channel, date_trunc('month', signup_date) AS cohort_month
FROM users WHERE signup_date BETWEEN DATE '2024-01-01' AND DATE '2024-12-31';
