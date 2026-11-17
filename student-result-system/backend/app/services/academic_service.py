from psycopg import Connection
from app.schemas.academic_schema import (
    TeachingAssignmentCreate,
    EnrollmentCreate,
    EvaluationComponentCreate,
    BulkMarksRequest,
)
from app.repositories import academic_repository as repo


def register_teaching_assignment(conn: Connection, data: TeachingAssignmentCreate):
    return repo.create_teaching_assignment(conn, data)


def list_teaching_assignments(conn: Connection):
    return repo.get_all_teaching_assignments(conn)


def get_teaching_assignment(conn: Connection, assignment_id: int):
    return repo.get_teaching_assignment_by_id(conn, assignment_id)


def mark_assignment_submitted(conn: Connection, assignment_id: int):
    return repo.submit_teaching_assignment(conn, assignment_id)


def enroll_student(conn: Connection, assignment_id: int, data: EnrollmentCreate):
    return repo.create_enrollment(conn, assignment_id, data)


def list_assignment_enrollments(conn: Connection, assignment_id: int):
    return repo.get_enrollments_by_assignment(conn, assignment_id)


def add_evaluation_component(
    conn: Connection, assignment_id: int, data: EvaluationComponentCreate
):
    return repo.create_evaluation_component(conn, assignment_id, data)


def list_assignment_components(conn: Connection, assignment_id: int):
    return repo.get_components_by_assignment(conn, assignment_id)


def upload_bulk_marks(
    conn: Connection, assignment_id: int, professor_id: int, data: BulkMarksRequest
):
    repo.bulk_upsert_marks(
        conn, assignment_id, professor_id, data.component_id, data.marks
    )
    return repo.get_marks_by_component(conn, data.component_id)


def list_component_marks(conn: Connection, component_id: int):
    return repo.get_marks_by_component(conn, component_id)