from psycopg import Connection

from app.repositories import result_repository as repo
from app.schemas.result_schema import RevaluationCreate, RevaluationDecision


def summary(conn: Connection, student_id: int):
    return repo.get_summary(conn, student_id)


def transcript(conn: Connection, student_id: int):
    return repo.get_transcript(conn, student_id)


def backlogs(conn: Connection, student_id: int):
    return repo.get_backlogs(conn, student_id)


def grade_scale(conn: Connection):
    return repo.get_grade_scale(conn)


def student_marks(conn: Connection, student_id: int):
    return repo.get_student_marks(conn, student_id)


def cgpa(conn: Connection, student_id: int):
    return repo.get_cgpa(conn, student_id)


def sgpa(conn: Connection, student_id: int, semester_no: int):
    return repo.get_sgpa(conn, student_id, semester_no)


def enrollment_total(conn: Connection, enrollment_id: int):
    return repo.get_enrollment_total(conn, enrollment_id)


def publish(conn: Connection, assignment_id: int):
    repo.publish_results(conn, assignment_id)


def create_revaluation(conn: Connection, data: RevaluationCreate):
    repo.create_revaluation(conn, data)


def list_revaluations(conn: Connection, user_id: int, role: str):
    return repo.list_revaluations(conn, user_id, role)


def decide_revaluation(
    conn: Connection, request_id: int, reviewer_id: int, data: RevaluationDecision
):
    repo.decide_revaluation(conn, request_id, reviewer_id, data)
