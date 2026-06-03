from urllib.parse import urlparse, urlunparse, urlencode, parse_qs


def _normalise_url(url: str) -> str:
    """Ensure the URL uses the postgresql+asyncpg scheme and strip any
    libpq-only parameters that asyncpg does not understand (e.g. channel_binding)."""
    asyncpg_unsupported_params = {"channel_binding", "sslmode"}

    parsed = urlparse(url)

    # Fix connection scheme
    if parsed.scheme in ("postgresql", "postgres"):
        parsed = parsed._replace(scheme="postgresql+asyncpg")

    # Strip unsupported query params
    params = parse_qs(parsed.query, keep_blank_values=True)
    filtered = {k: v for k, v in params.items() if k not in asyncpg_unsupported_params}
    parsed = parsed._replace(query=urlencode(filtered, doseq=True))

    return str(urlunparse(parsed))
