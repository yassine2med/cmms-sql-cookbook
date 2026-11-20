"""SQL cookbook for CMMS work order analytics on a sample SQLite database."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUERY_DIR = HERE / "queries"


def build_db(path: str = ":memory:") -> sqlite3.Connection:
    """Create the schema and load the sample data into a SQLite database."""
    conn = sqlite3.connect(path)
    conn.executescript((HERE / "schema.sql").read_text(encoding="utf-8"))
    conn.executescript((HERE / "seed.sql").read_text(encoding="utf-8"))
    return conn


def list_queries() -> dict[str, str]:
    """Return {name: title} for every bundled query."""
    out = {}
    for f in sorted(QUERY_DIR.glob("*.sql")):
        out[f.stem] = f.read_text(encoding="utf-8").splitlines()[0].lstrip("- ").strip()
    return out


def query_sql(name: str) -> str:
    f = QUERY_DIR / f"{name}.sql"
    if not f.exists():
        raise KeyError(name)
    return f.read_text(encoding="utf-8")


def run_query(conn: sqlite3.Connection, name: str, asof: str | None = None):
    """Run a named query. Returns (column names, rows)."""
    sql = query_sql(name)
    params = {"asof": asof or date.today().isoformat()} if ":asof" in sql else {}
    cur = conn.execute(sql, params)
    return [c[0] for c in cur.description], cur.fetchall()


def format_table(cols: list[str], rows: list) -> str:
    cells = [[str(c) for c in cols]] + [["" if v is None else str(v) for v in r] for r in rows]
    widths = [max(len(r[i]) for r in cells) for i in range(len(cols))]
    lines = ["  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in cells]
    lines.insert(1, "  ".join("-" * w for w in widths))
    return "\n".join(lines)
