# Chapter 2. Three Ways to Find Leading Indicators

Practice code that finds the **leading indicators** that move a lagging indicator (D7 retention), using three
methods on the same new-user event log. *Same data, same target, three lenses.*

- **2.5.2. Finding leading-indicator candidates with EDA.** Label users as D7 retained / churned and compare the share and average count of D0~D1 behaviors to shortlist candidates.
- **2.5.3. Decomposing contributions with SHAP values.** Train an LGBM model that predicts D7 retention (Optuna tuning is optional), then quantify each behavior's contribution and threshold (aha moment) with SHAP summary and dependence plots.
- **2.5.4. Diagnosing user flows with a Sankey diagram.** Draw the behavior flow right after install, color it by D7 retention per transition, and find the fork where retention splits.
- Finally, triangulate the leading indicators that all three methods point to.

## How to run

```bash
python generate_data.py                          # generate the example data (data/event_log.csv)
jupyter notebook leading_indicators.ipynb        # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | New-user event log generator (fixed seed; plants latent quality and path-dependent retention) |
| `data/event_log.csv` | Timestamp-level raw event log (shared input for all three practice sections) |
| `sql/eda_leading_indicator.sql` | 2.5.2 -- D0~D1 behaviors by D7 retention cohort |
| `sql/feature_matrix.sql` | 2.5.3 -- per-user D0 behavior feature matrix + D7 retention label |
| `sql/sankey_transitions.sql` | 2.5.4 -- install-session step transitions + D7 retention per transition |
| `leading_indicators.ipynb` | 2.5.2, 2.5.3, 2.5.4 + summary notebook |
