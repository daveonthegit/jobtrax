# Step-by-Step Implementation Walkthrough

**Audience:** You, implementing Smart Job Tracker yourself  
**Method:** Complete each step, verify, then proceed. If you use an AI assistant, ask for **guides** for a single step—not a full codebase dump.

---

## Before you start

- Read [product-requirements.md](product-requirements.md), [database-design.md](database-design.md), and [routes-and-pages.md](routes-and-pages.md) once.
- Keep [entity-relationship-diagram.md](entity-relationship-diagram.md) open for FK references while modeling.

---

## Step 1 — Initialize project

**What you build:** Virtual environment, `requirements.txt`, empty package layout (no business logic yet).

**Why first:** Reproducible runs locally and on PythonAnywhere.

**Files to touch:** `requirements.txt`; optional project `README.md` with run instructions.

**Suggested dependencies (pin versions in your file):** `flask`, `flask-sqlalchemy`, `flask-login`, `flask-wtf`, `python-dotenv`, `email-validator` (if you validate emails), `pytest` (optional).

**Verify:** `python -c "import flask"` from the activated venv; Python version matches what PA offers (3.10+ typical).

**Pitfalls:** Committing `venv/`; using system Python by mistake.

---

## Step 2 — Flask application factory

**What you build:** `create_app()`, configuration classes or env-based config, register a trivial route (e.g. “OK”).

**Why now:** All extensions and blueprints attach here.

**Files to touch:** `app/__init__.py`, `app/config.py`, optional `wsgi.py` importing `create_app`.

**Verify:** `flask --app <your_package> run` serves the test route; production config has `DEBUG=False`.

**Pitfalls:** Circular imports—keep `models` imported after `db` is created, or use patterns from Flask-SQLAlchemy docs.

---

## Step 3 — Database path and models

**What you build:** SQLite URI to `instance/jobtracker.db`; SQLAlchemy models for all tables in [database-design.md](database-design.md); relationships useful for queries (`application.history`, etc.).

**Why now:** Fixing schema late is painful.

**Files to touch:** `app/models.py`, `instance/.gitkeep`, `scripts/init_db.py` or `flask init-db` custom command.

**Verify:** Run init; open SQLite CLI—list tables; manually INSERT one status row if seed not run yet.

**Pitfalls:** Wrong relative path when cwd differs; forgetting `user_id` on `companies`; missing CASCADE behavior on delete (decide explicitly).

---

## Step 4 — Seed statuses

**What you build:** Insert the seven statuses with `sort_order` (see [sql/seed_statuses.sql](sql/seed_statuses.sql)).

**Why now:** Dropdowns and parser mapping depend on stable ids.

**Verify:** `SELECT * FROM statuses ORDER BY sort_order;`

**Pitfalls:** Running seed twice creates duplicates—use “insert if not exists” or wipe dev DB.

---

## Step 5 — Authentication

**What you build:** Register, login, logout; `User` implements Flask-Login `UserMixin`; `@login_required` on private blueprints; password hashing.

**Why before CRUD:** Ownership checks are easier from day one.

**Files to touch:** `app/auth.py`, `templates/auth/*.html`, login manager in `create_app`.

**Verify:** Create users A and B; confirm B cannot open A’s resource URLs once CRUD exists.

**Pitfalls:** Plaintext passwords; CSRF missing when you add WTForms.

---

## Step 6 — Company CRUD

**What you build:** List/create/edit/delete with `filter_by(user_id=current_user.id)`.

**Why before applications:** FK dependency.

**Verify:** Cross-user URL tampering returns 404/403.

**Pitfalls:** Deleting a company that still has applications—block with error or CASCADE (document).

---

## Step 7 — Application CRUD + initial history row

**What you build:** Create/edit/delete applications. On **create**, insert **two** rows: `applications` and `application_status_history` sharing the same `status_id`.

**Why now:** Parser confirm will reuse the same write logic.

**Verify:** One create → two related rows; delete removes children per your FK rules.

**Pitfalls:** Updating `applications.status_id` without a matching history row.

---

## Step 8 — Status changes (timeline)

**What you build:** POST handler that INSERTs history then UPDATEs `applications.status_id` in one transaction.

**Verify:** Three changes yield three ordered history rows.

**Pitfalls:** Double POST duplicates—use PRG and idempotent UX (disable button on submit optional).

---

## Step 9 — Contacts

**What you build:** Add/edit/delete contacts; always verify parent `application.user_id == current_user.id`.

**Verify:** Wrong `application_id` in URL is rejected.

**Pitfalls:** Editing contact by id without checking parent ownership.

---

## Step 10 — Parser service (pure functions)

**What you build:** `parser_service.parse_job_listing(text)`, `parse_email(text)` or unified `parse(text, input_type)` returning `fields` + `evidence`.

**Why isolated:** Unit-testable; clear for your report.

**Files to touch:** `app/services/parser_service.py`, `tests/test_parser_service.py`.

**Verify:** Tests pass for your fixtures in [starter-assets-and-fixtures.md](starter-assets-and-fixtures.md).

**Pitfalls:** Overfitting regex to one posting; failing silently—return explicit empty fields instead.

---

## Step 11 — Parser HTTP flow (preview + confirm)

**What you build:** GET paste page; POST preview stores proposal in **session**; POST confirm writes DB.

**Verify:** Preview does not create an application; refresh after confirm does not duplicate (redirect to GET).

**Pitfalls:** Cookie size—avoid storing huge raw text in session; store trimmed fields.

---

## Step 12 — Dashboard / home

**What you build:** List applications for user, sort by `updated_at` or `application_date`; empty state for new users.

**Verify:** Readable with 10+ seeded rows.

---

## Step 13 — Validation and error UX

**What you build:** Required field checks; `flash` messages; display errors next to fields or at top.

**Verify:** Empty `job_title` rejected with friendly message.

---

## Step 14 — UI polish

**What you build:** Consistent typography/spacing; readable tables; responsive width.

**Verify:** Screenshots for submission; tab through forms.

---

## Step 15 — Deployment (PythonAnywhere)

**What you build:** WSGI path, static mapping, env vars, `requirements.txt` install, init DB on server.

**Verify:** HTTPS login and one parser confirm on production data.

---

## If time runs short — cut list

1. Drop email → existing-application matching.  
2. Keep `parsed_inputs` insert **only** on confirm (no draft table).  
3. Trim optional company columns.

**Do not cut:** Auth isolation, history on status change, parser confirmation gate.
