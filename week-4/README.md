# FlyRank Week 4 - Authentication API

A secure REST API built using FastAPI and Supabase Authentication.

This project was developed as part of the FlyRank Backend AI Engineering Internship Week 4 assignment.

## Features

- User Sign Up
- User Login
- JWT Access Token Authentication
- Protected API Routes
- Public API Route
- User Profile
- Protected Dashboard
- User Logout
- Supabase Authentication
- Swagger/OpenAPI Documentation
- Bearer Token Authorization

## Tech Stack

- Python 3.12
- FastAPI
- Supabase
- Uvicorn
- Pydantic
- python-dotenv
- Git & GitHub

## Project Structure

```text
week-4-auth-api/
├── main.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

> `.env` is excluded from Git and must never be committed.

## Environment Variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_publishable_key
```

Do not commit your actual `.env` file.

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_REPOSITORY_NAME
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the `.env` file and add your Supabase credentials.

## Run the Server

```bash
python -m uvicorn main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Reference

| Method | Endpoint | Authentication | Description |
|---|---|---|---|
| GET | `/` | No | Server status |
| POST | `/auth/signup` | No | Create a user |
| POST | `/auth/login` | No | Login and receive JWT tokens |
| POST | `/auth/logout` | Yes | Logout authenticated user |
| GET | `/public/info` | No | Public information |
| GET | `/protected/profile` | Yes | Authenticated user's profile |
| GET | `/protected/dashboard` | Yes | Protected dashboard |

## Authentication

Login using:

```text
POST /auth/login
```

A successful login returns an access token and refresh token.

For protected routes, use the access token as a Bearer token.

In Swagger UI:

1. Login using `/auth/login`.
2. Copy the `access_token`.
3. Click **Authorize**.
4. Enter the access token.
5. Access the protected endpoints.

## HTTP Status Codes

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | User created successfully |
| 204 | Logout successful |
| 400 | Missing or invalid input |
| 401 | Missing, invalid, or expired authentication token |

## Swagger UI

Swagger provides interactive API documentation and Bearer token authentication.

Add your Swagger screenshot here:

```markdown
![Swagger UI](screenshots/swagger.png)
```

## Security

Sensitive environment variables are stored in `.env`.

The `.env` file is excluded using `.gitignore` and is never committed to the repository.

JWT access tokens are verified using Supabase Authentication before protected endpoints are accessed.

## Author

Konda Pranavi

FlyRank Backend AI Engineering Internship  
Week 4 - Auth: Login & Protect