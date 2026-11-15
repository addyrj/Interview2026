---

# 258. Azure Sentinel (SIEM)
# AWS: No single equivalent (Security Lake + GuardDuty + Detective; or OpenSearch SIEM)
# Azure: Microsoft Sentinel (cloud-native SIEM + SOAR)
# हिंदी में: Sentinel = सुरक्षा लॉग्स जोड़कर हमलों की पहचान और स्वचालित जवाब देने वाला SIEM

---

## 🔵 Simple Definition (2 lines)
Sentinel collects security data from everywhere, detects threats with analytics rules and automates response playbooks.
Sentinel सुरक्षा डेटा इकट्ठा करके खतरे पहचानता है और उन पर अपने-आप कार्रवाई करता है।

---

## 🔴 Why it Exists (2 lines)
Security teams drown in alerts spread across tools.
A SIEM correlates signals into incidents and SOAR automates the response.

---

## 🟢 How it Works
```
Data connectors (Entra ID, Azure Activity, Defender, Office 365, AWS CloudTrail, Syslog...)
   -> Log Analytics workspace (Sentinel enabled)
   -> Analytics rules (KQL scheduled / Microsoft security / NRT)
   -> Alerts -> Incidents (grouped, investigated with graph)
   -> Automation rules + Playbooks (Logic Apps): block user, post to Teams, open ticket
Extras: hunting queries, workbooks, threat intelligence, UEBA
```

---

## 💻 Code / Config Example
```
// KQL analytics rule: many failed Entra sign-ins from one IP
SigninLogs
| where TimeGenerated > ago(1h) and ResultType != 0
| summarize failures = count(), users = dcount(UserPrincipalName) by IPAddress
| where failures > 20
```
```bash
# Enable Sentinel on an existing workspace (az 'sentinel' extension, preview-style commands may change)
az extension add -n sentinel
az sentinel onboarding-state create -g rg-demo -n default --workspace-name law-demo
```
Note: connector, rule and CLI syntax change often; verify in current docs.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| SIEM | N/A (no first-party full SIEM; closest: Security Lake + OpenSearch/partners) | Microsoft Sentinel |
| Threat detection | GuardDuty | Defender plans + Sentinel analytics |
| Investigation | Detective | Sentinel incident graph |
| Automation | EventBridge + Lambda | Playbooks (Logic Apps) |
| Pricing | Varies by service | Per GB ingested/commitment tiers (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Ingesting every log source blindly.
✅ Correct: Start with high-value sources (identity, activity, firewall) and tune rules.

❌ Mistake: Too many noisy rules causing alert fatigue.
✅ Correct: Tune thresholds, group alerts into incidents, review false positives.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] SIEM vs SOAR?
A1: SIEM collects and correlates security events; SOAR automates responses. Sentinel does both.

Q2: [Medium] Where does Sentinel store data?
A2: In a Log Analytics workspace; rules are KQL queries.

Q3: [Hard] Control cost?
A3: Choose sources carefully, use commitment tiers, Basic/Auxiliary log tables for high-volume low-value data, and archive long-term.

---

## ✅ Quick Checklist
□ Core connectors enabled
□ Analytics rules tuned
□ Playbook for top incident types

---

## ⚡ 1-Line Summary
Sentinel is Azure's cloud-native SIEM plus SOAR | Sentinel Azure का cloud-native SIEM और SOAR है।

## ➡️ Next: 259. Azure Defender

---
