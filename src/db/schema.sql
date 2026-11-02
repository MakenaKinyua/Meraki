CREATE TABLE IF NOT EXISTS ingredients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient TEXT NOT NULL,
    normalised_name TEXT NOT NULL,
    description TEXT,
    llm_explanation TEXT,
    explanation_generated_at TEXT,
    UNIQUE(normalised_name)
    );

CREATE INDEX IF NOT EXISTS idx_normalised_name ON ingredients(normalised_name);