from __future__ import annotations

import json
from datetime import datetime

import requests

from .config import EXERCISE_CACHE_PATH, EXERCISE_DB_URL, OPENFOODFACTS_URL


class NutritionService:
    def search_food(self, query: str, page_size: int = 10) -> list[dict]:
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": page_size,
        }
        response = requests.get(OPENFOODFACTS_URL, params=params, timeout=15)
        response.raise_for_status()
        products = response.json().get("products", [])
        results = []
        for item in products:
            nutr = item.get("nutriments", {})
            results.append(
                {
                    "name": item.get("product_name") or item.get("generic_name") or "Unknown",
                    "serving": item.get("serving_size") or "100g",
                    "calories": float(nutr.get("energy-kcal_100g") or 0),
                    "protein": float(nutr.get("proteins_100g") or 0),
                    "carbs": float(nutr.get("carbohydrates_100g") or 0),
                    "fats": float(nutr.get("fat_100g") or 0),
                }
            )
        return results


class ExerciseService:
    def _download_exercises(self) -> list[dict]:
        response = requests.get(EXERCISE_DB_URL, timeout=20)
        response.raise_for_status()
        payload = response.json()
        EXERCISE_CACHE_PATH.write_text(json.dumps(payload), encoding="utf-8")
        return payload

    def get_exercises(self) -> list[dict]:
        if EXERCISE_CACHE_PATH.exists():
            try:
                cached = json.loads(EXERCISE_CACHE_PATH.read_text(encoding="utf-8"))
                if isinstance(cached, list) and cached:
                    return cached
            except json.JSONDecodeError:
                pass
        return self._download_exercises()

    def search_exercises(self, query: str) -> list[str]:
        query_l = query.lower().strip()
        exercises = self.get_exercises()
        names = [e.get("name", "") for e in exercises]
        filtered = [n for n in names if query_l in n.lower()] if query_l else names
        return sorted(filtered)[:50]


class WalmartPriceService:
    """Heuristic pricing service for local estimates.

    This app keeps costs local/offline-friendly by maintaining a curated base-price table.
    """

    BASE_PRICES = {
        "chicken breast": 3.99,
        "brown rice": 1.89,
        "eggs": 2.97,
        "greek yogurt": 4.26,
        "oats": 3.64,
        "salmon": 8.44,
        "spinach": 2.48,
        "banana": 0.62,
        "avocado": 1.18,
        "olive oil": 7.98,
    }

    def estimate_price(self, ingredient: str) -> float:
        ingredient = ingredient.lower().strip()
        for key, price in self.BASE_PRICES.items():
            if key in ingredient or ingredient in key:
                return price
        return 4.99

    def estimate_basket(self, ingredients: list[str]) -> dict:
        breakdown = [{"ingredient": i, "price": self.estimate_price(i)} for i in ingredients]
        total = round(sum(i["price"] for i in breakdown), 2)
        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "items": breakdown,
            "total": total,
        }
