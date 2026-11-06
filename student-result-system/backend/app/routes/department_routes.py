
from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.database import get_user_db_connection
from app.dependencies import get_current_user, require_admin

from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentHeadUpdate,
)

from app.services.department_service import (
    register_department,
    list_departments,
    get_department,
    edit_department,
    remove_department, set_department_head,
)


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


# 1. CREATE DEPARTMENT
@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department_route(
    department: DepartmentCreate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    return register_department(conn, department)


# 2. GET ALL DEPARTMENTS
@router.get("/", response_model=list[DepartmentResponse])
def get_departments_route(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    return list_departments(conn)


# 3. GET DEPARTMENT BY CODE
@router.get("/{department_code}", response_model=DepartmentResponse)
def get_department_route(
    department_code: str,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(get_current_user),
):
    department = get_department(conn, department_code)

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department


# 4. UPDATE DEPARTMENT
@router.put("/{department_code}", response_model=DepartmentResponse)
def update_department_route(
    department_code: str,
    department: DepartmentUpdate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    updated_department = edit_department(
        conn,
        department_code,
        department
    )

    if updated_department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return updated_department


# 5. DELETE DEPARTMENT
@router.delete("/{department_code}")
def delete_department_route(
    department_code: str,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    deleted_department = remove_department(
        conn,
        department_code
    )

    if deleted_department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return {
        "message": "Department deleted successfully",
        "department_code": deleted_department["department_code"]
    }


@router.put("/{department_code}/head", response_model=DepartmentResponse)
def assign_department_head_route(
        department_code: str,
        head: DepartmentHeadUpdate,
        conn: Connection = Depends(get_user_db_connection),
        current_user: dict = Depends(require_admin()),
):
    department = set_department_head(
        conn,
        department_code,
        head.head_professor_id
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department
