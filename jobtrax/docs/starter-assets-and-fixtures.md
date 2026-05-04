# Starter Assets, Seeds, and Test Fixtures

Reference material for development and for documenting parser behavior in your course submission. **Adapt** table/column names to match your final ORM models.

---

## 1. Status seed data (logical)

| status_name   | sort_order |
|---------------|------------|
| Saved         | 10         |
| Applied       | 20         |
| OA            | 30         |
| Interviewing  | 40         |
| Offer         | 50         |
| Rejected      | 60         |
| Withdrawn     | 70         |

SQL file: [sql/seed_statuses.sql](sql/seed_statuses.sql)

---

## 2. Example application rows (manual test data)

Use after you have two users, several companies, and seeded statuses.

**User A — Company “Northwind Labs”**

| job_title              | current_status | notes        |
|------------------------|----------------|--------------|
| Software Engineer Intern | Applied      | Via website  |
| Data Analyst Co-op      | Interviewing | Referral     |

**User B — separate companies**

Verify **User B** never sees User A’s rows in list or detail URLs.

---

## 3. Parser fixture strings (copy into tests)

### 3.1 Job listing — structured labels

```text
Software Engineer Intern - Summer 2026
Company: Northwind Labs
Location: San Francisco, CA (Hybrid)
Job type: Internship
Apply by: 10/15/2026

We are looking for a motivated intern...
```

**Expect (approximate):** company `Northwind Labs`, title contains `Software Engineer Intern`, location mentions SF/CA or Hybrid, deadline date detected.

### 3.2 Job listing — minimal posting

```text
Backend Engineer — Remote — $120k-$140k
At Riverstone Health

Must have Python and SQL experience.
```

**Expect:** salary band hint; Remote; company may be weak—user edits on review.

### 3.3 Email — rejection

```text
Subject: Update on your application

Hi Alex,

Thank you for your interest in Northwind Labs. Unfortunately, we will be moving forward with other candidates at this time.

Best,
Jamie Chen
```

**Expect:** suggested status **Rejected**; contact hint possibly “Jamie Chen”; company weak.

### 3.4 Email — interview invite

```text
Subject: Next steps — Software Intern role

Hi Alex,

We would like to schedule a 30-minute video interview with the team. Please reply with your availability.

Thanks,
recruiting@northwindlabs.example
```

**Expect:** suggested **Interviewing**; company hint from domain (if you implement domain rule).

### 3.5 Email — online assessment

```text
Subject: Complete your online assessment

Please complete the HackerRank assessment within 5 days. Good luck!
```

**Expect:** suggested **OA** or **Applied** depending on your rule ordering—**document** which you chose and why.

---

## 4. Form field checklist (server-side validation)

### 4.1 Application create / edit

| Field              | Required MVP | Notes                          |
|--------------------|-------------|--------------------------------|
| `company_id`       | Yes         | Must belong to current user   |
| `job_title`        | Yes         |                                |
| `status_id`        | Yes on create | Must exist in `statuses`   |
| `location`         | No          |                                |
| `job_type`         | No          |                                |
| `salary_range`     | No          | Free text                      |
| `application_date` | No          | Validate date if present       |
| `deadline`         | No          | Validate date if present       |
| `notes`            | No          |                                |

### 4.2 Company create / edit

| Field           | Required MVP |
|-----------------|--------------|
| `company_name`  | Yes          |
| `industry`      | No           |
| `location`      | No           |
| `website`       | No           |

### 4.3 Contact create / edit

| Field           | Required MVP |
|-----------------|--------------|
| `contact_name`  | No (but encourage at least one identifier) |
| `contact_role`  | No           |
| `email`         | No           |
| `phone`         | No           |

### 4.4 Parser review (confirm POST)

| Field / control     | Required MVP |
|---------------------|--------------|
| `company` resolution | Yes: existing id OR new name |
| `job_title`         | Yes for new application path   |
| `status_id`         | Yes                            |

---

## 5. Optional SQL smoke checks (SQLite CLI)

After implementation:

```sql
-- Each application has at least one history row with matching status
SELECT a.application_id, a.status_id AS app_status_id, h.status_id AS latest_hist_status_id
FROM applications a
JOIN application_status_history h ON h.history_id = (
  SELECT history_id FROM application_status_history
  WHERE application_id = a.application_id
  ORDER BY changed_at DESC, history_id DESC LIMIT 1
)
WHERE a.status_id != h.status_id;
```

Expect **zero rows** if your invariant holds.

---

## 6. Presentation checklist (demo day)

- [ ] Register new user live or use seeded account  
- [ ] Create company + application + status change (show history)  
- [ ] Add contact  
- [ ] Paste job fixture → review → confirm  
- [ ] Show SQLite schema or ERD slide referencing [entity-relationship-diagram.md](entity-relationship-diagram.md)
