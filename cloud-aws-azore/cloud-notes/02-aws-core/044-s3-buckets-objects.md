# 44. S3 Buckets + Objects
# AWS: S3 Buckets, Objects, Keys, Prefixes
# Azure: Storage Account, Container, Blob
# हिंदी में: बकेट (डिब्बा) और ऑब्जेक्ट (फ़ाइल) कैसे बनाते और इस्तेमाल करते हैं

---

## 🔵 Simple Definition (2 lines)
A bucket is a named container in one Region; an object is data + metadata identified by a key (max 5 TB; single PUT up to 5 GB).
बकेट = डिब्बा, ऑब्जेक्ट = उसमें रखी फ़ाइल, key = फ़ाइल का पूरा नाम/पाथ।

---

## 🔴 Why it Exists (2 lines)
You need a namespace and a security/billing boundary for stored data.
Buckets give per-bucket policies, region choice, logging and lifecycle.

---

## 🟢 How it Works
```
s3://my-app-uploads-prod/users/42/avatar.png
     |__ bucket __________|_____ key ________|
                           prefix = users/42/
Large file (>100 MB recommended): multipart upload (5 MiB-5 GiB parts, up to 10,000 parts)
```

---

## 💻 Code / Config Example
```bash
# AWS CLI v2
aws s3 mb s3://my-app-uploads-prod --region ap-south-1     # make bucket
aws s3 cp ./avatar.png s3://my-app-uploads-prod/users/42/avatar.png
aws s3 ls s3://my-app-uploads-prod/users/ --recursive
aws s3 sync ./dist s3://my-app-uploads-prod/web/ --delete  # deploy static build (GitHub Actions)
aws s3 rm s3://my-app-uploads-prod/users/42/avatar.png

# Metadata and content-type
aws s3api put-object --bucket my-app-uploads-prod --key a.json \
  --body a.json --content-type application/json --cache-control "max-age=300"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Top level | Bucket (global unique name) | Storage account (global unique name) |
| Grouping | Prefix in key | Container (+ virtual dirs; ADLS Gen2 has real dirs) |
| CLI sync | `aws s3 sync` | `az storage blob sync` / AzCopy |
| Pricing | storage + requests + egress (approximate — check current docs) | same model (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Uppercase or underscores in bucket names, or hot-spotting naming assumptions.
✅ Correct: Lowercase, 3-63 chars, DNS-safe; S3 scales per prefix automatically.

❌ Mistake: Forgetting `Content-Type` so browsers download instead of render.
✅ Correct: Set ContentType on upload.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Max object size?
A1: 5 TB; a single PUT is limited to 5 GB, so use multipart above that.

Q2: [Medium] How do you delete a bucket with data?
A2: Empty it first (and all versions/delete markers if versioned), then delete; or `aws s3 rb --force`.

Q3: [Hard] How do you speed uploads from distant users?
A3: S3 Transfer Acceleration, multipart with parallel parts, or upload to a nearer Region and replicate.

---

## ✅ Quick Checklist
□ Naming convention (app-env-purpose)
□ Region close to users/compute
□ Content-Type and Cache-Control set
□ Multipart for large files

---

## ⚡ 1-Line Summary
Bucket holds objects; each object is addressed by its key. | बकेट ऑब्जेक्ट रखता है और हर ऑब्जेक्ट key से पहचाना जाता है।

## ➡️ Next: S3 Storage Classes
