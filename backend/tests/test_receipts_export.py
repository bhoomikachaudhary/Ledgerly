import io


def _signup_and_login(client, email="ada@example.com", password="correct-horse-1", name="Ada"):
    client.post("/v1/auth/signup", json={"email": email, "password": password, "name": name})
    login = client.post("/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_expense(client, headers):
    category_id = client.get("/v1/categories", headers=headers).json()[0]["id"]
    created = client.post(
        "/v1/expenses",
        headers=headers,
        json={"category_id": category_id, "amount": "10.00", "spent_on": "2026-09-15"},
    )
    return created.json()["id"]


def test_receipt_upload_accepts_valid_image(client, tmp_path, monkeypatch):
    from app.services import storage_service

    monkeypatch.setattr(storage_service.settings, "upload_dir", str(tmp_path))

    headers = _signup_and_login(client)
    expense_id = _create_expense(client, headers)

    fake_image = io.BytesIO(b"\xff\xd8\xff\xe0fakejpegdata")
    response = client.post(
        f"/v1/expenses/{expense_id}/receipt",
        headers=headers,
        files={"file": ("receipt.jpg", fake_image, "image/jpeg")},
    )
    assert response.status_code == 200
    assert response.json()["receipt_key"] is not None


def test_receipt_upload_rejects_bad_content_type(client, tmp_path, monkeypatch):
    from app.services import storage_service

    monkeypatch.setattr(storage_service.settings, "upload_dir", str(tmp_path))

    headers = _signup_and_login(client)
    expense_id = _create_expense(client, headers)

    bad_file = io.BytesIO(b"not an image")
    response = client.post(
        f"/v1/expenses/{expense_id}/receipt",
        headers=headers,
        files={"file": ("virus.exe", bad_file, "application/x-msdownload")},
    )
    assert response.status_code == 415


def test_receipt_upload_404_for_unowned_expense(client, tmp_path, monkeypatch):
    from app.services import storage_service

    monkeypatch.setattr(storage_service.settings, "upload_dir", str(tmp_path))

    headers_a = _signup_and_login(client, email="a@example.com")
    headers_b = _signup_and_login(client, email="b@example.com")
    expense_id = _create_expense(client, headers_a)

    fake_image = io.BytesIO(b"\xff\xd8\xff\xe0fakejpegdata")
    response = client.post(
        f"/v1/expenses/{expense_id}/receipt",
        headers=headers_b,
        files={"file": ("receipt.jpg", fake_image, "image/jpeg")},
    )
    assert response.status_code == 404


def test_export_returns_csv(client):
    headers = _signup_and_login(client)
    _create_expense(client, headers)

    response = client.get("/v1/expenses/export", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "date,amount,category,note" in response.text


def test_export_shows_category_name_not_uuid(client):
    """Regression test: the export used to write the raw category UUID instead of
    its name, which rendered as garbled text when opened in Excel."""
    headers = _signup_and_login(client)
    categories = client.get("/v1/categories", headers=headers).json()
    food = next(c for c in categories if c["name"] == "Food")
    client.post(
        "/v1/expenses",
        headers=headers,
        json={"category_id": food["id"], "amount": "10.00", "spent_on": "2026-09-15"},
    )

    response = client.get("/v1/expenses/export", headers=headers)
    assert "Food" in response.text
    assert food["id"] not in response.text