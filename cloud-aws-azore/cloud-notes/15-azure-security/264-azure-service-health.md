---

# 264. AZURE SERVICE HEALTH
# AWS: AWS Health Dashboard (Personal Health Dashboard)
# Azure: Azure Service Health (+ Resource Health)
# हिंदी में: एज़्योर सर्विस हेल्थ

---

## 🔵 Simple Definition (2 lines)
Service Health tells you about Azure-side incidents, planned maintenance and advisories affecting your subscriptions and regions; Resource Health shows one resource's status.
हिंदी: Service Health बताता है कि Azure की तरफ़ से कोई आउटेज या मेंटेनेंस आपके रिसोर्स को प्रभावित कर रहा है या नहीं।

---

## 🔴 Why it Exists (2 lines)
When your API is down, you must know if it is your bug or an Azure outage. The public status page is generic; Service Health is personalised.

---

## 🟢 How it Works
```
Azure incident / maintenance
   -> filtered to YOUR subscriptions, services, regions
   -> Service Health blade (Service issues, Planned maintenance,
      Health advisories, Security advisories)
   -> Service Health alert -> Action Group -> email/SMS/webhook/Teams
Resource Health: per-resource Available / Unavailable / Degraded / Unknown
```

---

## 💻 Code / Config Example
```bash
# Action group that emails the on-call
az monitor action-group create -g rg-ops -n ag-oncall \
  --action email oncall oncall@example.com

# Activity-log alert for Service Health incidents
az monitor activity-log alert create -g rg-ops -n alert-service-health \
  --scope /subscriptions/<sub-id> \
  --condition category=ServiceHealth \
  --action-group ag-oncall
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Public status | health.aws.amazon.com | azure.status.microsoft |
| Personalised | AWS Health Dashboard | Service Health |
| Per-resource | Health events for resources | Resource Health |
| Alerts | EventBridge on aws.health | Activity log alert + Action Group |
| Pricing | Free (Health API needs Business support+) | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Relying on the public status page only.
✅ Correct: Create Service Health alerts for your regions and services.

❌ Mistake: Alert goes to one person's email.
✅ Correct: Use a shared action group (on-call rotation, Teams/webhook).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does Service Health cover?
A1: Service issues, planned maintenance, health advisories, security advisories for your resources.

Q2: [Medium] Service Health vs Resource Health vs Azure Monitor?
A2: Service Health = platform events; Resource Health = a single resource's availability; Monitor = your app/infra metrics and logs.

Q3: [Hard] How do you design for a regional outage?
A3: Multi-region active/passive with Front Door or Traffic Manager, geo-replicated data, tested failover runbooks, and Service Health alerts to trigger the runbook.

---

## ✅ Quick Checklist
□ Service Health alert on all prod regions
□ Action group has more than one receiver
□ Failover runbook tested

---

## ⚡ 1-Line Summary
Service Health = personalised Azure outage and maintenance feed | Service Health = आपके लिए Azure आउटेज की सूचना।

## ➡️ Next: Azure Activity Log

---
