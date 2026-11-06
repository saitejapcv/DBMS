-- Index for filtering subjects by department
CREATE INDEX IF NOT EXISTS idx_subjects_department_code
ON subjects(department_code);