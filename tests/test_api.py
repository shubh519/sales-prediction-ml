import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def sample_csv():
    rows = ["date,sales"]
    for i in range(24):
        year = 2024 + (i // 12)
        month = i % 12 + 1
        value = 100 + i * 5 + (month % 4) * 7
        rows.append(f"{year}-{month:02d}-01,{value}")
    return "\n".join(rows).encode()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_inspect_csv():
    response = client.post("/api/inspect", files={"file": ("sales.csv", sample_csv(), "text/csv")})
    assert response.status_code == 200
    assert response.json()["suggested_date_column"] == "date"
    assert response.json()["suggested_sales_column"] == "sales"

def test_forecast_csv():
    response = client.post(
        "/api/forecast",
        files={"file": ("sales.csv", sample_csv(), "text/csv")},
        data={"date_column": "date", "sales_column": "sales", "periods": "3"},
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["forecast"]) == 3
    assert "mae" in result["metrics"]

def test_reject_non_csv():
    response = client.post("/api/inspect", files={"file": ("sales.txt", b"not csv", "text/plain")})
    assert response.status_code == 400
