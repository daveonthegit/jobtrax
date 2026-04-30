-- JobTrax — from docs/sql/schema_reference.sql + seed_statuses
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS statuses (
  status_id INTEGER PRIMARY KEY AUTOINCREMENT,
  status_name TEXT NOT NULL UNIQUE,
  sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS companies (
  company_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  company_name TEXT NOT NULL,
  industry TEXT,
  location TEXT,
  website TEXT
);

CREATE TABLE IF NOT EXISTS applications (
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

CREATE TABLE IF NOT EXISTS parsed_inputs (
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

CREATE TABLE IF NOT EXISTS application_status_history (
  history_id INTEGER PRIMARY KEY AUTOINCREMENT,
  application_id INTEGER NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
  status_id INTEGER NOT NULL REFERENCES statuses(status_id),
  source_parse_id INTEGER REFERENCES parsed_inputs(parse_id),
  changed_at TEXT NOT NULL DEFAULT (datetime('now')),
  note TEXT
);

CREATE TABLE IF NOT EXISTS contacts (
  contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
  application_id INTEGER NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
  contact_name TEXT,
  contact_role TEXT,
  email TEXT,
  phone TEXT
);
