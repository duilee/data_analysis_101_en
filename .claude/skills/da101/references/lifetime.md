# Lifetime estimation — 3 methods from 7-day retention + triangulation

**Chapter folder**: `chapters/04_predict_lifetime_from_one_week_of_data/` · notebook: `lifetime_estimation.ipynb`
<!-- synced: code at duilee/data_analysis_101@226e1dd (Korean original) (2026-10-10) — cross-checked against the notebook, README and sql (power-law b<0 convention reflected); book text: cross-checked against the first proofread draft (2026-10-10, section layout: intro → 4.1 definition → 4.2 what it means for ad-based services → 4.3 accuracy/speed trade-off → 4.4 three methods (4.4.1~4.4.3, each with strengths/weaknesses subsections) → 4.5 grounds for judgment (4.5.1~4.5.2) → 4.6 practice (4.6.1~4.6.6) → 4.7 Claude Code practice (4.7.1~4.7.5) → 4.8 wrap-up). Notebook section numbers match the book's 4.6.x. -->

## The problem this method solves

Estimate user lifetime (average number of active days between signup and churn) from only the first 7 days of retention.
Apply three methods with different assumptions to the same cohort and cross-check the results (triangulation):

- **4.6.2 (Case 1). Churn-rate heuristic** — D1~D7 area + a geometric-series tail beyond D7 (`d7*r/(1-r)`).
- **4.6.3 (Case 2). Retention catalog matching** — the lifetime of the minimum-SSE curve on (D1, D3, D7) among 3,456 power-law curves (`D_t = D1·t^b`, b < 0).
- **4.6.4 (Case 3). Direct measurement on a mature cohort** — rescale a year-old cohort's measured lifetime by the ratio of the two cohorts' 7-day areas.
- **4.6.5. Comparing the three methods** — put the three estimates side by side in one table and bar chart and read them as a triangulation.

The notebook headings are `4.6.2~4.6.5`; `Case 1/2/3` in this document refer to `4.6.2/4.6.3/4.6.4` respectively
(4.6.3 subsections: 4.6.3.1 build catalog → 4.6.3.2 visualize → 4.6.3.3 SSE matching → 4.6.3.4 interpretation / 4.6.4: 4.6.4.1 area-ratio rescaling → 4.6.4.2 interpretation /
4.6.5: comparison table and chart → 4.6.5.1~4.6.5.2 interpretation → 4.6.6 cross-check).

**Pointers to the book's theory sections** — direct the reader to the book for the detailed explanation.

- Intro: the motivating problem — lifetime (≠ LTV) is neither a daily metric nor a headline dashboard number, but once a
  calculation framework is in place it becomes the reference value for marketing unit costs, channel expansion and
  profitability assessment, a core metric with wide-reaching impact.
- 4.1: definition of lifetime — not a calendar period but the **sum of active days** = `ΣD_k` = area under the retention curve (figure 4.1).
  This identity holds only for **classic retention** (share active on exactly day N after signup) and cannot be used with rolling retention.
  Three reasons to cut off at one year (365 days): CAC payback period of 6~12 months, time value / discount rate, uncertainty of long-range estimates.
  For habit-forming services with heavy tails, extend the period or adjust.
- 4.2: for ad-based services **LTV ≈ lifetime × ARPDAU** — lifetime sets the ceiling on CAC
  (book example: 50 days × $0.03 = $1.5; stretching lifetime to 100 days gives $3). For commerce, purchase frequency and basket size matter more than lifetime.
- 4.3: accuracy/speed trade-off — a 1-year measurement is too late and 1~2 days is too noisy, so the practical compromise is **7 days**
  (captures the early steep drop plus day-of-week effects, and lets you judge campaign performance within 1~2 weeks).
- 4.4 intro: all three methods "estimate long-term lifetime from the first few days", but the approach and assumptions differ. The criterion is
  not accuracy but usefulness for decision-making.
- 4.4.1: churn-rate heuristic — the difference between the daily survival ratio r (share remaining today relative to yesterday) and retention (curve height) (figure 4.2),
  geometric-series formula. 4.4.1.1 strengths (one-line SQL, reproducibility, baseline) / 4.4.1.2 weaknesses (r sensitivity, underestimates heavy tails).
- 4.4.2: retention catalog matching — 4.4.2.1 pre-draw power-law curves on a (D1 anchor 15~50%, b) grid (figure 4.3;
  sBG and Weibull are alternatives). 4.4.2.2 catalog table structure (table 4.1). 4.4.2.3 pick the minimum-SSE row on D1, D3, D7 —
  the role of the three points (D1 = depth of the cliff, D3 = curvature of the early deceleration, D7 = mid-term stabilization).
  4.4.2.4 strengths (instant results, reproducibility, no extrapolation) / 4.4.2.5 weaknesses (catalog coverage — anchor step 0.01 recommended; single-point noise —
  bundle a week of signups into one cohort; upfront build cost).
- 4.4.3: direct measurement on a mature cohort — 4.4.3.1 the measured lifetime of a cohort from a year ago (`ΣD_1..D_365`, no model assumption),
  4.4.3.2 rescale by the D1~D7 area ratio (why use the 7-day cumulative area rather than the single point D7 = noise cancels out).
  4.4.3.3 strengths (realism and persuasiveness — "40 days last year, first 7 days 15% higher, so about 46 days"; stability) / 4.4.3.4 weaknesses (needs 1+ year of data,
  does not reflect structural changes or changes in the long tail).
- 4.5: the three methods in one line each — the heuristic is for quick screening and a baseline, the catalog for automation and consistency, the mature cohort
  reflects the service's own texture. New service → heuristic; stabilized → catalog; after a year → run the mature cohort alongside and cross-check.
- 4.5.1: four decisions that lifetime estimation changes (CAC guideline, unified evaluation of conflicting experiments, early evaluation of improvements,
  comparing channel and cohort quality).
- 4.5.2: there is no perfect model — an estimate with 80% confidence today is more valuable to the business than a 100% answer a year from now. The goal is
  not prophecy but reducing decision risk and seizing opportunities quickly.
- 4.8 wrap-up: the analyst's core skill is not decimal-point accuracy but an **estimation system that runs consistently** in step with the business cycle
  (an estimate built on the same basis so channels and cohorts can be compared is more useful than a refined estimate whose basis changes every quarter).
  **Re-estimate** as D30 and D90 measurements accumulate, and feed the gap between estimate and measurement into the next estimate.
  Next actions from the summary table: get LTV early as estimated lifetime × ARPDAU and feed it into the CAC guideline (→ chapter 7 unit economics),
  and systematize D30/D90 re-estimation.

## Run and verify

```bash
python generate_data.py      # creates data/cohort_retention.csv
jupyter nbconvert --to notebook --execute lifetime_estimation.ipynb \
  --output-dir ../../my-work/04_predict_lifetime_from_one_week_of_data   # results go to my-work
```

- Input: `data/cohort_retention.csv` — `day, retention`, 8 rows (D0=1.000, D1=0.341 … D7=0.244).
- 4 SQL files: `heuristic.sql` (4.6.2), `catalog_match.sql` (4.6.3), `mature_cohort.sql` (4.6.4),
  `compare_methods.sql` (4.6.5 comparison).
- **Note**: the power-law catalog (3,456 rows) is generated on the fly inside the notebook from the `power_curve(b, d1)` grid
  and registered in DuckDB as `lifetime_catalog`. So `catalog_match.sql` and `compare_methods.sql`
  **cannot run standalone** — run them only within the notebook flow.
- **Expected results**: in 4.6.5 the three methods' lifetime estimates are compared in one table and bar chart, and against the planted truth
  you should get **4.6.2 (Case 1) ≈ 13.3 days, 4.6.3 (Case 2) ≈ 52.2 days, 4.6.4 (Case 3) ≈ 52.5 days** (values printed in the book: 13.33 / 52.15 / 52.52).
  Intermediate values can be checked too — Case 1: 7-day area 1.912, D7 0.244, r=0.9791, tail 11.42 / Case 2: catalog of 3,456 curves (36×96),
  D1 range 0.15~0.50, lifetime range 1.0~142.9 days (b grid is −1.00~−0.05); match (D1, b)=(0.34, −0.18),
  SSE 0.000057 / Case 3: new area 1.912 vs mature 1.875, scaling factor 1.0197. The LTV rough estimate in the wrap-up (4.6.6) is, at ARPDAU $0.015,
  13 days ≈ $0.2 and 52 days ≈ $0.78. The numbers should match the results table in book section 4.6. Cases 2 and 3 converging within
  a few days of ~52 days while only Case 1 (the heuristic) comes out far lower is **normal and is this chapter's lesson** —
  the geometric-series assumption cannot express a heavy tail, so it systematically underestimates; triangulation means
  trusting the value where the two methods with different assumptions (2 and 3) meet and doubting the outlier (1).
  Do not judge the chapter broken just because all three values did not converge.

## Apply to your data — interactive protocol

Proceed in order 1→5. Show the reader the result of each step and confirm before moving on.
The notebook has 7 `[Apply to your data]` callouts — follow those points by default. Inside the notebook each
constant lives in one place, but the standalone `sql/compare_methods.sql` duplicates the same constants (marked ⚠).

### 1. Intake — what to ask the reader

- Do you have the new cohort's D0~D7 retention? In what form?

| Role (notebook example name) | Column | Meaning | Required |
| --- | --- | --- | --- |
| `cohort_retention.csv` | `day` (0~7) | days since signup | required |
| 〃 | `retention` | retention on that day (D0=1.0) | required |

- **Cohort definition**: is it based on the same signup week (or month)? An all-user average will not do — guide the reader to
  recompute on a cohort basis first.
- Cohort size? (warn about retention swings if under a few hundred users)
- **For Case 3**: is there a mature (year-old) cohort whose churn has effectively finished? If so, that cohort's
  measured lifetime (sum of active days) and D1~D7 area. If not, proceed with Cases 1 and 2 only.

### 2. Data checks — do not start the analysis before these pass

- Confirm D0=1.0, that days 0~7 are all present, and that `retention` is monotonically decreasing (or nearly so).
- If a pattern of retention rising again after D7 is known (re-activation campaigns, etc.), tell the reader up front that
  the assumptions of Cases 1 and 2 break down.

### 3. Code substitution map

| Anchor (cell/identifier) | What | How |
| --- | --- | --- |
| 4.6.1 data cell | path `data/cohort_retention.csv` | the reader's file (keeping the column names `day, retention` is simplest) |
| 4.6.1 settings cell | `DAYS = 365` | the period that defines lifetime (keeping the default 1 year is recommended) |
| ⚠ 4.6.2 (Case 1) | churn-rate estimation window `WHERE day BETWEEN 5 AND 7` | one place in the notebook, `heuristic_query`. When using `sql/compare_methods.sql` separately, change the same window there too |
| 4.6.3.1 (Case 2) | catalog grid: `d1_anchors` (0.15~0.50, step 0.01, 36 points), `b_grid` (−1.00~−0.05, step 0.01, 96 points; b is negative per the book's convention) | if the reader's D1 is outside 0.15~0.50, widen the anchors range. Keep the D1 step at 0.01 (with b as the only shape parameter, a coarse D1 grid's error carries straight into lifetime) |
| 4.6.3.3 (Case 2) | matching points D1/D3/D7 (`catalog_match_query`) | if more observations exist, add D14 etc. as extra SSE terms |
| ⚠ 4.6.4.1 (Case 3) | mature-cohort constants `51.5` (measured lifetime), `1.875` (D1~D7 area) | one place in the notebook, `mature_query`, with the reader's measured values. `sql/compare_methods.sql` has the same constants, so change them too when using that file |

- Leave the `power_curve` function, the SSE matching logic and the comparison table structure as they are.

### 4. Step-by-step

1. Load the reader's retention → show a curve plot and confirm the shape (steep drop, then gentle).
2. Run 4.6.2 (Case 1) → present the estimate along with "what daily survival ratio r was picked up".
3. 4.6.3 (Case 2): 4.6.3.1 build the catalog → confirm the reader's D1 is within the anchors range → run 4.6.3.3 matching → overlay
   the matched curve on the observations in a plot.
4. (If possible) run 4.6.4 (Case 3).
5. Build the triangulation table with the `compare` DataFrame cell of 4.6.5 (pandas — simply gathers the three results) → read it with the
   interpretation frame below.

### 5. Interpreting the results

- If the three values converge, trust that range as the lifetime.
- If they diverge, look at which assumption broke — if only the heuristic is far lower, the tail is heavier than geometric
  (the most common pattern in real app retention, and the result in this chapter's example); if only the heuristic is far higher,
  the early decay is faster than geometric; if only the catalog is off, the retention shape falls outside the power-law family;
  if only Case 3 is off, the quality of past and current cohorts has changed.
- lifetime × ARPDAU (average daily revenue per active user) can be linked to a rough LTV — in this chapter's example,
  at ARPDAU $0.015, 13 days ≈ $0.2 and 52 days ≈ $0.78, so the CAC ceiling differs by nearly a factor of four
  (next action from the book's summary table: feed this LTV into the CAC guideline → chapter 7 unit economics; also compare with the LTV rough estimate in chapter 6 (MRR)).
- Estimation is not a one-off — re-estimate as D30 and D90 measurements accumulate, and use the gap between estimate and measurement
  as input for the next estimate (book 4.8). If the goal is channel/cohort comparison, do not switch methods often; keep accumulating on the same basis.

## Pitfalls

- Because long-term lifetime is estimated from 7 days of observation, the history-based Case 3 rescaling can be off for cohorts
  right after a major product change (onboarding overhaul, etc.). Case 3 needs 1+ year of production data and cannot capture a tail shape
  beyond D7 that has changed from the past.
- Lifetime is "average active days" — do not confuse it with calendar survival time.
- `Σ retention = lifetime` holds only for **classic retention** (share active on exactly day N) (book 4.1) — if the reader's data is
  rolling or unbounded retention, guide them to recompute as classic retention first.
- Consistency of the estimation system matters more than decimal-point accuracy (book 4.8) — changing the basis every quarter breaks channel/cohort
  comparisons. When you switch methods, re-estimate past cohorts retroactively with the same method.
- Case 1 swings widely with tiny errors in r because of `1/(1−r)` (0.98 → 49×, 0.99 → 99×), and it cannot express a heavy tail,
  so it systematically underestimates — use it as a lower bound / baseline.
- For Case 2, the catalog's coverage is the model's limit — if the reader's retention lies outside the grid, picking the nearest row still leaves error.
  If any one of D1, D3 or D7 lands on a weekend or a marketing event, that single day feeds straight into the result, so it is better to
  bundle a week of signups into one cohort rather than a single day's.
- For services like commerce where revenue is unrelated to activity duration, lifetime itself means little (purchase frequency and basket size
  matter more). It is most powerful for ad-based services.
- Never over-trust a single estimate as absolute truth — always cross-check two or more methods with different assumptions.

## Study guide

### Core concepts — what you should be able to explain after this chapter

- **lifetime** — the area under the retention curve (expected number of active days). `Σ retention(d)`. Not a calendar period but the sum of
  active days; in practice summed up to one year (365 days).
- **Geometric-series tail** — folding everything beyond D7 into `d7·r/(1−r)` under the assumption that "a constant share of the remaining users
  (daily survival ratio r = share remaining today relative to yesterday) stays each day". r is a different quantity from retention (the curve height).
- **Power-law retention** — `D_t = D1·t^b` (b < 0; the same convention as `y = a·x^b` in chapter 5). The assumption that the share remaining today
  relative to yesterday, `((t+1)/t)^b`, approaches 1 a little more each day, so the tail is heavier than geometric. The larger |b|, the steeper the drop.
  (sBG and Weibull are two-parameter alternatives; sBG's long tail is also approximated by a power law.)
- **Catalog matching** — instead of fitting a model directly, an approximation that looks up the curve most similar to the observations in a pre-built
  dictionary of curves.
- **Triangulation** — the attitude of crossing estimates with different assumptions to validate not the values but **whether the assumptions hold**.

### Concept check

1. What assumption does each of the three methods (Case 1 heuristic, Case 2 power-law catalog matching, Case 3 mature-cohort rescaling)
   rely on?
   - Hint: Case 1 = the daily survival ratio r is constant beyond D7 (geometric series); Case 2 = retention lies within the power-law curve family;
     Case 3 = the past and current cohorts' curves are similar in shape (the 7-day area ratio equals the 1-year area ratio).
2. Two services have exactly the same D1 retention of 34%, yet their lifetimes can differ by a factor of two. Why?
   - Hint: the tail — even from the same starting point, a different decay speed (curve shape, the power law's b) changes the area a lot.
3. When the three triangulation values diverge, why is "just average them" a bad idea?
   - Hint: divergence is a signal that some assumption broke — averaging erases the signal and mixes in the wrong values. In this chapter's example,
     the answer is to trust the value where Cases 2 and 3 (different assumptions) meet and to doubt Case 1.
4. Between a geometric series (fixed r) and a power law (r converging to 1), which fits real app retention tails better? So in which direction
   does the heuristic get lifetime wrong?
   - Hint: the power law — only the users least prone to churn remain, so the effective churn rate keeps falling (a straight line on log-log axes).
     A fixed r cannot hold this heavy tail, so it underestimates.
5. Catalog matching uses only the three points D1, D3 and D7 rather than all of D1~D7; what does each point measure about the curve?
   - Hint: D1 = depth of the first-day churn cliff, D3 = curvature of the early deceleration, D7 = mid-term stabilization tendency. Keeps the computation
     simple while identifying the shape well enough.
6. For an ad-based service with a lifetime of 50 days and ARPDAU of $0.03, what is the CAC ceiling? What if lifetime doubles?
   - Hint: LTV ≈ lifetime × ARPDAU = $1.5 → CAC must stay below that; at 100 days, $3 (book 4.2). Also explain why this calculation loses its force
     for commerce (revenue depends on purchase frequency and basket size rather than activity duration).

### Advanced exercises

1. **[Sandbox]** In `generate_data.py`'s `COHORT_RETENTION`, nudge the D5~D7 values up slightly to flatten the tail
   (e.g. D7 0.244 → 0.280) and have the reader predict **which estimate moves the most**, in order → edit → re-run → compare.
   (The goal is to discover that Case 1 is sensitive because the geometric r is estimated over days 5~7.) When done, restore with
   `git checkout --` and regenerate.
2. **[Sandbox]** Coarsen the `d1_anchors` step in 4.6.3.1 (Case 2) from `0.01 → 0.05` (36 points → 8) and predict what happens to the match
   → run → compare. (D1=0.341 lands on the 0.35 level and drops to about 49 days — confirms that "catalog coverage determines estimate quality".) Restoring is mandatory.
3. **[Thinking]** For a subscription service, what should be defined as lifetime instead of "active-day lifetime"?
   How does each of the three methods translate in that case? (Discuss with a focus on the relationship to 1/churn in chapter 6 (MRR).)
