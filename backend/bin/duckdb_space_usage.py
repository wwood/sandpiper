#!/usr/bin/env python3
"""
Estimate DuckDB table sizes by combining row counts with column width estimates.
The script connects to the provided DuckDB database file, walks all non-system
schemas, and reports the tables sorted by estimated size.
"""
import argparse
import math
import re
from typing import Dict, List, Optional

import duckdb


def quote_identifier(name: str) -> str:
    """Return a DuckDB-quoted identifier."""
    escaped = name.replace("\"", "\"\"")
    return f'"{escaped}"'


def qualify(name: str) -> str:
    """Quote each identifier part in a schema-qualified name."""
    return ".".join(quote_identifier(part) for part in name.split("."))


_FIXED_TYPE_SIZES = {
    "BOOLEAN": 1,
    "BOOL": 1,
    "TINYINT": 1,
    "UTINYINT": 1,
    "SMALLINT": 2,
    "USMALLINT": 2,
    "INTEGER": 4,
    "INT": 4,
    "UINTEGER": 4,
    "UINT": 4,
    "BIGINT": 8,
    "UBIGINT": 8,
    "HUGEINT": 16,
    "UHUGEINT": 16,
    "REAL": 4,
    "FLOAT": 4,
    "DOUBLE": 8,
    "DATE": 4,
    "TIME": 8,
    "TIMESTAMP": 8,
    "TIMESTAMP_TZ": 8,
    "TIMESTAMP_S": 8,
    "TIMESTAMP_MS": 8,
    "TIMESTAMP_NS": 8,
    "INTERVAL": 16,
    "UUID": 16,
}


_DECIMAL_SIZE_THRESHOLDS = [
    (4, 2),
    (9, 4),
    (18, 8),
    (38, 16),
]


def decimal_byte_width(type_spec: str) -> Optional[int]:
    match = re.match(r"DECIMAL\((\d+),(\d+)\)", type_spec)
    if not match:
        return None
    precision = int(match.group(1))
    for limit, width in _DECIMAL_SIZE_THRESHOLDS:
        if precision <= limit:
            return width
    return 16


def is_variable_length_type(type_spec: str) -> bool:
    normalized = type_spec.upper()
    return any(
        normalized.startswith(prefix)
        for prefix in ("VARCHAR", "BLOB", "TEXT"))


def estimate_column_width(type_spec: str, avg_length: Optional[float]) -> int:
    normalized = type_spec.upper()
    if normalized in _FIXED_TYPE_SIZES:
        return _FIXED_TYPE_SIZES[normalized]

    decimal_width = decimal_byte_width(normalized)
    if decimal_width is not None:
        return decimal_width

    if is_variable_length_type(normalized):
        # Assume a modest storage overhead per variable-width value.
        effective_length = avg_length if avg_length is not None else 24
        return int(math.ceil(effective_length + 4))

    # Fallback for unrecognized types.
    return 24


def collect_tables(con: duckdb.DuckDBPyConnection) -> List[str]:
    rows = con.execute(
        """
        SELECT table_schema || '.' || table_name
        FROM information_schema.tables
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY 1
        """
    ).fetchall()
    return [r[0] for r in rows]


def fetch_columns(con: duckdb.DuckDBPyConnection, table: str) -> List[Dict[str, str]]:
    info_rows = con.execute(f"PRAGMA table_info({qualify(table)})").fetchall()
    return [
        {
            "name": r[1],
            "type": r[2],
            "not_null": bool(r[3]),
        }
        for r in info_rows
    ]


def fetch_row_count(con: duckdb.DuckDBPyConnection, table: str) -> int:
    return con.execute(f"SELECT count(*) FROM {qualify(table)}").fetchone()[0]


def fetch_variable_lengths(
    con: duckdb.DuckDBPyConnection, table: str, columns: List[str]
) -> Dict[str, Optional[float]]:
    if not columns:
        return {}

    sample_clause = f"SELECT * FROM {qualify(table)} USING SAMPLE 100 ROWS"
    select_clause = ", ".join(
        f"avg(length({quote_identifier(col)})) AS {quote_identifier(col)}"
        for col in columns
    )
    query = f"WITH sample AS ({sample_clause}) SELECT {select_clause} FROM sample"

    row = con.execute(query).fetchone()
    return {col: row[idx] for idx, col in enumerate(columns)}


def human_bytes(num_bytes: float) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    size = float(num_bytes)
    for unit in units:
        if abs(size) < 1024.0:
            return f"{size:,.1f} {unit}"
        size /= 1024.0
    return f"{size:,.1f} PiB"


def estimate_table_size(
    con: duckdb.DuckDBPyConnection, table: str
) -> Optional[Dict[str, object]]:
    columns = fetch_columns(con, table)
    if not columns:
        return None

    variable_cols = [c["name"] for c in columns if is_variable_length_type(c["type"])]
    avg_lengths = fetch_variable_lengths(con, table, variable_cols)

    row_width = 0.0
    for col in columns:
        avg_len = avg_lengths.get(col["name"]) if variable_cols else None
        width = estimate_column_width(col["type"], avg_len)
        null_overhead = 1 if not col["not_null"] else 0
        row_width += width + null_overhead

    row_count = fetch_row_count(con, table)
    estimated_bytes = row_width * row_count

    return {
        "table": table,
        "rows": row_count,
        "row_width": row_width,
        "estimated_bytes": estimated_bytes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate DuckDB table sizes.")
    parser.add_argument("database", help="Path to DuckDB database file")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only show the top N tables by estimated size.",
    )
    args = parser.parse_args()

    con = duckdb.connect(args.database, read_only=True)

    tables = collect_tables(con)
    if not tables:
        print("No user tables found.")
        return

    estimates = []
    for table in tables:
        result = estimate_table_size(con, table)
        if result:
            estimates.append(result)

    estimates.sort(key=lambda e: e["estimated_bytes"], reverse=True)
    if args.limit is not None:
        estimates = estimates[: args.limit]

    print(f"Estimated table sizes for {args.database}:")
    for est in estimates:
        print(
            f"- {est['table']}: {est['rows']:,} rows, "
            f"~{human_bytes(est['estimated_bytes'])} (row width {est['row_width']:.1f} bytes)"
        )


if __name__ == "__main__":
    main()
