from fastapi import APIRouter, Depends
from psycopg import Connection

from app.database import get_admin_db_connection
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    conn: Connection = Depends(get_admin_db_connection),
):
    return authenticate_user(
        conn,
        credentials.username,
        credentials.password,
    )
