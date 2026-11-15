# 148. AWS Cost Explorer
# AWS: AWS Cost Explorer
# Azure: Microsoft Cost Management (Cost analysis)
# हिंदी में: कॉस्ट एक्सप्लोरर - खर्च कहाँ और क्यों हो रहा है, इसका चार्ट

---

## 🔵 Simple Definition
Cost Explorer visualises and queries your AWS spend and usage by service, account, tag, region, with forecasts.
हिंदी: यह दिखाता है कि कौन-सी सेवा, टैग या अकाउंट पर कितना पैसा खर्च हुआ और आगे कितना होगा।

## 🔴 Why it Exists
Cloud bills surprise teams. Grouping by service/tag finds the culprit (NAT Gateway data, idle EBS, oversized RDS).

## 🟢 How it Works
```
Billing data --> Cost Explorer (daily/monthly, 12 months)
   filter: account, service, tag   group-by: service | tag
   outputs: charts, forecast, RI/Savings Plan recommendations, API
```

## 💻 Code / Config Example
```bash
# Last month cost by service (AWS CLI v2; the API itself bills per request)
aws ce get-cost-and-usage \
  --time-period Start=2026-10-01,End=2026-11-01 \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Group by cost-allocation tag (tag must be activated first)
aws ce get-cost-and-usage \
  --time-period Start=2026-10-01,End=2026-11-01 \
  --granularity DAILY --metrics UnblendedCost \
  --group-by Type=TAG,Key=project
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Cost Explorer | Cost Management |
| Console use | Free | Free |
| API | Charged per request (check current docs) | Cost Management API |
| Tags | Must activate cost allocation tags | Tags flow into cost analysis |

## ⚠️ Common Mistakes
❌ No tags, so costs are unattributable. ✅ Enforce tags (env, project, owner) and activate them.
❌ Polling API in a loop. ✅ It costs per request; cache results.

## ⚫ Interview Q&A
Q1 [Easy]: What can you group by? A1: Service, account, region, tag, usage type.
Q2 [Medium]: Why is a tag missing in reports? A2: It must be activated as a cost allocation tag; it applies going forward.
Q3 [Hard]: How would you find a sudden spike? A3: Daily granularity by service then by usage type; compare to Cost Anomaly Detection alert.

## ✅ Quick Checklist
□ Cost allocation tags activated
□ Weekly review
□ Anomaly detection on

## ⚡ 1-Line Summary
Cost Explorer shows where the money goes | कॉस्ट एक्सप्लोरर बताता है पैसा कहाँ जा रहा है।

## ➡️ Next: AWS Budgets
