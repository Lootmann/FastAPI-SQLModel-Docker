from fastapi import status
from fastapi.testclient import TestClient

from api.models import auths as auth_model
from tests.factory import random_string


class TestGetUser:
    def test_get_all_users(self, client: TestClient, login_fixture):
        _, headers = login_fixture

        resp = client.get("/users", headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) == 1

    def test_get_user_find_by_id(self, client: TestClient, login_fixture):
        user, headers = login_fixture

        resp = client.get(f"/users/{user.id}", headers=headers)
        assert resp.status_code == status.HTTP_200_OK

        # new user
        username, password = random_string(), random_string()
        resp = client.post(
            "/users",
            json={"username": username, "password": password},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        token_resp = client.post(
            "/auth/token", data={"username": username, "password": password}
        )
        token = auth_model.Token(**token_resp.json())

        user_id = resp.json()["id"]
        resp = client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        assert resp.status_code == status.HTTP_200_OK


class TestPostUser:
    def test_create_user(self, client: TestClient):
        resp = client.post(
            "/users",
            json={"username": random_string(), "password": "hogehoge"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_user_with_short_password(self, client: TestClient):
        resp = client.post(
            "/users",
            json={"username": random_string(), "password": "123"},
        )

        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            resp.json()["detail"][0]["msg"]
            == "ensure this value has at least 5 characters"
        )

    def test_create_many_users(self, client: TestClient, login_fixture):
        _, headers = login_fixture

        for _ in range(4):
            resp = client.post(
                "/users",
                json={"username": random_string(), "password": random_string()},
            )
            assert resp.status_code == status.HTTP_201_CREATED

        resp = client.get("/users", headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) == 5
