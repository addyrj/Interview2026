---

# 83. Timestream (Time Series)
# AWS: Amazon Timestream
# Azure: Azure Data Explorer (ADX) / Azure Managed Grafana + Data Explorer (closest)
# हिंदी में: टाइमस्ट्रीम (टाइम-सीरीज़ डेटाबेस)

---

## 🔵 Simple Definition (2 lines)
Timestream is a serverless time-series database for data that arrives with timestamps (metrics, IoT sensors, app telemetry).
हिंदी: Timestream समय के साथ आने वाले डेटा (सेंसर, मेट्रिक्स) के लिए सर्वरलेस डेटाबेस है।

---

## 🔴 Why it Exists (2 lines)
Time-series data is huge, append-only and queried by time range. Timestream auto-tiers recent data (memory store) to older data (magnetic store) and offers time functions, so no manual partitioning.

---

## 🟢 How it Works
```
Sensors / App ──write──> Timestream table
                           ├─ Memory store   (recent, fast writes/queries)
                           └─ Magnetic store (older, cheap) -- by retention policy
SQL query with time functions (bin(), ago()) ──> Grafana / QuickSight
Note: availability for new customers has changed over time (AWS has moved toward
Timestream for InfluxDB) -- check current docs before choosing it.
```

---

## 💻 Code / Config Example
```python
# Python (boto3): write one record. Needs real AWS; not runnable offline.
import time, boto3
w = boto3.client("timestream-write", region_name="ap-south-1")

w.write_records(
    DatabaseName="iot", TableName="sensors",
    Records=[{
        "Dimensions": [{"Name": "device_id", "Value": "d-42"}],
        "MeasureName": "temperature",
        "MeasureValue": "27.5",
        "MeasureValueType": "DOUBLE",
        "Time": str(int(time.time() * 1000)),   # default unit = MILLISECONDS
    }],
)
```
```sql
SELECT bin(time, 5m) AS t, avg(measure_value::double) AS avg_temp
FROM "iot"."sensors"
WHERE time > ago(1h) AND measure_name = 'temperature'
GROUP BY bin(time, 5m) ORDER BY t;
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Timestream (LiveAnalytics / InfluxDB) | Azure Data Explorer (Kusto) |
| Query | SQL-like with time functions | KQL |
| Tiering | Memory + magnetic retention | Hot cache + cold storage policy |
| Pricing | Writes, storage, query bytes (approximate — check current docs) | Cluster compute + storage (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Storing time series in plain RDS and watching it bloat.
✅ Correct: Use a time-series store with retention policies.

❌ Mistake: Writing records with timestamps outside the memory-store retention window.
✅ Correct: Keep memory retention longer than your late-arriving data delay.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is time-series data?
A1: Measurements indexed by time, usually append-only: CPU metrics, IoT readings, stock ticks.

Q2: [Medium] What are dimensions vs measures?
A2: Dimensions are metadata labels (device_id, region); measures are the values over time (temperature).

Q3: [Hard] How do you control cost?
A3: Short memory-store retention, batch writes, narrow time ranges in queries, and rely on magnetic tier for history.

---

## ✅ Quick Checklist
□ Memory and magnetic retention set
□ Batched writes (not one record per call)
□ Confirm service availability for your account

---

## ⚡ 1-Line Summary
Timestream = serverless DB for timestamped data | Timestream टाइमस्टैम्प वाले डेटा का सर्वरलेस डेटाबेस है।

## ➡️ Next: Choosing Right AWS Database

---
