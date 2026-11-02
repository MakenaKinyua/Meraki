import sqlite3
from rapidfuzz import process, fuzz
from src.btc.config import FUZZY_LOOKUP_THRESHOLD, PROJECT_ROOT
from src.db.normalise import normalise_name

# converting sqlite row tuples to dict
def _row_to_dict(cursor: sqlite3.Cursor, row:tuple):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns,row))

# look up a single ingredient
def single_lookup(conn: sqlite3.Connection, name):
    name = normalise_name(name)
    cursor = conn.execute("SELECT * FROM ingredients WHERE normalised_name = ?", (name,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_dict(cursor, row)

# lookup by id 
def lookup_by_id(conn: sqlite3.Connection, id):
    cursor = conn.execute("SELECT * FROM ingredients WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_dict(cursor, row)

# fuzzy lookup
def fuzzy_lookup(
        conn: sqlite3.Connection,
        name,
        threshold = FUZZY_LOOKUP_THRESHOLD
):
    name = normalise_name(name)
    cursor = conn.execute("SELECT normalised_name FROM ingredients")
    all_names = [row[0] for row in cursor.fetchall()]
    if not all_names:
        return None
    
    #find a match
    match = process.extractOne(name, 
                               all_names,
                               scorer = fuzz.token_sort_ratio,
                               score_cutoff = threshold)
    if match is None:
        return None
    best_name, score, _ = match
    return single_lookup(conn, best_name)

# bulk lookup
def bulk_lookup(conn: sqlite3.Connection, names: list):
    if not names:
        return {}

    # map each original name -> its normalised form
    normalised = {n: normalise_name(n) for n in names}
    unique = list(set(normalised.values()))

    placeholders = ",".join("?" * len(unique))
    cursor = conn.execute(
        f"SELECT * FROM ingredients WHERE normalised_name IN ({placeholders})",
        unique,
    )

    found = {}
    for row in cursor.fetchall():
        d = _row_to_dict(cursor, row)
        found[d["normalised_name"]] = d

    # keep the caller's original names as keys
    return {n: found.get(normalised[n]) for n in names}

# stats 
def get_stats(conn: sqlite3.Connection):
    total = conn.execute("SELECT COUNT (*) FROM ingredients").fetchone()[0]
    explained = conn.execute("SELECT COUNT(*) FROM ingredients WHERE llm_explanation IS NOT NULL").fetchone()[0]
    unxplained = total - explained

    return{
        "total": total,
        "explained": explained,
        "unexplained": unxplained
    }

if __name__ == "__main__":
    conn = sqlite3.connect(PROJECT_ROOT / "data/ingredients.db")
    conn.close()