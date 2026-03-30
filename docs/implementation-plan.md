# Implementation Plan

**Project:** Smart Job Tracker  
**Audience:** Single student implementer

---

## 1. Phased build plan

| Phase | Milestone | Outcome | Depends on |
|-------|-----------|---------|------------|
| **P0** | Project skeleton + database + seed | Flask runs; tables exist; `statuses` populated | — |
| **P1** | Authentication | Register, login, logout; protected routes | P0 |
| **P2** | Companies CRUD | Full lifecycle for user-scoped companies | P1 |
| **P3** | Applications + history | Manual create/edit/delete; status changes append history and sync `current_status_id` | P2 |
| **P4** | Contacts | CRUD on application detail with ownership checks | P3 |
| **P5** | Parser + review flow | Paste → preview → confirm; no auto-save | P3 (and P2 for company resolution) |
| **P6** | Polish + deployment | Validation, UX, PythonAnywhere WSGI | P1–P5 |

---

## 2. Milestone breakdown (deliverable artifacts)

| Milestone | You should be able to demonstrate |
|-----------|-----------------------------------|
| P0 | `requirements.txt`, `flask run`, empty home, DB file created |
| P1 | Two users isolated; cannot read other user’s URLs |
| P2 | Company list/create/edit/delete |
| P3 | Application detail shows timeline; status dropdown updates history |
| P4 | Contacts appear under correct application only |
| P5 | Parser preview shows fields; DB unchanged until confirm |
| P6 | Production `SECRET_KEY`, HTTPS, smoke test on PA |

---

## 3. Suggested order of implementation

1. Environment + Flask factory + config  
2. Models + init DB + seed statuses  
3. Auth blueprint + templates  
4. Companies blueprint  
5. Applications blueprint (create with dual insert: app + history)  
6. Status POST handler (history append + current update)  
7. Contacts routes (nested under application ownership)  
8. `parser_service` unit tests / fixtures  
9. Parser routes (session preview, confirm transaction)  
10. Dashboard sorting and empty states  
11. Validation + flash messages  
12. CSS pass + accessibility basics  
13. PythonAnywhere deploy

---

## 4. What to postpone if time runs short

| Feature | Priority |
|---------|----------|
| Email → “suggest existing application” matching | **Optional** — defer |
| `parsed_inputs` rich audit (store full raw text) | Trim to short snapshot or omit raw on preview session |
| Company merge / duplicate detection | **Optional** |
| CSV export | **Optional** |
| Fancy charts / analytics | **Optional** |

**Do not cut:** Auth scoping, history on status change, parser confirmation gate.

---

## 5. Folder and codebase structure (proposal)

```
jobtracker/
  app/
    __init__.py              # create_app(); register blueprints; init extensions
    config.py                # Development vs production settings
    models.py                # SQLAlchemy models
    auth.py                  # Blueprint: register, login, logout
    companies.py             # Blueprint: company CRUD
    applications.py          # Blueprint: applications, status, nested contact routes (or split)
    parser.py                # Blueprint: paste, preview, confirm
    services/
      __init__.py
      parser_service.py      # Pure parsing functions + rule metadata
    templates/
      base.html
      auth/
        login.html
        register.html
      companies/
        list.html
        form.html
      applications/
        list.html
        detail.html
        form.html
      parser/
        paste.html
        review.html
    static/
      css/
        app.css
      js/
        app.js
  instance/
    .gitkeep                 # DB file gitignored
  scripts/
    init_db.py               # create_all + seed statuses (or Flask CLI command)
  tests/
    test_parser_service.py   # Fixture strings for parser
  requirements.txt
  wsgi.py                    # PythonAnywhere entry
  README.md                  # How to run locally and deploy (your course may require)
```

**Responsibilities**

| File / area | Responsibility |
|-------------|----------------|
| `__init__.py` | Wire app, extensions, blueprints; no business rules |
| `models.py` | Schema mapping; relationships for convenient queries |
| `*_service.py` | Parser logic isolated from HTTP |
| Blueprints | Routes + request/response only |
| `templates/` | Jinja HTML; extend `base.html` |
| `static/` | CSS/JS assets |
| `scripts/` or CLI | One-shot DB setup |

---

## 6. Testing strategy (lightweight)

- **Manual:** Script a demo path for your presentation (see walkthrough verify steps).
- **Automated (recommended small):** `pytest` on `parser_service` only—fast, no browser.
- **Security smoke:** Log in as user A; manually change URL to user B’s resource id; expect 404/403.
