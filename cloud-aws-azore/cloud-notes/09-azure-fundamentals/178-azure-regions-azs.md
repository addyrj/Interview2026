# 178. Azure Regions + AZs
# AWS: Regions + Availability Zones
# Azure: Regions + Availability Zones + paired regions
# हिंदी में: Azure के Regions और Availability Zones

---

## 🔵 Simple Definition
A region is a geographic set of datacenters; an Availability Zone is a physically separate datacenter group inside a region with independent power, cooling and network.
हिंदी: Region भौगोलिक इलाका है और AZ उसके अंदर अलग-अलग datacenter हैं ताकि एक fail हो तो दूसरा चले।

---

## 🔴 Why it Exists
Latency, data residency and fault tolerance.
Spreading across zones survives a datacenter outage; paired regions help with disaster recovery.

---

## 🟢 How it Works
```
Region: Central India (Pune) | South India (Chennai) | West India (Mumbai)
  Zone 1   Zone 2   Zone 3     (not every region has zones)
Zone-redundant service: replicas across zones (e.g. ZRS storage)
Zonal service: you pick a zone for a VM
Paired region: cross-region DR for some services
```

---

## 💻 Code / Config Example
```bash
az account list-locations -o table                       # region names
az vm list-skus --location centralindia --zone -o table  # SKUs and zones available (output is large)

# create VM pinned to zone 1
az vm create -g rg-demo -n vm1 --image Ubuntu2204 --zone 1 --location centralindia \
  --generate-ssh-keys
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Region name | ap-south-1 (Mumbai) | centralindia / southindia / westindia |
| AZs | 3+ per region (names mapped per account) | Up to 3 zones in zone-enabled regions (logical mapping per subscription) |
| DR | Pick any second region | Paired regions plus any region |
| Pricing | Varies by region (approximate — check current docs) | Varies by region (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming every Azure region supports zones.
✅ Correct: Check zone support before designing HA.

❌ Mistake: Choosing a region only for price, ignoring latency and data residency.
✅ Correct: Pick near users and compliant with laws; check service availability.

---

## ⚫ Interview Q&A
Q1: [Easy] What is an AZ?
A1: An isolated datacenter location within a region.

Q2: [Medium] Zonal vs zone-redundant?
A2: Zonal pins to one zone (you handle replication); zone-redundant is replicated automatically by the service.

Q3: [Hard] Design for a regional outage.
A3: Multi-region active-passive or active-active with Front Door/Traffic Manager, geo-replicated data (GRS, Cosmos multi-region), tested failover and RPO/RTO targets.

---

## ✅ Quick Checklist
□ Region near users, compliant
□ Zones used for production
□ DR region chosen and tested

---

## ⚡ 1-Line Summary
Spread across zones for HA and regions for DR | HA के लिए zones और DR के लिए regions में फैलाएँ।

## ➡️ Next: 179. Azure Resource Groups
