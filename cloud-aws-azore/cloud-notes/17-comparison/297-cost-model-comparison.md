# 297. Cost Model Comparison
# AWS: Cost Explorer, Budgets, Savings Plans, Reserved Instances, Spot
# Azure: Cost Management, Budgets, Reservations, Savings Plan, Spot VMs, Hybrid Benefit
# हिंदी में: कॉस्ट मॉडल की तुलना

---

## 🔵 Simple Definition
Both bill pay-as-you-go, with discounts for commitment (1 or 3 years) and spare capacity (Spot).
हिंदी: दोनों में उपयोग के हिसाब से बिल लगता है, कमिटमेंट और स्पॉट पर छूट मिलती है।

---

## 🔴 Why it Exists
Cloud bills surprise teams; knowing the levers prevents overspend.

---

## 🟢 How it Works
```
On-demand (flexible, highest)
  -> Commitment: Savings Plans / Reserved (AWS)  |  Reservations / Savings Plan (Azure)
  -> Spot (AWS Spot | Azure Spot VMs): cheap, can be evicted
Monitor: Budgets + alerts + tags/cost allocation
```

---

## 💻 Code / Config Example
```bash
# Monthly budget alert
aws budgets create-budget --account-id 123456789012 \
  --budget '{"BudgetName":"monthly","BudgetLimit":{"Amount":"50","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}'

az consumption budget create --budget-name monthly --amount 50 \
  --category cost --time-grain monthly \
  --start-date 2026-12-01 --end-date 2027-12-01
```
Flags for the Azure command vary by CLI version - check `az consumption budget create -h`.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Analysis | Cost Explorer | Cost Management |
| Commitment | Savings Plans / RI | Reservations / Savings Plan |
| Spot | Spot Instances | Spot VMs |
| Free tier | 12-month + always-free (approximate - check current docs) | Free account credit + always-free (approximate - check current docs) |
| Egress | Charged outbound | Charged outbound |
| License saver | BYOL | Azure Hybrid Benefit |

---

## ⚠️ Common Mistakes
❌ Mistake: No budgets, forgotten dev resources and NAT gateways.
✅ Correct: Budgets, tags, auto-shutdown schedules.

❌ Mistake: Buying 3-year commitments for unstable workloads.
✅ Correct: Commit to the stable baseline only.

---

## ⚫ Interview Q&A
Q1: [Easy] How to see spend?
A1: Cost Explorer (AWS) / Cost Management (Azure).

Q2: [Medium] Ways to cut compute cost?
A2: Rightsizing, commitments, Spot for fault-tolerant jobs, scale-to-zero, shutdown schedules.

Q3: [Hard] Hidden costs?
A3: Data egress, cross-AZ/region traffic, NAT gateways, log ingestion, idle load balancers and disks.

---

## ✅ Quick Checklist
□ Budgets with alerts
□ Tagging policy
□ Review egress and logs

---

## ⚡ 1-Line Summary
Same model: on-demand, commit, spot; watch egress. | वही मॉडल: ऑन-डिमांड, कमिटमेंट, स्पॉट; egress पर नजर रखें।

## ➡️ Next: 298. When to Choose AWS vs Azure
