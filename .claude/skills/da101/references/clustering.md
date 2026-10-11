# Usage-pattern clustering — KMeans personas

**Chapter folder**: `chapters/08_finding_user_usage_patterns_with_machine_learning/` · Notebook: `user_segmentation.ipynb`
<!-- synced: code at duilee/data_analysis_101@8e8b97c (2026-09-13) — cross-checked against notebook, README and sql (Korean original); book text: cross-checked 2026-09-26, manuscript section layout: section 1 the average-user trap → section 2 feature engineering (2.1–2.2) → section 3 clustering (3.1–3.3) → section 4 extensions → practice 0–4 (1.1 · 1.2 · 2 · 3.1 · 3.2 · 4.1 · 4.2 · 4.3) → Claude Code practice → wrap-up. -->

## The problem this method solves

Cluster users' behavioral features with KMeans (unsupervised) to discover usage patterns (personas),
map the centroids back to original units to interpret and name them, then link each cluster to a retention KPI
and turn that into action. Flow: feature SQL → distribution check → StandardScaler → choose k (Elbow · Silhouette) →
clustering and centroid interpretation → PCA visualization → new vs. existing comparison → retention by cluster → load labels, save model.

**Pointers to the book's theory sections** (direct the reader to the book for the full explanation)

- 8.1 — The "average user" does not exist: a case where the average (3 alarms, 15 minutes to get up) represented no group at all.
  The activity axis from chapter 1 (light/heavy) alone does not show *how* users use the product, so a split by behavioral pattern is needed.
  With segments, the same subscription-conversion goal can take a different pitch per group (wake up in one go / wake up feeling good /
  make use of the morning). Segments are not an answer but the starting point of a team discussion.
- 8.2 — Feature engineering. 8.2.1 Encoding domain knowledge (surface features → one-level-deeper features such as time-to-wake and interval;
  weekday/weekend split and period averages to reduce noise), 8.2.2 Verifying discriminating power (`.describe()` · `.hist()` EDA, outlier cleaning,
  scale differences → standardization/normalization). Book Figure 8.1.
- 8.3 — Why clustering (multi-dimensional combinations without label bias), KMeans intuition. 8.3.1 Choosing k: Elbow (the bend where the drop in
  inertia flattens) · Silhouette (-1 to 1, cohesion and separation) — both are only guides; decide k as "the number the team can interpret and manage"
  (the book fixes it at 4). Andrew Ng's "there is no right answer for k" + the T-shirt size analogy S/M/L vs. XS–XL (satisfaction vs. management-cost
  trade-off). Book Figure 8.2. Code is in [8.5.3] (Elbow · Silhouette); PCA visualization is in [8.5.4.2].
  8.3.2 centroid = a virtual representative user made from feature means; `.cluster_centers_` as a summary table (book Table 8.1 — a real-service-scale
  example, so the numbers differ from the notebook; see the expected results below). 8.3.3 Persona naming — a name carries further than a numeric
  summary (book Table 8.2). Action examples before naming: cluster 0 (long time to dismiss) → nudge toward adding alarms; cluster 2
  (many alarms but can't get up) → nudge toward a strong wake-up mission or a paid feature. If naming is hard, do it with PMs and designers.
- 8.4 — Extensions: re-clustering within existing cohorts (new/existing, country), tracking new → existing segment moves, linking clusters to KPIs
  (grow the high-retention group as a seed), no causal claims → A/B test, saving the model (`.pkl`) and labels for history tracking.
- Wrap-up — Question: "can we split users into types (personas) by *how* they use the product?" / Solution = feature design → standardization →
  KMeans (Elbow · Silhouette) → centroid interpretation → link to the key metric / Cautions = KMeans splits into k groups even when there is no
  pattern, feature choice drives the result, no causal guarantee / Next actions = save the model and scaler to turn labels into a metric + design an
  experiment that grows the high-retention cluster. Persona naming is about packaging the result so the team can "digest" it — without buy-in there is no action.

## Run and verify

```bash
python generate_data.py      # creates data/alarm_daily.csv, data/user_master.csv
jupyter nbconvert --to notebook --execute user_segmentation.ipynb \
  --output-dir ../../my-work/08_finding_user_usage_patterns_with_machine_learning   # results go to my-work
```

- Inputs: `alarm_daily.csv` (daily alarm-usage features), `user_master.csv` (`user_id, new_flag, retained_d7`).
- 8.5.2.1 is two cells: the `con.execute` cell registers the `clip(x, lim, cap)` macro and the `daily_stat` view with the weekday filter
  (`isodow(...) BETWEEN 1 AND 5`); the `query` cell builds the 7 user features + the 7 clipped `*_cluster` versions via period averages and
  clipping (`sql/extract_features.sql` is the two cells combined).
- **Expected results**: the generator plants 4 personas — `minimalist` (1,389 users), `trying_maximalist`
  (600), `weak_maximalist` (312), `weak_minimalist` (99), 2,400 users in total. At `k = 4` KMeans should recover
  this mix almost exactly, and the centroids' alarm count, interval and time-to-wake should match the planted characteristics.
  The centroids in the generator's `PERSONAS` are planted directly from book Table 8.1 (real-service scale: 9,842 · 138,205 · 31,058 · 59,741 users,
  shares 4.12/57.86/13.00/25.02%), so the book's Table 8.1 and the notebook table have the same shares but different
  user counts and decimals. Results printed in the book's practice section (identical to the notebook output):
  - 8.5.2.1 `users: 2400` · 8.5.3 `X shape: (2400, 7)` (7 clustering features).
  - 8.5.4.1 summary table — 0 Weak-willed Minimalist (alarms 1.40, interval 8.58 min, time to dismiss 68.09 min, first ring to last dismiss
    75.15 min, 99 users 4.12%), 1 Minimalist (1.19 / 3.14 / 6.21 / 8.41, 1,390 users 57.92%), 2 Weak-willed
    Maximalist (2.80 / 47.88 / 8.35 / 84.48, 312 users 13.00%), 3 Trying Maximalist (2.17 / 18.42 / 11.93 /
    40.41, 599 users 24.96%). A ±1-user difference from the planted counts is normal.
  - 8.5.5.1 — new (335 · 184 · 18 · 301 users) / existing (81 · 1,055 · 128 · 298 users). Label numbers are arbitrary per model, so match
    patterns by centroid values, not by number (new cluster 0 = existing cluster 1 = Minimalist).
  - 8.5.5.2 — D7 retention 0: 0.283, 1: 0.564, 2: 0.410, 3: 0.534 → best-retained cluster 1 (56%).
  - 8.5.5.3 — `saved 2,400 labels`; label reproduction match between the saved and reloaded model 100%.
- **Walkthrough point**: when you reach the centroid table in 8.5.4.1, have the reader name each cluster themselves
  (the skill summarizes the behavioral traits; the reader supplies the names) — this is the book's persona-naming exercise.
- **Note**: running creates `output/user_labels.csv` and `models/*.pkl` (gitignored).
  Alarm-time features are integer minutes (0–1439).

## Applying to my data — interactive protocol

Proceed in order 1→5. Show the reader the result of each step and confirm before moving on.
This notebook has no `[apply to my data]` comments, and **the whole feature SQL is domain-specific**, so of all the
chapters in the book this one has the widest replacement scope — spend time on the feature-design step.

### 1. Intake — what to ask the reader

- What is the **file path** of the user behavior log (in a form that can be aggregated daily)?

| Role (notebook example name) | Meaning | Required |
| --- | --- | --- |
| Behavior log (`alarm_daily.csv`) | Behavioral metrics per user × day | Required |
| User master (`user_master.csv`) | `user_id`, a grouping axis (e.g. `new_flag`), an outcome label (e.g. `retained_d7`) | Required for group comparison and KPI linking |

- Which **5–8 behavioral metrics** are likely to separate patterns? (usage frequency, time of day, feature-usage ratios, session length, etc. —
  let the reader choose from their domain knowledge. This choice is half the result.)
- Where to put the outlier cap (clipping threshold) for each metric? (notebook examples: `clip(scheduled_cnt, 10, 11)`,
  `clip(avg_interval, 60, 65)` — values above the limit are replaced)
- Is an **observation-condition filter** such as weekday/weekend needed? (the notebook uses weekdays only)
- Which outcome metric to link to the clusters? (D7 retention, payment, etc.)

### 2. Data check — do not start the analysis until it passes

- Check the user count (warn that clusters are unstable below a few hundred users), nulls and variance per feature
  (suggest dropping features with near-zero variance), the feature correlation matrix → if any pair has correlation 0.9+,
  suggest dropping one of them (that axis would be over-represented).

### 3. Code replacement map

| Anchor (practice section / identifier) | What | How |
| --- | --- | --- |
| 8.5.2.1 `con.execute` cell | `alarm_daily.csv` path, weekday filter `isodow(...) BETWEEN 1 AND 5`, the daily metrics in the `daily_stat` view | Rewrite with the reader's metrics. Keep the structure (daily `daily_stat` → user `user_features`) |
| 8.5.2.1 `query` cell | `user_master.csv` path, `user_features` CTE, the 7 `clip(value, limit, replacement)` calls | Use the thresholds decided at intake. Keep the rule of creating a clipped `*_cluster` twin for each feature |
| 8.5.2.2 | `feat_cols` list (7 feature names), `plt.subplots(2, 4)` · `axes.ravel()[-1].set_visible(False)` (assumes 7) | Reader's feature names — adjust the grid if the feature count differs |
| 8.5.3 | `cluster_cols` (`endswith('_cluster')`) | Automatic if the naming rule is kept |
| ⚠ 8.5.4.1 | `k = 4` **and the default in the `fit_kmeans(frame, k=4)` signature — two places** — 8.5.5.1 calls `fit_kmeans(df_new)` without passing k, so it uses the default | Decide after seeing the Elbow · Silhouette results (step 4 below). Change both places together, or pass `k=k` in the 8.5.5.1 calls |
| 8.5.4.1 `DISPLAY` dictionary | Display-header map with 7 keys — indexed via `summary[list(DISPLAY.values())]`, so a KeyError results if the keys don't match the feature names | Rewrite with the reader's feature names |
| 〃 | `PERSONA_ORDER`, the cutoffs in `name_persona(r)` (`scheduled_cnt < 2`, etc.) | Write anew after looking at the reader's centroids — they are specific to the example domain and must not be reused as-is |
| 8.5.5.1 · 8.5.5.2 | `new_flag` grouping axis, `retained_d7` KPI column | Reader's columns |
| 8.5.5.3 | `output/` · `models/` paths | Change if needed |

- Reuse `fit_kmeans(frame, k=4)`, `random_state=42, n_init=10`, and the scaler → `inverse_transform` flow as-is.

### 4. Step-by-step progress

1. Run the feature SQL → feature summary statistics and histograms. Drop features with no discriminating power here and redo.
2. Scaling → present the Elbow (`k_values = range(1, 11)`) · Silhouette (`range(2, 11)`) plots →
   **decide k together with the reader** (criteria: the curves + "the number the team can interpret and manage" + "can every centroid be
   named in plain words").
3. Fit KMeans → present the centroid table in original units via `inverse_transform` → name the personas with the reader.
   If some cluster cannot be named, adjust k or the features and go back to step 2.
4. Check separation with the PCA visualization.
5. (If there is a grouping axis) compare new/existing clustering separately → join clusters × outcome metric →
   discuss "which persona is at risk" and actions.
6. Save the label CSV and pickle — for production use, explain that re-training is needed when the distribution shifts (season, product changes).

### 5. Interpreting the results

- Always read centroids in original units. Persona names should describe behavior ("sets many alarms and can't get up").
- Translate into action (book 8.3.3 and wrap-up): attach a different prescription per persona — nudge the few-alarms-but-slow group toward
  adding alarms, nudge the many-alarms-but-can't-get-up group toward a strong mission or a paid feature. Use the high-outcome (retention)
  cluster as a seed and design an experiment that grows it; the low cluster is the "at-risk group."
- Outcome differences between clusters are **correlation** — confirm "making users do this behavior raises the outcome" with an experiment.
- Once judged meaningful, save the model, scaler and labels so user patterns can be quantified on the same basis going forward (book 8.4).

## Pitfalls

- KMeans will split any data into k groups — getting clusters does not mean the patterns are real. If the Silhouette is low and the clusters
  can't be named, "no pattern" may be the right answer. Only when the key metric per cluster (retention, etc.) actually differs do you have a
  "valid segment" (book 8.3).
- The "average user" trap — the overall average may represent no group at all. That is the reason for splitting into segments (book 8.1).
- Feature choice drives the result — there is no standard feature playbook. Drop features on which everyone looks the same (no discriminating
  power) and look for features with one more layer of domain context (book 8.2).
- Without scaling, the feature with the largest units dominates the distance.
- Highly correlated feature pairs over-represent their axis.
- k is a judgment, not a computation — even if inertia is lower, reduce k if the team can't understand or manage that many (book 8.3.1).
- Do not conclude that the behavior of the high-retention cluster is the cause of retention — frame it as a hypothesis and verify with an A/B test
  (book 8.4). Segments are not an answer but the starting point of a team discussion.
- KMeans label numbers are arbitrary per model (book 8.5.5.1 · 8.5.5.3) — the same 0 in the new and existing models can be different patterns, so
  match by centroid values, and when saving labels record which model they came from (`new_flag`).
- Saving only the model loses the standardization basis (book 8.5.5.3) — to assign labels to new data on the same basis, pickle the
  `StandardScaler` used in training together with the model.

## Study guide

### Core concepts — what you should be able to explain after this chapter

- **Unsupervised clustering** — grouping similar users by distance without labels. Since there is no ground truth, interpretability
  becomes the quality criterion.
- **Standardization (StandardScaler)** — scale features to mean 0 and variance 1 to remove the effect of units from the distance calculation.
- **Elbow / Silhouette** — two auxiliary metrics for choosing k: the bend in the inertia drop / a cohesion-and-separation score.
- **Centroid interpretation** — the step of reading the centroids mapped back to original units via `inverse_transform` and giving each cluster a
  meaning. This is the domain of domain knowledge, not ML.
- **Clipping** — preprocessing that caps values so outliers don't distort the distances (and therefore the centroids).

### Concept check

Questions cover the five core concepts above (unsupervised clustering · standardization · Elbow/Silhouette · centroid interpretation · clipping).

1. If you run KMeans without scaling, which feature ends up dominating the result? Explain with an example from this chapter's data.
   - Hint: the feature with the widest value range — the minute-scale wake-up time `first_ring_to_last_dismiss` (0–120 minutes) overwhelms a
     ratio feature like `avg_snooze` (roughly 0–1) or a count feature like `scheduled_cnt` (1–3), so you effectively cluster on one feature.
     Standardization puts every feature on the same scale: "how far from the mean."
2. When the bend in the Elbow curve is not clear, what practical criterion do you use to choose k?
   - Hint: use the Silhouette as a supplement + "the number the team can actually interpret and manage" + "the largest k at which every
     centroid can be named in plain words." Don't increase k just because inertia is lower.
3. What is a centroid, and why should you read it only after mapping it back with `scaler.inverse_transform`?
   - Hint: a "virtual representative user" made from the feature means of the cluster's members. Values in the standardized space are
     "how many σ from the mean," which humans can't read, so they must be restored to minutes and counts before naming is possible.
4. In 8.5.2.1, why do we feed the clipped `*_cluster` columns into the clustering while keeping the original features as well?
   - Hint: a handful of extreme users drag the distance calculation and the centroids, blurring group boundaries — so use the clipped
     version for clustering and the originals for distribution checks and interpretation.
5. Why can't you go straight from "retention differs by cluster" to "making users do this behavior raises retention"?
   - Hint: self-selection — users who were already inclined to stay may be the ones doing the behavior. Frame it as a hypothesis and verify
     with an A/B test. Also note that KMeans never used the label (retention) as an input.

### Advanced exercises

1. **[Sandbox]** Have the reader predict how the Elbow and Silhouette change at k=3 and k=4 if `weak_minimalist` (99 users) is deleted from
   `PERSONAS` in `generate_data.py`, leaving only 3 planted personas → edit → regenerate → re-run → compare. (Check whether
   "number of planted structures = optimal k" is recovered.)
   When done, restore with `git checkout -- generate_data.py data/` and regenerate.
2. **[Sandbox]** Redefine the `clip` macro in 8.5.2.1 as `AS x` to disable clipping (the `*_cluster` columns become the raw values — simpler
   than deleting the 7 calls in the `query` cell). Predict how the centroids get distorted → run → compare with the planted persona values.
   See with your own eyes that "a few outliers drag the centroid." Restoring afterwards is mandatory.
3. **[Thinking]** If users move between personas over time (new → mature), what is the problem with static clustering and how would you
   compensate? (Sliding-window re-clustering, transition tracking — discuss in connection with the Flow perspective of the dau-segments chapter.)
