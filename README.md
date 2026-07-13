# 🚀 Backend AI Week 1 – FastAPI REST API

This repository contains my **Week 1 assignment** for the **FlyRank AI Backend Engineering Internship**.

The objective of this assignment was to understand how a backend server receives client requests and returns structured JSON responses using **FastAPI**.

---

# 📌 Project Overview

In this project, I built a minimal REST API with two endpoints and tested it using multiple methods.

### Features

- ✅ Built a FastAPI backend server
- ✅ Created two JSON API endpoints
- ✅ Tested APIs using Swagger UI
- ✅ Tested APIs using Browser
- ✅ Tested APIs using `curl`
- ✅ Published the project to GitHub

---

# 🛠 Tech Stack

- Python 3
- FastAPI
- Uvicorn
- REST API
- JSON
- Git
- GitHub

---

# 📂 Project Structure

```text
backend-ai-week1/
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
└── images/
```

---

# 📷 Project Overview

The following screenshot shows the complete project structure, source code, and successful API testing using `curl`.

![Project Overview](images/project-overview.png)

---

# 🌐 API Endpoints

## GET /

Returns a welcome message.

Example Response

```json
{
    "message": "Hello from FlyRank Backend AI Internship!"
}
```

---

## GET /about

Returns information about the project.

Example Response

```json
{
    "name": "Sreepathi Gnaneshwar",
    "track": "Backend AI Engineering",
    "week": 1
}
```

---

# 🧪 API Testing

The APIs were tested using the built-in FastAPI Swagger UI.

![API Testing](images/api-testing.png)

The endpoints were also tested using:

- Browser
- curl
- Swagger UI

---

# ▶️ Run Locally

Clone the repository

```bash
git clone https://github.com/Gnaneshwarsreepathi/backend-ai-week1.git
```

Go to the project

```bash
cd backend-ai-week1
```

Create Virtual Environment

```bash
python3 -m venv venv
```

Activate Virtual Environment

macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
uvicorn main:app --reload
```

Open your browser

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

# 📸 GitHub Repository

The project is published publicly on GitHub.

![GitHub Repository](images/github-repository.png)

Repository Link

**https://github.com/Gnaneshwarsreepathi/backend-ai-week1**

---

# 🎯 Learning Outcomes

Through this assignment, I learned:

- Backend fundamentals
- FastAPI framework
- REST API development
- JSON responses
- Request → Response lifecycle
- API testing using Swagger UI
- API testing using curl
- Git & GitHub workflow

---

# 👨‍💻 Author

**Sreepathi Gnaneshwar**

Backend AI Engineering Intern @ FlyRank AI

GitHub:
https://github.com/Gnaneshwarsreepathi

LinkedIn:
https://lnkd.in/p/eKr-uU3a
