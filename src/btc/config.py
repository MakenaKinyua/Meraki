# imports
import os 
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# filepaths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FUZZY_LOOKUP_THRESHOLD = 80
SCHEMA_PATH = PROJECT_ROOT / "src/db/schema.sql"
DB_PATH = DATA_DIR/"ingredients.db"
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")