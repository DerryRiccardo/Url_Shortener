import pytest

def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Siti Test", "email": "siti@test.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "siti@test.com"
    assert "id" in data["data"]

def test_register_conflict(client, normal_user):
    # normal_user fixture sudah membuat budi@test.com
    response = client.post(
        "/api/auth/register",
        json={"name": "Budi Kembar", "email": "budi@test.com", "password": "password123"}
    )
    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "EMAIL_ALREADY_EXISTS"

def test_login_success(client, normal_user):
    response = client.post(
        "/api/auth/login",
        json={"email": "budi@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

def test_login_invalid(client, normal_user):
    response = client.post(
        "/api/auth/login",
        json={"email": "budi@test.com", "password": "salahpassword"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

def test_get_me(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "budi@test.com"
