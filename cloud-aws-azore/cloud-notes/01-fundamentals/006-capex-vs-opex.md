---

# 6. CapEx vs OpEx
# AWS: AWS Budgets, Cost Explorer, Savings Plans
# Azure: Cost Management + Billing, Azure Budgets, Reservations
# हिंदी में: CapEx = पहले बड़ी खरीद, OpEx = हर महीने इस्तेमाल का खर्च

---

## 🔵 Simple Definition (2 lines)
CapEx is upfront spending on assets (servers, data center). OpEx is ongoing spending on services you consume (cloud bills).
हिंदी: CapEx यानी पहले हार्डवेयर पर बड़ा निवेश, OpEx यानी इस्तेमाल के हिसाब से मासिक खर्च।

---

## 🔴 Why it Exists (2 lines)
Big upfront hardware bets are risky for startups and slow to approve.
Cloud turns them into a variable monthly cost that follows the business.

---

## 🟢 How it Works
```
CapEx:  buy 10 servers = big cost day 1, depreciate over ~3-5 yrs
        cost
         |■■■■■■■■■■|______________________ time
OpEx:   pay per hour used
         |■ ■ ■ ■ ■ ■ ■ ■ ■ ■  (grows with usage)
Middle path: 1-3 yr commitments (Savings Plans / Reservations) = lower rate, still OpEx
```

---

## 💻 Code / Config Example
```bash
# AWS: monthly cost budget with email alert at 80% (replace account id/email)
cat > budget.json <<'EOF'
{"BudgetName":"monthly-100usd","BudgetLimit":{"Amount":"100","Unit":"USD"},
 "TimeUnit":"MONTHLY","BudgetType":"COST"}
EOF
cat > notif.json <<'EOF'
[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN",
 "Threshold":80,"ThresholdType":"PERCENTAGE"},
 "Subscribers":[{"SubscriptionType":"EMAIL","Address":"me@example.com"}]}]
EOF
aws budgets create-budget --account-id 123456789012 \
  --budget file://budget.json --notifications-with-subscribers file://notif.json

# Azure: budget on a resource group (check `az consumption budget create -h` for your CLI version)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Cost analysis | Cost Explorer | Cost Management |
| Budget alerts | AWS Budgets | Azure Budgets |
| Commitment discount | Savings Plans, Reserved Instances | Reservations, Savings Plan |
| Spare capacity | Spot Instances | Spot VMs |

---

## ⚠️ Common Mistakes
❌ Mistake: No budget alert, then a surprise bill.
✅ Correct: Create budgets and anomaly alerts on day one.

❌ Mistake: Committing for 3 years before usage is stable.
✅ Correct: Measure 1-3 months first, then commit to the steady baseline only.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Define CapEx and OpEx.
A1: CapEx is upfront asset purchase; OpEx is recurring operating expense.

Q2: [Medium] Why do finance teams like OpEx?
A2: No big upfront cash, cost scales with revenue, easy to experiment; though long-run steady load may cost more.

Q3: [Hard] How do you lower OpEx for steady workloads?
A3: Right-size, commit via Savings Plans/Reservations for baseline, Spot for fault-tolerant jobs, schedule off non-prod, and use lifecycle tiers for storage.

---

## ✅ Quick Checklist
□ Budgets and alerts exist
□ Resources tagged by team/env
□ Commitments only on stable baseline

---

## ⚡ 1-Line Summary
Cloud shifts spend from CapEx to OpEx | क्लाउड बड़े पहले-खर्च को मासिक इस्तेमाल-खर्च में बदल देता है।

## ➡️ Next: 7. Shared Responsibility Model

---
