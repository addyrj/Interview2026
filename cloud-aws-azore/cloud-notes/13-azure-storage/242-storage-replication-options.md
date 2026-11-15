---

# 242. Storage Replication Options
# AWS: S3 storage durability, Cross-Region Replication (CRR) / Same-Region Replication (SRR)
# Azure: LRS, ZRS, GRS, RA-GRS, GZRS, RA-GZRS
# हिंदी में: डेटा की कितनी कॉपी और कहाँ रखनी है, यह replication तय करता है

---

## 🔵 Simple Definition (2 lines)
Replication decides how many copies of your data exist and where (one datacenter, multiple zones, or another region).
Replication तय करता है कि डेटा की कॉपियाँ कहाँ-कहाँ रहेंगी, ताकि फेल होने पर भी डेटा बचा रहे।

---

## 🔴 Why it Exists (2 lines)
Disks, racks, zones and even whole regions can fail.
Higher redundancy gives better durability/availability but costs more.

---

## 🟢 How it Works
```
LRS   : 3 copies in 1 datacenter                 (cheapest)
ZRS   : 3 copies across 3 availability zones     (survives zone loss)
GRS   : LRS in primary + LRS in paired region    (survives region loss, async)
GZRS  : ZRS in primary + LRS in paired region
RA-*  : same as GRS/GZRS + READ access to secondary endpoint (acct-secondary.blob...)
Failover: GRS secondary is writable only after account failover.
```

---

## 💻 Code / Config Example
```bash
# Create account with geo-zone-redundant storage
az storage account create -n mystorageacct123 -g rg-demo -l centralindia \
  --sku Standard_RAGZRS --kind StorageV2

# Change replication later (some conversions need a support request / migration)
az storage account update -n mystorageacct123 -g rg-demo --sku Standard_GRS

# AWS equivalent: S3 CRR needs versioning + replication config
# aws s3api put-bucket-replication --bucket src --replication-configuration file://repl.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Within region | S3 stores across >=3 AZs by default (Standard) | Choose LRS or ZRS |
| Cross-region | CRR rule, per bucket, opt-in | GRS/GZRS, whole account, paired region |
| Read secondary | Read from destination bucket | RA-GRS / RA-GZRS endpoint |
| Pricing | Replication + inter-region transfer (approximate - check current docs) | Cost rises LRS < ZRS < GRS < GZRS (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using LRS for production user uploads.
✅ Correct: Use ZRS minimum; GZRS/RA-GZRS for critical data.

❌ Mistake: Assuming GRS gives instant failover with zero data loss.
✅ Correct: Geo-replication is asynchronous (non-zero RPO); failover is a manual or Microsoft-initiated action.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] LRS vs ZRS?
A1: LRS keeps copies in one datacenter; ZRS spreads them across availability zones.

Q2: [Medium] What does RA-GRS add?
A2: Read-only access to the secondary region endpoint at any time, useful for read availability during primary outage.

Q3: [Hard] Is S3 Standard comparable to ZRS or GRS?
A3: S3 Standard stores data across multiple AZs in one region, so it is closest to ZRS; cross-region needs explicit CRR, similar to GRS.

---

## ✅ Quick Checklist
□ Chose redundancy from RPO/RTO requirement
□ Production data at least ZRS
□ Failover procedure documented and tested

---

## ⚡ 1-Line Summary
Pick LRS/ZRS/GRS/GZRS by how much failure you must survive | कितनी विफलता झेलनी है, उसी हिसाब से replication चुनें।

## ➡️ Next: 243. Azure Service Bus

---
