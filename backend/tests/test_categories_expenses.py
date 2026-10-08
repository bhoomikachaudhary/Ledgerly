def _signup_and_login(client, email="ada@example.com", password="correct-horse-1", name="Ada"):
    client.post("/v1/auth/signup", json={"email": email, "password": password, "name": name})
    login = client.post("/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_signup_seeds_default_categories(client):
    headers = _signup_and_login(client)
    response = client.get("/v1/categories", headers=headers)
    assert response.status_code == 200
    names = {c["name"] for c in response.json()}
    assert "Food" in names
    assert "Other" in names


def test_create_and_list_expense(client):
    headers = _signup_and_login(client)
    category_id = client.get("/v1/categories", headers=headers).json()[0]["id"]

    create = client.post(
        "/v1/expenses",
        headers=headers,
        json={
            "category_id": category_id,
            "amount": "42.50",
            "spent_on": "2026-09-15",
            "note": "lunch",
        },
    )
    assert create.status_code == 201
    expense_id = create.json()["id"]

    listing = client.get("/v1/expenses", headers=headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == expense_id


def test_create_expense_with_unowned_category_returns_404(client):
    headers_a = _signup_and_login(client, email="a@example.com")
    headers_b = _signup_and_login(client, email="b@example.com")

    other_category_id = client.get("/v1/categories", headers=headers_b).json()[0]["id"]

    response = client.post(
        "/v1/expenses",
        headers=headers_a,
        json={"category_id": other_category_id, "amount": "10.00", "spent_on": "2026-09-15"},
    )
    assert response.status_code == 404


def test_cross_user_cannot_access_others_expense(client):
    headers_a = _signup_and_login(client, email="a@example.com")
    headers_b = _signup_and_login(client, email="b@example.com")

    category_id = client.get("/v1/categories", headers=headers_a).json()[0]["id"]
    created = client.post(
        "/v1/expenses",
        headers=headers_a,
        json={"category_id": category_id, "amount": "10.00", "spent_on": "2026-09-15"},
    )
    expense_id = created.json()["id"]

    # Other user gets 404, never 403 — existence isn't leaked
    get_resp = client.get(f"/v1/expenses/{expense_id}", headers=headers_b)
    assert get_resp.status_code == 404

    patch_resp = client.patch(
        f"/v1/expenses/{expense_id}", headers=headers_b, json={"note": "hacked"}
    )
    assert patch_resp.status_code == 404

    delete_resp = client.delete(f"/v1/expenses/{expense_id}", headers=headers_b)
    assert delete_resp.status_code == 404

    # Owner can still access it fine
    owner_get = client.get(f"/v1/expenses/{expense_id}", headers=headers_a)
    assert owner_get.status_code == 200


def test_expense_filters_and_pagination(client):
    headers = _signup_and_login(client)
    category_id = client.get("/v1/categories", headers=headers).json()[0]["id"]

    for i, amount in enumerate(["10.00", "20.00", "30.00"]):
        client.post(
            "/v1/expenses",
            headers=headers,
            json={
                "category_id": category_id,
                "amount": amount,
                "spent_on": f"2026-09-{10 + i:02d}",
            },
        )

    filtered = client.get("/v1/expenses?min_amount=15", headers=headers)
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 2

    paged = client.get("/v1/expenses?limit=1&offset=1&sort_by=amount&sort_dir=asc", headers=headers)
    assert paged.status_code == 200
    body = paged.json()
    assert body["total"] == 3
    assert len(body["items"]) == 1
    assert body["items"][0]["amount"] == "20.00"


def test_update_and_delete_expense(client):
    headers = _signup_and_login(client)
    category_id = client.get("/v1/categories", headers=headers).json()[0]["id"]
    created = client.post(
        "/v1/expenses",
        headers=headers,
        json={"category_id": category_id, "amount": "10.00", "spent_on": "2026-09-15"},
    )
    expense_id = created.json()["id"]

    patched = client.patch(
        f"/v1/expenses/{expense_id}", headers=headers, json={"amount": "99.99"}
    )
    assert patched.status_code == 200
    assert patched.json()["amount"] == "99.99"

    deleted = client.delete(f"/v1/expenses/{expense_id}", headers=headers)
    assert deleted.status_code == 204

    gone = client.get(f"/v1/expenses/{expense_id}", headers=headers)
    assert gone.status_code == 404
