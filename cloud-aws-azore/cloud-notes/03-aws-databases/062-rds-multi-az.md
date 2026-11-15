# 62. RDS MULTI-AZ
# AWS: RDS Multi-AZ (instance deployment and Multi-AZ DB cluster)
# Azure: Zone-redundant High Availability (Flexible Server) / Azure SQL zone redundancy
# हिंदी में: RDS मल्टी-AZ यानी हाई अवेलेबिलिटी

---

## 🔵 Simple Definition (2 lines)
Multi-AZ keeps a standby copy of your database in another Availability Zone and fails over automatically if the primary dies.
हिंदी: मल्टी-AZ में दूसरे AZ में स्टैंडबाय कॉपी रहती है जो प्राइमरी फेल होने पर खुद चालू हो जाती है।

---

## 🔴 Why it Exists (2 lines)
A single DB instance is a single point of failure (hardware, AZ outage, maintenance).
Multi-AZ gives high availability, not extra read capacity (in the classic instance mode).

---

## 🟢 How it Works
```
        App --> endpoint: app-pg.xxxx.rds.amazonaws.com
                         |
              +----------+-----------+
          AZ-a: PRIMARY  --sync-->  AZ-b: STANDBY (not readable)
              X  primary fails
              -> DNS flips to standby (typically about 60-120 s, approximate)
  Multi-AZ DB cluster: 1 writer + 2 readable standbys, failover usually faster
```

---

## 💻 Code / Config Example
```bash
# Turn on Multi-AZ for an existing instance (AWS CLI v2)
aws rds modify-db-instance \
  --db-instance-identifier app-pg \
  --multi-az \
  --apply-immediately

# Test failover (reboots with failover)
aws rds reboot-db-instance \
  --db-instance-identifier app-pg \
  --force-failover
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| HA mode | Multi-AZ (sync standby) | Zone-redundant HA (sync standby in another zone) |
| Failover | Automatic, DNS endpoint stays same | Automatic, same server name |
| Standby readable? | No (instance); yes in Multi-AZ DB cluster | No |
| Pricing | Roughly 2x single-instance cost (approximate - check current docs) | Roughly 2x compute (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Thinking Multi-AZ scales reads.
✅ Correct: Use read replicas for reads; Multi-AZ is for availability.

❌ Mistake: App caches resolved DB IP forever.
✅ Correct: Respect DNS TTL and reconnect with retry logic in the pool.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does Multi-AZ protect against?
A1: Instance or AZ failure; it fails over automatically to the standby.

Q2: [Medium] Multi-AZ vs read replica?
A2: Multi-AZ = synchronous, HA, standby not readable. Read replica = asynchronous, scales reads, can be promoted manually.

Q3: [Hard] Your app errors for a minute during failover. How do you reduce impact?
A3: Connection pool with retries and short timeouts, use endpoint DNS, consider Multi-AZ DB cluster or RDS Proxy to preserve connections.

---

## ✅ Quick Checklist
□ Multi-AZ on for production
□ Failover tested (force-failover) in staging
□ App retries dropped connections

---

## ⚡ 1-Line Summary
Multi-AZ = synchronous standby in another AZ for automatic failover. | मल्टी-AZ = दूसरे AZ में सिंक्रोनस स्टैंडबाय, ऑटोमैटिक फेलओवर के लिए।

## ➡️ Next: RDS Read Replicas

---
