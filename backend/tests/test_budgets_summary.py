def _signup_and_login(client, email="ada@example.com", password="correct-horse-1", name="Ada"):
    client.post("/v1/auth/signup", json={"email": email, "password": password, "name": name})
    login = client.post("/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upsert_budget_is_idempotent_per_month(client):
    headers = _signup_and_login(client)
    category_id = client.get("/v1/categories", headers=headers).json()[0]["id"]

    first = client.put(
        "/v1/budgets",
        headers=headers,
        json={"category_id": category_id, "month": "2026-09", "limit_amount": "5000.00"},
    )
    assert first.status_code == 200
    assert first.json()["limit_amount"] == "5000.00"

    second = client.put(
        "/v1/budgets",
        headers=headers,
        json={"category_id": category_id, "month": "2026-09", "limit_amount": "6000.00"},
    )
    assert second.status_code == 200
    assert second.json()["limit_amount"] == "6000.00"

    listing = client.get("/v1/budgets?month=2026-09", headers=headers)
    assert len(listing.json()) == 1


def test_summary_matches_hand_calculated_fixture(client):
    """Done-when criterion from the project plan: summary JSON matches a hand-calculated fixture."""
    headers = _signup_and_login(client)
    categories = client.get("/v1/categories", headers=headers).json()
    food_id = next(c["id"] for c in categories if c["name"] == "Food")
    travel_id = next(c["id"] for c in categories if c["name"] == "Travel")

    # Hand-calculated expectation:
    # Food: 12.50 + 7.50 = 20.00 spent, budget 100.00
    # Travel: 300.00 spent, no budget set
    # total_spent = 320.00, total_budget = 100.00
    client.post(
        "/v1/expenses",
        headers=headers,
        json={"category_id": food_id, "amount": "12.50", "spent_on": "2026-09-05"},
    )
    client.post(
        "/v1/expenses",
        headers=headers,
        json={"category_id": food_id, "amount": "7.50", "spent_on": "2026-09-20"},
    )
    client.post(
        "/v1/expenses",
        headers=headers,
        json={"category_id": travel_id, "amount": "300.00", "spent_on": "2026-09-10"},
    )
    # Outside the month — must not be counted
    client.post(
        "/v1/expenses",
        headers=headers,
        json={"category_id": food_id, "amount": "999.00", "spent_on": "2026-08-15"},
    )
    client.put(
        "/v1/budgets",
        headers=headers,
        json={"category_id": food_id, "month": "2026-09", "limit_amount": "100.00"},
    )

    response = client.get("/v1/summary?month=2026-09", headers=headers)
    assert response.status_code == 200
    body = response.json()

    assert body["total_spent"] == "320.00"
    assert body["total_budget"] == "100.00"

    by_id = {c["category_id"]: c for c in body["categories"]}
    assert by_id[food_id]["spent"] == "20.00"
    assert by_id[food_id]["budget"] == "100.00"
    assert by_id[travel_id]["spent"] == "300.00"
    assert by_id[travel_id]["budget"] is None


def test_trend_returns_six_months(client):
    headers = _signup_and_login(client)
    response = client.get("/v1/summary/trend", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["months"]) == 6
