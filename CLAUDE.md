# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Practice code and example data for a **data-analysis book** (the English edition of [`duilee/data_analysis_101`](https://github.com/duilee/data_analysis_101), whose book was written in Korean). Each chapter is a self-contained, runnable teaching artifact — not production code. The audience is a reader following along with the book, so clarity and reproducibility matter more than abstraction or performance.

Section numbers that appear in notebooks and references (e.g. `10.7.2`) refer to the book's numbering. Chapter 10 (review text analysis) uses an English regex tokenizer with stop words and a negation marker where the Korean original used the `kiwipiepy` morphological analyzer; its review data is English synthetic text.

## Repository structure

- **All chapters live under `chapters/`, one folder per chapter**, named `NN_<english-title-slug>` — the chapter title in lowercase-ish snake case with punctuation dropped, prefixed by the zero-padded chapter number, e.g. `05_how_much_DAU_is_this_feature_worth/`.
- The top-level `README.md` holds a chapter index table; add a row when creating a new chapter.
- `.claude/skills/da101/` is a reader-facing Claude Code skill (method router + one `references/*.md` per chapter), also user-invocable as the `/da101` slash command. When adding or changing a chapter, update the skill's routing table and the matching reference file.
- `my-work/` (git-ignored) is where the reader-facing `/da101` skill writes everything it produces — executed notebooks, reader data, modified notebook copies, design docs, quiz session logs — mirrored as `my-work/<chapter folder name>/`. The skill never modifies chapter folders.
- A chapter folder contains: `README.md`, `requirements.txt`, a seeded `generate_data.py`, generated data in `data/*.csv`, optional `sql/*.sql`, and a Jupyter notebook that walks through the book's practice sections.

## Running / verifying a chapter

From inside a chapter folder:

```bash
python generate_data.py                                          # (re)generate data/*.csv
jupyter nbconvert --to notebook --execute --inplace <notebook>.ipynb   # run end-to-end
```

The notebook's first code cell installs deps via `%pip install -q -r requirements.txt`, so a reader does not run pip separately. **Always verify a chapter end-to-end before finishing**: run the generator, then execute the notebook and confirm exit 0 with no error outputs.

## Authoring conventions (important — these are deliberate teaching choices)

- **Synthetic data is generated from known parameters** (e.g. a planted power-law retention curve with chosen `a`, `b`), so the notebook's fitted results visibly recover the truth. This is the point — it lets the reader confirm the method works. Keep generators seeded for reproducibility.
- **Run SQL locally via DuckDB** on the committed CSV (`duckdb.query(sql).to_df()`), and **also show the SQL inline in a notebook cell** (as a `query = """ … """` string) so the reader sees the actual query, in addition to the standalone `sql/*.sql` file.
- **Keep example files self-contained.** Do NOT reference the original/real data source in chapter files — no BigQuery, real table names (e.g. `mart_user__active_daily`), `client.query`, or "original query" mentions. It must read as standalone example material.
- **Don't hardcode values that can only be known after running** (e.g. `curve_fit` `p0` initial guesses) — let defaults work, since the reader can't determine them up front.
- Use **`%pip`** (the kernel magic), not `!pip`, for in-notebook installs.
- **Plot labels and markdown narration are both in English.** Do not add non-ASCII font configuration to notebooks.
- **Keep chapter READMEs short**: title + 1-line intro, a brief practice summary (one bullet per practice section), a `## How to run` block, and a small `## Files` table. The conceptual theory lives in the book, not the README.
- **Chapter scope is decided per chapter** — don't assume a notebook must mirror every practice section of the book; confirm what to include.

## Git

Commit messages are written in English. Commit/push only when asked.
