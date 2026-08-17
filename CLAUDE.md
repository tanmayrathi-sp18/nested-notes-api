# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Execution
- **Install dependencies**: `uv sync`
- **Run application**: `uv run uvicorn app.main:app --reload`
- **Activate environment**: `source .venv/bin/activate`

### Code Quality
- **Lint checks**: `uv run ruff check .`
- **Format code**: `uv run ruff format .`

### Database Management
- **Apply migrations**: `uv run alembic upgrade head`
- **Generate migration**: `uv run alembic revision --autogenerate -m "description of change"`

## Architecture

The project follows a **Layered Architecture** (API → Service → Repository → Model) to maintain a strict separation of concerns.

### Layers
- **API Layer (`app/api/`)**: Controllers handling HTTP requests, validation, and response formatting.
- **Service Layer (`app/services/`)**: Business logic, ownership verification, and orchestration. Infrastructure concerns like caching are decoupled using decorators.
- **Repository Layer (`app/repositories/`)**: Encapsulates all SQLAlchemy async queries using atomic SQL operations to prevent race conditions.
- **Model Layer (`app/models/`)**: Defines database schemas and data structures.
- **Schemas (`app/schemas/`)**: Pydantic models for request/response validation and serialization.
- **Core (`app/core/`)**: Shared infrastructure: configuration, database connection, security, caching, and Redis setup.

### Key Technical Implementation Details
- **Caching**: Implemented as a write-through cache using Redis. Handled via the `@cache_result` decorator in the service layer. Uses Pydantic `TypeAdapter` for serialization.
- **Authentication**: JWT-based stateless authentication.
- **Database**: PostgreSQL with `asyncpg` and `SQLAlchemy` (Async).
- **Migrations**: Managed via Alembic.
- **Validation**: Pydantic for type safety and request validation.
