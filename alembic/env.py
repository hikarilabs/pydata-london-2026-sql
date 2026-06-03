import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from db.url_utils import _normalise_url

config = context.config

env_file = os.getenv("ENV_FILE", ".env")
load_dotenv(env_file)


def get_url() -> str:
    """Return a normalized asyncpg-compatible URL from DB_URL env var."""
    url = os.getenv("DB_URL")
    if not url:
        raise ValueError("DB_URL not found in environment variables")
    return _normalise_url(url)


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import models  # noqa: E402
from semantido import SemanticDeclarativeBase  # noqa: E402

target_metadata = SemanticDeclarativeBase.metadata


def include_object(db_object, name, type_, reflected, compare_to):
    if type_ == "table":
        return db_object.schema == "data_service"
    return True


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name == "data_service"
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()  # use normalised URL, not the ini placeholder
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        version_table_schema="data_service",
        include_schemas=True,
        include_object=include_object,
        include_name=include_name,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    connection.execute(text("COMMIT"))
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS data_service"))
    connection.execute(text("COMMIT"))

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema="data_service",
        include_schemas=True,
        include_name=include_name,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()  # normalised URL

    ssl_mode = os.getenv("DB_SSL_MODE")

    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "server_settings": {"search_path": "public"},
    }

    if ssl_mode:
        connect_args["ssl"] = ssl_mode

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
