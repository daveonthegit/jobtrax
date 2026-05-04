-- One-time migration for databases created before FK columns were aligned with parent PK names.
-- Requires SQLite 3.25.0+ (ALTER TABLE ... RENAME COLUMN).
-- Back up jobtrax.db before running.
--
-- Renames:
--   applications.current_status_id -> status_id   (references statuses.status_id)
--   parsed_inputs.parsed_status_id -> status_id     (references statuses.status_id)
--   application_status_history.source_parse_id -> parse_id (references parsed_inputs.parse_id)

PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

ALTER TABLE applications RENAME COLUMN current_status_id TO status_id;
ALTER TABLE parsed_inputs RENAME COLUMN parsed_status_id TO status_id;
ALTER TABLE application_status_history RENAME COLUMN source_parse_id TO parse_id;

COMMIT;

PRAGMA foreign_keys = ON;
