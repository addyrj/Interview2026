# 285. Azure Application Insights for Node.js
# AWS: CloudWatch + X-Ray (or CloudWatch Application Signals)
# Azure: Application Insights (Azure Monitor)
# हिंदी में: Node.js के लिए Application Insights

---

## 🔵 Simple Definition
Application Insights is Azure Monitor's APM: it collects requests, dependencies, exceptions, logs and traces from your app.
हिंदी: Application Insights आपके Node.js ऐप के रिक्वेस्ट, एरर और ट्रेस इकट्ठा करने वाला APM है।

---

## 🔴 Why it Exists
Console logs do not show slow dependencies or end-to-end request paths.
App Insights gives live metrics, distributed tracing and alerting.

---

## 🟢 How it Works
```
Node app + Azure Monitor OpenTelemetry distro
   -> connection string -> Application Insights (Log Analytics workspace)
   -> Live Metrics, Application Map, Failures, Performance
   -> KQL queries + Alerts
```

---

## 💻 Code / Config Example
```javascript
// tracing.js - must load BEFORE other imports (node -r ./tracing.js app.js)
// npm i @azure/monitor-opentelemetry
const { useAzureMonitor } = require("@azure/monitor-opentelemetry");

useAzureMonitor({
  azureMonitorExporterOptions: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING,
  },
});
```
```kusto
// KQL: slowest requests in last hour
requests
| where timestamp > ago(1h)
| summarize p95 = percentile(duration, 95) by name
| order by p95 desc
```
Note: the older `applicationinsights` SDK v2 is the classic path; `@azure/monitor-opentelemetry` is the current recommended one (verify version in docs).

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CloudWatch, X-Ray | Application Insights |
| Query | Logs Insights | KQL |
| Tracing | X-Ray / OpenTelemetry (ADOT) | OpenTelemetry distro |
| Pricing | Per metric/log/trace | Per GB ingested (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Initializing SDK after importing express/http, so nothing is instrumented.
✅ Correct: Load it first via `-r` or at the top of the entry file.

❌ Mistake: Hardcoding connection string in source.
✅ Correct: Env var / Key Vault; sample rate to control cost.

---

## ⚫ Interview Q&A
Q1: [Easy] What do you need to start?
A1: An Application Insights resource and its connection string.

Q2: [Medium] How do you control cost?
A2: Sampling, daily cap, and reducing verbose logs.

Q3: [Hard] How do you trace across NestJS and FastAPI services?
A3: OpenTelemetry W3C `traceparent` header propagation; both export to the same App Insights so Application Map links them.

---

## ✅ Quick Checklist
□ Init before app imports
□ Connection string via env
□ Alerts on failures and p95

---

## ⚡ 1-Line Summary
App Insights = APM and tracing for your Node.js app on Azure Monitor. | App Insights = Azure Monitor पर आपके ऐप का APM और ट्रेसिंग।

## ➡️ Next: 286. Compute Services Comparison
