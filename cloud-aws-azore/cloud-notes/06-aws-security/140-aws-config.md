# 140. AWS Config
# AWS: AWS Config
# Azure: Azure Policy + Resource Graph (change history) + Defender for Cloud
# हिंदी में: रिसोर्स की कॉन्फ़िगरेशन हिस्ट्री और नियमों से अनुपालन की जाँच

---

## 🔵 Simple Definition
Config records resource configurations over time and evaluates them against rules (compliant / non-compliant).
हिंदी: Config रिसोर्स की सेटिंग्स का इतिहास रखता है और नियमों से जाँचता है कि वे सही हैं या नहीं।

---

## 🔴 Why it Exists
You must know what a resource looked like last week and whether it breaks policy (e.g., public S3 bucket, unencrypted EBS).

---

## 🟢 How it Works
```
Resource change -> Configuration recorder -> configuration item (snapshot)
   stored in S3 (history/timeline)
Config rules (managed or custom Lambda) evaluate -> COMPLIANT / NON_COMPLIANT
   -> remediation (SSM Automation) / EventBridge / SNS
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation - managed rule: S3 buckets must not be public-read
# (assumes the Config recorder is already enabled in the account/region)
AWSTemplateFormatVersion: "2010-09-09"
Resources:
  S3NoPublicRead:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-no-public-read
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_PUBLIC_READ_PROHIBITED
      Scope:
        ComplianceResourceTypes: ["AWS::S3::Bucket"]
```
```bash
aws configservice get-compliance-details-by-config-rule \
  --config-rule-name s3-no-public-read --compliance-types NON_COMPLIANT
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Compliance rules | Config rules / conformance packs | Azure Policy |
| Change history | Config timeline | Resource Graph change history / Activity Log |
| Auto remediation | SSM Automation | Policy DeployIfNotExists / remediation tasks |
| Pricing | Per configuration item + rule evaluation (approximate - check current docs) | Policy free; others vary (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Thinking Config blocks bad changes.
✅ Correct: Config detects after the fact (use SCPs/IAM to prevent).

❌ Mistake: Recorder off in some regions.
✅ Correct: Enable in all regions/accounts (aggregator).

---

## ⚫ Interview Q&A
Q1: [Easy] What does Config do?
A1: Tracks resource configuration changes and checks compliance.

Q2: [Medium] Config vs CloudTrail?
A2: CloudTrail = who made which API call; Config = what the resource looked like before and after.

Q3: [Hard] Detect and auto-fix public buckets?
A3: Config rule detects, EventBridge/remediation action runs SSM Automation to block public access, SNS notifies, aggregator for the whole organization.

---

## ✅ Quick Checklist
□ Recorder on in all regions
□ Key managed rules enabled
□ Remediation or alerts wired

---

## ⚡ 1-Line Summary
Config = resource state history plus compliance rules | Config रिसोर्स का इतिहास रखता और अनुपालन जाँचता है।

## ➡️ Next: Compute and Containers (next section)
