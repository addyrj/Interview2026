# 43. S3 — Complete Guide
# AWS: Amazon S3 (Simple Storage Service)
# Azure: Azure Blob Storage
# हिंदी में: असीमित, टिकाऊ ऑब्जेक्ट स्टोरेज (फ़ाइलें, इमेज, बैकअप)

---

## 🔵 Simple Definition (2 lines)
S3 stores objects (file + metadata) in buckets, accessed over HTTPS by key, with very high durability (designed for 11 nines).
S3 = इंटरनेट पर फ़ाइलें रखने की जगह; हर फ़ाइल एक "object" और उसका नाम "key"।

---

## 🔴 Why it Exists (2 lines)
Servers' local disks are lost with the server and don't scale; apps need shared, durable, cheap storage.
S3 offloads uploads, static sites, logs, backups and data lakes from your VPS/containers.

---

## 🟢 How it Works
```
Bucket (globally unique name, one Region)
  |- key: uploads/2026/avatar.png  -> object (up to 5 TB)
  |- flat namespace ("folders" are just key prefixes)
Access: IAM / bucket policy / pre-signed URL
Add-ons: versioning, lifecycle, replication, encryption, events
```

---

## 💻 Code / Config Example
```javascript
// Node.js: AWS SDK v3 (@aws-sdk/client-s3)
import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";

const s3 = new S3Client({ region: "ap-south-1" });   // creds from IAM role/env

await s3.send(new PutObjectCommand({
  Bucket: "my-app-uploads-prod",
  Key: "uploads/hello.txt",
  Body: "hello s3",
  ContentType: "text/plain",
}));

const res = await s3.send(new GetObjectCommand({
  Bucket: "my-app-uploads-prod", Key: "uploads/hello.txt",
}));
console.log(await res.Body.transformToString());
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | S3 bucket | Storage account + container |
| Unit | Object (key) | Blob |
| Tiers | Standard ... Glacier Deep Archive | Hot, Cool, Cold, Archive |
| Pricing | per GB-month + requests + egress (approximate — check current docs) | per GB-month + operations + egress (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Treating S3 like a file system (rename/append in place).
✅ Correct: Objects are immutable; overwrite whole object or use multipart upload.

❌ Mistake: Public bucket for user uploads.
✅ Correct: Keep private; use pre-signed URLs or CloudFront OAC.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Are S3 bucket names global?
A1: Yes, unique across all AWS accounts in a partition; the data lives in one Region.

Q2: [Medium] Does S3 have folders?
A2: No, flat key space; the console shows prefixes ending with `/` as folders.

Q3: [Hard] What is S3's consistency model?
A3: Strong read-after-write consistency for PUT/DELETE and LIST (since Dec 2020).

---

## ✅ Quick Checklist
□ Block Public Access on
□ Encryption + versioning decided
□ IAM role (not keys) for the app
□ Lifecycle rule for old data

---

## ⚡ 1-Line Summary
S3 is durable, scalable object storage accessed by key over HTTPS. | S3 टिकाऊ और असीमित ऑब्जेक्ट स्टोरेज है जिसे key से एक्सेस करते हैं।

## ➡️ Next: S3 Buckets + Objects
