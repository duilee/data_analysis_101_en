# Chapter 5. How Much DAU Is This Feature Worth?

Practice code for this chapter.

- **5.8.2.** Fit a power law `y = a·x^b` to the new-user retention curve (`curve_fit`) to get the shape coefficient `b`.
- **5.8.3.** Simplify the one-year cumulative sum of `x^b` into a single constant to complete the formula `DAU = new users × (1 + D1 retention × constant)`.
- **5.8.4.** Plug the finished formula into features A and B from the opening quiz to confirm the answer (arithmetic only, no code).

## How to run

```bash
python generate_data.py            # generate the example data (data/active_daily.csv)
jupyter notebook dau_forecast.ipynb  # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Synthetic example data generator for retention analysis (fixed seed) |
| `data/active_daily.csv` | Generated example data (`date, user_id, platform, country_code, install_flag`) |
| `sql/retention_curve.sql` | DuckDB query that builds the D1–D28 retention curve per month and platform |
| `dau_forecast.ipynb` | Notebook for 5.8.2–5.8.4 |
