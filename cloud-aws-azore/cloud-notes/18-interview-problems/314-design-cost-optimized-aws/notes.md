# 314. Design Cost Optimized AWS
# AWS: Spot + Graviton + Savings Plans + S3 lifecycle + Budgets
# Azure: Spot VMs + Ampere/Arm VMs + Reservations/Savings Plan + Blob lifecycle + Cost Management budgets
# हिंदी में: कम से कम खर्च में वही परफॉर्मेंस - सही साइज़, स्पॉट, लाइफसाइकल और बजट अलर्ट

---

## 🔵 Simple Definition
Design so you pay only for what you use: right-size, use Spot/Arm for flexible work, commit for steady work, tier storage, alert on spend.
हिंदी: जितना इस्तेमाल उतना ही भुगतान - साइज़ सही, स्पॉट, कमिटमेंट और अलर्ट।

## 🔴 Why it Exists
Cloud bills grow silently (idle instances, old logs, over-provisioned DBs). Cost is a design constraint like latency.

## 🟢 How it Works
```
Baseline (steady)  -> Savings Plan / Reserved   (commit 1-3 yr)
Burst / stateless  -> Spot in ASG (mixed types)  + 1 on-demand base
Compute type       -> Graviton (arm64) where app supports it
Storage            -> S3 Standard -> IA (30d) -> Glacier (90d) -> expire
Guardrails         -> Budgets alert at 80%, cost-allocation tags, Cost Explorer review
```

## 💻 Code / Config Example
`main.tf` (this folder): Graviton launch template (IMDSv2), ASG mixed-instances policy (1 on-demand base, rest Spot, price-capacity-optimized), CPU target tracking, S3 lifecycle, monthly budget with 80% email alert. Not applied; terraform not installed.
Dependency: Spot instances can be reclaimed with a 2-minute notice - app must be stateless and handle SIGTERM.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Discount model | Savings Plans / RI | Reservations / Savings Plan |
| Interruptible | Spot | Spot VMs / Spot scale sets |
| Arm | Graviton | Cobalt/Ampere Arm VMs |
| Tiering | S3 lifecycle | Blob lifecycle management |
| Budgets | AWS Budgets | Cost Management budgets |
| Pricing | discounts vary by term/region (approximate - check current docs) | same |

## 💰 Cost / HA / Security
- Cost: biggest wins are usually right-sizing, turning off non-prod at night, deleting unattached volumes, and NAT/data-transfer review.
- HA: Spot only above an on-demand base and across many instance types/AZs.
- Security: do not trade away encryption/backups for savings; tag-based budgets need tag enforcement (SCP / Azure Policy).

## ⚠️ Common Mistakes
❌ Buying a 3-year commitment before right-sizing.
✅ Right-size first, then commit to the steady baseline only.

❌ Spot for the single stateful DB.
✅ Spot for stateless/batch; DBs on on-demand/reserved.

## ⚫ Interview Q&A
Q1 [Easy]: Spot vs On-Demand?
A1: Spot is spare capacity at a discount but can be reclaimed on short notice; On-Demand is guaranteed at list price.

Q2 [Medium]: Savings Plan vs Reserved Instance?
A2: Both are commitments for a discount; Savings Plans commit to $/hour spend and are more flexible; RIs are tied to instance attributes.

Q3 [Hard]: Bill jumped 40% this month; how do you find it?
A3: Cost Explorer grouped by service then usage type/tag, check data transfer/NAT, new resources via CloudTrail, anomaly detection, then fix and add budget alerts.

## ✅ Quick Checklist
□ Tags for cost allocation
□ Budget + anomaly alerts on
□ Idle/unattached resources reviewed monthly

## ⚡ 1-Line Summary
Right-size, mix Spot with a base, tier storage, commit last, alert always. | साइज़ सही करो, स्पॉट + बेस, स्टोरेज टियर, आख़िर में कमिटमेंट, हमेशा अलर्ट।

## ➡️ Next: 315. Design Same App on Azure
