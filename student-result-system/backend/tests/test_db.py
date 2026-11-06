from app.database import get_registration_db_connection


def test_database_connection():
    db = get_registration_db_connection()

    try:
        conn = next(db)

        result = conn.execute("""
            SELECT
                current_user,
                current_database(),
                version()
        """).fetchone()

        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    test_database_connection()