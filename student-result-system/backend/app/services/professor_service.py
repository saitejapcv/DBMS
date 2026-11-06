
from psycopg import Connection

from app.schemas.professor_schema import ProfessorRegistration

from app.repositories.professor_repository import (
    create_professor,
    get_all_professors,
    get_professor_by_employee_id,
    update_professor,
    delete_professor
)

from app.services.auth_service import hash_password


def register_professor(
    conn: Connection,
    professor: ProfessorRegistration
):
    password_hash = hash_password(professor.password)

    user_id = create_professor(
        conn,
        professor,
        password_hash
    )

    return {
        "message": "Professor registration successful",
        "user_id": user_id
    }


def list_professors(conn: Connection):
    return get_all_professors(conn)


def get_professor(
    conn: Connection,
    employee_id: str
):
    return get_professor_by_employee_id(
        conn,
        employee_id
    )


def edit_professor(
    conn: Connection,
    employee_id: str,
    designation: str,
    department_code: str
):
    return update_professor(
        conn,
        employee_id,
        designation,
        department_code
    )


def remove_professor(
    conn: Connection,
    employee_id: str
):
    return delete_professor(
        conn,
        employee_id
    )
