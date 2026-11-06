from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.database import (
    get_user_db_connection,
    get_registration_db_connection,
)
from app.schemas.student_schema import (
    StudentRegistration,
    StudentResponse,
    StudentUpdate,
)
from app.services.student_service import (
    register_student,
    get_student,
    update_student_details,
    delete_student_details,
    list_students,
)
from app.dependencies import require_admin

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/", response_model=list[StudentResponse])
def list_students_route(
        conn: Connection = Depends(get_user_db_connection),
):
    return list_students(conn)


@router.post("/", status_code=201)
def create_student(
        student: StudentRegistration,
        conn: Connection = Depends(get_registration_db_connection),
):
        return register_student(conn, student)


@router.get("/{roll_no}", response_model=StudentResponse)
def get_student_route(
        roll_no: str,
        conn: Connection = Depends(get_user_db_connection),
):
    student = get_student(
        conn,
        roll_no
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student

@router.put("/{roll_no}")
def update_student_route(
        roll_no: str,
        student: StudentUpdate,
        conn: Connection = Depends(get_user_db_connection),
        current_user: dict = Depends(require_admin()),
):
    result = update_student_details(
        conn,
        roll_no,
        student.current_semester,
        student.department_code,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return result

@router.delete("/{roll_no}")
def delete_student_route(
        roll_no: str,
        conn: Connection = Depends(get_user_db_connection),
        current_user: dict = Depends(require_admin()),
):
    result = delete_student_details(conn, roll_no)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return result


