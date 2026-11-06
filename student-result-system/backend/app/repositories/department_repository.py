
from psycopg import Connection

from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate
)


def create_department(
    conn: Connection,
    department: DepartmentCreate
):
    query = """
        INSERT INTO departments (
            department_code,
            department_name
        )
        VALUES (%s, %s)
        RETURNING
            department_code,
            department_name,
            head_professor_id;
    """

    return conn.execute(
        query,
        (
            department.department_code,
            department.department_name
        )
    ).fetchone()


def get_all_departments(conn: Connection):
    query = """
        SELECT
            department_code,
            department_name,
            head_professor_id
        FROM departments
        ORDER BY department_code;
    """

    return conn.execute(query).fetchall()


def get_department_by_code(
    conn: Connection,
    department_code: str
):
    query = """
        SELECT
            department_code,
            department_name,
            head_professor_id
        FROM departments
        WHERE department_code = %s;
    """

    return conn.execute(
        query,
        (department_code,)
    ).fetchone()


def update_department(
    conn: Connection,
    department_code: str,
    department: DepartmentUpdate
):
    query = """
        UPDATE departments
        SET department_name = %s
        WHERE department_code = %s
        RETURNING
            department_code,
            department_name,
            head_professor_id;
    """

    return conn.execute(
        query,
        (
            department.department_name,
            department_code
        )
    ).fetchone()


def delete_department(
    conn: Connection,
    department_code: str
):
    query = """
        DELETE FROM departments
        WHERE department_code = %s
        RETURNING department_code;
    """

    return conn.execute(
        query,
        (department_code,)
    ).fetchone()

def assign_department_head(
    conn: Connection,
    department_code: str,
    head_professor_id: int
):
    query = """
        UPDATE departments
        SET head_professor_id = %s
        WHERE department_code = %s
        RETURNING
            department_code,
            department_name,
            head_professor_id;
    """

    return conn.execute(
        query,
        (head_professor_id, department_code)
    ).fetchone()