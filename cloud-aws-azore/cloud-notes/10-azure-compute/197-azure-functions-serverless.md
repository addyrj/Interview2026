# 197. Azure Functions (Serverless = Lambda)
# AWS: AWS Lambda
# Azure: Azure Functions
# हिंदी में: event पर चलने वाला छोटा कोड, बिना सर्वर संभाले

---

## 🔵 Simple Definition
Event-driven serverless functions triggered by HTTP, timers, queues, blobs, etc., billed on execution.
Function किसी event पर चलता है और आप सिर्फ चलने के हिसाब से भुगतान करते हैं।

---

## 🔴 Why it Exists
Spiky or small jobs (webhooks, cron, queue consumers) do not justify always-on servers.

---

## 🟢 How it Works
```
Trigger (HTTP / Timer / Queue / Blob / Event Grid)
   -> Function App (host runtime v4, Node 20, Python 3.11)
   -> Input/output bindings (Storage, Cosmos, Service Bus)
Plans: Consumption (scale to zero) | Flex Consumption | Premium (no cold start) | Dedicated
```
Function App needs a storage account.

---

## 💻 Code / Config Example
```javascript
// src/functions/hello.js  (Node.js v4 programming model)
const { app } = require('@azure/functions');

app.http('hello', {
  methods: ['GET', 'POST'],
  authLevel: 'function',
  handler: async (request, context) => {
    const name = request.query.get('name') || 'world';
    context.log(`Hello ${name}`);
    return { status: 200, jsonBody: { message: `Hello, ${name}` } };
  },
});
```
```bash
az functionapp create -g rg-fn -n fn-demo-123 --storage-account stfndemo123 \
  --consumption-plan-location centralindia --runtime node --runtime-version 20 \
  --functions-version 4
func azure functionapp publish fn-demo-123   # Azure Functions Core Tools
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Lambda | Functions |
| Triggers | Event source mappings | Triggers + bindings |
| Orchestration | Step Functions | Durable Functions |
| Cold start fix | Provisioned concurrency | Premium / Flex always-ready |
| Pricing | Per request + GB-s | Per execution + GB-s (approximate - check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Long-running work in HTTP functions (timeouts).
✅ Correct: Queue it or use Durable Functions.

❌ Mistake: New DB connection per call.
✅ Correct: Reuse clients outside the handler.

---

## ⚫ Interview Q&A
Q1: [Easy] What triggers a function?
A1: HTTP, timer, queue, blob, Event Grid, etc.

Q2: [Medium] What are bindings?
A2: Declarative input/output connections to services, reducing boilerplate.

Q3: [Hard] Consumption vs Premium?
A3: Consumption scales to zero but has cold starts and limits; Premium keeps pre-warmed instances and VNet integration at higher cost.

---

## ✅ Quick Checklist
□ Idempotent handlers
□ Managed identity for storage/Key Vault
□ App Insights enabled

---

## ⚡ 1-Line Summary
Azure Functions = Lambda for Azure. | Azure Functions = Azure का Lambda।

## ➡️ Next: Azure Container Instances (ACI)
