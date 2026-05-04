from __future__ import annotations

from datetime import date

from flask import abort, flash, redirect, render_template, request, session, url_for

from .blueprint import jobtrax_bp
from .db import default_status_id, get_conn
from .decorators import login_required
from .forms import (
    ApplicationEditForm,
    ApplicationForm,
    ContactForm,
    DeleteForm,
    StatusChangeForm,
)


def _uid() -> int:
    return int(session["user_id"])


def _date_str(d) -> str | None:
    if d is None:
        return None
    if isinstance(d, date):
        return d.isoformat()
    return str(d)


@jobtrax_bp.route("/applications")
@login_required
def application_list():
    return redirect(url_for("jobtrax.dashboard"))


@jobtrax_bp.route("/applications/new", methods=["GET", "POST"])
@login_required
def application_new():
    uid = _uid()
    form = ApplicationForm()
    with get_conn() as conn:
        companies = conn.execute(
            "SELECT company_id, company_name FROM companies WHERE user_id = ? ORDER BY company_name",
            (uid,),
        ).fetchall()
        statuses = conn.execute(
            "SELECT status_id, status_name FROM statuses ORDER BY sort_order"
        ).fetchall()
        form.company_id.choices = [(c["company_id"], c["company_name"]) for c in companies]
        form.status_id.choices = [(s["status_id"], s["status_name"]) for s in statuses]

    if not companies:
        flash("Add a company before creating an application.", "warning")
        return redirect(url_for("jobtrax.company_new"))

    if form.validate_on_submit():
        with get_conn() as conn:
            sid = form.status_id.data
            conn.execute(
                """
                INSERT INTO applications (
                  user_id, company_id, status_id, job_title, location,
                  job_type, salary_range, application_date, deadline, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uid,
                    form.company_id.data,
                    sid,
                    form.job_title.data.strip(),
                    form.location.data.strip() or None,
                    form.job_type.data.strip() or None,
                    form.salary_range.data.strip() or None,
                    _date_str(form.application_date.data),
                    _date_str(form.deadline.data),
                    form.notes.data.strip() or None,
                ),
            )
            aid = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            conn.execute(
                """
                INSERT INTO application_status_history (application_id, status_id, note)
                VALUES (?, ?, ?)
                """,
                (int(aid), sid, "Created"),
            )
        flash("Application saved.", "success")
        return redirect(url_for("jobtrax.application_detail", aid=int(aid)))

    return render_template(
        "applications/form.html",
        form=form,
        title="New application",
    )


def _load_application(conn, aid: int, uid: int):
    return conn.execute(
        """
        SELECT a.*, c.company_name, s.status_name AS current_status_name
        FROM applications a
        JOIN companies c ON c.company_id = a.company_id
        JOIN statuses s ON s.status_id = a.status_id
        WHERE a.application_id = ? AND a.user_id = ?
        """,
        (aid, uid),
    ).fetchone()


@jobtrax_bp.route("/applications/<int:aid>")
@login_required
def application_detail(aid):
    uid = _uid()
    delete_form = DeleteForm()
    with get_conn() as conn:
        app_row = _load_application(conn, aid, uid)
        if not app_row:
            abort(404)
        history = conn.execute(
            """
            SELECT h.*, s.status_name
            FROM application_status_history h
            JOIN statuses s ON s.status_id = h.status_id
            WHERE h.application_id = ?
            ORDER BY h.changed_at DESC, h.history_id DESC
            """,
            (aid,),
        ).fetchall()
        contacts = conn.execute(
            "SELECT * FROM contacts WHERE application_id = ? ORDER BY contact_id",
            (aid,),
        ).fetchall()
        statuses = conn.execute(
            "SELECT status_id, status_name FROM statuses ORDER BY sort_order"
        ).fetchall()
    st_form = StatusChangeForm()
    st_form.status_id.choices = [(s["status_id"], s["status_name"]) for s in statuses]
    return render_template(
        "applications/detail.html",
        app_row=app_row,
        history=history,
        contacts=contacts,
        status_form=st_form,
        delete_form=delete_form,
    )


@jobtrax_bp.route("/applications/<int:aid>/edit", methods=["GET", "POST"])
@login_required
def application_edit(aid):
    uid = _uid()
    with get_conn() as conn:
        row = _load_application(conn, aid, uid)
    if not row:
        abort(404)

    form = ApplicationEditForm()
    if request.method == "GET":
        form.job_title.data = row["job_title"]
        form.location.data = row["location"]
        form.job_type.data = row["job_type"]
        form.salary_range.data = row["salary_range"]
        form.notes.data = row["notes"]
        if row["application_date"]:
            try:
                form.application_date.data = date.fromisoformat(row["application_date"])
            except ValueError:
                pass
        if row["deadline"]:
            try:
                form.deadline.data = date.fromisoformat(row["deadline"])
            except ValueError:
                pass

    if form.validate_on_submit():
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE applications SET
                  job_title = ?, location = ?, job_type = ?, salary_range = ?,
                  application_date = ?, deadline = ?, notes = ?,
                  updated_at = datetime('now')
                WHERE application_id = ? AND user_id = ?
                """,
                (
                    form.job_title.data.strip(),
                    form.location.data.strip() or None,
                    form.job_type.data.strip() or None,
                    form.salary_range.data.strip() or None,
                    _date_str(form.application_date.data),
                    _date_str(form.deadline.data),
                    form.notes.data.strip() or None,
                    aid,
                    uid,
                ),
            )
        flash("Application updated.", "success")
        return redirect(url_for("jobtrax.application_detail", aid=aid))

    return render_template(
        "applications/edit.html",
        form=form,
        app_row=row,
        title="Edit application",
    )


@jobtrax_bp.route("/applications/<int:aid>/status", methods=["POST"])
@login_required
def application_status(aid):
    uid = _uid()
    form = StatusChangeForm()
    with get_conn() as conn:
        statuses = conn.execute(
            "SELECT status_id, status_name FROM statuses ORDER BY sort_order"
        ).fetchall()
        form.status_id.choices = [(s["status_id"], s["status_name"]) for s in statuses]
        if not form.validate_on_submit():
            flash("Invalid status update.", "danger")
            return redirect(url_for("jobtrax.application_detail", aid=aid))
        row = _load_application(conn, aid, uid)
        if not row:
            abort(404)
        new_sid = form.status_id.data
        conn.execute(
            "UPDATE applications SET status_id = ?, updated_at = datetime('now') WHERE application_id = ?",
            (new_sid, aid),
        )
        conn.execute(
            """
            INSERT INTO application_status_history (application_id, status_id, note)
            VALUES (?, ?, ?)
            """,
            (aid, new_sid, form.note.data.strip() or None),
        )
    flash("Status updated.", "success")
    return redirect(url_for("jobtrax.application_detail", aid=aid))


@jobtrax_bp.route("/applications/<int:aid>/delete", methods=["POST"])
@login_required
def application_delete(aid):
    form = DeleteForm()
    if not form.validate_on_submit():
        abort(400)
    uid = _uid()
    with get_conn() as conn:
        r = conn.execute(
            "DELETE FROM applications WHERE application_id = ? AND user_id = ?",
            (aid, uid),
        )
        if r.rowcount == 0:
            abort(404)
    flash("Application deleted.", "info")
    return redirect(url_for("jobtrax.dashboard"))


@jobtrax_bp.route("/applications/<int:aid>/contacts/new", methods=["GET", "POST"])
@login_required
def contact_new(aid):
    uid = _uid()
    with get_conn() as conn:
        if not _load_application(conn, aid, uid):
            abort(404)
    form = ContactForm()
    if form.validate_on_submit():
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO contacts (application_id, contact_name, contact_role, email, phone)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    aid,
                    form.contact_name.data.strip() or None,
                    form.contact_role.data.strip() or None,
                    form.email.data.strip() or None,
                    form.phone.data.strip() or None,
                ),
            )
        flash("Contact added.", "success")
        return redirect(url_for("jobtrax.application_detail", aid=aid))
    return render_template("contacts/form.html", form=form, aid=aid, title="Add contact")


@jobtrax_bp.route("/contacts/<int:cid>/edit", methods=["GET", "POST"])
@login_required
def contact_edit(cid):
    uid = _uid()
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT ct.*, a.user_id
            FROM contacts ct
            JOIN applications a ON a.application_id = ct.application_id
            WHERE ct.contact_id = ?
            """,
            (cid,),
        ).fetchone()
    if not row or int(row["user_id"]) != uid:
        abort(404)
    aid = int(row["application_id"])
    form = ContactForm(obj=row)
    if form.validate_on_submit():
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE contacts SET contact_name = ?, contact_role = ?, email = ?, phone = ?
                WHERE contact_id = ?
                """,
                (
                    form.contact_name.data.strip() or None,
                    form.contact_role.data.strip() or None,
                    form.email.data.strip() or None,
                    form.phone.data.strip() or None,
                    cid,
                ),
            )
        flash("Contact updated.", "success")
        return redirect(url_for("jobtrax.application_detail", aid=aid))
    return render_template(
        "contacts/form.html",
        form=form,
        aid=aid,
        title="Edit contact",
    )


@jobtrax_bp.route("/contacts/<int:cid>/delete", methods=["POST"])
@login_required
def contact_delete(cid):
    form = DeleteForm()
    if not form.validate_on_submit():
        abort(400)
    uid = _uid()
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT ct.contact_id, a.application_id, a.user_id
            FROM contacts ct
            JOIN applications a ON a.application_id = ct.application_id
            WHERE ct.contact_id = ?
            """,
            (cid,),
        ).fetchone()
        if not row or int(row["user_id"]) != uid:
            abort(404)
        aid = int(row["application_id"])
        conn.execute("DELETE FROM contacts WHERE contact_id = ?", (cid,))
    flash("Contact removed.", "info")
    return redirect(url_for("jobtrax.application_detail", aid=aid))
