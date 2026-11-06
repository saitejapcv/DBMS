
from psycopg import Connection

from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate
)

from app.repositories.department_repository import (
    create_department,
    get_all_departments,
    get_department_by_code,
    update_department,
    delete_department,
    assign_department_head
)


def register_department(
    conn: Connection,
    department: DepartmentCreate
):
    return create_department(conn, department)


def list_departments(conn: Connection):
    return get_all_departments(conn)


def get_department(
    conn: Connection,
    department_code: str
):
    return get_department_by_code(
        conn,
        department_code
    )


def edit_department(
    conn: Connection,
    department_code: str,
    department: DepartmentUpdate
):
    return update_department(
        conn,
        department_code,
        department
    )


def remove_department(
    conn: Connection,
    department_code: str
):
    return delete_department(
        conn,
        department_code
    )

def set_department_head(
    conn: Connection,
    department_code: str,
    head_professor_id: int
):
    return assign_department_head(
        conn,
        department_code,
        head_professor_id
    )

