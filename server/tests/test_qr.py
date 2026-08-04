import pytest

def test_create_qr_success(client, auth_headers, mocker):
    # Membajak fungsi upload ke Cloudflare
    mock_upload = mocker.patch("app.services.qr_service.upload_image_to_r2", return_value="https://fake-r2.com/test.png")
    
    response = client.post(
        "/api/qr-codes",
        json={"long_url": "https://www.example.com", "title": "My QR"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["qr_image"] == "https://fake-r2.com/test.png"
    assert data["title"] == "My QR"
    mock_upload.assert_called_once() # Memastikan fungsi bajakan benar-benar dipanggil

def test_create_qr_validation(client, auth_headers):
    # Coba buat tanpa long_url dan url_id
    response = client.post(
        "/api/qr-codes",
        json={"title": "My QR"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

def test_update_qr_color(client, auth_headers, mocker):
    mocker.patch("app.services.qr_service.upload_image_to_r2", return_value="https://fake-r2.com/test1.png")
    
    res1 = client.post(
        "/api/qr-codes",
        json={"long_url": "https://www.example.com", "qr_color": "#000000"},
        headers=auth_headers
    )
    qr_id = res1.json()["data"]["id"]
    
    # Update warna
    mock_upload_2 = mocker.patch("app.services.qr_service.upload_image_to_r2", return_value="https://fake-r2.com/test2.png")
    res2 = client.patch(
        f"/api/qr-codes/{qr_id}",
        json={"qr_color": "#FF0000"},
        headers=auth_headers
    )
    
    assert res2.status_code == 200
    assert res2.json()["data"]["qr_color"] == "#FF0000"
    assert res2.json()["data"]["qr_image"] == "https://fake-r2.com/test2.png"
    mock_upload_2.assert_called_once()

def test_delete_qr(client, auth_headers, mocker):
    mocker.patch("app.services.qr_service.upload_image_to_r2", return_value="test.png")
    res1 = client.post("/api/qr-codes", json={"long_url": "https://test.com"}, headers=auth_headers)
    qr_id = res1.json()["data"]["id"]
    
    res2 = client.delete(f"/api/qr-codes/{qr_id}", headers=auth_headers)
    assert res2.status_code == 204
