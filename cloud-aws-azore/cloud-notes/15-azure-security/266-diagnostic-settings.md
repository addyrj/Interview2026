---

# 266. DIAGNOSTIC SETTINGS
# AWS: CloudWatch Logs subscriptions / log delivery configs (S3, CloudWatch)
# Azure: Diagnostic Settings
# हिंदी में: डायग्नोस्टिक सेटिंग्स

---

## 🔵 Simple Definition (2 lines)
A Diagnostic Setting routes a resource's logs and metrics to destinations: Log Analytics workspace, Storage account, Event Hub, or a partner.
हिंदी: Diagnostic Setting तय करती है कि किसी रिसोर्स के लॉग और मेट्रिक्स कहाँ भेजे जाएँ।

---

## 🔴 Why it Exists (2 lines)
Most Azure resource logs are not collected by default. Without a setting you cannot debug or audit them later.

---

## 🟢 How it Works
```
Resource (App Service, Key Vault, NSG, SQL...)
   |  categories: logs + AllMetrics
   v
Diagnostic Setting (up to 5 per resource)
   +--> Log Analytics workspace  (query with KQL, alerts)
   +--> Storage account          (cheap archive)
   +--> Event Hub                (stream to SIEM)
```

---

## 💻 Code / Config Example
```bash
WS=$(az monitor log-analytics workspace show -g rg-ops -n law-prod --query id -o tsv)
APP=$(az webapp show -g rg-prod -n api-prod --query id -o tsv)

az monitor diagnostic-settings create --name to-law \
  --resource "$APP" --workspace "$WS" \
  --logs '[{"category":"AppServiceHTTPLogs","enabled":true},{"category":"AppServiceConsoleLogs","enabled":true}]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'
```
```
// KQL: 5xx in the last hour
AppServiceHTTPLogs
| where TimeGenerated > ago(1h) and ScStatus >= 500
| summarize count() by CsUriStem
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Config unit | Per-service log config (e.g. ALB to S3, Lambda to CW) | Diagnostic Setting per resource |
| Query | CloudWatch Logs Insights | KQL in Log Analytics |
| Archive | S3 | Storage account |
| Streaming | Kinesis / Firehose | Event Hub |
| Pricing | Ingestion + storage billed | Ingestion + retention billed (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Enabling every category on every resource.
✅ Correct: Pick needed categories; ingestion cost grows fast.

❌ Mistake: Configuring settings by hand per resource.
✅ Correct: Enforce with Azure Policy (DeployIfNotExists) or IaC.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What destinations are supported?
A1: Log Analytics, Storage account, Event Hub, partner solutions.

Q2: [Medium] Activity Log vs resource logs?
A2: Activity Log = control plane at subscription level; resource logs = data-plane logs emitted per resource, need a Diagnostic Setting.

Q3: [Hard] How do you reduce Log Analytics cost?
A3: Select only needed categories, use Basic Logs tier or archive to Storage for noisy tables, set retention per table, use a daily cap and data collection rules to filter.

---

## ✅ Quick Checklist
□ Prod resources send to a central workspace
□ Categories chosen deliberately
□ Policy enforces it for new resources

---

## ⚡ 1-Line Summary
Diagnostic Settings = pipe resource logs to where you can query them | Diagnostic Settings = लॉग को सही जगह भेजने की सेटिंग।

## ➡️ Next: Azure Cost Alerts

---
