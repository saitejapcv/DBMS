from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.database import get_user_db_connection
from app.dependencies import get_current_user, require_admin
from app.schemas.user_schema import UserResponse, UserUpdate
from app.services.user_service import (
    delete_user_account,
    get_user,
    list_users,
    update_user_details,
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_route(
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_user_db_connection),
):
    user = get_user(conn, current_user["user_id"])

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/", response_model=list[UserResponse])
def list_users_route(
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    return list_users(conn)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_route(
    user_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    user = get_user(conn, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user_route(
    user_id: int,
    user: UserUpdate,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    updated_user = update_user_details(conn, user_id, user)

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user


@router.delete("/{user_id}")
def delete_user_route(
    user_id: int,
    conn: Connection = Depends(get_user_db_connection),
    current_user: dict = Depends(require_admin()),
):
    deleted_user = delete_user_account(conn, user_id)

    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User deleted successfully",
        "user_id": deleted_user["user_id"],
    }
