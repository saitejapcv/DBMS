BEGIN;

-- Upgrade existing databases that already used member1_security.sql.
DROP POLICY IF EXISTS users_self_access ON users;
DROP POLICY IF EXISTS users_registration_insert ON users;
DROP POLICY IF EXISTS users_select_access ON users;
DROP POLICY IF EXISTS users_admin_update ON users;
DROP POLICY IF EXISTS users_admin_delete ON users;
DROP POLICY IF EXISTS students_self_access ON students;
DROP POLICY IF EXISTS students_select_access ON students;
DROP POLICY IF EXISTS students_insert_access ON students;
DROP POLICY IF EXISTS students_admin_update ON students;
DROP POLICY IF EXISTS students_admin_delete ON students;
DROP POLICY IF EXISTS professors_self_access ON professors;
DROP POLICY IF EXISTS professors_select_access ON professors;
DROP POLICY IF EXISTS professors_insert_access ON professors;
DROP POLICY IF EXISTS professors_admin_update ON professors;
DROP POLICY IF EXISTS professors_admin_delete ON professors;

CREATE POLICY users_select_access ON users FOR SELECT
USING (current_setting('app.is_admin', TRUE) = 'true'
       OR user_id = current_setting('app.user_id', TRUE)::BIGINT);
CREATE POLICY users_registration_insert ON users FOR INSERT WITH CHECK (TRUE);
CREATE POLICY users_admin_update ON users FOR UPDATE
USING (current_setting('app.is_admin', TRUE) = 'true')
WITH CHECK (current_setting('app.is_admin', TRUE) = 'true');
CREATE POLICY users_admin_delete ON users FOR DELETE
USING (current_setting('app.is_admin', TRUE) = 'true');

CREATE POLICY students_select_access ON students FOR SELECT
USING (current_setting('app.is_admin', TRUE) = 'true'
       OR user_id = current_setting('app.user_id', TRUE)::BIGINT);
CREATE POLICY students_insert_access ON students FOR INSERT
WITH CHECK (current_setting('app.is_admin', TRUE) = 'true'
            OR user_id = current_setting('app.user_id', TRUE)::BIGINT);
CREATE POLICY students_admin_update ON students FOR UPDATE
USING (current_setting('app.is_admin', TRUE) = 'true')
WITH CHECK (current_setting('app.is_admin', TRUE) = 'true');
CREATE POLICY students_admin_delete ON students FOR DELETE
USING (current_setting('app.is_admin', TRUE) = 'true');

CREATE POLICY professors_select_access ON professors FOR SELECT
USING (current_setting('app.is_admin', TRUE) = 'true'
       OR user_id = current_setting('app.user_id', TRUE)::BIGINT);
CREATE POLICY professors_insert_access ON professors FOR INSERT
WITH CHECK (current_setting('app.is_admin', TRUE) = 'true');
CREATE POLICY professors_admin_update ON professors FOR UPDATE
USING (current_setting('app.is_admin', TRUE) = 'true')
WITH CHECK (current_setting('app.is_admin', TRUE) = 'true');
CREATE POLICY professors_admin_delete ON professors FOR DELETE
USING (current_setting('app.is_admin', TRUE) = 'true');

GRANT UPDATE, DELETE ON users TO app_user;
GRANT INSERT, UPDATE, DELETE ON departments, subjects TO app_user;

COMMIT;
