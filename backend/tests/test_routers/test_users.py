from fastapi import status
from fastapi.testclient import TestClient

from api.models import auths as auth_model
from api.models import users as user_model
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

        # generate new user's token
        user_id = resp.json()["id"]

        resp = client.post(
            "/auth/token",
            data={"username": username, "password": password},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        token = auth_model.Token(**resp.json())

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


class TestPatchUser:
    def test_update_user(self, client: TestClient, login_fixture):
        user, headers = login_fixture

        resp = client.patch(
            "/users",
            json={"username": "updated :^)", "password": "updated :^)"},
            headers=headers,
        )
        assert resp.status_code == status.HTTP_200_OK

        updated_user = user_model.UserRead(**resp.json())
        assert updated_user.username == "updated :^)"
        assert updated_user.id == user.id

    def test_update_user_without_login(self, client: TestClient):
        resp = client.patch(
            "/users",
            json={"username": "malicious", "password": "hoge"},
        )
        assert resp.json() == {"detail": "Not authenticated"}


class TestDeleteUser:
    def test_delete_user(self, client: TestClient, login_fixture):
        _, headers = login_fixture

        # create new user
        resp = client.post("/users", json={"username": "new D:", "password": "newnew"})
        new_user = user_model.UserRead(**resp.json())

        users = client.get("/users", headers=headers)
        assert len(users.json()) == 2

        # delete a user which is created by login_fixture
        resp = client.delete("/users", headers=headers)
        assert resp.json() is None

        # login_fixture user has been deleted, so headers is already unavailable.
        users = client.get("/users", headers=headers)
        assert users.json() == {"detail": "User Not Found"}

        # get new user token
        resp = client.post(
            "/auth/token", data={"username": "new D:", "password": "newnew"}
        )
        new_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        resp = client.get("/users", headers=new_headers)
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == new_user.id
        assert resp.json()[0]["username"] == new_user.username
