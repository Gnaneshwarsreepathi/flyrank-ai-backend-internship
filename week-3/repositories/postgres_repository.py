import os
import time
from typing import Optional

import psycopg
from psycopg.rows import dict_row


class PostgresTaskRepository:

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set"
            )

    def get_connection(self):
        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
        )

    def _wait_for_database(self):
        max_attempts = 30

        for attempt in range(max_attempts):
            try:
                with self.get_connection():
                    return
            except psycopg.OperationalError:
                if attempt == max_attempts - 1:
                    raise

                time.sleep(1)

    def initialize(self):
        self._wait_for_database()

        with self.get_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )

                cursor.execute(
                    "SELECT COUNT(*) AS task_count FROM tasks"
                )

                result = cursor.fetchone()

                if result["task_count"] == 0:
                    cursor.executemany(
                        """
                        INSERT INTO tasks (title, done)
                        VALUES (%s, %s)
                        """,
                        [
                            ("Learn PostgreSQL", False),
                            ("Connect FastAPI to a database", False),
                            ("Complete Week 3 Assignment", False),
                        ],
                    )

            connection.commit()

    def health_check(self):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

    def get_tasks(self):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, title, done
                    FROM tasks
                    ORDER BY id
                    """
                )

                return cursor.fetchall()

    def get_task(self, task_id: int):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, title, done
                    FROM tasks
                    WHERE id = %s
                    """,
                    (task_id,),
                )

                return cursor.fetchone()

    def create_task(self, title: str):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks (title, done)
                    VALUES (%s, FALSE)
                    RETURNING id, title, done
                    """,
                    (title,),
                )

                task = cursor.fetchone()

            connection.commit()

            return task

    def update_task(
        self,
        task_id: int,
        title: Optional[str],
        done: Optional[bool],
    ):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id, title, done
                    FROM tasks
                    WHERE id = %s
                    """,
                    (task_id,),
                )

                existing_task = cursor.fetchone()

                if existing_task is None:
                    return None

                new_title = (
                    title
                    if title is not None
                    else existing_task["title"]
                )

                new_done = (
                    done
                    if done is not None
                    else existing_task["done"]
                )

                cursor.execute(
                    """
                    UPDATE tasks
                    SET title = %s,
                        done = %s
                    WHERE id = %s
                    RETURNING id, title, done
                    """,
                    (new_title, new_done, task_id),
                )

                updated_task = cursor.fetchone()

            connection.commit()

            return updated_task

    def delete_task(self, task_id: int) -> bool:
        with self.get_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    DELETE FROM tasks
                    WHERE id = %s
                    """,
                    (task_id,),
                )

                deleted = cursor.rowcount > 0

            connection.commit()

            return deleted