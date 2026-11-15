---

# 268. AZURE PRICING CALCULATOR
# AWS: AWS Pricing Calculator
# Azure: Azure Pricing Calculator (+ TCO Calculator)
# हिंदी में: एज़्योर प्राइसिंग कैलकुलेटर

---

## 🔵 Simple Definition (2 lines)
A free web tool (azure.microsoft.com/pricing/calculator) to estimate monthly cost of a planned architecture before deploying it.
हिंदी: डिप्लॉय करने से पहले आर्किटेक्चर का महीने का खर्च अनुमान लगाने वाला मुफ्त टूल।

---

## 🔴 Why it Exists (2 lines)
Cost depends on SKU, region, hours, egress and licences. Estimating up front avoids bad surprises and helps compare options.

---

## 🟢 How it Works
```
1. Add services (App Service, Azure SQL, Storage, Front Door...)
2. Choose region, tier/SKU, instances, hours
3. Pick pricing model: pay-as-you-go | Reserved 1/3 yr | Savings plan
4. Add data transfer (egress), backups, logs
5. Export estimate (Excel) / share link
Then compare to real spend in Cost Management after deploy.
```

---

## 💻 Code / Config Example
```text
Example estimate worksheet for a small Node.js + FastAPI stack (illustrative)
 Service              Config                         Monthly
 App Service Plan     Linux, P0v3, 1 instance        see calculator
 Azure DB PostgreSQL  Burstable B1ms, 32 GB          see calculator
 Storage Account      100 GB hot, LRS                see calculator
 Log Analytics        5 GB/day ingestion             see calculator
 Egress               100 GB                         see calculator
Fill every row from the calculator; prices vary by region and change over time.
```
```bash
# Real prices can be fetched programmatically (public, no auth)
curl -s "https://prices.azure.com/api/retail/prices?\$filter=serviceName eq 'Virtual Machines' and armRegionName eq 'centralindia' and armSkuName eq 'Standard_B2s'" | head -c 600
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Estimator | AWS Pricing Calculator | Azure Pricing Calculator |
| On-prem comparison | Migration Evaluator | TCO Calculator |
| Discounts | Savings Plans, Reserved | Reservations, Savings plan, Hybrid Benefit |
| Price API | Price List API | Azure Retail Prices API |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Forgetting egress, logs, backups and IPs.
✅ Correct: Include data transfer, monitoring and backup lines.

❌ Mistake: Using pay-as-you-go for steady 24x7 workloads.
✅ Correct: Model reservations/savings plan (approximate savings — check current docs).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is the Pricing Calculator for?
A1: Estimating cost of Azure services before deployment.

Q2: [Medium] Pricing Calculator vs TCO Calculator?
A2: Pricing = estimate for Azure design; TCO = compare on-prem cost with Azure migration.

Q3: [Hard] How do you cut a steady workload's bill?
A3: Right-size using Advisor, reservations or savings plan, Azure Hybrid Benefit for licences, auto-shutdown for dev, spot for batch, and tier storage to cool/archive.

---

## ✅ Quick Checklist
□ Estimate saved with assumptions
□ Egress and logs included
□ Re-check against actual spend after month 1

---

## ⚡ 1-Line Summary
Calculator = know the cost before you click deploy | Calculator = डिप्लॉय से पहले खर्च का अंदाज़ा।

## ➡️ Next: Azure DevOps Overview

---
