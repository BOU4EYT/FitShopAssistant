from __future__ import annotations

import json

import requests

from .config import OLLAMA_URL


class RecommendationEngine:
    def __init__(self, model: str = "llama3") -> None:
        self.model = model

    @staticmethod
    def _macro_summary(profile: dict, foods: list[dict], exercise: list[dict]) -> dict:
        consumed = {
            "calories": sum(f["calories"] for f in foods),
            "protein": sum(f["protein"] for f in foods),
            "carbs": sum(f["carbs"] for f in foods),
            "fats": sum(f["fats"] for f in foods),
        }
        burned = sum(e["estimated_calories_burned"] for e in exercise)

        goals = {
            "calories": profile.get("calorie_goal", 0),
            "protein": profile.get("protein_goal", 0),
            "carbs": profile.get("carbs_goal", 0),
            "fats": profile.get("fats_goal", 0),
        }
        remaining = {
            "calories": goals["calories"] - consumed["calories"] + burned,
            "protein": goals["protein"] - consumed["protein"],
            "carbs": goals["carbs"] - consumed["carbs"],
            "fats": goals["fats"] - consumed["fats"],
        }
        return {"consumed": consumed, "burned": burned, "goals": goals, "remaining": remaining}

    def recommend(
        self,
        profile: dict,
        foods: list[dict],
        exercise: list[dict],
        settings: dict,
        basket_estimate: dict,
    ) -> str:
        macro = self._macro_summary(profile, foods, exercise)
        prompt = {
            "instruction": "Create 3 practical meals and a grocery list for tonight.",
            "constraints": {
                "goal": profile.get("goal", "general fitness"),
                "remaining_macros": macro["remaining"],
                "budget_mode": settings.get("budget_mode", "Low Cost"),
                "prep_speed": settings.get("prep_speed", "Easy/Fast"),
                "cookware": settings.get("cookware", "stove, pan"),
                "strictness": settings.get("ai_strictness", "Mid"),
            },
            "shopping_estimate": basket_estimate,
            "format": "Use headings: Meal 1/2/3, Why It Fits, Grocery List, Instructions",
        }
        try:
            resp = requests.post(
                OLLAMA_URL,
                json={
                    "model": settings.get("ollama_model", self.model),
                    "prompt": json.dumps(prompt, indent=2),
                    "stream": False,
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "").strip()
            if text:
                return text
        except requests.RequestException:
            pass

        remaining = macro["remaining"]
        return (
            "Offline fallback recommendation:\n\n"
            f"Remaining calories: {remaining['calories']:.0f}, protein: {remaining['protein']:.0f}g, "
            f"carbs: {remaining['carbs']:.0f}g, fats: {remaining['fats']:.0f}g.\n"
            "1) Chicken rice bowl with spinach and olive oil.\n"
            "2) Greek yogurt parfait with oats and banana.\n"
            "3) Egg scramble with avocado toast.\n"
            "Cookware-aware tip: keep recipes inside your declared cookware list."
        )
