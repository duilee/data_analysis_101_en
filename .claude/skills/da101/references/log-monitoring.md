# Log monitoring — finding logs that broke after a release

**Chapter folder**: `chapters/12_were_logging_events_so_why_cant_we_get_a_conversion_rate/` · Notebook: `log_monitoring.ipynb`
<!-- synced: code at duilee/data_analysis_101@3de9864 (Korean original, 2026-09-24) — checked against notebook, README, sql, generate_data, and extra. Book text checked (2026-09-26; manuscript section layout: section 1 intro → section 2 taxonomy components (2.1–2.5) → section 3 design (3.1–3.3) → section 4 naming (4.1–4.4) → section 5 templates (5.1–5.4) → section 6 validation and monitoring (6.1–6.2) → practice 0–4 → Claude Code practice → wrapping up). -->

## The problem this method solves

Even when the event taxonomy (the agreement on what to record, under which name, and with which context) is right, a new app version
quietly breaks the logs in one of three ways — an event stops arriving (missing), arrives twice (duplicate firing), or arrives with an empty
value (lost property values). The document shows no trace of it; only the numbers change. So, separately from comparing the document with the log, you need monitoring that **watches the numbers**.

- 12.7.2 Daily marts: raw log → event mart (counts and user counts by date, platform, and event) + property fill-rate mart (not-null ratio per (event, property)). Monitoring runs on these marts, not on raw data.
- 12.7.3 Event-count anomalies: basis date D-2 vs one week earlier D-9 (removes the day-of-week effect), |change| > 60% and count on one side > minimum 50. 30-day trend plot of the caught events (pre-release average = 100 index).
- 12.7.4 Property fill-rate anomalies (the book calls it "detecting missing-property anomalies"): same two dates, not-null ratio down by more than 60% (increases are not incidents, and events that didn't arrive on the basis date belong to step 2).
- 12.7.5 Report: three groups — 📉 dropped / 📈 rose / 🕳️ lower fill rate — as Slack mrkdwn text. When nothing is unusual, send a single "✅ No anomalies" line so "no issues" is distinguishable from "didn't run". Sending is a one-line `requests.post(WEBHOOK_URL, …)` comment.

**Pointers to the book's theory sections** (in Q&A mode, give the gist and refer the reader to the relevant book section for details):
- 12.1 Intro (Table 12.1) — searching for 'home' turns up page_view_home / home_view / HomeScreen, all three. Taxonomy = the agreement between the product and the data. The cost of neglect is "a product team that can't find the data and can't decide + an analyst who spends time tracing history".
- 12.2 Components of a taxonomy — four parts: events / event properties / user properties / context. 12.2.1 one log record as an example (JSON). 12.2.2 the four event types (page view, tap/click, impression, system/server) and the four questions before adding an impression event (is there a metric that uses it as a denominator; is there a decision it would change; can page_view stand in for it; can we handle the volume). 12.2.3 client vs server events — the difference is reliability; payments and state go on the server, behavior and context on the client; accept some client loss but catch sudden changes with monitoring. 12.2.4 (Table 12.2) event properties (the context of that moment, breakdown axes) vs user properties (the state at that time, segment axes). 12.2.5 context (auto-collected by the SDK) and the screen hierarchy — screen_name as a required property on every event (Figure 12.1).
- 12.3 Designing a taxonomy — 12.3.1 three premises: an event becomes part of the product the moment it is planted in code (logging and QA are a step of the development process) / many roles use it, so names must be predictable / it exists to check the current state, so don't force continuity with the past (logs have a short shelf life; server events are the exception). 12.3.2 (Table 12.3) design order = question → metric → funnel → events/properties (onboarding redesign example; planting bottom-up on every screen element is the common mistake). 12.3.3 (Table 12.4) event vs property trade-offs and the four deciding questions (will it ever be plotted on one line; is it a funnel step or an attribute; is the set of distinguishing values open-ended; are the required properties the same). Principle: an event is a unit of intentional behavior; where, on what, and under which condition are properties.
- 12.4 Naming — 12.4.1 (Table 12.5) prefixes page_view_/tap_/view_/system_. 12.4.2 (Table 12.6) prefix_target[_detail], lowercase snake_case, no screen, version, platform, or abbreviation in the name, record the trigger condition in two or three sentences. 12.4.3 (Table 12.7) event property definition = type, required or not, value range, example; a property name means one thing globally (content_id vs item_id, don't reuse 'type'); ids and phone numbers are strings; one boolean notation; bundle properties that are often used together. 12.4.4 user properties = up_ prefix, update policy (overwrite, accumulate, keep first value), enum allowed values and initial value, four categories (settings, num_of_record, account, experiment).
- 12.5 Templates (Tables 12.8–12.11) — screen / event / event property / user property templates. Add the columns you need (status, platform, note).
- 12.6 Validation and monitoring — 12.6.1 (Table 12.12) four kinds of gap between document and log: undocumented events / undeployed or missing events / missing properties or values outside the allowed set / platform asymmetry — put the document and the log side by side and find them mechanically with set differences, allowed-value comparison, and platform distribution (daily batch). The appendix `extra/taxonomy_check.py` covers this section. 12.6.2 (Table 12.13) three ways logs break even when the taxonomy is right: sharp drop in event count (missing, SDK init failure, release missing on one platform) / sharp rise (duplicate firing, retry loop, duplicate auto-tracking) / lost property values (missing value, renamed key, changed type). 12.7.3 covers the first two rows of Table 12.13, 12.7.4 the third.
- Practice section — the minimum count of 50 is the in-house threshold (10,000) scaled down to the practice data, so set it again for your service. The basis and comparison dates are fixed only in the practice; in operation compute them from today.
- Wrapping up — two things to remember: an unmanaged taxonomy is abandoned within months (bring logging and QA into the development process) / there is no perfect taxonomy from the start (make it answer today's questions, add when new questions arise, don't force continuity with the past). Summary table: question "we have logs, so why can't we analyze" → solution "prefixes to tell types apart, separate event properties, user properties, and context, monitor after releases" → caution "design from the question, maintain the document continuously" → next action "compare before and after the last release on your daily event mart → establish data governance by resolving the issues".

## Running and verifying

```bash
python generate_data.py      # 3 CSVs under data/ (SEED=11, 3,000 users × 30 days, event_log ≈ 170K rows)
jupyter nbconvert --to notebook --execute log_monitoring.ipynb \
  --output-dir ../../my-work/12_were_logging_events_so_why_cant_we_get_a_conversion_rate   # results go to my-work
```

- Input: `data/event_log.csv` (2026-08-01 to 08-30; event_time, user_id, platform, app_version, event_name, screen_name, properties JSON),
  `data/taxonomy_events.csv` (24 events), `data/taxonomy_properties.csv` (13 properties: scope, data_type, allowed_values, events).
- Notebook constants: `BASIS_DATE = "2026-08-28"` (D-2), comparison date 08-21 (D-9), `RELEASE_DATE = "2026-08-25"` (3.5.0 release). Thresholds are in the `params` CTE at the top of each query (basis_date, threshold 0.6, min_cnt 50).
- SQL files (same as inline): `sql/mart_event_daily.sql`, `sql/mart_event_param_daily.sql`, `sql/event_count_anomaly.sql`, `sql/param_null_anomaly.sql`.
- **Expected results** (the five incidents the generator plants in the 8/25 3.5.0 release — all caught by the standard thresholds ±60%, min 50. The numbers must match the tables in the book's practice section):
  - 12.7.2: raw log 172,458 rows → event mart 1,426 rows · property mart 1,486 rows. Check rows for 8/21: `page_view_home` Android 297 / iOS 378, `tap_content_card` Android 251 / iOS 330, `view_content_card` Android 1,048 / iOS 1,336; the content_id and content_type fill rates of `page_view_content_detail` are 1.0 on both platforms (Android 251 events, iOS 330 events).
  - 12.7.3 📉: Android and iOS `system_subscription_renewed` 83/76 → 0 (−100%, server renewal batch stopped — both platforms at once), iOS `tap_content_card` 330 → 103 (−68.8%), Android `page_view_home` 297 → 105 (−64.6%)
  - 12.7.3 📈: Android `view_content_card` 1,048 → 2,312 (+120.6%, duplicate firing)
  - 12.7.4: iOS `page_view_content_detail` `content_id` fill rate 1.0 → 0.2857 (−71.4%) — the event count rose from 330 to 350 while only the value went empty. Events that didn't arrive on the basis date (subscription renewal) are excluded from step 3 (step 2's job)
  - 12.7.5 Report with six items (4 dropped, 1 rose, 1 fill rate) — header "🚨 Log anomaly report — 2026-08-28 (vs. one week earlier, ±60%, min 50 events)". The two figures are saved to `img/event_trend.png` and `img/param_trend.png`.
- Appendix `extra/taxonomy_check.py` (run from inside extra/, book 12.6.1): document rule checks (prefix, snake_case, description, enum allowed values, user property candidates) + coverage of 4 questions (onboarding conversion, home banner click-through, content card click-through, paywall conversion by entry path) + document vs log comparison (4 files in `extra/sql/`: undocumented, dead events, enum drift, platform asymmetry) → draft change request. This dataset has no planted document defects, so 0 request rows is the correct result. Needs the `tabulate` package for `to_markdown`.

## Applying to your data — interactive protocol

### 1. Intake (same order as the four questions in the book's Claude Code practice section)
- Mart — is there already a daily event mart (table name and columns: date, platform, event name, count)? If not, the columns of the raw log (is properties one JSON column or spread into columns?).
- Dates — the last release date. The basis date is at least D-2 after the release (late-arriving events); the comparison date is one week before it.
- Thresholds — daily event volume → minimum count (the practice's 50 is a scaled-down value). The list of critical events that must not be missed (home entry, payment, subscription renewal) → a separate, lower threshold.
- Output format — table / Slack text / webhook send (taken from an environment variable; never write the webhook URL into code or the notebook).
### 2. Confirm the mapping
Show `params` (basis date, comparison date, threshold, minimum count, critical list) and the column mapping table first and get confirmation.
### 3. Run
12.7.2 (only when there is no mart) → 12.7.3 → 12.7.4 → 12.7.5. Build the key list for the property mart from the reader's taxonomy document; if there is none, from the most frequent JSON keys in the log.
### 4. Validate the results
For each caught item, plot the 30-day trend and check that it bends at the release date. Mark swings explained by campaigns or day-of-week effects as "normal variation".
### 5. Interpret the results
Classify each as one of three: regression (request a hotfix) / intended change that the document didn't follow (change request) / normal variation, and return that. Use the platform column to separate app incidents (one platform) from server incidents (both at once).
Next action from the book's wrap-up: resolving the issues caught by the before/after release comparison is the starting point of data governance — recommend running the document vs log comparison (12.6.1, appendix) as a daily batch and the number monitoring (12.6.2, practice) on a twice-weekly schedule.

## Pitfalls

- Using yesterday (D-1) as the basis date makes every event look like it dropped because of logs that haven't arrived yet, causing false alerts. Look at the distribution of received_time − event_time for your service first (usually 95%+ has arrived by D-2). Handling late data in the mart is chapter 11's job.
- Comparing with yesterday mixes in the day-of-week effect. Compare with the same weekday (one week earlier).
- The minimum count filters out chance doublings and halvings of events that fire around ten times a day (e.g. `tap_theme_toggle`, 4–16 events). If there is a small but important event, don't lower the global threshold; keep that event on a separate list with its own threshold.
- The `LEFT JOIN` must be anchored on one week earlier (d8) so that events with 0 on the basis date (−100%) stay in the result. Newly added events are not caught by this query (that is the appendix's undocumented-event check). If you need both directions, use a FULL OUTER JOIN.
- Looking at event counts alone misses the 12.7.4 incident (count up, value empty). Always check fill rates together.
- The document comparison (12.6.1, 4 kinds) and the number monitoring (12.6.2, 3 kinds) are different checks — even when document and log agree, the numbers break after a release. Run both.
- Some loss of client events is something to account for, not something to prevent (book 12.2.3). Payments and state, where loss is hard to tolerate, go to server events.
- Design-stage pitfalls (book 12.3–12.4): planting bottom-up on every screen element / too many impression events / different names for the same meaning (content_id vs item_id) / ids as numeric types / mixed boolean notation / version or platform in the name.
- Don't put execution results in 1×1 code tables (book rule). Don't leave webhooks or in-house table names in the notebook.

## Study guide

### Key concepts
The four event types and prefixes (page_view_/tap_/view_/system_) · client vs server events (reliability) · event properties vs user properties ("does the value exist even when no event happens?", up_ prefix, update policy) · context and the screen_name hierarchy · design order question → metric → funnel → events/properties · the four event-vs-property deciding questions · naming rules and the property definition (type, required, range, example) · the four kinds of document-vs-log gap · the three ways logs break after a release and the three monitoring metrics · the trade-offs of the thresholds (±60%, minimum count, D-2, same weekday).
### Concept check (the five quiz areas of the book's Claude Code practice: types and prefixes / event vs user properties / designing backwards from the question / naming and definitions / the three metrics and thresholds)
1. If the home banner has only tap_main_banner and no view_main_banner, which metric can't be computed? 2. Which release incident raises the event count yet blocks analysis, and which metric catches it? 3. Why use the day before yesterday, not yesterday, as the basis date? 4. Home entry drops only on Android, while subscription renewal is 0 on both platforms at once — where did each incident happen? 5. Should entering the three onboarding step screens be three events, or one event + a step property — which, and on what grounds (the four questions in book 12.3.3)? 6. Of signup date and subscription plan, which is a user property and why?
### Further exercises
Add a critical-event list with a lower threshold (e.g. ±25%, exempt from the minimum count) to `params` and rerun 12.7.3 (book example: what else gets caught when threshold is lowered to 0.4?), and build a practice 5 that detects changes in the per-value share of enum properties (plan, content_type) the same way.
