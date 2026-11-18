from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.database import get_user_db_connection
from app.dependencies import get_current_user, require_professor, require_student
from app.repositories import result_repository as repo
from app.schemas.result_schema import (
    AcademicSummaryResponse,
    BacklogResponse,
    GradeScaleResponse,
    StudentMarkResponse,
    RevaluationCreate,
    RevaluationDecision,
    RevaluationResponse,
    TranscriptResponse,
)
from app.services import result_service as service

router = APIRouter(prefix="/results", tags=["Results & Transcripts"])


@router.get("/me/summary", response_model=AcademicSummaryResponse)
def get_my_summary(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_student()),
):
    result = service.summary(conn, current_user["user_id"])
    if result is None:
        raise HTTPException(status_code=404, detail="Student academic summary not found")
    return result


@router.get("/me/transcript", response_model=list[TranscriptResponse])
def get_my_transcript(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_student()),
):
    return service.transcript(conn, current_user["user_id"])


@router.get("/me/backlogs", response_model=list[BacklogResponse])
def get_my_backlogs(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_student()),
):
    return service.backlogs(conn, current_user["user_id"])


@router.get("/me/cgpa")
def get_my_cgpa(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_student()),
):
    return {"cgpa": service.cgpa(conn, current_user["user_id"])}


@router.get("/me/marks", response_model=list[StudentMarkResponse])
def get_my_marks(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_student()),
):
    return service.student_marks(conn, current_user["user_id"])


@router.get("/me/sgpa/{semester_no}")
def get_my_sgpa(
    semester_no: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_student()),
):
    return {"semester_no": semester_no, "sgpa": service.sgpa(conn, current_user["user_id"], semester_no)}


@router.get("/grade-scale", response_model=list[GradeScaleResponse])
def get_grade_scale(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    return service.grade_scale(conn)


@router.post("/assignments/{assignment_id}/publish", status_code=204)
def publish_assignment_results(
    assignment_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    assignment = repo.get_assignment_owner(conn, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Teaching assignment not found")
    if current_user["role"] not in {"admin", "professor"}:
        raise HTTPException(status_code=403, detail="Only an administrator or assigned professor can publish")
    if current_user["role"] == "professor" and assignment["professor_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the assigned professor can publish")
    service.publish(conn, assignment_id)


@router.post("/revaluation", response_model=RevaluationResponse, status_code=201)
def request_revaluation(
    data: RevaluationCreate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_student()),
):
    owner = repo.get_enrollment_owner(conn, data.enrollment_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    if owner["student_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the enrolled student can request revaluation")
    service.create_revaluation(conn, data)
    rows = service.list_revaluations(conn, current_user["user_id"], "student")
    return rows[0]


@router.get("/revaluation", response_model=list[RevaluationResponse])
def get_revaluations(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in {"student", "professor", "admin"}:
        raise HTTPException(status_code=403, detail="Revaluation access is restricted")
    return service.list_revaluations(conn, current_user["user_id"], current_user["role"])


@router.patch("/revaluation/{request_id}", status_code=204)
def decide_revaluation(
    request_id: int,
    data: RevaluationDecision,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_professor()),
):
    owner = repo.get_revaluation_assignment_owner(conn, request_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Revaluation request not found")
    if owner["professor_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the assigned professor can decide")
    service.decide_revaluation(conn, request_id, current_user["user_id"], data)


@router.get("/enrollments/{enrollment_id}/total")
def get_enrollment_total(
    enrollment_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    owner = repo.get_enrollment_owner(conn, enrollment_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    if current_user["role"] == "student" and owner["student_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user["role"] == "professor" and owner["professor_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return service.enrollment_total(conn, enrollment_id)
