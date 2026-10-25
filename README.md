# Sales Prediction Using Machine Learning

A beginner-friendly sales forecasting web application based on the documented scope of the B.Tech minor project. The original report discusses Linear Regression and historical sales forecasting. This rebuilt application implements a working Linear Regression model with a time trend and month-of-year seasonal features.

## Features

- CSV upload with a 10 MB size limit
- CSV inspection and date/sales column selection
- Monthly aggregation of sales values
- Chronological train/test evaluation
- MAE, RMSE and R-squared (where meaningful)
- Configurable forecasts for 3, 6, 12 or 24 months
- Historical/forecast chart and forecast CSV download
- API validation and clear error responses
- Health endpoint and automated API tests
- Render deployment configuration

## Important modelling note

This implementation is a **rebuild**, not recovered original source code. It does not claim to reproduce the exact 2023 implementation. It uses Linear Regression with a time index and month-of-year sine/cosine features. CSV data must have a parseable date column and a numeric sales/value column. Values are summed by calendar month.

The test set is the latest 20% of observed monthly periods (with at least one test month and at least two training months). R-squared is omitted when the test set has fewer than two observations. Forecasts are clamped to zero because negative sales are generally not useful. This simple model does not incorporate prices, promotions, holidays, or other external predictors. Metrics are dataset-dependent and are not guaranteed to be good.

## Run locally on Windows (VS Code)

Install Python 3.11 or 3.12 and Git, then open this folder in VS Code.

### PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Open http://127.0.0.1:8000 in your browser. API documentation is at http://127.0.0.1:8000/docs and health check at http://127.0.0.1:8000/health.

### Run tests

From the project root:

```powershell
pytest -q
```

The repository currently defines **4 automated API tests** in `tests/test_api.py`:

1. Health endpoint returns a successful response.
2. CSV inspection detects the expected date and sales columns.
3. Forecast endpoint returns a three-period forecast and an MAE metric.
4. Non-CSV uploads are rejected.

The test file is evidence of these test cases, not proof of a recent passing run. Run `pytest -q` and record the actual pass/fail output before claiming a test result on your resume.

## CSV format

At minimum, include a date column and a numeric sales column, for example:

```csv
date,sales
2024-01-01,1200
2024-02-01,1350
2024-03-01,1280
```

Use real historical data for meaningful forecasts. The example above is only a format illustration, not a real dataset. The app lets you choose the correct columns if automatic suggestions are wrong.

## API endpoints

- `GET /` — frontend dashboard
- `GET /health` — health check
- `POST /api/inspect` — inspect a CSV upload
- `POST /api/forecast` — train/evaluate and return forecast JSON
- `GET /docs` — interactive API docs

## Deploy to Render

1. Create a GitHub repository and push this project.
2. Sign in to Render and choose **New + → Blueprint** (or create a Web Service manually).
3. Connect the GitHub repository. Render reads `render.yaml`.
4. Wait for the build and deployment to finish.
5. Open the Render-provided HTTPS URL. Test `/health`, the homepage, and a real CSV upload.
6. Do not publish a live URL in a resume until you have personally tested the deployed application.

## Suggested resume wording (keep the original project timeline)

**Sales Prediction Using Machine Learning | Python, FastAPI, Pandas, scikit-learn, HTML, CSS, JavaScript**
- Built a web application that accepts historical sales CSV files, aggregates data monthly, and forecasts future sales using Linear Regression with trend and seasonal features.
- Implemented chronological holdout evaluation using MAE, RMSE and R-squared, with interactive visualizations and CSV export.
- Added input validation and API error handling, and wrote four API tests covering health checks, CSV inspection, forecasting, and invalid file uploads.

Only claim that tests passed, a deployment is live, or specific metrics were achieved after personally running and verifying them. Keep the existing dates on your resume unchanged.

## Security and limitations

This is a portfolio/demo application. Use only non-sensitive sample data. Model metrics depend on the dataset, and this simple model does not account for external drivers such as promotions, pricing, holidays, or stockouts.

## Author

**Shubham Kumar**
