# Database Design Document

**Project:** Smart Job Tracker  
**DBMS:** SQLite  
**Normalization target:** 3NF / BCNF, with **one documented intentional denormalization** on `applications.current_status_id`.

---

## 1. Final entity list

| # | Entity | Description |
|---|--------|---------------|
| 1 | `users` | Application accounts. |
| 2 | `companies` | Employers; **owned by a user** (per-tenant). |
| 3 | `statuses` | Global lookup of allowed status values (seeded). |
| 4 | `applications` | A job application for a user at a company. |
| 5 | `application_status_history` | Append-only timeline of status changes. |
| 6 | `contacts` | People associated with an application. |
| 7 | `parsed_inputs` | Audit log of pasted text and parsed snapshot (typically on confirm). |

This satisfies the **≥4 tables** requirement with room to discuss relationships and integrity.

---

## 2. Logical schema (columns)

### 2.1 `users`

| Column | Constraints | Notes |
|--------|---------------|-------|
| `user_id` | INTEGER PK, autoincrement | |
| `username` | TEXT NOT NULL UNIQUE | |
| `email` | TEXT NOT NULL UNIQUE | |
| `password_hash` | TEXT NOT NULL | Werkzeug-style hash string |
| `created_at` | TIMESTAMP | Default now |

### 2.2 `companies`

| Column | Constraints | Notes |
|--------|---------------|-------|
| `company_id` | INTEGER PK | |
| `user_id` | INTEGER NOT NULL FK → `users.user_id` | **Required** for isolation |
| `company_name` | TEXT NOT NULL | |
| `industry` | TEXT NULL | Optional for MVP |
| `location` | TEXT NULL | HQ or user’s label |
| `website` | TEXT NULL | Optional |

**Optional constraint:** `UNIQUE (user_id, company_name)` to reduce duplicates.

### 2.3 `statuses`

| Column | Constraints | Notes |
|--------|---------------|-------|
| `status_id` | INTEGER PK | |
| `status_name` | TEXT NOT NULL UNIQUE | Saved, Applied, OA, … |
| `sort_order` | INTEGER NOT NULL | UI ordering |

Seeded; not user-editable in MVP.

### 2.4 `applications`

| Column | Constraints | Notes |
|--------|---------------|-------|
| `application_id` | INTEGER PK | |
| `user_id` | INTEGER NOT NULL FK → `users` | Denormalized convenience; must match company owner in app logic |
| `company_id` | INTEGER NOT NULL FK → `companies` | |
| `current_status_id` | INTEGER NOT NULL FK → `statuses` | **See normalization §4** |
| `job_title` | TEXT NOT NULL | |
| `location` | TEXT NULL | Role location |
| `job_type` | TEXT NULL | e.g. internship, full-time |
| `salary_range` | TEXT NULL | Display string |
| `application_date` | DATE NULL | |
| `deadline` | DATE NULL | |
| `notes` | TEXT NULL | |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |

**Application-layer invariant:** `current_status_id` equals the `status_id` of the **latest** `application_status_history` row for this application (by `changed_at` / `history_id`).

### 2.5 `application_status_history`

| Column | Constraints | Notes |
|--------|---------------|-------|
| `history_id` | INTEGER PK | |
| `application_id` | INTEGER NOT NULL FK → `applications` ON DELETE CASCADE | |
| `status_id` | INTEGER NOT NULL FK → `statuses` | |
| `source_parse_id` | INTEGER NULL FK → `parsed_inputs` | Nullable if manual change |
| `changed_at` | TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP | |
| `note` | TEXT NULL | Optional short reason |

Append-only in normal operation (no UI to edit past rows).

### 2.6 `contacts`

| Column | Constraints | Notes |
|--------|---------------|-------|
| `contact_id` | INTEGER PK | |
| `application_id` | INTEGER NOT NULL FK → `applications` ON DELETE CASCADE | |
| `contact_name` | TEXT NULL | |
| `contact_role` | TEXT NULL | |
| `email` | TEXT NULL | |
| `phone` | TEXT NULL | |

### 2.7 `parsed_inputs`

| Column | Constraints | Notes |
|--------|---------------|-------|
| `parse_id` | INTEGER PK | |
| `user_id` | INTEGER NOT NULL FK → `users` | |
| `input_type` | TEXT NOT NULL | `job_listing` or `email`; CHECK in SQLite |
| `raw_text` | TEXT NOT NULL | Consider size limits for UX |
| `parsed_company_name` | TEXT NULL | Snapshot at confirm time |
| `parsed_job_title` | TEXT NULL | |
| `parsed_status_id` | INTEGER NULL FK → `statuses` | |
| `parsed_location` | TEXT NULL | |
| `parsed_deadline` | TEXT NULL | ISO string or raw |
| `parsed_contact_name` | TEXT NULL | |
| `created_at` | TIMESTAMP | |

**Optional columns (phase 2):** `confirmed_at`, `result_application_id` FK, `suggested_application_id` FK.

---

## 3. Primary and foreign keys (summary)

- **PKs:** Surrogate integer keys on all tables (SQLite-friendly).
- **FKs:** As listed above; use `ON DELETE CASCADE` from `applications` to `contacts` and `application_status_history` where appropriate.
- **`parsed_inputs` → history:** `application_status_history.source_parse_id` references `parsed_inputs.parse_id`; multiple history rows could reference the same parse if you ever batch (unusual); typically zero or one.

---

## 4. Cardinalities

| From | Relationship | To | Cardinality |
|------|----------------|-----|-------------|
| User | owns | Companies | 1 : N |
| User | owns | Applications | 1 : N |
| User | creates | Parsed inputs | 1 : N |
| Company | has | Applications | 1 : N |
| Status | labels current | Applications | 1 : N |
| Application | has | Status history | 1 : N |
| Status | used in | Status history | 1 : N |
| Application | has | Contacts | 1 : N |
| Parsed input | may source | Status history | 1 : N (optional link) |

---

## 5. Normalization analysis

### 5.1 Third Normal Form (3NF)

For `users`, `companies`, `statuses`, `contacts`, `application_status_history`, and `parsed_inputs`, non-key attributes depend on the **whole** primary key, and there are **no** transitive dependencies of non-key attributes on other non-key attributes within each table. These relations are in **3NF**.

### 5.2 BCNF

Lookup tables (`statuses`) and single-key entities are straightforward. Functional dependencies respect the primary key as the determinant.

### 5.3 Intentional denormalization

`applications.current_status_id` **repeats** information that can be derived from `application_status_history`. This is **not** a normalization failure if you treat it as a **cached value** updated with every status transition. Document:

- **Why:** Faster list queries and simpler templates.
- **How enforced:** Application code updates `current_status_id` whenever a new history row is inserted for that application.

If the course requires **strict** elimination of redundancy, you could drop `current_status_id` and always compute latest status via subquery—at the cost of more complex queries. The recommended student project keeps the column and explains the tradeoff clearly.

---

## 6. Simplifications if time runs out

- Omit `industry` / `website` on companies.
- Omit `parsed_inputs` only if the course allows fewer tables—you still need ≥4; **prefer keeping** `parsed_inputs` for the parser story.
- Skip optional `suggested_application_id` and email-to-existing matching.

---

## 7. Reference DDL

See [sql/schema_reference.sql](sql/schema_reference.sql) for SQLite-oriented `CREATE TABLE` statements you can adapt when implementing (ORM models should reflect the same constraints).
