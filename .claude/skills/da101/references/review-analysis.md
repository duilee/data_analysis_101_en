# Review analysis — reading the Why that numbers don't tell you

**Chapter folder**: `chapters/10_reading_the_why_that_numbers_dont_tell_you/` · notebook: `review_analysis.ipynb`
<!-- synced: code at duilee/data_analysis_101@226e1dd (Korean original); book text: checked against the first proofread manuscript (2026-10-10, section layout: intro → 10.1 frequency (table 10.1, fig 10.1) → 10.2 weighting (10.2.1-10.2.3, fig 10.2, table 10.2, fig 10.3) → 10.3 association & networks (10.3.1-10.3.2, table 10.3, figs 10.4-10.5) → 10.4 topics & meaning (10.4.1 LDA fig 10.6, table 10.4, fig 10.7; 10.4.2 sentiment / embeddings / LLM 10.4.2.1-10.4.2.3) → 10.5 original context (tables 10.5-10.6) → 10.6 positive reviews (fig 10.8) → 10.7 practice 10.7.1-10.7.8 (Python, table 10.7) → 10.8 practice 10.8.1-10.8.5 (Claude Code) → 10.9 wrap-up). KWIC is the DataFrame-table version. English edition: the dataset is English synthetic reviews and the kiwipiepy morphological analyzer is replaced by regex tokenization with English stop words and a negation marker; expected results below come from the executed English notebook. -->

## The problem this method solves

Metrics tell you "what dropped" but not "why". We compare the language of the 5-star (satisfied)
and 1-star (dissatisfied) groups of e-commerce product reviews (qualitative data) through several
lenses, and always go back to the original text to check:

10.7.2 preprocessing and tokenization (regex tokenization with English stop words and a negation
marker) → 10.7.3 frequency and word clouds → 10.7.4 weighting (unique keywords, TF-IDF, log-odds
ratio z-score) → 10.7.5 context and relations (bigrams, co-occurrence network) → 10.7.6 topic
modeling (LDA, topic time series) → 10.7.7 back to the original text (KWIC, representative review
per topic) → 10.7.8 rediscovering positive reviews.

**Pointers to the book's theory sections** (direct the reader to the book for detail; notebook section
numbers follow the book's practice sections, so they differ from the theory numbers — theory 10.1 ↔
10.7.2-10.7.3, 10.2 ↔ 10.7.4, 10.3 ↔ 10.7.5, 10.4 ↔ 10.7.6 (10.4.2 only as the `[notebook extra]` note at
the end of 10.7.6), 10.5 ↔ 10.7.7, 10.6 ↔ 10.7.8)

- **Intro** — quantitative data answers 'What & How many'; qualitative data (reviews, testimonials,
  one-liners, CS inquiries, surveys, app-store reviews, interviews) answers 'Why & How'. Qualitative
  data is unstructured, subjective and voluminous (nobody reads 100,000 reviews), hence the need for
  a systematic method.
- **10.1 Text frequency analysis** — tokenize (a morphological analyzer for Korean, a regex
  tokenizer with stop words for English), then count per group (table 10.1) and draw word clouds
  (fig 10.1). Limitation: words that appear on both sides, like 'size / design / material', cannot
  be interpreted.
- **10.2 Text weighting analysis** — 10.2.1 unique keywords (remove words shared by both sides, fig
  10.2) → 10.2.2 TF-IDF (table 10.2; it measures 'which words matter within a review', not what
  separates the two groups) → 10.2.3 log-odds ratio (odds → odds ratio → log for symmetry; diverging
  bars fig 10.3; z-score standardization to stop rare words from being overrated).
- **10.3 Word association and networks** — 10.3.1 bigrams (table 10.3, fig 10.4; restore context
  like 'size → small', but only consecutive words) → 10.3.2 co-occurrence network (fig 10.5; word
  pairs within the same review; raw counts give a hairball, so link strength is measured with PMI).
  How to read it: hub = improvement leverage, cluster = category. Bigrams give 'order (the flow of
  expression)', co-occurrence gives 'grouping (theme clusters)' — use them as complements.
- **10.4 Topics and meaning** — 10.4.1 LDA topic modeling (fig 10.6 top words per topic, table 10.4
  topic share per review, fig 10.7 topic share over time). 10.4.2 sentiment analysis (ABSA,
  10.4.2.1), embeddings (10.4.2.2) and LLMs (10.4.2.3) are introduced only.
- **10.5 Checking the original context** — three reasons to go back to the original text (verify
  the signal, capture context, restore nuance). KWIC (table 10.5; literal matching, so 'return' must
  be searched separately from 'refund') and representative reviews per topic (table 10.6).
- **10.6 What positive reviews reveal** — complaints are flat, satisfaction is multi-dimensional.
  The 5-star co-occurrence network (fig 10.8) reveals a use case nobody planned (camping / car
  camping) and a customer segment (pet owners) → rewrite copy, product variants, channel expansion.
- **10.8 Practice (Claude Code)** — 10.8.1 fetch the repository → 10.8.2 run · 10.8.3 apply · 10.8.4 qna · 10.8.5 quiz.
  `/da101 run|apply|qna|quiz review analysis` or natural language ("let's work through the review analysis practice").
- **10.9 Wrap-up** — the techniques and their order are only an example: CS inquiries or surveys
  change the preprocessing, another language changes the tools, hundreds of thousands of rows
  change topic counts and thresholds. Embeddings and LLMs are fast becoming the standard, so tools
  will change, but the core is the 'analytical eye' that goes beyond fixing complaints to find
  hidden strengths and new targets in the context of satisfaction. (There is no summary table.)

## Run and verify

```bash
python generate_data.py      # creates data/reviews.csv
jupyter nbconvert --to notebook --execute review_analysis.ipynb \
  --output-dir ../../my-work/10_reading_the_why_that_numbers_dont_tell_you   # results go to my-work
```

- Input (book table 10.7): `data/reviews.csv` (`review_id, product_id, rating, text, created_at`).
- **Expected results**: the generator plants vocabulary differences per rating (complaints:
  delivery / quality / refund scenarios; satisfaction: usage scenarios), so the distinctive keywords
  and LDA topics must recover that planted split. Reference numbers from the notebook output
  (reproducible with the pinned version): load `total: 1020 | 5-star: 450 | 1-star: 450`; frequency
  #1 5★ `size · 291` / 1★ `refund · 355` (5★ #2-4 camping 253 · small 236 · space 236, 1★ #2-4
  material 174 · size 171 · packaging 169); unique keywords 5★ `camping · space · fur · studio · pet ·
  apartment · cleaning · dog · recommend · car`, 1★ `refund · flimsy · mess · delayed · letdown ·
  not_buying · disappointed · different · photo · not_response` (ties may swap order); TF-IDF #1 5★
  `camping 0.106` / 1★ `refund 0.194` (#2 space 0.101 / flimsy 0.099); log-odds z extremes `refund
  -17.2` / `camping 8.8`; 1★ bigram #1 `different→photo 94`, #2-5 `refund→request 66` ·
  `request→not_response 66` · `material→flimsy 66` · `packaging→mess 63`; 1★ co-occurrence network
  `36 words · 40 edges · 8 clusters` (design·color·different·photo·ugly·weird·tacky·dull /
  packaging·flimsy·mess·cancellation·damaged·sloppy / delivery·delayed·week·forever·slow /
  refund·inquiry·contact·silent / price·not_justified·not_worth·expensive / size·small·not_fit·baggy /
  material·rough·cheap / not_response·request); LDA 5 topics whose top words split into
  (small·space·studio·apartment), (camping·portable·car·lightweight), (recommend·dog·fur·pet·owners),
  (refund·design·material·size·packaging) and one mixed topic led by `okay` (the 2-4 star 'just okay'
  reviews plus the 'backpack' camping phrase); topic-share examples 97% / 95% / 49%·48%;
  representative review shares 96 · 97 · 96 · 95 · 93%; KWIC 'refund' table (left context · keyword ·
  right context, 8 rows) first row `…ive for what it is, | refund | request got no resp…`; 5★
  co-occurrence network `22 words · 48 edges · 3 clusters`
  (space·small·studio·apartment·not_crowd·little·perfect·hardly / fur·pet·cleaning·dog·hygienic·not_cling·not_stick /
  camping·car·portable·lightweight·outdoor·outdoors·light). Topic **numbers and order** can differ by
  environment, so judge by the top-word groups.
- **Caution (version-sensitive)**: `scikit-learn==1.9.0` is pinned. TF-IDF and LDA results change
  between versions, so **if the reader's results differ from the book, check this package version
  first**. (The tokenizer is plain regex + a stop-word list, so it has no version dependency.)
- This is the only chapter with a data file that does not use DuckDB / SQL (pandas directly). The
  sentiment analysis, embeddings and LLM of book 10.4.2 have no code in the notebook because of
  heavy dependencies / API keys; they are introduced only in the `[notebook extra]` cell at the end
  of 10.7.6 — if the reader asks, say so and point them to book 10.4.2.

## Apply to my data — interactive protocol

Proceed in order 1→5. Show the reader the result of each step and confirm before moving on.
This is the chapter with the most `[Apply to my data]` comments in the notebook (10 spots) — follow them.
The group definition lives in one place (the load cell) and every later lens reuses its result (`pos`/`neg`).

### 1. Intake — what to ask the reader

- The **file path** of the text data? (app-store reviews, CS inquiries, NPS free text, open survey answers all work)

| Role (notebook example name) | Type | Meaning | Required |
| --- | --- | --- | --- |
| `text` | TEXT | the text to analyze | required |
| `rating` | INT etc. | the axis that splits the groups | required* |
| `created_at` | DATE | when it was written (for the time series) | optional |

  *It does not have to be a star rating — any binary axis such as retained / churned, promoter / detractor.
- The **definition of the two groups to compare**? (this definition is the skeleton of the analysis,
  e.g. `rating == 5` vs `== 1`; also whether to drop the middle ratings)
- Domain **stop words** (service name, stock phrases) and **proper nouns** (product names, feature
  names)? For English these go into `CUSTOM_STOPWORDS`; multi-word product names can be joined
  with an underscore before tokenizing so they stay one token.
- **Language of the text?** The notebook's tokenizer is for English (lowercase → regex clean →
  whitespace split → stop words → `not_` negation marker). For Korean text swap in a Korean
  tokenizer such as `kiwipiepy` (keep nouns / verbs, restore verb stems, register domain words
  with `add_user_word`) — the rest of the pipeline consumes a list of tokens and stays the same.
  Other languages: a spaCy / NLTK tokenizer plus that language's stop-word list.
- How many reviews? — **at least several hundred per group** recommended (below that, LDA and the
  network are unstable; recommend stopping at frequency and distinctive keywords).

### 2. Data check — do not start the analysis before it passes

```python
df = pd.read_csv("YOUR_CSV_PATH")
df.groupby("YOUR_RATING_COL").agg(n=("YOUR_TEXT_COL", "count"),
    avg_len=("YOUR_TEXT_COL", lambda s: s.str.len().mean()))
```

- Pass criteria: several hundred rows in each group, average length checked (warn if one-word
  reviews dominate), duplicates and bot patterns (the same sentence repeated) checked. If the groups
  are extremely unbalanced, caution the reader about interpreting the distinctiveness metrics.

### 3. Code substitution map

| Anchor (section / identifier) | What | How |
| --- | --- | --- |
| Load cell | `data/reviews.csv` path, `rating`/`text`/`created_at` column names | the reader's data |
| Group definition | `GROUP_A = reviews["rating"] == 5` / `GROUP_B == 1` (one place in the load cell) | the reader's definition — frequency, TF-IDF and networks all reuse `GROUP_A/B` and `pos`/`neg`, so change only here |
| Preprocessing cell | `CUSTOM_STOPWORDS` (15 defaults), `NEGATORS` | extend with the reader's domain stop words; for Korean replace `clean()`/`tokenize()` with a `kiwipiepy`-based tokenizer |
| 〃 | `tokenize()` negation rule (`not`/`no`/`never`/`nothing`/`cannot` or `n't` → `not_` prefix on the next content word) | keep the default — extend `NEGATORS` if the domain uses other negators ("hardly", "without") |
| Distinctiveness cells | `TOP = 100` (unique keywords), `log_odds_z(..., alpha0=1000)` | to the data size |
| Network cells | `TOPN = 25` (bigrams), `build_cooccurrence(top_edges=40, min_word=22, min_pair=12)` defaults (`cooccurrence_network()` is the wrapper), `NET_DROP` | scale the min values with the number of reviews (lower them with fewer reviews) |
| LDA cell | `CountVectorizer(max_df=0.5, min_df=10)`, `n_components=5` | try 5-15 topics; stop at "nameable in plain words" |
| Topic inspection cell | `topic_with("camping")` · `topic_with("refund")` anchor words | anchor words from the reader's own top-word printout — picked by word, so changing n_components does not break it |
| Original-text cell | the keyword in `kwic(neg, "refund")` | the reader's keyword from the earlier steps |
| Topic time-series cell | `reviews["created_at"]`, `to_period("W")` weekly aggregation | skip the cell without a date column; otherwise adjust column name and aggregation unit |
| Positive rediscovery cell | `flat_words` (stock-phrase exclusion list), `cooccurrence_network(pos, …, top_edges=48, min_word=20)` arguments | rewrite with the obvious words of the reader's domain; arguments to the number of reviews |

### 4. Step by step

1. (10.7.1-10.7.2) Load, define groups → check counts → run the tokenizer → **check the 2 example
   token lists and the `freq_top` table (top 15 per group) with the reader for bad splits and missing
   stop words** (use `freq_terms(freq, n=30)` to see more. Quality here caps everything that follows —
   extend `CUSTOM_STOPWORDS` and repeat if needed).
2. (10.7.3-10.7.4.1) Frequency, word clouds → unique keywords → agree on a first impression.
3. (10.7.4.2-10.7.4.3) Distinctive keywords (TF-IDF, log-odds ratio) → show the top-word tables and explain what changed from the frequency result.
4. (10.7.5) Bigrams, co-occurrence network → read the communities (theme clusters) — hub words are candidate improvement levers.
5. (10.7.6) LDA (+ topic time series) → try naming each topic from its top words → if it fails, adjust `n_components` and repeat.
6. (10.7.7) **Back to the original text**: always read the KWIC of the key keyword and the representative review per topic, and base the conclusion on quotes.
7. (10.7.8, if time allows) Rediscover the positive group — look for unknown use cases and customer segments.

### 5. Interpreting the results

- Use a result from any lens in a report **only after checking the original text**. Keywords and
  topics are hypotheses; the evidence is the quote.
- Recommended report form: "The dissatisfied group talks about {theme} with {distinctive keywords} — representative quote: '…'".
- Do not read frequencies as shares of all customers (self-selection bias of review writers).
- Operational issues found in complaints must be fixed just to get back to even (rating recovery);
  unexpected use cases and segments found in satisfaction translate into growth levers (copy,
  product variants, channels).
- A hub word in the network (e.g. 'refund') is improvement leverage — the hypothesis that fixing one
  thing resolves the complaints hanging off it. Clusters are categories the data found on its own, so
  use them as candidate categories for topic modeling or automatic CS-ticket classification (book 10.3.2).
- Next actions: connect the complaint themes to the CS / product improvement backlog, and verify the
  effect of a fix with an A/B test (chapter 3). (Book 10.9 stresses that the techniques and order are
  only an example and emphasizes the 'analytical eye' — the backlog / A/B link is this reference's suggestion.)

## Pitfalls

- Tokenization quality caps the whole pipeline — if you see bad splits (or, for Korean, bad
  morpheme splits), fix the stop-word list / user dictionary first. Preprocessing and cleaning is the
  most time-consuming step of qualitative analysis.
- Negation: a plain stop-word list drops "not" / "no", turning "does not fit" into "fit". Keep the
  negators out of the stop-word list and mark them (`not_fit`), or the complaint signal vanishes.
- Extreme experiences write more reviews — comparisons between groups (relative) are valid, but never interpret absolute shares.
- Do not read the top TF-IDF words as "the words that separate the groups" — words shared by both
  sides still stay near the top. Measure separation with the log-odds z-score (without the
  standardization, a word seen once or twice becomes an extreme value).
- Bigrams only catch consecutive words ("delivery was unexpectedly slow" misses delivery–slow).
  Linking co-occurrences by raw count gives a hairball — filter with PMI to see clusters.
- Increasing the number of LDA topics keeps producing plausible-looking topics — stop when a topic
  you cannot name appears. Topic numbers and composition depend on the environment (version, seed).
- The higher the abstraction, the more original context is lost — irony ("they never refunded me so
  I just kept using it, and it's fine") is only filtered out by reading the text. KWIC matches
  literally, so search synonyms ('return') separately.
- Word-based lenses (frequency, weighting, networks, LDA) treat only identical strings as the same —
  'delivery / shipping', 'refund / return' are counted separately, and no stemming is applied, so
  'delay / delayed' are separate tokens too; irony like "super fast delivery, only took two weeks" is
  missed (book 10.4). Grouping by meaning needs embeddings / LLMs (not in the notebook).
- When the subject changes (CS inquiries, surveys, another language) re-think preprocessing and
  tools, and at hundreds of thousands of rows re-tune the topic count and thresholds (min_df,
  min_word · min_pair) (book 10.9).

## Study guide

### Core concepts — what the reader should be able to explain after this chapter

- **Tokenization** — splitting text into countable units. For English: lowercase, strip punctuation,
  split on whitespace, drop stop words, keep negation as a `not_` marker. For Korean (and other
  languages where particles and endings change a word's shape) a morphological analyzer is needed,
  because whitespace tokens would split the same word into different tokens.
- **Distinctive keywords vs frequency** — words that appear a lot (frequency) and words that
  **separate** the two groups (TF-IDF, log-odds ratio) are different. If 'delivery' is frequent on
  both sides it has no distinguishing power.
- **Log-odds ratio z-score** — a keyness metric that standardizes the difference in word-usage odds
  between the two groups, taking the variance into account. It filters out accidental differences in
  rare words.
- **Co-occurrence network** — a graph of word pairs that appear in the same review. It shows "which
  things are bundled together in a complaint", which a word list cannot.
- **LDA topic modeling** — a model that treats a document as a mixture of latent topics. A topic is
  only a word distribution; giving it meaning (naming) is the analyst's job.
- **Back to the original text (KWIC)** — the final step that verifies candidates found by the
  quantitative lenses against the original context. The conclusion of qualitative analysis always
  rests on quotes.

### Concept check

1. How do the top words by plain frequency differ from the top words by log-odds z-score? Why use
   the latter when comparing two groups?
   - Hint: frequency is dominated by words shared by both sides — distinctiveness measures how much a
     word is used "unusually on one side only", and z-score standardization filters out accidental
     skews of rare words.
2. If you finish the keyword and topic analysis but skip the "back to the original text" step before
   writing the report, what kind of error can creep in? Think about the distinctive keyword 'refund'.
   - Hint: misreading the keyword's context — only the original text tells whether 'refund' means
     'give me a refund' (complaint), 'the refund was quick' (praise), or irony. Nuance the numbers
     blur ("a day late" vs "two weeks and counting") also lives only in the text.
3. Why does the notebook keep "not" / "no" / "never" out of the stop-word list, and why does it mark
   'no response' as `not_response` instead of just dropping the negation?
   - Hint: a standard stop-word list drops negators, so 'does not fit' and 'fits' collapse into the
     same token and the complaint signal disappears. The marker keeps 'response' and 'no response'
     apart so they can be counted separately. (For Korean the same problem is handled inside the
     morphological analyzer with the an / mot / anh negation markers.)
4. The bigram network and the co-occurrence network look alike — how do the questions they answer
   differ? And why use PMI instead of raw counts for co-occurrence links?
   - Hint: bigram = order (the flow of expression "refund→request→not_response"), co-occurrence =
     order-free grouping (theme clusters). With raw counts a common word like 'delivery' links to
     everything — a hairball; PMI measures the actual strength of association relative to how often
     the pair would co-occur by chance.
5. What do LDA topic modeling and the co-occurrence network have in common, and how do they differ?
   What must a person do after getting the top words per topic?
   - Hint: both group words that appear together, but LDA gives a topic share per review as a number,
     which can be aggregated (e.g. over time). A topic is only a word distribution — naming is the
     analyst's job, and numbers / order change with the environment.

### Deeper exercises

1. **[Sandbox]** Add a new theme vocabulary to the complaint scenarios in `generate_data.py`
   (`NEG_CS`, `ASPECTS`, etc. — e.g. a few "battery" phrases) and have the reader predict **which lens
   catches that theme first / most clearly** among frequency → distinctiveness → network → LDA →
   edit → regenerate → re-run → compare. Afterwards restore with `git checkout -- generate_data.py data/`
   and regenerate.
2. **[Sandbox]** Raise LDA `n_components = 5 → 12` and have the reader predict how topic nameability
   changes → run (the topic inspection cell picks topics by anchor word, so it keeps working) → try
   naming each topic from its top words to experience "the limit of splitting". Restore afterwards.
3. **[Thinking]** Why does the positive-review analysis (10.7.8) lead to a different kind of action
   than the complaint analysis? (Complaints → fix actions — you only get back to even; positives →
   discovery actions — new use cases and segments → copy, product variants, channel expansion.
   Discuss using the clusters of the notebook's 5-star network as evidence.)
4. **[Thinking]** If the service collected thousands of reviews a day, how would you turn this
   pipeline into an operating system? (Discuss new-topic detection, a topic-trend dashboard, and
   designing the trigger for when a person must read the original text — there is no single answer.)
