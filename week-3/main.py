from contextlib import closing
from pathlib import Path
from typing import Optional
import sqlite3

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(
    title="Task Manager API",
    description="A FastAPI CRUD application connected to SQLite",
    version="3.0.0"
)


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "tasks.db"


class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def get_database_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with closing(get_database_connection()) as connection:

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

        if result["task_count"] == 0:
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


def row_to_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


initialize_database()


@app.get("/")
def home():
    return {
        "message": "Welcome to the Week 3 Task Manager API",
        "database": "SQLite"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.get("/tasks")
def get_tasks():
    with closing(get_database_connection()) as connection:

        rows = connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            ORDER BY id
            """
        ).fetchall()

        return [row_to_task(row) for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with closing(get_database_connection()) as connection:

        row = connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (task_id,)
        ).fetchone()

        if row is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found"}
            )

        return row_to_task(row)


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if task.title is None or not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    clean_title = task.title.strip()

    with closing(get_database_connection()) as connection:

        cursor = connection.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (?, ?)
            """,
            (clean_title, 0)
        )

        new_task_id = cursor.lastrowid
        connection.commit()

        new_task = connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (new_task_id,)
        ).fetchone()

        return row_to_task(new_task)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide title or done"}
        )

    if task.title is not None and not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be blank"}
        )

    with closing(get_database_connection()) as connection:

        existing_task = connection.execute(
            """
            SELECT id
            FROM tasks
            WHERE id = ?
            """,
            (task_id,)
        ).fetchone()

        if existing_task is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found"}
            )

        update_fields = []
        update_values = []

        if task.title is not None:
            update_fields.append("title = ?")
            update_values.append(task.title.strip())

        if task.done is not None:
            update_fields.append("done = ?")
            update_values.append(int(task.done))

        update_values.append(task_id)

        connection.execute(
            f"""
            UPDATE tasks
            SET {", ".join(update_fields)}
            WHERE id = ?
            """,
            update_values
        )

        connection.commit()

        updated_task = connection.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (task_id,)
        ).fetchone()

        return row_to_task(updated_task)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with closing(get_database_connection()) as connection:

        cursor = connection.execute(
            """
            DELETE FROM tasks
            WHERE id = ?
            """,
            (task_id,)
        )

        if cursor.rowcount == 0:
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found"}
            )

        connection.commit()

        return Response(status_code=204)