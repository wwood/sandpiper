#!/usr/bin/env python3
"""
Calculate disk space usage for each table and index inside a DuckDB database file.
"""

import argparse
import json
from typing import Dict, Iterable, List, Set, Tuple

import duckdb


def _format_size(num_bytes: int) -> str:
    units = ["bytes", "KiB", "MiB", "GiB", "TiB"]
    size = float(num_bytes)
    unit = 0
    while size >= 1024 and unit < len(units) - 1:
        size /= 1024
        unit += 1
    return f"{size:.2f} {units[unit]}"


def _collect_blocks(rows: Iterable[Dict]) -> Tuple[Set[int], Set[int]]:
    data_blocks: Set[int] = set()
    index_blocks: Set[int] = set()

    for row in rows:
        segment_type = str(row.get("segment_type", ""))
        block_id = row.get("block_id")
        additional_blocks = row.get("additional_block_ids")

        target = index_blocks if "INDEX" in segment_type.upper() else data_blocks

        if block_id is not None and block_id >= 0:
            target.add(int(block_id))

        if additional_blocks in (None, ""):
            continue

        if isinstance(additional_blocks, str):
            try:
                additional_blocks = json.loads(additional_blocks)
            except json.JSONDecodeError:
                additional_blocks = []

        for extra in additional_blocks:
            if extra is not None and extra >= 0:
                target.add(int(extra))

    return data_blocks, index_blocks


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
        cursor = con.execute(f"pragma storage_info({qualified_name})")
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        data_blocks, index_blocks = _collect_blocks(rows)
        data_bytes = len(data_blocks) * block_size
        index_bytes = len(index_blocks) * block_size

        print(f"{schema}.{name}:")
        print(f"  table size : {_format_size(data_bytes)} ({len(data_blocks)} blocks)")
        print(f"  index size : {_format_size(index_bytes)} ({len(index_blocks)} blocks)")
        print()


if __name__ == "__main__":
    main()
