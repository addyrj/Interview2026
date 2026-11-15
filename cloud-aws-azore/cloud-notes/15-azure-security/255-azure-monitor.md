---

# 255. Azure Monitor
# AWS: Amazon CloudWatch
# Azure: Azure Monitor (Metrics, Logs, Alerts, Application Insights)
# हिंदी में: Azure Monitor = मेट्रिक्स, लॉग्स और अलर्ट्स का केंद्रीय सिस्टम

---

## 🔵 Simple Definition (2 lines)
Azure Monitor collects metrics and logs from resources and apps, lets you query them and fire alerts.
Azure Monitor आपके सर्वर और ऐप का डेटा इकट्ठा करके अलर्ट भेजता है।

---

## 🔴 Why it Exists (2 lines)
You cannot fix what you cannot see.
One place for metrics, logs and alerts speeds up incident response.

---

## 🟢 How it Works
```
Sources: Azure resources | VMs (Azure Monitor Agent) | containers | apps (App Insights SDK)
   -> Metrics store (time series, ~93 days*)    -> Metric alerts, dashboards, autoscale
   -> Log Analytics workspace (KQL)             -> Log alerts, workbooks
Alert rule -> Action group (email, SMS, webhook, Function, Teams)
Diagnostic settings: send resource logs to workspace / storage / Event Hub
* approximate - check current docs
```

---

## 💻 Code / Config Example
```bash
# Alert when CPU of a VM > 80% for 5 min
az monitor action-group create -g rg-demo -n ag-ops --short-name ops \
  --action email me you@example.com
az monitor metrics alert create -g rg-demo -n cpu-high \
  --scopes $(az vm show -g rg-demo -n vps1 --query id -o tsv) \
  --condition "avg Percentage CPU > 80" --window-size 5m --evaluation-frequency 1m \
  --action ag-ops --description "High CPU"

# Send resource diagnostic logs to a workspace
az monitor diagnostic-settings create -n to-law --resource <resource-id> \
  --workspace <log-analytics-workspace-id> --logs '[{"category":"AuditEvent","enabled":true}]'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Metrics | CloudWatch Metrics | Azure Monitor Metrics |
| Logs | CloudWatch Logs | Log Analytics (KQL) |
| Alarms | CloudWatch Alarms + SNS | Alert rules + Action groups |
| APM | X-Ray / CloudWatch Application Signals | Application Insights |
| Pricing | Per metric/GB logs (approximate - check current docs) | Per GB ingested (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Sending all debug logs to Log Analytics, then facing a huge bill.
✅ Correct: Filter at source, set retention and daily cap, use basic logs for noisy tables.

❌ Mistake: Alerts without an action group.
✅ Correct: Always attach an action group with an owner.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Metrics vs logs?
A1: Metrics are numeric time series (cheap, fast); logs are detailed text/events queried with KQL.

Q2: [Medium] What is an action group?
A2: A reusable set of notification/automation targets triggered by alerts.

Q3: [Hard] Reduce alert noise?
A3: Use dynamic thresholds, proper aggregation windows, alert processing rules (suppression) and alert on symptoms (SLOs) not every cause.

---

## ✅ Quick Checklist
□ Diagnostic settings on key resources
□ Alerts with action groups
□ Retention and cost caps set

---

## ⚡ 1-Line Summary
Azure Monitor is CloudWatch for Azure: metrics, logs, alerts | Azure Monitor, Azure का CloudWatch है: मेट्रिक्स, लॉग्स, अलर्ट।

## ➡️ Next: 256. Azure Log Analytics

---
