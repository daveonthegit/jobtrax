-- Seed status lookup rows (run after statuses table exists).
-- Use INSERT OR IGNORE if you need idempotent seeding.

INSERT INTO statuses (status_name, sort_order) VALUES
  ('Saved', 10),
  ('Applied', 20),
  ('OA', 30),
  ('Interviewing', 40),
  ('Offer', 50),
  ('Rejected', 60),
  ('Withdrawn', 70);
