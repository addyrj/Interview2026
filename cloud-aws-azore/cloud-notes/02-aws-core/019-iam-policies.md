---

# 19. IAM Policies
# AWS: Identity-based, resource-based policies, SCPs, permission boundaries
# Azure: Role definitions + Azure Policy (different purpose)
# हिंदी में: पॉलिसी = JSON दस्तावेज़ जो बताता है क्या allow और क्या deny

---

## 🔵 Simple Definition (2 lines)
An IAM policy is a JSON document of statements (Effect, Action, Resource, optional Condition) defining permissions.
हिंदी: पॉलिसी JSON होती है जिसमें लिखा होता है कि कौन-सा एक्शन किस रिसोर्स पर allow या deny है।

---

## 🔴 Why it Exists (2 lines)
Permissions must be precise, reviewable and versioned as code.
Policies enable least privilege down to a single object prefix.

---

## 🟢 How it Works
```
Types:
 Identity-based : attached to user/group/role
 Resource-based : on S3 bucket, SQS, KMS key... (has Principal)
 Permission boundary : max permissions an identity may get
 SCP (Organizations): max permissions for accounts
 Session policy : limits an assumed-role session
Statement = Effect + Action + Resource (+ Condition)
Managed (AWS or customer) vs inline policies
```

---

## 💻 Code / Config Example
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadWriteOneBucketPrefix",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-app-bucket/uploads/*"
    },
    {
      "Sid": "ListOnlyThatPrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-app-bucket",
      "Condition": { "StringLike": { "s3:prefix": ["uploads/*"] } }
    },
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": ["arn:aws:s3:::my-app-bucket", "arn:aws:s3:::my-app-bucket/*"],
      "Condition": { "Bool": { "aws:SecureTransport": "false" } }
    }
  ]
}
```
```bash
aws iam create-policy --policy-name AppBucketAccess --policy-document file://policy.json
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Permission grant | IAM policy (JSON) | Role definition + role assignment |
| Org guardrails | SCP | Azure Policy / deny assignments |
| Resource-level | Resource policy | Data-plane RBAC, SAS, ACLs |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: "Action": "*", "Resource": "*".
✅ Correct: List exact actions and ARNs; add conditions.

❌ Mistake: Missing that s3:ListBucket applies to the bucket ARN, not /*.
✅ Correct: Use bucket ARN for list, object ARN for get/put.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Elements of a policy statement?
A1: Effect, Action, Resource, and optional Principal and Condition.

Q2: [Medium] Identity-based vs resource-based policy?
A2: Identity policy attaches to who; resource policy attaches to the resource and names a Principal, enabling cross-account access.

Q3: [Hard] Does a permission boundary grant permissions?
A3: No; effective permissions are the intersection of the identity policy and the boundary (and SCPs).

---

## ✅ Quick Checklist
□ Specific actions and ARNs
□ Validated with IAM Access Analyzer / simulator
□ Policies stored in Git (IaC)

---

## ⚡ 1-Line Summary
Policies are JSON: explicit deny wins, default is deny | पॉलिसी JSON है: deny सबसे ऊपर, डिफ़ॉल्ट deny।

## ➡️ Next: 20. IAM Best Practices

---
