"""Tests for the admin/dev endpoints."""

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_reset_wipes_all_data(client: TestClient) -> None:
    headers = register_and_login(client, "alice")
    post = client.post("/api/v1/posts", json={"content": "hello"}, headers=headers)
    assert post.status_code == 201

    resp = client.post("/api/v1/admin/reset")
    assert resp.status_code == 200
    deleted = resp.json()["deleted"]
    assert deleted["users"] == 1
    assert deleted["posts"] == 1

    assert client.get("/api/v1/users").json() == []
    assert client.get("/api/v1/posts").json() == []


def test_reset_on_empty_database_is_fine(client: TestClient) -> None:
    resp = client.post("/api/v1/admin/reset")
    assert resp.status_code == 200
    assert all(n == 0 for n in resp.json()["deleted"].values())
