import sqlite3
from pathlib import Path
import pytest
from src.btc.config import SCHEMA_PATH

SCHEMA = SCHEMA_PATH
@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA.read_text())
    c.executemany(
        "INSERT INTO ingredients (ingredient, normalised_name, description) VALUES (?, ?, ?)",
        [
            ("Azelaic Acid", "azelaic acid", "Treats acne and rosacea"),
            ("Glycerin", "glycerin", "Humectant"),
            ("Niacinamide", "niacinamide", "Vitamin B3"),
        ],
    )
    c.commit()
    yield c
    c.close()