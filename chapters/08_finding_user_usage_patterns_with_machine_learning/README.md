# Chapter 8. Finding User Usage Patterns with Machine Learning

Practice code for this chapter. We use KMeans clustering to split alarm-app users into usage patterns (personas)
without supervision, interpret and name them from their centroids, and link them to a retention metric to get all the way to an action.

- **8.5.2.** Building user features — extract user features with feature-engineering SQL that encodes domain knowledge (8.5.2.1), check feature distributions for discriminating power between users (8.5.2.2)
- **8.5.3.** Feature scaling (StandardScaler) + choosing the number of clusters (Elbow · Silhouette)
- **8.5.4.** Clustering — read characteristics from centroids (mapped back to original units) → persona naming (8.5.4.1), visualize clusters with PCA (8.5.4.2)
- **8.5.5.** Using clustering with cohorts and metrics — cluster new and existing users separately and compare (8.5.5.1), retention KPI by cluster → linking to actions (8.5.5.2), load labels (local CSV) & save/load the model (pickle) (8.5.5.3)

## How to run

```bash
python generate_data.py                 # generate the example data (data/*.csv)
jupyter notebook user_segmentation.ipynb  # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Synthetic alarm-usage data generator with 4 planted personas (fixed seed) |
| `data/alarm_daily.csv` | Daily alarm features (input to the feature-extraction SQL) |
| `data/user_master.csv` | `user_id, new_flag, retained_d7` |
| `sql/extract_features.sql` | DuckDB query that turns daily rows into user features (weekday filter, period average, clipping) |
| `user_segmentation.ipynb` | Notebook for 8.5.2–8.5.5 |

> The example data was built by "planting" four personas, so you can follow along and check whether KMeans
> recovers those personas almost exactly. (Alarm times are expressed as integer minutes, 0–1439.)
> Running the notebook creates `output/` (label CSV) and `models/` (.pkl); both are gitignored.
