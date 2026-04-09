from pathlib import Path

APP_NAME = "FitShop Assistant"
APP_DIR = Path.home() / ".fitshop_assistant"
DB_PATH = APP_DIR / "fitshop.db"
EXERCISE_CACHE_PATH = APP_DIR / "exercise_cache.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
OPENFOODFACTS_URL = "https://world.openfoodfacts.org/cgi/search.pl"
EXERCISE_DB_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"

DEFAULT_SETTINGS = {
    "budget_mode": "Low Cost",
    "prep_speed": "Easy/Fast",
    "cookware": "stove, pan",
    "ai_strictness": "Mid",
    "walmart_location": "",
    "ollama_model": "llama3",
}
