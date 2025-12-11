#!/usr/bin/env python3
"""
Calculate disk space usage for each table and index inside a DuckDB database file.
"""

import argparse
from typing import List, Tuple

import duckdb


def _format_size(num_bytes: int) -> str:
    units = ["bytes", "KiB", "MiB", "GiB", "TiB"]
    size = float(num_bytes)
    unit = 0
    while size >= 1024 and unit < len(units) - 1:
        size /= 1024
        unit += 1
    return f"{size:.2f} {units[unit]}"


def _describe_database(con: duckdb.DuckDBPyConnection) -> Tuple[int, List[Tuple[str, str]]]:
    size_cursor = con.execute("pragma database_size")
    size_row = dict(zip([col[0] for col in size_cursor.description], size_cursor.fetchone()))
    block_size = int(size_row["block_size"])

    tables_cursor = con.execute(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
        """
    )
    tables = [(schema, name) for schema, name in tables_cursor.fetchall()]
    return block_size, tables


def _quote_identifier(identifier: str) -> str:
    escaped = identifier.replace("\"", "\"\"")
    return f'"{escaped}"'


def _block_counts(con: duckdb.DuckDBPyConnection, qualified_name: str) -> Tuple[int, int]:
    """Return (data_block_count, index_block_count) for the given table.

    Computing this inside DuckDB avoids returning per-segment rows to Python, which
    keeps large databases fast.
    """

    query = f"""
        WITH info AS (SELECT * FROM pragma_storage_info({qualified_name})),
        expanded AS (
            SELECT segment_type, block_id
            FROM info
            WHERE block_id IS NOT NULL AND block_id >= 0

            UNION ALL

            SELECT segment_type, unnest(additional_block_ids) AS block_id
            FROM info
            WHERE additional_block_ids IS NOT NULL
        ),
        deduped AS (
            SELECT DISTINCT segment_type, block_id FROM expanded
        )
        SELECT
            COUNT(CASE WHEN segment_type ILIKE '%INDEX%' THEN 1 END) AS index_blocks,
            COUNT(CASE WHEN segment_type NOT ILIKE '%INDEX%' THEN 1 END) AS data_blocks
        FROM deduped
    """

    cursor = con.execute(query)
    index_blocks, data_blocks = cursor.fetchone()
    return int(data_blocks), int(index_blocks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", help="Path to DuckDB database file")
    args = parser.parse_args()

    con = duckdb.connect(args.database)
    block_size, tables = _describe_database(con)

    print(f"Block size: {_format_size(block_size)}")
    print()

    for schema, name in tables:
        qualified_name = (
            f"{_quote_identifier(schema)}.{_quote_identifier(name)}"
            if schema and schema != "main"
            else _quote_identifier(name)
        )
        data_blocks, index_blocks = _block_counts(con, qualified_name)
        data_bytes = data_blocks * block_size
        index_bytes = index_blocks * block_size

        print(f"{schema}.{name}:")
        print(f"  table size : {_format_size(data_bytes)} ({data_blocks} blocks)")
        print(f"  index size : {_format_size(index_bytes)} ({index_blocks} blocks)")
        print()


if __name__ == "__main__":
    main()
