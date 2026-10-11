# A/B Testing — Pitfall Simulations (wobble of chance · MDE · assignment balance · peeking)

**Chapter folder**: `chapters/03_p_is_0.049_so_we_can_ship_right/` · notebook: `ab_test_pitfalls.ipynb`
<!-- synced: code at duilee/data_analysis_101@226e1dd (Korean original) (2026-10-10) — cross-checked against the notebook and README; book text: cross-checked against the first proofread manuscript (2026-10-10, section layout: intro → 3.1 design (3.1.1–3.1.5) → 3.2 sample & MDE (3.2.1–3.2.3) → 3.3 analysis pitfalls (3.3.1–3.3.4) → 3.4 p-values (3.4.1–3.4.4) → 3.5 startups → 3.6 practice (3.6.1–3.6.5) → 3.7 Claude Code practice (3.7.1–3.7.5) → 3.8 wrap-up). Notebook section numbers match the book's 3.6.x. -->

## The problem this method solves

An A/B test result is not something you can trust just because it is significant. This chapter
reproduces the classic ways an experiment fools us — **the wobble of chance itself**, **too small a
sample (no MDE calculated)**, **accidental tilt in random assignment**, and **peeking (stopping midway
because it looks significant)** — through simulations with a planted answer (the true effect). The key
is to watch a "plausible win" get manufactured while knowing the effect is zero. Because the chapter's
core is conceptual explanation, the practice is **kept light, at a non-specialist's level** (3.6.2–3.6.5,
a single notebook; statistical formulas are hidden in helper functions and the meaning of constants is
moved into notes that explicitly say "you don't need to know the internals").

**Pointers into the book's theory sections** (in QnA mode, give the gist and refer to the relevant book
section for details):
- Intro — the starting point is a meeting that ends in 10 minutes with "p = 0.049, so ship it". A p-value
  is not a conclusion but one step in a verification procedure. Even organizations with a mature
  experimentation culture have a success rate of around 10% (Airbnb 92% failures, Bing 85%, Microsoft
  about 2/3) — and yet Airbnb got +6% booking conversion from the 20 wins out of 250. If more than half
  of our experiments succeed, that may be a signal of a hole somewhere in design or analysis.
- 3.1 Experiment design — correlation can be created by confounders, so causation needs an experiment
  (3.1.1; dark mode = heavy users, "problem experience" behind support tickets ↔ cancellations, reversed
  causal direction examples). Hypotheses written down to the target level (3.1.2, e.g. badge → annual
  subscription conversion +0.5%p or more), independent/dependent/control variables (3.1.3; control
  variable candidates = country, platform, subscription history, age; handled by stratified assignment or
  comparison at analysis time), random assignment is only fair on average → covariate imbalance →
  stratified assignment (3.1.4, 3.6.4), one success metric + guardrails (3.1.5). Required items of an
  experiment design doc: hypothesis (with target level), independent/dependent variables, control
  variables and how they are controlled, guardrails, sample size and duration.
- 3.2 Sample and MDE — an experiment is a measuring instrument with a resolution (3.2.1). The triangle
  of sample ↔ MDE ↔ duration: halving the MDE means about 4x the sample (+2%p in 2 weeks → +1%p in close
  to 8 weeks); compute it with a web calculator (Evan Miller) (3.2.2, 3.6.3). The seesaw between Type I
  (false positive, 5% significance level) and Type II error (80% power) — the only way to reduce both is
  more sample; with little traffic, use proxy metrics or A-B-A (3.2.3).
- 3.3 Analysis pitfalls — peeking and p-hacking (3.3.1, 3.6.5), trends over time and novelty/primacy
  (3.3.2), always check SRM (3.3.3, the 3.6.4 SRM cell; occurs in about 6% of Microsoft's experiments,
  causes fall into 4 stages: assignment, execution, log processing, analysis (post-hoc filters)),
  too-good results — check for bugs first (Twyman's law, 3.3.4).
- 3.4 Interpreting p-values — parameter vs statistic, null and alternative hypotheses (two-sided by
  default), the 3 big misconceptions (95% probability the effect is real X / 5% probability it is chance X
  / p = 0.001 means a big effect X), not significant ≠ no effect (presumption of innocence), 0.05 is just
  convention and p is a continuous measure of evidence strength (3.4.1, Table 3.1), size via confidence
  intervals (3.4.2), translating into business language (3.4.3, Tables 3.2 and 3.3), post-hoc segments
  are the next hypothesis (3.4.4; pre-registered hypothesis vs post-hoc exploration).
- 3.5 — 4 points for low-traffic startups: compute the MDE first and save experiments for bold changes,
  read small-sample wins conservatively (winner's curse), beware of contamination between experiments,
  an experiment may not be the best tool (call ten users; ship obviously-right improvements without an
  experiment and monitor guardrails).
- 3.8 Wrap-up — before/during/after checklist (see "Interpreting results" below), 3 limits of A/B
  testing: it is only local optimization within the given options (exploring options is chapter 9 MAB),
  results have an expiry date (re-run periodically for important questions), data-informed rather than
  data-driven (people decide). Next actions: adopt the checklist as a team process, change the reporting
  standard from significant-or-not to effect size and confidence interval, connect long-term impact to
  chapter 4 Lifetime.
- Book figures (for cross-checking): 1,000/day · 4% · 2 weeks → MDE ≈ 1%p; 184:216 tilt → 1.88% vs
  2.04%, about 1 in 10; peeking false-positive rate 26.1%; 5,200:4,800 probability about 0.006%;
  Table 3.1 badge experiment A 904 of 22,600 (4.0%) vs B 994 of 22,600 (4.4%), +0.4%p, p = 0.035,
  CI +0.03 to +0.77%p; Tables 3.2 and 3.3 (assuming an annual subscription fee of 30,000 KRW) 1,000/day
  +0.5%p → 55 million KRW a year, 5.5 billion KRW with 100,000/day, CI +0.2 to +0.9%p → 22 to 99 million
  KRW a year (compared with a 60 million KRW feature maintenance cost); testing 20 segments → probability
  of ≥1 false positive about 64%.

## Run and verify

```bash
jupyter nbconvert --to notebook --execute ab_test_pitfalls.ipynb \
  --output-dir ../../my-work/03_p_is_0.049_so_we_can_ship_right   # results go to my-work
```

- **This chapter has no data files, generator, or SQL.** The true conversion rate is fixed in code and
  the experiment itself is simulated (`np.random.seed(42)`). Skip the `generate_data.py` step.
- **Expected results** (the planted answer for each practice section):
  - 3.6.2: with the true conversion rate fixed at 4%, the observed conversion rate across 5 runs of
    10,000 users wobbles: 3.84% · 4.03% · 3.70% · 4.07% · 3.64% (384 · 403 · 370 · 407 · 364 users).
  - 3.6.3: `BASE_CVR=0.04`, `DAILY_PER_GROUP=500` — sample per group and duration by MDE: +3%p 903 users
    2 days, +2%p 1,861 users 4 days, **+1%p 6,744 users → about 14 days** (the book's "a two-week
    experiment's MDE ≈ 1%p"), +0.5%p 25,552 users 52 days. Halving the MDE (+2 → +1%p) means
    **about 3.6x** the sample (roughly 4x).
  - 3.6.4: 10,000 users split in half, 400 travel-ready users, conversion rates 25% vs 1%, banner effect 0
    — **with the 184:216 tilt, A 1.88% vs B 2.04% (+8.2%)**; in the apparent-lift histogram, "fake wins"
    of ±8% or more are **about 10%** (959 of 10,000, about one in ten). With stratified assignment
    (200:200) both groups are 1.96% and the difference vanishes. SRM is checked in a separate cell at the
    end of 3.6.4 with `stats.chisquare(observed, expected)` — for the example 5,000:4,500, p = 2.9e-07.
    The discussion of group "composition" imbalance (double-checking) is not in the notebook.
  - 3.6.5: 5,000 A/A experiments × 14 days — fixed-time test false-positive rate **5.5%**, with daily
    peeking and early stopping **22.4%** (it differs from the book's 26.1% because of the number of peeks
    and sample size — the notebook has a one-line explanation). The red lines in the trajectory chart are
    3 experiments that were significant at least once when checked daily (picked from those that dipped
    below 0.03 so they stand out in the chart; dot = first day below 0.05). For two of the three, p
    climbs back up and ends non-significant on day 14 — stopping on the day it dipped would have judged
    a non-significant experiment to be significant (the interpretation in book 3.6.5).

## Applying to your own data — interactive protocol

"Applying" this chapter means **designing and checking the reader's real experiment**: (A) before the
experiment — compute MDE and duration, (B) after the experiment — check assignment health (counts and
tilt). Proceed in the order 1 → 5 below.

### 1. Intake — what to ask the reader

- (Path A) What is the **current conversion rate** of the experiment's target metric and the **daily
  inflow (sample per group)**?
- What is the **minimum effect (MDE)** you want to detect? If the hypothesis has no target level, have
  them set one first.
- (Path B) What was the experiment's **designed assignment ratio** and the actual **sample size per
  group**?
- Is there a **rare but unusually high-converting user type** that strongly affects the result (whale
  users, users from a specific campaign, etc.)? What are its share and conversion level?
- What was the stopping rule for the experiment? Was it ever stopped or extended after looking at
  interim results?

### 2. Data checks

- (A) Compute `required_sample` with the intake values → if the projected duration exceeds 4 weeks,
  recommend a larger MDE or a higher-funnel metric (proxy metric) (the startup guide in book 3.5).
- (B) Confirm that the per-group sample sizes and the share of that user type are available as numbers.
  If the sample for a type is below a few dozen, explain that the balance check itself is unstable.

### 3. Code substitution map

| Anchor (section/identifier) | What | How |
| --- | --- | --- |
| 3.6.3 | `BASE_CVR`, `DAILY_PER_GROUP` | Replace with the reader's conversion rate and traffic (⚠ `DAILY_PER_GROUP` is reused in 3.6.5) |
| 3.6.3 | the constant `7.85` inside `required_sample` | Summary value of the 5% significance (two-sided) · 80% power convention: (1.96 + 0.84)² ≈ 7.85 — change only with a clear reason |
| 3.6.4 | `N_TOTAL`, `N_TRAVEL`, `CVR_TRAVEL`, `CVR_OTHER` | Replace with the reader's user-type share and conversion rates — reproduce "the apparent lift that tilt creates in our experiment" |
| 3.6.4 SRM cell | `observed` | Actual A:B counts from the logs — if the designed ratio is not 50:50, edit `expected` too |
| 3.6.5 | `N_SIM`, `DAYS`, `CVR` | Replace with the reader's experiment duration and conversion rate — what the false-positive rate becomes under peeking |
| 3.6.5 | `p_value(conv_a, conv_b, n_per_group)` | Plug in the actual cumulative conversions from the reader's experiment and it computes the p-value as is |

### 4. Step-by-step

1. (A) Build the MDE ↔ duration table with the reader's numbers using the 3.6.3 structure and
   translate it into "this experiment takes N days".
2. (B) Count check — if the designed ratio and actual sample sizes differ (SRM), have them stop
   interpreting results and find the cause first (the 4 stages in book 3.3.3: assignment logic bug or
   leftover assignment from a previous experiment / log loss from an error in a specific variant /
   missed joins or aggregations / the analyst's post-hoc filter). Entering the reader's counts into the
   3.6.4 SRM cell gives the p-value right away; note that the free web tools mentioned in book 3.3.3 are
   also sufficient.
3. (B) If there is a rare, high-converting user type, use the 3.6.4 structure to plot the distribution
   of "apparent lift that accidental tilt can create" and compare it with the observed lift. Recommend
   stratified assignment for the next experiment.
4. If the stopping rule involved peeking, use the 3.6.5 structure to estimate and show the actual
   false-positive rate of that rule.
5. Summarize the result not as "significant/not significant" but together with effect size and
   confidence interval (the interpretation frame in book 3.4).

### 5. Interpreting results

- (A) Summarize in the form "with this traffic, we cannot see anything below X%p → to run the
  experiment, either N days or a bolder variant".
- (B) Only after "counts match + user types balanced + stopping rule honored" are all confirmed do you
  move on to discussing effect size.
- Report effect size translated into business language (book 3.4.3, Tables 3.2 and 3.3): daily reach ×
  %p lift × revenue per conversion → additional annual revenue; convert the lower and upper bounds of
  the confidence interval separately and judge ROI by "does the worst-case scenario still exceed the
  maintenance cost?". Even if not significant, a large upper bound reads as "potential exists but the
  sample is insufficient".
- Review the whole experiment with the checklist in book 3.8 — **Before**: is this a question for an
  experiment (opinions diverge, hard to reverse, high impact) / target level in the hypothesis / one
  success metric + guardrails / control variables defined and applied / MDE calculated. **During**:
  check SRM / watch daily trends but no early stopping. **After**: if it is good enough to defy
  intuition, re-verify SRM, logging, and metric definitions / communicate with effect size and
  confidence interval / post-hoc segments become the next hypothesis.
- What to ask in the meeting instead of the p-value (book 3.8): What is the effect size? The confidence
  interval? The ratio of users in the two groups? The shape of the daily trend? Did we complete the
  originally planned duration? Will we ship even though it fell short of the hypothesis's target level
  (e.g. +0.5%p)? — the decision is made by people, not data (data-informed).

## Pitfalls

- The simulation's conversion-rate formula (`group_cvr`) is an **expected value**, so it has no binomial
  noise — a deliberate choice to reproduce the book's figures (1.88% vs 2.04%) exactly; real observed
  values wobble around them.
- In the 3.6.4 tilt case, the group sizes are exactly 5,000:5,000, so the count check (SRM) cannot
  catch it — SRM only looks at group "size"; "composition" (which users went in) must be checked
  separately. Because the SRM cell comes right after the stratified-assignment chart, it is easy to
  misread "SRM passed = no tilt". The notebook does not go deep into this distinction, so answer with
  this logic if the reader asks.
- The peeking false-positive rate depends on how often you look (daily, 14 times ≈ 22%; the extreme
  setting of testing every time a sample arrives is Evan Miller's 26.1% cited in the book). It is not
  "the number is different" but a difference in setup — if the reader asks why it differs from the
  book's 26.1%, answer with this logic (notebook 3.6.5 also has a one-line note: "because the number of
  peeks and the sample size are different").
- The 3.6.3 formula is a two-proportion z-test approximation (constant 7.85 = (z_α/2 + z_β)² rounded),
  so it can differ from calculators (Evan Miller etc.) by a few dozen users — not at a level that affects
  the decision.
- The notebook only deals with the cumulative summary metric (p-value) and **does not plot trends over
  time**. When interpreting a real experiment, you must check the trend chart for a pattern that leads
  big in the first week and then fades (novelty effect) and one that starts weak and widens later
  (primacy effect) (book 3.3.2) — the same p-value leads to different conclusions depending on the
  trend's shape.
- A result that is unbelievably good (+30%, +50%) is more plausibly explained by a logging, SRM, or
  metric-definition bug than by success (Twyman's law, book 3.3.4). Do not share it before re-verifying
  from design down to raw data.
- A significant result found by slicing segments after the fact may be a product of multiple testing —
  with 20 segments, the probability of at least one false positive is about 64% (book 3.4.4). Treat it
  only as a hypothesis for the next experiment, not a conclusion.
- A win that cleared the significance threshold on a small sample may be a "winner's curse" that passed
  only because positive noise was added (book 3.5) — read the effect size conservatively and don't be
  surprised if the metric doesn't move after launch.
- Do not read correlation in observational data as causation (book 3.1.1) — dark-mode users converting
  at 2x may be due to the confounder "usage intensity", and the causal direction may even be reversed.
  Verifying a growth lever needs an experiment.
- Write down ten dependent variables and one of them will go up by chance (book 3.1.5) — one success
  metric; manage the rest separately as guardrails (no launch if they worsen: crash rate, uninstall
  rate, refund rate, core funnel).
- With a very large sample, even a business-meaningless difference is "statistically" significant
  (book 3.4.3, 5.20% vs 5.25%) — significance and business impact are different concepts. Conversely,
  not significant ≠ no business effect.
- Winning an A/B test only means "B is better than A", not "B is the best" (book 3.8) — if the options
  themselves are poor, it is merely local optimization. Results have an expiry date: when the market,
  season, or user base changes, there is no guarantee last year's winner still wins this year.

## Study guide

### Core concepts — what you should be able to explain after finishing this chapter

- **The wobble of chance** — observed values differ every time even when nothing changes. Every pitfall
  starts with mistaking this wobble for an "effect".
- **MDE (minimum detectable effect)** — the resolution of this measuring instrument called an
  experiment. It must be computed before the experiment; "no significant difference" may mean "not
  visible at this resolution" rather than "no effect".
- **The sample ↔ MDE ↔ duration triangle** — halve the effect you want to detect and the sample is
  about 4x. The smaller the improvement, the more exponentially expensive it is to prove.
- **Random assignment ≠ balanced assignment** — random is only fair "on average". A user type that is
  small in number but unusually high in conversion can tilt by chance (on the order of one in ten), and
  stratified assignment prevents it at the design stage.
- **SRM (sample ratio mismatch)** — a gap between the designed ratio and the actual sample counts. A
  standing checklist item: count users before looking at conversion rates; if SRM is present, discard
  every result built on top of it.
- **Peeking / p-hacking** — a 5% significance level is a promise for testing "once, at a predetermined
  time". Watch and stop, and the false-positive rate exceeds the promise. Set the stopping time in
  advance and do not let people change it.
- **The meaning of a p-value** — the probability of observing a difference this large (or larger) by
  chance, assuming "no difference" (the null hypothesis). It is neither the probability the effect is
  real nor the probability the difference is chance, and a small p does not mean a big effect. When the
  effect is 0, p-values are spread uniformly — p = 0.04 is a value you get about 4 times in 100. The
  interpretation is asymmetric: a high p is not "no effect" but "this experiment failed to confirm it";
  a low p is evidence, not proof (the structure of the presumption of innocence). 0.05 is just a
  convention since Fisher — p = 0.049 and 0.051 are not different conclusions but evidence of similar
  strength (read it as a continuous value). The observed conversion rate is a statistic; the true value
  we want to know is a parameter.
- **Effect size and confidence intervals** — the p-value only answers "is it chance?"; "how different?"
  is answered by the confidence interval. Significant if it excludes 0, insufficient sample if it is
  wide. Report not significance but effect size and interval translated into business language (book
  3.4.2, 3.4.3).

### Concept check

Scope (the 5 questions promised by the book): the wobble of chance, MDE and sample size, random vs
stratified assignment, SRM, peeking, the meaning of a p-value.

1. The experiment ended with "no significant difference". Why shouldn't you read that as "no effect"?
   - Hint: MDE — with too small a sample, even a real effect sits below the resolution and stays
     invisible (book 3.2.1). Point to the rows in the 3.6.3 table where the duration falls short.
2. The banner effect was 0, yet variant B looked like it won by +8%. What is the culprit, and how can
   you prevent it in the next experiment?
   - Hint: accidental tilt of travel-ready users (rare, high-converting) — covariate imbalance;
     stratified assignment splits that type in half first (book 3.1.4).
3. What is the difference between "looking at the dashboard every day" and "peeking"?
   - Hint: the problem is not looking but "looking, stopping, and concluding". Looking in order to
     monitor SRM and bugs is actually encouraged. Set the stopping time in advance and do not let people
     change it (book 3.3.1).
4. An experiment designed as 50:50 ended with 10,000 users split 5,200:4,800. Can you wave it off as
   "within the margin of error" and move on to comparing conversion rates?
   - Hint: SRM — the probability of this ratio occurring by chance is 0.0066%. No need to even look at
     conversion rates; stop interpreting results and find the cause across the assignment, execution,
     log-processing, and analysis stages (book 3.3.3). Entering the counts into the 3.6.4 SRM cell gives
     the p-value right away.
5. What is wrong with "p = 0.049, so there's a 95% probability the treatment is better than the
   control"? Then what do you use to answer "how big is the difference"?
   - Hint: a p-value is the probability of a difference this large arising by chance under the
     "no difference" assumption, not the probability the effect is real. Size and uncertainty are stated
     with a confidence interval (book 3.4.1, 3.4.2).

### Advanced exercises

1. **[Sandbox]** Have the reader predict whether changing `N_TRAVEL = 400` in 3.6.4 to `4,000` (40% of
   the total) makes the apparent lift bigger or smaller → edit → re-run → compare. (The goal is the
   intuition that when the type is not rare, the relative tilt is smaller and so is the distortion.)
   Restore the original value afterwards.
2. **[Sandbox]** In 3.6.5, predict the false-positive rate of the rule "don't look for the first 7 days,
   then check daily from day 8" → compute with `(daily_pvals[:, 7:] < 0.05).any(axis=1)` → compare with
   daily checking (22.4%). Internalize the structure: the later and less often you look, the closer the
   false-positive rate gets to 5%. Restoring the original is required.
3. **[Think]** Traffic is low, and computing the MDE gives +5%p over 4 weeks. Have the reader lay out
   the options this organization has, grounded in book 3.2.3 and 3.5. (Saving experiments for bold
   variants, proxy metrics, A-B-A, etc. — discuss the cost of each choice as well.)
