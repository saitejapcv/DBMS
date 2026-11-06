from psycopg import Connection

from app.schemas.student_schema import StudentRegistration


def get_all_students(conn: Connection):
    query = """
    SELECT
            s.roll_no,
            u.name,
            u.email,
            s.admission_year,
            s.current_semester,
            s.cgpa,
            s.backlog_count,
            d.department_name
        FROM students s
        JOIN users u ON s.user_id = u.user_id
        JOIN departments d
            ON s.department_code = d.department_code
        ORDER BY s.roll_no;
    """

    rows = conn.execute(query).fetchall()

    return [dict(row) for row in rows]

def create_student(
        conn: Connection,
        student: StudentRegistration,
        password_hash: str,
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

    student_query = """
        INSERT INTO students (user_id, 
                              roll_no, 
                              admission_year, 
                              current_semester, 
                              department_code
                    )
                    VALUES (%s, %s, %s, %s, %s)"""

    with conn.transaction():

        conn.execute(
            user_query,
            (
                student.username,
                student.email,
                student.name,
                password_hash
            )
        )

        user = conn.execute("""
            SELECT currval(
                pg_get_serial_sequence(
                    'public.users', 'user_id'
                    )
                ) AS user_id
            """).fetchone()

        user_id = user["user_id"]

        conn.execute(
            "SELECT set_config('app.user_id', %s, TRUE)",
            (str(user_id),)
        )

        conn.execute(
            student_query,
            (
                user_id,
                student.roll_no,
                student.admission_year,
                student.current_semester,
                student.department_code,
            )
        )
    return user_id

def get_student_by_roll_no(
        conn: Connection,
        roll_no: str,
):
    query = """
    SELECT 
    s.roll_no,
    u.name,
    u.email,
    s.admission_year,
    s.current_semester,
    s.cgpa,
    s.backlog_count,
    d.department_name
    FROM students s
    JOIN users u ON s.user_id = u.user_id
    JOIN departments d ON s.department_code = d.department_code
    WHERE s.roll_no = %s
    """

    return conn.execute(query, (roll_no,)).fetchone()

def update_student(
    conn: Connection,
    roll_no: str,
    current_semester: int,
    department_code: str,
):
    query = """
        UPDATE students
        SET
            current_semester = %s,
            department_code = %s
        WHERE roll_no = %s
        RETURNING roll_no, current_semester, department_code;
    """

    with conn.transaction():
        result = conn.execute(
            query,
            (current_semester, department_code, roll_no)
        ).fetchone()

    return result

def delete_student(conn: Connection, roll_no: str):
    query = """
    DELETE FROM students WHERE roll_no = %s
    RETURNING roll_no;
    """

    with conn.transaction():
        result = conn.execute(query, (roll_no,)).fetchone()

    return result