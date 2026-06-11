from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "healthy"}


def test_register_and_me(client: TestClient) -> None:
    headers = register_and_login(client, "alice")
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"


def test_duplicate_registration_conflicts(client: TestClient) -> None:
    register_and_login(client, "bob")
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "supersecret"},
    )
    assert resp.status_code == 409


def test_protected_route_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_post_lifecycle_and_likes(client: TestClient) -> None:
    headers = register_and_login(client, "carol")

    created = client.post("/api/v1/posts", json={"content": "hello world"}, headers=headers)
    assert created.status_code == 201
    post_id = created.json()["id"]
    assert created.json()["likes_count"] == 0

    # Like it.
    assert client.post(f"/api/v1/posts/{post_id}/like", headers=headers).status_code == 204
    fetched = client.get(f"/api/v1/posts/{post_id}")
    assert fetched.json()["likes_count"] == 1

    # Liking again is idempotent.
    client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
    assert client.get(f"/api/v1/posts/{post_id}").json()["likes_count"] == 1

    # Unlike.
    assert client.delete(f"/api/v1/posts/{post_id}/like", headers=headers).status_code == 204
    assert client.get(f"/api/v1/posts/{post_id}").json()["likes_count"] == 0


def test_cannot_edit_others_post(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")

    post_id = client.post("/api/v1/posts", json={"content": "alice's post"}, headers=alice).json()[
        "id"
    ]

    resp = client.put(f"/api/v1/posts/{post_id}", json={"content": "hijacked"}, headers=bob)
    assert resp.status_code == 403


def test_comments(client: TestClient) -> None:
    headers = register_and_login(client, "dave")
    post_id = client.post("/api/v1/posts", json={"content": "a post"}, headers=headers).json()["id"]

    created = client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "nice post"},
        headers=headers,
    )
    assert created.status_code == 201

    listing = client.get(f"/api/v1/posts/{post_id}/comments")
    assert len(listing.json()) == 1
    assert listing.json()[0]["content"] == "nice post"


def test_follow_and_feed(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")

    bob_id = client.get("/api/v1/auth/me", headers=bob).json()["id"]

    # Bob posts something.
    client.post("/api/v1/posts", json={"content": "bob's update"}, headers=bob)

    # Alice's feed is empty until she follows Bob.
    assert client.get("/api/v1/posts/feed", headers=alice).json() == []

    assert client.post(f"/api/v1/users/{bob_id}/follow", headers=alice).status_code == 204
    feed = client.get("/api/v1/posts/feed", headers=alice).json()
    assert len(feed) == 1
    assert feed[0]["content"] == "bob's update"

    # Bob's profile reflects the new follower.
    profile = client.get(f"/api/v1/users/{bob_id}").json()
    assert profile["followers_count"] == 1
    assert profile["posts_count"] == 1


def test_cannot_follow_self(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    alice_id = client.get("/api/v1/auth/me", headers=alice).json()["id"]
    resp = client.post(f"/api/v1/users/{alice_id}/follow", headers=alice)
    assert resp.status_code == 400
