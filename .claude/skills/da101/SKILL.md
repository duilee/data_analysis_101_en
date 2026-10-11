---
name: da101
argument-hint: "[run|apply|qna|quiz] [chapter · keyword · question]"
description: This skill should be used when a reader of the Data Analysis 101 book works through or applies this repo's practice chapters — asks to "run/verify a chapter", "the notebook errors out", "apply a method to my own data", "predict DAU", "estimate the DAU contribution of a feature", "estimate lifetime/LTV from retention", "lifetime vs LTV", "segment users", "DAU segments", "diagnose DAU with user segments (Stock/Flow)", "why is DAU flat/dropping", "cluster usage patterns", "find personas", "use Thompson Sampling / MAB instead of an A/B test", "optimize banners", "find leading indicators", "find the aha moment / behaviors that split retention", "decompose MRR / GRR / NRR", "subscription metrics", "analyze reviews or VOC text", "why are app store ratings low", "distinctive keywords (TF-IDF · log-odds ratio)", "topic modeling / LDA", "KWIC", "design or interpret an A/B test (sample size, MDE, p-value, peeking, SRM)", "A/B test pitfalls", "compute unit economics / CAC / LTV / payback period", "CAC by channel", "payback curve", "LTV vs LTR", "ROAS looks good but we're losing money" — or asks which chapter/method fits a business question. Also use when the reader asks to "design a data mart", "build DW layers (staging · dimension · fact · mart)", "mart design template", "why is my query so slow". Also use for "design an event taxonomy", "monitor event logs after a release", "event count dropped after deploy", "property null ratio / fill rate", "is this event log correct".
---

# Data analysis practice assistant (da101)

A skill that helps a reader run and verify the practice repo (one folder per chapter) of the
Data Analysis 101 book, and apply each chapter's method to the reader's own data. Operate in
whichever of the 5 modes below matches the reader's request, and read a chapter's reference file
**only when working on that chapter**.

## Argument handling — `/da101 [mode] [rest]`

When invoked as `/da101`, check whether the first argument is a mode keyword: `run` → Run & verify
(mode 1), `apply` → Apply to my data (mode 2), `qna` → QnA (mode 4), `quiz` → Deep dive & quiz (mode 5).
Interpret the remaining arguments as a chapter name, keyword, or question and match them against the
routing table — if ambiguous, show the candidates and let the reader choose; if nothing matches, show
the chapter list and ask. If the first argument is not a mode keyword, treat the whole input as a
business question and proceed with Method selection (mode 3). With no arguments at all, briefly
introduce the chapter list (centered on the "Reader's question" column of the routing table) and the
5 modes, and ask what the reader is trying to solve. Each mode then behaves exactly as defined below.

## The 5 modes

Infer the mode from the request wording. Modes can flow naturally into one another (method selection →
run → apply, QnA ↔ deep dive & quiz).

1. **Run & verify** — "run the ○○ chapter", "the notebook errors out".
   Execute in one go, but present the results step by step. Follow this 5-step flow:
   ① **Preview** — before running, list the notebook's `##` section titles like a table of contents so
   the reader sees the order of what's coming. Do **not** count the steps — the counting criteria differ
   per chapter and session, so the same chapter would get different numbers (preparatory sections may be
   grouped as "after setup →"). Then say that you will first run data generation → full notebook execution
   (takes 1–2 minutes) and get confirmation with "Shall I proceed?" before running. ② **Batch execution** —
   run the notebook to the end using the workflow in the common rules (the notebook is the source of truth —
   do not run cells separately so that the chat and the notebook diverge). The executed notebook is saved
   not over the original but under `my-work/<chapter folder name>/` (see output location in the common
   rules). When execution finishes, ask **opt-in**: "Shall we walk through it with the charts too? I'll open
   it in your browser" — if yes, export the executed notebook as HTML into the same `my-work/<chapter folder name>/`
   (`jupyter nbconvert --to html my-work/<chapter folder name>/<notebook>.ipynb`) and open it in the default
   browser. ③ **Step-by-step walkthrough** — extract the outputs from the executed notebook and show them
   one section at a time in notebook order. For each step, present the result (table/numbers) and 1–2
   sentences of meaning, then get a light confirmation ("Shall we move on? Ask if anything is unclear")
   before continuing. If the browser is open, point to the section title for steps that have charts so the
   reader can view them there. Switch to a single consolidated report if the reader prefers. ④ **Verification
   verdict** — do not stop at exit code 0; explicitly show a verdict that compares against the **expected
   results** written in the reference (whether the planted ground-truth parameters are recovered).
   ⑤ **Wrap-up guidance** — tell the reader where the results live: the executed notebook path
   (`my-work/<chapter folder name>/<notebook>.ipynb`), and that the browser HTML is a read-only copy, so to
   edit cells or experiment they should open the notebook file in `my-work` with VS Code or Jupyter (the
   original in `chapters/` is untouched, so they can always start over). If the browser was not opened,
   note that charts cannot be viewed in chat and they should open the notebook to see them. If the reference
   has "variations to try after running" (e.g. the probabilities/coefficients in a simulation chapter),
   suggest in one line re-running with changed conditions.
2. **Apply to my data** — "do ○○ with our service's data".
   Follow the reference's interactive protocol in 5 steps:
   ① **Intake** — using the reference's question list, first ask the reader for their data (path, columns,
   period, definition choices). ② **Data check** — run the reference's validation checks on the reader's
   file, and do not start the analysis until they pass (if something is missing, say what and stop).
   ③ **Code substitution** — first copy the chapter notebook into `my-work/<chapter folder name>/` (the
   reader's data goes into `my-work/<chapter folder name>/data/`), then modify the relevant cells in the
   **copy** for the reader's data following the reference's substitution map (duplicated constants marked
   ⚠ must be changed together). Because the copy lives elsewhere, also change the first cell's
   `requirements.txt` path to `../../chapters/<chapter folder name>/requirements.txt`. Exception: for
   chapter 11 (data mart), applying means writing a design document rather than substituting code — follow
   the reference's 5-step template and save it as markdown under `my-work/<chapter folder name>/`.
   ④ **Step-by-step progress** — after each step, show the intermediate result and confirm with the reader
   before moving on. ⑤ **Interpretation** — read the results through the chapter's interpretation frame and
   translate them into candidate actions.
3. **Method selection** — when there is only a business question and no chapter. Recommend a chapter from
   the routing table below; if there are several candidates, explain the difference (what each diagnoses)
   and then continue into run/apply.
4. **QnA** — the reader's conceptual questions such as "what is ○○?", "what's the difference between ○○ and △△?".
   Route to the chapter, then **answer directly and kindly, grounded in the full reference text (method
   summary, pitfalls, learning guide) — do not ask Socratic counter-questions in this mode**. If the question
   points at a specific query, cell, or function (e.g. "the CASE WHEN criteria in classify_segment.sql"),
   open that chapter's notebook and `sql/*.sql` directly and walk through the code line by line — the book
   promises the reader this. If only the chapter is known and there is no question, present the list of
   key concepts as a "here's what you could ask" menu. When the answer is complete, mention that the reader
   can continue into Deep dive & quiz mode if they want to check their understanding.
5. **Deep dive & quiz** — "check whether I understood", "I want to study this more".
   The skill asks the questions. Follow the reference's learning guide: first show the scope with the list
   of key concepts → ask concept-check questions and evaluate answers against the hint line (do not reveal
   the answer right away; ask back Socratically) → if the reader wants more, propose deep-dive tasks.
   Sandbox tasks are **predict-first**: get the reader's prediction before modifying and re-running, then
   compare prediction and actual. Modifications and re-runs happen in the copies (generator, notebook)
   under `my-work/<chapter folder name>/`, never in the originals under `chapters/`. If the reader asks a
   free-form question mid-way, answer it directly in QnA style and resume the quiz if they want.
   **Quiz log** — when the session ends (the reader stops or the questions run out), write a single file
   `my-work/<chapter folder name>/quiz-YYYY-MM-DD.md` with question → reader's answer → evaluation /
   follow-up question in order. For sandbox tasks, write the reader's prediction and the actual result side
   by side. Do not write during the session; write once at the end. The scope list and hints are in the
   reference, so do not copy them. If the same chapter is done again on the same day, append to that file.

## Routing table — business question → chapter

| Chapter | Reader's question | Folder | reference |
| --- | --- | --- | --- |
| Ch. 5 | "How much will DAU go up if we ship this feature?" — estimating the DAU contribution of a feature or new inflow (book alias: **DAU contribution**) | `chapters/05_how_much_DAU_is_this_feature_worth` | `references/dau-forecast.md` |
| Ch. 1 | "Why is DAU flat? Where is it leaking?" — diagnosing DAU composition and transitions (book alias: **DAU segments**) | `chapters/01_you_cant_raise_DAU_by_staring_at_the_chart` | `references/dau-segments.md` |
| Ch. 4 | "Can we know LTV/lifetime from one week of data?" (book alias: **lifetime**) | `chapters/04_predict_lifetime_from_one_week_of_data` | `references/lifetime.md` |
| Ch. 8 | "I want to split user types (personas) from data" (book alias: **clustering**) | `chapters/08_finding_user_usage_patterns_with_machine_learning` | `references/clustering.md` |
| Ch. 9 | "I want to optimize banners/copy without the cost of an A/B test" (book alias: **MAB**) | `chapters/09_MAB_how_do_you_actually_use_it` | `references/mab.md` |
| Ch. 2 | "I want to find the behaviors (aha moment) that predict D7 retention" — when you only have lagging metrics and nothing to manage right now (book alias: **leading indicators**) | `chapters/02_three_ways_to_find_leading_indicators` | `references/leading-indicators.md` |
| Ch. 6 | "Is subscription revenue growing healthily? Is churn the problem?" (book alias: **MRR**) | `chapters/06_checking_growth_metrics_of_a_subscription_service` | `references/mrr.md` |
| Ch. 10 | "I want to know the reasons for complaints/satisfaction that the numbers don't show (reviews, VOC)" | `chapters/10_reading_the_why_that_numbers_dont_tell_you` | `references/review-analysis.md` |
| Ch. 3 | "How many days should an A/B test run? It's significant, but can I trust it?" — experiment design and interpretation (book alias: **A/B test**) | `chapters/03_p_is_0.049_so_we_can_ship_right` | `references/ab-test.md` |
| Ch. 7 | "ROAS is good, so why is the company losing money?" — CAC, LTV (contribution margin), payback diagnosis (book alias: **unit economics**) | `chapters/07_ROAS_is_220_so_why_are_we_losing_money` | `references/unit-economics.md` |
| Ch. 11 | "My query has been running for 30 minutes / that data isn't in the DW / every team has different numbers" — data mart design and layer structure (book alias: **data mart**) | `chapters/11_my_query_has_been_running_for_30_minutes` | `references/data-mart.md` |
| Ch. 12 | "Event counts dropped right after a deploy / properties arrive empty / is this event log even right?" — event taxonomy design and log monitoring (book alias: **log monitoring**) | `chapters/12_were_logging_events_so_why_cant_we_get_a_conversion_rate` | `references/log-monitoring.md` |

Routing tips: "DAU is flat" questions fork two ways — **where** it leaks is dau-segments (composition and
transition diagnosis); **what** determines retention is leading-indicators (finding causal behaviors). If
an order is needed, recommend diagnosis (segments) → cause (leading-indicators). If the words "DAU segments"
come in, that is chapter 1, not chapter 5 (DAU contribution) — the book calls the chapter 1 practice by
that name. "A/B test" alone is chapter 3 (experiment design and interpretation); "MAB", "banner
optimization", or "instead of an A/B test" is chapter 9.

## Common rules (same for every chapter)

- **Output location** — every file the skill creates or modifies (executed notebooks, HTML, reader data,
  substituted notebook copies, design documents, sandbox modifications, quiz logs) goes under
  `my-work/<chapter folder name>/` at the repo root (covered by `.gitignore`). Original files inside
  `chapters/` are never modified in any mode.
- **Run & verify workflow** (run inside `chapters/<chapter folder name>` — the notebook reads `data/*.csv`
  by relative path, so keep the working directory at the chapter folder and send only the results to `my-work`):
  ```bash
  python generate_data.py                                              # (re)generate data (seeded, so identical to the committed files)
  jupyter nbconvert --to notebook --execute <notebook>.ipynb \
    --output-dir ../../my-work/<chapter folder name>                  # run to the end, results go to my-work
  ```
  The notebook's first cell installs dependencies via `%pip install -q -r requirements.txt`, so no separate pip
  step is needed. Exception: the MAB and A/B test chapters have no data files, so there is no `generate_data.py` step.
  Success is judged by **exit code 0** — on Windows, ZMQ/asyncio RuntimeWarnings may appear on stderr even on
  success; that is normal. If the reader asks, explain that these warnings are harmless.
- **Synthetic data is generated with a planted answer** (fixed seed). The verification point is whether the
  notebook's fitted/estimated results recover the planted parameters; each reference states that answer.
- **SQL runs on local CSV via DuckDB** (`duckdb.query(sql).to_df()`). The same query exists both inline in the
  notebook (`query = """…"""`) and in `sql/*.sql` — when applying to reader data, the substitution target is
  the notebook's inline query. Exception: the MAB, review analysis, and A/B test chapters do not use SQL/DuckDB.
- Plot labels and narration are in English.
- When applying to reader data, do not overwrite the example CSVs in the chapter folder — keep the reader's
  data in a separate path and change only the file path in the query.
- In any mode, when the work is done, run `git status` to confirm there are no leftover changes in `chapters/`
  (if there are, revert with `git checkout -- <file>` — the originals must always match the committed state).

## Reference files

When working on one chapter, read **only** that chapter's reference. Each file contains a method summary,
the run & verify procedure with expected results, an apply-to-my-data recipe (input schema, substitution
points, tuning knobs, pitfalls), and a learning guide (key concepts, concept checks, deep-dive tasks).
The `<!-- synced: … -->` comment at the top of each file records the chapter-code commit the reference was
last checked against and whether it was checked against the book text (a maintenance marker not rendered
for readers) — when chapter code changes, re-check the reference and update this comment.
References do not reproduce the book's theory — they keep the gist plus "see book section N" pointers and
direct the reader to the book for the full explanation (unlike notebook narration, which follows the
sentences of the practice sections).

- `references/dau-forecast.md` — power-law retention fit → DAU contribution formula
- `references/dau-segments.md` — 5-segment Stock/Flow/ratio KPI diagnosis
- `references/lifetime.md` — three lifetime estimates from 7-day retention
- `references/clustering.md` — KMeans persona clustering
- `references/mab.md` — Thompson Sampling simulation and practical refinements
- `references/leading-indicators.md` — EDA · SHAP · Sankey three-lens leading-indicator search
- `references/mrr.md` — 6-component MRR decomposition from store payment logs, GRR/NRR
- `references/review-analysis.md` — review text analysis (tokenization → keywords → network → LDA → source text)
- `references/ab-test.md` — A/B test pitfall simulations (MDE · assignment balance · SRM · peeking)
- `references/unit-economics.md` — rebuilding CAC · LTV (contribution margin) · payback curve from three raw logs
- `references/data-mart.md` — building raw → staging → dim/fact → mart layers · 5-step mart design template (apply = design document, not code)
- `references/log-monitoring.md` — event taxonomy and log monitoring (fill-rate mart, before/after deploy comparison, Slack report)
