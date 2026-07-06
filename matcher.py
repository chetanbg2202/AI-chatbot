"""
matcher.py
----------
Similarity-matching module for the FAQ Chatbot.

Uses scikit-learn's TfidfVectorizer + cosine_similarity to find the best
matching FAQ for any incoming user query.

Public API
----------
build_index(faq_questions)        -> (vectorizer, tfidf_matrix)
find_best_match(user_query, ...)  -> MatchResult
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocess import clean_text

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_THRESHOLD: float = 0.3   # minimum cosine similarity to accept a match
TOP_N: int = 3                   # number of top candidates to return for debug


# ---------------------------------------------------------------------------
# Data class for a single match result
# ---------------------------------------------------------------------------
@dataclass
class MatchResult:
    """Container returned by find_best_match()."""

    matched: bool                          # True if similarity >= threshold
    best_score: float                      # cosine similarity of best match
    best_index: int                        # index into the FAQ list (-1 if no match)
    top_n: List[Tuple[int, float]] = field(default_factory=list)
    # top_n: list of (faq_index, score) for the top-N candidates


# ---------------------------------------------------------------------------
# Index builder (called ONCE at startup, not per query)
# ---------------------------------------------------------------------------
def build_index(
    faq_questions: List[str],
) -> Tuple[TfidfVectorizer, np.ndarray]:
    """
    Preprocess and vectorize all FAQ questions.

    Parameters
    ----------
    faq_questions : List[str]
        Raw FAQ question strings (not yet cleaned).

    Returns
    -------
    vectorizer : TfidfVectorizer
        Fitted vectorizer — must be reused for every user query.
    tfidf_matrix : np.ndarray  (shape: [n_faqs, n_features])
        TF-IDF matrix of all cleaned FAQ questions.
    """
    cleaned_questions = [clean_text(q) for q in faq_questions]
    logger.debug("Building TF-IDF index over %d FAQ questions.", len(cleaned_questions))

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),      # unigrams + bigrams for better coverage
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,       # apply log normalization to tf
    )
    tfidf_matrix = vectorizer.fit_transform(cleaned_questions)

    logger.info("TF-IDF index built: %d docs × %d features.",
                tfidf_matrix.shape[0], tfidf_matrix.shape[1])
    return vectorizer, tfidf_matrix


# ---------------------------------------------------------------------------
# Query matcher (called per user query)
# ---------------------------------------------------------------------------
def find_best_match(
    user_query: str,
    vectorizer: TfidfVectorizer,
    tfidf_matrix: np.ndarray,
    threshold: float = DEFAULT_THRESHOLD,
    top_n: int = TOP_N,
) -> MatchResult:
    """
    Find the best FAQ match for a user query using cosine similarity.

    Parameters
    ----------
    user_query : str
        Raw text typed by the user.
    vectorizer : TfidfVectorizer
        The same fitted vectorizer from build_index().
    tfidf_matrix : np.ndarray
        The pre-built TF-IDF matrix from build_index().
    threshold : float
        Minimum similarity score required to accept a match.
    top_n : int
        How many top candidates to include in MatchResult.top_n.

    Returns
    -------
    MatchResult
        Contains best_score, best_index, top_n candidates, and a
        boolean `matched` flag.
    """
    # Clean the user query the same way FAQ questions were cleaned
    cleaned_query = clean_text(user_query)
    logger.debug("Cleaned query: '%s'", cleaned_query)

    if not cleaned_query.strip():
        # Empty after cleaning — nothing to match
        return MatchResult(matched=False, best_score=0.0, best_index=-1, top_n=[])

    # Vectorize the query using the *fitted* vectorizer (no re-fitting!)
    query_vector = vectorizer.transform([cleaned_query])

    # Cosine similarity against every FAQ vector
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Gather top-N indices (descending order)
    top_indices = np.argsort(scores)[::-1][:top_n]
    top_candidates = [(int(idx), float(scores[idx])) for idx in top_indices]

    best_index = int(top_indices[0])
    best_score = float(scores[best_index])

    logger.debug(
        "Top-%d candidates: %s",
        top_n,
        [(i, f"{s:.3f}") for i, s in top_candidates],
    )

    return MatchResult(
        matched=best_score >= threshold,
        best_score=best_score,
        best_index=best_index if best_score >= threshold else -1,
        top_n=top_candidates,
    )
