# 135. CloudWatch - Monitoring
# AWS: Amazon CloudWatch
# Azure: Azure Monitor
# हिंदी में: मेट्रिक्स, लॉग्स और अलार्म के ज़रिए सिस्टम की निगरानी

---

## 🔵 Simple Definition
CloudWatch collects metrics, logs and events from AWS and your apps, and drives alarms and dashboards.
हिंदी: CloudWatch मेट्रिक्स और लॉग इकट्ठा करके अलार्म और डैशबोर्ड चलाता है।

---

## 🔴 Why it Exists
You cannot fix what you cannot see; outages should alert you before users do.

---

## 🟢 How it Works
```
EC2/ECS/Lambda/RDS --metrics--> CloudWatch Metrics --> Alarms --> SNS / Auto Scaling
App/containers --stdout--> CloudWatch Logs --> Logs Insights, metric filters
Dashboards visualise both
Extras: Synthetics, X-Ray (traces), Container Insights
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation - CPU alarm on an ECS service, notify SNS
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  Cluster: {Type: String}
  Service: {Type: String}
  AlertTopicArn: {Type: String}
Resources:
  HighCpu:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: api-high-cpu
      Namespace: AWS/ECS
      MetricName: CPUUtilization
      Dimensions:
        - {Name: ClusterName, Value: !Ref Cluster}
        - {Name: ServiceName, Value: !Ref Service}
      Statistic: Average
      Period: 60
      EvaluationPeriods: 5
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      AlarmActions: [!Ref AlertTopicArn]
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Platform | CloudWatch | Azure Monitor |
| Logs | CloudWatch Logs | Log Analytics (KQL) |
| Tracing | X-Ray | Application Insights |
| Pricing | Per metric, log GB ingested/stored (approximate - check current docs) | Per GB ingested (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Logs kept forever by default.
✅ Correct: Set retention on every log group.

❌ Mistake: Expecting memory/disk metrics on EC2 by default.
✅ Correct: Install the CloudWatch agent.

---

## ⚫ Interview Q&A
Q1: [Easy] What are the main parts?
A1: Metrics, Logs, Alarms, Dashboards, Events.

Q2: [Medium] Basic vs detailed monitoring?
A2: EC2 basic is 5-minute, detailed is 1-minute (paid).

Q3: [Hard] How to monitor a containerised Node app?
A3: awslogs/FireLens to CloudWatch Logs, Container Insights, custom metrics (EMF), alarms on 5xx/latency/p99, X-Ray for traces.

---

## ✅ Quick Checklist
□ Alarms on error rate and latency
□ Log retention set
□ Alerts go to a real channel

---

## ⚡ 1-Line Summary
CloudWatch = metrics, logs, alarms in one place | CloudWatch में मेट्रिक्स, लॉग और अलार्म एक जगह मिलते हैं।

## ➡️ Next: CloudWatch Logs
