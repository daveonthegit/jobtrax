import os
import sqlite3

_BASE = os.path.dirname(os.path.abspath(__file__))
_INSTANCE = os.path.join(_BASE, "instance")


def db_path() -> str:
    return os.path.join(_INSTANCE, "jobtrax.db")


def get_conn() -> sqlite3.Connection:
    os.makedirs(_INSTANCE, exist_ok=True)
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    os.makedirs(_INSTANCE, exist_ok=True)
    schema_path = os.path.join(_BASE, "schema.sql")
    seed_path = os.path.join(_BASE, "seed_statuses.sql")
    with open(schema_path, encoding="utf-8") as f:
        schema = f.read()
    with open(seed_path, encoding="utf-8") as f:
        seed = f.read()
    with get_conn() as conn:
        conn.executescript(schema)
        conn.executescript(seed)


def default_status_id(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT status_id FROM statuses ORDER BY sort_order ASC LIMIT 1"
    ).fetchone()
    if not row:
        raise RuntimeError("statuses table empty — run seed_statuses.sql")
    return int(row["status_id"])


def status_dict(conn: sqlite3.Connection) -> dict[int, str]:
    rows = conn.execute(
        "SELECT status_id, status_name FROM statuses ORDER BY sort_order"
    ).fetchall()
    return {int(r["status_id"]): r["status_name"] for r in rows}
