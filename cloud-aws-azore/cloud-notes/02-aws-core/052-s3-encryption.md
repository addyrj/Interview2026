# 52. S3 Encryption
# AWS: SSE-S3, SSE-KMS, DSSE-KMS, SSE-C, client-side
# Azure: Storage Service Encryption (Microsoft-managed or customer-managed keys in Key Vault)
# हिंदी में: S3 में रखा डेटा एन्क्रिप्ट करना (at rest और in transit)

---

## 🔵 Simple Definition (2 lines)
S3 encrypts every new object at rest by default (SSE-S3); you can choose KMS keys for audit and control.
डेटा डिस्क पर एन्क्रिप्टेड रहता है; KMS से चाबी पर आपका नियंत्रण और ऑडिट मिलता है।

---

## 🔴 Why it Exists (2 lines)
Compliance (PCI, HIPAA, GDPR) and defence if storage media or access is compromised.
Key control lets you restrict and audit who can decrypt.

---

## 🟢 How it Works
```
SSE-S3   : AWS-managed keys (AES-256), default since Jan 2023
SSE-KMS  : KMS key; CloudTrail logs each use; key policy gates access
SSE-C    : you send key per request (AWS doesn't store it)
Client-side: you encrypt before upload
In transit: HTTPS (enforce with aws:SecureTransport deny)
Bucket Key reduces KMS request cost for SSE-KMS
```

---

## 💻 Code / Config Example
```bash
# Default bucket encryption with a KMS key + Bucket Keys
aws s3api put-bucket-encryption --bucket my-app-uploads-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:ap-south-1:111122223333:key/EXAMPLE-KEY-ID"
      },
      "BucketKeyEnabled": true
    }]
  }'

# Per-object
aws s3 cp secret.pdf s3://my-app-uploads-prod/ --sse aws:kms
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Default | SSE-S3 (AES-256) | Microsoft-managed keys (AES-256), always on |
| Own keys | SSE-KMS (CMK) | Customer-managed keys in Key Vault / Managed HSM |
| Per-request keys | SSE-C | Customer-provided keys (blob requests) |
| Pricing | SSE-S3 free; KMS per key + requests (approximate — check current docs) | Key Vault operations billed (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: SSE-KMS with high request volume and no Bucket Key (KMS throttling and cost).
✅ Correct: Enable Bucket Keys.

❌ Mistake: App role lacks `kms:Decrypt`/`kms:GenerateDataKey`.
✅ Correct: Grant KMS permissions in role AND key policy.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Is S3 encrypted by default?
A1: Yes, SSE-S3 for all new objects since Jan 2023.

Q2: [Medium] SSE-S3 vs SSE-KMS?
A2: KMS adds key-level access control, rotation options and CloudTrail audit, at extra cost and quota limits.

Q3: [Hard] Replicating SSE-KMS objects cross-region?
A3: Replication rule must opt in to KMS objects and specify the destination KMS key; role needs decrypt on source and encrypt on destination.

---

## ✅ Quick Checklist
□ Default encryption set
□ Bucket Keys on for KMS
□ TLS-only policy
□ Key policy and role permissions aligned

---

## ⚡ 1-Line Summary
S3 encrypts at rest by default; use KMS when you need key control and audit. | S3 डिफ़ॉल्ट एन्क्रिप्ट करता है; चाबी पर नियंत्रण चाहिए तो KMS।

## ➡️ Next: CloudFront — CDN
