import json
from psycopg import Connection
from app.schemas.academic_schema import (
    TeachingAssignmentCreate,
    EnrollmentCreate,
    EvaluationComponentCreate,
    MarkItem,
)


# --- TEACHING ASSIGNMENTS ---
def create_teaching_assignment(conn: Connection, data: TeachingAssignmentCreate):
    query = """
        INSERT INTO teaching_assignments (
            subject_code, professor_id, academic_year, term
        )
        VALUES (%s, %s, %s, %s)
        RETURNING assignment_id, subject_code, professor_id, academic_year, term, submitted_at, published_at;
    """
    return conn.execute(
        query, (data.subject_code, data.professor_id, data.academic_year, data.term)
    ).fetchone()


def get_all_teaching_assignments(conn: Connection):
    query = """
        SELECT assignment_id, subject_code, professor_id, academic_year, term, submitted_at, published_at
        FROM teaching_assignments
        ORDER BY assignment_id;
    """
    return conn.execute(query).fetchall()


def get_teaching_assignment_by_id(conn: Connection, assignment_id: int):
    query = """
        SELECT assignment_id, subject_code, professor_id, academic_year, term, submitted_at, published_at
        FROM teaching_assignments
        WHERE assignment_id = %s;
    """
    return conn.execute(query, (assignment_id,)).fetchone()


def submit_teaching_assignment(conn: Connection, assignment_id: int):
    query = """
        UPDATE teaching_assignments
        SET submitted_at = CURRENT_TIMESTAMP
        WHERE assignment_id = %s
        RETURNING assignment_id, subject_code, professor_id, academic_year, term, submitted_at, published_at;
    """
    return conn.execute(query, (assignment_id,)).fetchone()


# --- ENROLLMENTS ---
def create_enrollment(conn: Connection, assignment_id: int, data: EnrollmentCreate):
    query = """
        INSERT INTO enrollments (student_id, assignment_id)
        VALUES (%s, %s)
        RETURNING enrollment_id, student_id, assignment_id, enrolled_on, grade;
    """
    return conn.execute(query, (data.student_id, assignment_id)).fetchone()


def get_enrollments_by_assignment(conn: Connection, assignment_id: int):
    query = """
        SELECT enrollment_id, student_id, assignment_id, enrolled_on, grade
        FROM enrollments
        WHERE assignment_id = %s
        ORDER BY enrollment_id;
    """
    return conn.execute(query, (assignment_id,)).fetchall()


# --- EVALUATION COMPONENTS ---
def create_evaluation_component(
    conn: Connection, assignment_id: int, data: EvaluationComponentCreate
):
    query = """
        INSERT INTO evaluation_components (assignment_id, name, max_marks, weightage)
        VALUES (%s, %s, %s, %s)
        RETURNING component_id, assignment_id, name, max_marks, weightage;
    """
    return conn.execute(
        query, (assignment_id, data.name, data.max_marks, data.weightage)
    ).fetchone()


def get_components_by_assignment(conn: Connection, assignment_id: int):
    query = """
        SELECT component_id, assignment_id, name, max_marks, weightage
        FROM evaluation_components
        WHERE assignment_id = %s
        ORDER BY component_id;
    """
    return conn.execute(query, (assignment_id,)).fetchall()


# --- MARKS ---
def bulk_upsert_marks(
    conn: Connection,
    assignment_id: int,
    professor_id: int,
    component_id: int,
    marks_list: list[MarkItem],
):
    payload = json.dumps(
        [
            {
                "enrollment_id": item.enrollment_id,
                "marks_obtained": float(item.marks_obtained),
            }
            for item in marks_list
        ]
    )
    conn.execute(
        "CALL sp_bulk_insert_marks(%s, %s, %s, %s::jsonb);",
        (assignment_id, professor_id, component_id, payload),
    )


def get_marks_by_component(conn: Connection, component_id: int):
    query = """
        SELECT m.enrollment_id, e.student_id, m.component_id, m.marks_obtained, m.entered_at
        FROM marks m
        JOIN enrollments e ON m.enrollment_id = e.enrollment_id
        WHERE m.component_id = %s
        ORDER BY e.student_id;
    """
    return conn.execute(query, (component_id,)).fetchall()