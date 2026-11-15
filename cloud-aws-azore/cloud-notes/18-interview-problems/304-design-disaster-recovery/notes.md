# 304. Design Disaster Recovery
# AWS: AWS Backup + cross-region copy, S3 CRR, Aurora Global DB, Route 53, Elastic Disaster Recovery
# Azure: Azure Backup, Site Recovery, GRS/GZRS storage, geo-replication, Traffic Manager/Front Door
# हिंदी में: DR = पूरा रीजन खराब हो जाए तब भी RPO/RTO के भीतर सिस्टम वापस चालू करना

---

## 🔵 Simple Definition
A plan and automation to restore service in another region within an agreed RTO (time to recover) and RPO (data you can lose).
हिंदी: RTO मतलब कितनी देर में वापस, RPO मतलब कितना डेटा खो सकते हैं।

## 🔴 Why it Exists
Regional outages, ransomware, bad deploys and human deletion are not covered by Multi-AZ.

## 🟢 How it Works
```
Strategy      RTO         RPO        Cost
Backup/Restore hours      hours      $       (this folder: AWS Backup copy to DR region)
Pilot Light   tens of min minutes    $$      (DB replica running, app stopped)
Warm Standby  minutes     seconds    $$$     (scaled-down full stack)
Active-Active ~0          ~0         $$$$
Primary region --AWS Backup plan (daily, 35d)--> vault --copy--> DR region vault (+ S3 CRR)
Disaster: restore / promote replica -> Route 53 failover record flips
```

## 💻 Code / Config Example
`backup.tf` (AWS Backup plan with cross-region copy, tag-based selection, IAM role; provider ~> 5.x, not applied here) and `runbook.sh` (restore steps using AWS CLI v2 commands; syntax-checked only).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Backup | AWS Backup | Azure Backup (Recovery Services vault) |
| VM DR | Elastic Disaster Recovery | Site Recovery |
| Storage copy | S3 CRR | GRS / GZRS, object replication |
| DB | Aurora Global DB, RDS cross-region replica | Geo-replication, failover groups, Cosmos multi-region |
| DNS | Route 53 failover | Traffic Manager / Front Door |

## 💰 Cost / HA / Security
- Cost: choose tier from business RTO/RPO; cross-region transfer and standby compute are the cost drivers.
- HA: DR region IaC ready (Terraform) so infrastructure is rebuilt, not hand-made.
- Security: separate backup account/vault lock (Backup Vault Lock) against ransomware; KMS keys exist in DR region.

## ⚠️ Common Mistakes
❌ Backups never restored.
✅ Scheduled restore tests with measured RTO.

❌ Replicating to the same region/account.
✅ Cross-region, ideally cross-account copy.

## ⚫ Interview Q&A
Q1 [Easy]: Define RTO and RPO.
A1: RTO is the max acceptable downtime; RPO is the max acceptable data loss window.

Q2 [Medium]: Pilot light vs warm standby?
A2: Pilot light keeps only core data (DB replica) running; warm standby runs a scaled-down complete stack that can take traffic after scale-up.

Q3 [Hard]: Replication copied a corrupted/deleted record. How do you recover?
A3: Replication is not backup; use point-in-time recovery or versioned/object-locked backups in a separate account and restore to a new instance.

## ✅ Quick Checklist
□ RTO/RPO written per service
□ Cross-region and cross-account copies
□ Restore drill done and documented

## ⚡ 1-Line Summary
Pick RTO/RPO, replicate and back up across regions, rehearse failover. | RTO/RPO तय करें, दूसरे रीजन में कॉपी रखें, रिहर्सल करें।

## ➡️ Next: 305. Design Auto Scaling Setup
