from pathlib import Path
from typing import Optional
import io
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.forecasting import inspect_csv, create_forecast

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

app = FastAPI(
    title="Sales Prediction Using Machine Learning",
    description="Upload historical sales data, evaluate a forecasting model, and forecast future monthly sales.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["GET", "POST"], allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    index = FRONTEND / "index.html"
    return index.read_text(encoding="utf-8")


async def read_csv_upload(file: UploadFile) -> pd.DataFrame:
    name = (file.filename or "").lower()
    if not name.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. Maximum upload size is 10 MB.")
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    try:
        return pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {exc}")


@app.post("/api/inspect")
async def inspect(file: UploadFile = File(...)):
    df = await read_csv_upload(file)
    try:
        return inspect_csv(df)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/api/forecast")
async def forecast(
    file: UploadFile = File(...),
    date_column: str = Form(...),
    sales_column: str = Form(...),
    periods: int = Form(6),
):
    if periods < 1 or periods > 24:
        raise HTTPException(status_code=422, detail="Forecast horizon must be between 1 and 24 months.")
    df = await read_csv_upload(file)
    try:
        return create_forecast(df, date_column, sales_column, periods)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        # Avoid leaking internal stack traces or file contents to public users.
        raise HTTPException(status_code=500, detail="Forecast failed unexpectedly. Check the CSV columns and try again.")


@app.get("/health")
def health():
    return {"status": "ok"}
