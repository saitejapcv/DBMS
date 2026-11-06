
from psycopg import Connection

from app.schemas.subject_schema import (
    SubjectCreate,
    SubjectUpdate
)

from app.repositories.subject_repository import (
    create_subject,
    get_all_subjects,
    get_subject_by_code,
    update_subject,
    delete_subject
)


def register_subject(
    conn: Connection,
    subject: SubjectCreate
):
    return create_subject(conn, subject)


def list_subjects(conn: Connection):
    return get_all_subjects(conn)


def get_subject(
    conn: Connection,
    subject_code: str
):
    return get_subject_by_code(conn, subject_code)


def edit_subject(
    conn: Connection,
    subject_code: str,
    subject: SubjectUpdate
):
    return update_subject(conn, subject_code, subject)


def remove_subject(
    conn: Connection,
    subject_code: str
):
    return delete_subject(conn, subject_code)
