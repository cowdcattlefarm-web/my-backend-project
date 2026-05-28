from conftest import client


def test_health_check() -> None:
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["api"] == "ok"
