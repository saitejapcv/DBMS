import os
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from app.database import DATABASE_URL, get_user_db_connection
from app.main import app
from app.services.token_service import create_access_token


@pytest.fixture
def admin_client():
    admin_user_id = int(os.environ["ADMIN_USER_ID"])
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    conn.execute(
        "SELECT set_config('app.user_id', %s, TRUE)",
        (str(admin_user_id),),
    )
    conn.execute("SELECT set_config('app.is_admin', 'true', TRUE)")

    def get_test_db_connection():
        yield conn

    app.dependency_overrides[get_user_db_connection] = get_test_db_connection

    try:
        with TestClient(app) as client:
            headers = {
                "Authorization": (
                    "Bearer " + create_access_token(admin_user_id, "admin")
                )
            }
            yield client, headers, conn, admin_user_id
    finally:
        app.dependency_overrides.pop(get_user_db_connection, None)
        conn.rollback()
        conn.close()


def test_admin_can_read_own_account(admin_client):
    client, headers, _, admin_user_id = admin_client

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["user_id"] == admin_user_id


def test_admin_can_update_user_without_persisting_change(admin_client):
    client, headers, _, admin_user_id = admin_client

    response = client.put(
        f"/users/{admin_user_id}",
        headers=headers,
        json={"name": "Temporary Test Admin"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Temporary Test Admin"


def test_empty_user_update_is_rejected(admin_client):
    client, headers, _, admin_user_id = admin_client

    response = client.put(f"/users/{admin_user_id}", headers=headers, json={})

    assert response.status_code == 422


def test_admin_can_delete_temporary_user_without_persisting_change(admin_client):
    client, headers, conn, _ = admin_client
    unique_suffix = uuid4().hex
    user = conn.execute(
        """
        INSERT INTO users (username, email, name, password_hash)
        VALUES (%s, %s, %s, %s)
        RETURNING user_id;
        """,
        (
            f"test_user_{unique_suffix}",
            f"test_{unique_suffix}@example.com",
            "Temporary Test User",
            "not-a-real-password-hash",
        ),
    ).fetchone()

    response = client.delete(f"/users/{user['user_id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["user_id"] == user["user_id"]
    assert conn.execute(
        "SELECT user_id FROM users WHERE user_id = %s",
        (user["user_id"],),
    ).fetchone() is None


def test_non_admin_cannot_list_users(admin_client):
    client, _, _, _ = admin_client
    headers = {
        "Authorization": "Bearer " + create_access_token(1, "professor"),
    }

    response = client.get("/users/", headers=headers)

    assert response.status_code == 403
