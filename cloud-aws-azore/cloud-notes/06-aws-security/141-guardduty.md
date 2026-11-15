# 141. GuardDuty
# AWS: Amazon GuardDuty
# Azure: Microsoft Defender for Cloud (threat protection plans) + Microsoft Sentinel
# हिंदी में: गार्डड्यूटी - AWS अकाउंट में खतरे की निगरानी करने वाली सेवा

---

## 🔵 Simple Definition
GuardDuty is a managed threat-detection service. It analyses CloudTrail, VPC Flow Logs and DNS logs with ML and threat intel, and raises findings (e.g. leaked keys, crypto mining).
हिंदी: यह लॉग्स को अपने-आप जाँचकर हैकिंग या संदिग्ध गतिविधि की चेतावनी (finding) देता है।

## 🔴 Why it Exists
You cannot read millions of log lines by hand. GuardDuty needs no agents and no log pipeline setup; one click enables it.

## 🟢 How it Works
```
CloudTrail + VPC Flow + DNS logs (read independently by GuardDuty)
            |
      GuardDuty (ML + threat intel)
            |
   Finding (severity 1-10, e.g. UnauthorizedAccess:EC2/SSHBruteForce)
            |
   EventBridge rule --> SNS / Lambda (auto-remediate) / Slack
```

## 💻 Code / Config Example
```bash
# Enable GuardDuty in the current region (AWS CLI v2)
DET=$(aws guardduty create-detector --enable --query DetectorId --output text)

# List high severity findings (>= 7)
aws guardduty list-findings --detector-id "$DET" \
  --finding-criteria '{"Criterion":{"severity":{"Gte":7}}}'
```
```yaml
# CloudFormation: detector + EventBridge rule for alerts
Resources:
  Detector:
    Type: AWS::GuardDuty::Detector
    Properties: { Enable: true }
  AlertRule:
    Type: AWS::Events::Rule
    Properties:
      EventPattern:
        source: [aws.guardduty]
        detail-type: [GuardDuty Finding]
      Targets:
        - Arn: arn:aws:sns:ap-south-1:111122223333:sec-alerts
          Id: sns
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | GuardDuty | Defender for Cloud + Sentinel |
| Data sources | CloudTrail, VPC Flow, DNS (+ S3, EKS, Lambda optional) | Activity logs, resource-level Defender plans |
| Setup | One-click, per region | Enable plans per resource type |
| Pricing | Per volume of events analysed; 30-day trial (approximate - check current docs) | Per-resource plan pricing (check current docs) |

## ⚠️ Common Mistakes
❌ Enabling only in one region. ✅ Enable in all regions (attackers use unused ones) or use the delegated admin via Organizations.
❌ Findings sit unread. ✅ Route to EventBridge -> SNS/Slack and set an owner.

## ⚫ Interview Q&A
Q1 [Easy]: Does GuardDuty need an agent? A1: No, it reads AWS-internal logs directly.
Q2 [Medium]: How do you auto-respond to a finding? A2: EventBridge rule on "GuardDuty Finding" -> Lambda that isolates the EC2 (swap security group) or disables the IAM key.
Q3 [Hard]: How to run it across 50 accounts? A3: Organizations delegated administrator, auto-enable for new members, aggregate findings in one security account, forward to Security Hub.

## ✅ Quick Checklist
□ Enabled in all regions
□ Findings routed to alerts
□ Delegated admin in multi-account setup

## ⚡ 1-Line Summary
GuardDuty watches your logs for attacks without agents | गार्डड्यूटी बिना एजेंट के लॉग देखकर हमले पकड़ता है।

## ➡️ Next: Security Hub
