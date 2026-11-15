---

# 85. Lambda — Complete Guide
# AWS: AWS Lambda
# Azure: Azure Functions
# हिंदी में: लैम्ब्डा (सर्वरलेस फ़ंक्शन)

---

## 🔵 Simple Definition (2 lines)
Lambda runs your code in response to events without you managing servers. You upload a function; AWS runs it, scales it and bills per use.
हिंदी: Lambda में आप सिर्फ़ कोड देते हैं, सर्वर AWS संभालता है और इस्तेमाल के हिसाब से बिल बनता है।

---

## 🔴 Why it Exists (2 lines)
Running a VPS 24/7 for a job that fires a few times a day wastes money and ops time. Lambda scales from 0 to many and back to 0.

---

## 🟢 How it Works
```
Event (HTTP, S3 upload, SQS, cron)
        |
        v
  Lambda service ──> creates execution environment (cold start) ──> runs handler(event, context)
        |                     reused for later calls (warm)
        v
  Logs -> CloudWatch Logs; permissions -> execution IAM role
Limits (approximate — check current docs): max timeout 15 min, memory 128 MB-10 GB,
zip package 50 MB direct / 250 MB unzipped, container image up to 10 GB.
```

---

## 💻 Code / Config Example
```javascript
// index.mjs  (Node.js 20 runtime, handler = index.handler)
export const handler = async (event) => {
  console.log("event", JSON.stringify(event));
  return {
    statusCode: 200,
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ ok: true, ts: Date.now() }),
  };
};
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Lambda | Azure Functions |
| Triggers | S3, SQS, API GW, EventBridge... | Blob, Queue, HTTP, Timer, Event Grid... |
| Max duration | 15 min | Consumption 5-10 min; Premium/Dedicated longer |
| Pricing | Requests + GB-seconds (approximate — check current docs) | Executions + GB-seconds (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Running long (>15 min) or stateful work in Lambda.
✅ Correct: Use ECS/Fargate or Step Functions; keep state in DynamoDB/S3.

❌ Mistake: Creating DB connections inside the handler every call.
✅ Correct: Create clients outside the handler (reused when warm); use RDS Proxy for SQL.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is serverless?
A1: You do not manage servers; the provider provisions, scales and bills per execution.

Q2: [Medium] What is the handler and context?
A2: Handler is the entry function; event is the input payload; context gives request ID, remaining time, etc.

Q3: [Hard] Lambda vs ECS Fargate vs VPS?
A3: Lambda for event-driven, spiky, short jobs; Fargate for long-running containers with steady traffic; VPS for cheapest steady low-scale load with full control.

---

## ✅ Quick Checklist
□ Least-privilege execution role
□ Timeout and memory tuned
□ Clients initialised outside the handler

---

## ⚡ 1-Line Summary
Lambda = run code on events, pay per use | Lambda इवेंट पर कोड चलाता है और सिर्फ़ इस्तेमाल का पैसा लगता है।

## ➡️ Next: Lambda Function Setup

---
