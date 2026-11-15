---

# 10. Disaster Recovery Basics
# AWS: AWS Backup, Elastic Disaster Recovery, cross-region replication
# Azure: Azure Backup, Azure Site Recovery, geo-redundant storage
# हिंदी में: डिज़ास्टर रिकवरी = बड़ी आपदा के बाद सिस्टम और डेटा वापस लाना

---

## 🔵 Simple Definition (2 lines)
Disaster recovery (DR) is the plan and tooling to restore systems and data after a major outage such as a region failure, ransomware or human error.
हिंदी: पूरा रीजन गिर जाए या डेटा खराब हो जाए तो सर्विस दोबारा चालू करने की योजना।

---

## 🔴 Why it Exists (2 lines)
HA covers small failures, not region loss, corruption or accidental deletion.
DR gives copies in another place and a rehearsed process.

---

## 🟢 How it Works
```
Strategy (cheap/slow -> costly/fast):
1 Backup & Restore   : backups copied to another region; rebuild on disaster
2 Pilot Light        : core (DB replica) running, rest off; scale up on event
3 Warm Standby       : scaled-down full copy always running
4 Multi-site Active-Active : full capacity in 2 regions

Region A (primary) ==replicate==> Region B (DR)
```

---

## 💻 Code / Config Example
```bash
# AWS: copy an RDS snapshot to another region (placeholders in <>)
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:ap-south-1:123456789012:snapshot:prod-snap \
  --target-db-snapshot-identifier prod-snap-dr \
  --source-region ap-south-1 --region ap-southeast-1

# Azure: create a geo-redundant storage account (GRS replicates to paired region)
az storage account create --name drstorage12345 --resource-group demo-rg \
  --location centralindia --sku Standard_GRS
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Backup service | AWS Backup | Azure Backup |
| VM DR | Elastic Disaster Recovery | Azure Site Recovery |
| Storage geo copy | S3 Cross-Region Replication | GRS / RA-GRS |
| Pricing | Pay for storage + replication + transfer (check docs) | Same model (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Having backups but never testing a restore.
✅ Correct: Run scheduled restore drills and time them.

❌ Mistake: Backups in the same account/region as production.
✅ Correct: Copy to another region and a separate account with restricted delete.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is DR?
A1: Process to recover IT systems after a disaster.

Q2: [Medium] Name the four AWS DR strategies.
A2: Backup and restore, pilot light, warm standby, multi-site active-active.

Q3: [Hard] How choose a strategy?
A3: From business RTO/RPO and budget: minutes-level RTO/RPO pushes toward warm standby or active-active; hours-level tolerates backup and restore.

---

## ✅ Quick Checklist
□ RTO and RPO defined per system
□ Cross-region copies of data
□ Restore tested and runbook written

---

## ⚡ 1-Line Summary
DR = tested copies plus a plan to recover elsewhere | DR = दूसरी जगह टेस्ट की हुई कॉपी और रिकवरी प्लान।

## ➡️ Next: 11. RPO + RTO

---
