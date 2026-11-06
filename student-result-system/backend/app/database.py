import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from fastapi import Depends
from app.dependencies import get_current_user

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

def get_dev_db_connection():
    conn = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )

    try:
        conn.execute(
            "SELECT set_config('app.user_id', %s, TRUE)",
            ("7",)
        )

        yield conn

        # Commit after the endpoint finishes successfully
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_registration_db_connection():
    with psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    ) as conn:
        yield conn

def get_admin_db_connection():
    admin_user_id = os.getenv("ADMIN_USER_ID")

    if not admin_user_id:
        raise RuntimeError("ADMIN_USER_ID is not configured")

    conn = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


    try:
        conn.execute(
            "SELECT set_config('app.user_id', %s, TRUE)",
            (admin_user_id,)
        )

        conn.execute(
            "SELECT set_config('app.is_admin', 'true', TRUE)"
        )

        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_user_db_connection(
    current_user: dict = Depends(get_current_user)
):
    conn = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )

    try:
        conn.execute(
            "SELECT set_config('app.user_id', %s, TRUE)",
            (str(current_user["user_id"]),)
        )

        conn.execute(
            "SELECT set_config('app.is_admin', %s, TRUE)",
            ("true" if current_user["role"] == "admin" else "false",)
        )

        yield conn

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()