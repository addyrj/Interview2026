# 195. App Service Plans
# AWS: N/A direct (closest: Beanstalk instance config / ECS cluster capacity)
# Azure: App Service Plan
# हिंदी में: वह compute जिस पर आपके Web Apps चलते हैं और जिसका बिल बनता है

---

## 🔵 Simple Definition
The plan defines region, OS, size and instance count; all apps in the plan share that compute and you pay for the plan.
Plan तय करता है कि ऐप किस साइज़ की मशीन पर और कितनी instances में चलेंगे; बिल plan का आता है।

---

## 🔴 Why it Exists
Separates compute (billed) from apps (free to add), letting you pack many small apps on one plan.

---

## 🟢 How it Works
```
Tiers (approximate - check docs):
 Free/Shared F1,D1 : dev only, quotas, no SLA
 Basic B1-B3       : no autoscale, no slots
 Standard S1-S3    : autoscale, slots (5), SLA
 Premium v3/v4 P*  : more slots, VNet, better perf, zone redundancy
 Isolated v2       : dedicated App Service Environment
Scale up = bigger size ; Scale out = more instances
```

---

## 💻 Code / Config Example
```bash
az appservice plan create -g rg-web -n plan-prod --is-linux --sku P1V3 --number-of-workers 2
# Scale up
az appservice plan update -g rg-web -n plan-prod --sku P2V3
# Scale out (manual)
az appservice plan update -g rg-web -n plan-prod --number-of-workers 3
# Autoscale on CPU (Standard+)
az monitor autoscale create -g rg-web --resource plan-prod \
  --resource-type Microsoft.Web/serverfarms --min-count 2 --max-count 5 --count 2 -n as-plan
az monitor autoscale rule create -g rg-web --autoscale-name as-plan \
  --condition "CpuPercentage > 70 avg 5m" --scale out 1
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Concept | N/A (AWS-only gap); closest ECS capacity / Beanstalk env | App Service Plan |
| Billing unit | Instances | Plan instances |
| Scaling | ASG | Scale up/out, autoscale |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving an unused plan running (still billed with no apps).
✅ Correct: Delete empty plans.

❌ Mistake: Dev and prod apps in one plan.
✅ Correct: Separate plans so a noisy dev app cannot starve prod.

---

## ⚫ Interview Q&A
Q1: [Easy] Scale up vs out?
A1: Up = larger instance; out = more instances.

Q2: [Medium] Why does cost not grow per app?
A2: You pay per plan instance; apps share it.

Q3: [Hard] Choose a tier for production with slots and VNet?
A3: Premium v3 (or higher) with at least 2 instances, zone redundancy where supported, autoscale rules.

---

## ✅ Quick Checklist
□ Tier supports slots/autoscale you need
□ Min 2 instances in prod
□ Separate dev/prod plans

---

## ⚡ 1-Line Summary
The plan is the billed compute shared by your apps. | Plan = वह compute जिसका बिल आता है और जिसे ऐप शेयर करते हैं।

## ➡️ Next: App Service Deployment
