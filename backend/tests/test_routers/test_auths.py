import time

from fastapi import status
from fastapi.testclient import TestClient

from tests.factory import random_string


class TestPostAuth:
    def test_create_user(self, client: TestClient):
        username, password = random_string(), random_string()
        resp = client.post(
            "/users",
            json={"username": username, "password": password},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        resp = client.post(
            "/auth/token",
            data={"username": username, "password": password},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert "access_token" in resp.json()
        assert "refresh_token" in resp.json()
        assert "token_type" in resp.json()


class TestRefreshToken:
    def test_refresh_token(self, client: TestClient, login_fixture):
        # header: {"Authorization": "Bearer_eyJ...."}
        user, headers = login_fixture

        # In login_fixture, time shifted by 1 sec with utcnow()
        time.sleep(1)
        resp = client.post("/auth/refresh", json={"refresh_token": user.refresh_token})

        old_access_token = headers["Authorization"][:7]
        new_access_token = resp.json()["access_token"]
        assert old_access_token != new_access_token
