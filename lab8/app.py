#
#   Lab 8: SQLite + Flask (deploy via root flask_app / PythonAnywhere WSGI)
#

import os
import sqlite3

from flask import Blueprint, render_template

lab8_bp = Blueprint(
    "lab8",
    __name__,
    template_folder="templates",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "mydatabase.db")

# ClubA / ClubB must share identical columns for SELECT * … UNION … SELECT *
# Member / Tournament / Entry match Lab 9 seed data for the division query.
LAB8_SCHEMA_SCRIPT = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Entry;
DROP TABLE IF EXISTS Tournament;
DROP TABLE IF EXISTS Member;
DROP TABLE IF EXISTS ClubB;
DROP TABLE IF EXISTS ClubA;

CREATE TABLE ClubA (
    cluba_id INTEGER PRIMARY KEY,
    cluba_last_name TEXT NOT NULL,
    cluba_first_name TEXT NOT NULL,
    cluba_handicap INTEGER,
    cluba_member_type TEXT NOT NULL
);

CREATE TABLE ClubB (
    cluba_id INTEGER PRIMARY KEY,
    cluba_last_name TEXT NOT NULL,
    cluba_first_name TEXT NOT NULL,
    cluba_handicap INTEGER,
    cluba_member_type TEXT NOT NULL
);

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

INSERT INTO ClubA (
    cluba_id, cluba_last_name, cluba_first_name, cluba_handicap, cluba_member_type
) VALUES
    (10, 'Smith', 'Alice', 12, 'Regular'),
    (11, 'Jones', 'Bob', 14, 'Regular'),
    (12, 'Chen', 'Wei', 9, 'Guest');

INSERT INTO ClubB (
    cluba_id, cluba_last_name, cluba_first_name, cluba_handicap, cluba_member_type
) VALUES
    (11, 'Jones', 'Bob', 14, 'Regular'),
    (12, 'Chen', 'Wei', 9, 'Guest'),
    (20, 'Park', 'Sam', 11, 'Regular');

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


def init_lab8_db() -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executescript(LAB8_SCHEMA_SCRIPT)


def needs_lab8_db() -> bool:
    """True if DB file is missing or required tables are not present (PythonAnywhere)."""
    if not os.path.isfile(db_path):
        return True
    try:
        with sqlite3.connect(db_path) as conn:
            for tbl in ("ClubA", "ClubB", "Member"):
                cur = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                    (tbl,),
                )
                if cur.fetchone() is None:
                    return True
        return False
    except sqlite3.Error:
        return True


def init_lab8_db_if_needed() -> None:
    if needs_lab8_db():
        init_lab8_db()


@lab8_bp.route("/", strict_slashes=False)
def home():
    return render_template("lab8_home.html")


@lab8_bp.route("/union")
def union():
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM ClubA
            UNION
            SELECT * FROM ClubB;
        """
        )
        rows = cur.fetchall()
    return render_template("union.html", rows=rows)


@lab8_bp.route("/intersection")
def intersection():
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM ClubA
            INTERSECT
            SELECT * FROM ClubB;
        """
        )
        rows = cur.fetchall()
    return render_template("intersection.html", rows=rows)


@lab8_bp.route("/difference")
def difference():
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM ClubA
            EXCEPT
            SELECT * FROM ClubB;
        """
        )
        rows = cur.fetchall()
    return render_template("difference.html", rows=rows)


@lab8_bp.route("/division")
def division():
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT m.member_last_name, m.member_first_name
            FROM Member m
            WHERE NOT EXISTS (
                SELECT *
                FROM Tournament t
                WHERE NOT EXISTS (
                    SELECT *
                    FROM Entry e
                    WHERE e.entry_member_id = m.member_id
                      AND e.entry_tournament_id = t.tournament_id
                )
            );
        """
        )
        rows = cur.fetchall()
    return render_template("division.html", rows=rows)


init_lab8_db_if_needed()

if __name__ == "__main__":
    from flask import Flask

    _app = Flask(__name__)
    _app.register_blueprint(lab8_bp)  # local dev: routes at /, /union, …
    _app.run(debug=True)
