# Backend Stage 1 - FastAPI Job Search App

This scaffold contains the Stage 1 project setup & architecture for the FastAPI backend.
It includes example files for configuration, initial routers, database connection, Docker, and env examples.

## What is included
- `app/` - FastAPI application package with starter modules
- `requirements.txt` - Python deps
- `.env.example` - environment variables example
- `Dockerfile` & `docker-compose.yml` - containerization helpers
- `alembic/` placeholder note for migrations
- `README.md` - this file

## Quick start (local)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/jobdb
uvicorn app.main:app --reload --port 8000
```
