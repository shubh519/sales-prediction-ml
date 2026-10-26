# Sales Prediction Using Machine Learning

A sales forecasting web application that accepts historical sales CSV data and predicts future monthly sales using Linear Regression with time-trend and month-of-year seasonal features.

## Features

- CSV upload with a 10 MB size limit
- CSV inspection and date/sales column selection
- Monthly aggregation of sales values
- Chronological train/test evaluation
- MAE, RMSE and R-squared (where meaningful)
- Forecast horizons from 1 to 24 months
- Historical/forecast chart and forecast CSV download
- Input validation and clear API error responses
- Health endpoint and automated API tests
- GitHub Actions workflow that runs tests on pushes and pull requests to `main`

## Model and evaluation notes

This implementation is a rebuild of the documented project scope, not recovered original source code. It uses Linear Regression with a time index and month-of-year sine/cosine features. Values are summed by calendar month. The test set is the latest 20% of observed monthly periods, with at least one test month and at least two training months. R-squared is omitted when the test set has fewer than two observations. Forecasts are clamped to zero.

This is a simple baseline model and does not use promotions, holidays, prices, or other external predictors. Model metrics depend on the uploaded dataset; no fixed accuracy percentage is guaranteed. For this regression problem, MAE, RMSE, and R-squared are core evaluation metrics. The API also reports MAPE and a clearly labelled MAPE-based accuracy estimate calculated as max(0, 100 − MAPE). This percentage is a presentation convention, not a universal definition of accuracy; it can be misleading when the dataset is small or sales values are near zero. Review the held-out MAE/RMSE and R² alongside it.

## Run locally on Windows (VS Code)

Install Python 3.11 or 3.12 and Git, then open this folder in VS Code.

### PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

To start the app:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. API documentation is at http://127.0.0.1:8000/docs and the health check is at http://127.0.0.1:8000/health.

## Example evaluation report

See [the synthetic-fixture evaluation report](docs/model-evaluation-example.md) for a reproducible example of MAE, RMSE, R², MAPE, and MAPE-based accuracy. Its 96.12% estimate is from generated test data only, not a real sales dataset.

## Automated tests

The API test suite has been expanded to **24 test cases** covering the homepage, health check, CSV inspection, successful forecasting, forecast output and metrics (including MAPE-based accuracy), supported forecast horizons, invalid uploads, missing columns, invalid horizons, and insufficient/invalid data.

GitHub Actions is configured to run `pytest -q` on pushes and pull requests to `main`. The added tests and workflow are committed, but a passing result should only be reported after the GitHub Actions run or a local `pytest -q` run finishes successfully.

## CSV format

At minimum, include a date column and a numeric sales column:

```csv
date,sales
2024-01-01,1200
2024-02-01,1350
2024-03-01,1280
```

Use real historical data for meaningful forecasts. The example above illustrates the format only.

## API endpoints

- `GET /` — frontend dashboard
- `GET /health` — health check
- `POST /api/inspect` — inspect a CSV upload
- `POST /api/forecast` — train/evaluate and return forecast JSON
- `GET /docs` — interactive API documentation

## Deploy to Render

The project is configured for Render deployment. After deployment, test the homepage, `/health`, and a real CSV upload before relying on the live link in a resume. Free-tier hosting and storage may have limitations.

## Suggested resume wording

**Sales Prediction Using Machine Learning | Python, FastAPI, Pandas, Scikit-learn, HTML, CSS, JavaScript | 2024**

- Developed a web application to forecast future sales from historical CSV data using Linear Regression with trend and seasonal features.
- Collaborated with a fellow developer on project development, debugging, and testing to improve application reliability.
- Implemented chronological train/test evaluation using MAE, RMSE, and R-squared, with interactive forecast visualization and CSV export.
- Expanded automated API test coverage to 23 cases and configured GitHub Actions to run the test suite on pushes and pull requests.

Only claim that tests passed or a specific model performance was achieved after verifying the actual test output and metrics. Keep the original project timeline unchanged.

## Limitations

Forecast quality depends on the uploaded data and can be poor when sales patterns change. The model does not account for external drivers such as promotions, pricing, holidays, or stockouts. Use only non-sensitive sample data.

## Author

**Shubham Kumar**
