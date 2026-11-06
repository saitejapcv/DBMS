-- Create a separate application login
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'app_user'
    ) THEN
        CREATE ROLE app_user
        LOGIN
        PASSWORD 'change_this_local_password';
    END IF;
END
$$;

-- Allow connection to our project database
GRANT CONNECT
ON DATABASE student_result_system
TO app_user;

-- Allow access to public schema
GRANT USAGE
ON SCHEMA public
TO app_user;

GRANT USAGE ON SCHEMA public TO app_user;

GRANT SELECT
ON users, departments, students, professors, subjects
TO app_user;

GRANT INSERT, UPDATE, DELETE
ON departments, students, professors, subjects
TO app_user;

GRANT INSERT (username, email, password_hash, name)
ON users
TO app_user;
