# Subscription growth metrics — six-component MRR decomposition and GRR/NRR

**Chapter folder**: `chapters/06_checking_growth_metrics_of_a_subscription_service/` · notebook: `mrr_analysis.ipynb`
<!-- synced: code at duilee/data_analysis_101@226e1dd (Korean original) (2026-10-10) — cross-checked against the notebook, README and sql; book text: cross-checked against the first proofread draft (2026-10-10; section layout: intro → 6.1 Subscribers (6.1.1 drivers, 6.1.2 framework: 6.1.2.1 Flow, 6.1.2.2 Stock) → 6.2 Subscription revenue (6.2.1–6.2.3, 6.2.4 in practice 6.2.4.1–6.2.4.7) → 6.3 Practice 6.3.1–6.3.6 (Python/SQL) → 6.4 Practice 6.4.1–6.4.5 (Claude Code) → 6.5 Wrapping up). Notebook-only code sections: 3 `[Notebook extra]` blocks (6.3.3, 6.3.4, 6.3.5). -->

## The problem this method solves

Diagnose the health of a subscription business using nothing but a store payment log with no user ID
(shaped like a Google Play Sales Report). Identify users by parsing `order_number`, decompose monthly
MRR into the six components **new / renew / reactivation / expansion / contraction / churn**, and
summarize it as GRR (defense) and NRR (growth). You can then tell whether "MRR is growing" thanks to
new acquisition or thanks to defending existing revenue.

**Pointers to the book's theory sections** (in QnA mode, give the gist and point to the relevant section of the book for details):
- Intro — A subscription is an LTV-driven business, so retention and MRR/ARR are what matter. Metrics are viewed on
  two axes, subscribers (Subscriber) and revenue (Sales), **independently**. Three reasons: some events affect only one
  axis (trial start, declined renewal, etc.), revenue lags subscribers, and there are cases where the subscriber count
  stays flat but only revenue moves (price changes, up/downgrades). This is why you must not measure experiment impact
  by payment counts or revenue alone.
- 6.1 — On the subscriber axis the key is not Stock (number of subscribers) but Flow (net change in paid subscribers).
  Trials are not mixed with paid (a drop in trials is a neutral metric: positive if it is conversion, negative if it is
  expiry). From here on the term is 'paid subscriber'.
  - 6.1.1 — Only two variables move the net change in paid subscribers: growth in new paid subscribers and churn of
    existing paid subscribers. Churn is viewed as subscription retention rather than the number of cancellations.
  - 6.1.2 (Figure 6.1) — The subscriber analysis framework. 6.1.2.1 Flow: users A–E (A net change in paid subscribers
    = B new − C cancellations, D new trials, E new sign-ups) + conversion rates 1–5 (I2P, I2T, T2P, existing-user
    conversion, subscription cancellation). 6.1.2.2 Stock: F existing non-subscribed users, G currently subscribed users.
    Look at the daily net change in paid subscribers first, then raise the resolution with subscription retention by sign-up cohort.
- 6.2.1–6.2.3 — Limits of simply summing payment amounts (future revenue recognized up front, deferred revenue) and of
  prorating over the period (prorated recognized revenue, not enough resolution for root-cause analysis) →
  MRR = Baseline + new + reactivation + expansion − contraction − churn; the sum of the last five terms is
  Net New MRR. Previous month − churn = renew. churn rate = 1 − renew ÷ previous month. MRR is used as a growth
  metric, for forecasting, and for valuation.
- 6.2.4 — Seven practical issues when building MRR from store reports: user identification (order-number prefix and
  row_number in Figure 6.2; Apple only provides aggregates and records trials as a first payment → load user-level data
  yourself via server notifications (RTDN etc.) or a subscription management tool) and gross/net (6.2.4.1); cancellation is
  a passive event, so churn = previous month − renew is backed out, but with multiple plans previous month − renew =
  churn + contraction − expansion, so up/downgrades are separated (6.2.4.2); renew/reactivation uses a payment-interval
  threshold (32 days, Figure 6.3) plus the grace period, and a large reactivation share distorts the new-MRR funnel reading
  (6.2.4.3); annual subscriptions are prorated monthly + retained MRR (included in Baseline) (6.2.4.4); refunds are an active
  event, finalize in early M+1, involuntary churn, dunning (6.2.4.5); GRR/NRR definitions, Baseline and gap interpretation
  (6.2.4.6); the subscriber-count decomposition has no expansion/contraction (6.2.4.7).
- 6.3 Practice (Python/SQL) — 6.3.1 data preparation (Table 6.1 payment log table) → 6.3.2 user identification → 6.3.3
  renew/reactivation → 6.3.4 MRR decomposition → 6.3.5 GRR/NRR → 6.3.6 churn rate and LTV. Code and numbers are the same
  as the notebook (for the 3 notebook-only `[Notebook extra]` cells, see the expected results below).
- 6.4 Practice (Claude Code) — 6.4.1 get the repository → 6.4.2 run · 6.4.3 apply · 6.4.4 qna · 6.4.5 quiz, with
  natural-language / `/da101 … MRR` examples. The 4 intake questions in 6.4.3
  (columns, order-number scheme, billing cycle, amounts and exception rows) and the data checks are the same as the protocol below.
- 6.5 Wrapping up — daily net change in paid subscribers, whether monthly Net New MRR is positive (new > churn), the
  quarterly GRR/NRR gap. LTV ≈ ARPU ÷ monthly churn rate (5% → ≈ 20 months) → comparison with CAC and payback period is chapter 7.

## Running and verifying

```bash
python generate_data.py      # creates data/subscription_sales.csv
jupyter nbconvert --to notebook --execute mrr_analysis.ipynb \
  --output-dir ../../my-work/06_checking_growth_metrics_of_a_subscription_service   # results go to my-work
```

- Input: `data/subscription_sales.csv` (`order_number, order_charged_date, product_id,
  sales_amount_krw`).
- Flow: 6.3.2 `split_part(order_number, '..', 1) AS pid` + `row_number()` payment number →
  6.3.3 `lag()` interval + `pay_type` (new/renew/reactivation, 32-day threshold) + [Notebook extra] payment-interval distribution →
  6.3.4 FULL OUTER JOIN with the previous month for the six-component decomposition (`mrr` df) + [Notebook extra] identity
  check (`check`) → 6.3.5 `grr`/`nrr` + [Notebook extra] the same decomposition in subscriber counts
  (`sql/subscriber_counts.sql` — the only SQL read from disk) → 6.3.6 churn-rate recovery and LTV approximation.
  The notebook's inline queries form the **view chain** `orders → classified → monthly → paired`, while
  `sql/mrr_breakdown.sql` is a standalone copy of the same logic as **four CTE layers**
  `payments → classified → paired → SELECT` (in QnA, the "four layers" explanation refers to this file).
- The practice table's `renew` is the "amount kept as is": the renew MRR from 6.2.3 (previous month − churn) with
  contraction subtracted as well (`least(amt, prev_amt)`). Since the downgraded portion is already removed, the result
  table satisfies MRR = renew + new + reactivation + expansion exactly; to match the formula in 6.2.3, add contraction
  back onto renew (book 6.3.4).
- **Expected results**: the answer planted by the generator is a **5% monthly churn rate** (`CHURN_RATE=0.05`). In 6.3.6
  the churn rate over the `stable = mrr[mrr.month >= "2025-04"]` period converges near 5% and connects to
  `LTV ≈ ARPU ÷ churn rate`. Plans are monthly_basic 4,900 KRW / monthly_plus 9,900 KRW —
  expansion/contraction come from up/downgrades at renewal. The 6.3.5 [Notebook extra] confirms that up/downgrades change
  revenue but not the subscriber count.
  Numbers identical to the book's practice sections (for cross-checking): 1,653 users / 10,653 payments (18 months,
  2025-01-01 to 2026-06-28, up to 18 payments; payment-count distribution 198 users with 1 payment … 25 users with 18 —
  the result table in book 6.3.2) · pay_type renew 8,961 / new 1,653 / reactivation 39 ·
  last month 2026-06 MRR 7,608,900 KRW (baseline 7,136,700 · new 811,700 · reactivation 49,300 · renew
  6,707,900 · expansion 40,000 · contraction 25,000 · churn 403,800) · **GRR mean 94.4% / NRR mean 95.2% /
  gap +0.73%p** · recovered churn rate **5.2%** → expected lifetime 19.2 months, ARPU 6,237 KRW, LTV approx. 120,030 KRW
  (at 4.2% churn: 23.8 months, about 148,500 KRW, +24%).
  Notebook-only output (the 3 `[Notebook extra]` blocks, not in the book): 6.3.3 payment intervals renew 28–31 days (median 31) /
  reactivation 44–396 days (median 160) · 6.3.4 max identity error 0 KRW · 6.3.5 subscribers in 2026-06: 1,211
  (new 133 · reactivation 7 · churned 62), subscriber-count identity error 0.

## Applying to your data — interactive protocol

Proceed in order 1→5 below. Show the reader the result of each step and confirm before moving on.
The notebook has 2 `[Applying to your data]` notes, but ⚠ the fact that the 32-day threshold also lives separately in
`sql/subscriber_counts.sql` is not in those notes — the table below is the reference.

### 1. Intake — what to ask the reader

- What is the **file path** of the payment log?

| Role (notebook example name) | Type | Meaning | Required |
| --- | --- | --- | --- |
| `order_number` | TEXT | Order number (source for user identification) | Required* |
| `order_charged_date` | DATE | Payment date | Required |
| `product_id` | TEXT | Plan identifier | Required |
| `sales_amount_krw` | NUMERIC | Payment amount | Required |

  *If a user ID column already exists, skip 6.3.2 (order-number parsing) and use that column as `pid`.
- What is the order-number scheme? — A `base order number..renewal number` structure like Google's, or a different rule?
  (Ask for 5–10 samples and settle the parsing rule together.)
- What is the **billing cycle**? Monthly only, or are annual subscriptions mixed in? (renew thresholds would need to be split)
- Are amounts gross (before store fees) or net? How do refunds appear in the log?
  (Negative rows? A separate file?)
- Do free trials appear in the log as 0-amount rows? Should they be excluded from the decomposition?
- What period does the data cover? — **At least 6 months** recommended to judge a stable period.

### 2. Data checks — do not start the analysis until these pass

```python
duckdb.query("""SELECT COUNT(*) AS rows, MIN(order_charged_date) AS min_d,
    MAX(order_charged_date) AS max_d, COUNT(DISTINCT product_id) AS plans,
    SUM(CASE WHEN sales_amount_krw <= 0 THEN 1 ELSE 0 END) AS nonpos_rows
    FROM read_csv_auto('YOUR_CSV_PATH')""").to_df()
```

- Pass criteria: period ≥ 6 months; if `nonpos_rows` (refund/free rows) exist, agree on a handling rule first;
  the number of plans matches the intake answer. If a parsing rule was settled, apply it to the samples and confirm
  with the reader that pid and payment number come out correctly.

### 3. Code substitution map

| Anchor (practice / identifier) | What | How |
| --- | --- | --- |
| Load cell `CREATE TABLE sales AS …` | CSV path, column names | Point to the reader's data — keep the table name `sales` (every later SQL and `sql/*.sql` references it) |
| 6.3.2 `orders` view cell | Delimiter and parsing rule in `split_part(order_number, '..', 1)` | Match the reader's order-number scheme (skip this practice if a user ID exists) |
| ⚠ renew threshold | `date_diff('day', prev_date, order_charged_date) < 32` — in the notebook it is in **one place, the 6.3.3 `classified` view** (6.3.4–6.3.6 reuse that view), and once more separately in **`sql/subscriber_counts.sql`**, which the 6.3.5 [Notebook extra] reads | 32 days for monthly subscriptions. If annual subscriptions are mixed in, split by plan cycle + grace period and edit **both places together** (also worth aligning the reference copies `sql/classify_payment.sql` and `sql/mrr_breakdown.sql`) |
| 6.3.4 `paired` view cell | `INTERVAL 1 MONTH` in 2 places (coalesce and JOIN condition) | Change together if a weekly decomposition is needed |
| 6.3.5 [Notebook extra] (subscriber-count decomposition) | `open("sql/subscriber_counts.sql")` — the only SQL read from disk | This file is actually executed, so edit it directly |
| 6.3.6 | Stable-period cut `mrr[mrr.month >= "2025-04"]` | Set to a point that excludes the reader's early growth distortion |

- Leave the FULL OUTER JOIN structure of the six-component decomposition and the identity-check cell (`check`) as they are —
  if the identity breaks after substitution, the classification rule is wrong (use it as a debugging signal).
- The `stayed` (paid in both months) and `delta` (this month − previous month amount) columns of the `paired` view are
  the core of the six components: renew = `least(amt, prev_amt)`, expansion = `greatest(delta, 0)`,
  contraction = `greatest(-delta, 0)`. Keep these column names even if you change the cycle.

### 4. Step-by-step procedure

1. (If needed) run the parsing → present the number of pids and the payment-number distribution → check the
   payment-interval distribution with the `gap` cell in the 6.3.3 [Notebook extra] (for monthly subscriptions it should
   cluster at 28–31 days — confirm the validity of the threshold with the reader here). ⚠ In 6.3.5 the same name `gap`
   is redefined as the NRR−GRR gap, so re-run the 6.3.3 cell if you want to see the interval distribution again later.
2. `pay_type` classification → present the new/renew/reactivation shares and compare against common sense.
3. Six-component decomposition → **confirm the identity check passes** → present the monthly stacked chart.
4. Compute GRR/NRR → trend chart.
5. Subscriber-count decomposition → compare against the revenue decomposition (separate the up/downgrade effect).
6. Stable-period churn rate → LTV approximation → interpretation.

### 5. Interpreting the results

- GRR is defense reflecting only churn + contraction (capped at 100%); NRR is growth that adds expansion.
  **A large NRR−GRR gap means upgrades by a few users are driving growth** — if defense (GRR) is poor, that growth is fragile.
- In the monthly six-component stack, compare the months when the churn bar grows against events (price changes, campaigns).
- If reactivation is large, re-examine the definition of "churn" (temporary non-payment vs. true churn).
- Conversely, **if GRR is high but the gap is nearly zero**, churn defense is excellent but there is no upselling structure —
  the example data is this case (gap +0.73%p). Use it as grounds for deciding whether it is time to grow revenue per
  customer through plan tiers and add-ons (book 6.2.4.6).
- Operating rhythm (book 6.5): daily net change in paid subscribers, monthly whether Net New MRR is positive (new > churn),
  quarterly the GRR/NRR gap to see the balance between defense and upselling. The fork in the road is "is it time to work
  on churn defense (GRR) or on revenue per customer (NRR)?"
- Read the revenue decomposition side by side with the subscriber axis (net change in paid subscribers, subscription
  retention by sign-up cohort) — revenue lags subscribers, and some events such as trials and declined renewals register on
  only one axis (book intro, 6.1).
- Carry the recovered churn rate into the LTV approximation (ARPU ÷ churn) and compare with CAC and payback period (book 6.5 → chapter 7).

## Pitfalls

- How refunds and partial refunds are represented in the log differs by store — fix the cleaning rule before decomposing.
  A refund is an active event that reverses a past payment, so numbers shift retroactively; it is better to finalize
  month M's MRR in early M+1 (book 6.2.4.5).
- If you don't decide up front whether amounts are gross (before fees) or net, the numbers will later disagree with other
  data (book 6.2.4.1). This chapter uses gross.
- A payment that succeeds late after a store retry following a failed payment (grace period) can exceed 32 days and be
  caught as reactivation — give the threshold some slack or check the distribution (book 6.2.4.3).
- **Involuntary churn** from card expiry or payment errors gets mixed into churn MRR — it does not appear as a
  'cancellation' in the behavior log. Unless you track payment failures separately (dunning management), you cannot tell a
  product-appeal problem from a billing defect (book 6.2.4.5).
- Backing out `churn = previous month − renew` is exact only when there is effectively one plan — with multiple plans,
  previous month − renew = churn + contraction − expansion, so separate up/downgrades as this notebook does (book 6.2.4.2).
- Apple's store reports are aggregates, not user-level, and trials are recorded as a first payment — store reports alone
  have limits, so the proper approach is to accumulate user-level subscription data yourself via server notifications
  (RTDN, App Store Server Notifications) or a subscription management tool (book 6.2.4.1).
- Mixing reactivation into new inflates the install/sign-up → new MRR funnel conversion rate (book 6.2.4.3).
- Don't judge the impact of experiments and improvements from the revenue axis alone — trial starts and declined renewals
  register only on the subscriber axis, post-trial payments and renew only on the revenue axis, and revenue lags (book intro).
  Use subscription retention by sign-up cohort instead of overall retention to remove the illusion created by long-time
  loyal customers (book 6.1.2.2).
- The Baseline for GRR/NRR is existing-customer revenue excluding this month's new revenue — including new inflates
  retention (book 6.2.4.6). Benchmarks like 80–90% annually are rough figures that vary by industry and product structure.
- If annual subscriptions are mixed in, you need a retained MRR term for subscriptions maintained without a payment —
  this notebook's decomposition is for monthly subscriptions only (book 6.2.4.4).
- MRR decomposition compares monthly snapshots, so a sign-up and churn within the same month cancel out and go unseen.
  Look at short-cycle problems at weekly granularity.
- `LTV ≈ ARPU ÷ churn` is an approximation that assumes a constant churn rate — if churn varies by cohort, correct it
  with the methods of chapter 4 (lifetime).

## Study guide

### Core concepts — what you should be able to explain after this chapter

- **Six-component MRR decomposition** — this month's MRR = previous month + new + reactivation + expansion − contraction −
  churn (renew is the retained portion). Accounting that reveals the "source" of growth.
- **GRR vs NRR** — Gross Retention Rate (defense reflecting only churn and contraction, ≤100%) vs
  Net Revenue Retention (growth including expansion, can exceed 100%). The gap between them tells the quality of growth.
- **Subscriber axis vs revenue axis** — the net change in paid subscribers (Flow, = new − churn) and MRR are viewed
  independently. Some events register on only one axis (trials, declined renewals, up/downgrades) and revenue lags.
  The subscriber-count decomposition has no expansion/contraction terms.
- **Distinguishing renew from reactivation** — splitting "continued subscriptions" from "returned subscriptions" with a
  payment-interval threshold. Threshold = billing cycle + grace period.
- **Identity check** — the habit of confirming that the decomposition sums to the actual MRR change. If the accounting
  doesn't balance, the classification is wrong.
- **ARPU ÷ churn LTV approximation** — the geometric-series result that expected subscription months = 1/churn if the churn rate is constant.

### Concept check

1. What state is a service in with NRR 115% but GRR 80%? What should you check first?
   - Hint: upgrades by a few heavy customers are masking heavy churn — check expansion concentration (dependence on top
     customers) and the causes of churn first.
2. Why distinguish reactivation from new? What illusion arises if you don't?
   - Hint: an acquisition-efficiency illusion — counting returning users as new inflates marketing performance and
     hides the churn problem.
3. If expansion stays at 0 in the MRR decomposition but revenue is growing, what is the source of growth and what is the risk?
   - Hint: complete dependence on new inflow — growth stalls immediately once inflow drops. Also check for the absence of upsell room.
4. You finished the six-component decomposition but the identity (MRR = Baseline + new + reactivation + expansion − contraction − churn)
   has a non-zero error. What should you suspect? And what error arises if you apply the same formula to 'subscriber counts'?
   - Hint: the classification rules (pay_type, 32-day threshold, user × month aggregation) are off — if the accounting
     doesn't balance, the classification is wrong. The subscriber-count formula must have no expansion/contraction terms;
     applying the revenue formula as is would count an upgrade as a subscriber increase.
5. For a service with 5% monthly churn and 6,000 KRW ARPU, what are the expected subscription lifetime and the approximate LTV?
   How much does LTV change if churn drops by 1%p? What is the premise of this approximation?
   - Hint: 1/0.05 = 20 months, LTV ≈ 6,000 × 20 = 120,000 KRW. At 4%: 25 months, 150,000 KRW (about a 25% increase).
     The premise is that churn is constant every month (geometric series) — if it varies by cohort, correct with the methods of chapter 4 (lifetime).
6. Trial subscribers fell compared with last month. Is that a good or a bad sign? Which axis — subscribers or revenue — does this event register on?
   - Hint: neutral by itself — positive if the drop came from paid conversion, negative if from expiry (book 6.1). A trial start
     registers only on the subscriber axis and the conversion payment only on the revenue axis, so the two axes must be viewed independently (book intro).

### Advanced exercises

1. **[Sandbox]** Have the reader predict how the recovered churn rate in 6.3.6, LTV, and NRR each change when
   `CHURN_RATE = 0.05 → 0.08` in `generate_data.py` → edit → `python generate_data.py` → re-run the notebook → compare.
   When done, restore with `git checkout -- generate_data.py data/` and regenerate.
2. **[Sandbox]** Predict which of the six components disappears and what happens to the NRR−GRR gap when
   `P_UPGRADE = 0.015 → 0` (upgrades vanish) → run → compare. Internalize "where expansion sits in the accounting". Restoring is mandatory.
3. **[Thinking]** If you launch a new annual subscription plan, where does this decomposition break? (Discuss a design
   around the monthly normalization (MRR-ization) rule, the renew threshold, and the timing of the churn decision — no single right answer)
