from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import sqlite3

app = FastAPI()


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "tasks.db"


def get_database_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_database_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        result = connection.execute(
            "SELECT COUNT(*) AS task_count FROM tasks"
        ).fetchone()

        task_count = result["task_count"]

        if task_count == 0:
            example_tasks = [
                ("Learn SQLite", 0),
                ("Connect FastAPI to a database", 0),
                ("Complete Week 3 Assignment", 0)
            ]

            connection.executemany(
                """
                INSERT INTO tasks (title, done)
                VALUES (?, ?)
                """,
                example_tasks
            )

        connection.commit()


initialize_database()