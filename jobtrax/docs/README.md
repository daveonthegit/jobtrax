# Smart Job Tracker — Documentation Index

This folder contains the full planning and design package for **Smart Job Tracker**, a database-driven Flask + SQLite web application for students to track job applications, with a rule-based paste parser and mandatory review before saving.

## How to use these documents

- **Implement the app yourself** using [implementation-walkthrough.md](implementation-walkthrough.md) as your primary build sequence.
- **Cite** [database-design.md](database-design.md) and [entity-relationship-diagram.md](entity-relationship-diagram.md) in your course write-up for normalization and ERD.
- **Reference** [routes-and-pages.md](routes-and-pages.md) and [parsing-design.md](parsing-design.md) when explaining behavior and data flow.

## Document map

| Document | Purpose |
|----------|---------|
| [design-rationale.md](design-rationale.md) | Concept critique, schema refinements vs. original draft |
| [product-requirements.md](product-requirements.md) | PRD: scope, stories, functional/non-functional requirements |
| [technical-design.md](technical-design.md) | Architecture, stack, security, deployment, risks |
| [database-design.md](database-design.md) | Entities, keys, cardinalities, 3NF/BCNF discussion |
| [entity-relationship-diagram.md](entity-relationship-diagram.md) | Text ERD, Mermaid diagram, relationship narrative |
| [implementation-plan.md](implementation-plan.md) | Phased milestones, folder structure, deferrals |
| [routes-and-pages.md](routes-and-pages.md) | Flask routes, methods, read/write per endpoint |
| [parsing-design.md](parsing-design.md) | Job vs. email parsing rules, review flow, limitations |
| [implementation-walkthrough.md](implementation-walkthrough.md) | Self-guided steps 1–15 with verify/pitfalls |
| [starter-assets-and-fixtures.md](starter-assets-and-fixtures.md) | Seed ideas, parser fixtures, form checklists |
| [sql/schema_reference.sql](sql/schema_reference.sql) | Reference `CREATE TABLE` for SQLite (adapt to your ORM) |
| [sql/seed_statuses.sql](sql/seed_statuses.sql) | Status lookup seed data |

## Project constraints (non-negotiables)

- **Stack:** Python 3.10+, Flask, SQLite, server-rendered HTML (Jinja2), CSS, vanilla JavaScript.
- **Hosting:** PythonAnywhere-compatible (WSGI, instance folder for DB).
- **Schema:** At least four tables; design targets **3NF/BCNF** with one documented intentional denormalization.
- **Parser:** Rule-based (regex + keywords), **no** auto-save without user confirmation on a review step.
- **Out of scope for MVP:** React/SPA, Docker, PostgreSQL, Celery, paid cloud APIs, ML/NLP services.

## Repository layout (when you create the app)

See [implementation-plan.md](implementation-plan.md) for the recommended `jobtracker/` tree. This repo currently holds **documentation only** until you scaffold the application.
