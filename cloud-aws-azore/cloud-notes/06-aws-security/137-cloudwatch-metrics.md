# 137. CloudWatch Metrics
# AWS: CloudWatch Metrics (namespaces, dimensions, custom metrics)
# Azure: Azure Monitor Metrics
# हिंदी में: समय के साथ बदलने वाले आँकड़े जैसे CPU, रिक्वेस्ट, लेटेंसी

---

## 🔵 Simple Definition
A metric is a time-ordered set of data points identified by namespace, name and dimensions. AWS services publish them automatically; you can add custom ones.
हिंदी: मेट्रिक समय के साथ के डेटा पॉइंट्स हैं, जो नेमस्पेस, नाम और डाइमेंशन से पहचाने जाते हैं।

---

## 🔴 Why it Exists
You need numbers (CPU, error rate, queue depth) to alert and autoscale.

---

## 🟢 How it Works
```
Namespace  AWS/ECS   or  MyApp/Orders
Metric     CPUUtilization  or  OrdersCreated
Dimensions ClusterName=prod, ServiceName=api
Datapoint  (timestamp, value, unit)  -> Statistic: Avg/Sum/p99 over Period
```

---

## 💻 Code / Config Example
```python
# custom_metric.py (boto3, runs against moto)
import boto3
from datetime import datetime, timedelta, timezone
cw = boto3.client("cloudwatch", region_name="ap-south-1")
cw.put_metric_data(Namespace="MyApp/Orders", MetricData=[{
    "MetricName": "OrdersCreated", "Value": 1, "Unit": "Count",
    "Dimensions": [{"Name": "Env", "Value": "prod"}]}])
now = datetime.now(timezone.utc)
r = cw.get_metric_statistics(Namespace="MyApp/Orders", MetricName="OrdersCreated",
    Dimensions=[{"Name": "Env", "Value": "prod"}],
    StartTime=now - timedelta(minutes=10), EndTime=now + timedelta(minutes=1),
    Period=60, Statistics=["Sum"])
print(r["Datapoints"])
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CloudWatch Metrics | Azure Monitor Metrics |
| Custom | PutMetricData / EMF | Custom metrics API / App Insights |
| Retention | Tiered by resolution (approximate - check current docs) | 93 days (approximate - check current docs) |
| Pricing | Custom metrics billed per metric (approximate - check current docs) | Included for platform metrics |

---

## ⚠️ Common Mistakes
❌ Mistake: High-cardinality dimensions (userId) create huge costs.
✅ Correct: Use low-cardinality dimensions like env/service.

❌ Mistake: Wrong statistic (Average for counts).
✅ Correct: Use Sum for counts, p99 for latency.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a dimension?
A1: A name/value pair that identifies a metric variant.

Q2: [Medium] Standard vs high-resolution custom metric?
A2: Standard has 1-minute granularity; high-resolution allows down to 1 second.

Q3: [Hard] Emit metrics cheaply from Lambda/containers?
A3: Embedded Metric Format: log a JSON line and CloudWatch extracts metrics, avoiding PutMetricData calls.

---

## ✅ Quick Checklist
□ Right statistic and period
□ Low-cardinality dimensions
□ Business metrics as well as infra

---

## ⚡ 1-Line Summary
Metrics = numeric time series for alerts and scaling | मेट्रिक्स अलर्ट और स्केलिंग के लिए संख्यात्मक टाइम-सीरीज़ हैं।

## ➡️ Next: CloudWatch Alarms
