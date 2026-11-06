
from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.database import (
    get_user_db_connection
)
from app.dependencies import get_current_user, require_admin

from app.schemas.professor_schema import (
    ProfessorRegistration,
    ProfessorUpdate,
    ProfessorResponse
)

from app.services.professor_service import (
    register_professor,
    list_professors,
    get_professor,
    edit_professor,
    remove_professor
)


router = APIRouter(
    prefix="/professors",
    tags=["Professors"]
)


# 1. REGISTER PROFESSOR
@router.post("/", status_code=201)
def create_professor_route(
    professor: ProfessorRegistration,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    return register_professor(conn, professor)


# 2. GET ALL PROFESSORS
@router.get("/", response_model=list[ProfessorResponse])
def get_professors_route(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    return list_professors(conn)


# 3. GET PROFESSOR BY EMPLOYEE ID
@router.get("/{employee_id}", response_model=ProfessorResponse)
def get_professor_route(
    employee_id: str,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    professor = get_professor(conn, employee_id)

    if professor is None:
        raise HTTPException(
            status_code=404,
            detail="Professor not found"
        )

    return professor


# 4. UPDATE PROFESSOR
@router.put("/{employee_id}", response_model=ProfessorResponse)
def update_professor_route(
    employee_id: str,
    professor: ProfessorUpdate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    updated_professor = edit_professor(
        conn,
        employee_id,
        professor.designation,
        professor.department_code
    )

    if updated_professor is None:
        raise HTTPException(
            status_code=404,
            detail="Professor not found"
        )

    return updated_professor


# 5. DELETE PROFESSOR
@router.delete("/{employee_id}")
def delete_professor_route(
    employee_id: str,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    deleted_professor = remove_professor(conn, employee_id)

    if deleted_professor is None:
        raise HTTPException(
            status_code=404,
            detail="Professor not found"
        )

    return {
        "message": "Professor deleted successfully",
        "employee_id": deleted_professor["employee_id"]
    }
