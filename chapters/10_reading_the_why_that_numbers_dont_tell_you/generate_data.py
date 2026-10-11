"""Synthetic e-commerce product review generator.

Core design: complaints (1-star) are FLAT, satisfaction (5-star) is MULTI-DIMENSIONAL.
- A 1-star review is 'aspect (delivery / price / design / color / size / material / packaging)
  + negative opinion + customer-service complaint'. Complaints converge on a handful of
  operational issues, so the co-occurrence network splits into a few "flat" clusters.
- A 5-star review adds a 'usage scenario' (a use case or a customer segment) on top of that.
  It is not the contrived structure of one product that pleases every segment, but a realistic
  'discovery' structure. The product was designed for a studio / small apartment (little space),
  and its core attributes (small, lightweight, easy to clean) spread into contexts the makers never
  planned for: a use case ('car camping / camping' - light enough to be surprisingly handy) and a
  customer segment ('pet owners' - fur does not stick, easy to clean, word of mouth).
  So the 5-star co-occurrence network branches "multi-dimensionally": the intended use plus the
  discovered use case and the discovered customer segment.

With this answer planted (1-star = flat complaint clusters, 5-star = varied use-case / segment
clusters), the notebook's co-occurrence network recovers the structure as is. The seed is fixed for
reproducibility, and 1-star reviews are generated first so later changes to the 5-star design do
not disturb the 1-star data.
"""

import csv
import random
import datetime
import sys
from pathlib import Path

# Prevent garbled characters when output is captured through a pipe with a non-UTF-8 encoding
# (harmless when printing directly to the console)
sys.stdout.reconfigure(encoding="utf-8")

random.seed(42)

# === Review date (created_at) design ===
# Text and rating are left as they are; only 'when it was written' is assigned. This puts the
# chapter's 'discovery' story on a time axis:
#   - studio / small apartment (the intended use) is concentrated early,
#   - camping / car camping and pet owners (the discovered use case / segment) grow later on as
#     word spreads,
#   - 1-star refund / delivery complaints pile up once in the middle, like a logistics incident.
# -> The topic time-series (area) chart shows 'when a theme rises and fades'.
START_DATE = datetime.date(2024, 1, 1)
WEEKS = 26   # about 6 months


def _clip_week(w):
    return int(min(WEEKS - 1, max(0, round(w))))


def assign_date(rating, text):
    """Guess the theme from the text and place the review date in the period when that theme
    is trending."""
    t = text.lower()
    if rating == 5:
        if "camping" in t:                                 # discovered use case -> late rise
            w = random.triangular(WEEKS * 0.3, WEEKS - 1, WEEKS - 2)
        elif ("pet" in t) or ("dog" in t):                 # discovered segment -> mid-late rise
            w = random.triangular(WEEKS * 0.4, WEEKS - 1, WEEKS * 0.9)
        else:                                              # studio / apartment (intended use) -> early
            w = random.triangular(0, WEEKS * 0.6, WEEKS * 0.15)
    elif rating == 1:
        if ("delay" in t) or ("slow" in t) or ("refund" in t):   # logistics / CS issue -> mid spike
            w = random.triangular(WEEKS * 0.35, WEEKS * 0.8, WEEKS * 0.55)
        else:
            w = random.uniform(0, WEEKS - 1)
    else:
        w = random.uniform(0, WEEKS - 1)
    d = START_DATE + datetime.timedelta(weeks=_clip_week(w), days=random.randint(0, 6))
    return d.isoformat()

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

PRODUCTS = [f"P-{1000 + i}" for i in range(40)]

# Neutral aspects (shared by both groups) + positive / negative opinions per aspect.
# Some negative phrases spell the negation out ("does not fit", "no response", "not worth")
# so the notebook's negation-aware tokenizer has something to show.
ASPECTS = {
    "delivery": {
        "pos": ["delivery was fast", "delivery was quick", "delivery arrived in a day"],
        "neg": ["delivery was slow", "delivery is delayed by a week", "delivery took forever"],
    },
    "price": {
        "pos": ["price is reasonable", "price is satisfying", "great value for the price"],
        "neg": ["not worth the price", "price is expensive for what it is",
                "price is not justified"],
    },
    "design": {
        "pos": ["design is pretty", "design is stylish", "design looks premium"],
        "neg": ["design is ugly", "design is different from the photo", "design looks tacky"],
    },
    "color": {
        "pos": ["color matches the screen", "color is vivid", "color is lovely"],
        "neg": ["color is dull", "color is different from the photo", "color looks weird"],
    },
    "size": {
        "pos": ["size fits perfectly", "size is true to size", "size is roomy"],
        "neg": ["size is small", "size does not fit", "size is baggy"],
    },
    "material": {
        "pos": ["material is sturdy", "material feels premium", "material is soft"],
        "neg": ["material is flimsy", "material feels cheap", "material is rough"],
    },
    "packaging": {
        "pos": ["packaging was careful", "packaging was neat", "packaging was thoughtful"],
        "neg": ["packaging was a mess", "packaging was flimsy so the item got damaged",
                "packaging was sloppy"],
    },
}

# === 1-star (complaints) ===
NEG_CS = ["refund request got no response", "refund is still delayed",
          "refund cancellation was a mess",
          "contact about my refund inquiry went silent"]
NEG_CLOSER = ["so disappointed", "never buying again", "give me a refund",
              "what a letdown"]

# === 'Usage scenarios' for 5-star (satisfaction) - a 'discovery' structure in which the
#     product's core attributes (small, lightweight, easy to clean) spread beyond the intended
#     use (studio living) into unexpected use cases / customers ===
SCENARIOS = {
    # Intended use: an item for a studio / small apartment with little room
    # (anchors: studio, apartment, space, small)
    "studio": [
        "I was worried my studio apartment is small but it takes up hardly any space",
        "perfect size for a small studio apartment space",
        "I live alone in a small apartment and love that it takes so little space",
        "bought it when I moved into my studio and it fits the small space well",
        "my studio is small but it does not crowd the apartment space at all",
    ],
    # Discovered use case: lightweight, so surprisingly handy for camping / car camping
    # (anchors: camping, car camping, portable, outdoor, lightweight)
    # 'car camping' and 'camping' are spread so each also appears on its own (avoids perfect
    # collinearity) while bridging each other inside a sentence
    "camping": [
        "bought it for home but it is so lightweight I bring it car camping",
        "great for outdoor camping and very portable",
        "lightweight and portable so I pack it on every car camping trip",
        "light enough to carry in a backpack when camping",
        "portable enough for outdoor use like camping and car camping, surprisingly useful",
        "car camping outdoors it is portable and lightweight, really useful",
    ],
    # Discovered customer segment: fur does not stick and cleaning is easy, so word spreads
    # among pet owners (anchors: dog, pet, fur, cleaning, hygienic)
    "pet": [
        "I have a dog and fur does not stick so cleaning is easy",
        "we have a pet dog and cleaning the fur is simple and hygienic",
        "dog fur does not cling so I recommend it to pet owners",
        "as a pet household the fur cleaning is easy and hygienic",
        "dog fur cleaning is so easy that word spread among pet owners",
    ],
}
POS_CLOSER = ["overall very satisfied", "would buy again", "highly recommend",
              "better than expected"]

NOISE = ["", "", "", " lol", " :(", "!!", "..."]


def _sentence(parts):
    """Join phrases with commas, capitalize the first letter, and finish with a period."""
    s = ", ".join(parts)
    return s[0].upper() + s[1:] + "."


def make_neg():
    asp = random.sample(list(ASPECTS), k=random.randint(2, 3))
    parts = [random.choice(ASPECTS[a]["neg"]) for a in asp]
    if random.random() < 0.55:                                   # more than half include a CS complaint
        parts.insert(random.randint(0, len(parts)), random.choice(NEG_CS))
    parts.append(random.choice(NEG_CLOSER))
    return _sentence(parts) + random.choice(NOISE)


def make_pos():
    parts = []
    # 1-2 usage scenarios (use case / customer segment) - this is what makes satisfaction
    # reviews 'multi-dimensional'
    for s in random.sample(list(SCENARIOS), k=random.randint(1, 2)):
        parts.append(random.choice(SCENARIOS[s]))
    # 3 satisfied aspects - so the neutral aspect words (delivery, price, packaging, ...) also
    # fill the top of the 5-star frequency list. That way the plain frequency word clouds look
    # alike and bland on both sides (all aspect words), and only after the unique-keyword filter
    # strips that shared layer do the 5-star-only use-case / customer words (studio, dog,
    # cleaning, ...) show through.
    for a in random.sample(list(ASPECTS), k=3):
        parts.append(random.choice(ASPECTS[a]["pos"]))
    parts.append(random.choice(POS_CLOSER))
    random.shuffle(parts)
    return _sentence(parts) + random.choice(NOISE)


def make_mid():
    # 2-4 stars: one aspect satisfied, another aspect disappointing, in the same review
    a1, a2 = random.sample(list(ASPECTS), 2)
    return _sentence([random.choice(ASPECTS[a1]["pos"]), random.choice(ASPECTS[a2]["neg"]),
                      "just okay overall"])


rows = []
for _ in range(450):                                  # 1-star first (so later 5-star changes do not affect it)
    rows.append((random.choice(PRODUCTS), 1, make_neg()))
for _ in range(450):
    rows.append((random.choice(PRODUCTS), 5, make_pos()))
for _ in range(120):
    rows.append((random.choice(PRODUCTS), random.choice([2, 3, 4]), make_mid()))

random.shuffle(rows)
# Re-assign review_id 1..N and add created_at (text generation is finished, so body and rating stay as is)
rows = [(i + 1, p, r, t, assign_date(r, t)) for i, (p, r, t) in enumerate(rows)]

with open(OUT / "reviews.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["review_id", "product_id", "rating", "text", "created_at"])
    w.writerows(rows)

print(f"reviews.csv written: {len(rows)} rows (1-star 450 / 5-star 450 / 2-4 stars 120), with created_at")
