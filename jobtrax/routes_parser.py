from __future__ import annotations

from flask import flash, redirect, render_template, request, session, url_for

from .blueprint import jobtrax_bp
from .db import default_status_id, get_conn
from .decorators import login_required
from .forms import ParserConfirmForm, ParserPasteForm
from .services import parser_service

PREVIEW_KEY = "jobtrax_parse_preview"


def _uid() -> int:
    return int(session["user_id"])


@jobtrax_bp.route("/parser")
@login_required
def parser_paste():
    form = ParserPasteForm()
    return render_template("parser/paste.html", form=form)


@jobtrax_bp.route("/parser/preview", methods=["POST"])
@login_required
def parser_preview():
    form = ParserPasteForm()
    if not form.validate_on_submit():
        flash("Please fill in the paste form.", "danger")
        return redirect(url_for("jobtrax.parser_paste"))
    raw = form.raw_text.data
    it = form.input_type.data
    try:
        parsed = parser_service.parse(it, raw)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("jobtrax.parser_paste"))

    with get_conn() as conn:
        status_id = default_status_id(conn)
        rows = conn.execute(
            "SELECT status_id, status_name FROM statuses ORDER BY sort_order"
        ).fetchall()
    hint = parsed.get("status_hint")
    if hint:
        for r in rows:
            if r["status_name"] == hint:
                status_id = int(r["status_id"])
                break

    session[PREVIEW_KEY] = {
        "input_type": it,
        "raw_text": raw,
        "parsed": parsed,
        "default_status_id": status_id,
    }
    return redirect(url_for("jobtrax.parser_review"))


@jobtrax_bp.route("/parser/review", methods=["GET"])
@login_required
def parser_review():
    data = session.get(PREVIEW_KEY)
    if not data:
        flash("Nothing to review — run preview from the parser page first.", "warning")
        return redirect(url_for("jobtrax.parser_paste"))

    with get_conn() as conn:
        statuses = conn.execute(
            "SELECT status_id, status_name FROM statuses ORDER BY sort_order"
        ).fetchall()

    form = ParserConfirmForm()
    form.status_id.choices = [(s["status_id"], s["status_name"]) for s in statuses]
    p = data["parsed"]
    form.company_name.data = p.get("parsed_company_name") or ""
    form.job_title.data = p.get("parsed_job_title") or ""
    form.location.data = p.get("parsed_location") or ""
    form.job_type.data = p.get("job_type") or ""
    form.salary_range.data = p.get("salary_range") or ""
    form.deadline.data = p.get("parsed_deadline") or ""
    form.contact_name.data = p.get("parsed_contact_name") or ""
    form.status_id.data = int(data["default_status_id"])
    form.notes.data = ""

    return render_template(
        "parser/review.html",
        form=form,
        raw_text=data["raw_text"],
        input_type=data["input_type"],
    )


@jobtrax_bp.route("/parser/confirm", methods=["POST"])
@login_required
def parser_confirm():
    data = session.get(PREVIEW_KEY)
    if not data:
        flash("Session expired — start over.", "warning")
        return redirect(url_for("jobtrax.parser_paste"))

    with get_conn() as conn:
        statuses = conn.execute(
            "SELECT status_id, status_name FROM statuses ORDER BY sort_order"
        ).fetchall()

    form = ParserConfirmForm()
    form.status_id.choices = [(s["status_id"], s["status_name"]) for s in statuses]

    if not form.validate_on_submit():
        flash("Fix validation errors and try again.", "danger")
        return redirect(url_for("jobtrax.parser_review"))

    uid = _uid()
    company_name = form.company_name.data.strip()
    job_title = form.job_title.data.strip()
    if not company_name or not job_title:
        flash("Company and job title are required.", "danger")
        return redirect(url_for("jobtrax.parser_review"))

    sid = form.status_id.data
    raw_text = data["raw_text"]
    it = data["input_type"]

    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT company_id FROM companies
            WHERE user_id = ? AND lower(company_name) = lower(?)
            """,
            (uid, company_name),
        ).fetchone()
        if row:
            cid = int(row["company_id"])
        else:
            conn.execute(
                "INSERT INTO companies (user_id, company_name) VALUES (?, ?)",
                (uid, company_name),
            )
            cid = int(conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"])

        conn.execute(
            """
            INSERT INTO parsed_inputs (
              user_id, input_type, raw_text,
              parsed_company_name, parsed_job_title, parsed_status_id,
              parsed_location, parsed_deadline, parsed_contact_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                uid,
                it,
                raw_text,
                company_name,
                job_title,
                sid,
                form.location.data.strip() or None,
                form.deadline.data.strip() or None,
                form.contact_name.data.strip() or None,
            ),
        )
        parse_id = int(conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"])

        conn.execute(
            """
            INSERT INTO applications (
              user_id, company_id, current_status_id, job_title, location,
              job_type, salary_range, application_date, deadline, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?)
            """,
            (
                uid,
                cid,
                sid,
                job_title,
                form.location.data.strip() or None,
                form.job_type.data.strip() or None,
                form.salary_range.data.strip() or None,
                form.notes.data.strip() or None,
            ),
        )
        aid = int(conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"])

        conn.execute(
            """
            INSERT INTO application_status_history
              (application_id, status_id, source_parse_id, note)
            VALUES (?, ?, ?, ?)
            """,
            (aid, sid, parse_id, "From parser"),
        )

        cname = form.contact_name.data.strip()
        if cname:
            conn.execute(
                """
                INSERT INTO contacts (application_id, contact_name)
                VALUES (?, ?)
                """,
                (aid, cname),
            )

    session.pop(PREVIEW_KEY, None)
    flash("Application saved from parser.", "success")
    return redirect(url_for("jobtrax.application_detail", aid=aid))
