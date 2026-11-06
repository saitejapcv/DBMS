
from psycopg import Connection

from app.schemas.professor_schema import ProfessorRegistration


# 1. CREATE PROFESSOR
def create_professor(
    conn: Connection,
    professor: ProfessorRegistration,
    password_hash: str
):
    user_query = """
        INSERT INTO users (
            username,
            email,
            name,
            password_hash
        )
        VALUES (%s, %s, %s, %s)
    """

    professor_query = """
        INSERT INTO professors (
            user_id,
            employee_id,
            designation,
            department_code
        )
        VALUES (%s, %s, %s, %s)
    """

    with conn.transaction():

        # Step 1: Create user account
        conn.execute(
            user_query,
            (
                professor.username,
                professor.email,
                professor.name,
                password_hash
            )
        )

        # Step 2: Retrieve generated user_id
        user = conn.execute(
            """
            SELECT currval(
                pg_get_serial_sequence('public.users', 'user_id')
            ) AS user_id
            """
        ).fetchone()

        user_id = user["user_id"]

        # Step 3: Set RLS identity for the new professor
        conn.execute(
            "SELECT set_config('app.user_id', %s, TRUE)",
            (str(user_id),)
        )

        # Step 4: Create professor profile
        conn.execute(
            professor_query,
            (
                user_id,
                professor.employee_id,
                professor.designation,
                professor.department_code
            )
        )

    return user_id


# 2. GET ALL PROFESSORS
def get_all_professors(conn: Connection):
    query = """
        SELECT
            p.employee_id,
            u.name,
            u.email,
            p.designation,
            p.department_code,
            d.department_name
        FROM professors p
        JOIN users u
            ON p.user_id = u.user_id
        JOIN departments d
            ON p.department_code = d.department_code
        ORDER BY p.employee_id;
    """

    rows = conn.execute(query).fetchall()


    return rows


# 3. GET PROFESSOR BY EMPLOYEE ID
def get_professor_by_employee_id(
    conn: Connection,
    employee_id: str
):
    query = """
        SELECT
            p.employee_id,
            u.name,
            u.email,
            p.designation,
            p.department_code,
            d.department_name
        FROM professors p
        JOIN users u
            ON p.user_id = u.user_id
        JOIN departments d
            ON p.department_code = d.department_code
        WHERE p.employee_id = %s;
    """

    return conn.execute(
        query,
        (employee_id,)
    ).fetchone()


# 4. UPDATE PROFESSOR
def update_professor(
    conn: Connection,
    employee_id: str,
    designation: str,
    department_code: str
):
    query = """
        WITH updated_professor AS (
            UPDATE professors
            SET
                designation = %s,
                department_code = %s
            WHERE employee_id = %s
            RETURNING user_id, employee_id, designation, department_code
        )
        SELECT
            p.employee_id,
            u.name,
            u.email,
            p.designation,
            p.department_code,
            d.department_name
        FROM updated_professor p
        JOIN users u
            ON p.user_id = u.user_id
        JOIN departments d
            ON p.department_code = d.department_code;
    """

    return conn.execute(
        query,
        (designation, department_code, employee_id)
    ).fetchone()

# 5. DELETE PROFESSOR
def delete_professor(
    conn: Connection,
    employee_id: str
):
    query = """
        DELETE FROM professors
        WHERE employee_id = %s
        RETURNING user_id, employee_id;
    """

    with conn.transaction():
        result = conn.execute(
            query,
            (employee_id,)
        ).fetchone()

    return result
