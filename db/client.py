import contextlib
import os
from typing import Any

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text, pool


class DatabaseSessionManager:
    def __init__(self, host: str, engine_args=None):
        if engine_args is None:
            engine_args = {"future": True}
        self._engine = create_async_engine(host, **engine_args)
        self._session_maker = async_sessionmaker(autocommit=False, bind=self._engine)

    @property
    def engine(self):
        return self._engine

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise RuntimeError("Session maker is not initialized")

        session = self._session_maker()

        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()

        self._engine = None
        self._session_maker = None


class PostgresClient:
    def __init__(
        self,
        database_url: str,
        ssl_mode: str | None = None,
        default_schema: str = "public",
    ):
        self.database_url = database_url
        self.ssl_mode = ssl_mode
        self.default_schema = default_schema
        self._session_manager = self._create_session_manager()

    @property
    def engine(self):
        return self._session_manager.engine

    @classmethod
    def from_env(cls, env_file: str = None, default_schema: str = "public"):

        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            load_dotenv()

        database_url = os.getenv("SUPABASE_DB_URL")
        if database_url is None:
            raise ValueError("SUPABASE_DB_URL environment variable is required")

        ssl_mode = os.getenv("SUPABASE_DB_SSL_MODE")

        return cls(
            database_url=database_url, ssl_mode=ssl_mode, default_schema=default_schema
        )

    def _create_session_manager(self) -> DatabaseSessionManager:

        connect_args: dict[str, Any] = {
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        }

        if self.ssl_mode:
            connect_args["ssl"] = self.ssl_mode

        engine_args = {
            "future": True,
            "connect_args": connect_args,
            "poolclass": pool.NullPool,
        }

        return DatabaseSessionManager(self.database_url, engine_args=engine_args)

    @contextlib.asynccontextmanager
    async def session(self, schema: str | None = None):
        async with self._session_manager.session() as session:
            target_schema = schema or self.default_schema
            if target_schema:
                await session.execute(text(f"SET search_path TO {target_schema}"))
            yield session

    async def connect(self) -> None:
        """Verify the current connection and print the active schema."""
        async with self.session() as session:
            result = await session.execute(
                text("SELECT current_schema(), current_database()")
            )
            schema, database = result.one()
            print(f"✅ Connected to database='{database}', schema='{schema}'")

    async def execute_query(self, query: str, schema: str | None = None):
        try:
            async with self.session(schema=schema) as session:
                result = await session.execute(text(query))
                return result.fetchall()
        except Exception as e:
            raise

    async def close(self):
        if self._session_manager:
            await self._session_manager.close()
