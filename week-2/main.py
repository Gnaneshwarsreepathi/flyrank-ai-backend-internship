from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


# Model used when creating a task
class TaskCreate(BaseModel):
    title: str


# Model used when updating a task
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# Temporary in-memory task storage
tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Complete Week 2 Assignment",
        "done": False
    }
]


# Root endpoint
@app.get("/")
def home():
    return {
        "message": "Task API is running",
        "docs": "/docs"
    }


# Health check
@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# READ - Get all tasks
@app.get("/tasks")
def get_tasks():
    return tasks


# READ - Get one task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


# CREATE - Create a new task
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):

    if not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    new_id = max(
        (existing_task["id"] for existing_task in tasks),
        default=0
    ) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


# UPDATE - Update an existing task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskUpdate):

    # Reject an empty request body
    if updated_task.title is None and updated_task.done is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field must be provided"
        )

    # Reject an empty title
    if updated_task.title is not None and not updated_task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    for task in tasks:

        if task["id"] == task_id:

            if updated_task.title is not None:
                task["title"] = updated_task.title

            if updated_task.done is not None:
                task["done"] = updated_task.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


# DELETE - Delete an existing task
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(task_id: int):

    for index, task in enumerate(tasks):

        if task["id"] == task_id:
            tasks.pop(index)
            return None

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )