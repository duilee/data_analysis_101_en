# MAB — Thompson Sampling Simulation and Practical Refinements

**Chapter folder**: `chapters/09_MAB_how_do_you_actually_use_it/` · Notebook: `mab_thompson_sampling.ipynb`
<!-- synced: code at duilee/data_analysis_101@`8e8b97c` (2026-09-13) (Korean original) — cross-checked against the notebook and README; book text: cross-checked 2026-09-26 (manuscript section layout: section 1 intro → section 2 drawbacks of A/B testing (2.1, 2.2) → section 3 what is MAB (3.1-3.3) → section 4 applying it in practice (intro, 4.1-4.4) → practice 0-3 → Claude Code practice → wrap-up). -->

## The problem this method solves

A fixed-split A/B test spends traffic on inferior variants for the entire experiment period. The Multi-Armed
Bandit's **Thompson Sampling** (Beta-Bernoulli Bayesian) gradually shifts traffic to the variants that look
better while still exploring, which reduces the cost of experimentation (cumulative regret). It is the right tool
for optimizations where "converging on a good variant quickly" is all you need: banners, copy, recommendation slots.

**Pointers to the book's theory sections** (details are in the book; only the gist here)

- **Introduction** — The author's experience that bringing a technique you have learned (MAB) into practice takes an
  adoption strategy and the right moment: the right problem and the right colleagues. → Book 9.1.
- **Where MAB sits** — Unlike a fixed-split A/B test, it reallocates traffic to the better-performing variants in real
  time; neither is strictly superior, and MAB is an alternative that compensates for the limits and opportunity cost of
  A/B tests. Deeper theory is left to the external course the book recommends. → Book 9.2 intro. Uses at Netflix, Google
  and others are mentioned at the end of 9.2.2.
- **Two drawbacks of A/B testing** — (1) Experiment cost: a fixed share of traffic is tied up in inferior variants, so
  opportunity cost accumulates, and as the number of experiments grows so does the operational and management cost
  (Table 9.1: control 5% / variant A 7% / variant B 1%, 33% each — the scenario in 9.5.2 is this table). (2) Responding
  to change over time: the test runs for a fixed period and then ends, so it cannot reflect seasonality or shifts in
  taste. → Book 9.2.1, 9.2.2.
- **MAB and explore & exploit** — The slot-machine etymology, and the decision problem of "how much to explore while
  maximizing what you harvest." An A/B test is interpreted as the strategy "explore briefly, then exploit a fixed winner
  forever." Other frameworks such as Epsilon-Greedy and UCB get a one-line introduction each. → Book 9.3.1, 9.3.2,
  9.3.3 intro.
- **Thompson Sampling = the probability of a probability** — The reward probability is held not as a single number but
  as a Beta(α, β) distribution, updated with α = number of rewards and β = number of non-rewards (thanks to conjugacy,
  by addition alone). As observations accumulate the variance shrinks and density gathers near the true probability,
  while a wide (uncertain) variant occasionally draws a large sample and thus gets a chance to be explored. → Book
  9.3.3, Figures 9.2-9.4.
- **Four practical refinements** → Book 9.4. The two warnings in the intro (guardrail metrics, checking traffic volume)
  are covered under Pitfalls below. The intro also points out the prerequisite infrastructure: a system that creates and
  updates the per-banner Beta parameters plus impression/click logging must come first, and near-real-time is best
  (the rationale for intake path B). 9.4.1-9.4.4 correspond to Figures 9.5-9.7.
  9.4.1 Delayed learning — update in batches (100 or 1,000 events), sample once per session and set the exposure order
  by the "ranking of the sampled values." 9.4.2 α × Coefficient — per click, add a coefficient such as 10 or 15 to α to
  spread overlapping distributions apart (2.0% vs 1.5% → roughly 20% vs 15%; the estimates are inflated but that is
  fine as long as the ranking is preserved). 9.4.3 Discounted TS — each period multiply α and β by a factor below 1
  (e.g. 0.8 per day) to lower the weight of the past (the weight of 20 days ago is 0.8^20 ≈ 0.012); the variance widens
  again and re-exploration happens. 9.4.4 Forcing a fixed exposure rank — banners that must be guaranteed exposure, such
  as direct ad deals, are pinned in the admin tool and MAB is applied only to the remaining slots.
- **Wrap-up** — The fixes for the two drawbacks (traffic to inferior variants during the experiment, no response to
  change after it ends) are TS plus Discounted TS, α adjustment and near-real-time batching. But MAB is not a
  replacement for A/B testing (convergence ≠ estimation). The reward must be a metric observed immediately; for delayed
  metrics such as payment or retention, pick a proxy metric first. It closes with the advice that an organization with
  low data maturity should wait for the right moment to adopt it.
- **Summary table row** — "Can we keep optimizing while operating without A/B tests?" / Situation: a banner area that
  needs continuous management — running an experiment every time a variant changes wastes traffic and time → automate
  the impression-reward loop with Thompson Sampling and tune convergence speed and responsiveness to change with the
  coefficient and discounting; Caution: monitor guardrail metrics separately, convergence ≠ estimation; Next action:
  choose the coefficient and discount factor by simulation, then apply them in the pipeline; revisit the discount factor
  when seasonal shifts appear.

## Running and verifying

```bash
jupyter nbconvert --to notebook --execute mab_thompson_sampling.ipynb \
  --output-dir ../../my-work/09_MAB_how_do_you_actually_use_it   # results go to my-work
```

- **This chapter has no data files, generator, or SQL.** The banners' 'true probabilities' are set in code and the
  notebook runs the simulation itself (`np.random.seed(42)`). Skip the `generate_data.py` step.
- **Expected results** (the planted answers per practice section — numbers in parentheses are the output at seed 42 as
  printed in the notebook and in the book's practice section. As of 2026-09-26 the notebook outputs and the manuscript
  numbers all match):
  - 9.5.1: `BANNER_PROBABILITIES = [0.2, 0.5, 0.75]`, `NUM_TRIALS = 2000` — the Beta distributions narrow and
    impressions concentrate on the 0.75 banner (observed in a 2×3 panel at `checkpoints = [5, 20, 100, 500, 1000, 1999]`).
    In the middle, impressions alternate between the 0.5 and 0.75 banners before concentrating on 0.75 later.
    (`total reward earned: 1516.0`, `overall win rate: 0.758`, `times each selected: [4, 64, 1932]`)
  - 9.5.2: `PROBS = [0.05, 0.07, 0.01]` — `run_ts`'s cumulative regret is clearly lower than `run_ab`'s.
    (`AB total reward: 77`, `MAB total reward: 118`)
  - 9.5.3: `CTR = [0.009, 0.006, 0.003]`, `IMPR = 1000` → expected clicks under equal exposure `wins = [9, 6, 3]` — left
    alone, the Beta distributions overlap and impressions leak to the 2nd- and 3rd-ranked banners; applying the
    coefficient via `make_beta(coef)`/`exposure_share(15)` separates them faster.
    (exposure % — `plain (coef=1): [75.4, 21.7, 3.0]`, `coef=15: [99.8, 0.2, 0.0]`)
  - 9.5.4: `SCHED` (`[0.6, 0.3, 0.1]` for i<1000, then `[0.1, 0.3, 0.6]` — the optimal arm flips), `N4 = 2000`,
    rolling window `w = 100` — reusing `run_ts` from 9.5.2, Discounted TS run as
    `run_ts(SCHED, N4, gamma=0.9)` (`decay_every` at its default 50) switches to the new optimal arm, unlike plain TS.
    (`phase 2 reward — plain: 367, discounted: 510`)
- **Suggested variations after running**: it is a simulation, so re-running is free. Once the walkthrough is done,
  suggest changing `PROBS` (the true probabilities), the coefficients in 9.5.3 (`[1, 15]`) and `gamma` in 9.5.4 and
  re-running — the book frames this chapter as a practice in "changing conditions and comparing results."

## Applying it to my data — interactive protocol

"Applying" this chapter has two paths: **(A) pre-validate your own situation by simulation**, **(B) connect real
impression/click logs as the prior**. Proceed in order 1→5 and confirm each step's result with the reader.

### 1. Intake — what to ask the reader

- What is being optimized? (banners / copy / recommendation slots, etc.) **How many arms**?
- How is the reward defined? Is it a binary metric observed immediately (e.g. a click)? If it is a delayed metric
  (retention after sign-up), first explain that this method must not be used as-is (see Pitfalls).
- What is the expected CTR level and the gap between arms, and what is the **daily traffic** (impressions)? (e.g. 1% vs
  0.8% — the lower and closer they are, the more traffic is needed. This is also where to judge whether the coefficient
  trick from 9.5.3 is needed.)
- (Path B) Are there logs of **cumulative impressions and clicks per variant** in production? Is per-arm attribution
  accurate? If so, go beyond simulation to Beta initialization → a recommended exposure split.
- (If relevant) Are there factors that change the optimal arm over time (seasonality, creative fatigue)? → the 9.5.4 path.

The intake in the book's Claude Code practice section follows the order of items 1-4 above (target & arm count /
reward definition / CTR & daily traffic / existing logs).

### 2. Data check — validating the simulation design

- (A) Build a simulation parameter table from the intake values and confirm it with the reader: number of arms,
  probability array, number of trials (= daily traffic × expected days of operation).
- (B) For impression/click logs: confirm ≥ several hundred impressions and ≥ 1 click per arm. Explain that an arm
  with 0 clicks has a near-uniform prior and will take a long time to explore.

### 3. Code substitution map

| Anchor (practice / identifier) | What | How |
| --- | --- | --- |
| 9.5.1 | `BANNER_PROBABILITIES`, `NUM_TRIALS`, `checkpoints` | Use the reader's arm count, expected CTRs and traffic |
| 9.5.2 | `PROBS`, `N` | The reader's scenario — used to show the savings vs A/B as a number |
| 9.5.3 | `CTR`, `IMPR`, coefficients — two places: the plot loop `zip(axes, [1, 15], [0.03, 0.25])` (coefficient paired with x-axis upper limit) and `exposure_share(15)` in the print | Only needed when CTRs are low and close together. Start the coefficient at 1 (no effect) and raise it |
| ⚠ 9.5.4 | The switch point `1000` appears in **three places: the `SCHED` lambda, `plt.axvline(1000 - w // 2)`, and the phase 2 aggregation `r_plain[1000:]`/`r_disc[1000:]`** | Change all three together when moving the switch point |
| 9.5.4 | `gamma=0.9`, `decay_every` (not passed in the call — `run_ts` default 50) | Match the cadence of change — the shorter the cycle, the lower gamma, or pass it explicitly as `run_ts(SCHED, N4, gamma=0.9, decay_every=…)` and reduce it |
| Arm count | `run_ts` infers the arm count via `k = len(sched(0))` | Just change the length of `PROBS`/`SCHED` — nothing else is hardcoded |
| (Path B) `Banner` class (9.5.1) · `a = np.ones(k); b = np.ones(k)` in `run_ts` (9.5.2-9.5.4) | Initial prior values | Initialize as `Beta(1+clicks, 1+impressions−clicks)` to reflect existing data — for the 9.5.2-9.5.4 path, replace the two arrays inside `run_ts` with prior arrays |

### 4. Step-by-step

1. Run the 9.5.1 structure on the reader's scenario to find the convergence point → translate into "about N days at
   our traffic."
2. Use the 9.5.2 structure for the cumulative regret gap vs A/B → translate into "we would have thrown away X clicks
   with an A/B test."
3. If CTRs are low and close, run the 9.5.3 coefficient experiment → compare `exposure_share` per coefficient and pick
   a suitable one.
4. If there are factors that change over time, tune gamma and decay_every with the 9.5.4 structure.
5. (Path B) Draw the current Beta distributions from the real-data prior and produce a recommended exposure split for
   "how to divide traffic right now."

### 5. Interpreting the results

- Summarize the simulation conclusion in the form "with this setup, convergence within N days, regret M lower than A/B."
- Explain that even after convergence, exploration never drops fully to zero (uncertainty is maintained).
- Translate into next actions (book summary table): apply the coefficient and discount chosen by simulation in the
  pipeline, and revisit the discount factor when seasonal shifts appear. The coefficient and discount are pipeline
  settings, not values you set once and forget.

## Pitfalls

- MAB does not tell you "why it won" — if the goal is effect-size estimation or causal interpretation, use an A/B test.
  Use MAB when the goal is convergence (convergence ≠ estimation — book summary table).
- **It maximizes a single reward metric only** — with CTR as the only reward, a clickbait banner can become the winner.
  Separate monitoring that guardrail metrics such as purchase conversion and churn do not deteriorate is mandatory
  (book 9.4 intro).
- **Check traffic volume first** — at a CTR of 1-2%, the distributions need at least tens of thousands of impressions
  to converge. With hundreds to a few thousand impressions per day, convergence takes weeks or more and MAB's advantage
  evaporates, so estimate the expected time to convergence up front from expected CTR and daily traffic (book 9.4 intro
  — the rationale for intake question 3).
- Using it as-is on a metric that is not observed immediately (e.g. D7 retention) distorts convergence through feedback
  delay. It suits proxy metrics observed immediately (clicks) (book wrap-up).
- With α × Coefficient the posterior mean is no longer the real CTR — it is for ranking comparison and must not be
  reported as a CTR estimate (book 9.4.2). Multiplying online on every impression can lock in early luck, so apply it
  on top of batch aggregates (notebook 9.5.3 narrative — pairs with batch updates in book 9.4.1).
- The A/B simulation in 9.5.2 keeps an equal split for all 2,000 trials — a real A/B test sends traffic to the winner
  after it ends, so read the regret gap as the cost 'during the experiment period'. That cost accumulates as the number
  and repetition of experiments grow (book 9.2.1).
- Plain TS that only accumulates keeps a banner whose season has passed on top by inertia — for a placement where the
  optimum changes, design in discounting (Discounted TS) from the start (book 9.4.3).
- It assumes per-arm attribution in the impression/click logs is accurate.

## Learning guide

### Core concepts — what you should be able to explain after this chapter

- **Exploration-exploitation trade-off** (the book's term: explore & exploit) — the balancing problem between learning
  more (exploring) and using the best you know (exploiting/harvesting). An MAB algorithm automates this balance.
- **Beta-Bernoulli conjugacy** — the structure by which, as click/no-click (Bernoulli) observations accumulate, the
  posterior is updated in closed form as Beta(successes+α, failures+β). The single line `Banner.update()` is exactly that.
- **Thompson Sampling** — draw **one sample** from each arm's posterior and show the arm with the largest. Uncertain arms
  occasionally sample high and are explored naturally.
- **Cumulative regret** — the running total of "reward lost compared with showing only the optimal arm." The unit of an
  algorithm's cost.
- **Non-stationary environment** — one where the true probabilities change over time. Past data must be discounted to
  adapt. Book terms: discount factor, discounted Thompson Sampling; the coefficient in 9.5.3 is the weight coefficient.

### Concept check

Each question maps to one of the five concepts the book lists as the review scope for this chapter
(exploration-exploitation trade-off, Beta-Bernoulli conjugacy, Thompson Sampling, cumulative regret, non-stationary
environments and discounting).

1. In Thompson Sampling, what exactly is being "sampled," and how does that automatically produce a balance between
   exploration and exploitation?
   - Hint: one sample from each arm's posterior (Beta) — a wide (uncertain) arm occasionally draws a value above its
     expectation, becomes the maximum and gets shown (exploration), while a narrowed high-performing arm reliably draws
     large values and keeps being chosen (exploitation).
2. What is cumulative regret, and why does an A/B test's cumulative regret grow linearly?
   - Hint: the running total of "expected reward missed compared with showing only the optimal arm." An A/B test shows
     inferior arms at a fixed ratio until the end → a constant loss accrues every trial. (Also note the caveat that the
     9.5.2 simulation keeps an equal split for all 2,000 trials, so this is the cost 'during the experiment period'.)
3. In Beta(α, β), what do α and β each count, how does the distribution change as observations accumulate, and why is
   the update finished "by addition alone"?
   - Hint: α = number of rewards (+1), β = number of non-rewards (+1). The mean α/(α+β) represents the reward rate, and
     as α+β grows the variance shrinks and the distribution sharpens around the true probability. Thanks to conjugacy,
     the posterior of Bernoulli observations closes back into a Beta — `a += x; b += 1 - x` in `Banner.update()` is
     exactly that.
4. In Discounted TS, what happens to the distribution when α and β are multiplied by a factor below 1 each period, and
   why is that an advantage in an environment where the best banner changes?
   - Hint: the parameters shrink and the variance widens again → an arm that had been eliminated can sample high again
     and is re-explored. The weight of the past decays exponentially (e.g. at 0.8/day, 20 days ago ≈ 0.012). Pure
     accumulation leaves the past winner on top by inertia (the phase 2 reward gap in 9.5.4).
5. For which decisions should you use an A/B test instead of MAB?
   - Hint: MAB's goal is convergence, A/B's goal is estimation. Decisions that need an effect size and confidence
     interval (price changes, large redesigns) — MAB concentrates traffic, so estimates for inferior arms become
     inaccurate. Whether the reward is observed immediately and whether guardrail metrics can be watched separately are
     criteria too.

### Advanced exercises

1. **[Sandbox]** Change `PROBS = [0.05, 0.07, 0.01]` in 9.5.2 to `[0.06, 0.07, 0.01]`, halving the gap between 1st and
   2nd place, and have the reader predict roughly how many times more trials TS will need to break away from the
   runner-up → edit → re-run → compare regret curves. (The target intuition: halving the gap Δ means roughly 4× the
   required samples.) Restore the original value afterwards.
2. **[Sandbox]** Move the switch point in 9.5.4 from `1000 → 200` (⚠ all three places together: `SCHED`, `axvline`,
   phase 2 aggregation), leave `decay_every` at its default 50, and predict whether Discounted TS will still adapt well →
   run → compare → adjust `gamma`/`decay_every` (passed explicitly in the call) to make it adapt. Internalize "the fit
   between the cadence of change and the discount period." Restore afterwards.
3. **[Thinking]** If banner A is optimal in the morning and banner B in the evening, is Discounted TS enough? What
   structure would be better? (Lead toward the contextual bandit idea of conditioning on context — start the discussion
   with independent TS per time slot.)
