# 48. S3 Replication
# AWS: S3 Replication (CRR / SRR)
# Azure: Blob Object Replication (+ GRS/GZRS redundancy)
# हिंदी में: डेटा की कॉपी दूसरे बकेट/रीजन में अपने-आप भेजना

---

## 🔵 Simple Definition (2 lines)
Replication asynchronously copies new objects from a source bucket to a destination bucket in the same (SRR) or another Region (CRR).
नया ऑब्जेक्ट आते ही उसकी कॉपी दूसरे बकेट में अपने-आप चली जाती है।

---

## 🔴 Why it Exists (2 lines)
Disaster recovery, lower latency in another Region, compliance copies, or log aggregation into one account.
Same-Region copies protect against account-level mistakes.

---

## 🟢 How it Works
```
Source bucket (versioning ON) --IAM role--> Destination bucket (versioning ON)
  new objects only (use Batch Replication for existing)
  async, usually seconds-minutes (S3 RTC: 99.99% in 15 min, extra cost)
  delete markers: optional; permanent deletes are NOT replicated
```

---

## 💻 Code / Config Example
```json
{
  "Role": "arn:aws:iam::111122223333:role/s3-replication-role",
  "Rules": [
    {
      "ID": "crr-all",
      "Status": "Enabled",
      "Priority": 1,
      "Filter": { "Prefix": "" },
      "DeleteMarkerReplication": { "Status": "Disabled" },
      "Destination": {
        "Bucket": "arn:aws:s3:::my-app-uploads-dr",
        "StorageClass": "STANDARD_IA"
      }
    }
  ]
}
```
```bash
aws s3api put-bucket-replication --bucket my-app-uploads-prod \
  --replication-configuration file://replication.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Feature | CRR / SRR rules | Object replication policy |
| Prerequisite | Versioning both buckets | Versioning + change feed |
| Redundancy alt. | N/A (use CRR) | GRS / GZRS at account level |
| Pricing | storage + inter-region transfer + requests (approximate — check current docs) | similar (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Expecting existing objects to replicate.
✅ Correct: Only new objects; use S3 Batch Replication for old ones.

❌ Mistake: Versioning off on source or destination.
✅ Correct: Enable on both; role needs read on source and replicate permissions on destination.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] CRR vs SRR?
A1: CRR copies across Regions (DR, latency); SRR within the same Region (log aggregation, separate account).

Q2: [Medium] Is replication a backup?
A2: Not fully; corruption and delete markers can propagate. Combine with versioning and Object Lock.

Q3: [Hard] How do you guarantee a replication SLA?
A3: Enable S3 Replication Time Control (15-minute target with metrics/events) and monitor ReplicationLatency.

---

## ✅ Quick Checklist
□ Versioning on both buckets
□ IAM replication role correct
□ Destination KMS key handled if SSE-KMS
□ Existing data via Batch Replication

---

## ⚡ 1-Line Summary
Replication keeps a live copy of your bucket elsewhere for DR and compliance. | रेप्लिकेशन आपके बकेट की लाइव कॉपी दूसरी जगह रखता है।

## ➡️ Next: S3 Bucket Policies
