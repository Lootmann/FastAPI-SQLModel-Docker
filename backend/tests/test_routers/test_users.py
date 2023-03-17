from fastapi import status
from fastapi.testclient import TestClient

from tests.factory import random_string


class TestGETUser:
    def test_get_all_user(self, client: TestClient):
        resp = client.get("/users")
        assert resp.status_code == status.HTTP_200_OK


class TestPOSTUser:
    def test_create_user(self, client: TestClient):
        resp = client.post("/users", json={"name": "hoge"})
        assert resp.status_code == status.HTTP_201_CREATED

    def test_create_many_users(self, client: TestClient):
        for _ in range(10):
            resp = client.post("/users", json={"name": random_string()})
            assert resp.status_code == status.HTTP_201_CREATED

        resp = client.get("/users")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) == 10
