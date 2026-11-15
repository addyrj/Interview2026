# 46. S3 Versioning
# AWS: S3 Versioning (+ MFA Delete)
# Azure: Blob versioning / soft delete
# हिंदी में: हर बदलाव का पुराना वर्ज़न सुरक्षित रखना

---

## 🔵 Simple Definition (2 lines)
With versioning on, every overwrite creates a new version ID and a delete only adds a delete marker.
गलती से ओवरराइट या डिलीट हो जाए तो पुराना वर्ज़न वापस मिल सकता है।

---

## 🔴 Why it Exists (2 lines)
Accidental deletes, bad deploys and ransomware can destroy data in an unversioned bucket.
Versioning gives point-in-time recovery of individual objects.

---

## 🟢 How it Works
```
PUT a.txt -> v1
PUT a.txt -> v2 (current)
DELETE a.txt -> delete marker (current); v1, v2 still stored
DELETE a.txt?versionId=v2 -> permanent delete of that version
States: unversioned -> enabled <-> suspended (cannot go back to unversioned)
```

---

## 💻 Code / Config Example
```bash
aws s3api put-bucket-versioning --bucket my-app-uploads-prod \
  --versioning-configuration Status=Enabled

aws s3api list-object-versions --bucket my-app-uploads-prod --prefix a.txt

# Restore: copy an old version over the current key
aws s3api copy-object --bucket my-app-uploads-prod --key a.txt \
  --copy-source "my-app-uploads-prod/a.txt?versionId=<OLD_VERSION_ID>"

# Remove a delete marker to "undelete"
aws s3api delete-object --bucket my-app-uploads-prod --key a.txt \
  --version-id "<DELETE_MARKER_VERSION_ID>"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Feature | Bucket versioning | Blob versioning (+ soft delete for blobs/containers) |
| Delete protection | MFA Delete (root only) | Immutability policies, resource locks |
| Needed by | Replication, Object Lock | Object replication |
| Pricing | every version billed as storage (approximate — check current docs) | same idea (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Enabling versioning with no lifecycle rule, so old versions pile up forever.
✅ Correct: Add `NoncurrentVersionExpiration` rule.

❌ Mistake: Thinking suspending versioning deletes old versions.
✅ Correct: Existing versions stay (and are billed).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What happens on delete in a versioned bucket?
A1: A delete marker becomes the current version; data remains recoverable.

Q2: [Medium] Can you disable versioning?
A2: Only suspend it; you cannot return to the unversioned state.

Q3: [Hard] How do you protect against admin-level deletion?
A3: S3 Object Lock (needs versioning) in compliance/governance mode, plus MFA Delete and restrictive IAM/SCP.

---

## ✅ Quick Checklist
□ Versioning enabled on critical buckets
□ Noncurrent version expiry rule
□ Know how to remove delete marker
□ Object Lock if compliance needs it

---

## ⚡ 1-Line Summary
Versioning keeps every object revision so mistakes are reversible. | वर्ज़निंग हर बदलाव सहेजती है ताकि गलती वापस ठीक हो सके।

## ➡️ Next: S3 Lifecycle Policies
