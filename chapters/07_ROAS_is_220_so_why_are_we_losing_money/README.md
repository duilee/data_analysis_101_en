# Chapter 7. ROAS Is 220%, So Why Are We Losing Money?

Practice code for unit economics. Starting from three raw logs — marketing costs, acquisitions,
and payments — we compute and reproduce the tables completed in the chapter (the CAC cascade,
the channel table, and the payback curve).

- **7.4.2.** Compute CAC by channel on a media-cost basis and a fully-loaded basis (12,000 KRW → 14,500 KRW).
- **7.4.3.** Compute LTR → LTV (contribution margin) from the actual payments of mature cohorts acquired more than a year ago (the 3.1 → 2.0 → 1.7 cascade).
- **7.4.4.** Join CAC and LTV at the channel level to reproduce the chapter's channel table.
- **7.4.5.** Draw payback curves by cohort and measure the payback period (search April cohort breaks even in month 3; 12-month observation window).
- **7.4.6.** Compute a CAC guideline as target payback period x average monthly contribution margin per user.

## How to run

```bash
python generate_data.py                  # generate example data (data/*.csv)
jupyter notebook unit_economics.ipynb    # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Synthetic data generator (fixed seed — plants CAC, LTV, and payback curves by channel as the answers) |
| `data/marketing_costs.csv` | Marketing cost by month x channel (`month, channel, media_cost_krw, other_cost_krw`) |
| `data/users.csv` | Roster of acquired users (`user_id, channel, signup_date`) — includes users who never paid |
| `data/payments.csv` | One row per payment (`user_id, payment_date, amount_krw`) |
| `sql/cac_by_channel.sql` | Media-cost / fully-loaded CAC by channel |
| `sql/mature_cohort.sql` | Mature cohort view (12+ months since acquisition) — reused by the backtest below and 7.4.6 |
| `sql/ltv_backtest.sql` | Mature cohort 12-month actual LTR → LTV (contribution margin) (prerequisite: mature_cohort.sql) |
| `sql/payback_curve.sql` | Cohort payback curve (cumulative contribution margin ÷ total CAC) |
| `unit_economics.ipynb` | Practice notebook for 7.4 (7.4.1-7.4.6) |
