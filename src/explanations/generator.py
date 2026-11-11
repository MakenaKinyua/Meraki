import logging
import sqlite3
from dataclasses import dataclass

from src.db.normalise import normalise_name
from src.db.queries import single_lookup, fuzzy_lookup
from src.explanations.prompt import (
    build_prompt, get_system_prompt, InvalidIngredientError,
)
from src.explanations.llm_client import call_groq, LLMError

logger = logging.getLogger(__name__)


@dataclass
class ExplanationResult:
    status: str                  
    query: str
    matched_name: str | None = None
    match_type: str | None = None    
    explanation: str | None = None
    error: str | None = None


def explain_ingredient(conn, name):
    query = normalise_name(name)

    # 1. look up (exact first, then fuzzy)
    row = single_lookup(conn, query)
    match_type = "exact"
    if row is None:
        row = fuzzy_lookup(conn, query)
        match_type = "fuzzy"
    if row is None:
        logger.info("not found: %r", name)
        return ExplanationResult(status="not_found", query=name)

    matched = row["normalised_name"]

    # 2. build prompt
    try:
        user_prompt = build_prompt(row)
    except InvalidIngredientError as e:
        logger.warning("bad row for %r: %s", matched, e)
        return ExplanationResult("error", name, matched, match_type, error=str(e))

    # 3. call LLM
    try:
        text = call_groq(get_system_prompt(), user_prompt)
    except LLMError as e:
        logger.error("LLM failed for %r: %s", matched, e)
        return ExplanationResult("error", name, matched, match_type, error=str(e))

    logger.info("explained %r via %s match", matched, match_type)
    return ExplanationResult("ok", name, matched, match_type, explanation=text)
