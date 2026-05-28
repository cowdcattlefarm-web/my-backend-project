from conftest import client

from app.core.auth import get_current_user
from app.main import app


def test_write_api_requires_bearer_token() -> None:
    original_override = app.dependency_overrides.pop(get_current_user, None)
    try:
        response = client.post(
            "/api/v1/animals",
            json={
                "animal_code": "ANM-AUTH-001",
                "animal_type": "cow",
                "gender": "female",
                "current_status": "milking",
            },
        )
    finally:
        if original_override is not None:
            app.dependency_overrides[get_current_user] = original_override

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token."


def test_get_api_remains_public() -> None:
    original_override = app.dependency_overrides.pop(get_current_user, None)
    try:
        response = client.get("/api/v1/animals")
    finally:
        if original_override is not None:
            app.dependency_overrides[get_current_user] = original_override

    assert response.status_code == 200
