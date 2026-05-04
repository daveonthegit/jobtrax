# Design Rationale — Concept Critique and Refinements

This document records why the final design differs slightly from an early draft that used global companies and parser tables without per-user scoping.

## What works well in the original idea

- **Clear MVP:** Authentication, CRUD for applications and companies, fixed statuses, status history, contacts, and paste-to-parse with confirmation.
- **Lookup table for statuses** supports referential integrity and history rows keyed by `status_id` (stronger than free-text status strings for a database course).
- **`parsed_inputs` plus `application_status_history.parse_id`** supports audit (“this status change came from that paste”) without auto-saving parsed data into core entities.

## Recommended refinements

### 1. Add `user_id` to `companies`

Without per-user companies, you either share one global company table (collision: many students each have an “Acme Corp” row or worse, shared rows) or you encode ownership awkwardly elsewhere.

**Decision:** Each **company** row belongs to exactly one **user**. Every query for companies filters by `current_user.id` (or equivalent). Applications still reference `company_id`; combined with `applications.user_id`, you can enforce consistency in application code.

### 2. Optional: `suggested_application_id` on `parsed_inputs`

For “this email might refer to an existing application,” the parser can store a best-guess `application_id` for the review UI.

**Mark as optional** if time is short. MVP can support **new application from job paste** first; email-to-existing matching is phase 2.

### 3. Intentional denormalization: `applications.status_id`

The latest status is derivable from `application_status_history` (ORDER BY `changed_at` DESC LIMIT 1). Duplicating it on `applications` speeds list views and simplifies queries.

**Invariant (application layer):** After any status change, `applications.status_id` must match the newest history row’s `status_id`. SQLite does not enforce this; your Flask code must update both in one logical transaction.

**Course narrative:** Document as *intentional denormalization for read performance; integrity maintained in application logic*.

### 4. Uniqueness

- `users.username` and `users.email`: **UNIQUE**.
- Optional: `UNIQUE (user_id, company_name)` on `companies` to reduce duplicate employer rows (soft rule; users can still merge manually by editing).

### 5. JavaScript vs. TypeScript

Course stack calls for HTML/CSS/JavaScript. On PythonAnywhere without a frontend build pipeline, **vanilla JavaScript** is the default. TypeScript is optional only if you accept compiling to JS locally.

### 6. Parser scope and risk

**“Suggest update to existing application”** is the hardest feature (matching company/title across noisy text). **Sequence:** ship **new draft from job listing paste** first; add heuristic matching later if time allows.
