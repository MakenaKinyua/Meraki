import sqlite3
from rapidfuzz import process, fuzz
from src.btc.config import FUZZY_LOOKUP_THRESHOLD, PROJECT_ROOT
from src.db.queries import (
    single_lookup, lookup_by_id, fuzzy_lookup, bulk_lookup, get_stats
)

def test_single_lookup_finds_exact_match(conn):
    result = single_lookup(conn, "Glycerin")
    assert result["normalised_name"] == "glycerin"

def test_single_lookup_returns_none_when_missing(conn):
    assert single_lookup(conn, "unobtainium") is None

def test_lookup_by_id_returns_row(conn):
    assert lookup_by_id(conn, 1)["normalised_name"] == "azelaic acid"

def test_lookup_by_id_returns_none_when_missing(conn):
    assert lookup_by_id(conn, 9999) is None

def test_fuzzy_lookup_matches_typo(conn):
    result = fuzzy_lookup(conn, "azelaic acd")
    assert result["normalised_name"] == "azelaic acid"

def test_fuzzy_lookup_returns_none_below_threshold(conn):
    assert fuzzy_lookup(conn, "zzzzzz") is None

def test_fuzzy_lookup_on_empty_table_returns_none(conn):
    conn.execute("DELETE FROM ingredients")
    assert fuzzy_lookup(conn, "glycerin") is None

def test_bulk_lookup_returns_none_for_missing_names(conn):
    result = bulk_lookup(conn, ["glycerin", "unobtainium"])
    assert result["glycerin"] is not None
    assert result["unobtainium"] is None

def test_bulk_lookup_empty_list_returns_empty_dict(conn):
    assert bulk_lookup(conn, []) == {}

def test_get_stats_counts(conn):
    stats = get_stats(conn)
    assert stats["total"] == 3
    assert stats["explained"] == 0
    assert stats["unexplained"] == 3