# 127. AWS Security Overview
# AWS: IAM, KMS, WAF, Shield, GuardDuty, CloudTrail, Security Hub
# Azure: Entra ID, Key Vault, WAF, DDoS Protection, Defender for Cloud, Activity Log
# हिंदी में: क्लाउड सुरक्षा की परतें - पहचान, नेटवर्क, डेटा, निगरानी

---

## 🔵 Simple Definition
Cloud security is layered: identity, network, data protection, detection and audit. AWS secures the cloud; you secure what you put in it (shared responsibility).
हिंदी: सुरक्षा कई परतों में होती है, और AWS इंफ्रा संभालता है जबकि आपका ऐप और डेटा आपकी ज़िम्मेदारी है।

---

## 🔴 Why it Exists
Misconfigured buckets, leaked keys and open ports cause most cloud breaches.

---

## 🟢 How it Works
```
Identity   : IAM roles, least privilege, MFA
Network    : VPC, security groups, WAF, Shield
Data       : KMS encryption, Secrets Manager, ACM (TLS)
Detect     : GuardDuty, CloudWatch, Config
Audit      : CloudTrail (who did what)
```

---

## 💻 Code / Config Example
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ReadOneSecretOnly",
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:prod/api/db-*"
  }]
}
```
A least-privilege IAM policy for an app role (account ID is a placeholder).

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Identity | IAM | Entra ID + RBAC |
| Secrets/Keys | Secrets Manager, KMS | Key Vault |
| Edge protection | WAF + Shield | Front Door WAF + DDoS Protection |
| Audit | CloudTrail | Activity Log |
| Threat detection | GuardDuty | Defender for Cloud |

---

## ⚠️ Common Mistakes
❌ Mistake: Long-lived access keys in code or GitHub.
✅ Correct: Use IAM roles and GitHub OIDC for Actions.

❌ Mistake: Using the root account daily.
✅ Correct: Lock root with MFA; use IAM Identity Center/roles.

---

## ⚫ Interview Q&A
Q1: [Easy] What is the shared responsibility model?
A1: AWS secures the infrastructure; the customer secures configuration, identities and data.

Q2: [Medium] How to give an EC2/ECS app AWS access safely?
A2: Attach an IAM role (instance/task role); credentials are temporary and rotated automatically.

Q3: [Hard] How do you detect and respond to a leaked key?
A3: CloudTrail + GuardDuty alerts, deactivate key, review activity, rotate, move to roles, add SCP/permission boundaries.

---

## ✅ Quick Checklist
□ MFA on root and users
□ CloudTrail on in all regions
□ Encryption at rest and in transit

---

## ⚡ 1-Line Summary
Layer identity, network, data, detection, audit | पहचान, नेटवर्क, डेटा, डिटेक्शन और ऑडिट की परतें लगाएँ।

## ➡️ Next: AWS Shield (DDoS)
