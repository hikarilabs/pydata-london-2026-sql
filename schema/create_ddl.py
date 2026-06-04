import models  # registers all models with SemanticDeclarativeBase

from pathlib import Path
from sqlalchemy import create_mock_engine
from sqlalchemy.schema import CreateTable, CreateIndex
from semantido.models.declarative_base import SemanticDeclarativeBase

dialect = create_mock_engine(
    "postgresql+psycopg2://", executor=lambda sql, *a, **kw: None
).dialect

# Pre-generated DDL file
_DEFAULT_SQL_PATH = Path(__file__).parent / "sql" / "schema.sql"


def generate_ddl(output_file: str | None = None) -> str:
    """Generate DDL from SQLAlchemy metadata and optionally write to a file."""
    lines = []

    tables = list(SemanticDeclarativeBase.metadata.sorted_tables)

    for i, table in enumerate(tables, start=1):
        separator = "=" * 77
        lines.append(f"-- {separator}")
        lines.append(f"-- {i}. {table.name}")
        lines.append(f"-- {separator}")

        ddl = str(CreateTable(table).compile(dialect=dialect))
        lines.append(ddl.strip())
        lines.append("")

        for index in table.indexes:
            idx_ddl = str(CreateIndex(index).compile(dialect=dialect))
            lines.append(idx_ddl.strip() + ";")

        lines.append("")

    result = "\n".join(lines)

    if output_file:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result)

    return result


def load_ddl_schema(sql_path: Path = _DEFAULT_SQL_PATH) -> str:
    """
    Load DDL for use at runtime.
    - If the pre-generated file exists, reads it from disk (fast).
    - Otherwise generates it in-memory from the current metadata (fallback).
    """
    if sql_path.exists():
        return sql_path.read_text()

    return generate_ddl(output_file=None)


if __name__ == "__main__":
    generate_ddl(output_file="schema/sql/schema.sql")
