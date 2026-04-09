# FitShopAssistant

FitShopAssistant is a desktop AI shopping + nutrition assistant focused on macro-based meal planning, daily food/exercise tracking, and practical grocery guidance.  
It is designed to run locally and can be packaged into a Windows `.exe`.

## What is included

- **Profile onboarding** (name, age, height, weight, goal, macro/calorie targets).
- **Food logging** with nutrition search powered by **OpenFoodFacts**.
- **Exercise logging** with exercise discovery powered by **free-exercise-db**.
- **Local persistent storage** using SQLite (no cloud account required).
- **AI meal recommendations** using local **Ollama** (`llama3` default).
- **Budget/cookware/strictness settings** that influence recommendation style.
- **Walmart-style basket cost estimation** with offline-friendly heuristics.
- **Ready-to-build executable flow** via PyInstaller.

## Tech stack

- Python 3.11+
- Tkinter GUI
- SQLite
- Requests
- PyInstaller (build packaging)

## Project structure

```text
fitshop_assistant/
  __init__.py
  ai.py
  config.py
  database.py
  main.py
  services.py
  ui.py
run.py
requirements.txt
build_exe.bat
```

## Data sources used

1. OpenFoodFacts product search (nutrition values).
2. free-exercise-db dataset by yuhonas (exercise names).
3. Local Ollama API (`http://localhost:11434/api/generate`) for recommendations.

## Quick start (dev mode)

1. Install Python 3.11+.
2. Create and activate a virtual environment.
3. Install requirements:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python run.py
```

## First-time user flow

1. Open app.
2. Go to **Profile** and save your profile + goals.
3. Use **Food Log** to search + add foods.
4. Use **Exercise Log** to search + add exercises and duration.
5. Configure **Settings** (budget, cookware, strictness, model).
6. Open **Recommendations** and click **Generate Meal Plan**.

## Ollama setup (for AI recommendations)

If you want local LLM recommendations:

```bash
ollama pull llama3
ollama serve
```

If Ollama is unavailable, the app falls back to an offline rules-based recommendation.

## Build Windows EXE

From the project root:

```bat
build_exe.bat
```

Output:

- `dist/FitShopAssistant.exe`

## Notes on Walmart pricing

The app includes an **offline heuristic price estimator** to keep the app reliable without requiring paid or unstable scraping dependencies.
You can adjust behavior through settings and extend pricing logic in `services.py`.

## Missing or future enhancements already planned

- Barcode scanning workflow.
- Better per-exercise calorie burn estimation using MET values and user weight.
- Historical charts (weekly macro adherence + spending trends).
- Optional cloud sync/export.
- Real retailer API integration if official access is available.

## Troubleshooting

- If food/exercise lookup fails, verify internet access.
- If AI generation fails, make sure Ollama is running locally.
- If EXE build fails, ensure your Python environment can install `pyinstaller`.

## License

MIT (see `LICENSE`).
