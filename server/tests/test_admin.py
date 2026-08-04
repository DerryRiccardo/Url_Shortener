import pytest

def test_admin_forbidden(client, auth_headers):
    # auth_headers adalah milik normal_user (Budi)
    response = client.get("/api/admin/summary", headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"

def test_admin_summary_success(client, admin_headers):
    # admin_headers adalah milik admin_user
    response = client.get("/api/admin/summary", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "total_users" in data
    assert "total_urls" in data

def test_admin_get_users(client, admin_headers, normal_user):
    # Seharusnya ada 2 user (admin_user dan normal_user)
    response = client.get("/api/admin/users", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 2
    assert data["meta"]["total"] >= 2
