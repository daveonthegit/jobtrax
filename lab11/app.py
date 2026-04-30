import os
import sqlite3

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

_EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mydatabase.db")

lab11_bp = Blueprint(
    "lab11",
    __name__,
    template_folder="templates",
)

# Legacy import used by some forks: `from lab11.app import bp`
bp = lab11_bp


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            users_id INTEGER PRIMARY KEY AUTOINCREMENT,
            users_first_name TEXT NOT NULL,
            users_last_name TEXT NOT NULL,
            users_email TEXT NOT NULL UNIQUE,
            users_college TEXT
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


class UserForm(FlaskForm):
    users_first_name = StringField("First Name", validators=[DataRequired()])
    users_last_name = StringField("Last Name", validators=[DataRequired()])
    users_email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Regexp(_EMAIL_RE, message="Enter a valid email address."),
        ],
    )
    users_college = StringField("College Name")
    submit = SubmitField("Submit")


@lab11_bp.route("/home")
def home():
    """Hub links and older deployments used lab11.home — redirect to the real entry."""
    return redirect(url_for("lab11.index"))


@lab11_bp.route("/", methods=["GET", "POST"])
def index():
    form = UserForm()

    if form.validate_on_submit():
        users_first_name = form.users_first_name.data
        users_last_name = form.users_last_name.data
        users_email = form.users_email.data
        users_college = form.users_college.data or None

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO Users (
                    users_first_name,
                    users_last_name,
                    users_email,
                    users_college
                )
                VALUES (?, ?, ?, ?)
                """,
                (users_first_name, users_last_name, users_email, users_college),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("That email is already registered. Try another address.", "error")
            return redirect(url_for("lab11.index"))
        conn.close()
        flash(f"{users_first_name} was added to the database.", "success")
        return redirect(url_for("lab11.success"))

    return render_template("lab11_form.html", form=form)


@lab11_bp.route("/success")
def success():
    return render_template("lab11_success.html")


@lab11_bp.route("/users")
def users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM Users").fetchall()
    conn.close()

    return "<br>".join(
        [
            f"{u['users_first_name']} {u['users_last_name']} - "
            f"{u['users_email']} ({u['users_college']})"
            for u in rows
        ]
    )


if __name__ == "__main__":
    from flask import Flask

    _app = Flask(__name__)
    _app.config["SECRET_KEY"] = "Secret Key"
    _app.register_blueprint(lab11_bp)
    _app.run(debug=True)
