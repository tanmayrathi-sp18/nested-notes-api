# CLAUDE.md

Guidance for Claude Code (claude.ai/code) in this repo.

## Build and Run Commands
- Run app: `uvicorn app.main:app --reload`
- Lint: `ruff check .`
- Format: `ruff format .`
- Database migrations (Alembic):
  - Create migration: `alembic revision --autogenerate -m "description"`
  - Apply migration: `alembic upgrade head`

## Architecture
FastAPI layered architecture:
- `app/main.py`: Entry point and router registration.
- `app/api/`: HTTP endpoints (Route handlers).
- `app/services/`: Business logic layer.
- `app/repositories/`: Data access layer (SQLAlchemy).
- `app/models/`: SQLAlchemy ORM models.
- `app/schemas/`: Pydantic models for request/response validation.
- `app/core/`: Global configuration, database connection, and security utilities.

## Project Logic & Domain
Nested Notes API. Notes organize into categories.

### Core Entities
- **User**: JWT auth. Owns notes and categories.
- **Category**: Group for notes. Linked to User.
- **Note**: Text content. Linked to User and Category.

### Key Flows
- **Auth**: Signup/Login $\rightarrow$ JWT token $\rightarrow$ `get_current_user` dependency for protected routes.
- **Note Management**: Access via nested paths: `/notes/{category_id}/{note_id}`.
- **Authorization**: Services verify `user_id` ownership before modify/delete.

## Tech Stack
- Language: Python 3.13+
- Framework: FastAPI
- Database: PostgreSQL (via `asyncpg` and `sqlalchemy[asyncio]`)
- Migration Tool: Alembic
- Linting/Formatting: Ruff
- Dependency Management: uv