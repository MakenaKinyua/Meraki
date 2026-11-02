# imports
import pandas as pd
import sqlite3
from pathlib import Path
from src.btc.config import PROCESSED_DIR, PROJECT_ROOT, DATA_DIR

# paths 
SCHEMA_PATH = PROJECT_ROOT / "src/db/schema.sql"
DB_PATH = DATA_DIR / "ingredients.db"
INPUT_PATH = PROCESSED_DIR / "clean_ingredients.csv"

# build database function
def build_db(INPUT_PATH):
    df = pd.read_csv(INPUT_PATH)

    # sanity checks
    required_cols = {"ingredient", "description", "normalised_name"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
            f"Found columns: {list(df.columns)}."
        )
    
    # create database connection
    # Path("database").mkdir(exist_ok=True)
    sqlite_connection = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        sqlite_connection.executescript(f.read())

    # add rows 
    inserted_rows = 0
    skipped_rows = 0

    for _, row in df.iterrows():
        ingredient = str(row["ingredient"]).strip()
        description = str(row["description"]).strip()
        normalised_name = str(row["normalised_name"])

        if not description or description.lower == "nan":
            skipped_rows += 1
            continue

        try:
            sqlite_connection.execute(
                """ 
                INSERT INTO ingredients (ingredient, normalised_name, description)
                VALUES (?,?,?)
                """,
                (ingredient, normalised_name, description),
            )
            
            inserted_rows += 1

        except sqlite_connection.IntegrityError:
            skipped_rows += 1

    sqlite_connection.commit()
    sqlite_connection.close()

    print(f"Rows inserted:{inserted_rows} and Rows skipped:{skipped_rows}")

build_db(INPUT_PATH)