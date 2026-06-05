import asyncio
from db.client import PostgresClient
from db.url_utils import _normalise_url


async def test_neon_client() -> None:
    client = PostgresClient.from_env(default_schema="data_service")

    try:
        # 1. Basic connectivity + schema check
        await client.connect()

        # 2. Confirm the normalized URL scheme is correct
        normalized = _normalise_url(client.database_url)
        scheme = normalized.split("://")[0]
        assert scheme == "postgresql+asyncpg", f"Unexpected scheme: {scheme}"
        print(f"URL scheme correct: '{scheme}'")

        # 3. Confirm channel_binding is stripped from the URL
        assert "channel_binding" not in normalized, "channel_binding was not stripped!"
        print("channel_binding stripped from URL")

        # 4. Quick sanity query against the data_service schema
        rows = await client.execute_query(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'data_service' ORDER BY table_name;",
        )
        table_names = [row[0] for row in rows]
        print(f"Tables found in data_service: {table_names}")

    except AssertionError as e:
        print(f"Assertion failed: {e}")
        raise
    except Exception as e:
        print(f"Connection failed: {e}")
        raise
    finally:
        await client.close()
        print("Connection closed.")


if __name__ == "__main__":
    asyncio.run(test_neon_client())
