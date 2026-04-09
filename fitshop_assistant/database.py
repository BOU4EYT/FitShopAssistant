from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .config import APP_DIR, DB_PATH, DEFAULT_SETTINGS


@dataclass
class UserProfile:
    name: str
    age: int
    height_cm: float
    weight_kg: float
    goal: str
    calorie_goal: int
    protein_goal: int
    carbs_goal: int
    fats_goal: int


class Database:
    def __init__(self, db_path: str | None = None) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = str(DB_PATH if db_path is None else db_path)
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    height_cm REAL NOT NULL,
                    weight_kg REAL NOT NULL,
                    goal TEXT NOT NULL,
                    calorie_goal INTEGER NOT NULL,
                    protein_goal INTEGER NOT NULL,
                    carbs_goal INTEGER NOT NULL,
                    fats_goal INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS food_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consumed_at TEXT NOT NULL,
                    food_name TEXT NOT NULL,
                    serving_desc TEXT NOT NULL,
                    calories REAL NOT NULL,
                    protein REAL NOT NULL,
                    carbs REAL NOT NULL,
                    fats REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS exercise_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    completed_at TEXT NOT NULL,
                    exercise_name TEXT NOT NULL,
                    duration_min REAL NOT NULL,
                    estimated_calories_burned REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            for key, value in DEFAULT_SETTINGS.items():
                conn.execute(
                    "INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)",
                    (key, value),
                )

    def save_profile(self, profile: UserProfile) -> None:
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO profile(
                    id, name, age, height_cm, weight_kg, goal, calorie_goal,
                    protein_goal, carbs_goal, fats_goal, created_at, updated_at
                ) VALUES(1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    age=excluded.age,
                    height_cm=excluded.height_cm,
                    weight_kg=excluded.weight_kg,
                    goal=excluded.goal,
                    calorie_goal=excluded.calorie_goal,
                    protein_goal=excluded.protein_goal,
                    carbs_goal=excluded.carbs_goal,
                    fats_goal=excluded.fats_goal,
                    updated_at=excluded.updated_at
                """,
                (
                    profile.name,
                    profile.age,
                    profile.height_cm,
                    profile.weight_kg,
                    profile.goal,
                    profile.calorie_goal,
                    profile.protein_goal,
                    profile.carbs_goal,
                    profile.fats_goal,
                    now,
                    now,
                ),
            )

    def get_profile(self) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
            return dict(row) if row else None

    def log_food(self, entry: dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO food_logs(consumed_at, food_name, serving_desc, calories, protein, carbs, fats)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["consumed_at"],
                    entry["food_name"],
                    entry["serving_desc"],
                    entry["calories"],
                    entry["protein"],
                    entry["carbs"],
                    entry["fats"],
                ),
            )

    def log_exercise(self, entry: dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO exercise_logs(completed_at, exercise_name, duration_min, estimated_calories_burned)
                VALUES(?, ?, ?, ?)
                """,
                (
                    entry["completed_at"],
                    entry["exercise_name"],
                    entry["duration_min"],
                    entry["estimated_calories_burned"],
                ),
            )

    def list_food_today(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM food_logs
                WHERE date(consumed_at) = date('now', 'localtime')
                ORDER BY consumed_at DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def list_exercise_today(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM exercise_logs
                WHERE date(completed_at) = date('now', 'localtime')
                ORDER BY completed_at DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def get_settings(self) -> dict[str, str]:
        with self._conn() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            return {row["key"]: row["value"] for row in rows}

    def update_settings(self, updates: dict[str, str]) -> None:
        with self._conn() as conn:
            for key, value in updates.items():
                conn.execute(
                    "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (key, value),
                )
