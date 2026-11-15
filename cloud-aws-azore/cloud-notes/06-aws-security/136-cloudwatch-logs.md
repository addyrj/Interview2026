# 136. CloudWatch Logs
# AWS: CloudWatch Logs (+ Logs Insights)
# Azure: Azure Monitor Logs / Log Analytics
# हिंदी में: ऐप और सर्विस के लॉग इकट्ठा करने, खोजने और सहेजने की सेवा

---

## 🔵 Simple Definition
CloudWatch Logs stores log events in log groups and streams, searchable with Logs Insights.
हिंदी: CloudWatch Logs लॉग को ग्रुप और स्ट्रीम में रखता है और Insights से खोजने देता है।

---

## 🔴 Why it Exists
Logs scattered over servers vanish with containers; you need central, queryable logs.

---

## 🟢 How it Works
```
Log group  /ecs/api         (retention, KMS, metric filters)
  Log stream  task-id-1     (events in order)
Sources: ECS awslogs driver, Lambda (automatic), CloudWatch agent, SDK
Outputs: Logs Insights query, subscription filter -> Lambda/Firehose/Kinesis, export to S3
```

---

## 💻 Code / Config Example
```json
{
  "family": "api",
  "containerDefinitions": [{
    "name": "api",
    "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/api:latest",
    "essential": true,
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/api",
        "awslogs-region": "ap-south-1",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
```
```
# Logs Insights query: top errors, last hour
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Store | Log groups | Log Analytics workspace |
| Query | Logs Insights | KQL |
| Stream out | Subscription filters | Diagnostic settings / Event Hubs |
| Pricing | Ingestion + storage per GB (approximate - check current docs) | Per GB ingested (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Never-expire retention.
✅ Correct: Set retention (e.g., 14-30 days) and archive to S3.

❌ Mistake: Logging huge debug output in production.
✅ Correct: Use log levels and structured JSON; ingestion is the main cost.

---

## ⚫ Interview Q&A
Q1: [Easy] Log group vs log stream?
A1: Group = collection with shared settings; stream = sequence from one source.

Q2: [Medium] How to turn logs into alarms?
A2: Metric filter on the group creates a metric, then an alarm on it.

Q3: [Hard] Ship logs to a central account/OpenSearch?
A3: Subscription filters to Firehose/Kinesis, cross-account destination, Firehose delivers to S3/OpenSearch.

---

## ✅ Quick Checklist
□ Retention set
□ JSON structured logs
□ Metric filter for errors

---

## ⚡ 1-Line Summary
CloudWatch Logs = central searchable logs | CloudWatch Logs केंद्रीय और खोजने योग्य लॉग देता है।

## ➡️ Next: CloudWatch Metrics
