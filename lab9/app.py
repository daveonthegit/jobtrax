#
#   Lab 9: Aggregate functions & window functions (SQLite + Flask)
#

import os
import sqlite3

from flask import Blueprint, render_template

lab9_bp = Blueprint(
    "lab9",
    __name__,
    template_folder="templates",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "mydatabase.db")

# Lab 9 sample database (Member, Tournament, Entry) for aggregate / window demos.
SCHEMA_SCRIPT = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Entry;
DROP TABLE IF EXISTS Tournament;
DROP TABLE IF EXISTS Member;

CREATE TABLE Member (
    member_id         INTEGER PRIMARY KEY,
    member_last_name  VARCHAR(50) NOT NULL,
    member_first_name VARCHAR(50) NOT NULL,
    member_gender     CHAR(1) CHECK (member_gender IN ('M', 'F')),
    member_handicap   INTEGER,
    member_coach_id   INTEGER,
    FOREIGN KEY (member_coach_id) REFERENCES Member (member_id)
);

CREATE TABLE Tournament (
    tournament_id   INTEGER PRIMARY KEY,
    tournament_name VARCHAR(100) NOT NULL,
    tournament_type VARCHAR(50)
);

CREATE TABLE Entry (
    entry_member_id     INTEGER NOT NULL,
    entry_tournament_id INTEGER NOT NULL,
    entry_year          INTEGER,
    PRIMARY KEY (entry_member_id, entry_tournament_id, entry_year),
    FOREIGN KEY (entry_member_id) REFERENCES Member (member_id),
    FOREIGN KEY (entry_tournament_id) REFERENCES Tournament (tournament_id)
);

INSERT INTO Member (
    member_id, member_last_name, member_first_name, member_gender,
    member_handicap, member_coach_id
) VALUES
    (118, 'McKenzie', 'Melissa', 'F', 30, 153),
    (138, 'Stone', 'Michael', 'M', 30, NULL),
    (153, 'Nolan', 'Brenda', 'F', 11, NULL),
    (176, 'Branch', 'Helen', 'F', NULL, NULL),
    (178, 'Beck', 'Sarah', 'F', NULL, NULL),
    (228, 'Burton', 'Sandra', 'F', 26, 153),
    (235, 'Cooper', 'William', 'M', 14, 153),
    (239, 'Spence', 'Thomas', 'M', 10, NULL),
    (258, 'Olson', 'Barbara', 'F', 16, NULL),
    (286, 'Pollard', 'Robert', 'M', 19, 235),
    (290, 'Sexton', 'Thomas', 'M', 26, 235),
    (323, 'Wilcox', 'Daniel', 'M', 3, NULL),
    (331, 'Schmidt', 'Thomas', 'M', 25, 153),
    (332, 'Bridges', 'Deborah', 'F', 12, 235),
    (339, 'Young', 'Betty', 'F', 21, NULL),
    (414, 'Gilmore', 'Jane', 'F', 5, 153),
    (415, 'Taylor', 'William', 'M', 7, 235),
    (461, 'Reed', 'Robert', 'M', 3, 235),
    (469, 'Willis', 'Carolyn', 'F', 29, NULL),
    (487, 'Kent', 'Susan', 'F', NULL, NULL);

INSERT INTO Tournament (tournament_id, tournament_name, tournament_type) VALUES
    (1, 'League Spring', 'Open'),
    (2, 'Club Championship', 'Closed'),
    (3, 'Open Invitational', 'Open');

INSERT INTO Entry (entry_member_id, entry_tournament_id, entry_year) VALUES
    (118, 1, 2023), (118, 2, 2023), (118, 3, 2024),
    (138, 1, 2023), (138, 3, 2024),
    (153, 2, 2023),
    (228, 1, 2023), (228, 2, 2024),
    (235, 1, 2023), (235, 2, 2023), (235, 3, 2024),
    (239, 3, 2024),
    (258, 1, 2023), (258, 2, 2023),
    (286, 1, 2024), (286, 2, 2024),
    (290, 3, 2023),
    (331, 2, 2023), (331, 3, 2024),
    (332, 1, 2023), (332, 2, 2023),
    (414, 1, 2024),
    (415, 2, 2023), (415, 3, 2023),
    (461, 1, 2023), (461, 2, 2024), (461, 3, 2024);
"""


def init_db() -> None:
    """Create tables and seed data in mydatabase.db."""
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_SCRIPT)


def needs_lab9_db() -> bool:
    """True if DB is missing, unreadable, or never initialized (empty upload on PythonAnywhere)."""
    if not os.path.isfile(db_path):
        return True
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='Member'"
            )
            if cur.fetchone() is None:
                return True
            cur = conn.execute("SELECT COUNT(*) FROM Member")
            if cur.fetchone()[0] == 0:
                return True
        return False
    except sqlite3.Error:
        return True


def init_db_if_needed() -> None:
    if needs_lab9_db():
        init_db()


def query_rows(sql: str):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        fetched = cur.fetchall()
    if not fetched:
        return [], []
    columns = list(fetched[0].keys())
    rows = [dict(r) for r in fetched]
    return columns, rows


@lab9_bp.route("/", strict_slashes=False)
def home():
    return render_template("lab9_home.html")


@lab9_bp.route("/count-women")
def count_women():
    sql = """
SELECT COUNT(*) AS NumberWomen
FROM Member
WHERE member_gender = 'F';
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="COUNT(*) — women in Member",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
    )


@lab9_bp.route("/count-with-coach")
def count_with_coach():
    sql = """
SELECT
    (SELECT COUNT(*) FROM Member WHERE member_coach_id IS NOT NULL) AS count_star_where_not_null,
    (SELECT COUNT(member_coach_id) FROM Member) AS count_column;
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="COUNT(*) vs COUNT(member_coach_id)",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
        note=(
            "Both expressions count non-null coach assignments: "
            "COUNT(*) with WHERE member_coach_id IS NOT NULL, "
            "and COUNT(member_coach_id) which ignores NULLs by definition."
        ),
    )


@lab9_bp.route("/count-distinct-coaches")
def count_distinct_coaches():
    sql = """
SELECT COUNT(DISTINCT member_coach_id) AS distinct_coach_ids
FROM Member;
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="COUNT(DISTINCT member_coach_id)",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
        note='Answers "how many distinct coaches appear?" (NULL excluded).',
    )


@lab9_bp.route("/avg-handicap")
def avg_handicap():
    sql = """
SELECT
    AVG(member_handicap) AS avg_plain,
    AVG(member_handicap * 1.0) AS avg_times_one,
    ROUND(AVG(member_handicap * 1.0), 2) AS avg_rounded_2
FROM Member;
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="AVG() and ROUND()",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
        note=(
            "SQLite treats AVG() as floating-point here. Multiplying by 1.0 is a "
            "portable habit for engines that average integers as integers."
        ),
    )


@lab9_bp.route("/max-min-avg")
def max_min_avg():
    sql = """
SELECT MAX(member_handicap) AS maximum,
       MIN(member_handicap) AS minimum,
       ROUND(AVG(member_handicap * 1.0), 2) AS average
FROM Member;
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="MAX(), MIN(), AVG() together",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
    )


@lab9_bp.route("/group-entries")
def group_entries():
    sql = """
SELECT entry_member_id,
       COUNT(*) AS NumEntries
FROM Entry
GROUP BY entry_member_id
ORDER BY entry_member_id;
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="GROUP BY entry_member_id",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
        note="One row per member: how many tournament entries they have.",
    )


@lab9_bp.route("/above-average-handicap")
def above_average_handicap():
    sql = """
SELECT *
FROM Member
WHERE member_handicap > (
    SELECT AVG(member_handicap)
    FROM Member
)
ORDER BY member_id;
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="Nested query — handicap above average",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
        note="Inner query computes one average; outer query filters members (NULL handicap excluded from comparison).",
    )


@lab9_bp.route("/avg-entry-counts")
def avg_entry_counts():
    sql = """
SELECT AVG(NewTable.CountEntries) AS avg_entries_per_member
FROM (
    SELECT entry_member_id,
           COUNT(*) AS CountEntries
    FROM Entry
    GROUP BY entry_member_id
) AS NewTable;
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="Average of per-member entry counts",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
        note=(
            "The inner query builds one row per member with their entry count; "
            "the outer query averages those counts. Lab handouts sometimes write "
            "MemberID — here the column is entry_member_id."
        ),
    )


@lab9_bp.route("/window-handicap-rank")
def window_handicap_rank():
    sql = """
SELECT member_id,
       member_last_name,
       member_first_name,
       member_handicap,
       ROW_NUMBER() OVER (
           ORDER BY (member_handicap IS NULL), member_handicap, member_id
       ) AS handicap_rank
FROM Member
ORDER BY handicap_rank;
"""
    columns, rows = query_rows(sql)
    return render_template(
        "aggregate_result.html",
        title="Window function — ROW_NUMBER() OVER",
        sql=sql.strip(),
        columns=columns,
        rows=rows,
        note=(
            "Requires SQLite 3.25+ for window functions. "
            "NULL handicaps are ordered last via (member_handicap IS NULL)."
        ),
    )


init_db_if_needed()

if __name__ == "__main__":
    from flask import Flask

    _app = Flask(__name__)
    _app.register_blueprint(lab9_bp)
    _app.run(debug=True)
