from conftest import client


def _create_animal(*, animal_code: str, current_status: str = "milking") -> int:
    response = client.post(
        "/api/v1/animals",
        json={
            "animal_code": animal_code,
            "animal_type": "cow",
            "gender": "female",
            "current_status": current_status,
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_create_get_update_and_delete_milk_entry() -> None:
    animal_id = _create_animal(animal_code="ANM-100")

    create_response = client.post(
        "/api/v1/milk-entries",
        json={
            "animal_id": animal_id,
            "entry_date": "2026-05-14",
            "shift": "morning",
            "quantity_liters": "12.50",
            "fat_percentage": "4.20",
            "snf_percentage": "8.60",
            "recorded_by": "Ramesh",
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["data"]["quantity_liters"] == "12.50"
    milk_entry_id = create_response.json()["data"]["id"]

    get_response = client.get(f"/api/v1/milk-entries/{milk_entry_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["shift"] == "morning"

    update_response = client.put(
        f"/api/v1/milk-entries/{milk_entry_id}",
        json={
            "shift": "evening",
            "quantity_liters": "13.25",
            "milk_quality_notes": "Good quality.",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["quantity_liters"] == "13.25"
    assert update_response.json()["data"]["shift"] == "evening"

    list_response = client.get("/api/v1/milk-entries", params={"animal_id": animal_id})
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 1

    delete_response = client.delete(f"/api/v1/milk-entries/{milk_entry_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["id"] == milk_entry_id

    missing_response = client.get(f"/api/v1/milk-entries/{milk_entry_id}")
    assert missing_response.status_code == 404


def test_milk_entry_business_rules() -> None:
    milking_animal_id = _create_animal(animal_code="ANM-101", current_status="milking")
    dry_animal_id = _create_animal(animal_code="ANM-102", current_status="dry")

    first_response = client.post(
        "/api/v1/milk-entries",
        json={
            "animal_id": milking_animal_id,
            "entry_date": "2026-05-14",
            "shift": "morning",
            "quantity_liters": "8.00",
        },
    )
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/milk-entries",
        json={
            "animal_id": milking_animal_id,
            "entry_date": "2026-05-14",
            "shift": "morning",
            "quantity_liters": "8.50",
        },
    )
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["message"] == "Milk entry already exists for this animal, date, and shift."

    non_milking_response = client.post(
        "/api/v1/milk-entries",
        json={
            "animal_id": dry_animal_id,
            "entry_date": "2026-05-14",
            "shift": "morning",
            "quantity_liters": "6.50",
        },
    )
    assert non_milking_response.status_code == 400
    assert non_milking_response.json()["message"] == "Milk entry is allowed only for animals with current_status 'milking'."

    invalid_quantity_response = client.post(
        "/api/v1/milk-entries",
        json={
            "animal_id": milking_animal_id,
            "entry_date": "2026-05-15",
            "shift": "morning",
            "quantity_liters": "-1.00",
        },
    )
    assert invalid_quantity_response.status_code == 422


def test_milk_entry_summary_endpoints() -> None:
    animal_id = _create_animal(animal_code="ANM-103")

    entries = [
        {"entry_date": "2026-05-14", "shift": "morning", "quantity_liters": "10.50"},
        {"entry_date": "2026-05-14", "shift": "evening", "quantity_liters": "11.00"},
        {"entry_date": "2026-05-15", "shift": "morning", "quantity_liters": "9.50"},
    ]
    for entry in entries:
        response = client.post("/api/v1/milk-entries", json={"animal_id": animal_id, **entry})
        assert response.status_code == 201

    daily_response = client.get("/api/v1/milk-entries/daily-summary", params={"entry_date": "2026-05-14"})
    assert daily_response.status_code == 200
    assert daily_response.json()["data"]["total_quantity_liters"] == "21.50"

    monthly_response = client.get("/api/v1/milk-entries/monthly-summary", params={"year": 2026, "month": 5})
    assert monthly_response.status_code == 200
    assert monthly_response.json()["data"]["items"] == [
        {"entry_date": "2026-05-14", "total_quantity_liters": "21.50"},
        {"entry_date": "2026-05-15", "total_quantity_liters": "9.50"},
    ]

    animal_summary_response = client.get(f"/api/v1/milk-entries/animal/{animal_id}/summary")
    assert animal_summary_response.status_code == 200
    assert animal_summary_response.json()["data"] == {
        "animal_id": animal_id,
        "total_quantity_liters": "31.00",
        "average_quantity_liters": "10.33",
        "entry_count": 3,
    }
