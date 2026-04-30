from flask import abort, flash, redirect, render_template, session, url_for

from .blueprint import jobtrax_bp
from .db import get_conn
from .decorators import login_required
from .forms import CompanyForm, DeleteForm


@jobtrax_bp.route("/companies")
@login_required
def company_list():
    uid = _user_id()
    delete_form = DeleteForm()
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT company_id, company_name, location, industry
            FROM companies WHERE user_id = ?
            ORDER BY company_name
            """,
            (uid,),
        ).fetchall()
    return render_template(
        "companies/list.html",
        companies=rows,
        delete_form=delete_form,
    )


def _user_id() -> int:
    return int(session["user_id"])


@jobtrax_bp.route("/companies/new", methods=["GET", "POST"])
@login_required
def company_new():
    uid = _user_id()
    form = CompanyForm()
    if form.validate_on_submit():
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO companies (user_id, company_name, industry, location, website)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    uid,
                    form.company_name.data.strip(),
                    form.industry.data.strip() or None,
                    form.location.data.strip() or None,
                    form.website.data.strip() or None,
                ),
            )
        flash("Company added.", "success")
        return redirect(url_for("jobtrax.company_list"))
    return render_template("companies/form.html", form=form, title="New company")


@jobtrax_bp.route("/companies/<int:cid>/edit", methods=["GET", "POST"])
@login_required
def company_edit(cid):
    uid = _user_id()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM companies WHERE company_id = ? AND user_id = ?",
            (cid, uid),
        ).fetchone()
    if not row:
        abort(404)
    form = CompanyForm(obj=row)
    if form.validate_on_submit():
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE companies SET company_name = ?, industry = ?, location = ?, website = ?
                WHERE company_id = ? AND user_id = ?
                """,
                (
                    form.company_name.data.strip(),
                    form.industry.data.strip() or None,
                    form.location.data.strip() or None,
                    form.website.data.strip() or None,
                    cid,
                    uid,
                ),
            )
        flash("Company updated.", "success")
        return redirect(url_for("jobtrax.company_list"))
    return render_template("companies/form.html", form=form, title="Edit company")


@jobtrax_bp.route("/companies/<int:cid>/delete", methods=["POST"])
@login_required
def company_delete(cid):
    form = DeleteForm()
    if not form.validate_on_submit():
        abort(400)
    uid = _user_id()
    with get_conn() as conn:
        n = conn.execute(
            "SELECT COUNT(*) AS c FROM applications WHERE company_id = ? AND user_id = ?",
            (cid, uid),
        ).fetchone()["c"]
        if int(n) > 0:
            flash("Cannot delete: applications exist for this company.", "danger")
            return redirect(url_for("jobtrax.company_list"))
        conn.execute(
            "DELETE FROM companies WHERE company_id = ? AND user_id = ?",
            (cid, uid),
        )
    flash("Company deleted.", "info")
    return redirect(url_for("jobtrax.company_list"))
