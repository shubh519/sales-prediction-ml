import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


DATE_HINTS = ("date", "time", "month", "period", "day")
SALES_HINTS = ("sales", "revenue", "amount", "turnover", "quantity", "units", "total")


def _suggest_column(columns, hints):
    for col in columns:
        if any(h in str(col).strip().lower() for h in hints):
            return str(col)
    return str(columns[0]) if len(columns) else None


def inspect_csv(df: pd.DataFrame):
    if df.empty:
        raise ValueError("The CSV has no data rows.")
    if len(df.columns) < 2:
        raise ValueError("The CSV must contain at least a date column and a sales/value column.")
    columns = [str(c) for c in df.columns]
    preview_df = df.head(5).replace({np.nan: None})
    preview = preview_df.to_dict(orient="records")
    date_guess = _suggest_column(columns, DATE_HINTS)
    numeric_cols = [str(c) for c in df.columns if pd.to_numeric(df[c], errors="coerce").notna().sum() > 0]
    sales_guess = _suggest_column(numeric_cols, SALES_HINTS) if numeric_cols else None
    if sales_guess == date_guess and len(numeric_cols) > 1:
        sales_guess = next((c for c in numeric_cols if c != date_guess), numeric_cols[0])
    return {
        "columns": columns,
        "preview": preview,
        "suggested_date_column": date_guess,
        "suggested_sales_column": sales_guess,
        "rows": int(len(df)),
        "note": "Suggestions are automatic. Confirm the correct date and sales columns before forecasting."
    }


def _features(indices, dates):
    indices = np.asarray(indices, dtype=float)
    months = np.asarray([d.month for d in dates], dtype=float)
    return np.column_stack([
        indices,
        np.sin(2 * np.pi * months / 12.0),
        np.cos(2 * np.pi * months / 12.0),
    ])


def create_forecast(df: pd.DataFrame, date_column: str, sales_column: str, periods: int = 6):
    if date_column not in df.columns:
        raise ValueError(f"Date column '{date_column}' was not found.")
    if sales_column not in df.columns:
        raise ValueError(f"Sales column '{sales_column}' was not found.")
    if date_column == sales_column:
        raise ValueError("Choose different columns for date and sales.")
    if periods < 1 or periods > 24:
        raise ValueError("Forecast horizon must be between 1 and 24 months.")

    data = df[[date_column, sales_column]].copy()
    data[date_column] = pd.to_datetime(data[date_column], errors="coerce")
    data[sales_column] = pd.to_numeric(
        data[sales_column].astype(str).str.replace(",", "", regex=False).str.replace("$", "", regex=False),
        errors="coerce"
    )
    data = data.dropna(subset=[date_column, sales_column])
    if data.empty:
        raise ValueError("No usable rows found. Check date formats and numeric sales values.")
    if len(data) < 3:
        raise ValueError("At least 3 valid rows are required to build a forecast.")
    if (data[sales_column] < 0).all():
        raise ValueError("Sales values cannot all be negative.")
    data = data.sort_values(date_column)
    data["period"] = data[date_column].dt.to_period("M")
    monthly = data.groupby("period", as_index=False)[sales_column].sum()
    monthly["date"] = monthly["period"].dt.to_timestamp()
    monthly = monthly.sort_values("date").reset_index(drop=True)
    if len(monthly) < 3:
        raise ValueError("At least 3 distinct months are required. The selected date column may not contain a useful time range.")

    y = monthly[sales_column].astype(float).to_numpy()
    dates = monthly["date"].tolist()
    n = len(monthly)
    # Chronological holdout: train on earlier months and test on later months.
    test_size = max(1, min(max(1, int(round(n * 0.2))), n - 2))
    split = n - test_size
    x_all = _features(np.arange(n), dates)
    model = LinearRegression()
    model.fit(x_all[:split], y[:split])
    test_pred = model.predict(x_all[split:])
    mae = float(mean_absolute_error(y[split:], test_pred))
    rmse = float(np.sqrt(mean_squared_error(y[split:], test_pred)))
    r2 = float(r2_score(y[split:], test_pred)) if len(y[split:]) >= 2 else None

    # Refit on all observed months for production forecasts.
    final_model = LinearRegression().fit(x_all, y)
    future_dates = pd.date_range(monthly["date"].iloc[-1] + pd.offsets.MonthBegin(1), periods=periods, freq="MS")
    future_x = _features(np.arange(n, n + periods), future_dates.tolist())
    future_pred = final_model.predict(future_x)
    future_pred = np.maximum(future_pred, 0)

    history = [
        {"month": d.strftime("%Y-%m"), "sales": round(float(v), 2)}
        for d, v in zip(dates, y)
    ]
    forecast_rows = [
        {"month": d.strftime("%Y-%m"), "predicted_sales": round(float(v), 2)}
        for d, v in zip(future_dates, future_pred)
    ]
    return {
        "model": "Linear Regression with trend and month-of-year seasonal features",
        "aggregation": "Sales values summed by calendar month",
        "observations": int(n),
        "training_observations": int(split),
        "test_observations": int(test_size),
        "metrics": {"mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4) if r2 is not None and np.isfinite(r2) else None},
        "history": history,
        "forecast": forecast_rows,
        "limitations": [
            "Forecast quality depends on the uploaded dataset and may be poor when sales patterns change.",
            "Evaluation uses a chronological holdout; R-squared is omitted when the test set has fewer than two observations.",
            "The model uses time trend and month-of-year seasonality only; it does not account for promotions, holidays, prices, or other external factors."
        ]
    }
