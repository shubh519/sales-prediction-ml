# Example Model Evaluation (Synthetic Test Fixture)

This report demonstrates the metrics returned by the model using the deterministic 24-month CSV fixture in `tests/test_api.py`. It is **not a benchmark on real business sales data** and must not be presented as the model's real-world accuracy.

## Evaluation setup

- Input: 24 generated monthly observations (2024–2025)
- Split: chronological holdout; first 19 months for training and last 5 months for testing
- Model: Linear Regression with time-trend and month-of-year sine/cosine features
- Test actual sales: 195, 207, 219, 231, 215

## Results on this synthetic fixture

| Metric | Result |
|---|---:|
| MAE | 8.1447 |
| RMSE | 9.2151 |
| R² | 0.4129 |
| MAPE | 3.8755% |
| MAPE-based accuracy estimate (max(0, 100 − MAPE)) | 96.1245% |

## Interpretation

The synthetic fixture produces a **96.12% MAPE-based accuracy estimate**, with MAE of about 8.14 sales units and R² of about 0.41. This result only describes this constructed test series. It does not establish 96% accuracy on real sales, other CSV uploads, or future periods.

For a valid project performance claim, upload a representative real dataset and report the chronological holdout metrics from that dataset. Avoid relying on the accuracy percentage alone; report MAE, RMSE and R² as well. MAPE-based accuracy is a convention, not a universal regression accuracy metric, and zero/near-zero sales can make percentage errors undefined or unstable.
