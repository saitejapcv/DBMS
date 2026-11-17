from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.database import get_user_db_connection
from app.dependencies import get_current_user, require_admin, require_professor
from app.schemas.academic_schema import (
    TeachingAssignmentCreate,
    TeachingAssignmentResponse,
    EnrollmentCreate,
    EnrollmentResponse,
    EvaluationComponentCreate,
    EvaluationComponentResponse,
    BulkMarksRequest,
    MarkResponse,
)
from app.services import academic_service as service

router = APIRouter(prefix="/assignments", tags=["Assignments & Marks"])


# 1. CREATE TEACHING ASSIGNMENT (Admin)
@router.post("/", response_model=TeachingAssignmentResponse, status_code=201)
def create_assignment_route(
    data: TeachingAssignmentCreate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    return service.register_teaching_assignment(conn, data)


# 2. GET ALL TEACHING ASSIGNMENTS
@router.get("/", response_model=list[TeachingAssignmentResponse])
def get_assignments_route(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    return service.list_teaching_assignments(conn)


# 3. GET TEACHING ASSIGNMENT BY ID
@router.get("/{assignment_id}", response_model=TeachingAssignmentResponse)
def get_assignment_route(
    assignment_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    assignment = service.get_teaching_assignment(conn, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Teaching assignment not found")
    return assignment


# 4. SUBMIT TEACHING ASSIGNMENT (Fires weightage = 100 trigger)
@router.patch("/{assignment_id}/submit", response_model=TeachingAssignmentResponse)
def submit_assignment_route(
    assignment_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_professor()),
):
    assignment = service.get_teaching_assignment(conn, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Teaching assignment not found")
    if assignment["professor_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the assigned professor can submit")
    return service.mark_assignment_submitted(conn, assignment_id)


# 5. ENROLL STUDENT IN ASSIGNMENT
@router.post("/{assignment_id}/enrollments", response_model=EnrollmentResponse, status_code=201)
def enroll_student_route(
    assignment_id: int,
    data: EnrollmentCreate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    return service.enroll_student(conn, assignment_id, data)


# 6. LIST ENROLLMENTS FOR ASSIGNMENT
@router.get("/{assignment_id}/enrollments", response_model=list[EnrollmentResponse])
def get_enrollments_route(
    assignment_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    return service.list_assignment_enrollments(conn, assignment_id)


# 7. ADD EVALUATION COMPONENT
@router.post(
    "/{assignment_id}/components",
    response_model=EvaluationComponentResponse,
    status_code=201,
)
def add_component_route(
    assignment_id: int,
    data: EvaluationComponentCreate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_professor()),
):
    assignment = service.get_teaching_assignment(conn, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Teaching assignment not found")
    if assignment["professor_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only the assigned professor can add components")
    return service.add_evaluation_component(conn, assignment_id, data)


# 8. LIST EVALUATION COMPONENTS FOR ASSIGNMENT
@router.get(
    "/{assignment_id}/components",
    response_model=list[EvaluationComponentResponse],
)
def get_components_route(
    assignment_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    return service.list_assignment_components(conn, assignment_id)


# 9. BULK UPLOAD / UPSERT MARKS (Professor)
@router.post("/{assignment_id}/marks/bulk", response_model=list[MarkResponse])
def bulk_upload_marks_route(
    assignment_id: int,
    data: BulkMarksRequest,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_professor()),
):
    return service.upload_bulk_marks(
        conn, assignment_id, current_user["user_id"], data
    )


# 10. GET MARKS FOR COMPONENT
@router.get("/components/{component_id}/marks", response_model=list[MarkResponse])
def get_component_marks_route(
    component_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    return service.list_component_marks(conn, component_id)