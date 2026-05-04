import os
import sqlite3

_BASE = os.path.dirname(os.path.abspath(__file__))
_INSTANCE = os.path.join(_BASE, "instance")


def db_path() -> str:
    return os.path.join(_INSTANCE, "jobtrax.db")


def _table_column_names(conn: sqlite3.Connection, table: str) -> set[str]:
    """Return quoted SQLite identifier column names for `table` (empty if table missing)."""
    rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    return {str(r[1]) for r in rows}


def migrate_legacy_fk_columns(conn: sqlite3.Connection) -> None:
    """
    Align older DB files with current schema: FK columns renamed to match parent PK names.
    Safe to run repeatedly; no-ops when already migrated. Requires SQLite 3.25+ (RENAME COLUMN).
    """
    # Applications: current_status_id -> status_id
    apps = _table_column_names(conn, "applications")
    if apps and "current_status_id" in apps:
        conn.execute(
            "ALTER TABLE applications RENAME COLUMN current_status_id TO status_id"
        )

    parsed = _table_column_names(conn, "parsed_inputs")
    if parsed and "parsed_status_id" in parsed:
        conn.execute(
            "ALTER TABLE parsed_inputs RENAME COLUMN parsed_status_id TO status_id"
        )

    hist = _table_column_names(conn, "application_status_history")
    if hist and "source_parse_id" in hist:
        conn.execute(
            "ALTER TABLE application_status_history RENAME COLUMN source_parse_id TO parse_id"
        )


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
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.executescript(schema)
        migrate_legacy_fk_columns(conn)
        conn.execute("PRAGMA foreign_keys = ON")
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
