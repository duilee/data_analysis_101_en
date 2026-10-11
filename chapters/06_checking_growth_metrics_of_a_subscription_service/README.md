# Chapter 6. Checking the Growth Metrics of a Subscription Service

Practice code for MRR analysis. Starting from a store payment log with no user ID (shaped like a
Google Play Sales Report), we identify users and decompose monthly MRR to diagnose the health of a subscription business.

- **6.3.2.** Parse the prefix/suffix of `order_number` to identify users (pid) and the cumulative payment number.
- **6.3.3.** Measure the interval from the previous payment with `LAG()` to separate renew from reactivation (32-day threshold).
- **6.3.4.** FULL OUTER JOIN with the previous month to decompose monthly MRR into new/renew/reactivation/expansion/contraction/churn.
- **6.3.5.** Compute GRR (defense) and NRR (growth) and interpret the gap between them.
- **6.3.6.** Recover the 5% monthly churn rate planted in the data and connect it to the LTV ≈ ARPU ÷ churn rate rule of thumb.

Three **[Notebook extra]** sections not in the book (checking payment intervals, verifying the MRR identity,
decomposing subscriber counts — 6.2.4.7) appear only in the notebook. Section numbers match the practice sections of book chapter 6 (6.3.x).

## How to run

```bash
python generate_data.py             # generate the example data (data/subscription_sales.csv)
jupyter notebook mrr_analysis.ipynb # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Synthetic payment-log generator (fixed seed, 5% monthly churn planted) |
| `data/subscription_sales.csv` | Per-payment log (`order_number, order_charged_date, product_id, sales_amount_krw`) |
| `sql/identify_orders.sql` | Identify users (pid) + cumulative payment number |
| `sql/classify_payment.sql` | Classify new / renew / reactivation |
| `sql/mrr_breakdown.sql` | Decompose monthly MRR into its six components |
| `sql/subscriber_counts.sql` | The same decomposition in units of subscriber count |
| `mrr_analysis.ipynb` | Practice notebook for 6.3 (6.3.1–6.3.6 + notebook extras) |
