# 185. Azure Cost Management
# AWS: Cost Explorer + AWS Budgets
# Azure: Microsoft Cost Management + Billing
# हिंदी में: Azure का खर्च देखना, बजट लगाना और अलर्ट पाना

---

## 🔵 Simple Definition
Cost Management analyzes spend by scope/tag, sets budgets with alerts, and gives advisor-based savings recommendations.
यह बताता है कि पैसा कहाँ खर्च हो रहा है, बजट सेट करता है और सीमा पार होने पर अलर्ट देता है।

---

## 🔴 Why it Exists
Cloud bills are pay-as-you-go; forgotten VMs or public IPs silently cost money.

---

## 🟢 How it Works
```
Usage data -> Cost analysis (group by resource group / tag / service)
           -> Budgets (scope + amount + thresholds) -> email / action group
           -> Advisor: right-size, shutdown idle, Reservations, Savings Plans
```
Cost data can lag by hours; exports to a storage account are available for BI.

---

## 💻 Code / Config Example
```bash
# Budget on a subscription (az consumption budget; check az version for flags)
az consumption budget create \
  --budget-name monthly-100 --amount 100 --category cost \
  --time-grain monthly \
  --start-date 2026-11-01 --end-date 2027-10-31
```
```bicep
// Bicep: budget with 80% alert (subscription scope), API 2023-05-01
targetScope = 'subscription'
resource budget 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: 'monthly-100'
  properties: {
    category: 'Cost'
    amount: 100
    timeGrain: 'Monthly'
    timePeriod: { startDate: '2026-11-01' }
    notifications: {
      actual80: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 80
        contactEmails: ['me@example.com']
      }
    }
  }
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Analysis | Cost Explorer | Cost analysis |
| Alerts | Budgets | Budgets |
| Commitment | Savings Plans / RIs | Reservations / Savings Plans |
| Pricing | Explorer free; API calls small fee | Free for Azure-native scopes |

---

## ⚠️ Common Mistakes
❌ Mistake: Budget only emails, nobody reads it.
✅ Correct: Send to an action group and a team channel; set forecast alerts.

❌ Mistake: Leaving stopped (not deallocated) VMs.
✅ Correct: Deallocate; delete orphan disks and public IPs.

---

## ⚫ Interview Q&A
Q1: [Easy] Does a budget stop spending?
A1: No, it only alerts unless an action (automation) is attached.

Q2: [Medium] How to attribute cost per team?
A2: Consistent tags (inherit via Policy) and group cost analysis by tag.

Q3: [Hard] Cut a small API's bill by 40%?
A3: Right-size, auto-shutdown dev, Reservations for steady prod, B-series/burstable, Spot for batch, delete unattached resources.

---

## ✅ Quick Checklist
□ Budget + forecast alert set
□ Tags enforced
□ Monthly review of Advisor

---

## ⚡ 1-Line Summary
Cost Management = visibility, budgets and savings advice. | Cost Management = खर्च की निगरानी, बजट और बचत।

## ➡️ Next: Azure SLA + Credits
