# Semantic layer project for Pydata London 2026

# Setup instructions:

Instant postgres database valid for 72 hours https://neon.new


Generate schema DDL based on current SQLAlcheny models:
```bash
uv run python -m schema.create_ddl
```
