from unittest.mock import patch

from src.explanations.generator import explain_ingredient
from src.explanations.llm_client import LLMError

GEN = "src.explanations.generator.call_groq"

def test_known_ingredient_returns_ok(conn):
    with patch(GEN, return_value="Fake explanation.") as fake:
        result = explain_ingredient(conn, "glycerin")

    assert result.status == "ok"
    assert result.explanation == "Fake explanation."
    assert result.matched_name == "glycerin"
    assert result.match_type == "exact"
    fake.assert_called_once()

def test_llm_receives_system_prompt_and_db_data(conn):
    with patch(GEN, return_value="x") as fake:
        explain_ingredient(conn, "glycerin")

    system_prompt, user_prompt = fake.call_args.args
    assert "cosmetic chemist" in system_prompt      # rules came from prompts.py
    assert "Glycerin" in user_prompt                # display name from the DB row
    assert "Humectant" in user_prompt               # description from the DB row

def test_messy_input_is_normalised(conn):
    with patch(GEN, return_value="x"):
        result = explain_ingredient(conn, "  Azelaic   ACID! ")

    assert result.status == "ok"
    assert result.matched_name == "azelaic acid"
    assert result.match_type == "exact"

def test_typo_uses_fuzzy_match(conn):
    with patch(GEN, return_value="x"):
        result = explain_ingredient(conn, "azelaic acd")

    assert result.status == "ok"
    assert result.matched_name == "azelaic acid"
    assert result.match_type == "fuzzy"

def test_unknown_ingredient_returns_not_found(conn):
    with patch(GEN) as fake:
        result = explain_ingredient(conn, "unobtainium")

    assert result.status == "not_found"
    assert result.explanation is None
    fake.assert_not_called()                        # no LLM call wasted

def test_not_found_keeps_original_query(conn):
    with patch(GEN):
        result = explain_ingredient(conn, "Unobtainium")

    assert result.query == "Unobtainium"            # what the user typed, not normalised

def test_llm_failure_returns_error_result(conn):
    with patch(GEN, side_effect=LLMError("api down")):
        result = explain_ingredient(conn, "glycerin")

    assert result.status == "error"
    assert "api down" in result.error
    assert result.explanation is None


def test_row_with_blank_description_returns_error(conn):
    conn.execute("UPDATE ingredients SET description = '   ' WHERE normalised_name = 'glycerin'")
    with patch(GEN) as fake:
        result = explain_ingredient(conn, "glycerin")

    assert result.status == "error"
    fake.assert_not_called()                        # bad row never reaches the LLM