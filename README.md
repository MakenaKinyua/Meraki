## Meraki: Skincare Ingredient Explainer

Imagine this.. you're standing in a cosmetics shop, holding a moisturiser you've never tried, and you turn it over. *Glycerin, niacinamide, sodium lauryl sulfate...* You have no idea what the ingredients are and whether they are any good for your skin, so you probably just wing it..

This project aims to give you a better understanding of those ingredients and make it easier for you to make a decision. Give it an ingredient and it gives you a short, friendly explanation of what it is and what it does for your skin.

---

### V1

- Takes **one ingredient name** at a time
- Forgives typos and messy typing (*"glycin"* still finds *glycine*)
- Looks the ingredient up in its own ingredient database
- Asks LLM to explain it in simple terms breaking down the jurgon, using only the database as our source of truth
- Says "no match found" when it doesn't know, instead of guessing

---

### How it works

1. **Prepare the data.** A raw list of ingredients and descriptions is cleaned up - consistent names, no blanks, no duplicates and stored in a database.
2. **You type an ingredient.** The name is tidied up so differences in capital letters, spacing, and punctuation don't matter.
3. **Find it.** The system looks for an exact match first. If there isn't one, it looks for the closest match to handle typos.
4. **Explain it.** The ingredient's description from the database is handed to Groq, which rewrites it in short, plain language.
5. **Get an answer.** You receive the explanation, or a clear message that nothing matched or something went wrong.

---

### How the pieces connect

```
 Raw ingredient list
        │
        ▼
 Cleaning step ──► Database
                      │
 You type a name      │
        │             │
        ▼             ▼
   Cleanup the name ──► Find a match (exact, or fuzzy)
                      │
                      ▼
              Write the question for Groq
                      │
                      ▼
                Groq explains it
                      │
                      ▼
                Answer shown to you
```

---

### Project structure

```
meraki/
├── README.md
├── pyproject.toml              project details and dependencies
├── .env.example                template for private settings
│
├── data/
│   ├── raw/                    the original ingredient list
│   ├── processed/              the cleaned version
│   └── ingredients.db          the finished database
│
├── tests/                      automatic checks that everything works
│
└── src/btc/
    ├── config.py               settings and keys
    ├── cli.py                  where you type and see answers
    │
    ├── db/                     everything about the data
    │   ├── schema.sql          the database layout
    │   ├── normalise.py        tidies ingredient names
    │   ├── preprocess.py       cleans the raw list
    │   ├── build_db.py         builds the database
    │   └── queries.py          finds ingredients
    │
    └── explanations/           everything about the AI answer
        ├── prompts.py          wording of the question
        ├── llm_client.py       talks to the AI service
        └── generator.py        runs the whole process
```

---

### Requirements

- **Python** 3.12+ with [uv](https://docs.astral.sh/uv/) to manage the backend
- **Node.js** 18+ with [pnpm](https://pnpm.io/) to manage the frontend
- **A Groq API key**, for the AI that writes the explanations
- **An ingredient list** (`data/raw/ingredients.csv` with `ingredient` and `description` columns) to build the database from

### How to run the app

**1. Install packages.**

Frontend (Vite/Vue) dependencies:

```bash
pnpm install --dir frontend
```

Backend (FastAPI) dependencies — `uv` creates a virtual environment from `backend/pyproject.toml`:

```bash
cd backend
uv sync
cd ..
```

**2. Set up environment variables.**

Copy `.env.example` to `.env` in the repository root and fill in your Groq key:

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

**3. Build the ingredient database.**

The web app reads `data/ingredients.db`, which is built from your raw list in two steps:

```bash
uv run python -m src.db.preprocess   # cleans the raw list into data/processed/
uv run python -m src.db.build        # builds data/ingredients.db
```

**4. Start both servers.**

From the repository root:

```bash
pnpm dev
```

This runs the FastAPI API at `http://localhost:8000` (interactive docs at `/docs`) and the Vite dev server at the same time. Open `http://localhost:5173` and press Ctrl+C to stop both servers.

Chat conversations are stored automatically in `data/chat.db` — no setup needed.

**Optional:** use the terminal-only version instead of the web app:

```bash
uv run python -m src.btc.cli
```
