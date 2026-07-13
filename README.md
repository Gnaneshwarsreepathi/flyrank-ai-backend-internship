# 🚀 Backend AI Engineering – Week 1

<div align="center">

## Building My First Backend API with FastAPI

**FlyRank AI Internship | Backend AI Engineering Track**

![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)
![REST API](https://img.shields.io/badge/REST-API-green)
![GitHub](https://img.shields.io/badge/GitHub-Portfolio-black?logo=github)

</div>

---

# 📖 Introduction

This repository contains my **Week 1 assignment** for the **FlyRank AI Backend Engineering Internship**.

The purpose of this assignment was **not to build a complex application**.

Instead, it was designed to teach one of the most fundamental concepts in backend engineering:

> **How does a backend receive a request and send a response back to the client?**

Every modern application—whether it's ChatGPT, Amazon, Netflix, or Instagram—works because of this request → response cycle.

This project helped me understand that process by building a minimal backend using **FastAPI**.

---

---
# 🎯 Assignment Goal

The assignment required me to:

- Build the smallest possible backend server
- Create two JSON API endpoints
- Test the API using:
  - Browser
  - Swagger UI
  - curl
- Publish the project to GitHub

Although the application contains only a few lines of code, it introduces the complete lifecycle of a backend API.

---

# 🤔 Before Writing Code...

Before writing Python, I wanted to understand:

- What is a Backend?
- What is an API?
- What is a Server?
- What is an Endpoint?
- What is JSON?
- Why do we need FastAPI?

Answering these questions made the implementation much easier.

---

# 🏗 What is a Backend?

Imagine searching for a product on Amazon.

```
Amazon Website

        │

        ▼

Backend Server

        │

        ▼

Database

        │

        ▼

Backend Server

        │

        ▼

Website
```

The website doesn't contain all the data.

Instead,

the backend receives the request,

processes it,

and sends back the response.

---

# 🍽 Restaurant Analogy

One of the easiest ways to understand backend development is through a restaurant.

```
Customer

↓

Waiter

↓

Kitchen

↓

Waiter

↓

Customer
```

Software works exactly the same way.

```
User

↓

Browser

↓

Backend API

↓

Business Logic

↓

Browser
```

The browser never directly accesses the business logic.

Everything goes through the backend.

---

# 📂 Project Structure

```
backend-ai-week1/

│

├── images/

│ ├── project-overview.png

│ ├── api-testing.png

│ └── github-repository.png

│

├── main.py

├── requirements.txt

├── README.md

└── .gitignore
```

---

# 🛠 Technologies Used

- Python
- FastAPI
- Uvicorn
- REST API
- JSON
- Git
- GitHub

---

# 🚀 Step-by-Step Development Process

## Step 1 – Create a Project Folder

Every project should have its own dedicated workspace.

```
backend-ai-week1/
```

This keeps all project files organized.

---

## Step 2 – Create a Virtual Environment

Command:

```bash
python3 -m venv venv
```

### Why?

A virtual environment creates an isolated Python environment for the project.

Without it,

multiple projects would share the same packages,

which can cause version conflicts.

Think of it as giving every project its own private workspace.

---

## Step 3 – Activate the Virtual Environment

macOS/Linux

```bash
source venv/bin/activate
```

After activation,

the terminal displays:

```
(venv)
```

This indicates that every package installed from this point onward belongs only to this project.

---

## Step 4 – Install Required Packages

```bash
pip install fastapi uvicorn
```

### What is pip?

`pip` is Python's package manager.

It downloads libraries from the Python Package Index (PyPI).

### Why FastAPI?

FastAPI makes it easy to create REST APIs using Python.

### Why Uvicorn?

FastAPI creates the application.

Uvicorn runs the application so browsers can communicate with it.

---

## Step 5 – Save Dependencies

```bash
pip freeze > requirements.txt
```

This creates a list of every installed package.

Anyone cloning this repository can recreate the same environment by running:

```bash
pip install -r requirements.txt
```

---

## Step 6 – Create the Backend

Create a file named:

```
main.py
```

---

# 🧠 Understanding Every Line of Code

## Import FastAPI

```python
from fastapi import FastAPI
```

This imports the **FastAPI** class into the program.

Think of it as taking a tool from a toolbox.

Without importing it,

Python doesn't know what FastAPI is.

---

## Create the Application

```python
app = FastAPI()
```

This line creates the backend application.

The variable `app` now represents the entire FastAPI application.

Without this line,

there is no backend.

---

## Create the Home Endpoint

```python
@app.get("/")
def home():
    return {
        "message": "Hello from FlyRank Backend AI Internship!"
    }
```

### What happens here?

- `@app.get("/")` registers the **Home URL**.
- `def home()` creates a Python function.
- `return` sends data back.
- The dictionary is automatically converted into JSON by FastAPI.

Opening:

```
http://127.0.0.1:8000/
```

returns:

```json
{
  "message": "Hello from FlyRank Backend AI Internship!"
}
```

---

## Create the About Endpoint

```python
@app.get("/about")
def about():
    return {
        "name": "Sreepathi Gnaneshwar",
        "track": "Backend AI Engineering",
        "week": 1
    }
```

Opening:

```
http://127.0.0.1:8000/about
```

returns information about the project.

---

# ▶ Running the Application

Start the server:

```bash
uvicorn main:app --reload
```

### What does this command mean?

- `uvicorn` → Starts the web server.
- `main` → Looks for `main.py`.
- `app` → Uses the `app = FastAPI()` object.
- `--reload` → Automatically restarts the server whenever the code changes.

---
# 🚀 Getting Started

Follow the steps below to run this project on your local machine.

---

## Step 1 – Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/Gnaneshwarsreepathi/backend-ai-week1.git
```

---

## Step 2 – Navigate to the Project Folder

```bash
cd backend-ai-week1
```

---

## Step 3 – Verify Python Installation

Check whether Python is installed.

```bash
python3 --version
```

Expected output:

```text
Python 3.x.x
```

If Python is not installed, download it from:

https://www.python.org/downloads/

---

## Step 4 – Create a Virtual Environment

```bash
python3 -m venv venv
```

This creates an isolated Python environment for the project.

---

## Step 5 – Activate the Virtual Environment

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows (Command Prompt)

```cmd
venv\Scripts\activate
```

After activation, your terminal should display:

```text
(venv)
```

---

## Step 6 – Install Project Dependencies

Install all required Python packages.

```bash
pip install -r requirements.txt
```

This command installs every dependency listed in `requirements.txt`.

---

## Step 7 – Start the FastAPI Server

```bash
uvicorn main:app --reload
```

If everything is successful, you should see output similar to:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Leave this terminal running.

---

## Step 8 – Open the Application

Open your browser and visit:

```
http://127.0.0.1:8000/
```

Expected response:

```json
{
    "message": "Hello from FlyRank Backend AI Internship!"
}
```

---

## Step 9 – Test the Second Endpoint

Open:

```
http://127.0.0.1:8000/about
```

Expected response:

```json
{
    "name": "Sreepathi Gnaneshwar",
    "track": "Backend AI Engineering",
    "week": 1
}
```

---

## Step 10 – Open Swagger Documentation

FastAPI automatically generates interactive API documentation.

Open:

```
http://127.0.0.1:8000/docs
```

You can test both endpoints directly from the browser.

---

## Step 11 – Test Using curl

Open a new terminal (keep the server running).

Run:

```bash
curl http://127.0.0.1:8000/
```

Then run:

```bash
curl http://127.0.0.1:8000/about
```

If both commands return JSON responses, the project has been set up successfully.


# 🧪 Testing the API

## Browser

```
http://127.0.0.1:8000/
```

---

## Swagger UI

```
http://127.0.0.1:8000/docs
```

FastAPI automatically generates interactive API documentation.

---

## curl

```bash
curl http://127.0.0.1:8000/
```

```bash
curl http://127.0.0.1:8000/about
```

Using `curl` proves that the backend works independently of the browser.

---

# 🔄 Request → Response Flow

```
Browser

↓

HTTP Request

↓

Uvicorn

↓

FastAPI

↓

Matching Endpoint

↓

Python Function

↓

Python Dictionary

↓

FastAPI converts it to JSON

↓

HTTP Response

↓

Browser
```

This flow is the foundation of backend development.

---

## 📸 Project Overview

<p align="center">
  <img src="images/project-overview.png" alt="Project Overview" width="900">
</p>

---

## 🧪 API Testing

<p align="center">
  <img src="images/api-testing.png" alt="API Testing" width="900">
</p>

---

## 📂 GitHub Repository

<p align="center">
  <img src="images/github-repository.png" alt="GitHub Repository" width="900">
</p>

---

# 🎓 What I Learned

After completing this assignment, I gained practical experience with:

- Backend Fundamentals
- REST APIs
- FastAPI
- Uvicorn
- Python Virtual Environments
- JSON Responses
- HTTP Request–Response Lifecycle
- API Testing
- Git & GitHub

---

# 🚀 Future Improvements

In future weeks, I plan to extend this project by:

- Adding POST endpoints
- Accepting user input
- Connecting to a database
- Implementing CRUD operations
- Deploying the API to the cloud
- Integrating AI models

---

# 👨‍💻 Author

**Sreepathi Gnaneshwar**

Backend AI Engineering Intern @ FlyRank AI

GitHub:
https://github.com/Gnaneshwarsreepathi
