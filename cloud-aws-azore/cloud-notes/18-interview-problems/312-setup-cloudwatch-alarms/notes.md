# 312. Setup CloudWatch Alarms
# AWS: CloudWatch Alarms + SNS (+ log metric filters)
# Azure: Azure Monitor alert rules + Action Groups
# हिंदी में: मेट्रिक थ्रेशोल्ड पार होते ही SNS से ईमेल/Slack अलर्ट भेजना

---

## 🔵 Simple Definition
An alarm watches one metric over N periods and moves OK / ALARM / INSUFFICIENT_DATA; on change it triggers actions (SNS, Auto Scaling, EC2).
हिंदी: मेट्रिक सीमा पार करे तो अलार्म बजे और SNS से सूचना जाए।

## 🔴 Why it Exists
You should hear about errors, latency and saturation before customers do.

## 🟢 How it Works
```
Metric (ALB 5xx, p95 latency, UnHealthyHostCount, CPU, RDS storage, custom log metric)
  -> Alarm (period 60s, 3 of 5 datapoints, treat_missing_data) -> SNS topic
  -> email / Slack (AWS Chatbot) / PagerDuty / Lambda
Golden signals: latency, traffic, errors, saturation
```

## 💻 Code / Config Example
`alarms.tf` (SNS topic + email subscription, six alarms, log metric filter; provider ~> 5.x, not applied here) and `put-alarm.sh` (AWS CLI v2 `put-metric-alarm` and `set-alarm-state` to test; syntax-checked only).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Alerting | CloudWatch Alarms | Azure Monitor alerts |
| Notify | SNS | Action Group |
| Logs to metrics | Metric filter | Log query alert (KQL) |
| Dashboards | CloudWatch Dashboards | Azure Dashboards / Workbooks |
| Pricing | per alarm per month + custom metrics (approximate - check current docs) | per rule / evaluation |

## 💰 Cost / HA / Security
- Cost: alarms and custom metrics are billed; alert on symptoms, avoid hundreds of noisy alarms; set log retention.
- HA: alarms are regional; for region loss use Route 53 health checks or an external monitor.
- Security: restrict SNS topic policy, encrypt topic with KMS if payloads are sensitive.

## ⚠️ Common Mistakes
❌ Alarm on a single datapoint.
✅ Use `datapoints_to_alarm` (M of N) to cut flapping.

❌ Missing data treated as breaching during idle periods.
✅ Choose `treat_missing_data` deliberately.

## ⚫ Interview Q&A
Q1 [Easy]: What are the alarm states?
A1: OK, ALARM, INSUFFICIENT_DATA.

Q2 [Medium]: How do you alarm on application errors in logs?
A2: Metric filter on the log group produces a custom metric; alarm on that metric.

Q3 [Hard]: Design alerting to reduce fatigue.
A3: Page only on user-impact symptoms (5xx, latency SLO burn), ticket for capacity warnings, use composite alarms, M-of-N evaluation, runbook links.

## ✅ Quick Checklist
□ SNS subscription confirmed
□ Test with set-alarm-state
□ Each alarm has an owner and runbook

## ⚡ 1-Line Summary
Alarm on symptoms, route through SNS. | लक्षण पर अलार्म लगाएं और SNS से रूट करें।

## ➡️ Next: 313. Design Multi-region AWS
