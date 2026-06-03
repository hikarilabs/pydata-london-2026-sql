from typing import Optional, Annotated

from fastapi import HTTPException, Depends
from semantido.generators.semantic_bridge import SQLAlchemySemanticBridge

from db.client import PostgresClient


class AppState:
    """Global application state including semantic layer."""

    def __init__(self):
        self.semantic_bridge: Optional[SQLAlchemySemanticBridge] = None
        self.semantic_layer: str | None = None
        self.ddl_schema: str | None = None
        self.db_client: PostgresClient | None = None


app_state = AppState()

# ---------------------------------------------------------------------------
# FastAPI dependency functions
# ---------------------------------------------------------------------------


def get_db_client() -> PostgresClient:
    if app_state.db_client is None:
        raise HTTPException(status_code=503, detail="Database client not initialised")
    return app_state.db_client


def get_semantic_layer() -> str:
    if app_state.semantic_layer is None:
        raise HTTPException(status_code=503, detail="Semantic layer not initialised")
    return app_state.semantic_layer


def get_ddl_schema() -> Optional[str]:
    """Returns the DDL schema string, or None if not loaded."""
    return app_state.ddl_schema


# Annotated aliases for clean injection in route signatures
DbClient = Annotated[PostgresClient, Depends(get_db_client)]
SemanticLayer = Annotated[str, Depends(get_semantic_layer)]
DdlSchema = Annotated[Optional[str], Depends(get_ddl_schema)]
