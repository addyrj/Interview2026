# 147. Service Control Policies (SCP)
# AWS: SCP (AWS Organizations)
# Azure: Azure Policy (deny effect) + Management Group scope
# हिंदी में: SCP - अकाउंट में क्या-क्या करने की अनुमति ही नहीं है, उसकी सीमा

---

## 🔵 Simple Definition
An SCP sets the maximum permissions for accounts in an OU. It never grants access by itself; an action needs both an SCP allow and an IAM allow.
हिंदी: SCP अनुमति की ऊपरी सीमा तय करता है, खुद अनुमति नहीं देता।

## 🔴 Why it Exists
Even an account admin could disable CloudTrail or use a forbidden region. SCPs stop that, even for the account's root user (not the management account).

## 🟢 How it Works
```
Effective permission = SCP (every level: root, OU, account)
                       AND IAM identity policy (and boundary)
Explicit Deny anywhere wins.
```

## 💻 Code / Config Example
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyOutsideAllowedRegions",
      "Effect": "Deny",
      "NotAction": ["iam:*", "organizations:*", "sts:*", "support:*", "cloudfront:*", "route53:*"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": { "aws:RequestedRegion": ["ap-south-1", "us-east-1"] }
      }
    },
    {
      "Sid": "ProtectCloudTrail",
      "Effect": "Deny",
      "Action": ["cloudtrail:StopLogging", "cloudtrail:DeleteTrail"],
      "Resource": "*"
    }
  ]
}
```
```bash
aws organizations create-policy --name guardrails --type SERVICE_CONTROL_POLICY \
  --description "region + trail" --content file://scp.json
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Tool | SCP | Azure Policy (deny), RBAC deny assignments |
| Scope | Root, OU, account | Management group, subscription, RG |
| Grants access? | No | No (Policy does not grant) |
| Pricing | Free | Free |

## ⚠️ Common Mistakes
❌ Thinking SCP gives permission. ✅ It only filters; IAM must still allow.
❌ Applying a deny-all test to Root OU. ✅ Test on a sandbox OU first; you can lock out everyone.

## ⚫ Interview Q&A
Q1 [Easy]: Do SCPs affect the management account? A1: No.
Q2 [Medium]: SCP allows S3, IAM has no S3 allow - result? A2: Denied; both are required.
Q3 [Hard]: Deny-list vs allow-list strategy? A3: Default FullAWSAccess + targeted denies is easier; allow-list is stricter but requires listing every needed service.

## ✅ Quick Checklist
□ Tested in sandbox OU
□ Region and CloudTrail guardrails
□ Break-glass role considered

## ⚡ 1-Line Summary
SCP is a permission ceiling for accounts | SCP अकाउंट की अनुमतियों की छत है।

## ➡️ Next: AWS Cost Explorer
