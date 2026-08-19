# Week 3 — FastAPI CRUD API with SQLite & PostgreSQL Docker

This project extends the Week 2 Task Manager API by replacing temporary in-memory storage with persistent database storage.

Week 3 contains two assignments:

- **A2 — Connecting CRUD to the Database**
- **A3 — Containerize Your Stack**

The project demonstrates CRUD operations, database persistence, PostgreSQL, Docker, Docker Compose, environment variables, and persistent Docker volumes.

---

# A2 — Connecting CRUD to the Database

## Overview

The original Week 2 application stored tasks in a temporary in-memory Python list.

For A2, the storage layer was replaced with a persistent SQLite database.

The API continues to expose the same CRUD endpoints while task data now survives FastAPI server restarts.

## Features

- Automatically creates the SQLite database
- Automatically creates the `tasks` table
- Inserts three starter tasks only when the table is empty
- Creates new tasks using SQL `INSERT`
- Reads tasks using SQL `SELECT`
- Updates tasks using SQL `UPDATE`
- Deletes tasks using SQL `DELETE`
- Preserves data after server restarts
- Returns proper HTTP status codes
- Handles invalid requests and missing task IDs
- Provides Swagger API documentation

## Technologies Used

- Python
- FastAPI
- SQLite
- Pydantic
- Uvicorn
- DB Browser for SQLite
- Swagger UI

## Project Structure

```text
week-3/
├── images/
│   ├── sqlite-exploration.png
│   └── swagger-crud-overview.png
├── main.py
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── sql/
    └── init.sql




SQLite Database Schema

The SQLite application automatically creates the following table:

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
);
Column	Type	Description
id	INTEGER	Unique task identifier
title	TEXT	Task title
done	INTEGER	Task completion status

SQLite stores Boolean values as integers:

0 = false
1 = true

The API converts SQLite values into JSON Boolean values.

Automatic Database Initialization

When the application starts:

SQLite creates tasks.db when it does not exist.
The application creates the tasks table.
The application checks how many tasks are stored.
Three starter tasks are inserted only when the table is empty.

This prevents duplicate seed tasks when the server restarts.

API Endpoints
Method	Endpoint	Description	Success Code
GET	/	Welcome message	200
GET	/health	Health check	200
GET	/tasks	Get all tasks	200
GET	/tasks/{task_id}	Get one task	200
POST	/tasks	Create a task	201
PUT	/tasks/{task_id}	Update a task	200
DELETE	/tasks/{task_id}	Delete a task	204
Example Requests
Create a Task
POST /tasks

Request body:

{
  "title": "Practice SQLite"
}

Example response:

{
  "id": 4,
  "title": "Practice SQLite",
  "done": false
}
Update a Task
PUT /tasks/1

Request body:

{
  "title": "Learn advanced SQLite",
  "done": true
}

Example response:

{
  "id": 1,
  "title": "Learn advanced SQLite",
  "done": true
}
Delete a Task
DELETE /tasks/1

Successful deletion returns:

204 No Content

A successful 204 response does not contain a response body.

Error Handling
Task Not Found

Status:

404 Not Found

Response:

{
  "error": "Task not found"
}
Missing or Blank Task Title

Status:

400 Bad Request

Response:

{
  "error": "Title is required"
}
Empty Update Request

Status:

400 Bad Request

Response:

{
  "error": "Provide title or done"
}
Blank Title During Update

Status:

400 Bad Request

Response:

{
  "error": "Title cannot be blank"
}
SQL Queries Explored

The SQLite database was manually explored using DB Browser for SQLite.

View All Tasks
SELECT * FROM tasks;
View Completed Tasks
SELECT * FROM tasks WHERE done = 1;
Count All Tasks
SELECT COUNT(*) FROM tasks;
Mark All Tasks as Completed
UPDATE tasks SET done = 1;
Delete Completed Tasks
DELETE FROM tasks WHERE done = 1;

Changes made manually in DB Browser were reflected in the FastAPI responses because both applications use the same tasks.db file.

How to Run A2 — SQLite
1. Clone the Repository
git clone https://github.com/Gnaneshwarsreepathi/flyrank-ai-backend-internship.git
2. Enter the Week 3 Folder
cd flyrank-ai-backend-internship/week-3
3. Create a Virtual Environment

Windows:

py -m venv venv
4. Activate the Virtual Environment

PowerShell:

.\venv\Scripts\Activate.ps1
5. Install Dependencies
python -m pip install -r requirements.txt
6. Start FastAPI
uvicorn main:app --reload
7. Open Swagger Documentation
http://127.0.0.1:8000/docs
8. View All Tasks
http://127.0.0.1:8000/tasks
SQLite Database Persistence Test

Database persistence was verified using the following steps:

A new task was created using POST /tasks.
The FastAPI server was stopped.
The server was started again.
The created task was still available through GET /tasks.

This confirms that task data is stored permanently in SQLite instead of a temporary Python list.

Screenshots
Swagger CRUD API

The Swagger interface demonstrates the available CRUD endpoints.

SQLite Database Exploration

DB Browser for SQLite was used to inspect the database and execute SQL queries manually.

A3 — Containerize Your Stack
Overview

For A3, the backend application was containerized using Docker.

The application and PostgreSQL database run together using Docker Compose.

The final architecture is:

Client
   |
   v
FastAPI Application
   |
   v
PostgreSQL Database
   |
   v
Docker Persistent Volume

The goal of A3 is to run the complete backend stack using one command.

Technologies Used for A3
Python 3.12
FastAPI
Uvicorn
PostgreSQL 16
Docker
Docker Compose
SQL
Environment Variables
Docker Volumes
PostgreSQL Database

For A3, the database layer was changed from the SQLite implementation used in A2 to PostgreSQL.

PostgreSQL runs inside its own Docker container.

The FastAPI application connects to PostgreSQL using a database connection string stored in the .env file.

The database connection is not hard-coded into the application.

Environment Variables

The PostgreSQL connection string is stored in .env.

Example:

DATABASE_URL=postgresql://postgres:postgres@db:5432/tasks

The .env file is intentionally excluded from Git.

A .env.example file is included in the repository as a template.

Example .env.example:

DATABASE_URL=postgresql://postgres:postgres@db:5432/tasks
PostgreSQL Repository

The database storage implementation was replaced with a PostgreSQL repository.

The repository is responsible for:

Creating tasks
Reading tasks
Reading a task by ID
Updating tasks
Deleting tasks

The service and API routes remain unchanged.

This demonstrates separation between the API layer and the data layer.

The architecture is:

Client
   |
   v
FastAPI Routes
   |
   v
Service Layer
   |
   v
PostgreSQL Repository
   |
   v
PostgreSQL Database
PostgreSQL Database Schema

The PostgreSQL table is created using:

sql/init.sql

The initialization script creates the tasks table if it does not already exist.

Example:

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
Docker Setup

The application is built using the Dockerfile.

The complete stack is managed using:

docker-compose.yml

The stack contains two main services:

app
db
App Service

The app service runs the FastAPI application.

Database Service

The db service runs PostgreSQL 16.

A named Docker volume is attached to PostgreSQL so database data survives container restarts.

Build the Docker Image

Run:

docker compose build
Start the Complete Stack

Run:

docker compose up -d --build

This command:

Builds the FastAPI application image
Starts the FastAPI container
Starts the PostgreSQL container
Creates the Docker network
Creates the PostgreSQL persistent volume
Initializes the database
Check Running Containers

Run:

docker compose ps

The application and PostgreSQL containers should be running.

View Application Logs

Run:

docker compose logs -f app

The FastAPI application runs on:

http://0.0.0.0:8000

From the host machine, the API is available at:

http://localhost:8000
Swagger Documentation

FastAPI automatically provides interactive API documentation.

Open:

http://localhost:8000/docs

Alternative documentation:

http://localhost:8000/redoc
Test the API
Get All Tasks
curl http://localhost:8000/tasks
Get Task by ID
curl http://localhost:8000/tasks/1
Create a Task

Using Swagger:

POST /tasks

Example request:

{
  "title": "Docker persistence test"
}
Update a Task
PUT /tasks/1

Example request:

{
  "title": "Updated Docker task",
  "done": true
}
Delete a Task
DELETE /tasks/1
PostgreSQL Persistence Test

Persistence was tested by creating tasks and restarting the application and database containers.

Step 1 — Start the Stack
docker compose up -d --build
Step 2 — Create a Task

Create a task using Swagger:

POST /tasks

Example:

{
  "title": "Persistence Test"
}
Step 3 — Verify the Task
curl http://localhost:8000/tasks

The created task should appear.

Step 4 — Stop the Containers
docker compose down
Step 5 — Start the Stack Again
docker compose up -d
Step 6 — Verify the Data
curl http://localhost:8000/tasks

The previously created task should still exist.

This proves that PostgreSQL data persists across container restarts using the Docker volume.

Docker Volume

PostgreSQL uses a named Docker volume to persist database data.

Stopping the stack with:

docker compose down

does not remove the named volume.

To completely remove the database and its stored data:

docker compose down -v

Use docker compose down -v only when intentionally resetting the database.

Useful Docker Commands
Build
docker compose build
Start
docker compose up -d
Build and Start
docker compose up -d --build
Check Containers
docker compose ps
View Application Logs
docker compose logs -f app
View Database Logs
docker compose logs -f db
Stop Containers
docker compose down
Stop Containers and Remove Database Volume
docker compose down -v
Access PostgreSQL

PostgreSQL can be accessed directly from the database container.

Run:

docker compose exec db psql -U postgres -d tasks

Then run SQL queries.

View All Tasks
SELECT * FROM tasks;
Count Tasks
SELECT COUNT(*) FROM tasks;
View Completed Tasks
SELECT * FROM tasks WHERE done = TRUE;

Exit PostgreSQL:

\q
Final Architecture
                         Client
                           |
                           v
                  +------------------+
                  |   FastAPI App    |
                  |   Port 8000      |
                  +--------+---------+
                           |
                           v
                  +------------------+
                  |   PostgreSQL     |
                  |   Port 5432      |
                  +--------+---------+
                           |
                           v
                  +------------------+
                  | Docker Volume    |
                  | Persistent Data  |
                  +------------------+
A2 → A3 Progression

The project demonstrates the evolution of the backend application.

A2
Client
   |
   v
FastAPI
   |
   v
SQLite
A3
Client
   |
   v
FastAPI Container
   |
   v
PostgreSQL Container
   |
   v
Docker Persistent Volume

The API contract remains unchanged while the storage implementation and infrastructure are improved.

Assignment Requirements
A2 — Connecting CRUD to Database
 CRUD API maintained
 SQLite database implemented
 Database created automatically
 Tasks table created automatically
 Three starter tasks inserted only when the table is empty
 CRUD operations implemented using SQL
 Data survives application restart
 Unknown IDs return 404
 Invalid requests return appropriate errors
 SQLite database manually explored using SQL
A3 — Containerize Your Stack
 PostgreSQL runs in Docker
 PostgreSQL uses a persistent Docker volume
 Database connection uses .env
 .env is gitignored
 .env.example is committed
 SQL initialization file is provided
 PostgreSQL repository implemented
 FastAPI application containerized
 Docker Compose used
 Application and database start together
 CRUD API remains unchanged
 Database persistence tested across container restart
Learning Outcomes

This project demonstrates practical knowledge of:

FastAPI
REST API development
CRUD operations
SQL
SQLite
PostgreSQL
Database repositories
Separation of API and data layers
Environment variables
Docker
Docker Compose
Docker volumes
Database initialization
Persistent storage
API testing
PostgreSQL CLI
Conclusion

Week 3 demonstrates how a backend application can evolve from temporary in-memory storage to persistent database storage and finally into a containerized application.

The API contract remains the same while the underlying storage and infrastructure are changed.

Week 2
Client → FastAPI → In-Memory List


A2
Client → FastAPI → SQLite


A3
Client → FastAPI Container → PostgreSQL Container → Docker Volume

The final application can be started using:

docker compose up -d --build

The API is available at:

http://localhost:8000

Swagger documentation:

http://localhost:8000/docs
