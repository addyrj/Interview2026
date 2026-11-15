# 320. Cloud Cost Optimization
# AWS: Cost Explorer + Budgets + Compute Optimizer + Trusted Advisor
# Azure: Cost Management + Advisor + Reservations
# हिंदी में: क्लाउड बिल कम करना - बर्बादी ढूँढो, साइज़ सही करो, फिर कमिटमेंट लो

---

## 🔵 Simple Definition
A repeatable loop: see spend, find waste, right-size, commit to the steady part, and set alerts.
हिंदी: खर्च देखो, बर्बादी हटाओ, साइज़ सही करो, स्थिर हिस्से पर कमिटमेंट, अलर्ट लगाओ।

## 🔴 Why it Exists
Spend grows with forgotten resources and over-provisioning; FinOps keeps engineering and finance aligned.

## 🟢 How it Works
```
Visibility : tags + cost allocation + Cost Explorer / Cost Management
Waste      : unattached disks, idle IPs/LBs, stopped-but-billed, old snapshots, NAT/data transfer
Right-size : Compute Optimizer / Advisor recommendations, CloudWatch CPU/mem
Pricing    : Savings Plans/Reservations (steady), Spot (flexible), lifecycle tiers (storage)
Governance : budgets, anomaly detection, monthly review, scheduled non-prod shutdown
```

## 💻 Code / Config Example
`cost_audit.py`: read-only boto3 script listing unattached EBS volumes, idle Elastic IPs, stopped instances. Azure counterpart: `az disk list --query "[?diskState=='Unattached']"` (not run - Azure CLI unavailable). See also 314 for Terraform (Spot ASG, lifecycle, budget).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Analysis | Cost Explorer | Cost Management |
| Recommendations | Compute Optimizer / Trusted Advisor | Azure Advisor |
| Commitments | Savings Plans / RI | Reservations / Savings Plan |
| Alerts | Budgets, Cost Anomaly Detection | Budgets, anomaly alerts |
| Pricing | rates vary (approximate - check current docs) | same |

## 💰 Cost / HA / Security
- Cost: order of effort - delete waste, right-size, schedule off-hours, then commit.
- HA: never cut redundancy blindly; weigh savings against RTO/RPO.
- Security: cost scripts should be read-only; auditing public IPs/unused resources also shrinks attack surface.

## ⚠️ Common Mistakes
❌ Committing before right-sizing.
✅ Right-size, then commit to baseline.

❌ No tagging, so nobody owns the bill.
✅ Mandatory owner/env tags via policy.

## ⚫ Interview Q&A
Q1 [Easy]: Name three quick wins.
A1: Delete unattached volumes/idle IPs, stop non-prod at night, right-size oversized instances.

Q2 [Medium]: Hidden costs besides compute?
A2: NAT gateway processing, cross-AZ/region/internet data transfer, CloudWatch logs ingestion, snapshots, idle load balancers.

Q3 [Hard]: How would you build FinOps culture?
A3: Tag standards and showback/chargeback, per-team budgets and anomaly alerts, monthly reviews, cost as an engineering metric in design reviews, automated cleanup with guardrails.

## ✅ Quick Checklist
□ Tags and budgets in place
□ Monthly waste audit
□ Commitments sized to baseline

## ⚡ 1-Line Summary
Visibility, cleanup, right-size, then commit - repeat monthly. | दृश्यता, सफ़ाई, साइज़ सही, फिर कमिटमेंट - हर महीने दोहराओ।

## ➡️ Next: 321 (next folder topic)
