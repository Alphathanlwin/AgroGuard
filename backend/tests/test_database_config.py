from app.db.session import make_async_database_url


def test_async_database_url_converts_driver_and_supabase_sslmode() -> None:
    url = make_async_database_url(
        "postgresql+psycopg://postgres:secret@db.example.com:5432/agroguard"
        "?sslmode=require"
    )

    assert url.drivername == "postgresql+asyncpg"
    assert url.query == {"ssl": "require"}


def test_async_database_url_preserves_pooler_query_options() -> None:
    url = make_async_database_url(
        "postgresql://postgres:secret@pooler.example.com:6543/postgres"
        "?sslmode=require&prepared_statement_cache_size=0"
    )

    assert url.drivername == "postgresql+asyncpg"
    assert url.query == {
        "ssl": "require",
        "prepared_statement_cache_size": "0",
    }
