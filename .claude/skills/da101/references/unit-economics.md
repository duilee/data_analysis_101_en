# Unit Economics — CAC, LTV (contribution margin), and payback curves

**Chapter folder**: `chapters/07_ROAS_is_220_so_why_are_we_losing_money/` · Notebook: `unit_economics.ipynb`
<!-- synced: code at duilee/data_analysis_101@226e1dd (Korean original) (2026-10-10) — cross-checked against the notebook, README, and sql. Cross-checked against the book's first proofread draft (2026-10-10, section layout: Intro (Table 7.1) → 7.1 Is LTV:CAC 3 good enough? (7.1.1-7.1.2, Figure 7.1) → 7.2 Calculating in practice (7.2.1-7.2.3, Tables 7.2-7.6) → 7.3 Putting it to use (7.3.1-7.3.3, Table 7.7, Figure 7.2) → 7.4 Practice 7.4.1-7.4.6 (Python/SQL, Table 7.8) → 7.5 Practice 7.5.1-7.5.5 (Claude Code) → 7.6 Wrapping up). "Payback Period" rendered as "payback period". -->

## The problem this method solves

Uses three raw logs — marketing costs, acquisitions, and payments — to judge "is our business
actually making money?" It separates revenue (LTR) from value (contribution-margin LTV), computes
CAC on both a media-cost basis and a fully-loaded basis, breaks the result down by channel, and
measures the payback period from cohort-level payback curves. It reproduces in data how the
opening contradiction — "ROAS is 220% but we're losing money" — dissolves the moment the 'units'
of the metrics are aligned.

**Pointers to the book's theory** (details are in the book — only the gist here)

- Intro (Table 7.1) — The marketing lead's calculation: CAC 12,000 KRW, D7 payments 26,400 KRW
  (ROAS 220%), lifetime payments 37,000 KRW → LTV:CAC 3.1. The starting point is the contradiction
  that the numbers aren't wrong, yet the monthly loss keeps growing.
- 7.1 — Three services whose revenue all grows 20% per period (A profitable per user, B losing
  money per user, C a one-off promotion) cannot be told apart on a revenue chart; you have to look at
  per-user profit alongside. Revenue lumps 'scale' and 'efficiency' into one number. → book 7.1 (Figure 7.1)
- 7.1.1 — Unit economics = a model that divides total profit and loss down to the smallest unit of
  sale (the unit). Depending on the business model the unit is a user, an order, a subscriber, etc.
  A unit's economics = the money the unit leaves behind over its lifetime − the money spent to
  acquire it. If (+), today's loss is an up-front investment; if (−), you are piling up future
  losses in advance. → book 7.1.1
- 7.1.2 — Standard guidelines: **LTV ≥ CAC x 3** (around 1x cannot absorb fixed costs or estimation
  error), **CAC payback within 12 months** (startup capital is expensive). VCs use these benchmarks
  too. → book 7.1.2
- 7.2.1 (Tables 7.2, 7.3) — LTR (total revenue) vs LTV (contribution margin after variable costs).
  What should be compared to CAC is LTV. ROAS is a legitimate operating metric for marketers; the
  problem is its 'use' (misapplied to judging business profitability). Four variable-cost items
  (store fee 15%, promotions 10%, payment/CS/refunds 5%, variable infrastructure 5%) total 35% →
  contribution margin ratio 65%. The reason to use contribution margin is the marginal question
  "if we bring in one more user, how much is left?" Table 7.3: 24,050/12,000 = 2.0. → book 7.2.1
- 7.2.2 (Table 7.4) — Four things to decide in a CAC calculation (acquisition definition
  install/signup/first payment · paid/blended · match the CAC used for unit economics to the LTV
  population · cost scope fully-loaded) and two things that make it wobble (attribution window and
  iOS ATT, marginal CAC). Fully-loaded 14,500 KRW → 1.7. → book 7.2.2
- 7.2.3 (Tables 7.5, 7.6) — The channel table (search 2.9 stable / display 1.0 effectively
  negative / retargeting 6.7 suspected last-click overstatement → incrementality analysis /
  brand & other 0.9 is for awareness, so evaluate with separate metrics). The 1.7 average is a
  phantom number that represents no channel (the paid-total contribution-margin LTV of 23,980 KRW
  in Table 7.5 is a user-weighted channel average). Simpson's paradox (Table 7.6: every channel
  improves, but search's share drops from 70% → 31%, so blended goes 2.3 → 1.9). → book 7.2.3
- 7.3 intro — Rather than pouring resources into the 'prediction accuracy' of CAC and LTV,
  complement them with a short-term measurement (payback period). → book 7.3
- 7.3.1 (Table 7.7) — Payback period is not a prediction but an observed value from past cohorts.
  Look at it on a contribution-margin basis, with fully-loaded CAC, by channel x cohort. Within 6
  months is good, within 12 months is acceptable (longer for B2B). For subscriptions, draw the curve
  on revenue recognized over the service period. Five calculation steps and Table 7.7 (search April
  cohort 1,000 users, cost 11.5M KRW, monthly contribution margin 4.2M → 2.7M KRW, payback ratio
  0.37/0.70/1.02/1.30/1.57/1.80 — M+2 = paid back in month 3). Service A (3.0, 18 months) vs B
  (2.0, 6 months): B grows faster — it turns the same budget over twice a year; a profitable company
  can still go bankrupt. → book 7.3.1 (Figure 7.2)
- 7.3.2 — CAC guideline = target payback period (months) x average monthly contribution margin per
  user (e.g. 10 months x 800 KRW = 8,000 KRW). Caution: the denominator of average monthly
  contribution margin is the whole cohort (including churned users), not that month's surviving
  users; when the target changes, the verdict on a channel whose efficiency is unchanged also
  flips. The target payback period is a management decision, not an analysis output. The marketing
  team works in ROAS, so the data team builds the bridge (e.g. target 8 months → CAC 8,000 KRW →
  D7 ROAS of at least 80%; 8-month cumulative payments ≈ 155% of CAC = 1/0.65). → book 7.3.2
- 7.3.3 — "Are we making money?" splits into two questions: are the unit economics (+) / is the
  company profitable (sum of contribution margin > fixed costs). A better question: "which channel,
  in how many months, actually earns us money?" → book 7.3.3
- 7.6 Wrapping up — Question: ROAS is 220% yet we're losing money / Situation: an LTR metric
  misused to judge profitability; after correction 3.1 → 1.7 / Solution: align the units to
  contribution-margin LTV and fully-loaded CAC, break down by channel, and measure payback period /
  Caution: the average LTV:CAC is a phantom number (Simpson's paradox), and payback speed determines
  cash flow and growth speed / Answer: are the units profitable (per-channel contribution-margin LTV
  > fully-loaded CAC, payback curve crosses 1.0 within the target period) → is the company
  profitable (sum of contribution margin > fixed costs). Keep channel x cohort payback curves
  available at all times. (Refining the lifetime estimate itself is Chapter 4 — a pointer not in
  book 7.6)

## Run and verify

```bash
python generate_data.py      # generates data/marketing_costs.csv, users.csv, payments.csv
jupyter nbconvert --to notebook --execute unit_economics.ipynb \
  --output-dir ../../my-work/07_ROAS_is_220_so_why_are_we_losing_money   # output goes to my-work
```

- Input (book Table 7.8): `data/marketing_costs.csv` (month x channel cost, media/other split) ·
  `data/users.csv` (acquisition roster — **includes non-paying users**) · `data/payments.csv`
  (per-payment revenue).
- Flow: setup cell (`CM_RATIO = 0.65`) → 7.4.2 CAC by channel (2025-04 basis, media-cost vs
  fully-loaded; organic drops out naturally in the cost join) → 7.4.3 mature cohort view `mature`
  (acquired 2024-01 to 2024-12 — 12+ months since acquisition, same one-year basis as Chapter 4)
  backtest for LTR → x `CM_RATIO` → contribution-margin LTV + the cascade (divides by the
  `media_cac` and `full_cac` variables from 7.4.2 as-is) → 7.4.4 merge CAC and LTV at the channel
  level (channel table) → 7.4.5 four payback curves via `payback_df(channel, cohort_month,
  max_m=11)` (search and display x 2025-03/04) → 7.4.6 CAC guideline with `TARGET_PAYBACK = 12`.
  7.4.3 and 7.4.5 use `mature` LEFT JOIN `payments` + `COALESCE(…, 0)` to **include non-paying
  users as 0 KRW** — this is the definition of LTV 'per acquired user' and the device that keeps
  the population aligned with the CAC denominator (an INNER JOIN would give the average over
  payers and inflate LTV).
- **Expected results**: the answers planted by the generator (all values from the chapter's tables)
  must be reproduced. Same numbers as the result tables in book 7.4.
  - 7.4.2: 2025-04 paid acquisitions 2,500 users (search 1,000 / brand 750 / display 500 /
    retargeting 250). Media-cost CAC by channel 9,890 / 22,389 / 5,016 / 3,240 KRW → fully-loaded
    **11,500 / 28,000 / 5,700 / 3,600 KRW**. Paid-total CAC: media-cost **12,000 KRW** →
    fully-loaded **14,500 KRW** (+21%).
  - 7.4.3: mature cohort user counts search 1,440 / organic 1,440 / brand 1,080 / retargeting 360 /
    display 720. LTR 50,762 / 39,984 / 36,940 / 36,939 / 9,082 KRW → contribution-margin LTV
    32,995 / 25,989 / 24,011 / 24,010 / 5,903 KRW (book Table 7.5: 33,000 / 26,000 / 24,000 /
    24,000 / 5,900). Paid-total LTR 36,897 KRW → LTV 23,983 KRW (book Tables 7.1 and 7.3: 37,000 →
    24,050; paid total in Table 7.5 is 23,980). Cascade **3.1 → 2.0 → 1.7**.
  - 7.4.4: LTV:CAC brand 0.9 / display 1.0 / retargeting 6.7 / search 2.9 · paid_total 1.7.
  - 7.4.5: 2025-04 search cohort monthly contribution margin 4.2M / 3.9M / 3.6M / 3.3M / 3.0M /
    2.7M KRW, payback ratio 0.37 / 0.70 / **1.02** / 1.30 / 1.57 / 1.80 — breaks even at M+2
    (**month 3**). Four curves: search April M+2, search March M+3 (month 4, `QUALITY=0.93`),
    display April M+11 (barely, in month 12), display March not recovered within the 12-month
    observation window.
  - 7.4.6: average monthly contribution margin per user retargeting 2,001 / search 2,750 / display
    492 / brand 2,001 KRW → guideline (x12) 24,000 / 33,000 / 5,900 / 24,000 KRW, current CAC ÷
    guideline 0.15 / 0.35 / 0.97 / 1.17 — only brand exceeds, display just squeaks by. With
    `TARGET_PAYBACK = 8`, display flips to exceeding.

## Applying to your own data — interactive protocol

Proceed in order 1 → 5. Show the reader the result of each step and confirm before moving on.
Invocations from book 7.5 (Claude Code practice): 7.5.2 run · 7.5.3 apply · 7.5.4 qna · 7.5.5 quiz
— `/da101 run|apply|qna|quiz unit economics` or natural language ("let's go through the unit
economics practice", "I want to see CAC by channel and payback curves on our service's data"). The
notebook's setup paragraph names the "five values to change when applying to your own data"
(`CM_RATIO`, the 7.4.2 reference month, the 7.4.3 cohort window, the 7.4.5 channel and acquisition
month, `TARGET_PAYBACK` in 7.4.6) — the substitution map in step 3 includes that list.

### 1. Intake — what to ask the reader

- **File paths** of the three logs and the column mapping:

| Role (notebook example name) | Type | Meaning | Required |
| --- | --- | --- | --- |
| `marketing_costs`: month, channel, media_cost_krw, other_cost_krw | DATE/TEXT/NUM | month x channel cost | Required* |
| `users`: user_id, channel, signup_date | TEXT/TEXT/DATE | acquisition roster (includes non-paying users) | Required |
| `payments`: user_id, payment_date, amount_krw | TEXT/DATE/NUM | per-payment revenue | Required |

  *If there is no other-cost column (agency, production, etc.), start on a media-cost basis, but
  agree on the list of items to include in fully-loaded and have the reader prepare them as a
  separate row/column.
- **Contribution margin ratio** — agree on the variable-cost items (fees, promotions, payment/CS,
  infrastructure, etc.) and their ratio to revenue, and set `CM_RATIO`. This single value drives
  every LTV and payback curve.
- **The definition of 'acquisition'** — is a row in the acquisition roster an install, a signup, or
  a first payment? Check that the CAC denominator and the LTV population use the same definition
  (the unit alignment in book 7.2.2).
- Channel naming — do the cost table and the acquisition table use the same channel scheme? How is
  organic defined?
- **Data period** — set the LTV measurement horizon. If a full year is not available, state a
  shorter horizon explicitly (e.g. 6-month cumulative) before starting (never compare LTVs with
  different horizons).

### 2. Data check — do not start the analysis until this passes

```python
con.execute("""SELECT (SELECT COUNT(*) FROM read_csv_auto('USERS')) AS users,
    (SELECT COUNT(DISTINCT user_id) FROM read_csv_auto('PAYMENTS')) AS payers,
    (SELECT MIN(signup_date) FROM read_csv_auto('USERS')) AS first_signup,
    (SELECT SUM(CASE WHEN amount_krw <= 0 THEN 1 ELSE 0 END)
       FROM read_csv_auto('PAYMENTS')) AS nonpos_rows""").df()   # reuses the notebook's con
```

- Pass criteria: `payers < users` (a roster containing only payers distorts both the CAC
  denominator and per-user LTV — first obtain an acquisition source that includes non-paying
  users), channel lists match between the cost and acquisition tables, a rule is agreed for
  negative/zero rows (refunds), and cohorts old enough to fill the LTV horizon exist.

### 3. Code substitution map

| Anchor (practice section / identifier) | What | How |
| --- | --- | --- |
| Setup cell (second code cell) | the `read_csv_auto('data/{t}.csv')` loop, `CM_RATIO = 0.65` | Point at the reader's data and the agreed contribution margin ratio. `CM_RATIO` is shared via f-strings by the queries in 7.4.3-7.4.5, so this one place is the only change |
| 7.4.2 `cac` and `apr` queries | reference month `DATE '2025-04-01'` (3 places: users filter, costs filter, `apr`) | The reader's most recent 'completed' month. The cascade, 7.4.4, and 7.4.5 use the resulting `cac`, `media_cac`, `full_cac` as variables, so no further edits |
| 7.4.3 `mature` view (`CREATE OR REPLACE VIEW`) | `BETWEEN DATE '2024-01-01' AND DATE '2024-12-31'` | The cohort window that fills the reader's LTV horizon — one edit, and 7.4.6 reuses this view too |
| 7.4.3 LTV query | `INTERVAL 12 MONTH` | Change together with the LTV horizon (also `INTERVAL 12 MONTH` and `/ 12.0` in 7.4.6 if the horizon is the same) |
| 7.4.5 `payback_df("search", "2025-04")` call and the `styles` list | channel and cohort-month combinations (`max_m=11` is the number of observed months) | The channel x cohort combinations to compare |
| 7.4.6 | `TARGET_PAYBACK = 12` | The target payback period (months) agreed with management — show how the verdict changes under several values |

- The four `sql/*.sql` files (`cac_by_channel`, `mature_cohort`, `ltv_backtest`, `payback_curve`)
  are reference copies — the substitution targets are the notebook's inline queries. The copies
  have 0.65 hardcoded as a literal, and `ltv_backtest.sql` requires the view from
  `mature_cohort.sql` to be run first.

### 4. Step-by-step progression

1. CAC by channel → sanity-check against the attribution tool's channel report (confirm the
   media-cost vs fully-loaded gap).
2. Mature cohort LTV → present per-channel values, reproduce the cascade (revenue basis vs
   contribution-margin basis).
3. Complete the channel table → point out the gap between the average ratio and the per-channel ratios.
4. Payback curves → compare payback periods by cohort. Also confirm that recent cohorts' curves are
   'short, not low'.
5. CAC guideline → explain that the target payback period is a management decision rather than an
   analysis output, and show how the verdict flips under several target values.

### 5. Interpreting results

- Standard guidelines: contribution-margin LTV:CAC of **3:1 or more**, CAC payback **within 12
  months** (room to absorb fixed costs and estimation error). Around 1:1 is effectively negative
  once fixed costs are considered. Payback within 6 months is good, within 12 months acceptable
  (B2B with low churn is sometimes allowed longer).
- "Are we making money?" is answered on two levels — are the units (+) (per-channel
  contribution-margin LTV > fully-loaded CAC, payback curve crosses 1.0 within the target months),
  and is the company profitable (sum of contribution margin > fixed costs). If units are profitable
  but the company is losing money, it can be explained as a planned up-front investment ("recovered
  along this curve in N months"); if the units themselves lose money, fix margin and retention
  before increasing the marketing budget (book 7.3.3, 7.6).
- Extreme efficiency in retargeting-type channels (e.g. 6.7) should raise suspicion of last-click
  attribution overstatement; recommend an incrementality analysis. Channels like brand/other, whose
  purpose is awareness, should not be cut on unit economics alone but evaluated together with
  separate metrics suited to the campaign's purpose (book 7.2.3).
- Blended CAC answers the "company-wide average" question; paid CAC answers "should we spend more
  on this channel". Match the question to the kind of CAC, and match the kind of CAC to the LTV
  population (all users / paid users) — that is the key.
- Next actions (book 7.6): set a CAC guideline as target payback period x average monthly
  contribution margin, and keep channel x cohort payback curves available at all times. To refine
  the lifetime estimate, see Chapter 4 (lifetime).

## Pitfalls

- If the CAC denominator (acquisition definition) and the LTV population differ, the ratio is
  meaningless as a whole — unit alignment is this chapter's first principle.
- Many organizations have only a payment log and no acquisition roster — computing on payers makes
  CAC larger and per-user LTV larger too, so the ratio may coincidentally look similar, but the
  absolute level of the payback curve is distorted. For the same reason, the LTV and average
  monthly contribution margin queries must use LEFT JOIN + COALESCE to include non-paying users as
  0 KRW (an INNER JOIN gives the average over payers).
- The denominator of average monthly contribution margin (7.4.6) is the whole cohort (including
  churned users), not that month's surviving users (book 7.3.2).
- In 7.4.6 the average monthly contribution margin is measured on 2024 cohorts while CAC is the
  2025-04 value — check that payment patterns did not change in between.
- If prepaid fixed-term plans (annual passes, etc.) are mixed in, draw the curve on revenue
  recognized over the service period rather than cash at payment time (book 7.3.1).
- If the LTV measurement horizon (e.g. a 12-month cap) is not stated explicitly, you end up
  comparing numbers with different horizons.
- ROAS itself is not a bad metric — the problem is using a campaign operating metric as-is to judge
  business profitability. Rather than demanding that the marketing team operate on contribution
  margin, the data team builds the bridge between contribution-margin LTV, LTR, and ROAS (e.g.
  target payback 8 months → CAC guideline 8,000 KRW → required D7 ROAS 80%) (book 7.3.2).
- CAC is not a 'fixed value' — it wobbles with the attribution window, estimated aggregates after
  iOS ATT, and marginal CAC that rises as budget grows. Keep a buffer and watch the trend on a
  consistent basis (book 7.2.2).
- Looking only at the blended ratio gets you caught by Simpson's paradox — every channel improves,
  yet if the share of the efficient channel shrinks, the total looks worse (book Table 7.6). Search's
  share is prone to seasonal swings. That is why you manage at the channel level.
- When the target payback period changes, the verdict on a channel whose efficiency is unchanged
  flips too — the target is a management decision, and the data team brings the decision inputs
  (cash runway, LTV improvement outlook, etc.) (book 7.3.2).
- Even with profitable units, slow payback can bankrupt a profitable company — the reason to look at
  payback period before LTV:CAC (book 7.3.1, 7.6).

## Study guide

### Core concepts — what you should be able to explain after this chapter

- **LTR vs contribution-margin LTV** — the distinction between total revenue and the money actually
  left after variable costs. The one to compare with CAC is LTV. ROAS is only a marketing
  operating metric on a revenue (LTR) basis, not a metric for judging business profitability.
- **Fully-loaded CAC** — acquisition cost with agency fees, production costs, and so on added on top
  of media cost. The basis for managing net profit and for unit economics calculations.
- **Channel breakdown** — the average (paid total 1.7) is a phantom number that represents no channel.
- **Payback curve and payback period** — not a prediction but a measurement on past cohorts. The
  point where cumulative contribution margin ÷ total CAC crosses 1.0.
- **CAC guideline = target payback period x average monthly contribution margin per user** —
  marketing budget setting that also accounts for cash flow. When the target changes, the channel
  verdict flips too.

### Concept check

1. D7 ROAS is 220%, yet the company's losses are growing. If the metric isn't wrong, how is this
   possible?
   - Hint: ROAS is on a revenue (LTR) basis — subtract variable costs (contribution margin), widen
     the cost to fully-loaded, and account for the payback lag (cash goes out today, contribution
     margin comes in over several months), and the picture changes.
2. The chapter called the paid-total LTV:CAC of 1.7 a 'phantom number'. Why? Separate the decisions
   this number can support from those it cannot.
   - Hint: broken down by channel it is 2.9 / 1.0 / 6.7 / 0.9 — the average represents none of the
     four stories. It can be used for the company-wide average acquisition cost and the overall
     budget size, but it gives no information for channel-level scale-up/stop decisions (also note
     the population difference between blended and paid).
3. A service with LTV:CAC 3.0 and an 18-month payback period vs one with 2.0 and 6 months — which
   can grow faster, and why?
   - Hint: how fast the same budget turns over. With faster payback, the same money is turned over
     twice a year — even with profitable units, slow payback can bankrupt a profitable company.
4. What is the difference between the marketing lead's CAC of 12,000 KRW and the 14,500 KRW CAC used
   for unit economics? Which should be used for channel performance comparison and which for business
   planning?
   - Hint: media-cost basis vs fully-loaded (agency fees, creative production, and in some cases
     headcount). Channel comparison uses the media-cost basis; net profit management and unit
     economics use fully-loaded. On top of that, the acquisition definition (install/signup/first
     payment) and paid/blended must be aligned with the LTV population and units.
5. If the target payback period is 8 months and average monthly contribution margin per user is
   1,000 KRW, what is the CAC guideline? If the target changes to 12 months, what happens to the
   verdict on the same channel?
   - Hint: CAC guideline = target payback period (months) x average monthly contribution margin per
     user = 8,000 KRW. A longer target raises the guideline, so a channel that was failing can pass
     — the channel's efficiency is unchanged but the verdict flips. The target payback period is a
     management decision, not an analysis output. The denominator of average monthly contribution
     margin must be the whole cohort (including churned users).

### Advanced exercises

1. **[Sandbox]** Have the reader predict how the display ratio in 7.4.4 and the guideline verdict in
   7.4.6 change if `"display": 5700 → 4500` in `CAC_TARGET` in `generate_data.py` → edit →
   `python generate_data.py` → re-run the notebook → compare. When done, restore with
   `git checkout -- generate_data.py data/` and regenerate.
2. **[Sandbox]** Predict how the order of the March/April curves in 7.4.5 changes and what each
   payback period becomes if the 2025-03 multiplier in `QUALITY` is changed `0.93 → 1.05` → run →
   compare. Internalize "how a change in cohort quality shows up in the payback curve". Restoring
   afterwards is mandatory.
3. **[Thinking]** Redoing this chapter's calculations with a blended CAC that puts organic
   acquisitions in the denominator makes the ratio look better. Why, and which question must not be
   answered with that number? (Focus on how users who arrived without ad spend pull up the average,
   and on the population behind the question "is the money we spend on marketing a profitable
   trade?" — no single right answer)
