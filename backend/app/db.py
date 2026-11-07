from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .config import DB_PATH, ensure_dirs

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
SCHEMA_VERSION = 3


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def json_loads(value: Any, default: Any = None) -> Any:
    if value is None or value == "":
        return default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def connect() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


@contextmanager
def db_cursor():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    with db_cursor() as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def fetch_one(sql: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    with db_cursor() as conn:
        row = conn.execute(sql, tuple(params)).fetchone()
        return dict(row) if row else None


def execute(sql: str, params: Iterable[Any] = ()) -> int:
    with db_cursor() as conn:
        cur = conn.execute(sql, tuple(params))
        return cur.rowcount


def execute_many(sql: str, seq: Iterable[Iterable[Any]]) -> int:
    with db_cursor() as conn:
        cur = conn.executemany(sql, seq)
        return cur.rowcount


def insert_returning_id(sql: str, params: Iterable[Any] = ()) -> int:
    with db_cursor() as conn:
        cur = conn.execute(sql, tuple(params))
        return int(cur.lastrowid)


def get_setting(key: str, default: Any = None) -> Any:
    row = fetch_one("SELECT value FROM settings WHERE key=?", (key,))
    return row["value"] if row else default


def set_setting(key: str, value: Any) -> None:
    execute(
        "INSERT INTO settings(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )


def audit(action: str, details: str | dict | None = None, actor: str = "local") -> None:
    if isinstance(details, (dict, list)):
        details = json_dumps(details)
    execute(
        "INSERT INTO audit_log(actor, action, details, created_at) VALUES(?,?,?,?)",
        (actor, action, details or "", utcnow()),
    )


# Colonnes ajoutées après la première version : CREATE TABLE IF NOT EXISTS ne modifie pas une table existante.
ADDED_COLUMNS = {
    "threat_items": {"epss": "REAL", "epss_percentile": "REAL"},
    "findings": {"ai_verdict": "TEXT NOT NULL DEFAULT ''", "ai_notes": "TEXT NOT NULL DEFAULT ''", "ai_at": "TEXT"},
    "income_opportunities": {"proposal_draft": "TEXT NOT NULL DEFAULT ''"},
}


def _add_missing_columns(conn: sqlite3.Connection) -> None:
    for table, columns in ADDED_COLUMNS.items():
        existing = {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}
        for name, ddl in columns.items():
            if name not in existing:
                conn.execute(f'ALTER TABLE "{table}" ADD COLUMN {name} {ddl}')


def init_db() -> None:
    ensure_dirs()
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with db_cursor() as conn:
        conn.executescript(schema)
        _add_missing_columns(conn)
        current = conn.execute("PRAGMA user_version").fetchone()[0]
        if current < SCHEMA_VERSION:
            conn.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
        fts_init = conn.execute("SELECT value FROM settings WHERE key='intel_fts_initialized'").fetchone()
        if not fts_init:
            conn.execute("INSERT INTO threat_fts(threat_fts) VALUES('rebuild')")
            conn.execute("INSERT INTO settings(key,value) VALUES('intel_fts_initialized','1')")
    # Import tardif pour éviter un cycle.
    from .seed import seed_all

    seed_all()


def health_db() -> dict[str, Any]:
    with db_cursor() as conn:
        conn.execute("SELECT 1").fetchone()
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        fts = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_fts'"
        ).fetchone()
        return {"ok": True, "schema_version": version, "fts5": bool(fts), "path": str(DB_PATH)}
