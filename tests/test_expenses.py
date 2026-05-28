from conftest import client


def _create_animal(*, animal_code: str) -> int:
    response = client.post(
        "/api/v1/animals",
        json={
            "animal_code": animal_code,
            "animal_type": "cow",
            "gender": "female",
            "current_status": "milking",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def _create_animal_event(*, animal_id: int) -> int:
    response = client.post(
        f"/api/v1/animals/{animal_id}/events",
        json={
            "event_type": "treatment",
            "event_date": "2026-05-14",
            "title": "Basic treatment",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_create_get_update_and_delete_expense_entry() -> None:
    animal_id = _create_animal(animal_code="ANM-300")
    animal_event_id = _create_animal_event(animal_id=animal_id)

    create_response = client.post(
        "/api/v1/expenses",
        json={
            "expense_date": "2026-05-14",
            "expense_type": "feed",
            "amount": "1250.00",
            "payment_mode": "upi",
            "vendor_name": "Local Feed Supplier",
            "animal_id": animal_id,
            "animal_event_id": animal_event_id,
        },
    )
    assert create_response.status_code == 201
    expense_id = create_response.json()["data"]["id"]

    get_response = client.get(f"/api/v1/expenses/{expense_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["amount"] == "1250.00"

    update_response = client.put(
        f"/api/v1/expenses/{expense_id}",
        json={
            "amount": "1500.00",
            "payment_mode": "bank_transfer",
            "description": "Updated expense details.",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["amount"] == "1500.00"
    assert update_response.json()["data"]["payment_mode"] == "bank_transfer"

    delete_response = client.delete(f"/api/v1/expenses/{expense_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["id"] == expense_id

    missing_response = client.get(f"/api/v1/expenses/{expense_id}")
    assert missing_response.status_code == 404


def test_expense_validations() -> None:
    animal_id = _create_animal(animal_code="ANM-301")
    animal_event_id = _create_animal_event(animal_id=animal_id)

    invalid_animal_response = client.post(
        "/api/v1/expenses",
        json={
            "expense_date": "2026-05-14",
            "expense_type": "feed",
            "amount": "1000.00",
            "payment_mode": "cash",
            "animal_id": 999,
        },
    )
    assert invalid_animal_response.status_code == 400
    assert invalid_animal_response.json()["message"] == "Animal not found."

    invalid_animal_event_response = client.post(
        "/api/v1/expenses",
        json={
            "expense_date": "2026-05-14",
            "expense_type": "medicine",
            "amount": "1000.00",
            "payment_mode": "cash",
            "animal_event_id": 999,
        },
    )
    assert invalid_animal_event_response.status_code == 400
    assert invalid_animal_event_response.json()["message"] == "Animal event not found."

    invalid_amount_response = client.post(
        "/api/v1/expenses",
        json={
            "expense_date": "2026-05-14",
            "expense_type": "feed",
            "amount": "0.00",
            "payment_mode": "cash",
            "animal_id": animal_id,
            "animal_event_id": animal_event_id,
        },
    )
    assert invalid_amount_response.status_code == 422


def test_list_expense_entries_with_filters_and_total_expense_amount() -> None:
    animal_id = _create_animal(animal_code="ANM-302")
    animal_event_id = _create_animal_event(animal_id=animal_id)

    payloads = [
        {
            "expense_date": "2026-05-14",
            "expense_type": "feed",
            "amount": "1200.00",
            "payment_mode": "upi",
            "animal_id": animal_id,
            "animal_event_id": animal_event_id,
        },
        {
            "expense_date": "2026-05-15",
            "expense_type": "electricity",
            "amount": "300.00",
            "payment_mode": "cash",
        },
        {
            "expense_date": "2026-05-16",
            "expense_type": "feed",
            "amount": "900.00",
            "payment_mode": "upi",
        },
    ]

    for payload in payloads:
        response = client.post("/api/v1/expenses", json=payload)
        assert response.status_code == 201

    list_response = client.get(
        "/api/v1/expenses",
        params={
            "page": 1,
            "limit": 10,
            "expense_type": "feed",
            "payment_mode": "upi",
            "date_from": "2026-05-14",
            "date_to": "2026-05-16",
        },
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]["items"]) == 2
    assert list_response.json()["data"]["metadata"] == {
        "page": 1,
        "limit": 10,
        "total": 2,
        "total_expense_amount": "2100.00",
    }


def test_expense_date_range_validation() -> None:
    response = client.get(
        "/api/v1/expenses",
        params={"date_from": "2026-05-16", "date_to": "2026-05-14"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "date_from must be before or equal to date_to.",
        "data": None,
    }
