# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Run Commands
- Run app: `uvicorn app.main:app --reload`
- Lint: `ruff check .`
- Format: `ruff format .`
- Database migrations (Alembic):
  - Create migration: `alembic revision --autogenerate -m "description"`
  - Apply migration: `alembic upgrade head`

## Architecture
FastAPI application with a layered architecture:
- `app/main.py`: Entry point and router registration.
- `app/api/`: HTTP endpoints (Route handlers).
- `app/services/`: Business logic layer.
- `app/repositories/`: Data access layer (SQLAlchemy).
- `app/models/`: SQLAlchemy ORM models.
- `app/schemas/`: Pydantic models for request/response validation.
- `app/core/`: Global configuration, database connection, and security utilities.

## Project Logic & Domain
Nested Notes API for organizing user notes into categories.

### Core Entities
- **User**: Auth via JWT. Manages own notes and categories.
- **Category**: Grouping for notes. Linked to User.
- **Note**: Text content linked to both a User and a Category.

### Key Flows
- **Auth**: Signup/Login $\rightarrow$ JWT token $\rightarrow$ `get_current_user` dependency for protected routes.
- **Note Management**: Notes accessed via nested paths: `/notes/{category_id}/{note_id}`.
- **Authorization**: Services verify `user_id` ownership before modifying/deleting notes or categories.

## Tech Stack
- Language: Python 3.13+
- Framework: FastAPI
- Database: PostgreSQL (via `asyncpg` and `sqlalchemy[asyncio]`)
- Migration Tool: Alembic
- Linting/Formatting: Ruff
- Dependency Management: uv
