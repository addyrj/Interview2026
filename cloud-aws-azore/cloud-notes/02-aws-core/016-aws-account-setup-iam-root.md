---

# 16. AWS Account Setup + IAM Root
# AWS: AWS account, root user, IAM Identity Center, Organizations
# Azure: Entra ID tenant, Subscription, Global Administrator
# हिंदी में: AWS अकाउंट बनाना और रूट यूज़र को सुरक्षित रखना

---

## 🔵 Simple Definition (2 lines)
Creating an AWS account creates a root user (email + password) with unrestricted power over everything in the account.
हिंदी: अकाउंट बनाते ही रूट यूज़र बनता है जिसके पास सब कुछ करने की ताक़त होती है, इसलिए इसे रोज़ इस्तेमाल नहीं करते।

---

## 🔴 Why it Exists (2 lines)
Every resource needs an owner and a billing boundary.
The root user must be locked down because it cannot be restricted by IAM policies.

---

## 🟢 How it Works
```
1 Sign up (email, card, phone) -> root user
2 Enable MFA on root (hardware key or authenticator)
3 Delete/avoid root access keys
4 Set billing alerts + budget
5 Create admin via IAM Identity Center (or an IAM admin user)
6 Use that admin daily; root only for root-only tasks
    (change account settings, close account, restore IAM admin, etc.)
Multi-account: Organizations -> dev / staging / prod accounts + SCPs
```

---

## 💻 Code / Config Example
```bash
# After creating an admin identity, configure CLI v2 with SSO (interactive)
aws configure sso
aws sts get-caller-identity            # confirm who you are (not root!)

# Check whether root has access keys / MFA (needs permission)
aws iam get-account-summary \
  --query 'SummaryMap.{RootKeys:AccountAccessKeysPresent,RootMFA:AccountMFAEnabled}'

# Azure equivalent: sign in and view subscription
az login
az account show --query '{sub:name,tenant:tenantId}'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Top identity | Root user (per account) | Global Administrator (tenant) |
| Billing boundary | Account | Subscription |
| Multi-account mgmt | Organizations + SCPs | Management Groups + Azure Policy |
| Pricing | Free tier for new accounts (terms change, check docs) | Free account with credit (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using root for daily work or creating root access keys.
✅ Correct: MFA on root, no keys, use IAM Identity Center/admin role.

❌ Mistake: Root email is a personal mailbox of one person.
✅ Correct: Use a team-owned distribution email and secure recovery contacts.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is the root user?
A1: The account owner identity with full, unrestrictable access.

Q2: [Medium] What do you do right after creating an account?
A2: Enable root MFA, set billing alerts, create an admin identity, turn on CloudTrail, avoid access keys.

Q3: [Hard] Design a multi-account setup.
A3: Organizations with separate prod/non-prod/log-archive/security accounts, SCP guardrails, Identity Center for SSO, centralized CloudTrail and Config.

---

## ✅ Quick Checklist
□ Root MFA enabled
□ No root access keys
□ Budget alert and CloudTrail on

---

## ⚡ 1-Line Summary
Lock the root user away and work through an admin identity | रूट को ताले में रखो, रोज़ का काम एडमिन आइडेंटिटी से करो।

## ➡️ Next: 17. IAM, Complete Guide

---
