from psycopg import Connection


def get_user_by_username(conn: Connection, username: str):
    query = """
        SELECT
            u.user_id,
            u.username,
            u.email,
            u.name,
            u.password_hash,
            r.role
        FROM users u
        JOIN v_user_role r ON u.user_id = r.user_id
        WHERE u.username = %s;
    """

    return conn.execute(query, (username,)).fetchone()