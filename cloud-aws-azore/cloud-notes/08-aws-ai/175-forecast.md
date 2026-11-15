# 175. Forecast
# AWS: Amazon Forecast (closed to new customers; AWS points to SageMaker Canvas / SageMaker AI for new forecasting; check current status)
# Azure: N/A (AWS-only concept); closest: Azure Machine Learning AutoML forecasting
# हिंदी में: पुराने data से भविष्य की demand का अनुमान

---

## 🔵 Simple Definition
Forecast is a managed time-series service that predicts future values (sales, traffic, inventory) from historical data.
हिंदी: Forecast पुराने time-series data से आने वाली demand का अनुमान लगाता है।

---

## 🔴 Why it Exists
Over- or under-stocking and capacity planning need reliable predictions.
It automates model selection (e.g. DeepAR+, Prophet, ARIMA) and hyperparameters.

---

## 🟢 How it Works
```
Target time series (item_id, timestamp, value) in S3
 -> Dataset group -> Predictor (AutoML or algorithm)
 -> Forecast (P10/P50/P90 quantiles) -> query_forecast or export to S3
Interview note: for new projects consider SageMaker Canvas or AutoGluon-TimeSeries
```

---

## 💻 Code / Config Example
```python
import boto3

fq = boto3.client("forecastquery", region_name="us-east-1")
resp = fq.query_forecast(
    ForecastArn="arn:aws:forecast:us-east-1:123456789012:forecast/demand",
    Filters={"item_id": "SKU-1001"},
)
for p50 in resp["Forecast"]["Predictions"]["p50"][:3]:
    print(p50["Timestamp"], p50["Value"])
```
This only applies to accounts that already have Forecast access.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Forecast (legacy for new customers) | N/A (AWS-only concept) |
| Alternative | SageMaker Canvas / AutoGluon | Azure ML AutoML forecasting |
| Output | Quantile forecasts | Point and interval forecasts |
| Pricing | Per data, training, forecast generated (approximate — check current docs) | Compute-based |

---

## ⚠️ Common Mistakes
❌ Mistake: Missing values and irregular timestamps in data.
✅ Correct: Clean to a consistent frequency before import.

❌ Mistake: Using only the mean forecast.
✅ Correct: Use P10/P90 for safety stock and capacity buffers.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a time series?
A1: Values recorded over time, like daily sales.

Q2: [Medium] Why quantile forecasts?
A2: They express uncertainty so you can plan service levels.

Q3: [Hard] Evaluate forecast quality.
A3: Backtest on holdout windows, compare WAPE/RMSE/wQL vs a naive baseline, monitor drift and retrain.

---

## ✅ Quick Checklist
□ Clean, regular time series
□ Baseline comparison
□ Check service availability before designing

---

## ⚡ 1-Line Summary
Forecast predicts future demand from history, but check availability | Forecast इतिहास से भविष्य की demand बताता है, पर पहले availability जाँचें।

## ➡️ Next: 176. Azure vs AWS — Overview
