import pytest

def test_create_url_success(client, auth_headers):
    response = client.post(
        "/api/urls",
        json={"long_url": "https://www.google.com"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["long_url"] == "https://www.google.com"
    assert len(data["alias"]) == 6 # Alias acak

def test_create_url_custom_alias(client, auth_headers):
    response = client.post(
        "/api/urls",
        json={"long_url": "https://www.youtube.com", "alias": "myyoutube", "alias_mode": "custom"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["data"]["alias"] == "myyoutube"

def test_create_url_conflict(client, auth_headers):
    # Buat pertama kali berhasil
    client.post(
        "/api/urls",
        json={"long_url": "https://www.youtube.com", "alias": "bentrok", "alias_mode": "custom"},
        headers=auth_headers
    )
    # Buat kedua kali harus gagal
    response = client.post(
        "/api/urls",
        json={"long_url": "https://www.facebook.com", "alias": "bentrok", "alias_mode": "custom"},
        headers=auth_headers
    )
    assert response.status_code == 409

def test_get_urls(client, auth_headers):
    client.post("/api/urls", json={"long_url": "https://www.a.com"}, headers=auth_headers)
    client.post("/api/urls", json={"long_url": "https://www.b.com"}, headers=auth_headers)
    
    response = client.get("/api/urls", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 2
    assert data["meta"]["total"] >= 2

def test_update_url(client, auth_headers):
    # Buat URL
    res1 = client.post("/api/urls", json={"long_url": "https://old.com"}, headers=auth_headers)
    url_id = res1.json()["data"]["id"]
    
    # Update title
    res2 = client.patch(f"/api/urls/{url_id}", json={"title": "New Title"}, headers=auth_headers)
    assert res2.status_code == 200
    assert res2.json()["data"]["title"] == "New Title"

def test_delete_url(client, auth_headers):
    # Buat URL
    res1 = client.post("/api/urls", json={"long_url": "https://delete.com"}, headers=auth_headers)
    url_id = res1.json()["data"]["id"]
    
    # Delete
    res2 = client.delete(f"/api/urls/{url_id}", headers=auth_headers)
    assert res2.status_code == 204
    
    # Pastikan sudah hilang
    res3 = client.get(f"/api/urls/{url_id}", headers=auth_headers)
    assert res3.status_code == 404
