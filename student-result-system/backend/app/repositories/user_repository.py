from psycopg import Connection


def get_user_by_id(conn: Connection, user_id: int):
    query = """
        SELECT user_id, username, email, name, role
        FROM v_user_role
        WHERE user_id = %s;
    """

    return conn.execute(query, (user_id,)).fetchone()


def get_all_users(conn: Connection):
    query = """
        SELECT user_id, username, email, name, role
        FROM v_user_role
        ORDER BY user_id;
    """

    return conn.execute(query).fetchall()


def update_user(
    conn: Connection,
    user_id: int,
    username: str | None,
    email: str | None,
    name: str | None,
    is_admin: bool | None,
):
    query = """
        UPDATE users
        SET
            username = COALESCE(%s, username),
            email = COALESCE(%s, email),
            name = COALESCE(%s, name),
            is_admin = COALESCE(%s, is_admin)
        WHERE user_id = %s
        RETURNING user_id;
    """

    with conn.transaction():
        updated_user = conn.execute(
            query,
            (username, email, name, is_admin, user_id),
        ).fetchone()

    if updated_user is None:
        return None

    return get_user_by_id(conn, updated_user["user_id"])


def delete_user(conn: Connection, user_id: int):
    query = """
        DELETE FROM users
        WHERE user_id = %s
        RETURNING user_id;
    """

    with conn.transaction():
        return conn.execute(query, (user_id,)).fetchone()
