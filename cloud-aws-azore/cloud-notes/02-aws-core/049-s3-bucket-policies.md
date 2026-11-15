# 49. S3 Bucket Policies
# AWS: S3 Bucket Policy (resource-based IAM policy)
# Azure: Azure RBAC on storage + stored access policies / network rules
# हिंदी में: बकेट पर लगने वाला एक्सेस नियम (कौन, क्या कर सकता है)

---

## 🔵 Simple Definition (2 lines)
A JSON resource policy attached to a bucket that allows or denies principals specific actions, with optional conditions.
बकेट पॉलिसी = JSON नियम जो तय करता है किसे इस बकेट पर कौन-सा काम करने देना है।

---

## 🔴 Why it Exists (2 lines)
IAM identity policies cannot easily grant cross-account or service (CloudFront, CloudTrail) access or enforce rules like HTTPS-only.
A bucket policy centralises rules at the resource.

---

## 🟢 How it Works
```
Request -> evaluate: explicit Deny? -> yes: DENIED
                    -> Allow in IAM or bucket policy? (same account: either is enough;
                       cross-account: BOTH must allow)
                    -> otherwise implicit deny
Max policy size: 20 KB
```

---

## 💻 Code / Config Example
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": ["arn:aws:s3:::my-app-uploads-prod", "arn:aws:s3:::my-app-uploads-prod/*"],
      "Condition": { "Bool": { "aws:SecureTransport": "false" } }
    },
    {
      "Sid": "AllowAppRoleReadWrite",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::111122223333:role/api-task-role" },
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-app-uploads-prod/*"
    }
  ]
}
```
```bash
aws s3api put-bucket-policy --bucket my-app-uploads-prod --policy file://policy.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Resource policy | Bucket policy | N/A (closest: RBAC role assignment on account/container) |
| Delegated URL | Pre-signed URL | SAS + stored access policy |
| Network limit | aws:SourceVpce condition | Storage firewall / private endpoint |
| Pricing | free | free |

---

## ⚠️ Common Mistakes
❌ Mistake: `"Principal": "*"` with Allow on the whole bucket.
✅ Correct: Name exact roles; keep Block Public Access on.

❌ Mistake: Using the bucket ARN for object actions (`s3:GetObject`).
✅ Correct: Object actions need `bucket/*`; bucket actions (ListBucket) need the bucket ARN.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Bucket policy vs IAM policy?
A1: Bucket policy is attached to the resource and can name other accounts; IAM policy is attached to an identity.

Q2: [Medium] How to force HTTPS?
A2: Deny when `aws:SecureTransport` is false.

Q3: [Hard] Cross-account access needs what?
A3: The bucket policy must allow the other account's principal AND that account's IAM policy must allow the action.

---

## ✅ Quick Checklist
□ Least privilege principals/actions
□ Bucket vs object ARN correct
□ Deny non-TLS
□ Validate with IAM Access Analyzer

---

## ⚡ 1-Line Summary
A bucket policy is a resource-level JSON rulebook for who may do what. | बकेट पॉलिसी बताती है कौन क्या कर सकता है।

## ➡️ Next: S3 ACL + Public Access Block
