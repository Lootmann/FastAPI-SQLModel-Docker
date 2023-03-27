import time
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from jose import jwt

from api.cruds import auths as auth_api
from api.settings import Settings
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

    def test_create_token_with_non_exist_user(self, client: TestClient):
        resp = client.post(
            "/auth/token", data={"username": "hoge", "password": "newnew"}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json() == {"detail": "User Not Found"}

    def test_create_token_with_wrong_password(self, client: TestClient):
        resp = client.post(
            "/users",
            json={"username": "hhhhhh", "password": "laksdjfl"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        resp = client.post(
            "/auth/token", data={"username": "hhhhhh", "password": "newnew"}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json() == {"detail": "username or password is invalid"}


class TestJWT:
    def test_invalid_jwt_with_wrong_payload(self):
        credential = Settings()

        expire = datetime.utcnow() + timedelta(credential.refresh_token_expire_minutes)
        token = jwt.encode(
            {"exp": expire}, credential.secret_key, algorithm=credential.algorithm
        )

        with pytest.raises(HTTPException):
            auth_api.check_token(token)

    def test_invalid_jwt_with_expired_date(self):
        credential = Settings()

        expire = datetime.utcnow() + timedelta(days=-1)
        token = jwt.encode(
            {"sub": "hoge", "exp": expire},
            credential.secret_key,
            algorithm=credential.algorithm,
        )

        assert auth_api.check_token(token) is False

    def test_invalid_jwt(self):
        credential = Settings()

        expire = datetime.utcnow() + timedelta(days=-1)
        token = (
            jwt.encode(
                {"sub": "hoge", "exp": expire},
                credential.secret_key,
                algorithm=credential.algorithm,
            )
            + "k"
        )

        with pytest.raises(HTTPException):
            auth_api.check_token(token)


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
