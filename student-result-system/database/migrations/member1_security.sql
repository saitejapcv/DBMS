-- Derive a user's role from the admin flag or their profile.
CREATE VIEW v_user_role AS
SELECT
    u.user_id,
    u.username,
    u.email,
    u.name,
    CASE
        WHEN u.is_admin = TRUE THEN 'admin'
        WHEN s.user_id IS NOT NULL THEN 'student'
        WHEN p.user_id IS NOT NULL THEN 'professor'
        ELSE 'unassigned'
    END AS role
FROM users u
LEFT JOIN students s
    ON u.user_id = s.user_id
LEFT JOIN professors p
    ON u.user_id = p.user_id;

-- Enable row-level security on identity and profile tables.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE professors ENABLE ROW LEVEL SECURITY;

-- Also subject the table owner to RLS (superusers still bypass RLS).
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE students FORCE ROW LEVEL SECURITY;
ALTER TABLE professors FORCE ROW LEVEL SECURITY;

-- The backend will set app.user_id from the authenticated identity.
-- Do not accept this value directly from an untrusted client request.
CREATE POLICY users_self_access
ON users
FOR ALL
USING (
    user_id = current_setting('app.user_id', TRUE)::BIGINT
)
WITH CHECK (
    user_id = current_setting('app.user_id', TRUE)::BIGINT
);

CREATE POLICY students_self_access
ON students
FOR ALL
USING (
    user_id = current_setting('app.user_id', TRUE)::BIGINT
)
WITH CHECK (
    user_id = current_setting('app.user_id', TRUE)::BIGINT
);

CREATE POLICY professors_self_access
ON professors
FOR ALL
USING (
    user_id = current_setting('app.user_id', TRUE)::BIGINT
)
WITH CHECK (
    user_id = current_setting('app.user_id', TRUE)::BIGINT
);

