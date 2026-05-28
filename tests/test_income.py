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


def _create_milk_entry(*, animal_id: int, entry_date: str = "2026-05-14", shift: str = "morning") -> int:
    response = client.post(
        "/api/v1/milk-entries",
        json={
            "animal_id": animal_id,
            "entry_date": entry_date,
            "shift": shift,
            "quantity_liters": "10.00",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_create_get_update_and_delete_income_entry() -> None:
    animal_id = _create_animal(animal_code="ANM-200")
    milk_entry_id = _create_milk_entry(animal_id=animal_id)

    create_response = client.post(
        "/api/v1/income",
        json={
            "income_date": "2026-05-14",
            "income_type": "milk_sale",
            "amount": "1250.00",
            "payment_mode": "upi",
            "reference_number": "TXN-1",
            "animal_id": animal_id,
            "milk_entry_id": milk_entry_id,
        },
    )
    assert create_response.status_code == 201
    income_id = create_response.json()["data"]["id"]

    get_response = client.get(f"/api/v1/income/{income_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["amount"] == "1250.00"

    update_response = client.put(
        f"/api/v1/income/{income_id}",
        json={
            "amount": "1500.00",
            "payment_mode": "bank_transfer",
            "description": "Settlement received.",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["amount"] == "1500.00"
    assert update_response.json()["data"]["payment_mode"] == "bank_transfer"

    delete_response = client.delete(f"/api/v1/income/{income_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["id"] == income_id

    missing_response = client.get(f"/api/v1/income/{income_id}")
    assert missing_response.status_code == 404


def test_income_validations() -> None:
    animal_id = _create_animal(animal_code="ANM-201")
    milk_entry_id = _create_milk_entry(animal_id=animal_id)

    invalid_animal_response = client.post(
        "/api/v1/income",
        json={
            "income_date": "2026-05-14",
            "income_type": "milk_sale",
            "amount": "1000.00",
            "payment_mode": "cash",
            "animal_id": 999,
        },
    )
    assert invalid_animal_response.status_code == 400
    assert invalid_animal_response.json()["message"] == "Animal not found."

    invalid_milk_entry_response = client.post(
        "/api/v1/income",
        json={
            "income_date": "2026-05-14",
            "income_type": "milk_sale",
            "amount": "1000.00",
            "payment_mode": "cash",
            "milk_entry_id": 999,
        },
    )
    assert invalid_milk_entry_response.status_code == 400
    assert invalid_milk_entry_response.json()["message"] == "Milk entry not found."

    invalid_amount_response = client.post(
        "/api/v1/income",
        json={
            "income_date": "2026-05-14",
            "income_type": "milk_sale",
            "amount": "0.00",
            "payment_mode": "cash",
            "animal_id": animal_id,
            "milk_entry_id": milk_entry_id,
        },
    )
    assert invalid_amount_response.status_code == 422


def test_list_income_entries_with_filters_and_total_income_amount() -> None:
    animal_id = _create_animal(animal_code="ANM-202")
    milk_entry_id = _create_milk_entry(animal_id=animal_id)

    payloads = [
        {
            "income_date": "2026-05-14",
            "income_type": "milk_sale",
            "amount": "1200.00",
            "payment_mode": "upi",
            "animal_id": animal_id,
            "milk_entry_id": milk_entry_id,
        },
        {
            "income_date": "2026-05-15",
            "income_type": "manure_sale",
            "amount": "300.00",
            "payment_mode": "cash",
        },
        {
            "income_date": "2026-05-16",
            "income_type": "milk_sale",
            "amount": "900.00",
            "payment_mode": "upi",
        },
    ]

    for payload in payloads:
        response = client.post("/api/v1/income", json=payload)
        assert response.status_code == 201

    list_response = client.get(
        "/api/v1/income",
        params={
            "page": 1,
            "limit": 10,
            "income_type": "milk_sale",
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
        "total_income_amount": "2100.00",
    }


def test_income_date_range_validation() -> None:
    response = client.get(
        "/api/v1/income",
        params={"date_from": "2026-05-16", "date_to": "2026-05-14"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "date_from must be before or equal to date_to.",
        "data": None,
    }
