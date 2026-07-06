"""
chatbot.py
----------
Core chatbot logic for the FAQ Chatbot.

Responsibilities
----------------
* Load the FAQ dataset once at module import time.
* Pre-build the TF-IDF index once (not per query).
* Detect greetings, thanks, and farewells before FAQ matching.
* Expose get_response(user_query) -> str as the single public entry point.
* Log unmatched questions to `logs/unanswered.log` for dataset improvement.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from matcher import build_index, find_best_match, MatchResult

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "faqs.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Separate file handler for unanswered questions
_unanswered_handler = logging.FileHandler(LOG_DIR / "unanswered.log", encoding="utf-8")
_unanswered_handler.setLevel(logging.WARNING)
_unanswered_logger = logging.getLogger("unanswered")
_unanswered_logger.addHandler(_unanswered_handler)
_unanswered_logger.propagate = False   # don't duplicate to root logger


# ---------------------------------------------------------------------------
# Intent patterns (checked BEFORE FAQ matching)
# ---------------------------------------------------------------------------
INTENT_PATTERNS: Dict[str, List[str]] = {
    "greeting": [
        r"\b(hi|hello|hey|howdy|greetings|good\s(morning|afternoon|evening))\b"
    ],
    "thanks": [
        r"\b(thank(s| you)|thx|cheers|appreciate|grateful)\b"
    ],
    "farewell": [
        r"\b(bye|goodbye|see\s?you|later|take\s?care|quit|exit)\b"
    ],
    "help": [
        r"\b(help|support|assist|what can you do|how does this work)\b"
    ],
}

INTENT_RESPONSES: Dict[str, str] = {
    "greeting": (
        "👋 Hello! Welcome to the Online Course Platform Support chatbot. "
        "Ask me anything about courses, payments, certificates, and more!"
    ),
    "thanks": (
        "😊 You're very welcome! Is there anything else I can help you with?"
    ),
    "farewell": (
        "👋 Goodbye! Have a great learning journey. Feel free to come back anytime!"
    ),
    "help": (
        "I can answer questions about:\n"
        "• Enrolling in courses\n"
        "• Payments & refunds\n"
        "• Certificates & progress\n"
        "• Account & subscription settings\n"
        "• Technical issues\n\n"
        "Just type your question and I'll do my best to help!"
    ),
}

FALLBACK_RESPONSE = (
    "🤔 I'm not sure I understand that question. Could you rephrase it? "
    "You can also type **help** to see what topics I can assist with."
)


# ---------------------------------------------------------------------------
# FAQ loading
# ---------------------------------------------------------------------------
def _load_faqs(path: Path) -> List[Dict]:
    """Load FAQ entries from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        faqs = json.load(f)
    logger.info("Loaded %d FAQ entries from %s", len(faqs), path)
    return faqs


# ---------------------------------------------------------------------------
# Module-level initialisation (runs ONCE at import time)
# ---------------------------------------------------------------------------
_FAQS: List[Dict] = _load_faqs(DATA_PATH)
_QUESTIONS: List[str] = [entry["question"] for entry in _FAQS]
_ANSWERS: List[str] = [entry["answer"] for entry in _FAQS]

logger.info("Pre-building TF-IDF index…")
_VECTORIZER, _TFIDF_MATRIX = build_index(_QUESTIONS)
logger.info("Index ready — chatbot is online.")


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------
def _detect_intent(text: str) -> Optional[str]:
    """
    Check whether user input matches a simple intent pattern.

    Returns the intent name (str) or None if no pattern matches.
    """
    lower = text.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lower):
                return intent
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_response(user_query: str) -> Tuple[str, Optional[MatchResult], Optional[str]]:
    """
    Generate a response for the given user query.

    Parameters
    ----------
    user_query : str
        Raw text from the user.

    Returns
    -------
    response : str
        The bot's answer text.
    match_result : Optional[MatchResult]
        The MatchResult object from the matcher (None for intent replies).
    matched_question : Optional[str]
        The FAQ question that was matched (None if no FAQ match).
    """
    query = user_query.strip()
    if not query:
        return "Please type a question and I'll do my best to help!", None, None

    # --- 1. Intent detection (greetings, thanks, farewell, help) ---
    intent = _detect_intent(query)
    if intent:
        logger.info("Intent detected: '%s'", intent)
        return INTENT_RESPONSES[intent], None, None

    # --- 2. FAQ similarity matching ---
    result = find_best_match(
        user_query=query,
        vectorizer=_VECTORIZER,
        tfidf_matrix=_TFIDF_MATRIX,
        threshold=0.3,
        top_n=3,
    )

    if result.matched:
        faq_question = _QUESTIONS[result.best_index]
        faq_answer = _ANSWERS[result.best_index]
        logger.info(
            "Matched FAQ #%d (score=%.3f): '%s'",
            result.best_index,
            result.best_score,
            faq_question,
        )
        return faq_answer, result, faq_question
    else:
        # --- 3. No match — log for future improvement ---
        _unanswered_logger.warning(
            "%s | UNMATCHED | query=%r | best_score=%.3f | top3=%s",
            datetime.now().isoformat(timespec="seconds"),
            query,
            result.best_score,
            result.top_n,
        )
        logger.warning("No match found for query: '%s' (best=%.3f)", query, result.best_score)
        return FALLBACK_RESPONSE, result, None


# ---------------------------------------------------------------------------
# Simple CLI mode for quick testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n🎓 FAQ Chatbot — Online Course Platform")
    print("Type 'bye' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        response, match_result, matched_q = get_response(user_input)

        print(f"\nBot: {response}")
        if matched_q:
            print(f"     📌 Matched FAQ : {matched_q}")
        if match_result:
            print(f"     📊 Confidence  : {match_result.best_score:.1%}")
            print(f"     🔍 Top matches : {match_result.top_n}")
        print()

        if _detect_intent(user_input) == "farewell":
            break
