# Chapter 10. Reading the 'Why' That Numbers Don't Tell You

Practice code for analyzing e-commerce product reviews (qualitative data). It compares what words
5-star (satisfied) and 1-star (dissatisfied) reviews are written in through several lenses, and
finishes by going back to the original reviews to check.

- **10.7.2. Preprocessing and tokenization** — regex tokenization with English stop words and a `not_` negation marker
- **10.7.3. Text frequency analysis** — word-frequency tables and word clouds: which words appear a lot
- **10.7.4. Text weighting analysis** — unique keywords (shared words removed), TF-IDF, log-odds ratio z-score: the words that separate the two groups
- **10.7.5. Word association and network analysis** — bigrams, co-occurrence network graph
- **10.7.6. Topic modeling (LDA)** — top words per topic, topic share per review, topic time series
- **10.7.7. Checking the concrete context in the original text** — KWIC, reading representative reviews per LDA topic
- **10.7.8. What positive reviews reveal** — reading use cases and customer segments you never knew about from the 5-star co-occurrence network

## How to run

```bash
python generate_data.py                       # generate the example data (data/reviews.csv)
jupyter notebook review_analysis.ipynb        # run the notebook top to bottom (the first cell installs dependencies)
```

## Files

| File | Description |
| --- | --- |
| `generate_data.py` | Synthetic review generator with vocabulary differences planted per rating |
| `data/reviews.csv` | Product reviews (`review_id, product_id, rating, text, created_at`) |
| `review_analysis.ipynb` | Practice notebook for 10.7 (10.7.1-10.7.8): preprocessing → frequency → weighting (distinctive keywords) → networks → topics → back to the original text → rediscovering positive reviews |

> The embedding clustering (`sentence-transformers`) and LLM coding in the book need heavy
> dependencies or API keys, so they are left out of the notebook; going back to the original text
> is done by picking representative reviews from LDA topic shares instead.
