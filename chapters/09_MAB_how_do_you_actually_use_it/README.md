# Chapter 9. MAB? How Do You Actually Use It?

Practice code for this chapter. We run **Thompson Sampling** (Bayesian, Beta distributions) for a Multi-Armed Bandit
as a hands-on simulation, and cover the complementary techniques you need when applying it to a real service
(banner click-through-rate optimization).

- **9.5.1.** Basic Thompson Sampling: how the Beta distributions converge and impressions concentrate on the best banner
- **9.5.2.** A/B test vs MAB: cumulative regret of a fixed-split A/B test vs MAB (putting a number on the cost of an experiment)
- **9.5.3.** α × Coefficient: separating the distributions of banners with similar, low CTRs with a coefficient
- **9.5.4.** Discounted Thompson Sampling: adapting to seasonality (an environment where the best option changes)

## How to run

```bash
jupyter notebook mab_thompson_sampling.ipynb   # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `mab_thompson_sampling.ipynb` | Notebook for 9.5.1-9.5.4 (Thompson Sampling simulation) |
| `requirements.txt` | Dependencies (numpy, scipy, pandas, matplotlib, jupyter) |

> This chapter has **no data files**. The banners' 'true probabilities' are set in code and the notebook runs the
> simulation itself, so you can watch the algorithm discover those probabilities step by step.
> Plot labels are in English and the simulation is reproducible via `np.random.seed(42)`.
