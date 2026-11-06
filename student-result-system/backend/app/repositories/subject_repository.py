
from psycopg import Connection

from app.schemas.subject_schema import (
    SubjectCreate,
    SubjectUpdate
)


# 1. CREATE SUBJECT
def create_subject(
    conn: Connection,
    subject: SubjectCreate
):
    query = """
        INSERT INTO subjects (
            subject_code,
            subject_name,
            credits,
            department_code
        )
        VALUES (%s, %s, %s, %s)
        RETURNING
            subject_code,
            subject_name,
            credits,
            department_code;
    """

    result = conn.execute(
        query,
        (
            subject.subject_code,
            subject.subject_name,
            subject.credits,
            subject.department_code
        )
    ).fetchone()

    if result is None:
        return None

    return get_subject_by_code(
        conn,
        result["subject_code"]
    )


# 2. GET ALL SUBJECTS
def get_all_subjects(conn: Connection):
    query = """
        SELECT
            s.subject_code,
            s.subject_name,
            s.credits,
            s.department_code,
            d.department_name
        FROM subjects s
        JOIN departments d
            ON s.department_code = d.department_code
        ORDER BY s.subject_code;
    """

    return conn.execute(query).fetchall()


# 3. GET SUBJECT BY CODE
def get_subject_by_code(
    conn: Connection,
    subject_code: str
):
    query = """
        SELECT
            s.subject_code,
            s.subject_name,
            s.credits,
            s.department_code,
            d.department_name
        FROM subjects s
        JOIN departments d
            ON s.department_code = d.department_code
        WHERE s.subject_code = %s;
    """

    return conn.execute(
        query,
        (subject_code,)
    ).fetchone()


# 4. UPDATE SUBJECT
def update_subject(
    conn: Connection,
    subject_code: str,
    subject: SubjectUpdate
):
    query = """
        WITH updated_subject AS (
            UPDATE subjects
            SET
                subject_name = %s,
                credits = %s,
                department_code = %s
            WHERE subject_code = %s
            RETURNING *
        )
        SELECT
            s.subject_code,
            s.subject_name,
            s.credits,
            s.department_code,
            d.department_name
        FROM updated_subject s
        JOIN departments d
            ON s.department_code = d.department_code;
    """

    return conn.execute(
        query,
        (
            subject.subject_name,
            subject.credits,
            subject.department_code,
            subject_code
        )
    ).fetchone()


# 5. DELETE SUBJECT
def delete_subject(
    conn: Connection,
    subject_code: str
):
    query = """
        DELETE FROM subjects
        WHERE subject_code = %s
        RETURNING subject_code;
    """

    return conn.execute(
        query,
        (subject_code,)
    ).fetchone()
