import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def sample_csv(months=24):
    rows = ["date,sales"]
    for i in range(months):
        year = 2024 + (i // 12)
        month = i % 12 + 1
        value = 100 + i * 5 + (month % 4) * 7
        rows.append(f"{year}-{month:02d}-01,{value}")
    return "\n".join(rows).encode()


def upload_csv(content=None, filename="sales.csv"):
    return {"file": (filename, content if content is not None else sample_csv(), "text/csv")}


def forecast_data(periods="3", date_column="date", sales_column="sales"):
    return {"date_column": date_column, "sales_column": sales_column, "periods": periods}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_homepage_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Sales" in response.text


def test_inspect_csv():
    response = client.post("/api/inspect", files=upload_csv())
    assert response.status_code == 200
    assert response.json()["suggested_date_column"] == "date"
    assert response.json()["suggested_sales_column"] == "sales"


def test_inspect_reports_row_count():
    response = client.post("/api/inspect", files=upload_csv(sample_csv(12)))
    assert response.status_code == 200
    assert response.json()["rows"] == 12


def test_inspect_reports_column_names():
    response = client.post("/api/inspect", files=upload_csv())
    assert response.json()["columns"] == ["date", "sales"]


def test_forecast_csv():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data())
    assert response.status_code == 200
    result = response.json()
    assert len(result["forecast"]) == 3
    assert "mae" in result["metrics"]


def test_forecast_contains_model_name():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data())
    assert "Linear Regression" in response.json()["model"]


def test_forecast_contains_history():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data())
    assert len(response.json()["history"]) == 24


def test_forecast_metrics_are_nonnegative():
    metrics = client.post("/api/forecast", files=upload_csv(), data=forecast_data()).json()["metrics"]
    assert metrics["mae"] >= 0
    assert metrics["rmse"] >= 0


def test_forecast_dates_are_month_strings():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data())
    assert all(len(row["month"]) == 7 for row in response.json()["forecast"])


def test_forecast_predictions_are_nonnegative():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data())
    assert all(row["predicted_sales"] >= 0 for row in response.json()["forecast"])


def test_forecast_one_month():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data(periods="1"))
    assert response.status_code == 200
    assert len(response.json()["forecast"]) == 1


def test_forecast_maximum_24_months():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data(periods="24"))
    assert response.status_code == 200
    assert len(response.json()["forecast"]) == 24


def test_reject_non_csv():
    response = client.post("/api/inspect", files=upload_csv(b"not csv", "sales.txt"))
    assert response.status_code == 400


def test_reject_empty_csv_upload():
    response = client.post("/api/inspect", files=upload_csv(b"", "sales.csv"))
    assert response.status_code == 400


def test_reject_csv_with_one_column():
    response = client.post("/api/inspect", files=upload_csv(b"date\n2024-01-01\n"))
    assert response.status_code == 422


def test_reject_forecast_zero_periods():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data(periods="0"))
    assert response.status_code == 422


def test_reject_forecast_over_24_periods():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data(periods="25"))
    assert response.status_code == 422


def test_reject_missing_date_column():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data(date_column="missing"))
    assert response.status_code == 422


def test_reject_missing_sales_column():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data(sales_column="missing"))
    assert response.status_code == 422


def test_reject_same_date_and_sales_column():
    response = client.post("/api/forecast", files=upload_csv(), data=forecast_data(sales_column="date"))
    assert response.status_code == 422


def test_reject_insufficient_rows():
    response = client.post("/api/forecast", files=upload_csv(b"date,sales\n2024-01-01,10\n2024-02-01,20\n"))
    assert response.status_code == 422


def test_reject_invalid_date_and_sales_values():
    content = b"date,sales\nnot-a-date,nope\ninvalid,also-nope\nbad,unknown\n"
    response = client.post("/api/forecast", files=upload_csv(content))
    assert response.status_code == 422
