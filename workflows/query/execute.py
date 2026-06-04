from typing import Any
from db.client import PostgresClient


async def execute_query(
    sql: str, client: PostgresClient, schema: str = None
) -> list[dict[Any, Any] | dict[str, Any] | dict[str, str] | dict[bytes, bytes]]:
    """
    Executes a SQL query against the database using the provided PostgresClient.
    """
    # execute_query returns a list of SQLAlchemy Row objects
    records = await client.execute_query(sql, schema=schema)

    # Convert the Row objects into dictionaries so they are JSON serializable
    return [dict(record._mapping) for record in records]
