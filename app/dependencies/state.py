from typing import Optional
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
