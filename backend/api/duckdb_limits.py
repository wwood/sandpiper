"""Utilities to apply DuckDB resource limits consistently."""

from sqlalchemy import event


def configure_duckdb_connection(connection):
    """Apply resource limits to a DuckDB connection."""

    connection.execute("SET memory_limit='1GB'")
    connection.execute("SET threads=2")
    connection.execute("SET temp_directory='/tmp/duckdb_spill'")


def register_duckdb_limits(engine):
    """Ensure DuckDB limits are applied for all SQLAlchemy connections."""

    if getattr(engine, "_duckdb_limits_registered", False):
        return

    @event.listens_for(engine, "connect")
    def _set_duckdb_limits(dbapi_connection, connection_record):  # pragma: no cover - SQLAlchemy hook
        configure_duckdb_connection(dbapi_connection)

    engine._duckdb_limits_registered = True
