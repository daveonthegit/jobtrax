from flask import redirect, render_template, request, session, url_for

from .blueprint import jobtrax_bp
from .db import get_conn
from .decorators import login_required


@jobtrax_bp.route("/home")
def home():
    return redirect(url_for("jobtrax.dashboard"))


@jobtrax_bp.route("/")
def dashboard():
    if session.get("user_id") is None:
        return redirect(url_for("jobtrax.login"))
    uid = session["user_id"]
    status_id = request.args.get("status_id", type=int)
    company_id = request.args.get("company_id", type=int)

    with get_conn() as conn:
        statuses = conn.execute(
            "SELECT status_id, status_name FROM statuses ORDER BY sort_order"
        ).fetchall()
        companies = conn.execute(
            "SELECT company_id, company_name FROM companies WHERE user_id = ? ORDER BY company_name",
            (uid,),
        ).fetchall()

        q = """
        SELECT a.application_id, a.job_title, a.application_date, a.deadline,
               c.company_name, s.status_name, a.current_status_id
        FROM applications a
        JOIN companies c ON c.company_id = a.company_id
        JOIN statuses s ON s.status_id = a.current_status_id
        WHERE a.user_id = ?
        """
        params: list = [uid]
        if status_id:
            q += " AND a.current_status_id = ?"
            params.append(status_id)
        if company_id:
            q += " AND a.company_id = ?"
            params.append(company_id)
        q += " ORDER BY a.updated_at DESC, a.application_id DESC"
        apps = conn.execute(q, params).fetchall()

    return render_template(
        "dashboard.html",
        applications=apps,
        statuses=statuses,
        companies=companies,
        filter_status_id=status_id,
        filter_company_id=company_id,
    )
