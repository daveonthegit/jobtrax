# Product Requirements Document (PRD)

**Product:** Smart Job Tracker  
**Version:** MVP (course project)  
**Stack:** Flask, SQLite, server-rendered HTML/CSS/JS, PythonAnywhere

---

## 1. Project summary

Smart Job Tracker is a database-driven web application that helps students and new graduates record job applications, employers (companies), contacts, and status changes over time. A distinguishing feature is a **rule-based text parser**: users paste a job posting or recruiter email; the system extracts candidate fields and presents a **review screen**; **nothing** is persisted to core tables until the user explicitly confirms.

---

## 2. Problem statement

Spreadsheets and ad hoc notes are error-prone, hard to query, and often fail to preserve a **timeline** of status changes. Students need a single, account-scoped system with normalized data suitable for reporting and class demonstration. Pasting raw text reduces typing while keeping humans in the loop when extraction is imperfect.

---

## 3. Target users

- Undergraduate and graduate students applying for internships or full-time roles.
- Recent graduates managing roughly **10–100** concurrent applications (SQLite is adequate at this scale).

---

## 4. Goals

- Reliable **per-user** storage of applications, companies, contacts, and status history.
- Fast **manual** CRUD for everyday maintenance.
- **Deterministic, explainable** parsing (regex + keywords) with mandatory confirmation.
- **Deployable** on PythonAnywhere with minimal dependencies and no external paid APIs.

---

## 5. Non-goals

- Machine learning, third-party NLP APIs, or resume file parsing.
- Multi-user collaboration, recruiter portals, or admin analytics products.
- Native mobile apps (responsive web is sufficient).
- Automatic ingestion of email (IMAP/webhooks); **paste-only** for MVP.

---

## 6. MVP scope

**In scope**

- User registration, login, logout (session-based).
- Companies CRUD; companies **scoped to the logged-in user**.
- Applications CRUD; each application linked to one company and one current status from a **seeded lookup table**.
- On status change: append `application_status_history` and update `applications.current_status_id` consistently.
- Contacts CRUD scoped to an application (with ownership checks via the parent application).
- Dashboard-style **application list** (can be the home page).
- Parser: **job listing** and **email** input types; preview → editable review → confirm; writes only on confirm.
- SQLite + Flask + Jinja2 templates; simple CSS and optional vanilla JS.

**Optional / phase 2**

- Suggest matching an existing application from pasted email (heuristic match).
- Duplicate-company warnings or merge helpers.
- CSV export.

---

## 7. User stories (representative)

| ID | Story |
|----|--------|
| US-1 | As a user, I want to register and log in so that only I can see my data. |
| US-2 | As a user, I want to add and edit companies so my applications link to consistent employers. |
| US-3 | As a user, I want to create an application with title, company, dates, and status so I can track progress. |
| US-4 | As a user, I want each status change recorded with a timestamp so I can see a timeline. |
| US-5 | As a user, I want contacts (name, role, email, phone) on an application so I know whom to follow up with. |
| US-6 | As a user, I want to paste a job description and review extracted fields before saving. |
| US-7 | As a user, I want to paste recruiter email text, see suggested status and fields, and confirm before updating. |

---

## 8. Functional requirements

| ID | Requirement |
|----|----------------|
| FR-AUTH | Session-based authentication; passwords stored as strong hashes; logout clears session. |
| FR-CO | Full CRUD for companies; each company row owned by exactly one user. |
| FR-APP | Full CRUD for applications; each application belongs to one user and one company. |
| FR-STAT | Status values come from seeded `statuses` table; changing status **appends** `application_status_history` and updates `current_status_id`. |
| FR-CON | CRUD for contacts; each contact belongs to one application; enforce access via parent application ownership. |
| FR-PARSE | Accept `input_type` + raw text; run rule-based extractor; show review UI; on confirm, INSERT/UPDATE core entities as chosen; optionally log `parsed_inputs`. |
| FR-NO-AUTO | Parser output must **never** auto-persist applications or history without an explicit confirm action. |

---

## 9. Non-functional requirements

| ID | Requirement |
|----|----------------|
| NFR-SEC | Deploy with HTTPS on PythonAnywhere; `SECRET_KEY` from environment; CSRF protection on mutating forms; parameterized SQL / ORM only (no string-concatenated SQL). |
| NFR-PERF | Acceptable performance for hundreds of rows per user on SQLite. |
| NFR-MAINT | Single deployable Flask app; clear separation: models, blueprints, parser service module. |
| NFR-DOC | Submittable ERD, schema description, and normalization rationale (see database docs). |

---

## 10. Assumptions and constraints

- One SQLite database file per deployment; path under `instance/` writable on PythonAnywhere.
- Parser rules may be **English-centric**; accuracy is “helpful,” not perfect.
- Users understand extracted fields require review.

---

## 11. Success criteria

- Schema demonstrates **≥4 tables** (this design uses **7** core entities) and **3NF/BCNF** narrative with documented denormalization where applicable.
- Demo path: signup → company → application → status changes with visible history → contact → paste parse → confirm save.
- **3–5** parser fixtures documented (see [starter-assets-and-fixtures.md](starter-assets-and-fixtures.md)).
- Application runs locally and is **deployed** (or screen-recorded) on PythonAnywhere.
