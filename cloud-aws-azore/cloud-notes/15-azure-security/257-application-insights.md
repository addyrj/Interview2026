---

# 257. Application Insights
# AWS: AWS X-Ray + CloudWatch RUM / Application Signals
# Azure: Application Insights (part of Azure Monitor, workspace-based)
# हिंदी में: ऐप का प्रदर्शन, एरर और डिपेंडेंसी ट्रेस करने वाला APM टूल

---

## 🔵 Simple Definition (2 lines)
Application Insights is an APM service tracking requests, dependencies, exceptions and traces of your running app.
यह बताता है कि आपका ऐप कहाँ धीमा है या कहाँ एरर आ रहा है।

---

## 🔴 Why it Exists (2 lines)
Infrastructure metrics do not explain slow endpoints or failing DB calls.
App-level telemetry shows the exact request, query and exception.

---

## 🟢 How it Works
```
App + OpenTelemetry/SDK -> connection string -> Application Insights (workspace-based)
   -> Requests, Dependencies, Exceptions, Traces, Custom events
   -> Application Map, Live Metrics, Transaction search, Availability tests, Alerts
Data stored in Log Analytics tables: AppRequests, AppDependencies, AppExceptions, AppTraces
```

---

## 💻 Code / Config Example
```javascript
// Node.js / NestJS: npm i @azure/monitor-opentelemetry   (call BEFORE other imports)
const { useAzureMonitor } = require("@azure/monitor-opentelemetry");
useAzureMonitor({
  azureMonitorExporterOptions: { connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING },
});
// Express/Nest code follows; HTTP requests, DB calls and exceptions are auto-collected
```
```python
# FastAPI: pip install azure-monitor-opentelemetry
import os
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor(connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"])
from fastapi import FastAPI
app = FastAPI()
```
```bash
az monitor app-insights component create --app my-api -g rg-demo -l centralindia \
  --workspace <log-analytics-workspace-id>   # needs 'application-insights' CLI extension
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Tracing | X-Ray | Application Insights (distributed tracing) |
| Service map | X-Ray service map | Application Map |
| Browser monitoring | CloudWatch RUM | JS SDK / browser telemetry |
| Standard | OpenTelemetry via ADOT | OpenTelemetry distro |
| Pricing | Per trace/sample (approximate - check current docs) | Per GB ingested (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Initialising telemetry after importing frameworks, so nothing is instrumented.
✅ Correct: Start OpenTelemetry first in the entry file.

❌ Mistake: 100% sampling of high-traffic apps.
✅ Correct: Configure sampling to control cost.

❌ Mistake: Using the old instrumentation key only.
✅ Correct: Use the connection string.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does it monitor?
A1: Requests, dependencies, exceptions, performance and custom telemetry of an app.

Q2: [Medium] Workspace-based vs classic?
A2: Workspace-based stores data in Log Analytics (unified queries, RBAC); classic is retired.

Q3: [Hard] Trace one request across microservices?
A3: W3C trace context propagation (OpenTelemetry) links spans by operation ID; view in Transaction search or Application Map.

---

## ✅ Quick Checklist
□ Connection string from env/Key Vault
□ Sampling configured
□ Availability test + alerts on failures

---

## ⚡ 1-Line Summary
Application Insights is Azure's APM for traces, errors and performance | Application Insights ऐप की परफ़ॉर्मेंस और एरर ट्रैक करने वाला APM है।

## ➡️ Next: 258. Azure Sentinel

---
