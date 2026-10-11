# Leading-indicator search -- cross-checking three lenses: EDA, SHAP, Sankey

**Chapter folder**: `chapters/02_three_ways_to_find_leading_indicators/` · notebook: `leading_indicators.ipynb`
<!-- synced: code at duilee/data_analysis_101@8e8b97c (Korean original) (2026-09-13) -- cross-checked against the notebook, README and sql. Book text cross-checked (2026-09-26; manuscript section layout: section 1 why leading indicators are needed -> section 2 EDA (Table 1, Figure 1) -> section 3 SHAP (3.1~3.4, Table 2) -> section 4 Sankey (4.1~4.2, Table 3) -> practice 0~3 (Python, SQL) -> Claude Code practice 0~4 -> wrap-up (table)). -->

## The problem this method solves

A lagging indicator (D7 retention) is an outcome, so it cannot be moved directly. From a single new-user
event log, we look for the **leading indicators (aha-moment behaviors)** that signal D7 retention ahead of
time, through three lenses. When three methods with different assumptions point to the same behavior, that
candidate is more trustworthy; a behavior that pops up in only one method gets its experiment priority lowered by one notch:

- **2.5.2. Finding leading-indicator candidates with EDA** -- differences in share and average count of D0~D1 behaviors between the D7 retained / churned cohorts.
- **2.5.3. Decomposing contributions with SHAP values** -- train a D7 retention prediction model with LGBM (Optuna tuning), read the
  contributions from the SHAP summary and the thresholds ("effective from N times or more") from the dependence plots.
- **2.5.4. Diagnosing user flows with a Sankey diagram** -- draw the behavior flow right after install, color it by D7 retention
  per transition, and see at which fork retention splits.

**The role of each method** (the detailed comparison is Table 2.3 in book section 2.4.2):
- EDA -- which behaviors differ between retained and churned. Go here first when you have no hypothesis. Univariate, so it cannot see interactions.
- SHAP -- which of many candidates contribute most. Use when you need a priority order. Model setup cost; contribution is not causation.
- Sankey -- at which path or fork the metric splits. Use when the order of behaviors matters. The picture changes with the step design.

**Pointers to the book's theory sections** (in QnA mode, give only the gist and point to the relevant book section for details):
- 2.1 -- revenue, retention and active users are lagging indicators, with a delay before an action's result shows (at least a
  week for a 7-day trial subscription), so you need leading indicators to manage right now. Leading indicators are always
  fuzzy, so the team agrees on the best available metric and stays flexible about being wrong. Aha-moment examples from
  Facebook ("7 friends in 10 days") and Uber ("fast dispatch on the first ride").
- 2.2 (Table 2.1, Figure 2.1) -- compare the "performance rate" and "average count" of each event between the converted /
  non-converted cohorts (here D7 retained / churned). Do not cherry-pick behaviors; look at every event broadly. The ranking by
  rate difference and the ranking by count difference can differ (search is 5th by rate but 1st by count difference). Variants:
  change the label to D1 retention or purchase conversion.
- 2.3 intro -- if machine learning is new to you, read the basic concepts in the intro of chapter 8 (usage-pattern clustering) first.
- 2.3.1~2.3.2 (Figures 2.2, 2.3) -- SHAP (from the Shapley value: weighted average of marginal contributions over coalitions) vs
  feature importance: the latter is a global, positive-only metric with no direction, while the former is a per-row contribution
  with a sign, so you can read direction and thresholds.
- 2.3.3 (Table 2.2) -- for an interpretation model, an AUC around 0.85 is enough and elaborate tuning is not required. Fixed LGBM
  base parameters + `colsample_bytree`/`subsample` (overfitting), `class_weight` (imbalance), AUC early stopping.
- 2.3.4 (Figures 2.4, 2.5) -- reading the summary plot (more content views: +, more error popups: -, session duration contributes
  more than content views), thresholds in the dependence plot (session about 150 seconds, 3 likes). A threshold is not a final
  target but a hypothesis to validate with an A/B test.
- 2.4.1 (Figure 2.6) -- Sankey = nodes (screens, key actions) + links (flow volume as band thickness). Shows how the same event
  behaves differently depending on the context before and after it. Setting a particular screen as the first event shows only the flow after it.
- 2.4.2 (Figures 2.7, 2.8, Table 2.3) -- overlay the target metric (retention rate) on the links as color to find "the path that
  raises the metric" rather than "the path with the most traffic". Start 40% -> skip onboarding and enter home 15% -> recovers
  to 28% on entering content. High retention at late steps is selection bias. Example conclusion: put "first content entry"
  forward as a candidate and remove friction on the path to it. Table 2.3 at the end of the section compares the three methods.
- Wrap-up (table) -- there is no absolute right answer; all three methods are a process for finding candidates. The deliverable
  is "a list of hypotheses to test right now". Design an A/B test on the overlapping behaviors (-> chapter 3), monitor guardrail
  metrics after the intervention.

## Running and verifying

```bash
python generate_data.py      # creates data/event_log.csv (SEED=314, 12,000 users)
jupyter nbconvert --to notebook --execute leading_indicators.ipynb \
  --output-dir ../../my-work/02_three_ways_to_find_leading_indicators   # results go to my-work
```

- Input: `data/event_log.csv` (`event_timestamp, event_date, user_id, event_name, screen_name,
  event_count, description`).
- 3 SQL files: `eda_leading_indicator.sql`, `feature_matrix.sql`, `sankey_transitions.sql`.
- **Expected result**: the generator plants latent quality and path-dependent retention, so the three lenses should
  point to the **same behaviors** as the top leading indicators (top EDA `share_diff` ≈ top SHAP features ≈ the
  high-retention forks in the Sankey). Put the results of the three practice sections side by side and confirm the agreement
  (summary table in the notebook's closing "2.5.5. The behaviors all three methods point to" cell).
  The thresholds planted by the generator are `session_duration >= 150 seconds` and `like_cnt >= 3` -- whether the 2.5.3
  interpretation ("about 150 seconds / 3 times") recovers them is the verification point.
- **Numbers printed in the book** (to compare with the reader's results): right after loading `event_rows 136,391 · users 12,000` ·
  D7 retention of the population 39.7% · top EDA `share_diff` tap_like_button +46.8pp (28.1 -> 74.9), page_view_content_detail
  +41.2pp (58.8 -> 100.0), tap_share_button +34.3pp, tap_tutorial_complete +31.7pp (46.0 -> 77.8),
  tap_search_button +23.9pp (its count gap, 3.7 -> 5.7, is the largest) · bottom view_error_popup -27.9pp,
  page_view_settings -22.5pp, page_view_profile -21.5pp · feature matrix 12,000 rows,
  `session_duration_sec` mean 119.36 seconds · baseline LGBM `accuracy=0.7717 AUC=0.8534 best_iter=202`
  (1,200 test users: 476 retained / 724 churned, precision 0.840/0.688) · Optuna `best CV AUC = 0.8587`
  (`num_leaves 8, min_child_samples 119`) · after tuning `accuracy=0.7767 AUC=0.8539 best_iter=185` (a tiny difference is
  normal for an interpretation model; note that the Optuna numbers depend on the optuna/lightgbm versions -- the committed notebook output in this repo shows `min_child_samples 112` and `accuracy=0.7650 AUC=0.8425 best_iter=10`, which is the same drift the Korean original shows in this environment, so treat the baseline LGBM/EDA/Sankey numbers as the verification points, not the tuned ones) · Sankey `transitions: 84 rows | D7 retention range: 2.6% ~ 86.7%` · from a starting
  retention of 39.7%, skipping onboarding and entering home (2,809 users) drops it to 15.0%, and going on to
  page_view_content_detail recovers it to 27.6% (the book text rounds this to 40% -> 15% -> 28%) · top fork in `branches`
  5-page_view_home -> 6-page_view_content_detail 74.6% vs profile/settings 24.8% · TOP transition
  9-tap_like_button -> 10-page_view_content_detail 86.7% (641 users) · BOTTOM 4-page_view_profile ->
  5-view_error_popup 2.6% (547 users).
- This is the chapter with the heaviest dependencies (lightgbm, shap, optuna, plotly, etc.) -- the first run takes installation time.

## Applying to my data -- interactive protocol

Proceed in order 1 -> 5. Show the reader the result of each step and confirm before moving on.
This notebook has no `[apply to my data]` comments -- the substitution map below is the only guide. The label is
defined in one place, the `d7_label` view, and the three queries JOIN it, so there are few substitution points inside
the notebook, but the same view definition is replicated in each of the 3 `sql/*.sql` files.

### 1. Intake -- what to ask the reader

- What is the **file path** of the new-user event log?

| Role (example name in the notebook) | Type | Meaning | Required |
| --- | --- | --- | --- |
| `user_id` | TEXT | user identifier | required |
| `event_name` | TEXT | event name | required |
| `event_timestamp` / `event_date` | TIMESTAMP / DATE | event time and date | required |
| `event_count` | INT | event count (1 per row if absent) | optional |

- What is the event name of the **install (anchor) event**? (notebook anchor: `'system_app_install'` -- if there is none,
  derive it as each user's first event)
- What is the **target (lagging indicator) definition**? -- anything besides the default D7 retention works: subscription
  conversion, repeat purchase, etc. Also decide the number of elapsed days needed to observe the label.
- What is the **behavior observation window**? (notebook: D0~D1 for EDA, D0 only for the feature matrix -- use the
  "decisive early window" of the reader's service)
- What install period and how many users are analyzed? -- include **only users whose target observation period has elapsed**.

### 2. Data check -- do not start the analysis before it passes

```python
duckdb.query("""SELECT COUNT(DISTINCT user_id) AS users,
    COUNT(DISTINCT event_name) AS event_kinds, MIN(event_date) AS min_d, MAX(event_date) AS max_d
    FROM read_csv_auto('YOUR_CSV_PATH')""").to_df()
```

- Pass criteria: every user has an install event (share of users without one), users ≥ several thousand (stability of
  the 2.5.3 model training), `max_d` is after the last install date + the target's elapsed days (prevents label leakage and
  immature labels), positive/negative ratio of the target label (warn on extreme imbalance).

### 3. Code substitution map

| Anchor (practice / identifier) | What | How |
| --- | --- | --- |
| Load cell `CREATE OR REPLACE TABLE event_log AS … read_csv_auto('data/event_log.csv')` | CSV path, column names | Point at the reader's data -- every later query references the `event_log` table name, so the path lives in this one place |
| Label view cell (`installs`, `d7_label` views; result checked as `labels`) | anchor event `'system_app_install'` | the reader's definition |
| ⚠ D7 window | `date_diff('day', i.install_date, e.event_date) = 7` in the `d7_label` view -- **1 place in the notebook**; `eda_query`, `fm_query` and `sankey_query` JOIN this view | When changing the target's elapsed days, only the one view. But the view definition is replicated in each of the 3 `sql/*.sql` files, so matching the files adds 3 more places. Keep the label column name `d7_retention_flag`, which the three queries and the `fm` split code share |
| `eda_query` | behavior window `<= 1` (D0~D1), noise cut `HAVING d7_ret1_share >= 10 OR d7_ret0_share >= 10` (there is no period filter -- to restrict, add a `WHERE` to the `installs` view) | fit the reader's window and data size |
| EDA highlight cell `spot` | event list `page_view_content_detail, tap_like_button, tap_search_button, tap_share_button, view_error_popup` | the reader's events |
| SHAP dependence cell | `interaction_index="page_view_content_detail"` | the reader's key event |
| `fm_query` ⚠ | the feature event-name list (`page_view_content_detail, tap_like_button, tap_search_button, tap_share_button, page_view_profile, page_view_settings, view_error_popup, tap_tutorial_complete, system_push_permission_granted`) is hardcoded | rewrite for the reader's event taxonomy, **together with** the `NUMERIC` list in the SHAP cell |
| Model cells | `train_test_split(test_size=0.10, random_state=314, stratify=y)`, LGBM parameters, Optuna `n_trials=25` | keeping the defaults is recommended; raise `test_size` if the data is small |
| Sankey CONFIG | `MAX_STEPS = 10`, `TOP_K = 6`, `MIN_USERS = 20`, session window `INTERVAL 1 HOUR` | with many event types, lower `TOP_K` and raise `MIN_USERS` to remove noisy transitions |
| Diagnosis cell | `ret_gap_at_source > 15`, `user_count >= 50` cuts | fit the data size |

- The 3 `sql/*.sql` files are display copies of the inline queries -- if only the notebook is changed, the sql files remain the old version.

### 4. Step-by-step procedure

1. Label view cell -> check the `labels` distribution (retention rate). If it differs wildly from common sense, recheck the label definition.
2. 2.5.2 EDA -> present the top `share_diff` table and chart, agree on the candidate behavior list with the reader.
3. 2.5.3: `fm_query` -> baseline LGBM (`report`) -> if ROC-AUC is near 0.5, go back to feature redesign.
   Optuna tuning -> SHAP summary -> compare the top features against the EDA result. Read thresholds from the dependence plots.
4. 2.5.4: build the Sankey -> find the forks where the color (retention per transition) splits -> `branches` diagnosis.
5. Line up the results of the three lenses -- overlapping behaviors gain credibility, behaviors that appear in only one lens
   get a lower priority -> translate into A/B test candidates (a hypothesis list).

### 5. Interpreting the results

- Behaviors where the three lenses overlap are more trustworthy. If one appears in only one lens, suspect that lens's blind
  spot and lower its experiment priority by one notch (do not discard it).
- Translate a threshold in the dependence plot into an action criterion such as "drive N occurrences during onboarding". But do
  not immediately lock the threshold in as the final target (book 2.3.4).
- The rate difference and the count difference are different signals -- a behavior with a small rate difference that users who do
  it repeat many times (search) is caught by count (book 2.2).
- Read the Sankey for "the path where the metric splits at the same fork", not "the path with the most traffic" (book 2.4.2).
- The final conclusion is always "a list of hypotheses to test" -- not a causal verdict. The next action is to design an A/B test on
  the overlapping behaviors (-> chapter 3) and monitor guardrail metrics after the intervention (book wrap-up table).

## Pitfalls

- What you found is **correlation**. Confirm causal claims with an experiment (A/B).
- Beware of future-information leakage: features must be built only from behavior before the label's point in time.
- An event with a very low share is hard to act on even if it ranks high in SHAP -- look at it together with its share.
  A feature only a few users use is hard to scale to the whole product even if the gap is large (book 2.2). If there are too many
  candidates, prioritize by average performance rate.
- **Selection bias** (book 2.2, 2.4.2) -- users who did a behavior a lot may have been highly interested to begin with, and only
  highly engaged users remain at the late Sankey steps, so retention looks high there.
- In a real log, users whose 7 days since install have not yet passed must be excluded from the population -- the labeling query
  treats anyone without D7 activity as churned, so mixing in recent installs whose observation has not ended distorts the result
  (book 2.5.1).
- A leading indicator is not a fixed answer -- in a fast-growing organization a metric that was valid a few months ago can drop
  in priority, so decide by team agreement and review periodically (book 2.1).
- Do not obsess over model tuning -- for an interpretation model, a 1~2% accuracy difference does not change the conclusion
  (book 2.3.3; 2.5.3.3 is an optional step that can be skipped with `clf = baseline`).

## Study guide

### Core concepts -- what you should be able to explain after this chapter

- **Leading vs lagging indicators** -- early behaviors you can move vs the metrics that appear as their result. Actions can only
  be aimed at the leading side.
- **Aha moment** -- the decisive early experience (behavior + threshold count) that separates retained users from churned users.
- **SHAP value** -- a decomposition of how much each feature pushed or pulled an individual prediction. The summary shows the
  overall tendency, the dependence plot the feature-value-to-contribution relationship (thresholds). Unlike feature importance it
  is per-row and has a direction (positive/negative) (book 2.3.2).
- **Data leakage** -- information from after the label mixing into the features. Respecting the time boundary is the lifeline of this analysis.
- **Cross-checking three methods** -- the attitude of trusting a result only when methods with different assumptions point to the
  same answer. EDA (univariate), SHAP (multivariate model) and Sankey (path) cover each other's blind spots.

### Concept check

1. Why look for leading indicators with three methods rather than one? Name one blind spot of each lens.
   - Hint (book Table 2.3): EDA is univariate and cannot see interactions between behaviors; SHAP costs model setup and its
     contributions are not causal; the Sankey picture changes with the step design (window, TOP_K, MIN_USERS).
2. What does a "threshold" in a SHAP dependence plot mean, and how is it translated into an action?
   - Hint: the feature value where the contribution turns positive -- "drive users up to that count" becomes an onboarding goal.
3. Why are "the model's accuracy (ROC-AUC) is high" and "we found a good leading indicator" different questions?
   - Hint: a highly predictive feature may be impossible to act on (e.g., total usage time) or a tautology of the outcome.
4. How do SHAP values differ from feature importance, and why use SHAP for the leading-indicator search?
   - Hint: feature importance is a global, positive-only metric of "how often it was used" and has no direction. SHAP is a
     per-row contribution with a sign, so you can read "does this behavior raise or lower retention" and the threshold.
5. Why must a high retention rate at late Sankey steps not be read as "that screen creates retention"?
   - Hint: selection bias -- users who reach the late steps are the group where only the highly engaged remain. Compare links
     that branch from the same fork, and confirm the conclusion with an experiment.

### Advanced exercises

1. **[Sandbox]** In the D7 logit block inside `simulate_user` in `generate_data.py` (`0.6 * (session_duration
   >= 150)`, `0.5 * (like_cnt >= 3)`), lower one coefficient (`EVENT_META` is only the event-name-to-screen/description
   mapping and carries no strength) and have the reader predict how the SHAP ranking and the EDA `share_diff` ranking
   will change -> edit -> regenerate -> re-run -> compare. When done, restore with
   `git checkout -- generate_data.py data/` and regenerate.
2. **[Sandbox]** The feature window in `fm_query` is currently D0 only (`date_diff('day', b.install_date, e.event_date) = 0`
   in the `d0_session` CTE). Predict how the model AUC and the top SHAP features change when it is widened to `<= 1`
   (D0~D1) -> run -> compare. Discuss the trade-off "a wider observation window raises predictive power but delays the point
   at which you can act". Restoring is mandatory.
3. **[Thinking]** The three lenses each pointed to a different behavior as number one. Design a procedure for deciding which
   to trust. (Check each lens's assumptions -> prioritize the intersection -> steer toward experiment design; there is no single right answer)
