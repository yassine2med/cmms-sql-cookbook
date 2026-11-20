"""Command line: python -m cmmscookbook list|run|sql|init"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys

from . import build_db, format_table, list_queries, query_sql, run_query


def main(argv: list[str] | None = None) -> int:
    """Return 0 on success, 2 for an unknown query or an existing database file."""
    parser = argparse.ArgumentParser(prog="cmmscookbook", description="CMMS SQL cookbook on sample data")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list the bundled queries")
    run = sub.add_parser("run", help="run a query on the sample data")
    run.add_argument("name")
    run.add_argument("--asof", default="2026-11-01", help="date used by aging queries (default 2026-11-01)")
    run.add_argument("--db", help="SQLite file to query instead of the built-in sample")
    show = sub.add_parser("sql", help="print the SQL of a query")
    show.add_argument("name")
    init = sub.add_parser("init", help="write the sample database to a file")
    init.add_argument("path")
    args = parser.parse_args(argv)

    if args.command == "list":
        for name, title in list_queries().items():
            print(f"{name:<22} {title}")
        return 0
    if args.command == "init":
        if os.path.exists(args.path):
            print(f"Refusing to overwrite {args.path}", file=sys.stderr)
            return 2
        build_db(args.path).close()
        print(f"Sample database written to {args.path}")
        return 0
    if args.name not in list_queries():
        print(f"Unknown query: {args.name}. Run 'list' to see the names.", file=sys.stderr)
        return 2
    if args.command == "sql":
        print(query_sql(args.name), end="")
        return 0
    conn = sqlite3.connect(args.db) if args.db else build_db()
    cols, rows = run_query(conn, args.name, args.asof)
    print(format_table(cols, rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
