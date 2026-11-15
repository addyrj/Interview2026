---

# 256. Azure Log Analytics
# AWS: CloudWatch Logs Insights
# Azure: Log Analytics workspace (query language: KQL)
# हिंदी में: Log Analytics = सभी लॉग्स एक जगह जमा करके KQL से खोजने की सर्विस

---

## 🔵 Simple Definition (2 lines)
A Log Analytics workspace stores logs from many sources and lets you query them with Kusto Query Language (KQL).
Log Analytics में लॉग्स जमा होते हैं और KQL क्वेरी से तुरंत खोजे जा सकते हैं।

---

## 🔴 Why it Exists (2 lines)
Logs scattered across servers are impossible to search during an incident.
A central queryable store gives fast root cause analysis.

---

## 🟢 How it Works
```
VMs/AKS/Apps/Resources -> (Azure Monitor Agent / diagnostic settings / API)
   -> Workspace (tables: AzureActivity, AppRequests, Syslog, ContainerLogV2, custom *_CL)
   -> KQL query -> chart / alert / workbook / export
Retention: per workspace/table (interactive + long-term archive)
```

---

## 💻 Code / Config Example
```bash
az monitor log-analytics workspace create -g rg-demo -n law-demo -l centralindia --retention-time 30

# Run KQL from CLI
az monitor log-analytics query -w <workspace-guid> --analytics-query \
 "AzureActivity | where TimeGenerated > ago(1d) | where ActivityStatusValue == 'Failure' | summarize count() by OperationNameValue | top 10 by count_" -o table
```
```
// KQL: slow requests in the last hour (Application Insights table)
AppRequests
| where TimeGenerated > ago(1h) and DurationMs > 1000
| summarize p95 = percentile(DurationMs, 95), n = count() by Name
| order by p95 desc
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Store | CloudWatch Log groups | Log Analytics workspace |
| Query | Logs Insights / Athena | KQL |
| Cross-source | Per log group | One workspace, many tables |
| Pricing | Ingestion + storage + scan (approximate - check current docs) | Ingestion per GB + retention (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: One workspace per resource.
✅ Correct: Few workspaces (per environment/region) for cross-resource queries; use RBAC to scope.

❌ Mistake: Querying without a time filter.
✅ Correct: Always start with `where TimeGenerated > ago(...)`.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is KQL?
A1: Kusto Query Language, a pipe-based language for log and telemetry analytics.

Q2: [Medium] How do logs get in?
A2: Diagnostic settings, Azure Monitor Agent with data collection rules, SDKs/Logs Ingestion API.

Q3: [Hard] Control cost?
A3: Data collection rules to filter/transform at ingest, table plans (Analytics vs Basic), daily cap, archive tier.

---

## ✅ Quick Checklist
□ Workspace per env/region
□ Time filter in all queries
□ Retention and daily cap set

---

## ⚡ 1-Line Summary
Log Analytics is the KQL-queryable central log store | Log Analytics सभी लॉग्स का केंद्रीय स्टोर है जिसे KQL से क्वेरी करते हैं।

## ➡️ Next: 257. Application Insights

---
