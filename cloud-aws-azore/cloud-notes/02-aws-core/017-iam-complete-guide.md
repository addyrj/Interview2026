---

# 17. IAM, Complete Guide
# AWS: IAM (Identity and Access Management)
# Azure: Microsoft Entra ID + Azure RBAC
# हिंदी में: IAM = कौन (identity) क्या (action) किस पर (resource) कर सकता है

---

## 🔵 Simple Definition (2 lines)
IAM controls who is authenticated and what they are authorized to do on which AWS resources, via users, roles and policies.
हिंदी: IAM तय करता है कि कौन लॉगिन कर सकता है और किस चीज़ पर कौन-सा काम कर सकता है।

---

## 🔴 Why it Exists (2 lines)
Without fine-grained access control, one leaked credential owns the whole account.
IAM enables least privilege and auditable access.

---

## 🟢 How it Works
```
Principal (user/role/service) --request--> AWS API
   1 Authenticate (password+MFA, access key, role session token)
   2 Authorize: evaluate policies
        explicit Deny  -> DENIED (always wins)
        else Allow in (identity policy / resource policy ...) and not blocked
             by SCP / permission boundary / session policy -> ALLOWED
        else implicit deny
IAM is global (not regional) and free.
```

---

## 💻 Code / Config Example
```bash
# Who am I and what can I see?
aws sts get-caller-identity
aws iam list-users --query 'Users[].UserName'

# Test a policy decision without running the action
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/dev1 \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-app-bucket/file.txt

# Azure: assign a built-in role at resource group scope
az role assignment create --assignee user@contoso.com \
  --role "Reader" --scope /subscriptions/<sub-id>/resourceGroups/demo-rg
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Identity store | IAM users / Identity Center | Entra ID users/groups |
| Authorization | JSON policies | RBAC role assignments (scope-based) |
| Workload identity | IAM role | Managed Identity |
| Pricing | IAM free | Entra ID Free tier; P1/P2 paid (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Attaching AdministratorAccess to everyone.
✅ Correct: Least privilege; start narrow and expand using Access Analyzer findings.

❌ Mistake: Embedding access keys in app code or Docker images.
✅ Correct: Use roles (EC2 instance profile, ECS task role, Lambda role).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Is IAM regional?
A1: No, it is global.

Q2: [Medium] Policy evaluation order?
A2: Explicit deny wins, otherwise an explicit allow is needed (and not limited by SCP/boundary), else implicit deny.

Q3: [Hard] Debug "AccessDenied" for an ECS task reading S3.
A3: Check task role (not execution role), identity policy actions/ARNs, bucket policy, KMS key policy, SCPs/boundaries, and use CloudTrail plus the policy simulator.

---

## ✅ Quick Checklist
□ MFA for humans
□ Roles for workloads
□ Least privilege and regular review

---

## ⚡ 1-Line Summary
IAM = authenticate then authorize with least privilege | IAM = पहचान जाँचो, फिर कम-से-कम ज़रूरी अनुमति दो।

## ➡️ Next: 18. IAM Users + Groups + Roles

---
