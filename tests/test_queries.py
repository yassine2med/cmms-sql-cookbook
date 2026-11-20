from datetime import datetime

import pytest

from cmmscookbook import build_db, format_table, list_queries, query_sql, run_query
from cmmscookbook.__main__ import main

FMT = "%Y-%m-%d %H:%M"


@pytest.fixture(scope="module")
def conn():
    return build_db()


def all_wo(conn):
    return conn.execute("SELECT wo_id, asset_id, type, priority, status, opened_at, started_at, closed_at, tech_id, labor_hours FROM work_orders").fetchall()


def test_seed_loaded(conn):
    assert conn.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0] == 48
    assert conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == 8


def test_six_queries_listed():
    names = list(list_queries())
    assert len(names) == 6 and "aging_buckets" in names


def test_every_query_has_title_and_runs(conn):
    for name, title in list_queries().items():
        assert title
        cols, rows = run_query(conn, name, "2026-11-01")
        assert cols


def test_backlog_matches_python_count(conn):
    _, rows = run_query(conn, "backlog_by_priority")
    expected = sum(1 for w in all_wo(conn) if w[4] != "Closed")
    assert sum(r[3] for r in rows) == expected
    assert all(r[1] + r[2] == r[3] for r in rows)


def test_backlog_sorted_by_priority(conn):
    _, rows = run_query(conn, "backlog_by_priority")
    assert [r[0] for r in rows] == sorted(r[0] for r in rows)


def test_aging_total_equals_backlog(conn):
    _, rows = run_query(conn, "aging_buckets", "2026-11-01")
    assert sum(r[1] for r in rows) == sum(1 for w in all_wo(conn) if w[4] != "Closed")


def test_aging_changes_with_asof(conn):
    _, early = run_query(conn, "aging_buckets", "2026-06-01")
    _, late = run_query(conn, "aging_buckets", "2027-06-01")
    assert [r[0] for r in late] == ["4: over 90 days"]
    assert early != late


def test_aging_average_matches_python(conn):
    _, rows = run_query(conn, "aging_buckets", "2026-11-01")
    asof = datetime(2026, 11, 1)
    ages = [(asof - datetime.strptime(w[5], FMT)).total_seconds() / 86400 for w in all_wo(conn) if w[4] != "Closed"]
    total = sum(r[1] * r[2] for r in rows)
    assert abs(total - sum(ages)) < 0.1 * len(ages)


def test_mttr_matches_python(conn):
    cols, rows = run_query(conn, "mttr_by_category")
    cats = dict(conn.execute("SELECT asset_id, category FROM assets").fetchall())
    by = {}
    for w in all_wo(conn):
        if w[2] == "CM" and w[4] == "Closed":
            hrs = (datetime.strptime(w[7], FMT) - datetime.strptime(w[6], FMT)).total_seconds() / 3600
            by.setdefault(cats[w[1]], []).append(hrs)
    assert {r[0]: r[1] for r in rows} == {k: len(v) for k, v in by.items()}
    for r in rows:
        assert abs(r[2] - sum(by[r[0]]) / len(by[r[0]])) < 0.06


def test_pm_compliance_between_zero_and_hundred(conn):
    _, rows = run_query(conn, "pm_compliance_by_month")
    assert rows and all(0 <= r[3] <= 100 for r in rows)
    assert sum(r[1] for r in rows) == sum(1 for w in all_wo(conn) if w[2] == "PM")


def test_repeat_failures_threshold(conn):
    _, rows = run_query(conn, "repeat_failures")
    assert rows and all(r[2] >= 3 for r in rows)


def test_technician_workload_counts(conn):
    _, rows = run_query(conn, "technician_workload")
    assert sum(r[2] for r in rows) == sum(1 for w in all_wo(conn) if w[4] == "Closed" and w[8] is not None)


def test_schema_rejects_bad_priority(conn):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO work_orders VALUES (1,'AHU-01','CM',9,'Open','2026-01-01 08:00',NULL,NULL,NULL,0,'x')")


def test_format_table_aligns():
    text = format_table(["a", "bb"], [(1, "x"), (22, None)])
    assert text.splitlines()[0].startswith("a ") and len(text.splitlines()) == 4


def test_cli_run_list_sql_and_errors(capsys, tmp_path):
    assert main(["run", "backlog_by_priority"]) == 0
    assert "priority" in capsys.readouterr().out
    assert main(["list"]) == 0
    assert main(["sql", "mttr_by_category"]) == 0
    assert main(["run", "nope"]) == 2
    db = tmp_path / "c.db"
    assert main(["init", str(db)]) == 0
    assert main(["init", str(db)]) == 2
    assert main(["run", "repeat_failures", "--db", str(db)]) == 0
    assert query_sql("aging_buckets").startswith("-- Aging")
