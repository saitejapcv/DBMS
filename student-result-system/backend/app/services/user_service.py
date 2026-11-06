from psycopg import Connection

from app.repositories.user_repository import (
    get_all_users,
    get_user_by_id,
    delete_user,
    update_user,
)
from app.schemas.user_schema import UserUpdate


def get_user(conn: Connection, user_id: int):
    return get_user_by_id(conn, user_id)


def list_users(conn: Connection):
    return get_all_users(conn)


def update_user_details(
    conn: Connection,
    user_id: int,
    user: UserUpdate,
):
    return update_user(
        conn,
        user_id,
        user.username,
        str(user.email) if user.email is not None else None,
        user.name,
        user.is_admin,
    )


def delete_user_account(conn: Connection, user_id: int):
    return delete_user(conn, user_id)
