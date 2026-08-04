import pytest

def test_redirect_success(client, auth_headers):
    # Buat URL
    client.post(
        "/api/urls",
        json={"long_url": "https://www.google.com", "alias": "gugelll", "alias_mode": "custom"},
        headers=auth_headers
    )
    
    # Kita set follow_redirects=False agar testclient tidak otomatis mengikuti link tujuan
    # Kita hanya ingin memastikan status 302 dikirim
    response = client.get("/gugelll", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://www.google.com"

def test_redirect_not_found(client):
    response = client.get("/tidakada", follow_redirects=False)
    assert response.status_code == 404
