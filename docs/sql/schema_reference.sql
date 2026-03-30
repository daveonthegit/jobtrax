-- Smart Job Tracker — reference schema for SQLite
-- Adapt when translating to SQLAlchemy models.
-- After opening the DB, run: PRAGMA foreign_keys = ON;

-- 1. No dependencies
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE statuses (
  status_id INTEGER PRIMARY KEY AUTOINCREMENT,
  status_name TEXT NOT NULL UNIQUE,
  sort_order INTEGER NOT NULL
);

-- 2. Depends on users
CREATE TABLE companies (
  company_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  company_name TEXT NOT NULL,
  industry TEXT,
  location TEXT,
  website TEXT
  -- Optional: UNIQUE(user_id, company_name)
);

-- 3. Depends on users, companies, statuses
CREATE TABLE applications (
  application_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  company_id INTEGER NOT NULL REFERENCES companies(company_id),
  current_status_id INTEGER NOT NULL REFERENCES statuses(status_id),
  job_title TEXT NOT NULL,
  location TEXT,
  job_type TEXT,
  salary_range TEXT,
  application_date TEXT,
  deadline TEXT,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 4. Depends on users, statuses (before history — history references this)
CREATE TABLE parsed_inputs (
  parse_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  input_type TEXT NOT NULL CHECK (input_type IN ('job_listing', 'email')),
  raw_text TEXT NOT NULL,
  parsed_company_name TEXT,
  parsed_job_title TEXT,
  parsed_status_id INTEGER REFERENCES statuses(status_id),
  parsed_location TEXT,
  parsed_deadline TEXT,
  parsed_contact_name TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 5. Depends on applications, statuses, parsed_inputs
CREATE TABLE application_status_history (
  history_id INTEGER PRIMARY KEY AUTOINCREMENT,
  application_id INTEGER NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
  status_id INTEGER NOT NULL REFERENCES statuses(status_id),
  source_parse_id INTEGER REFERENCES parsed_inputs(parse_id),
  changed_at TEXT NOT NULL DEFAULT (datetime('now')),
  note TEXT
);

-- 6. Depends on applications
CREATE TABLE contacts (
  contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
  application_id INTEGER NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
  contact_name TEXT,
  contact_role TEXT,
  email TEXT,
  phone TEXT
);
