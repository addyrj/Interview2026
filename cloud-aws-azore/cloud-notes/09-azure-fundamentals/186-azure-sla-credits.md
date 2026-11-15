# 186. Azure SLA + Credits
# AWS: Service SLAs + AWS Free Tier / Credits
# Azure: Azure SLA + Free account credits
# हिंदी में: Azure की uptime गारंटी और मुफ़्त क्रेडिट की जानकारी

---

## 🔵 Simple Definition
An SLA is Microsoft's uptime commitment per service, with service credits if missed. Free account offers trial credit plus free-tier services.
SLA uptime की गारंटी है; मिस होने पर बिल में credit मिलता है। Free account में शुरुआती क्रेडिट मिलता है।

---

## 🔴 Why it Exists
You must know the availability you can promise customers; composite SLAs of chained services are lower than each part.

---

## 🟢 How it Works
```
Composite SLA = SLA1 x SLA2 x ...
App Service 99.95% x Azure SQL 99.99% = ~99.94%
Single VM (Premium SSD) 99.9% ; 2+ VMs in Availability Zones 99.99%
```
These numbers are approximate - check the current Azure SLA page. Credits are claimed via a support request within a time window; they do not cover your losses.

---

## 💻 Code / Config Example
```python
# Composite SLA calculator
slas = {"app_service": 99.95, "azure_sql": 99.99, "front_door": 99.99}
total = 1.0
for v in slas.values():
    total *= v / 100
print(f"Composite: {total*100:.3f}%")
downtime_min = (1 - total) * 30 * 24 * 60
print(f"Allowed downtime/month: {downtime_min:.1f} min")
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| SLA | Per service (e.g., EC2 Region 99.99%) | Per service, varies by config |
| Free offer | Free Tier (changed model in 2025: credits-based for new accounts, check docs) | Free account: credit for first 30 days + 12 months/always-free services (approximate - check docs) |
| Remedy | Service credits | Service credits |

---

## ⚠️ Common Mistakes
❌ Mistake: Quoting a single service SLA as the app SLA.
✅ Correct: Multiply dependencies; add redundancy for critical paths.

❌ Mistake: Forgetting free credits expire and resources keep billing.
✅ Correct: Set a budget and delete the resource group after labs.

---

## ⚫ Interview Q&A
Q1: [Easy] What does 99.9% allow per month?
A1: About 43 minutes of downtime.

Q2: [Medium] Why does a single VM have a low SLA?
A2: No redundancy; SLA depends on disk type and zones/availability sets.

Q3: [Hard] How do you reach 99.99% for an API?
A3: Zone-redundant App Service/AKS, zone-redundant DB, Front Door or Traffic Manager across regions, health probes, and stateless design.

---

## ✅ Quick Checklist
□ Composite SLA computed
□ Zones used for production
□ Free-credit expiry noted

---

## ⚡ 1-Line Summary
SLA = promised uptime; chain them by multiplication. | SLA = uptime का वादा; सेवाओं को जोड़ने पर गुणा करें।

## ➡️ Next: Azure Naming Conventions
