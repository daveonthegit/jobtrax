from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .blueprint import jobtrax_bp
from .db import get_conn
from .forms import LoginForm, RegisterForm


@jobtrax_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("jobtrax.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        with get_conn() as conn:
            exists = conn.execute(
                "SELECT 1 FROM users WHERE username = ? OR email = ?",
                (form.username.data.strip(), form.email.data.strip().lower()),
            ).fetchone()
            if exists:
                flash("Username or email already registered.", "danger")
                return render_template("auth/register.html", form=form)
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (
                    form.username.data.strip(),
                    form.email.data.strip().lower(),
                    generate_password_hash(form.password.data),
                ),
            )
            uid = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        session["user_id"] = int(uid)
        session["username"] = form.username.data.strip()
        flash("Account created.", "success")
        return redirect(url_for("jobtrax.dashboard"))
    return render_template("auth/register.html", form=form)


@jobtrax_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("jobtrax.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        with get_conn() as conn:
            row = conn.execute(
                "SELECT user_id, username, password_hash FROM users WHERE username = ?",
                (form.username.data.strip(),),
            ).fetchone()
        if row and check_password_hash(row["password_hash"], form.password.data):
            session["user_id"] = int(row["user_id"])
            session["username"] = row["username"]
            flash("Welcome back.", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("jobtrax.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html", form=form)


@jobtrax_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("jobtrax.login"))
