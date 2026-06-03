import os
from contextlib import asynccontextmanager

import logfire

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from semantido import SQLAlchemySemanticBridge, SemanticDeclarativeBase
from starlette.responses import JSONResponse

from db.client import PostgresClient
from dependencies.state import app_state
from routes import semantic

service_name = os.getenv("LOGFIRE_SERVICE_NAME")
environment = os.getenv("LOGFIRE_ENV")
logfire.configure(service_name=service_name, environment=environment)

logfire.instrument_pydantic_ai()
logfire.instrument_asyncpg()

app = FastAPI()
logfire.instrument_fastapi(app)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        print("🚀 Starting application...")

        print("📚 Initializing semantic layer...")
        app_state.semantic_bridge = SQLAlchemySemanticBridge(SemanticDeclarativeBase)

        # Sync semantic layer from models
        semantic_models = app_state.semantic_bridge.sync_from_models()
        app_state.semantic_layer = semantic_models.to_json()

        # Startup: Initialize workout database connection pool
        print("Initializing workout database connection...")
        db_client = PostgresClient.from_env(default_schema="data_service")
        await db_client.connect()
        app_state.db_client = db_client
        print("🚀 Connected to workout database")

        print("🚀 Application started...")
        yield

        # Shutdown: Close the Postgres connection pool gracefully
        print("Closing database connection...")
        await db_client.close()

    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise  # <-- re-raise so FastAPI surfaces the real error


app = FastAPI(
    title="Semantic Service",
    description=(
        "A metadata-driven service that exposes the schema through a Semantic Layer."
        "It translates SQLAlchemy models into a machine-readable format optimized for "
        "LLM Agents, Model Context Protocol (MCP) servers, and Natural Language-to-SQL interfaces."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(semantic.router)

# Allow requests from your Next.js Vercel frontend
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handlers for clean error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with a clean, user-friendly format.
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": errors,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with consistent formatting.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unexpected errors.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
        },
    )
