# 47. S3 Lifecycle Policies
# AWS: S3 Lifecycle configuration
# Azure: Blob Storage lifecycle management policy
# हिंदी में: समय के साथ डेटा को सस्ते क्लास में भेजना या अपने-आप डिलीट करना

---

## 🔵 Simple Definition (2 lines)
Rules that automatically transition objects to cheaper classes or expire them after N days.
नियम: "30 दिन बाद IA में, 365 दिन बाद डिलीट" — अपने-आप चलता है।

---

## 🔴 Why it Exists (2 lines)
Manual cleanup is forgotten and storage bills grow silently.
Lifecycle automates cost control and retention compliance.

---

## 🟢 How it Works
```
day 0   Standard
day 30  -> STANDARD_IA        (Transition)
day 90  -> GLACIER            (Transition)
day 365 -> deleted            (Expiration)
Also: noncurrent versions expire, incomplete multipart uploads aborted
Filter by prefix / tags / size
```

---

## 💻 Code / Config Example
```json
{
  "Rules": [
    {
      "ID": "logs-tiering",
      "Status": "Enabled",
      "Filter": { "Prefix": "logs/" },
      "Transitions": [
        { "Days": 30, "StorageClass": "STANDARD_IA" },
        { "Days": 90, "StorageClass": "GLACIER" }
      ],
      "Expiration": { "Days": 365 },
      "NoncurrentVersionExpiration": { "NoncurrentDays": 30 },
      "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 }
    }
  ]
}
```
```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-app-logs-prod --lifecycle-configuration file://lifecycle.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Lifecycle configuration (JSON/XML) | Lifecycle management policy (JSON) |
| Actions | Transition, Expire, abort MPU | tierToCool/Cold/Archive, delete |
| Filter | Prefix, tags, size | Prefix, blob index tags, blob types |
| Pricing | rule free; transition requests billed (approximate — check current docs) | policy free; operations billed (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Transition to IA before 30 days (rejected) or for objects under 128 KB (costly).
✅ Correct: Respect minimum days (30 for IA) and size.

❌ Mistake: Forgetting incomplete multipart uploads.
✅ Correct: Add AbortIncompleteMultipartUpload rule.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What can lifecycle do?
A1: Transition to other classes and expire current/noncurrent objects.

Q2: [Medium] How do you clean old versions?
A2: NoncurrentVersionExpiration (and ExpiredObjectDeleteMarker cleanup).

Q3: [Hard] Lifecycle vs Intelligent-Tiering?
A3: Lifecycle is time-based, predictable and free; Intelligent-Tiering reacts to actual access and charges a monitoring fee per object, best for unknown patterns.

---

## ✅ Quick Checklist
□ Rule per prefix (logs/, tmp/, backups/)
□ Noncurrent versions handled
□ Multipart cleanup enabled
□ Retention matches compliance

---

## ⚡ 1-Line Summary
Lifecycle rules move and delete data automatically to save money. | लाइफसाइकिल रूल्स डेटा को अपने-आप सस्ते क्लास में भेजते या हटाते हैं।

## ➡️ Next: S3 Replication
