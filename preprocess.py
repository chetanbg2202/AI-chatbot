"""
preprocess.py
-------------
NLP preprocessing module for the FAQ Chatbot.

Provides a single reusable function `clean_text(text)` that:
  - Lowercases input
  - Removes punctuation
  - Tokenizes
  - Removes English stopwords
  - Lemmatizes each token using WordNetLemmatizer

This function is used both when indexing FAQs at startup and when
processing live user queries so both sides use identical preprocessing.
"""

import re
import string
import nltk

# ---------------------------------------------------------------------------
# NLTK resource bootstrap — nltk.download is idempotent (skips if present)
# ---------------------------------------------------------------------------
for _pkg in ["punkt_tab", "stopwords", "wordnet", "omw-1.4"]:
    nltk.download(_pkg, quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# ---------------------------------------------------------------------------
# Module-level singletons (created once, reused across calls)
# ---------------------------------------------------------------------------
_LEMMATIZER = WordNetLemmatizer()
_STOP_WORDS = set(stopwords.words("english"))


def clean_text(text: str) -> str:
    """
    Preprocess a text string for TF-IDF vectorisation.

    Steps
    -----
    1. Lowercase
    2. Remove punctuation
    3. Tokenize with NLTK word_tokenize
    4. Remove stopwords and single-character tokens
    5. Lemmatize each remaining token

    Parameters
    ----------
    text : str
        Raw input text (FAQ question or user query).

    Returns
    -------
    str
        A cleaned, space-joined string of lemmatized tokens.
    """
    if not isinstance(text, str):
        return ""

    # Step 1 – Lowercase
    text = text.lower()

    # Step 2 – Remove punctuation (keep only letters, digits, whitespace)
    text = re.sub(r"[^\w\s]", " ", text)          # replace punctuation with space
    text = re.sub(r"\d+", " ", text)               # optionally strip digits
    text = re.sub(r"\s+", " ", text).strip()       # collapse extra whitespace

    # Step 3 – Tokenize
    tokens = word_tokenize(text)

    # Step 4 & 5 – Remove stopwords / short tokens, then lemmatize
    cleaned_tokens = [
        _LEMMATIZER.lemmatize(token)
        for token in tokens
        if token not in _STOP_WORDS and len(token) > 1
    ]

    return " ".join(cleaned_tokens)


# ---------------------------------------------------------------------------
# Quick self-test when module is run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        "How do I reset my password?",
        "Can I get a refund for a course I purchased?",
        "What payment methods do you accept?",
    ]
    print("=== preprocess.py self-test ===\n")
    for s in samples:
        print(f"  Original : {s}")
        print(f"  Cleaned  : {clean_text(s)}\n")
