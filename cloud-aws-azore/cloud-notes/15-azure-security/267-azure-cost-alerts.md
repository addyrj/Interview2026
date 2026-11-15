---

# 267. AZURE COST ALERTS
# AWS: AWS Budgets + Cost Anomaly Detection
# Azure: Cost Management Budgets / Cost Alerts
# हिंदी में: एज़्योर कॉस्ट अलर्ट

---

## 🔵 Simple Definition (2 lines)
Azure Cost Management lets you set budgets and get alerts when actual or forecasted spend crosses thresholds; it can also trigger an action group.
हिंदी: Budget तय करो और खर्च तय प्रतिशत पार करते ही ईमेल/ऑटोमेशन से अलर्ट पाओ।

---

## 🔴 Why it Exists (2 lines)
Cloud bills surprise teams (a forgotten GPU VM, a runaway log). Alerts catch overspend while it is still small.

---

## 🟢 How it Works
```
Budget (scope: subscription / RG, amount, monthly)
   -> thresholds: 50% 80% 100% (actual) , 100% (forecasted)
   -> notify: email contacts  and/or  Action Group
   -> Action Group -> webhook / Function / Logic App (e.g. stop dev VMs)
Anomaly alerts: separate, detect unusual daily spend
```

---

## 💻 Code / Config Example
```bicep
// Monthly budget at subscription scope with email alerts
targetScope = 'subscription'

resource budget 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: 'monthly-prod-budget'
  properties: {
    category: 'Cost'
    amount: 200
    timeGrain: 'Monthly'
    timePeriod: { startDate: '2026-12-01' }
    notifications: {
      actual80: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 80
        thresholdType: 'Actual'
        contactEmails: [ 'team@example.com' ]
      }
      forecast100: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        thresholdType: 'Forecasted'
        contactEmails: [ 'team@example.com' ]
      }
    }
  }
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Budgets | AWS Budgets | Cost Management budgets |
| Anomalies | Cost Anomaly Detection | Anomaly alerts |
| Actions | Budget Actions (IAM/SCP, stop EC2) | Action Groups |
| Pricing | First budgets free then per budget; check docs | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Alerts only at 100% actual.
✅ Correct: Add 50/80% actual and a forecasted alert.

❌ Mistake: Thinking a budget stops spending.
✅ Correct: Budgets only notify; add automation via action groups to act.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Does a budget cap spending?
A1: No, it only alerts (and can trigger automation).

Q2: [Medium] Actual vs forecasted alert?
A2: Actual fires on spend so far; forecasted predicts month-end spend and warns earlier.

Q3: [Hard] How do you auto-stop dev costs?
A3: Budget alert -> Action Group -> Logic App/Function using managed identity to deallocate tagged dev VMs, plus auto-shutdown schedules and tag-based cost allocation.

---

## ✅ Quick Checklist
□ Budget per subscription/environment
□ Tags for cost allocation
□ Alerts go to a shared mailbox

---

## ⚡ 1-Line Summary
Cost alerts = early warning before the bill hurts | Cost alerts = बिल बढ़ने से पहले चेतावनी।

## ➡️ Next: Azure Pricing Calculator

---
