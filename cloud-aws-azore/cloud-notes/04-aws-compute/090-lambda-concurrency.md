---

# 90. Lambda Concurrency
# AWS: Lambda reserved + provisioned concurrency
# Azure: Functions scale-out limits / Premium plan always-ready instances
# हिंदी में: लैम्ब्डा कॉन्करेंसी

---

## 🔵 Simple Definition (2 lines)
Concurrency is how many instances of your function run at the same moment. Each in-flight request uses one execution environment.
हिंदी: Concurrency मतलब एक ही समय में कितने Lambda इंस्टेंस चल रहे हैं।

---

## 🔴 Why it Exists (2 lines)
Unlimited scaling can overload your database or starve other functions of the account limit. Concurrency controls cap and guarantee capacity.

---

## 🟢 How it Works
```
Concurrency ≈ requests/second × average duration (seconds)
  100 req/s × 0.5 s = ~50 concurrent

Account limit: default 1000 per region (approximate — check current docs; can be raised)
Reserved concurrency  : guarantees AND caps a function (0 = disable it)
Provisioned concurrency: pre-warmed environments, no cold start (costs extra)
Over the limit -> throttle (429 / TooManyRequests; async events retried)
```

---

## 💻 Code / Config Example
```bash
# AWS CLI v2 (needs real credentials; not run here)
# Cap this function at 20 so it cannot flood the DB
aws lambda put-function-concurrency --function-name orders-worker \
  --reserved-concurrent-executions 20

# Pre-warm 5 environments on alias "live"
aws lambda put-provisioned-concurrency-config --function-name orders-api \
  --qualifier live --provisioned-concurrent-executions 5
```
```yaml
# SAM equivalent
Resources:
  Api:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: nodejs20.x
      Handler: index.handler
      AutoPublishAlias: live
      ReservedConcurrentExecutions: 50
      ProvisionedConcurrencyConfig: { ProvisionedConcurrentExecutions: 5 }
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Cap | Reserved concurrency | `functionAppScaleLimit` / host.json concurrency |
| Pre-warm | Provisioned concurrency | Premium plan pre-warmed / always-ready instances |
| Per-instance concurrency | 1 request per environment | Many executions per instance |
| Pricing | Provisioned billed while configured (approximate — check current docs) | Premium billed per instance (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Setting reserved concurrency to 0 by accident (function stops).
✅ Correct: Verify values; 0 is a kill switch.

❌ Mistake: Letting Lambda scale to hundreds while RDS has 100 connections.
✅ Correct: Reserve concurrency and use RDS Proxy.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What happens on throttling?
A1: Sync callers get 429; async and stream/queue sources retry.

Q2: [Medium] Reserved vs provisioned?
A2: Reserved = capacity guarantee and cap (free). Provisioned = warm environments to avoid cold starts (paid).

Q3: [Hard] 200 req/s, 300 ms each. What concurrency?
A3: 200 × 0.3 = 60 concurrent, so reserve above ~60 plus headroom and check the account limit.

---

## ✅ Quick Checklist
□ Estimate rps × duration
□ Downstream DB limits considered
□ Throttle alarms in CloudWatch

---

## ⚡ 1-Line Summary
Concurrency = parallel instances; reserve to protect, provision to warm | Concurrency = समानांतर इंस्टेंस की संख्या।

## ➡️ Next: Lambda Cold Start

---
