from fitshop_assistant.ai import RecommendationEngine
from fitshop_assistant.services import WalmartPriceService


def test_walmart_estimate_basket_has_total():
    service = WalmartPriceService()
    basket = service.estimate_basket(["chicken breast", "unknown"])
    assert "total" in basket
    assert basket["total"] > 0


def test_macro_summary_remaining_keys():
    summary = RecommendationEngine._macro_summary(
        {"calorie_goal": 2000, "protein_goal": 160, "carbs_goal": 200, "fats_goal": 60},
        [{"calories": 500, "protein": 30, "carbs": 40, "fats": 10}],
        [{"estimated_calories_burned": 100}],
    )
    assert set(summary["remaining"].keys()) == {"calories", "protein", "carbs", "fats"}
