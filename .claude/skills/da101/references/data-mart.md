# Building data mart layers — raw → staging → dim/fact → mart

**Chapter folder**: `chapters/11_my_query_has_been_running_for_30_minutes/` · notebook: `data_mart_layers.ipynb`
<!-- synced: code at duilee/data_analysis_101@8e8b97c (Korean original, 2026-09-13) — cross-checked against the notebook, README and sql. Book text cross-checked (2026-09-26; manuscript section layout: section 1 intro → section 2 where data sits (2.1–2.3) → section 3 data has layers (3.1–3.4) → section 4 what designing a mart means (4.1, 4.2.1–4.2.5, 4.3) → section 5 operational notes (5.1–5.4) → practice 0–6 → Claude Code practice → wrap-up). -->

## The problem this method solves

Slow queries, data that is not in the DW, and numbers that differ by team are not a matter of query skill but of
**where the data sits**. This chapter builds four layers on synthetic data from a fictional subscription app (five sources)
and answers the same question ("daily active subscribers and revenue") from raw and from a mart, so the reader feels the difference.

- 11.6.2 raw: join four CSVs (all but events) in one 47-line query — a structure where definitions are scattered through the query, so every person gets a different number
- 11.6.3 staging: 1:1 views over the sources — clean up only names, types, duplicates and system events; business logic forbidden
- 11.6.4 dim/fact: user daily-snapshot and SKU dimensions + a transaction fact (subscription events) + a snapshot fact (daily active subscriptions)
- 11.6.5 mart: a `run_partition()` batch that fills one partition (date) at a time, 90-day backfill, the same question in 3 lines
- 11.6.6 idempotency and the unique-key test; 11.6.7 late-arriving events and a 4-day reload window

**Pointers to the book's theory** (the full explanation is in the book — only the gist here)

- Intro (11.1) — three scenes: a query that has been running for 30 minutes / "the refund data isn't in the analytics DB yet" / a meeting where
  marketing (gross) and finance (net) report different revenue. What the three share is not query skill but a problem of data architecture and
  governance, and "which question is this table for" must be answered by the business side. See book section 11.1.
- Why you must not run analytics queries against the production DB — the structural difference between row storage (transactions) and
  column storage (aggregation), and the two risks: service load and slow reads. See book section 11.2.1.
- DW vs Data Lake — the core difference is "do you tidy up on the way in, or on the way out". More important than the terms is the essence
  that the Raw layer and the Mart/Warehouse layer are separated (the Lakehouse blurs the boundary). A neglected lake is a Data Swamp. See book section 11.2.2.
- Data flow — source → ingestion → storage → transformation → marts and consumption, with an orchestrator managing the order. "Data that is not
  in the DW" is data blocked at the ingestion step, and which sources to connect first is up to the analyst and the business. See book section 11.2.3 and figure 11.1.
- The four layers — src (= raw, immutable, date-partitioned: the only point you can roll back to when a bug in a later layer is found months
  later, so it is never touched, 11.3.1) / staging (1:1 with src, names, types, duplicates and noise only, usually views, 11.3.2) / dim (describes) and
  fact (measures, keys only — attributes are not attached to facts because of storage waste and consistency when a label changes, 11.3.3) /
  mart (joins and aggregations per question; fast and cheap at the cost of fixing the question, 11.3.4). Some teams add an int_ layer. See book section 11.3, figure 11.2 and table 11.1.
- additive / semi-additive / non-additive — payment amounts and counts / subscriber counts, DAU and balances (point-in-time state) / conversion
  rates and average prices. See book section 11.3.3.
- Three design premises (the coverage-vs-performance trade-off, storage is cheap and people are expensive, growing use by non-data roles) and
  four conditions for a good mart (a clear subject, sliceable by several dimensions, no overlap with other marts, consistent and stable). See book section 11.4.1.
- The five steps of mart design (Kimball's four + batch) — business process (11.4.2.1) → grain (11.4.2.2) → dimensions (11.4.2.3) → facts (11.4.2.4) →
  batch (11.4.2.5). In the "daily subscriber count" example, why the grain is "one subscription event" rather than "one day" (from the lowest
  level you can roll up in any direction). The measure examples in 11.4.2.4 are payment amount (local currency and USD), subscription streak and
  counts — the notebook leaves out the streak. The batch check questions in 11.4.2.5 are five (partition definition / one batch = one partition /
  does it read more source partitions than needed, circular references / immutable sources / tests). For each step's deliverable, check questions
  and owner see book section 11.4.2 and table 11.2 — the template in "4. Step by step" below follows that table.
- The role of PMs and leaders — the most common reason a mart goes unused is not technical but the absence of the business partner. Steps 1 and 2
  are filled in together with the requester. See book section 11.4.3.
- Operations — one batch = one partition (insert-overwrite, idempotent, simple backfill; full rebuilds cannot bear the cost once data grows, and
  UPDATE batches give no confidence about the result of running twice, 11.5.1) / SCD via a full daily snapshot (date × user_id, 11.5.2) / four kinds of
  tests (unique, not null, accepted values, freshness) to catch marts that go wrong silently (revenue doubled by source duplicates, revenue NULL from
  a missing exchange rate, a new event dropped by a filter) — run automatically after the batch, 11.5.3 / late-arriving data: partition sources by
  arrival time, marts by occurrence time plus a reload window (3 or 7 days), and share the settle time in advance ("yesterday's number is final
  after 3 days"), 5.4. See book sections 11.5.1–11.5.4 and figure 11.3.
- Wrap-up — a mart is not a cure-all: questions the design did not anticipate go down to the facts/dimensions or raw. The thing to do right now
  is to write the grain of your slowest or most frequently rewritten query in one sentence — if you can write it, half the design is done; if you
  cannot, it shows where the ambiguity is. Caution in the summary table: a grain declaration plus unique, not-null and freshness tests are the minimum line of trust.

## Run and verify

```bash
python generate_data.py      # creates 5 files in data/*.csv (SEED=42, 3,000 users × 90 days, ~16MB total)
jupyter nbconvert --to notebook --execute data_mart_layers.ipynb \
  --output-dir ../../my-work/11_my_query_has_been_running_for_30_minutes   # results go to my-work
```

- Inputs: `data/events.csv`(event_id, user_id, event_name, session_id, event_time, received_time, properties),
  `data/subscription_events.csv`(sub_event_id, user_id, event_type, sku_id, is_trial, event_time, received_time, price_local, currency),
  `data/user_snapshots.csv`(snapshot_date, user_id, platform, country, app_version, install_date), `data/sku.csv`, `data/exchange_rates.csv`.
  Row counts (approx., table in book section 11.6.1): events 95K · subscription_events 1,600 · user_snapshots 136K · sku 4 · exchange_rates 450.
  Period 2026-04-01 to 06-29; a trial start is a purchase with price 0, a refund is a negative amount.
- SQL files (same queries as inline — the mart SQL is an example with one partition expanded): `sql/raw_daily_subscribers.sql`, `sql/stg_views.sql`, `sql/dim_tables.sql`,
  `sql/fact_subscription_events.sql`, `sql/fact_subscriber_daily.sql`, `sql/mart_subscription_daily.sql`. Run them from the chapter folder.
- **Expected results**: the truth planted by the generator (printed to stdout when `python generate_data.py` runs — the notebook does not
  recompute it) is a June daily average of **574 active subscribers (incl. trials)**, total revenue for the period
  **$5,953** (net of refunds), arrival-lag distribution app events 70/20/8/2%, subscription events 55/25/12/8%.
  What to check in the notebook is the list below (the fact layer aggregates differently from the generator, so the two amounts above are
  not compared directly with notebook results):
  - 11.6.2 raw query 47 lines → 885 result rows; 11.6.3 `stg_subscription_events` 1,597 rows / 1,008 users, raw 95,313 rows → staging 86,040 rows (duplicates and system events removed)
  - 11.6.4 `dim_user_daily` 136,213 rows / 3,000 users / max_days 89 · `fact_subscription_events` purchase 1,405 ($6,074.05) · renewal 153 ($915.74) · cancel 26 · refund 13 (−$126.14) · `fact_subscriber_daily` 20,955 rows / 1,008 users
  - 11.6.5 mart 5,225 rows (2026-04-01 to 06-29), mart query 3 lines → 885 rows, `Active-subscriber difference, raw query vs mart (sum): 0` — raw and mart give the same number.
    Last tail row on both sides: 2026-06-29 ios KR 72 active · $43.04.
    The revenue difference (sum) is **126.14 USD** (raw side higher) — because the raw query treats the cancel/refund day as inactive so the negative refunds drop out (an intended difference)
  - 11.6.6 before/after running twice identical `(70, 109.83)`; INSERT without DELETE gives 70 unique-key violations
  - 11.6.7 the 2026-06-14 partition fills in from the D+1 morning batch 13 events ($82.31) → D+2 20 ($96.90) → D+3 24 ($104.84) → D+4 morning batch 26 ($109.83) (50% → 77% → 92% → 100%).
    Only purchase/renewal counts and revenue are examined — active subscriber counts only reflect the delay once `fact_subscriber_daily` is rebuilt.
  - Execution times are not expected values (raw query around 1 second, mart query 0.00x seconds — varies by environment).
- This chapter's **apply mode is writing a design document, not substituting code** (protocol below).

## Apply to my data — interactive protocol

Take one line of the reader's requirements, or the slow query they are using now, and fill in the **five-step mart design template** together.
Fill in first whatever can be extracted from code, and ask the reader only for business context. Show the result of each step and confirm before moving on.

### 1. Intake — what to ask the reader

- How are you looking at this number today? (not at all / someone's query / a dashboard) What is painful about it? (slow / cannot see it / differs by team)
- Down to what level do you want to slice it? (platform, country, product, channel, trial flag, ...)
- Definitions of the key metrics — e.g. does "subscriber" include trials, are refunds excluded
- Where are the sources, and does any source arrive late (attribution, store notifications, etc. → reload window)
- If a query was brought: which tables it reads, and classify each CTE as cleanup / join / aggregation

| Role (example name in the notebook) | Type | Meaning | Required |
| --- | --- | --- | --- |
| Event/transaction log (`subscription_events`) | row-level | grain candidate — what is one row | ✅ |
| Attribute source (`user_snapshots`) | user × date | dimension candidate (slowly changing) | ✅ |
| Reference tables (`sku`, `exchange_rates`) | small tables | dimensions and conversions | optional |
| `event_time` / `received_time` | timestamp | to judge late arrival | recommended |

### 2. Data check — do not start the analysis until this passes

```python
import duckdb
con = duckdb.connect()
con.execute("""
SELECT COUNT(*) AS rows, COUNT(DISTINCT <id>) AS ids, MIN(<ts>) AS t0, MAX(<ts>) AS t1,
       COUNT(*) - COUNT(DISTINCT <id>) AS dup_rows
FROM read_csv_auto('<file>')""").df()
```

Pass criteria: a row identifier exists or can be built (without one, no grain can be declared) · a time column exists · the duplicate ratio is known
· you know which entities have changing attributes (users, products).

### 3. Code substitution map

| Anchor (practice section / identifier) | What | How |
| --- | --- | --- |
| 11.6.3 `stg_*` views | source file paths and column names | one view per source. Names, types, duplicates and noise only |
| 11.6.4 `fact_subscription_events` | one-sentence grain → one row | exactly the grain declared in step 2. Conversions (exchange rates etc.) go here. Measures like the streak in book 11.4.2.4 are added by extending the fact with a column |
| 11.6.4 `fact_subscriber_daily` | state snapshot (semi-additive) | only when you need "entities that are ~ at that point × date" |
| 11.6.4 `dim_user_daily` | slowly changing attributes | full daily snapshot + a `_latest` view |
| 11.6.4 `dim_sku` | reference table (product master) | copy staging as-is — the reader's reference tables work the same way |
| 11.6.5 `MART_SQL` | aggregation of one `{partition_date}` partition | GROUP BY the level (dimensions) decided in step 1 |
| 11.6.7 `window_days` | reload window | the source's maximum delay in days + 1 |

⚠ The `{received_filter}` slot in `MART_SQL` is filled only in 11.6.7 — in a production batch it stays empty.

### 4. Step by step

1. **Business process** — one page on the current situation, the pain, the metrics and levels being watched, and the extra metrics wanted. Confirm the business partner has been talked to.
2. **Grain declaration** — one sentence, "One row per ...". Recommend the lowest level (event) and ask whether it overlaps an existing mart.
3. **Dimensions** — who, what, where, when, why, how. Mark the keys to split out into separate dimensions (user, product).
4. **Facts** — the list of measures, each marked additive / semi-additive / non-additive.
5. **Batch** — partition key, full/incremental/view, one batch = one partition, whether it reads more source partitions than necessary (circular references),
   immutable sources, tests (unique, not null, accepted values, freshness), reload window. The five check questions in book section 11.4.2.5.
6. The deliverable is one markdown page with the template below filled in. If a query was brought, append a table classifying its CTEs as staging / fact / mart.

```markdown
# Mart design — <mart name>
## 1. Business process (Select the Business Process)
- Current situation: / Pain: / Metrics and levels watched today: / Extra metrics wanted:
- [ ] Talked to the business partner directly  [ ] The operational process actually exists
## 2. Grain (Declare the Grain)
- One row per ...
- [ ] Is it one sentence  [ ] Does it cover most of the process in 1  [ ] Does it not overlap an existing model
## 3. Dimensions (Identify the Dimensions)
- Who: / What: / Where: / When: / Why and how:
- [ ] Keys to split out into separate dimension tables  [ ] No overlap with existing dimensions
## 4. Facts (Identify the Facts)
- Measures (marked additive / semi-additive / non-additive)
- [ ] All metrics from 1 are covered  [ ] No overlap with existing facts
## 5. Batch (Define Batch Process)
- Partition key: / Mode (full, incremental, view): / Reload window: / Tests: / Schedule:
- [ ] Partition defined  [ ] One batch = one partition  [ ] Does not read more source partitions than necessary (no circular references)  [ ] Immutable sources  [ ] Tests defined
```

### 5. Interpreting the result

- If the one-sentence grain cannot be written, what is missing is not a mart but a **definition** — go back to steps 1 and 2.
- If a mart with the same grain already exists, do not build a new one; first consider **attaching** dimensions and facts to it.
- If the reload window is not 0, tell dashboards and meetings that "yesterday's number can still change" (book section 11.5.4: "yesterday's number is final after 3 days").
- A mart answers only the questions it was designed for (book wrap-up) — for a question the design did not anticipate, do not improvise a new mart; go down to the facts/dimensions or raw
  to answer it, and if it recurs, consider adding a dimension to the existing mart.
- The final sign-off on the deliverable is with the business partner (owner column of book table 11.2: steps 1 and 2 are PM/business partner + analyst, step 5 is engineer + analyst).

## Pitfalls

- The moment one line of business logic (e.g. "exclude trial users") lands in staging, the definition lives in two places — push it down to the fact/mart.
- Never SUM semi-additive values (active subscribers, DAU, balances) across dates. Weekly is the last day's value or the average, not the sum.
- A batch that only INSERTs without DELETE duplicates when run twice (11.6.6). Without a unique-key test it goes wrong silently.
- Batch success ≠ correct numbers (book section 11.5.3) — revenue doubled by source duplicates, a whole day's revenue NULL from an empty exchange-rate table, a new event type
  dropped by a filter. Build the accepted-values test so it **fails** when a new value arrives, to detect it proactively.
- Choosing a full rebuild or an UPDATE-changed-rows approach instead of incremental (insert-overwrite) causes cost problems as data grows and
  uncertainty about the result of running twice (book section 11.5.1).
- DuckDB syntax: `DATE + BIGINT` does not work (CSV integers come in as BIGINT → `CAST(... AS INTEGER)`); expanding partitions is
  `UNNEST(generate_series(start, end, INTERVAL 1 DAY))`.
- At notebook scale even the raw query finishes within a second, so the "30 minutes" is not reproduced — the practice shows the difference in structure and reproducibility.
- In 11.6.7 only the subscription-event numbers (purchase/renewal counts, revenue) reflect the delay — to see active subscriber counts too,
  `fact_subscriber_daily` must be rebuilt.
- A mart answers only the questions it was designed for — a mart aggregated by day, platform and country cannot show hour of day or app version. Coverage and performance are
  a trade-off, and questions not in the mart go down to the facts/dimensions or raw (book sections 11.3.4 and 11.4.1).
- Building one more mart on a similar subject for a quick fix guarantees a day when the same metric gives different numbers in each mart —
  consider modifying the existing mart first (book section 11.4.1).
- The practice's `fact_subscriber_daily` takes the cancel/refund date as the first one per user (MIN), a simplification — re-subscribing users disappear silently.
  In production, refine it so a cancel is matched only to the immediately preceding subscription period (notebook 11.6.4 note).
- For late-arriving data, partitioning the source by occurrence time breaks the immutable-source rule — sources by arrival time,
  marts by occurrence time plus a reload window (book section 11.5.4).

## Study guide

### Core concepts — what you should be able to explain after this chapter

- The role of the four layers (raw, staging, dim/fact, mart) and what each layer **does not** do
- Why the one-sentence grain is half the design, and why to take the lowest level
- additive / semi-additive / non-additive
- One batch = one partition (idempotency) and backfill; solving SCD with daily snapshots
- Late-arriving data and the reload window; the four tests (unique, not null, accepted values, freshness)

### Concept check

1. A colleague proposes adding a WHERE clause to a staging view that "excludes trial users from subscribers". Which layer does that logic belong in, and what goes wrong if it goes into staging?
   - Hint: the definition is in two places — some people trust staging, others trust the mart.
2. The goal is "daily subscriber count", but the grain was set to "one event". Compared with "user × date", what do you gain and what do you lose?
   - Hint: drill-down and re-aggregation vs table size.
3. How do you look at the mart's `active_subscribers` weekly?
   - Hint: semi-additive.
4. The batch ran twice. Why is `run_partition` safe, and why is an INSERT-only batch dangerous?
   - Hint: the 70 unique-key violations in 11.6.6.
5. Attribution settles up to 3 days after install. What has to change in the batch, and what in the dashboard?
   - Hint: reload window + "yesterday's number is not final".

### Further exercises

1. **[Sandbox]** Predict how the D+1 to D+4 morning-batch table in 11.6.7 changes when `SUB_ARRIVAL_LAG` in `generate_data.py` is set to `{0: 0.3, 1: 0.3, 2: 0.2, 3: 0.2}` → regenerate and re-run → check → restore with `git checkout -- generate_data.py data/`.
2. **[Sandbox]** Remove the `QUALIFY` from `fact_subscriber_daily` and re-run 11.6.6 to see what the unique-key test catches. Restoring is mandatory.
3. **[Thinking]** Pick the query your team rewrites most often and write its grain as "One row per ...". If you cannot, why not?
