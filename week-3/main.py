from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from repositories.postgres_repository import PostgresTaskRepository


repository = PostgresTaskRepository()


@asynccontextmanager
async def lifespan(app: FastAPI):
    repository.initialize()
    yield


app = FastAPI(
    title="Task Manager API",
    description="A FastAPI CRUD application connected to PostgreSQL",
    version="3.0.0",
    lifespan=lifespan,
)


class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/")
def home():
    return {
        "message": "Welcome to the Week 3 Task Manager API",
        "database": "PostgreSQL",
    }


@app.get("/health")
def health_check():
    try:
        repository.health_check()

        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
            },
        )


@app.get("/tasks")
def get_tasks():
    return repository.get_tasks()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = repository.get_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return task


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if task.title is None or not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"},
        )

    return repository.create_task(task.title.strip())


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide title or done"},
        )

    if task.title is not None and not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be blank"},
        )

    updated_task = repository.update_task(
        task_id=task_id,
        title=task.title.strip() if task.title is not None else None,
        done=task.done,
    )

    if updated_task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return updated_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    deleted = repository.delete_task(task_id)

    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return Response(status_code=204)