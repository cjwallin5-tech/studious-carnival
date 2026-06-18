"""Tests that the graph API endpoints are wired up correctly.

These assert the route exists and responds cleanly. While the algorithms are
unimplemented the endpoints return 501 (Not Implemented); once implemented they
return 200. Both are acceptable here — this test only guards the wiring, so it
keeps passing as students implement the algorithms.
"""

from fastapi.testclient import TestClient

from tests.conftest import register_and_login

OK_OR_NOT_IMPLEMENTED = (200, 501)


def test_recommendations_endpoint_wired(client: TestClient) -> None:
    headers = register_and_login(client, "alice")
    uid = client.get("/api/v1/auth/me", headers=headers).json()["id"]
    resp = client.get(f"/api/v1/graph/users/{uid}/recommendations")
    assert resp.status_code in OK_OR_NOT_IMPLEMENTED


def test_path_endpoint_wired(client: TestClient) -> None:
    a = register_and_login(client, "alice")
    b = register_and_login(client, "bob")
    a_id = client.get("/api/v1/auth/me", headers=a).json()["id"]
    b_id = client.get("/api/v1/auth/me", headers=b).json()["id"]
    resp = client.get(f"/api/v1/graph/users/{a_id}/path/{b_id}")
    assert resp.status_code in OK_OR_NOT_IMPLEMENTED


def test_degrees_endpoint_wired(client: TestClient) -> None:
    a = register_and_login(client, "alice")
    b = register_and_login(client, "bob")
    a_id = client.get("/api/v1/auth/me", headers=a).json()["id"]
    b_id = client.get("/api/v1/auth/me", headers=b).json()["id"]
    resp = client.get(f"/api/v1/graph/users/{a_id}/degrees/{b_id}")
    assert resp.status_code in OK_OR_NOT_IMPLEMENTED


def test_all_paths_endpoint_wired(client: TestClient) -> None:
    a = register_and_login(client, "alice")
    b = register_and_login(client, "bob")
    a_id = client.get("/api/v1/auth/me", headers=a).json()["id"]
    b_id = client.get("/api/v1/auth/me", headers=b).json()["id"]
    resp = client.get(f"/api/v1/graph/users/{a_id}/paths/{b_id}")
    assert resp.status_code in OK_OR_NOT_IMPLEMENTED


def test_influencers_endpoint_wired(client: TestClient) -> None:
    register_and_login(client, "alice")
    resp = client.get("/api/v1/graph/influencers")
    assert resp.status_code in OK_OR_NOT_IMPLEMENTED


def test_graph_endpoint_404_for_unknown_user(client: TestClient) -> None:
    # User validation happens before the algorithm runs, so this is a clean 404.
    resp = client.get("/api/v1/graph/users/99999/recommendations")
    assert resp.status_code == 404
