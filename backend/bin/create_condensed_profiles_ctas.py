#!/usr/bin/env python3
import argparse
import duckdb


def main(db_path: str):
    con = duckdb.connect(db_path)
    con.execute(
        """
        CREATE OR REPLACE TABLE condensed_profiles_ctas1 AS
        SELECT taxonomy_id, run_id, relative_abundance, filled_coverage
        FROM condensed_profiles
        ORDER BY taxonomy_id, run_id
        """
    )
    con.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create condensed_profiles_ctas1 table for performance"
    )
    parser.add_argument("db_path", help="Path to DuckDB database file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.db_path)
