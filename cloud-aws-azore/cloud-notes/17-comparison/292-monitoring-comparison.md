# 292. Monitoring Comparison
# AWS: CloudWatch (Metrics, Logs, Alarms), X-Ray, CloudTrail
# Azure: Azure Monitor, Log Analytics, Application Insights, Activity Log
# हिंदी में: मॉनिटरिंग की तुलना

---

## 🔵 Simple Definition
Metrics, logs, traces and alerts are collected centrally; AWS centers on CloudWatch, Azure on Azure Monitor.
हिंदी: मेट्रिक, लॉग, ट्रेस और अलर्ट एक जगह जमा होते हैं, AWS में CloudWatch और Azure में Azure Monitor।

---

## 🔴 Why it Exists
You cannot fix what you cannot see; alerts catch outages before users do.

---

## 🟢 How it Works
```
App/VM/Container -> agent / SDK / diagnostic settings
   -> Metrics + Logs + Traces store (CloudWatch | Azure Monitor + Log Analytics)
   -> Query (Logs Insights | KQL) -> Alarm / Alert rule -> SNS | Action Group
```

---

## 💻 Code / Config Example
```bash
# CPU alarm
aws cloudwatch put-metric-alarm --alarm-name cpu-high --namespace AWS/EC2 \
  --metric-name CPUUtilization --statistic Average --period 300 \
  --threshold 80 --comparison-operator GreaterThanThreshold --evaluation-periods 2 \
  --dimensions Name=InstanceId,Value=i-0abc --alarm-actions arn:aws:sns:ap-south-1:123456789012:ops

az monitor metrics alert create -n cpu-high -g rg-demo \
  --scopes /subscriptions/SUB/resourceGroups/rg-demo/providers/Microsoft.Compute/virtualMachines/vm1 \
  --condition "avg Percentage CPU > 80" --window-size 5m --evaluation-frequency 1m \
  --action ops-action-group
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Metrics | CloudWatch Metrics | Azure Monitor Metrics |
| Logs query | Logs Insights | KQL in Log Analytics |
| APM/tracing | X-Ray | Application Insights |
| Audit | CloudTrail | Activity Log |
| Notify | SNS | Action Groups |

---

## ⚠️ Common Mistakes
❌ Mistake: Logging everything forever.
✅ Correct: Set retention and sampling to control cost.

❌ Mistake: Alerting on CPU only.
✅ Correct: Alert on user-facing symptoms: error rate, latency, queue depth.

---

## ⚫ Interview Q&A
Q1: [Easy] CloudWatch equivalent?
A1: Azure Monitor.

Q2: [Medium] Where do Azure logs live?
A2: Log Analytics workspace, queried with KQL.

Q3: [Hard] Design alerting for an API?
A3: SLOs on p95 latency and 5xx rate, multi-window alerts, routing to on-call via Action Group/SNS, plus runbooks.

---

## ✅ Quick Checklist
□ Metrics, logs, traces all on
□ Retention set
□ Alerts routed to a person

---

## ⚡ 1-Line Summary
CloudWatch=Azure Monitor, X-Ray=App Insights. | CloudWatch=Azure Monitor, X-Ray=App Insights।

## ➡️ Next: 293. CI/CD Comparison
