# DAU contribution estimate — power-law retention fit

**Chapter folder**: `chapters/05_how_much_DAU_is_this_feature_worth/` · notebook: `dau_forecast.ipynb`
<!-- synced: code at duilee/data_analysis_101@8e8b97c (Korean original) (2026-09-13) — cross-checked against notebook, README and sql; book text: cross-checked 2026-09-26 (manuscript section layout: section 1 opening quiz → 2 → 3 (3.1) → 4 (4.1–4.2) → 5 (5.1–5.2) → 6 (6.1–6.2) → 7 → practice 0–3 → Claude Code practice 0–4 → wrap-up). -->

## The problem this method solves

Fit a power law `y = a·x^b` to the new-user retention curve to get the shape coefficient `b`,
fold the one-year cumulative sum of `x^b` into a single constant, and build the formula
**`DAU contribution = new users × (1 + D1 retention × constant)`**.
It lets you estimate roughly how many DAU a single feature or a single acquisition campaign is worth in the long run.

**Book theory pointers** (in QnA mode, give the gist and point to the relevant book section for details)

- **Opening quiz (5.1, Table 5.1)** — Feature A with 6,700 new users/day and D1 7%, versus feature B with 600 new users/day
  and D1 35%: which converges to the larger DAU? The answer is revealed in 5.8.4 (A ≈ 35,800, B ≈ 13,600 — with constant 62).
- **Why estimate feature DAU up front (5.2)** — the PO's quarterly-planning question ("what is this feature's impact and a realistic target?").
  Feature-level DAU is the base for downstream metrics such as conversion rate and revenue, so it is the starting point for sizing impact;
  ideally you compute the contribution of each proposal and prioritize accordingly. A new feature gives you no intuition, so quantify it
  from new users and retention.
- **What matters (5.3, the two questions in 3.1)** — (1) You must be able to answer how much a lever (acquisition, retention) moves DAU —
  e.g. simulate whether doubling new users or improving retention by 10% is more effective.
  (2) The metric must be a leading indicator with a short feedback cycle — pick monthly retention and the cycle stretches from 1 day to 1 month.
  New users and new-user D1 retention satisfy both, and everyone on the team understands the pair. See book 5.3.
- **Where Carrying Capacity fails (5.4)** — 5.4.1: `new users / daily churn rate` is the sum of a geometric series (the same fraction retained every day).
  It computes feature A as `6,700 / 0.93 ≈ 7,200`, but the actual figure exceeds 20,000. 5.4.2: the formula's two premises —
  a narrow definition of active users as "those who hit the wow moment" (assuming 80–90% daily retention) and the assumption that
  daily retention stays constant every day — do not match general DAU. Figure 5.1: `y = a^x` collapses to near zero within 30 days even at a=0.8.
- **Power-law curve and cumulative sum (5.5)** — 5.5.1: real new-user retention drops sharply at first and then flattens, so `y = a·x^b` (b<0)
  fits. `a` is the starting point, `b` the shape (Figure 5.2: exponential decay 0.8^x vs. power law 0.8·x^-0.3; Figure 5.3: b varying from -0.3 to -0.6).
  5.5.2: today's DAU = today's new users + retained share of yesterday's new users + … = `new users × cumulative sum of the retention curve`
  (assuming a constant number of new users per day). This cumulative sum is the same concept as Lifetime in chapter 4 (area under the curve),
  differing only in whether the y(0) term is included. See book 5.5.
- **The one-click formula (5.6)** — 5.6.1: decompose the cumulative sum as `1 + a·(1^b + … + N^b)`; then `a` is simply new-user D1 retention,
  and the parenthesized part is a constant you can precompute once you know `b` (the x=0 term cannot be computed as `0^b`, so it is set to
  "everyone retained on install day" = 1). 5.6.2: `b` comes from the curve of **all new users of the service**, not from the new feature
  (if the feature is very different in nature, use the most similar feature's curve) — waiting 1–2 months for feature-level data defeats
  the purpose of predicting ahead. The assumption: within the same product, starting points differ but the decay shape (slope) is similar. See book 5.6.
- **As a decision tool (5.7, Table 5.2)** — with constant 62, feature A scenarios: baseline ≈35,800 / new users +50% (10,050) ≈53,700 /
  D1 +5%p (12%) ≈56,500 / new users +20% and D1 +2%p (8,040, 9%) ≈52,900. Lever conversion: 1%p of D1 ≈ 4,200 DAU (= 6,700 × 1% × 62)
  ≈ about 800 new users/day (= 4,200 ÷ (1 + 62 × 0.07)). To the PO's "target of 50,000 next quarter," answer along the lines of
  "holding D1 at 7%, you need about 2,700 more new users/day (1.4× today), or about +3.5%p of D1."
  Note that this is **feature DAU**, not the net increase in service-wide DAU (users may have moved over from other features) —
  recommend measuring net lift with a treatment/control group. See book 5.7.
- **Practice sections (5.8.1–5.8.4)** — 5.8.1 data preparation (`active_daily.csv`, 5 columns) → 5.8.2 `b` from the retention curve →
  5.8.3 simplify into a constant → 5.8.4 quiz answer revealed. Same structure as the notebook.
- **Wrap-up** — two practical tips: use stabilized numbers instead of early figures that swing with launch effects and rollout rates,
  and for long-running features add the users already accumulated as `+ existing-user term`
  (`DAU = new users × (1 + D1 × constant) + existing-user term`).
  The value of this method is that when growth falls short of expectations, you can separate whether it is an acquisition problem or a retention problem.
  Summary table: question "how many users will one new feature gather?" / situation "a number for prioritizing before launch" /
  solution "new users × (1 + D1 retention × constant)" / caution "the constant differs per service (62 in the book text, about 40 in the practice)" /
  next action "compare against actual DAU after launch; refit the curve if they diverge widely."

**Example invocations from the book's Claude Code practice section** (each maps to a current skill mode)

- run: "Let's go through the DAU contribution estimate practice" / `/da101 run DAU contribution` — generator → run the whole notebook → walk through 5.8.2–5.8.3
  (5.8.4 is markdown arithmetic).
- apply: "Estimate how many DAU this feature is worth from our new feature's usage log" / `/da101 apply DAU contribution` —
  the 4 intake questions (path, column mapping, definition of new user, observation window) are the same as step 1 of the protocol below.
- qna: "How does the cumulative sum of retention turn into DAU?" (answer with the cohort decomposition) /
  `/da101 qna the self-join retention query in retention_curve.sql …` — explain in order: base → installs (2 views) → daily_stat →
  population (2 CTEs) → final SELECT.
- quiz: "Give me just 5 quiz questions" / `/da101 quiz DAU contribution` — the 5 concept-check questions below are the question pool.

## Run and verify

```bash
python generate_data.py      # creates data/active_daily.csv
jupyter nbconvert --to notebook --execute dau_forecast.ipynb \
  --output-dir ../../my-work/05_how_much_DAU_is_this_feature_worth   # outputs go to my-work
```

- Input: `data/active_daily.csv` (`date, user_id, platform, country_code, install_flag`).
- `sql/retention_curve.sql` (identical to the inline query) builds D1–D28 retention per basis_month × platform
  (3 months × 2 platforms × 28 days = 168 rows).
- **Expected results**: the generator (seed 42, daily cohorts for 90 days from 2026-01-01, ~100 new users/day per platform) plants
  ios `a=0.42, b=-0.45` and android `a=0.35, b=-0.50`. The `b` from `curve_fit` per cohort group should recover values near these,
  and the observed and model curves should overlap. On the example data (notebook output = the numbers in the book's practice section):
  `rows: 168`, first row of `df.head()` android 2026-01 D1 0.3487 · D2 0.2419 · D3 0.2065;
  mean `b` **-0.4804** (iOS -0.4603, Android -0.5005), `df_constant` 6 rows — android `a` 0.347~0.351 ·
  `b` -0.497~-0.504, ios `a` 0.425~0.436 · `b` -0.455~-0.466; `baseline = 39.9` (about 40).
  Differing from the book's example service (62) is normal — the constant depends on the service's `b`.
- The constant in 5.8.3 is computed as `baseline = np.sum(np.arange(1, 365) ** b_mean)` (≈39.9). The `1` in the formula (today's new users)
  is not folded into the constant; it stays separate inside the parentheses of `1 + D1 × constant`.
- 5.8.4 reveals the answer by plugging the formula into the opening quiz; it is a single markdown cell (no code, arithmetic with constant 62 —
  it uses the book's example-service constant, not the practice data's ~40).

## Apply to my data — interactive protocol

Proceed in order 1→5. Show the reader the result of each step and confirm before moving on.
This notebook has no `[apply to my data]` comments, so the substitution map below is the only guide.

Point out first that the data comes in **two strands**: the coefficient `b` is estimated from the retention curve of
**all new users of the service**, not the new feature (a new feature's observation window is too short), while from the feature's
own log you only need the **daily number of new users and D1 retention**.

### 1. Intake — what to ask the reader

- What is the **file path** of the service-wide daily activity log CSV (or an already computed retention table)?
- Column mapping — which of the reader's columns plays each role in the table below?

| Role (notebook example name) | Type | Meaning | Required |
| --- | --- | --- | --- |
| `date` | DATE | activity date | required |
| `user_id` | TEXT | user identifier | required |
| `install_flag` | BOOL | whether that day is the first activity (install) day | required* |
| `platform` | TEXT | segment axis (platform, country, etc.) | optional |

  *If there is no `install_flag`, explain that it can be derived as `MIN(date)` per user.
- What is the **definition of a new user**? (app install date, or first use of the feature?)
- Is the observation window sufficient — the service-wide new-user log must cover at least **2 monthly cohorts × 28 days of observation**.
- If a D1–D28 retention table already exists, skip the SQL step and take that table.
- On the feature side: are the daily new-user count and D1 retention taken from the **stabilized period** after launch effects and rollout rates have settled?

### 2. Data check — do not start the analysis until it passes

Run the following on the reader's file and show the result (row count, user count, date range, number of new users):

```python
duckdb.query("""SELECT COUNT(*) AS rows, COUNT(DISTINCT user_id) AS users,
    MIN(date) AS min_d, MAX(date) AS max_d,
    SUM(CASE WHEN install_flag THEN 1 ELSE 0 END) AS installs
    FROM read_csv_auto('YOUR_CSV_PATH')""").to_df()
```

- Pass criteria: date range ≥ 2 months, new users per (monthly) cohort ≥ several hundred (warn that with fewer, retention fluctuates
  and the fit becomes unstable), check null ratios. If it falls short, say what is missing and stop.

### 3. Code substitution map

Read the relevant notebook cells and change only the following. Reuse the rest of the code as is.

| Anchor (practice section / identifier) | What | How |
| --- | --- | --- |
| 5.8.2 `con.execute` CREATE VIEW cell (`base`, `installs` views) | `read_csv_auto('data/active_daily.csv')`, column mapping | Replace with `YOUR_CSV_PATH`. Map column names in the SELECT of the `base` view (⚠ the `query` cell contains no path) |
| 〃 `installs` view | `WHERE install_flag = TRUE` (definition of new) | Use the reader's definition of new (if none, replace the view definition with `SELECT user_id, MIN(date) … GROUP BY user_id`) |
| 〃 ⚠ | `BETWEEN 1 AND 28` observation window | If you change it, change `days = np.arange(1, 29)` in the fitting cell **together** |
| `b_mean` cell and plot cell | hardcoded `'ios'` / `'android'`; in the plot cell `plt.subplots(1, 2)` and `zip(axes, ["ios", "android"])` (subplot count 2 is also fixed) | Use the reader's segment values and count (for one segment use `axes = [ax]`; with no segments remove the group axis) |
| 5.8.3 cell | `np.arange(1, 365)` horizon | Set to the desired horizon (keeping the default 1 year is recommended) |

- Do not touch the `func(x, a, b)`, `curve_fit(..., maxfev=10000)`, `df_constant` and `baseline` computation logic.
  Do not add a `p0` initial guess (it converges with the defaults).
- `sql/retention_curve.sql` is a display copy of the inline query — tell the reader that editing only the notebook leaves the sql file
  as an outdated version.

### 4. Step-by-step walkthrough

1. Run the CREATE VIEW cell, then the `query` cell → show the retention table. Check that it decreases monotonically by day_diff,
   and that `df.groupby(['basis_month', 'platform']).size()` is 28 everywhere (days with zero retained users drop out as rows,
   and `curve_fit` fails on the length mismatch — if any are missing, `reindex(days, fill_value=0)`).
2. `curve_fit` per group → present the `df_constant` table (`a`, `b` per group). Check the spread of `b` across groups —
   if the spread is large (e.g. 0.1 or more), do not fold into a single constant; propose a constant per segment instead.
3. Plot observed vs. model curves → confirm fit quality with the reader (does the early sharp drop and the later tail match?).
4. Compute `baseline` → ask for the feature's daily new users and D1 retention, and compute the final DAU contribution
   (laying it out like the quiz table in 5.8.4 works well). When stating the result, attach the reference horizon ("expected DAU at the one-year mark").

### 5. Interpreting the results

- The closer `b` is to 0 (flatter), the larger the constant = the greater the long-term DAU value of one new user.
- The formula lets you separately compute the expected effect of actions that "increase new-user inflow," "raise D1," and "flatten the curve" —
  plug in the actions the reader is discussing. Recomputing the lever conversion from book 5.7 (1%p of D1 ≈ how many new users/day) with
  the reader's numbers is a good idea.
- Back-solving a target (the PO example in book 5.7): for "target DAU 50,000," compute the required daily new users as `target ÷ (1 + D1 × constant)`,
  and the required D1 as `(target ÷ new users − 1) ÷ constant`; show how many times the current values that is, and point out the more realistic lever.
- This value is **feature DAU**. The net increase in service-wide DAU may be smaller because users moved over from other features;
  if net lift is the question, recommend a treatment/control comparison.
- Always state alongside that this is a 365-day extrapolation from D1–D28 observations.
- Next action (book wrap-up): compare the estimate against actual DAU after launch, and refit the curve if they diverge widely.
  If growth falls short, split the cause along the two levers — acquisition problem or retention problem.

## Pitfalls

- Do not hardcode a `p0` initial guess in `curve_fit` — the defaults converge fine.
- A power law is the right model for a sharp early drop followed by gentle decline. If retention oscillates with day-of-week effects,
  smooth with weekly averages before fitting.
- Unlike a geometric series, the cumulative sum of `x^b` has no limit — extend the horizon and the constant keeps growing.
  When sharing the constant, always state the reference horizon such as "at the one-year mark."
- The constant differs per service (62 in the book's example, about 40 on the practice data). Do not borrow someone else's constant;
  compute it from your own service's curve.
- `b` comes from the new-user curve of the whole service (or the most similar feature), not from the new feature's own short data.
  From the feature side, use only new users and D1, taken from the stabilized period after launch effects and rollout rates have settled.
- A long-running feature has users already accumulated, so new users and D1 alone do not explain it — add the gap between
  the estimate and actual DAU as an `existing-user term`.
- What the formula gives is feature DAU, not the net increase in service DAU (cannibalization). Measure net lift with an experiment.
- If long cohorts exist, calibrate the extrapolation against actuals. If actual DAU after launch diverges widely from the estimate, refit the curve.

## Study guide

### Core concepts — what you should be able to explain after this chapter

- **Retention curve** — a cohort's D+n retention rate plotted against n. DAU is the sum of past cohorts' curves.
- **Power-law decay** — `y = a·x^b` (b<0). Unlike exponential decay, it has a fat tail and fits app retention well.
- **Shape coefficient `b`** — how quickly the curve bends. A "habit formation" metric separate from `a` (starting point ≈ D1).
- **Folding into a constant** — `Σ x^b` (x = 1~364; in the formula, `1 + D1 × constant`). Summarizes the whole curve as a single
  multiplier: "the number of active days one new user generates in a year."
- **Limits of extrapolation** — it estimates 365 days from 28 days of observation, so the model assumption is itself the risk.

### Concept check

1. One service has `b` = -0.3 and another has `b` = -0.6. Which one has the larger long-term DAU multiplier (constant)?
   Explain why as well.
   - Hint: -0.3. The closer `b` is to 0, the slower `x^b` decays → the cumulative sum grows larger.
2. The final formula, "new users × (1 + D1 retention × constant)," deliberately keeps D1 retention and the constant separate.
   Why keep them separate instead of merging them into one?
   - Hint: `a` (=D1) is moved by onboarding improvements, while the curve shape (`b`) is moved by habit-forming features — the levers
     differ, and `b` is computed once from the service-wide curve and reused as a constant.
3. Explain, in terms of cohorts, why "today's DAU = new users × cumulative sum of the retention curve."
   What assumption is needed for this equation to hold?
   - Hint: today's DAU = today's new users + retained share of yesterday's new users (D1) + retained share of the day before's new users (D2) + ….
     The daily number of new users must be constant to factor it out as a common term.
4. The Carrying Capacity formula computed feature A's DAU as 7,200, but the actual figure exceeded 20,000. Where did the
   underestimate come from?
   - Hint: the geometric-series (exponential decay) assumption that daily retention is constant every day — within 30 days, retention
     collapses to near zero. The real curve is a power law that drops sharply and then flattens, so retained users from old cohorts accumulate.
5. You computed the one-year constant from a `b` estimated on D1–D28 observations. What two things must you state when sharing this
   constant with another team, and why?
   - Hint: (1) The reference horizon — the cumulative sum of `x^b` does not converge, so the constant grows with the horizon
     ("expected DAU at the one-year mark"). (2) That it was computed from our own service's curve — it differs per service
     (62 in the book text vs. 40 in the practice), and it is a 365-day extrapolation from 28 days of observation.

### Advanced exercises

1. **[Sandbox]** Have the reader first predict roughly what the `baseline` constant becomes if ios `b` in `PLATFORM_PARAMS` of
   `generate_data.py` changes from `-0.45 → -0.70` (how many times the current value?).
   Then modify → `python generate_data.py` → rerun the notebook to confirm.
   When done, restore with `git checkout -- generate_data.py data/` and regenerate.
2. **[Sandbox]** Predict how the estimated `b` and `baseline` change if the observation window in the 5.8.2 `query` is shortened from
   `BETWEEN 1 AND 28 → BETWEEN 1 AND 14` (together with `np.arange(1, 15)` in the fitting cell) → run → compare.
   Discuss "what becomes unstable as the observation window gets shorter." Restoring afterwards is mandatory.
3. **[Calculation]** Refill the quiz table in 5.8.4 and the feature A scenario table from book 5.7 (constant 62) with the practice data's
   constant (about 40): have the reader first predict what each scenario's DAU becomes and how the conversion
   "1%p of D1 ≈ how many new users/day" changes, then compute it together.
4. **[Thinking]** If our service has strong weekly usage habits (users who only use it on weekends), where does this method break,
   and how should it be adapted? (No single right answer — discuss Socratically around the data aggregation unit, the model's
   functional form, and the interpretation of the constant.)
