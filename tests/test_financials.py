from conftest import client


def _create_income(*, income_date: str, income_type: str, amount: str) -> None:
    response = client.post(
        "/api/v1/income",
        json={
            "income_date": income_date,
            "income_type": income_type,
            "amount": amount,
            "payment_mode": "cash",
        },
    )
    assert response.status_code == 201


def _create_expense(*, expense_date: str, expense_type: str, amount: str) -> None:
    response = client.post(
        "/api/v1/expenses",
        json={
            "expense_date": expense_date,
            "expense_type": expense_type,
            "amount": amount,
            "payment_mode": "cash",
        },
    )
    assert response.status_code == 201


def test_financial_summary() -> None:
    _create_income(income_date="2026-05-14", income_type="milk_sale", amount="1200.00")
    _create_income(income_date="2026-05-15", income_type="manure_sale", amount="300.50")
    _create_income(income_date="2026-05-20", income_type="milk_sale", amount="999.00")
    _create_expense(expense_date="2026-05-14", expense_type="feed", amount="700.00")
    _create_expense(expense_date="2026-05-16", expense_type="medicine", amount="150.25")
    _create_expense(expense_date="2026-05-21", expense_type="feed", amount="999.00")

    response = client.get(
        "/api/v1/financials/summary",
        params={"date_from": "2026-05-14", "date_to": "2026-05-16"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "total_income": "1500.50",
        "total_expense": "850.25",
        "profit_or_loss": "650.25",
        "income_count": 2,
        "expense_count": 2,
    }


def test_profit_loss_for_month() -> None:
    _create_income(income_date="2026-05-01", income_type="milk_sale", amount="1000.00")
    _create_income(income_date="2026-05-31", income_type="manure_sale", amount="250.00")
    _create_income(income_date="2026-06-01", income_type="milk_sale", amount="500.00")
    _create_expense(expense_date="2026-05-10", expense_type="feed", amount="400.00")
    _create_expense(expense_date="2026-06-01", expense_type="feed", amount="900.00")

    response = client.get("/api/v1/financials/profit-loss", params={"month": "2026-05"})

    assert response.status_code == 200
    assert response.json()["data"] == {
        "month": "2026-05",
        "total_income": "1250.00",
        "total_expense": "400.00",
        "profit_or_loss": "850.00",
    }


def test_category_summary() -> None:
    _create_income(income_date="2026-05-14", income_type="milk_sale", amount="1200.00")
    _create_income(income_date="2026-05-15", income_type="milk_sale", amount="800.00")
    _create_income(income_date="2026-05-16", income_type="manure_sale", amount="300.00")
    _create_expense(expense_date="2026-05-14", expense_type="feed", amount="700.00")
    _create_expense(expense_date="2026-05-15", expense_type="feed", amount="500.00")
    _create_expense(expense_date="2026-05-16", expense_type="medicine", amount="250.00")

    response = client.get(
        "/api/v1/financials/category-summary",
        params={"date_from": "2026-05-14", "date_to": "2026-05-16"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "income": [
            {"income_type": "manure_sale", "total_amount": "300.00", "count": 1},
            {"income_type": "milk_sale", "total_amount": "2000.00", "count": 2},
        ],
        "expenses": [
            {"expense_type": "feed", "total_amount": "1200.00", "count": 2},
            {"expense_type": "medicine", "total_amount": "250.00", "count": 1},
        ],
    }


def test_financial_date_range_validation() -> None:
    response = client.get(
        "/api/v1/financials/summary",
        params={"date_from": "2026-05-16", "date_to": "2026-05-14"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "date_from must be before or equal to date_to.",
        "data": None,
    }
