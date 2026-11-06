
from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.database import get_user_db_connection
from app.dependencies import get_current_user, require_admin

from app.schemas.subject_schema import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse
)

from app.services.subject_service import (
    register_subject,
    list_subjects,
    get_subject,
    edit_subject,
    remove_subject
)


router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


# 1. CREATE SUBJECT
@router.post("/", response_model=SubjectResponse, status_code=201)
def create_subject_route(
    subject: SubjectCreate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    return register_subject(conn, subject)


# 2. GET ALL SUBJECTS
@router.get("/", response_model=list[SubjectResponse])
def get_subjects_route(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    return list_subjects(conn)


# 3. GET SUBJECT BY CODE
@router.get("/{subject_code}", response_model=SubjectResponse)
def get_subject_route(
    subject_code: str,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    subject = get_subject(conn, subject_code)

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    return subject


# 4. UPDATE SUBJECT
@router.put("/{subject_code}", response_model=SubjectResponse)
def update_subject_route(
    subject_code: str,
    subject: SubjectUpdate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    updated_subject = edit_subject(
        conn,
        subject_code,
        subject
    )

    if updated_subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    return updated_subject


# 5. DELETE SUBJECT
@router.delete("/{subject_code}")
def delete_subject_route(
    subject_code: str,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    deleted_subject = remove_subject(conn, subject_code)

    if deleted_subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    return {
        "message": "Subject deleted successfully",
        "subject_code": deleted_subject["subject_code"]
    }
