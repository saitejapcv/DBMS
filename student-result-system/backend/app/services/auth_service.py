from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from app.repositories.auth_repository import get_user_by_username
from app.services.token_service import create_access_token

password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False

from fastapi import HTTPException, status


def authenticate_user(conn, username: str, password: str):
    user = get_user_by_username(conn, username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if user["role"] == "unassigned":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have an assigned role",
        )

    access_token = create_access_token(
        user_id=user["user_id"],
        role=user["role"],
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

