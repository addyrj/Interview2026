# 105. Disaster Recovery (RPO / RTO)
# हिंदी में: Disaster Recovery — बड़ी आपदा (region डाउन, डेटा मिटना, ransomware) के बाद सिस्टम और डेटा वापस लाने की योजना; RPO = कितना डेटा खो सकते हैं, RTO = कितनी देर में वापस चालू होना है

---

## 🔵 Simple Definition (English)
**Disaster Recovery (DR)** is the set of plans, processes and infrastructure to **restore systems and data after a major failure**: a region/data-center outage, accidental mass deletion, data corruption, ransomware, or a cloud account compromise. Two key targets:
- **RPO (Recovery Point Objective):** the **maximum acceptable data loss**, measured in time. "RPO = 5 min" means we may lose at most the last 5 minutes of data.
- **RTO (Recovery Time Objective):** the **maximum acceptable downtime** until service is restored. "RTO = 1 hour".
DR strategies range from **backup & restore** (cheap, slow) to **multi-site active-active** (expensive, near-zero RTO/RPO).

## 🔵 सरल परिभाषा (Hindi)
Disaster Recovery = बड़ी आपदा (पूरा region बंद, ग़लती से डेटा delete, ransomware) के बाद सिस्टम और डेटा वापस लाने की योजना।
RPO = ज़्यादा से ज़्यादा कितना डेटा (समय में) खो सकते हैं, जैसे आख़िरी 5 मिनट। RTO = ज़्यादा से ज़्यादा कितनी देर में सिस्टम वापस चलना चाहिए, जैसे 1 घंटा।

---

## 🔴 Problem it Solves
High availability (multi-AZ, replicas, failover) protects against **common** failures, but not:
- **Region-wide outages** (an entire AWS region degraded for hours).
- **Logical disasters:** a bad migration `DROP TABLE`, a buggy job deleting millions of rows. Replicas faithfully replicate the damage instantly.
- **Ransomware / malicious insider / compromised cloud credentials** wiping resources and backups.
- **Software bugs corrupting data** silently over days.

Without DR you may lose data permanently or be down for days, which can be **company-ending**. DR defines the targets, then builds and **regularly tests** the means to meet them.

## 🔴 यह क्यों बना? (Hindi)
Multi-AZ, replicas जैसी HA आम ख़राबियों से बचाती है, पर पूरा region डाउन, ग़लत migration से टेबल delete (replica भी तुरंत delete!), ransomware या bug से धीरे-धीरे बिगड़ता डेटा — इनसे नहीं।
बिना DR के डेटा हमेशा के लिए जा सकता है या कई दिन downtime — कंपनी ख़त्म। DR लक्ष्य तय करता है और उन्हें पूरा करने के तरीके बनाकर नियमित टेस्ट करता है।

---

## 🟢 How it Works — Step by Step

### RPO and RTO on a timeline

```
   last good backup/replication point        disaster            service restored
            │                                    💥                     ✅
 ───────────●────────────────────────────────────●──────────────────────●──────────► time
            │◄──────────── RPO (data lost) ──────►│◄──── RTO (downtime) ─►│
Lower RPO → more frequent backups / continuous replication
Lower RTO → more pre-provisioned standby infrastructure + automation
Both cost money: choose per system based on business impact.
```

### DR strategies (AWS's four classic tiers)

```
┌──────────────────────┬─────────────────────────────────────┬──────────────┬──────────────┬──────────┐
│ Strategy             │ What it means                       │ RPO          │ RTO          │ Cost     │
├──────────────────────┼─────────────────────────────────────┼──────────────┼──────────────┼──────────┤
│ Backup & restore     │ backups copied to another region;   │ hours        │ hours–days   │ $        │
│                      │ rebuild infra (IaC) + restore data  │ (backup freq)│              │          │
│ Pilot light          │ core data replicated live (DB       │ seconds–min  │ tens of min  │ $$       │
│                      │ replica); minimal infra off/small;  │              │ – hours      │          │
│                      │ scale up on disaster                │              │              │          │
│ Warm standby         │ scaled-down but RUNNING full copy   │ seconds–min  │ minutes      │ $$$      │
│                      │ in DR region; scale up + switch DNS │              │              │          │
│ Multi-site           │ full capacity in 2+ regions serving │ ~0 – seconds │ ~0 – minutes │ $$$$     │
│ active-active        │ traffic; route away from failed one │              │              │          │
└──────────────────────┴─────────────────────────────────────┴──────────────┴──────────────┴──────────┘
```

### Backups done right (3-2-1-1-0 rule)

```
3 copies of data, on 2 different media/services, 1 offsite (other region),
1 immutable/air-gapped (can't be deleted even by an admin — Object Lock / backup vault lock),
0 errors after restore verification (TEST RESTORES!)

DB: automated snapshots + continuous WAL/binlog archiving → POINT-IN-TIME RECOVERY (PITR)
    "restore to 13:59:00, one minute before the bad DELETE"
Object storage: versioning + cross-region replication + Object Lock
Separate AWS account for backups (blast radius: compromised prod account can't delete them)
```

### Classify systems (not everything needs the same DR)

```
Tier 0 (payments, orders, auth):      RPO ≤ 1 min, RTO ≤ 15–60 min → warm standby / active-active
Tier 1 (catalog, search, notifications): RPO ≤ 15 min, RTO ≤ 4 h → pilot light
Tier 2 (analytics, internal tools):   RPO 24 h, RTO 1–3 days → backup & restore
Business decides via impact analysis (revenue/min lost, regulatory obligations).
```

### DR plan components
```
- Inventory & dependencies (what must come back first: DNS, auth, DB, then services)
- Runbooks: step-by-step, automated where possible (IaC: Terraform for whole environment)
- Roles & communication: incident commander, status page, customer/regulator comms
- Data replication/backups config + verification
- DNS/traffic failover mechanism (Route 53 failover, Global Accelerator)
- Secrets/config/container images available in DR region (ECR replication!)
- REGULAR DR DRILLS (game days): actually fail over, measure real RTO/RPO
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर सिस्टम के लिए RPO (कितना डेटा खो सकते हैं) और RTO (कितना downtime) तय करो — पेमेंट के लिए सख़्त, analytics के लिए ढीला।
2. रणनीति चुनो: Backup & restore (सस्ता, धीमा) → Pilot light (DB replica तैयार) → Warm standby (छोटी copy चालू) → Active-active (दोनों पूरी चालू)।
3. Backups: 3 copies, 2 तरह की जगह, 1 दूसरे region में, 1 जिसे कोई delete न कर सके (Object Lock); और restore टेस्ट।
4. DB में PITR — ग़लत DELETE से एक मिनट पहले की स्थिति पर वापस जा सकते हो। Backups अलग AWS account में रखो।
5. Runbook, Terraform से पूरा environment, DR region में images/secrets, और नियमित DR drill करके असली RTO/RPO नापो।

---

## 🟡 Real World Example

**GitLab (Jan 2017)** — an engineer accidentally deleted the primary database directory during an incident. Of five backup/replication mechanisms, none worked properly (backups silently failing, snapshots not enabled). They recovered from a 6-hour-old staging copy and lost ~6 hours of data (RPO violated). They live-streamed the recovery, and it's the classic lesson: **untested backups are not backups**.

**OVHcloud Strasbourg fire (March 2021)** — a data center burned down. Customers without offsite backups lost data permanently, including some websites and businesses. Customers whose backups were in the same building lost both.

**Code Spaces (2014)** — attackers gained access to its AWS console and deleted EC2 instances, S3 buckets and backups in the same account. The company shut down within days. This is why backups belong in separate accounts with immutability.

**Banks in India** — RBI requires DR sites and periodic DR drills for critical banking systems, with defined RTO/RPO for core banking and payment systems.

## 🟡 Real Example Hindi में
2017 में GitLab का primary DB ग़लती से delete हुआ और पाँचों backup तरीके काम नहीं कर रहे थे — 6 घंटे का डेटा गया। सबक़: बिना टेस्ट किया backup, backup नहीं है।
2021 में OVH का डेटा सेंटर जल गया — जिनके backup उसी इमारत में थे, उनका सब गया। Code Spaces का AWS account हैक हुआ, backups भी उसी में थे — कंपनी बंद हो गई।

---

## 🟠 My Stack Example

### Postgres on AWS RDS — PITR + cross-region copies
```
RDS automated backups: retention 14–35 days → PITR to any second in window (RPO ≈ 5 min)
Cross-region automated backup replication (ap-south-1 → ap-southeast-1)
Aurora Global Database: storage-level replication to DR region (~1 s lag), managed failover (RTO minutes)
AWS Backup: central policies, vault lock (immutable), copy to a separate backup account
```
```bash
# Restore to just before a bad migration (new instance; then repoint app)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier prod-db --target-db-instance-identifier prod-db-restored \
  --restore-time 2026-10-18T13:59:00Z
```

### Self-managed Postgres on a VPS — wal-g / pgBackRest to S3
```bash
# continuous WAL archiving + nightly base backups to S3 (other region), encrypted
archive_command = 'wal-g wal-push %p'
wal-g backup-push $PGDATA                 # cron nightly
wal-g backup-fetch /restore LATEST        # restore + replay WAL to target time (recovery_target_time)
```

### S3 protection
```hcl
resource "aws_s3_bucket_versioning" "uploads" { bucket = aws_s3_bucket.uploads.id  versioning_configuration { status = "Enabled" } }
resource "aws_s3_bucket_object_lock_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id
  rule { default_retention { mode = "COMPLIANCE"  days = 30 } }     # nobody can delete for 30 days
}
# + replication rule to a bucket in another region and another account
```

### Infra as code = fast rebuild (RTO)
```
Terraform modules parameterized by region → `terraform apply -var region=ap-southeast-1`
ECR cross-region replication for Docker images; Secrets Manager multi-region secrets
Route 53 failover records + health checks (Topic 81)
```

### MongoDB / Redis
```
MongoDB Atlas: continuous cloud backup with PITR, multi-region clusters
Redis (cache): usually NO backup needed (rebuildable) — but queues/sessions in Redis: AOF + replicas,
or move critical state to a durable DB
```

### Restore drill script (monthly, automated)
```bash
#!/usr/bin/env bash
set -euo pipefail
LATEST=$(aws rds describe-db-snapshots --db-instance-identifier prod-db --snapshot-type automated \
  --query 'reverse(sort_by(DBSnapshots,&SnapshotCreateTime))[0].DBSnapshotIdentifier' --output text)
aws rds restore-db-instance-from-db-snapshot --db-instance-identifier drill-$(date +%s) --db-snapshot-identifier "$LATEST"
# wait, run integrity checks: row counts vs prod, recent orders present, app smoke tests → report RTO achieved
```

### Mobile/web considerations
```
- Status page on separate infra (not on the failed region)
- Mobile apps with remote config pointing to API base URL → can redirect to DR region if needed
- Offline-capable apps keep working briefly during regional failover
```

---

## ⚫ Interview Questions + Answers

**Q1: What are RPO and RTO?**
A1: RPO (Recovery Point Objective) is the maximum acceptable amount of data loss, measured as time between the last recoverable point and the disaster (RPO 5 minutes means losing at most 5 minutes of writes). It's driven by backup frequency and replication. RTO (Recovery Time Objective) is the maximum acceptable time to restore service after a disaster. It's driven by standby infrastructure, automation and runbooks. Both are business decisions, traded against cost.

**Q2: Describe the main DR strategies and their trade-offs.**
A2: Backup and restore: periodic backups copied offsite, with infrastructure rebuilt and data restored on disaster. Cheapest, but RPO of hours and RTO of hours to days. Pilot light: data continuously replicated to the DR region with minimal or off compute that's scaled up on disaster, giving low RPO and moderate RTO. Warm standby: a smaller fully functional environment running in DR, scaled up and switched over in minutes. Multi-site active-active: full capacity in multiple regions serving traffic, with near-zero RPO and RTO but highest cost and complexity (data consistency across regions).

**Q3: Why aren't database replicas enough for disaster recovery?**
A3: Replicas copy every change immediately, including mistakes, so a `DELETE`, a corrupting bug or ransomware encryption propagates to all replicas within seconds. They protect against hardware or zone failure, not logical corruption or malicious deletion. You need point-in-time backups (snapshots plus WAL or binlog archives), versioned and immutable storage, offsite copies in a separate account, and tested restores.

**Q4: How do you make backups ransomware- and insider-proof?**
A4: Keep backups immutable (S3 Object Lock in compliance mode, AWS Backup vault lock) with retention that can't be shortened, even by admins. Store them in a separate account or organization with restricted, MFA-protected access and different credentials. Copy them cross-region, encrypt them with separately controlled keys, monitor and alert on backup deletion attempts, and regularly test restores into an isolated environment.

**Q5: How would you design DR for a payments platform in India?**
A5: Classify it as Tier 0: RPO near zero, RTO of minutes. Run the primary in one Indian region with multi-AZ HA, and a warm standby or active-passive in a second Indian region (data localization rules require keeping data in India), with synchronous or near-synchronous replication for the ledger (or a distributed SQL database across regions). Use DNS or global-accelerator failover, IaC-defined environments, replicated secrets and images, immutable PITR backups in a separate account, reconciliation jobs after failover, and RBI-mandated periodic DR drills with documented RTO and RPO results.

---

## 🔷 Trade-offs
✅ Lower RPO/RTO: less data loss and downtime, regulatory compliance, customer trust.
❌ Cost & complexity rise sharply (standby infra, cross-region data transfer, multi-region consistency).
✅ Backup & restore: cheap — ❌ slow recovery, larger data loss.
Untested DR = false confidence.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Disaster recovery | Restoring after major failure | बड़ी आपदा के बाद वापसी |
| RPO | Max acceptable data loss (time) | कितना डेटा खो सकते हैं |
| RTO | Max acceptable downtime | कितनी देर में वापस चालू |
| PITR | Point-in-time recovery | किसी ख़ास समय पर वापसी |
| Pilot light | Minimal core running in DR | DR में न्यूनतम चालू ढाँचा |
| Warm standby | Scaled-down running copy | छोटी चालू copy |
| Active-active | All sites serve traffic | सारी जगहें चालू |
| Immutable backup | Can't be modified/deleted | न बदला/मिटाया जा सकने वाला backup |
| DR drill | Practice failover/restore | DR का अभ्यास |
| 3-2-1 rule | 3 copies, 2 media, 1 offsite | 3 copies, 2 माध्यम, 1 बाहर |

---

## ⚡ 3-Line Summary
**English:**
1. DR restores service after region outages, deletions, corruption or ransomware; define RPO (data loss) and RTO (downtime) per system tier.
2. Strategies: backup & restore → pilot light → warm standby → active-active (cost ↑, RPO/RTO ↓).
3. Replicas ≠ backups: use PITR, offsite immutable backups in a separate account, IaC, and regular tested drills.

**Hindi:**
1. DR = आपदा के बाद वापसी; हर सिस्टम के लिए RPO (डेटा नुक़सान) और RTO (downtime) तय करो।
2. रणनीतियाँ: backup & restore → pilot light → warm standby → active-active (ख़र्च बढ़ता, नुक़सान घटता)।
3. Replica backup नहीं है: PITR, अलग account में न मिटने वाले backups, IaC, और नियमित drill।

---

## ➡️ Next Topic Suggestion
**106. Multi-Region Architecture** — The ultimate DR and latency strategy: running across multiple regions. Next: active-passive vs active-active regions, data replication and conflicts, routing users, and when it's worth the cost.
