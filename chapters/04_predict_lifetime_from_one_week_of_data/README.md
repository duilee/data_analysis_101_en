# Chapter 4. Predict Lifetime from One Week of Data?

Practice code for lifetime estimation. We estimate a user's lifetime (the average number of
active days between signup and churn) from only the first 7 days of retention data, applying
three different methods to the same new cohort and comparing the results.

- **4.6.2. Churn-rate heuristic (Case 1).** Add a geometric-series tail beyond D7 to the D1~D7 area.
- **4.6.3. Retention catalog matching (Case 2).** Pre-build 3,456 power-law curves, then take the lifetime of the curve that most closely matches the new cohort's (D1, D3, D7).
- **4.6.4. Direct measurement on a mature cohort (Case 3).** Rescale the measured lifetime of a year-old cohort by the ratio of the two cohorts' 7-day areas.
- **4.6.5. Comparing the three methods.** Put the three results side by side in one table and bar chart (triangulation).

## How to run

```bash
python generate_data.py                  # generate the example data (data/cohort_retention.csv)
jupyter notebook lifetime_estimation.ipynb   # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Example data generator for the new cohort's 7-day observed retention |
| `data/cohort_retention.csv` | The new cohort's daily retention (`day, retention`, 8 rows D0~D7) |
| `sql/heuristic.sql` | 4.6.2 (Case 1) — churn-rate heuristic (geometric-series extrapolation) |
| `sql/catalog_match.sql` | 4.6.3 (Case 2) — match the minimum-SSE curve in the catalog |
| `sql/mature_cohort.sql` | 4.6.4 (Case 3) — rescale a mature cohort's measured lifetime by the 7-day area ratio |
| `sql/compare_methods.sql` | 4.6.5 — compare the three methods' results in one table |
| `lifetime_estimation.ipynb` | Practice notebook for 4.6 (4.6.1~4.6.6, Cases 1~3 + comparison; the power-law catalog is built inside the notebook) |

> The catalog (3,456 rows) is generated on the fly inside the notebook from a power-law grid and
> registered in DuckDB, so it is not kept as a separate CSV. `sql/catalog_match.sql` and
> `sql/compare_methods.sql` assume that `lifetime_catalog` table has already been registered.
