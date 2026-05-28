from datetime import date

from conftest import client

import app.api.v1.endpoints.dashboard as dashboard_endpoint


class FixedDate(date):
    @classmethod
    def today(cls) -> date:
        return cls(2026, 5, 14)


def _create_animal(*, animal_code: str, current_status: str = "milking", animal_type: str = "cow") -> int:
    response = client.post(
        "/api/v1/animals",
        json={
            "animal_code": animal_code,
            "animal_type": animal_type,
            "gender": "female",
            "current_status": current_status,
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def _create_milk_entry(*, animal_id: int, entry_date: str, shift: str, quantity_liters: str) -> None:
    response = client.post(
        "/api/v1/milk-entries",
        json={
            "animal_id": animal_id,
            "entry_date": entry_date,
            "shift": shift,
            "quantity_liters": quantity_liters,
        },
    )
    assert response.status_code == 201


def _create_income(*, income_date: str, amount: str) -> None:
    response = client.post(
        "/api/v1/income",
        json={
            "income_date": income_date,
            "income_type": "milk_sale",
            "amount": amount,
            "payment_mode": "cash",
        },
    )
    assert response.status_code == 201


def _create_expense(*, expense_date: str, amount: str) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "expense_date": expense_date,
            "expense_type": "feed",
            "amount": amount,
            "payment_mode": "cash",
        },
    )
    assert response.status_code == 201


def _create_event(*, animal_id: int, event_type: str, next_due_date: str, title: str = "Follow up") -> None:
    response = client.post(
        f"/api/v1/animals/{animal_id}/events",
        json={
            "event_type": event_type,
            "event_date": "2026-05-01",
            "title": title,
            "next_due_date": next_due_date,
        },
    )
    assert response.status_code == 201


def test_dashboard_summary(monkeypatch) -> None:
    monkeypatch.setattr(dashboard_endpoint, "date", FixedDate)
    milking_id = _create_animal(animal_code="ANM-D001", current_status="milking")
    _create_animal(animal_code="ANM-D002", current_status="pregnant")
    _create_animal(animal_code="ANM-D003", current_status="dry")
    _create_animal(animal_code="ANM-D004", current_status="calf", animal_type="calf")
    _create_animal(animal_code="ANM-D005", current_status="sick")
    _create_milk_entry(animal_id=milking_id, entry_date="2026-05-14", shift="morning", quantity_liters="12.50")
    _create_milk_entry(animal_id=milking_id, entry_date="2026-05-15", shift="morning", quantity_liters="10.00")
    _create_income(income_date="2026-05-02", amount="1000.00")
    _create_expense(expense_date="2026-05-03", amount="400.00")

    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    assert response.json()["data"] == {
        "total_animals": 5,
        "milking_animals": 1,
        "pregnant_animals": 1,
        "dry_animals": 1,
        "calves": 1,
        "sick_animals": 1,
        "today_total_milk": "12.50",
        "monthly_total_milk": "22.50",
        "monthly_income": "1000.00",
        "monthly_expense": "400.00",
        "monthly_profit_or_loss": "600.00",
    }


def test_dashboard_milk_trend_and_financial_summary() -> None:
    animal_id = _create_animal(animal_code="ANM-D006", current_status="milking")
    _create_milk_entry(animal_id=animal_id, entry_date="2026-05-10", shift="morning", quantity_liters="8.00")
    _create_milk_entry(animal_id=animal_id, entry_date="2026-05-10", shift="evening", quantity_liters="7.50")
    _create_milk_entry(animal_id=animal_id, entry_date="2026-05-11", shift="morning", quantity_liters="9.00")
    _create_income(income_date="2026-05-10", amount="700.00")
    _create_expense(expense_date="2026-05-11", amount="125.50")

    trend_response = client.get(
        "/api/v1/dashboard/milk-trend",
        params={"date_from": "2026-05-10", "date_to": "2026-05-11"},
    )
    assert trend_response.status_code == 200
    assert trend_response.json()["data"] == [
        {"date": "2026-05-10", "total_quantity_liters": "15.50"},
        {"date": "2026-05-11", "total_quantity_liters": "9.00"},
    ]

    financial_response = client.get(
        "/api/v1/dashboard/financial-summary",
        params={"date_from": "2026-05-10", "date_to": "2026-05-11"},
    )
    assert financial_response.status_code == 200
    assert financial_response.json()["data"] == {
        "total_income": "700.00",
        "total_expense": "125.50",
        "profit_or_loss": "574.50",
    }


def test_dashboard_upcoming_events_and_alerts(monkeypatch) -> None:
    monkeypatch.setattr(dashboard_endpoint, "date", FixedDate)
    milked_animal_id = _create_animal(animal_code="ANM-D007", current_status="milking")
    missing_milk_animal_id = _create_animal(animal_code="ANM-D008", current_status="milking")
    sick_animal_id = _create_animal(animal_code="ANM-D009", current_status="sick")
    _create_milk_entry(
        animal_id=milked_animal_id,
        entry_date="2026-05-14",
        shift="morning",
        quantity_liters="11.00",
    )
    _create_event(animal_id=milked_animal_id, event_type="vaccination", next_due_date="2026-05-20")
    _create_event(animal_id=missing_milk_animal_id, event_type="deworming", next_due_date="2026-05-21")
    _create_event(animal_id=sick_animal_id, event_type="vaccination", next_due_date="2026-07-01")

    events_response = client.get("/api/v1/dashboard/upcoming-events")
    assert events_response.status_code == 200
    assert [item["next_due_date"] for item in events_response.json()["data"]] == ["2026-05-20", "2026-05-21"]

    alerts_response = client.get("/api/v1/dashboard/alerts")
    assert alerts_response.status_code == 200
    alerts = alerts_response.json()["data"]
    assert [animal["id"] for animal in alerts["sick_animals"]] == [sick_animal_id]
    assert [event["next_due_date"] for event in alerts["upcoming_vaccinations"]] == ["2026-05-20"]
    assert [event["next_due_date"] for event in alerts["upcoming_deworming"]] == ["2026-05-21"]
    assert [animal["id"] for animal in alerts["milking_animals_without_milk_entry_today"]] == [missing_milk_animal_id]


def test_dashboard_date_range_validation() -> None:
    response = client.get(
        "/api/v1/dashboard/milk-trend",
        params={"date_from": "2026-05-16", "date_to": "2026-05-14"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "date_from must be before or equal to date_to.",
        "data": None,
    }
