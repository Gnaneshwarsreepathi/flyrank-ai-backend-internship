# Backend AI Week 1

This repository contains my Week 1 assignment for the FlyRank AI Backend Engineering Internship.

## Project Overview

A minimal FastAPI backend exposing two JSON endpoints.

## Endpoints

### GET /

Returns a welcome message.

Example:

```json
{
  "message": "Hello from FlyRank Backend AI Internship!"
}
```

### GET /about

Returns information about the project.

Example:

```json
{
  "name": "Sreepathi Gnaneshwar",
  "track": "Backend AI Engineering",
  "week": 1
}
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs