# PyData London 2026 SQL Semantic Service

A sample Python project demonstrating a semantic layer for SQL-backed applications using **Semantido**, **SQLAlchemy**, **FastAPI**, and **Pydantic AI**.

The service exposes database schema metadata as a machine-readable semantic layer that can be consumed by LLM agents, natural-language-to-SQL workflows, and other application integrations. It includes:

- A FastAPI application for serving semantic metadata and chat/query endpoints
- SQLAlchemy models annotated with semantic descriptions
- Alembic migrations for managing the database schema
- A database seed script for loading example data
- Environment-driven configuration via `.env`
- Dependency and environment management with `uv`

## Project structure

```text
pydata-london-2026-sql/
├── agents/
│   ├── analyst/
│   ├── intent_validator/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── prompts.py
│   ├── sql_generator/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── prompts.py
│   ├── sql_validator/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── __init__.py
│   └── shared.py
├── alembic/
├── app/
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── convertors.py
│   │   ├── logger.py
│   │   └── state.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── semantic.py
│   ├── __init__.py
│   └── app.py
├── data/
│   ├── __init__.py
│   └── seed.py
├── db/
│   ├── __init__.py
│   ├── client.py
│   ├── test_client.py
│   └── url_utils.py
├── models/
│   ├── __init__.py
│   ├── account_product_map.py
│   ├── accounts.py
│   ├── customer_account_map.py
│   ├── customers.py
│   ├── products.py
│   ├── transaction_category.py
│   └── transactions.py
├── schema/
│   ├── __init__.py
│   ├── create_ddl.py
│   └── sql/
│       └── schema.sql
├── workflows/
│   ├── chat/
│   │   ├── __init__.py
│   │   └── workflow.py
│   ├── query/
│   │   ├── __init__.py
│   │   ├── execute.py
│   │   └── serialiser.py
│   ├── __init__.py
│   ├── context.py
│   └── steps.py
├── .env
├── .gitignore
├── .python-version
├── alembic.ini
├── LICENSE
├── main.py
├── pyproject.toml
├── questions.txt
├── README.md
└── uv.lock
```

## Requirements

- Python `>=3.13`
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- A PostgreSQL-compatible database
- A configured `.env` file

## Environment variables

Create a `.env` file in the project root.

At minimum, the application expects:

```dotenv
DB_URL=postgresql://user:password@host:5432/database 
DB_SSL_MODE=require
LOGFIRE_SERVICE_NAME=semantic-service 
LOGFIRE_ENV=local
```

### Notes

- `DB_URL` is required.
- `DB_SSL_MODE` is optional, but commonly required for hosted PostgreSQL providers.
- The application uses the `data_service` schema by default.
- Add any provider-specific API keys required by your LLM or agent configuration.

For local development, your `.env` may look like:

```dotenv
DB_URL=postgresql://postgres:postgres@localhost:5432/semantic_service
DB_SSL_MODE=
LOGFIRE_SERVICE_NAME=semantic-service 
LOGFIRE_ENV=local
```


## Install dependencies

This project uses `uv`.
From the project root, run:

```bash
uv sync
```
To include development dependencies such as `ruff`, run:
```bash
uv sync --dev
```

## Database setup

The database schema is managed by Alembic.

### 1. Configure the database

Make sure your `.env` file contains a valid `DB_URL`.

Example:
```dotenv
DB_URL=postgresql://postgres:postgres@localhost:5432/semantic_service
DB_SSL_MODE=
```

If your database requires SSL, use:
```dotenv
 DB_SSL_MODE=require
```


### 2. Run migrations

Apply all migrations:
```bash
uv run alembic upgrade head
```


This creates or updates the database schema expected by the application.

### 3. Seed example data

The project includes an example seed script under `data/`.

Run:
```bash
uv run python -m data.seed
```


Use this after migrations to populate the database with sample data for local testing and demos.

## Run the application

Start the FastAPI service with:
```bash
uv run python main.py
```

The server starts on:
```text
http://0.0.0.0:8000
```

## Useful endpoints

Once the service is running, useful endpoints include:

| Endpoint | Description |
| --- | --- |
| `GET /view/semantic` | HTML view of the generated semantic layer |
| `GET /view/semantic/markdown` | Markdown representation of the semantic layer for LLM consumption |
| `GET /view/ddl` | DDL/schema view |
| `POST /chat/...` | Chat or query workflow endpoints, depending on route configuration |

FastAPI also exposes interactive API documentation at:
