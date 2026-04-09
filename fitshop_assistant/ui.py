from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from .ai import RecommendationEngine
from .database import Database, UserProfile
from .services import ExerciseService, NutritionService, WalmartPriceService


class FitShopApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("FitShop Assistant")
        self.geometry("1100x700")

        self.db = Database()
        self.nutrition = NutritionService()
        self.exercise = ExerciseService()
        self.prices = WalmartPriceService()
        self.ai = RecommendationEngine()

        self._build_ui()
        self.refresh_today_views()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.profile_tab = ttk.Frame(notebook)
        self.food_tab = ttk.Frame(notebook)
        self.exercise_tab = ttk.Frame(notebook)
        self.settings_tab = ttk.Frame(notebook)
        self.recommend_tab = ttk.Frame(notebook)

        notebook.add(self.profile_tab, text="Profile")
        notebook.add(self.food_tab, text="Food Log")
        notebook.add(self.exercise_tab, text="Exercise Log")
        notebook.add(self.settings_tab, text="Settings")
        notebook.add(self.recommend_tab, text="Recommendations")

        self._build_profile_tab()
        self._build_food_tab()
        self._build_exercise_tab()
        self._build_settings_tab()
        self._build_recommendation_tab()

    def _build_profile_tab(self) -> None:
        fields = [
            "name",
            "age",
            "height_cm",
            "weight_kg",
            "goal",
            "calorie_goal",
            "protein_goal",
            "carbs_goal",
            "fats_goal",
        ]
        self.profile_vars = {f: tk.StringVar() for f in fields}

        current = self.db.get_profile() or {}
        for field, var in self.profile_vars.items():
            var.set(str(current.get(field, "")))

        for idx, field in enumerate(fields):
            ttk.Label(self.profile_tab, text=field.replace("_", " ").title()).grid(
                row=idx, column=0, sticky="w", padx=10, pady=5
            )
            ttk.Entry(self.profile_tab, textvariable=self.profile_vars[field], width=40).grid(
                row=idx, column=1, padx=10, pady=5
            )

        ttk.Button(self.profile_tab, text="Save Profile", command=self.save_profile).grid(
            row=len(fields), column=1, sticky="e", padx=10, pady=15
        )

    def _build_food_tab(self) -> None:
        self.food_query = tk.StringVar()
        self.food_choice = tk.StringVar()

        top = ttk.Frame(self.food_tab)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Entry(top, textvariable=self.food_query, width=50).pack(side="left", padx=5)
        ttk.Button(top, text="Search OpenFoodFacts", command=self.search_food).pack(side="left", padx=5)

        self.food_listbox = tk.Listbox(self.food_tab, height=8)
        self.food_listbox.pack(fill="x", padx=10)

        ttk.Button(self.food_tab, text="Add Selected Food", command=self.add_food).pack(pady=8)

        self.food_today = tk.Text(self.food_tab, height=18)
        self.food_today.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_exercise_tab(self) -> None:
        self.exercise_query = tk.StringVar()
        self.exercise_minutes = tk.StringVar(value="30")

        top = ttk.Frame(self.exercise_tab)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Entry(top, textvariable=self.exercise_query, width=50).pack(side="left", padx=5)
        ttk.Button(top, text="Search Exercises", command=self.search_exercise).pack(side="left", padx=5)

        self.exercise_listbox = tk.Listbox(self.exercise_tab, height=8)
        self.exercise_listbox.pack(fill="x", padx=10)

        mins_frame = ttk.Frame(self.exercise_tab)
        mins_frame.pack(fill="x", padx=10, pady=8)
        ttk.Label(mins_frame, text="Duration (min):").pack(side="left")
        ttk.Entry(mins_frame, textvariable=self.exercise_minutes, width=10).pack(side="left", padx=5)

        ttk.Button(self.exercise_tab, text="Add Selected Exercise", command=self.add_exercise).pack(pady=8)

        self.exercise_today = tk.Text(self.exercise_tab, height=18)
        self.exercise_today.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_settings_tab(self) -> None:
        settings = self.db.get_settings()
        keys = ["budget_mode", "prep_speed", "cookware", "ai_strictness", "walmart_location", "ollama_model"]
        self.setting_vars = {k: tk.StringVar(value=settings.get(k, "")) for k in keys}

        for idx, key in enumerate(keys):
            ttk.Label(self.settings_tab, text=key.replace("_", " ").title()).grid(
                row=idx, column=0, sticky="w", padx=10, pady=5
            )
            ttk.Entry(self.settings_tab, textvariable=self.setting_vars[key], width=45).grid(
                row=idx, column=1, padx=10, pady=5
            )

        ttk.Button(self.settings_tab, text="Save Settings", command=self.save_settings).grid(
            row=len(keys), column=1, sticky="e", padx=10, pady=15
        )

    def _build_recommendation_tab(self) -> None:
        action_frame = ttk.Frame(self.recommend_tab)
        action_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(action_frame, text="Generate Meal Plan", command=self.generate_plan).pack(side="left")

        self.plan_text = tk.Text(self.recommend_tab)
        self.plan_text.pack(fill="both", expand=True, padx=10, pady=10)

    def save_profile(self) -> None:
        try:
            profile = UserProfile(
                name=self.profile_vars["name"].get().strip(),
                age=int(self.profile_vars["age"].get()),
                height_cm=float(self.profile_vars["height_cm"].get()),
                weight_kg=float(self.profile_vars["weight_kg"].get()),
                goal=self.profile_vars["goal"].get().strip(),
                calorie_goal=int(self.profile_vars["calorie_goal"].get()),
                protein_goal=int(self.profile_vars["protein_goal"].get()),
                carbs_goal=int(self.profile_vars["carbs_goal"].get()),
                fats_goal=int(self.profile_vars["fats_goal"].get()),
            )
            self.db.save_profile(profile)
            messagebox.showinfo("Saved", "Profile saved successfully.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for numeric fields.")

    def search_food(self) -> None:
        self.food_listbox.delete(0, tk.END)
        query = self.food_query.get().strip()
        if not query:
            return
        try:
            self.food_results = self.nutrition.search_food(query)
            for item in self.food_results:
                self.food_listbox.insert(
                    tk.END,
                    f"{item['name']} | {item['serving']} | {item['calories']} kcal | P{item['protein']} C{item['carbs']} F{item['fats']}",
                )
        except Exception as exc:
            messagebox.showerror("Search Error", str(exc))

    def add_food(self) -> None:
        selection = self.food_listbox.curselection()
        if not selection:
            return
        item = self.food_results[selection[0]]
        self.db.log_food(
            {
                "consumed_at": datetime.now().isoformat(timespec="seconds"),
                "food_name": item["name"],
                "serving_desc": item["serving"],
                "calories": item["calories"],
                "protein": item["protein"],
                "carbs": item["carbs"],
                "fats": item["fats"],
            }
        )
        self.refresh_today_views()

    def search_exercise(self) -> None:
        self.exercise_listbox.delete(0, tk.END)
        query = self.exercise_query.get().strip()
        try:
            self.exercise_results = self.exercise.search_exercises(query)
            for name in self.exercise_results:
                self.exercise_listbox.insert(tk.END, name)
        except Exception as exc:
            messagebox.showerror("Search Error", str(exc))

    def add_exercise(self) -> None:
        selection = self.exercise_listbox.curselection()
        if not selection:
            return
        name = self.exercise_results[selection[0]]
        try:
            minutes = float(self.exercise_minutes.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Duration must be a number.")
            return
        # conservative kcal estimate if MET detail unavailable
        kcal_burned = round(minutes * 5.5, 1)
        self.db.log_exercise(
            {
                "completed_at": datetime.now().isoformat(timespec="seconds"),
                "exercise_name": name,
                "duration_min": minutes,
                "estimated_calories_burned": kcal_burned,
            }
        )
        self.refresh_today_views()

    def save_settings(self) -> None:
        updates = {k: v.get().strip() for k, v in self.setting_vars.items()}
        self.db.update_settings(updates)
        messagebox.showinfo("Saved", "Settings updated.")

    def refresh_today_views(self) -> None:
        foods = self.db.list_food_today()
        self.food_today.delete("1.0", tk.END)
        total_cals = sum(f["calories"] for f in foods)
        for f in foods:
            self.food_today.insert(
                tk.END,
                f"{f['consumed_at']} | {f['food_name']} | {f['calories']} kcal | P{f['protein']} C{f['carbs']} F{f['fats']}\n",
            )
        self.food_today.insert(tk.END, f"\nTotal calories today: {total_cals:.1f}\n")

        exercises = self.db.list_exercise_today()
        self.exercise_today.delete("1.0", tk.END)
        total_burn = sum(e["estimated_calories_burned"] for e in exercises)
        for e in exercises:
            self.exercise_today.insert(
                tk.END,
                f"{e['completed_at']} | {e['exercise_name']} | {e['duration_min']} min | {e['estimated_calories_burned']} kcal\n",
            )
        self.exercise_today.insert(tk.END, f"\nTotal calories burned today: {total_burn:.1f}\n")

    def generate_plan(self) -> None:
        profile = self.db.get_profile()
        if not profile:
            messagebox.showwarning("Missing Profile", "Please create your profile first.")
            return

        foods = self.db.list_food_today()
        exercises = self.db.list_exercise_today()
        settings = self.db.get_settings()

        likely_ingredients = ["chicken breast", "brown rice", "spinach", "greek yogurt", "eggs", "banana"]
        basket = self.prices.estimate_basket(likely_ingredients)
        recommendation = self.ai.recommend(profile, foods, exercises, settings, basket)

        self.plan_text.delete("1.0", tk.END)
        self.plan_text.insert(tk.END, recommendation)


def run_app() -> None:
    app = FitShopApp()
    app.mainloop()
