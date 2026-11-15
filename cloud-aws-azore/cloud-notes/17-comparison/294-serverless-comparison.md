# 294. Serverless Comparison
# AWS: Lambda, API Gateway, Step Functions, DynamoDB, EventBridge
# Azure: Azure Functions, API Management, Durable Functions/Logic Apps, Cosmos DB, Event Grid
# हिंदी में: सर्वरलेस की तुलना

---

## 🔵 Simple Definition
Serverless runs your code on demand with no server management, billed by usage.
हिंदी: सर्वरलेस में कोड जरूरत पर चलता है, सर्वर नहीं संभालना पड़ता, उपयोग के हिसाब से बिल।

---

## 🔴 Why it Exists
Spiky or low traffic workloads waste money on idle servers.

---

## 🟢 How it Works
```
Trigger (HTTP / queue / timer / blob) -> Function runtime scales out
  -> your handler -> output binding / DB
Cold start possible after idle; scale-to-zero by default
```

---

## 💻 Code / Config Example
```javascript
// AWS Lambda (Node.js 20 runtime)
exports.handler = async (event) => ({
  statusCode: 200, body: JSON.stringify({ msg: "hello" }) });

// Azure Functions v4 programming model
// npm i @azure/functions
const { app } = require("@azure/functions");
app.http("hello", {
  methods: ["GET"], authLevel: "anonymous",
  handler: async () => ({ status: 200, jsonBody: { msg: "hello" } }),
});
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Functions | Lambda | Azure Functions |
| Workflow | Step Functions | Durable Functions / Logic Apps |
| Hosting plans | One model (memory-based) | Consumption, Flex Consumption, Premium, Dedicated |
| Pricing | Requests + GB-seconds (approximate - check current docs) | Executions + GB-seconds (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Opening a new DB connection per invocation.
✅ Correct: Reuse connections outside the handler or use a proxy/pooler.

❌ Mistake: Ignoring cold starts for latency-sensitive APIs.
✅ Correct: Provisioned concurrency (Lambda) / Premium or always-ready instances (Functions).

---

## ⚫ Interview Q&A
Q1: [Easy] Lambda equivalent?
A1: Azure Functions.

Q2: [Medium] Step Functions equivalent?
A2: Durable Functions (code-first) or Logic Apps (low-code).

Q3: [Hard] When avoid serverless?
A3: Steady high load, long-running jobs, strict latency, or heavy local state, where containers are cheaper and simpler.

---

## ✅ Quick Checklist
□ Idempotent handlers
□ Timeouts and retries set
□ Connection reuse

---

## ⚡ 1-Line Summary
Lambda=Azure Functions, Step Functions=Durable Functions. | Lambda=Azure Functions, Step Functions=Durable Functions।

## ➡️ Next: 295. Container Services Comparison
