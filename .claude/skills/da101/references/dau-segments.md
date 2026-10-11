# Diagnosing DAU composition — 5-segment Stock/Flow analysis

**Chapter folder**: `chapters/01_you_cant_raise_DAU_by_staring_at_the_chart/` · Notebook: `dau_segment.ipynb`
<!-- synced: code at duilee/data_analysis_101@226e1dd (Korean original) (2026-10-10) — cross-checked against the notebook, README and sql; book text: cross-checked against the first proofread manuscript (2026-10-10; section structure: intro → 1.1 revisit rate → 1.2 framework (1.2.1-1.2.3) → 1.3 practice (1.3.1-1.3.5) → 1.4 Claude Code practice (1.4.1-1.4.5) → 1.5 wrap-up). Notebook section numbers match book 1.3.x. -->

## The problem this method solves

A single-line DAU chart can't tell you why the service has stalled. Classify users into 5 segments
(new / heavy / light / risk / dormant — new is within 7 days of signup, heavy/light is 5+ / 1-4 days with a
record in the last 7 days, risk/dormant is last record 7-30 days / more than 30 days ago) and diagnose
**where users are leaking and where they are moving** from several angles with the distribution (Stock), the transition matrix (Flow)
and 5 ratio KPIs (HURR/CURR/Heavy Loss/Light Loss/Reactivation).
The whole pipeline is DuckDB SQL, so it ports easily to warehouse queries.

**Pointers to the book's theory sections** (in QnA mode, give only the gist and point to the relevant book section for details):
- Intro — DAU and MAU are classic lagging indicators; staring at the chart cannot answer "what should we do?"
- 1.1 — Two services with the same monthly revisit rate end up on different growth trajectories depending on the growth
  rate of new user inflow (CCGR). The revisit rate is an illusory metric whose meaning changes with the growth stage, so never use it alone.
  The Duolingo case (among segment-level retention metrics, CURR is the key lever of DAU growth) and the Alarmy case (monitoring segments and
  transition paths) in the latter half of 1.1 are the origin of this chapter's framework. See user state from several angles instead of the active/inactive dichotomy.
- 1.2 intro — Fictional service "RoutineLog" (habit tracker; "logged a record today?" is the activity). Framework = boxes (user
  segments, Stock) and arrows (segment changes, Flow). Stock is a point-in-time snapshot; Flow is change over a period.
- 1.2.1 (Table 1.1) — Definition of the 5 segments. Boundaries (5 of 7 days, etc.) are only examples to be adjusted to the service's usage cycle and activity definition.
  Why new is 7 days: whether users stay past the first week is what matters, and the path out of new tells you whether they settled in.
  At a daily granularity, heavy → risk and risk → heavy never happen in one step; they pass through light (a logical constraint).
- 1.2.2 (Table 1.2) — The 10 segment changes:
  New Activation (new → light/heavy) · New Loss (new → risk) · Loyalization (light → heavy) ·
  Heavy Loss (heavy → light) · Light Loss (light → risk) · Risk Loss (risk → dormant) ·
  Reactivation (risk → light) · Resurrection (dormant → light) · HURR (heavy → heavy) ·
  CURR (light+heavy → light+heavy). The notebook's 5 KPIs are HURR, CURR, Heavy Loss, Light Loss and
  Reactivation. Change is viewed two ways: absolute count and 'ratio with the pre-change state as the denominator'.
- 1.2.3 (Table 1.3) — Six health questions answered by segments and changes (size of new, first-week settling, light → heavy/risk ratio,
  defending light → risk, HURR, reactivation). Put 'users active today' next to the Stock and you can split DAU by
  segment (the same DAU of 70 is different on a day with 30 heavy vs. a day with 30 new). Change is viewed not only daily
  but also cumulatively over 30/90 days. Example actions: Heavy Loss spike → check releases/incidents; rising light → risk →
  retention campaign; judge feature experiments by the 'light → heavy transition rate'.
- 1.5 wrap-up — Segments and thresholds are examples (7 days for a daily-use service, 14/28 days for a weekly one). The next action is to
  adjust the rules to our service's cycle and build them as a mart.

## Run and verify

```bash
python generate_data.py      # creates data/user_master.csv, data/user_activity.csv
jupyter nbconvert --to notebook --execute dau_segment.ipynb \
  --output-dir ../../my-work/01_you_cant_raise_DAU_by_staring_at_the_chart   # results go to my-work
```

- Input: `user_master.csv` (`user_id, first_active_date`), `user_activity.csv` (`user_id, event_date`).
- Pipeline: derived-metrics query (3 metrics: `days_since_signup, active_day_count,
  last_active_date` + `d0_active` for the DAU cross-tab → table `user_metrics`) → classification CASE (5 classes, column `user_seg`) →
  segment × logged-today cross-tab (`dau_by_seg`) →
  calendar (`generate_series`, 31 days) × user to compute the same metrics per date (`user_metrics_daily`) →
  same CASE + `lag(user_seg)` to attach yesterday's segment in the mart (`mart_user_segment`, one month) →
  Stock (`dist`) / Flow (`trans`) / KPI (`kpi`) → N-day tracking via self-join in 1.3.5 (heavy 30 days ago → today,
  new 30 days ago → today).
- **Expected results**: the generator (seed 42, 200 users, target date `TARGET = "2026-05-20"`) plants activity tiers and
  churn types (recent/mid/old), so dormant and risk should show up clearly in the Stock, and the transition matrix should
  show the heavy → light → risk → dormant flow and new → heavy/light settling.
  On the example data: Stock new 16 · heavy 39 · light 72 · risk 53 · dormant 20 (total 200), DAU 70
  (new 11 · heavy 30 · light 29); mart `n_days` 31 · `n_rows` 5233; HURR 92.1% · CURR 96.4% ·
  Heavy Loss 7.9% · Light Loss 5.4% · Reactivation 2.0% (1 of 51 risk users); of 45 users heavy 30 days ago,
  heavy 25 (55.6%) · light 12 · risk 8; of 10 users new 30 days ago, 7 remain heavy/light (light 6 · heavy 1).
  These numbers must match the result tables in book section 1.3.

## Apply to your data — interactive protocol

Proceed in order 1→5. Show the reader the result of each step and confirm before moving on.
The notebook has 5 `[Apply to your data]` callouts — follow those spots as the baseline, but the ⚠ items below
cover a wider scope than the comments.

### 1. Intake — what to ask the reader

- **File paths** of the two tables?

| Role (notebook example name) | Column | Type | Required |
| --- | --- | --- | --- |
| User master (`user_master.csv`) | `user_id` | TEXT | Required |
| 〃 | `first_active_date` | DATE | Required (if absent, derive as per-user MIN of the activity log) |
| Activity log (`user_activity.csv`) | `user_id` | TEXT | Required |
| 〃 | `event_date` | DATE | Required (activity log deduplicated to the day level — in the RoutineLog example, the days a habit check-in was logged) |

- The **analysis target date**? (the notebook's `TARGET` — usually yesterday)
- The service's **usage cycle**? (daily-use app or weekly — needed to adjust the segment boundaries)
- How far back does the activity log go? — At least **60 days before the target date** (30 days for the dormant rule + margin) is needed.

### 2. Data check — do not start the analysis until this passes

```python
con.execute("""SELECT COUNT(DISTINCT user_id) AS users, MIN(event_date) AS min_d,
    MAX(event_date) AS max_d FROM read_csv_auto('YOUR_ACTIVITY_PATH')""").df()   # reuse the notebook's con
```

- Pass criteria: `max_d` ≥ target date, log span ≥ 60 days, master users include the activity-log users
  (check the share of null `first_active_date` after the LEFT JOIN). If the activity log is at event grain (multiple rows per day),
  tell the reader to dedup it to the day level first.

### 3. Code substitution map

| Anchor (practice section / identifier) | What | How |
| --- | --- | --- |
| ⚠ CSV paths | The one f-string `read_csv_auto('data/{t}.csv')` in the setup cell's `for t in ["user_master", "user_activity"]` loop | The path is derived from the table name — if the file names differ from the table names, unroll the loop into two lines or switch to a `{table_name: path}` dict. Later queries refer to table names, so no further edits are needed |
| ⚠ Target date | One place, `TARGET = "2026-05-20"` in the setup cell — each query inserts it via f-string `DATE '{TARGET}'`, and the loading range in 1.3.3 (`TARGET - INTERVAL 30 DAY ~ TARGET`) is derived from it too | Change only `TARGET` to your date |
| ⚠ Segment boundaries | new window 7 days, heavy rule 5 active days, dormant rule `INTERVAL 30 DAY` | **Both the classification CASE in 1.3.2.2 and the CASE in the 1.3.3 mart query** — identical CASE down to the column names, so always edit both together |
| ⚠ Recency window | `INTERVAL 6 DAY` | Edit both the derived-metrics query (`user_metrics`, 1.3.2.1) and the daily metrics query (`user_metrics_daily`, 1.3.3) together |
| 1.3.3 | `generate_series(DATE '{TARGET}' - INTERVAL 30 DAY, DATE '{TARGET}', INTERVAL 1 DAY)` | Loading range — increase `30 DAY` to match the N-day tracking span (60/90 days) |
| 1.3.5 | `nday_query.format(seg="heavy")` | Starting segment to track — the notebook runs both `heavy` and `new` |

- Leave `SEG_ORDER` (the 5 segment names) and the calculation logic of the 5 KPIs (`hurr_pct, curr_pct, heavy_loss_pct, light_loss_pct,
  reactivation_pct`) as they are.
- Boundary adjustment guide: the longer the service's cycle, the more you should stretch the recency window (6 days) and the heavy rule (5 of 7 days)
  by multiples of the cycle (book 1.5: 7 days for a daily-use service, 14/28 days for a weekly service). The definition of
  'activity' can also be changed from app opens to purchases, content consumption, or use of a core feature.
- The 8 `sql/*.sql` files are display copies of the inline queries — if you only edit the notebook, the sql files are left as the old version.
- When porting to a warehouse (book 1.3.2.1, 1.3.2.2): `count_if` → BigQuery `COUNTIF` / Snowflake `COUNT_IF`, otherwise
  `SUM(CASE WHEN … THEN 1 ELSE 0 END)`; `generate_series` → BigQuery `GENERATE_DATE_ARRAY`;
  `lag() OVER (PARTITION BY user_id ORDER BY target_date)` is standard SQL, so it stays as-is.

### 4. Step-by-step walkthrough

1. Run the derived-metrics query (1.3.2.1) → check the `user_metrics` distribution (summary statistics of the 3 metrics) — look together with the reader
   at whether the boundary values sit at meaningful points in the actual distribution.
2. Classification CASE query (1.3.2.2) → user counts by segment. If a segment has 0 users or more than 90%, readjust the boundaries.
3. Load the mart (1.3.3, `user_metrics_daily` → `mart_user_segment`) → show the from→to moves of a few representative users and confirm the classification matches intuition.
4. Run Stock (1.3.4.1) → Flow (1.3.4.2) → KPI (1.3.4.3) in order, attaching an interpretation to each.
5. (If the reader wants) 30-day tracking via the self-join in 1.3.5 — in practice, recommend a daily batch loading structure.

### 5. Interpreting the results

- Stock for the current composition → Flow for the direction of movement → the 5 KPIs for the trend. Take the largest outflow transition
  (e.g. heavy → light, light → risk) as the action target.
- Even if the Stock looks good, a bad Flow (rising heavy → light, light → risk transitions) means it will soon collapse — always look at both axes together.
- DAU is the segment Stock crossed with 'logged today?' (`dau_by_seg`) — the same DAU is different on a day filled by heavy users and a day filled by new users.
- Translate into action (book 1.2.3, 1.5): on a day when Heavy Loss spikes above normal, check releases and incidents first; when the light → risk
  ratio rises, run a retention campaign targeting those users; "DAU down 200" has a different cause and response on a day when New Loss spiked
  versus a day when Heavy Loss spiked. The success criterion for a feature experiment is not total DAU but the 'light → heavy transition rate'.

## Pitfalls

- 1.3.5 (N-day tracking) is only meaningful when the mart is loaded for many days — in practice, build the daily batch
  loading structure first.
- Changing the segment rules frequently breaks time-series comparison. Version each rule change and recompute retroactively.
- **Read ratio metrics together with the denominator size** (book 1.3.4.3). A segment with few people swings wildly on one or two users
  — show the denominator alongside, or accumulate over a period to enlarge the denominator before interpreting.
- **Never compute long-term retention by multiplying 1-day retention N times** (book 1.3.5). It misses round trips between
  segments — measure it directly by stacking the mart for N days, as in 1.3.5.
- **The illusion of interpreting the revisit rate alone** (book 1.1) — read the segment diagnosis together with the trend of inflow cohorts as well.

## Study guide

### Core concepts — what you should be able to explain after finishing this chapter

- **Stock vs Flow** — composition at a point in time (stock) vs. movement between points in time (flow). DAU is just a one-day
  observation layered on the Stock; health lives in the Flow.
- **The 5 segments** — first week after signup (new) / activity frequency (heavy, light) / churn stage (risk, dormant), discretized on the same 7-day
  window. The path out of new (→ heavy/light vs. → risk) is exactly whether the user settled in during the first week.
- **Transition matrix** — the cross-tab of yesterday's segment × today's segment. The service's "user flow map".
- **The 5 ratio KPIs** — HURR (heavy user retention), CURR, Heavy/Light Loss, Reactivation. The transition matrix summarized into
  a handful of trackable metrics.
- **Segment mart** — a table holding two points in time in one row. Loaded by daily batch, it becomes the source of every analysis.

### Concept check

1. Why can a service be at risk even when the Stock looks good (high active share)?
   - Hint: Flow — if heavy → light and light → risk transitions exceed inflow, the Stock collapses with a lag.
2. Between HURR and Reactivation, which metric should our service look at first right now, and on what grounds?
   - Hint: a large heavy share → HURR (defend it); a large risk pool → Reactivation (revive risk → light) —
     the Stock composition sets the priority. Include the denominator size in the reasoning (1 of 51 risk users = 2.0%).
3. If two services with the same DAU have different segment compositions, what differs?
   - Hint: the future DAU trajectory and the action portfolio — heavy-centric is stable, new-centric is vulnerable to retention.
4. The 1-day HURR is 92.1%, yet the same heavy group measured on a 30-day basis is 55.6%. Why are the two numbers so
   different, and why can't you multiply the 1-day HURR 30 times?
   - Hint: small daily churn accumulates + multiplication can't capture round trips of dropping to light and returning to heavy
     — that is why you stack the mart for N days and measure directly (1.3.5).
5. Why can two services with the same 75% monthly revisit rate have completely different Active User trajectories?
   - Hint: the growth rate of new inflow (CCGR) — the revisit rate is an illusory metric whose meaning changes with the growth stage,
     so look at inflow cohort growth together with the level at which the retention curve flattens.

### Advanced exercises

1. **[Sandbox]** Have the reader predict how the Stock and transition matrix would change if the `recent` churn share in
   `generate_data.py`'s `CHURN_TYPES` were raised substantially (which segment swells, which transition grows).
   Edit → regenerate → rerun the notebook → compare. When done, restore with `git checkout -- generate_data.py data/` and
   regenerate.
2. **[Sandbox]** If the heavy rule is lowered from `active_day_count >= 5 → >= 3` (⚠ in both the 1.3.2.2 CASE and the 1.3.3 mart query CASE),
   predict which direction HURR and Heavy Loss each move → run → compare. Discuss "the illusion that lowering the boundary makes the metrics
   look better". Restoring afterwards is mandatory.
3. **[Thinking]** If our service has many "users who paid for a subscription but don't open the app", how should the 5-segment
   scheme be extended? (Discuss Socratically, centered on adding a value-behavior axis beyond app opens and the trade-off in
   the number of segments)
