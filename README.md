# 📝 Nested Notes API

A high-performance, scalable REST API for managing hierarchical notes. The system allows users to organize thoughts into nested structures, ensuring a clean separation between categories and notes while providing low-latency access through an intelligent caching layer.

## 🏗 Architecture

This project employs a **Layered Architecture** (API → Service → Repository → Model). This approach ensures a strict separation of concerns:

-   **API Layer (Controllers)**: Handles HTTP parsing, request validation, and response formatting. It uses global exception handlers to map domain errors to HTTP responses.
-   **Service Layer**: The "Brain" of the application. It orchestrates business rules and manages ownership verification. Infrastructure concerns (like caching) are decoupled using **Custom Decorators**, keeping service methods pure.
-   **Repository Layer**: Encapsulates all SQLAlchemy queries. It utilizes **Atomic SQL Operations** (via `update()` and `delete()`) to prevent race conditions and maximize performance.
-   **Model Layer**: Defines the data structures and database schemas.

**Why this approach?**
By decoupling business logic from data access and the transport protocol, the system is highly maintainable and resilient to concurrency issues. Moving infrastructure logic into decorators and global handlers ensures that the service layer remains focused on core business rules.

## 🛠 Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.13 | Latest features and performance improvements. |
| **Framework** | FastAPI | Asynchronous, type-safe web framework with auto-generated OpenAPI docs. |
| **Database** | PostgreSQL | Relational storage for structured user and note data. |
| **ORM** | SQLAlchemy (Async) | Efficient asynchronous database interactions. |
| **Migrations** | Alembic | Database versioning and schema evolution. |
| **Caching** | Redis | Write-through caching to reduce DB load for frequently accessed notes. |
| **Package Manager**| `uv` | Ultra-fast Python package installation and environment management. |
| **Linter/Formatter**| Ruff | Extremely fast Python linting and formatting. |

## ✨ Key Features

-   **JWT Authentication**: Secure, stateless user authentication using JSON Web Tokens.
-   **Hierarchical Organization**: Support for nested notes, allowing users to create deep organizational trees of information.
-   **Strict Ownership Verification**: Middleware and service-level checks ensure users can only access or modify their own data.
-   **Intelligent Caching**: 
    -   **Decorator-Based**: Caching is handled via a high-performance `@cache_result` decorator, decoupling infrastructure from business logic.
    -   **Serialization**: Uses Pydantic `TypeAdapter` for efficient, type-safe serialization of complex data structures.
    -   **Invalidation**: Precise cache purging on entity updates to prevent stale data.

## ⚙️ How it Works: The Request Lifecycle

When a request hits the API (e.g., `GET /notes/{id}`), the following flow occurs:

1.  **API Layer**: The request is validated. The JWT is extracted from the header to identify the user.
2.  **Service Layer**: 
    -   **Auth Check**: The service verifies if the requested note belongs to the authenticated user.
    -   **Cache Lookup**: The service checks Redis for the note. If a hit occurs, the data is returned immediately.
    -   **Database Fallback**: On a cache miss, the Service calls the Repository.
3.  **Repository Layer**: Executes an async SQL query to fetch the note from PostgreSQL.
4.  **Service Layer (Post-process)**: On a cache miss, the result is serialized via Pydantic and stored back into Redis for future requests.
5.  **API Layer**: Returns the final JSON response to the client.

## 🚀 Getting Started

### Prerequisites
-   Python 3.13+
-   PostgreSQL
-   Redis

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/nested-notes-api.git
   cd nested-nodes-api
   ```

2. **Setup environment with `uv`**
   ```bash
   uv sync
   source .venv/bin/activate
   ```

3. **Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
   REDIS_URL=redis://localhost:6379/0
   JWT_SECRET=your_super_secret_key
   ```

4. **Database Migrations**
   ```bash
   uv run alembic upgrade head
   ```

5. **Run the Application**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`. Access the interactive docs at `/docs`.

## 🛣 API Overview

### 🔐 Authentication
- `POST /auth/register` - Create a new account.
- `POST /auth/token` - Login and receive a JWT.

### 📂 Categories
- `GET /categories` - List all user categories.
- `POST /categories` - Create a new organizational category.

### 📝 Notes
- `GET /notes` - Retrieve notes (supports nesting filters).
- `POST /notes` - Create a new note (can be nested under another note).
- `GET /notes/{id}` - Fetch a specific note (Cache-enabled).
- `PATCH /notes/{id}` - Update note content (Triggers cache invalidation).
- `DELETE /notes/{id}` - Remove a note and its children.

## 🛠 Development Workflow

### Linting & Formatting
We use **Ruff** for all code quality checks.
```bash
# Check for linting errors
uv run ruff check .

# Automatically fix linting and format code
uv run ruff format .
```

### Database Changes
All schema changes must be handled via Alembic.
```bash
# Generate a migration script after changing models
uv run alembic revision --autogenerate -m "description of change"

# Apply the migration
uv run alembic upgrade head
```
