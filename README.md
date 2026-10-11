# data_analysis_101

Practice code and example data for the Data Analysis 101 book — the English edition of
[duilee/data_analysis_101](https://github.com/duilee/data_analysis_101) (the book was written in Korean).
Each chapter is a folder named after the chapter title; open the notebook inside and run it top to bottom.

## Chapters

Chapter numbers follow the book, and folder names use the same number in the `NN_title` form.
(Chapter 0, "An Analysis Workflow with AI", is an introductory chapter with no practice notebook, so it has no folder here.)

| # | Chapter | What you do |
| --- | --- | --- |
| 1 | [You Can't Raise DAU by Staring at the DAU Chart](./chapters/01_you_cant_raise_DAU_by_staring_at_the_chart) | Split users into 5 segments and diagnose activity with distribution (Stock), transition (Flow), and ratio metrics |
| 2 | [Three Ways to Find Leading Indicators](./chapters/02_three_ways_to_find_leading_indicators) | Find leading indicators of D7 retention in the same event log three ways: EDA comparison, SHAP, and Sankey |
| 3 | [p = 0.049, So We Can Ship, Right?](./chapters/03_p_is_0.049_so_we_can_ship_right) | Reproduce A/B-test pitfalls by simulation (MDE and sample size, random ≠ balanced assignment, peeking false positives) |
| 4 | [Predict Lifetime from One Week of Data?](./chapters/04_predict_lifetime_from_one_week_of_data) | Estimate a year of lifetime from the first 7 days of retention (churn-rate heuristic, power-law catalog matching, long-cohort correction) |
| 5 | [How Much DAU Is This Feature Worth?](./chapters/05_how_much_DAU_is_this_feature_worth) | Forecast a new feature's DAU from new-user counts and D1 retention (power-law retention curve) |
| 6 | [Checking the Growth Metrics of a Subscription Service](./chapters/06_checking_growth_metrics_of_a_subscription_service) | Decompose MRR from store payment logs that have no user ID (user identification, renew/reactivation, GRR/NRR, rough LTV) |
| 7 | [ROAS Is 220%, So Why Are We Losing Money?](./chapters/07_ROAS_is_220_so_why_are_we_losing_money) | Compute unit economics from marketing spend, acquisition, and payment logs (fully-loaded CAC, contribution-margin LTV, channel breakdown, payback curve and payback period) |
| 8 | [Finding User Usage Patterns with Machine Learning](./chapters/08_finding_user_usage_patterns_with_machine_learning) | Cluster usage patterns (personas) with KMeans, interpret and name the centroids, and connect them to action via a retention KPI |
| 9 | [MAB? How Do You Actually Use It?](./chapters/09_MAB_how_do_you_actually_use_it) | Simulate Thompson Sampling for a Multi-Armed Bandit (A/B comparison, alpha coefficient, discounted TS) |
| 10 | [Reading the 'Why' That Numbers Don't Tell You](./chapters/10_reading_the_why_that_numbers_dont_tell_you) | Find the words that separate satisfaction from complaints in product reviews (qualitative data): tokenization, distinctive keywords, co-occurrence network, topic modeling |
| 11 | [My Query Has Been Running for 30 Minutes](./chapters/11_my_query_has_been_running_for_30_minutes) | Build four layers raw → staging → dim/fact → mart on subscription-app data (grain declaration, semi-additive facts, partition-level batches and idempotency, unique-key tests, late-arriving events and the reload window) |
| 12 | [We're Logging Events, So Why Can't We Get a Conversion Rate?](./chapters/12_were_logging_events_so_why_cant_we_get_a_conversion_rate) | Event taxonomy and log monitoring — build a daily event / property fill-rate mart, compare before and after a deploy (D-2 vs D-9) to catch missing events, duplicate firing, and missing values, and assemble a Slack report |

## 🤖 Practicing with Claude Code

This repository ships a [Claude Code](https://claude.com/claude-code) skill (`.claude/skills/da101/`).
Open Claude Code in the cloned folder and it is picked up automatically. You can use it like this:

- **Run & verify a chapter** — "run the MRR chapter", "the notebook errors out"
- **Apply to my data** — "decompose MRR from our service's payment log"
- **Method selection** — "DAU is flat, what should I look at first?"
- **QnA** — "what's the difference between GRR and NRR?"
- **Deep dive & quiz** — "check whether I understood this chapter"

You can also start with the `/da101` slash command instead of natural language. The first argument picks
the mode, and the rest is a chapter name, keyword, or question:

| Example | What it does |
| --- | --- |
| `/da101 DAU is flat, what should I look at first` | Find the right chapter from a business question |
| `/da101 run mrr` | Run and verify the chapter notebook (step-by-step walkthrough) |
| `/da101 apply decompose MRR from our payment log` | Apply the chapter's method to your own data |
| `/da101 qna difference between GRR and NRR` | Get a direct answer to a concept question (QnA) |
| `/da101 quiz lifetime` | Check your understanding with a deep dive and quiz |

Run it with no arguments to see the chapter list and the 5 modes and pick one.

To use it in your own project folder unrelated to the book, copy `.claude/skills/da101/` to `~/.claude/skills/`.
