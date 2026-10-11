# Chapter 3. p = 0.049, So We Can Ship, Right?

Practice code for this chapter. Rather than showing how to run an A/B test, this practice lets you
see with your own eyes, through simulations with a planted answer (the true effect), **the pitfalls
that let A/B test results fool us**. It is designed to be followed lightly, without knowing the
statistical details.

- **3.6.2.** Coin flips - the numbers wobble even when nothing changes (warm-up on the wobble of chance)
- **3.6.3.** How many days do we need to run this? - how a sample size calculator works (required sample and duration per MDE)
- **3.6.4.** We split randomly, so why isn't it fair? - an accidental tilt of travel-ready users, and stratified assignment
- **3.6.5.** Day 3, the dashboard says p = 0.04 - how peeking inflates fake wins

## How to run

```bash
jupyter notebook ab_test_pitfalls.ipynb   # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `ab_test_pitfalls.ipynb` | Practice notebook for 3.6 (3.6.1-3.6.5) (A/B testing pitfall simulations) |
| `requirements.txt` | Dependencies (numpy, scipy, pandas, matplotlib, jupyter) |

> **This chapter has no data files.** The "true value" of the conversion rate is fixed in code and the
> experiment itself is simulated, so you can watch how an experiment fools us while knowing the effect
> is zero. Plot labels are in English and the run is reproducible with `np.random.seed(42)`.
