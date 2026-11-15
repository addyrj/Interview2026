# 134. CloudTrail - Audit Logs
# AWS: AWS CloudTrail
# Azure: Azure Activity Log (+ Diagnostic Settings)
# हिंदी में: खाते में कौन, कब, क्या API कॉल किया - इसका रिकॉर्ड

---

## 🔵 Simple Definition
CloudTrail records AWS API calls (console, CLI, SDK) for governance and auditing.
हिंदी: CloudTrail हर AWS API कॉल का रिकॉर्ड रखता है - किसने, कब, क्या किया।

---

## 🔴 Why it Exists
Security investigations and compliance need a reliable record of who changed what.

---

## 🟢 How it Works
```
API call -> CloudTrail event (who, what, when, source IP)
 Event history: last 90 days, management events, free to view
 Trail -> S3 bucket (long-term) (+ CloudWatch Logs for alerts)
 Event types: management | data (S3 objects, Lambda) | Insights
```

---

## 💻 Code / Config Example
```bash
# AWS CLI v2 - org-style multi-region trail with log validation
aws cloudtrail create-trail --name main-trail \
  --s3-bucket-name my-audit-logs-123456789012 \
  --is-multi-region-trail --enable-log-file-validation
aws cloudtrail start-logging --name main-trail

# Who deleted that bucket?
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket
```
The S3 bucket needs a policy allowing cloudtrail.amazonaws.com to write.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Control-plane audit | CloudTrail | Activity Log |
| Long-term store | S3 | Storage / Log Analytics |
| Data-plane events | Data events (paid) | Resource diagnostic logs |
| Pricing | First management trail free, extras paid (approximate - check current docs) | Activity Log free (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Relying only on 90-day event history.
✅ Correct: Create a trail to S3 for retention.

❌ Mistake: Logs in the same account anyone can delete.
✅ Correct: Central log account, bucket policy, MFA delete/Object Lock, log validation.

---

## ⚫ Interview Q&A
Q1: [Easy] What does CloudTrail log?
A1: AWS API activity: management events and optionally data events.

Q2: [Medium] CloudTrail vs CloudWatch vs Config?
A2: CloudTrail = who did what; CloudWatch = metrics/logs/alarms; Config = resource state history/compliance.

Q3: [Hard] How to alert on root login?
A3: Trail to CloudWatch Logs, metric filter on userIdentity.type=Root, alarm to SNS (or EventBridge rule on the sign-in event).

---

## ✅ Quick Checklist
□ Multi-region trail on
□ Log validation enabled
□ Alerts on sensitive events

---

## ⚡ 1-Line Summary
CloudTrail = audit log of API calls | CloudTrail API कॉल्स का ऑडिट लॉग है।

## ➡️ Next: CloudWatch - Monitoring
