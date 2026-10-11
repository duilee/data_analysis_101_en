# Chapter 11. My Query Has Been Running for 30 Minutes

Analysis queries are slow, the data you want to look at is not in the DW, and every team reports a different subscriber count — all three are really
a problem of where the data sits. This is the practice code for building the four layers **raw → staging →
dimension/fact → mart** yourself on synthetic data from a fictional subscription app (five sources), and seeing how the same question
("daily active subscribers and revenue") gets answered differently from raw and from a mart.

- **11.6.2. Pulling straight from raw.** Join four CSVs in a single query to get the answer, and measure the query's length and time.
- **11.6.3. staging.** One view per source — clean up only names, types, duplicates and system events; no business logic.
- **11.6.4. dimension / fact.** Build a user daily-snapshot dimension and two facts: subscription events (transaction) and daily active subscriptions (snapshot).
- **11.6.5. mart.** Fill 90 days with a batch function that builds one partition (date) at a time, then answer the same question in three lines and confirm the numbers match raw.
- **11.6.6. Reloading a partition.** Run the same date twice to confirm idempotency, and see the duplicates a unique-key test catches when you INSERT without DELETE.
- **11.6.7. Late-arriving events.** See how the same partition's numbers fill in at each batch time (D+1 to D+4 mornings) and apply a 4-day reload window.

## How to run

```bash
python generate_data.py                       # generate the example data (5 files in data/*.csv)
jupyter notebook data_mart_layers.ipynb       # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Synthetic data generator for a subscription app (fixed seed — deliberately plants re-sent duplicates, system events, mixed-case codes and late arrivals) |
| `data/events.csv` | App event log (separate event_time / received_time) |
| `data/subscription_events.csv` | Subscription events — purchase / renewal / cancel / refund |
| `data/user_snapshots.csv` | User × date attribute snapshots (platform, country, app version) |
| `data/sku.csv`, `data/exchange_rates.csv` | Product definitions · daily exchange rates per currency |
| `sql/raw_daily_subscribers.sql` | 11.6.2 — answering with one query and no mart |
| `sql/stg_views.sql` | 11.6.3 — the five staging views |
| `sql/dim_tables.sql`, `sql/fact_subscription_events.sql`, `sql/fact_subscriber_daily.sql` | 11.6.4 — dimensions and facts |
| `sql/mart_subscription_daily.sql` | 11.6.5 — mart (the SQL of one batch run that fills one partition) |
| `data_mart_layers.ipynb` | Notebook for 11.6.2–11.6.7 |
