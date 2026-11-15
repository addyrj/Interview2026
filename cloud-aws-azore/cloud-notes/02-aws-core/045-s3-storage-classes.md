# 45. S3 Storage Classes
# AWS: S3 Standard, Intelligent-Tiering, Standard-IA, One Zone-IA, Glacier tiers
# Azure: Blob access tiers (Hot, Cool, Cold, Archive)
# हिंदी में: डेटा कितनी बार इस्तेमाल होता है उसके हिसाब से सस्ता/महँगा स्टोरेज

---

## 🔵 Simple Definition (2 lines)
Storage classes trade storage price against retrieval cost, latency and minimum duration.
बार-बार इस्तेमाल होने वाला डेटा Standard में, पुराना डेटा सस्ते Glacier में रखो।

---

## 🔴 Why it Exists (2 lines)
Most data gets cold over time; paying Standard prices for old logs and backups wastes money.
Classes let you cut cost 50-90% for rarely accessed data.

---

## 🟢 How it Works
```
Hot ----------------------------------------------> Cold
Standard | Intelligent-Tiering | Standard-IA | One Zone-IA
        | Glacier Instant | Glacier Flexible | Glacier Deep Archive
Cheaper storage <-> higher retrieval cost / slower / min. storage days
IA classes: min 30 days & 128 KB billing size; Glacier Flexible 90 d; Deep Archive 180 d
(approximate - check current docs)
```

---

## 💻 Code / Config Example
```bash
# Upload straight into a class
aws s3 cp backup.tar.gz s3://my-backups-prod/db/ --storage-class STANDARD_IA

# Change class of an existing object by copying onto itself
aws s3 cp s3://my-backups-prod/db/backup.tar.gz s3://my-backups-prod/db/backup.tar.gz \
  --storage-class GLACIER

# Restore an archived (Glacier Flexible) object for 7 days, Standard tier
aws s3api restore-object --bucket my-backups-prod --key db/backup.tar.gz \
  --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Standard"}}'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Hot | Standard | Hot |
| Infrequent | Standard-IA / One Zone-IA | Cool / Cold |
| Auto-tier | Intelligent-Tiering | Lifecycle policy (no direct auto equivalent) |
| Archive | Glacier Flexible / Deep Archive | Archive (offline, rehydrate needed) |
| Pricing | varies by class (approximate — check current docs) | varies by tier (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Moving tiny or short-lived objects to IA/Glacier.
✅ Correct: Min size/duration charges apply; keep small, hot objects in Standard.

❌ Mistake: Using One Zone-IA for irreplaceable data.
✅ Correct: It stores in one AZ only; use only for re-creatable data.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which class for unknown access patterns?
A1: Intelligent-Tiering; it moves objects between tiers automatically (small monitoring fee per object).

Q2: [Medium] Difference between Glacier Instant and Flexible Retrieval?
A2: Instant gives millisecond access; Flexible needs a restore job (minutes to hours).

Q3: [Hard] How to cut cost for 5 TB of logs read mostly in first 7 days?
A3: Standard for 30 days, lifecycle to Standard-IA/Glacier, then expire per compliance; avoid tiny-object overhead by batching logs.

---

## ✅ Quick Checklist
□ Access pattern analysed
□ Min duration/size charges understood
□ Lifecycle rule automates transitions
□ Critical data not in One Zone

---

## ⚡ 1-Line Summary
Pick the class that matches how often data is read. | डेटा कितना पढ़ा जाता है, उसी हिसाब से स्टोरेज क्लास चुनो।

## ➡️ Next: S3 Versioning
