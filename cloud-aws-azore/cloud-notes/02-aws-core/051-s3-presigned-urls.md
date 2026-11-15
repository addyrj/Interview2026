# 51. S3 Pre-signed URLs
# AWS: S3 Pre-signed URLs
# Azure: Shared Access Signature (SAS) tokens
# हिंदी में: प्राइवेट फ़ाइल को सीमित समय के लिए डाउनलोड/अपलोड करने वाला टेम्परेरी लिंक

---

## 🔵 Simple Definition (2 lines)
A URL signed with your credentials that grants temporary access to one object for GET or PUT.
बिना बकेट पब्लिक किए, एक फ़ाइल के लिए कुछ मिनट का सुरक्षित लिंक।

---

## 🔴 Why it Exists (2 lines)
Users shouldn't get AWS keys, and routing big uploads through your API wastes bandwidth.
Pre-signed URLs let browsers upload/download directly to S3.

---

## 🟢 How it Works
```
Browser -> API (auth) -> API signs URL (expires in N sec)
Browser -> PUT/GET directly to S3 with the URL
Valid only while the signer's credentials are valid
(IAM role creds: max session lifetime; SigV4 max 7 days for IAM user)
```

---

## 💻 Code / Config Example
```javascript
// Node.js: @aws-sdk/s3-request-presigner (SDK v3)
import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({ region: "ap-south-1" });

// Upload URL: client must send the same Content-Type
export async function uploadUrl(userId) {
  const cmd = new PutObjectCommand({
    Bucket: "my-app-uploads-prod",
    Key: `users/${userId}/avatar.png`,
    ContentType: "image/png",
  });
  return getSignedUrl(s3, cmd, { expiresIn: 300 });  // 5 minutes
}

// Download URL
export const downloadUrl = (key) =>
  getSignedUrl(s3, new GetObjectCommand({ Bucket: "my-app-uploads-prod", Key: key }), { expiresIn: 60 });
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Mechanism | Pre-signed URL (SigV4) | SAS (account, service, or user-delegation) |
| Best practice | Short expiry, role creds | User-delegation SAS (Entra ID) |
| Revocation | Hard; rotate creds or deny in policy | Stored access policy or revoke delegation key |
| Pricing | free to generate | free to generate |

---

## ⚠️ Common Mistakes
❌ Mistake: Very long expiry or URL logged/shared.
✅ Correct: Seconds-to-minutes expiry; treat URL as a secret.

❌ Mistake: Signing with a role whose creds expire sooner than `expiresIn`.
✅ Correct: URL dies when signer's session dies; account for it.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Why use pre-signed URLs?
A1: Temporary private access without exposing credentials or making bucket public.

Q2: [Medium] How do you restrict upload size/type?
A2: Sign Content-Type for PUT; for size limits use pre-signed POST with a `content-length-range` condition.

Q3: [Hard] How to revoke an issued URL?
A3: Not individually; delete the object, change the key, or deny via bucket policy/revoke the signing role's sessions.

---

## ✅ Quick Checklist
□ Expiry as short as possible
□ Auth check before issuing
□ CORS configured on bucket for browser use
□ Signer has only needed permission

---

## ⚡ 1-Line Summary
Pre-signed URLs give time-limited direct S3 access without public buckets. | प्री-साइन्ड URL बिना पब्लिक किए सीमित समय का S3 एक्सेस देता है।

## ➡️ Next: S3 Encryption
