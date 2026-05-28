from conftest import client


def test_create_and_get_animal() -> None:
    payload = {
        "animal_code": "ANM-001",
        "tag_number": "TAG-001",
        "name": "Gauri",
        "animal_type": "cow",
        "breed": "Holstein Friesian",
        "gender": "female",
        "current_status": "milking",
    }

    create_response = client.post("/api/v1/animals", json=payload)

    assert create_response.status_code == 201
    assert create_response.json()["success"] is True
    animal_id = create_response.json()["data"]["id"]

    get_response = client.get(f"/api/v1/animals/{animal_id}")

    assert get_response.status_code == 200
    assert get_response.json()["data"]["animal_code"] == "ANM-001"


def test_unique_animal_code_and_tag_number_validation() -> None:
    payload = {
        "animal_code": "ANM-001",
        "tag_number": "TAG-001",
        "animal_type": "cow",
        "gender": "female",
        "current_status": "milking",
    }

    assert client.post("/api/v1/animals", json=payload).status_code == 201

    duplicate_code = dict(payload)
    duplicate_code["tag_number"] = "TAG-002"
    duplicate_code_response = client.post("/api/v1/animals", json=duplicate_code)

    assert duplicate_code_response.status_code == 409
    assert duplicate_code_response.json()["message"] == "Animal code already exists."

    duplicate_tag = dict(payload)
    duplicate_tag["animal_code"] = "ANM-002"
    duplicate_tag_response = client.post("/api/v1/animals", json=duplicate_tag)

    assert duplicate_tag_response.status_code == 409
    assert duplicate_tag_response.json()["message"] == "Tag number already exists."


def test_list_animals_with_filters_and_soft_delete() -> None:
    client.post(
        "/api/v1/animals",
        json={
            "animal_code": "ANM-001",
            "name": "Gauri",
            "animal_type": "cow",
            "breed": "Holstein Friesian",
            "gender": "female",
            "current_status": "milking",
        },
    )
    second_response = client.post(
        "/api/v1/animals",
        json={
            "animal_code": "ANM-002",
            "name": "Kali",
            "animal_type": "buffalo",
            "breed": "Murrah",
            "gender": "female",
            "current_status": "pregnant",
        },
    )
    second_id = second_response.json()["data"]["id"]

    filtered_response = client.get("/api/v1/animals", params={"search": "Kali", "animal_type": "buffalo"})

    assert filtered_response.status_code == 200
    assert filtered_response.json()["data"]["pagination"]["total"] == 1
    assert filtered_response.json()["data"]["items"][0]["animal_code"] == "ANM-002"

    delete_response = client.delete(f"/api/v1/animals/{second_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["is_active"] is False

    post_delete_list = client.get("/api/v1/animals")
    assert post_delete_list.json()["data"]["pagination"]["total"] == 1

    post_delete_get = client.get(f"/api/v1/animals/{second_id}")
    assert post_delete_get.status_code == 404


def test_update_animal() -> None:
    create_response = client.post(
        "/api/v1/animals",
        json={
            "animal_code": "ANM-001",
            "animal_type": "heifer",
            "gender": "female",
            "current_status": "heifer",
        },
    )
    animal_id = create_response.json()["data"]["id"]

    update_response = client.put(
        f"/api/v1/animals/{animal_id}",
        json={"current_status": "pregnant", "notes": "Confirmed by vet."},
    )

    assert update_response.status_code == 200
    assert update_response.json()["data"]["current_status"] == "pregnant"
    assert update_response.json()["data"]["notes"] == "Confirmed by vet."
