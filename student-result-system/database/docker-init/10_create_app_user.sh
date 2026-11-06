#!/usr/bin/env sh
set -eu

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 --set=app_db_password="$APP_DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE app_user LOGIN PASSWORD %L', :'app_db_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user')
\gexec

GRANT CONNECT ON DATABASE student_result_system TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT ON users, departments, students, professors, subjects TO app_user;
GRANT INSERT, UPDATE, DELETE ON departments, students, professors, subjects TO app_user;
GRANT INSERT (username, email, password_hash, name) ON users TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
GRANT SELECT ON v_user_role TO app_user;
SQL
