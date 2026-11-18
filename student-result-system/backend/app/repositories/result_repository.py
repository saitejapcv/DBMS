from decimal import Decimal

from psycopg import Connection

from app.schemas.result_schema import RevaluationCreate, RevaluationDecision


def get_summary(conn: Connection, student_id: int):
    return conn.execute(
        "SELECT student_id, roll_no, admission_year, cgpa, backlog_count "
        "FROM v_student_academic_summary WHERE student_id = %s",
        (student_id,),
    ).fetchone()


def get_transcript(conn: Connection, student_id: int):
    return conn.execute(
        """
        SELECT enrollment_id, subject_code, subject_name, credits,
               academic_year, term, semester_no, attempt_no,
               total_marks, grade, grade_points, result_status
        FROM v_transcript
        WHERE student_id = %s
        ORDER BY academic_year, semester_no, subject_code
        """,
        (student_id,),
    ).fetchall()


def get_backlogs(conn: Connection, student_id: int):
    return conn.execute(
        """
        SELECT subject_code, subject_name, grade, grade_points,
               academic_year, term, semester_no
        FROM v_backlog
        WHERE student_id = %s
        ORDER BY academic_year, semester_no, subject_code
        """,
        (student_id,),
    ).fetchall()


def get_grade_scale(conn: Connection):
    return conn.execute(
        "SELECT letter_grade, min_marks, grade_points FROM grade_scale "
        "ORDER BY min_marks DESC NULLS LAST, letter_grade"
    ).fetchall()


def get_cgpa(conn: Connection, student_id: int):
    return conn.execute("SELECT fn_cgpa(%s) AS value", (student_id,)).fetchone()["value"]


def get_sgpa(conn: Connection, student_id: int, semester_no: int):
    return conn.execute(
        "SELECT fn_sgpa(%s, %s) AS value", (student_id, semester_no)
    ).fetchone()["value"]


def get_enrollment_total(conn: Connection, enrollment_id: int):
    return conn.execute(
        "SELECT fn_total(%s) AS total_marks, fn_grade(fn_total(%s)) AS suggested_grade",
        (enrollment_id, enrollment_id),
    ).fetchone()


def get_assignment_owner(conn: Connection, assignment_id: int):
    return conn.execute(
        "SELECT professor_id, submitted_at, published_at FROM teaching_assignments "
        "WHERE assignment_id = %s",
        (assignment_id,),
    ).fetchone()


def publish_results(conn: Connection, assignment_id: int):
    conn.execute("CALL sp_publish_results(%s)", (assignment_id,))


def get_enrollment_owner(conn: Connection, enrollment_id: int):
    return conn.execute(
        """
        SELECT e.student_id, e.assignment_id, ta.professor_id
        FROM enrollments e
        JOIN teaching_assignments ta ON ta.assignment_id = e.assignment_id
        WHERE e.enrollment_id = %s
        """,
        (enrollment_id,),
    ).fetchone()


def create_revaluation(conn: Connection, data: RevaluationCreate):
    conn.execute(
        """
        CALL sp_request_revaluation(
            %s, %s, %s, make_interval(days => %s)
        )
        """,
        (data.enrollment_id, data.component_id, data.reason, data.window_days),
    )

def list_revaluations(conn: Connection, user_id: int, role: str):
    if role == "professor":
        where = "ta.professor_id = %s"
        params = (user_id,)
    elif role == "student":
        where = "e.student_id = %s"
        params = (user_id,)
    else:
        where = "TRUE"
        params = ()
    return conn.execute(
        f"""
        SELECT v.request_id, v.enrollment_id, v.component_id, v.reason,
               v.old_marks, v.requested_at, v.reviewed_by, v.decision,
               v.decided_at, v.revaluation_status
        FROM v_reval_status v
        JOIN enrollments e ON e.enrollment_id = v.enrollment_id
        JOIN teaching_assignments ta ON ta.assignment_id = e.assignment_id
        WHERE {where}
        ORDER BY v.requested_at DESC
        """,
        params,
    ).fetchall()


def get_revaluation_assignment_owner(conn: Connection, request_id: int):
    return conn.execute(
        """
        SELECT ta.professor_id
        FROM revaluation_request rr
        JOIN enrollments e ON e.enrollment_id = rr.enrollment_id
        JOIN teaching_assignments ta ON ta.assignment_id = e.assignment_id
        WHERE rr.request_id = %s
        """,
        (request_id,),
    ).fetchone()


def decide_revaluation(
    conn: Connection,
    request_id: int,
    reviewer_id: int,
    data: RevaluationDecision,
):
    conn.execute(
        "CALL sp_decide_revaluation(%s, %s, %s, %s)",
        (request_id, reviewer_id, data.decision, data.new_marks),
    )
