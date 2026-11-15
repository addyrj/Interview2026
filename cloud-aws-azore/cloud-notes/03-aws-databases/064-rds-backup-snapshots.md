# 64. RDS BACKUP + SNAPSHOTS
# AWS: RDS automated backups, manual snapshots, point-in-time restore (PITR)
# Azure: Automated backups + PITR (Flexible Server); long-term retention
# हिंदी में: RDS बैकअप और स्नैपशॉट

---

## 🔵 Simple Definition (2 lines)
Automated backups take a daily snapshot plus transaction logs so you can restore to any second in the retention window; manual snapshots are kept until you delete them.
हिंदी: ऑटोमैटिक बैकअप से रिटेंशन विंडो में किसी भी समय पर रिस्टोर हो सकता है; मैन्युअल स्नैपशॉट खुद डिलीट करने तक रहते हैं।

---

## 🔴 Why it Exists (2 lines)
Bad migrations, `DELETE` without `WHERE` and corruption happen.
Backups give a way back; restore always creates a NEW instance.

---

## 🟢 How it Works
```
Daily backup window --> storage snapshot
        + transaction logs (about every 5 min) --> PITR to any second
Retention: 1-35 days (0 disables automated backups)
Manual snapshot: independent, survives instance deletion
Restore --> NEW instance with NEW endpoint (point app to it)
```

---

## 💻 Code / Config Example
```bash
# Manual snapshot before a risky migration (AWS CLI v2)
aws rds create-db-snapshot \
  --db-instance-identifier app-pg \
  --db-snapshot-identifier app-pg-pre-migration

# Point-in-time restore to a new instance
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier app-pg \
  --target-db-instance-identifier app-pg-restored \
  --restore-time 2026-11-09T10:15:00Z

# Change retention
aws rds modify-db-instance --db-instance-identifier app-pg \
  --backup-retention-period 14 --apply-immediately
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Automated backup | 1-35 days | Typically 7-35 days (Flexible Server) |
| PITR | Yes, new instance | Yes, new server |
| Manual snapshot | Yes (shareable, copyable cross-region) | Long-term retention / on-demand backup (varies by service) |
| Pricing | Free up to DB size, extra storage billed (approximate - check current docs) | Included up to storage size, extra billed (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming restore overwrites the existing DB.
✅ Correct: It creates a new instance; update the connection string or rename.

❌ Mistake: Never testing a restore.
✅ Correct: Run a scheduled restore drill and time it (RTO).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Automated backup vs manual snapshot?
A1: Automated is scheduled with PITR and expires; manual persists until deleted.

Q2: [Medium] A dev dropped a table 10 minutes ago. What do you do?
A2: PITR to a time just before, into a new instance, then copy the table back.

Q3: [Hard] Design DR for RDS with RPO of minutes in another Region.
A3: Cross-region read replica or cross-region automated backup replication, plus a runbook to promote/restore and flip DNS; test regularly.

---

## ✅ Quick Checklist
□ Retention at least 7 days in prod
□ Snapshot before every migration
□ Restore tested and timed

---

## ⚡ 1-Line Summary
Backups + logs give PITR; restores always make a new instance. | बैकअप और लॉग से PITR मिलता है; रिस्टोर हमेशा नया इंस्टेंस बनाता है।

## ➡️ Next: RDS Parameter Groups

---
