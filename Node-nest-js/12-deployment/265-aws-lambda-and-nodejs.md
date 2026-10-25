# 265. AWS Lambda + Node.js
# हिंदी में: AWS Lambda + Node.js — Serverless Computing

---

## 🔵 Simple Definition (English)
**AWS Lambda** lets you run Node.js code without managing any server — you just upload a function, AWS runs it when triggered (HTTP request, file upload, queue message), and you only pay for the exact compute time used (milliseconds). No server to patch, scale, or keep running 24/7.

## 🔵 सरल परिभाषा (Hindi)
**AWS Lambda** एक ऐसी service है जहाँ तुम Node.js function upload करते हो, और AWS उसे तभी run करता है जब कोई trigger (HTTP request, file upload, queue message) आता है। कोई server manage नहीं करना — patch, scale, 24/7 chalana कुछ नहीं। Pay सिर्फ उतने compute time का जितना function actually चला (milliseconds में billing)।

---

## 🔴 Problem it Solves
```
TRADITIONAL SERVER (EC2/VPS) PROBLEMS:
  - Server runs 24/7 even if traffic comes for 2 hours/day
  - You pay for idle time (99% of a low-traffic API's life)
  - Scaling needs manual setup: load balancer + auto-scaling groups
  - OS patching, security updates, Node version upgrades = your job
  - One crashed server = downtime until you notice and restart

EXAMPLE: Zomato's "send order confirmation email" function
  - Runs maybe 50,000 times/day, each call takes ~200ms
  - Total actual work: 50,000 × 0.2s = 10,000s = ~2.7 hours/day
  - On EC2: paying for 24 hours, using only 2.7 hours = huge waste

LAMBDA SOLUTION:
  - Code only runs when triggered — zero cost when idle
  - AWS auto-scales: 1 request or 10,000 requests simultaneously — handled
  - No OS/patching — AWS manages the runtime environment
  - Pay per invocation + per 1ms of execution time (very cheap for short tasks)
  - Perfect fit for: webhooks, image resizing, email sending, cron jobs,
    file processing — short, event-driven, bursty workloads
```

## 🔴 यह क्यों बना? (Hindi)
Traditional EC2 server 24/7 chalta hai, chahe traffic ho ya na ho — tum idle time ka bhi paisa dete ho. Zomato ka "order confirmation email" function din mein 50,000 baar chalta hai, har baar 200ms — total actual kaam sirf ~2.7 ghante/din. EC2 par 24 ghante ka paisa dena padta, jabki use sirf 2.7 ghante hua. Lambda mein code sirf trigger hone par chalta hai — idle time ka zero cost. AWS automatically scale karta hai — 1 request ya 10,000 simultaneous, dono handle. OS patching, Node upgrade AWS ki responsibility — perfect for webhooks, image resize, email, cron jobs jaise short bursty kaam ke liye.

---

## 🟢 How it Works — Step by Step

Step 1 → You write a handler function: `exports.handler = async (event, context) => {...}`
Step 2 → You zip your code (with `node_modules`) and upload it to Lambda, OR deploy via CLI/IaC tool.
Step 3 → You attach a **trigger**: API Gateway (HTTP), S3 (file upload), SQS (queue message), DynamoDB Streams (table change), EventBridge (cron schedule).
Step 4 → When the trigger fires, AWS spins up a lightweight execution environment (container), loads your code, and calls `handler(event, context)`.
Step 5 → `event` contains trigger data (HTTP body/headers, S3 file info, etc.); `context` has runtime info (remaining time, request ID).
Step 6 → Your function returns a response (for API Gateway, a specific `{statusCode, body}` shape); AWS sends it back to the caller.
Step 7 → After some idle time, AWS **freezes or destroys** the execution environment to save resources — next invocation may need a fresh "cold start."

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Tum ek handler function likhte ho: `exports.handler = async (event, context) => {...}`
Step 2 → Code ko zip karke (node_modules ke saath) Lambda par upload karte ho, ya CLI/IaC tool se deploy karte ho।
Step 3 → Ek **trigger** attach karte ho: API Gateway (HTTP), S3 (file upload), SQS (queue message), DynamoDB Streams (table change), EventBridge (cron schedule)।
Step 4 → Trigger fire hone par AWS ek lightweight execution environment (container) spin up karta hai, code load karta hai, aur `handler(event, context)` call karta hai।
Step 5 → `event` mein trigger ka data hota hai (HTTP body/headers, S3 file info); `context` mein runtime info (remaining time, request ID)।
Step 6 → Function response return karta hai (API Gateway ke liye specific `{statusCode, body}` shape mein); AWS caller ko bhej deta hai।
Step 7 → Kuch idle time ke baad AWS environment ko **freeze ya destroy** kar deta hai resources bachane ke liye — next invocation par fresh "cold start" lag sakta hai।

---

## 🟡 Real World Example
**Swiggy image processing:** When a restaurant owner uploads a new dish photo to S3, an S3 trigger fires a Lambda function that resizes the image into 3 sizes (thumbnail, medium, full) and saves them back to S3 — no server sitting idle waiting for uploads. **Razorpay webhook handler:** A payment gateway webhook hits API Gateway → Lambda validates the signature, updates order status in DynamoDB, and publishes an event to SQS for downstream processing — scales instantly during flash-sale traffic spikes without any manual provisioning.

## 🟡 Real Example Hindi mein
**Swiggy image processing:** Jab restaurant owner S3 par naya dish photo upload karta hai, S3 trigger ek Lambda function ko fire karta hai jo image ko 3 sizes (thumbnail, medium, full) mein resize karke S3 mein wapas save karta hai — koi server idle baithkar upload wait nahi kar raha। **Razorpay webhook handler:** Payment gateway ka webhook API Gateway par aata hai → Lambda signature validate karta hai, DynamoDB mein order status update karta hai, aur SQS mein event publish karta hai downstream processing ke liye — flash-sale traffic spike mein bhi instantly scale hota hai, manual provisioning ki zaroorat nahi।

---

## 💻 Code Example — Basic

```javascript
// basic-lambda.js — a simple Lambda handler, run locally with mock event
// In real AWS, this file is zipped and uploaded; here we simulate the call.

// Lambda handlers export a function named "handler" (convention, configurable)
exports.handler = async (event, context) => {
  // "event" carries the trigger's payload — here we assume an API Gateway HTTP event
  console.log('Event received:', JSON.stringify(event));

  // "context" gives runtime info — useful for logging/timeouts
  console.log('Remaining time (ms):', context.getRemainingTimeInMillis?.() ?? 'N/A');

  // Extract query string param, e.g. ?name=Rahul
  const name = event.queryStringParameters?.name || 'Guest';

  // API Gateway (HTTP API / Lambda proxy integration) expects this exact shape
  return {
    statusCode: 200, // HTTP status code sent back to the client
    headers: { 'Content-Type': 'application/json' }, // response headers
    body: JSON.stringify({ message: `Hello, ${name}! From Lambda.` }), // body must be a STRING
  };
};

// ─── LOCAL SIMULATION (so you can run `node basic-lambda.js`) ────────────────
if (require.main === module) {
  // Fake an API Gateway event object the way AWS would send it
  const fakeEvent = {
    queryStringParameters: { name: 'Priya' },
    httpMethod: 'GET',
    path: '/hello',
  };

  // Fake context object (real AWS provides a much richer one)
  const fakeContext = {
    getRemainingTimeInMillis: () => 3000,
  };

  // Call the handler exactly like AWS would, and print the result
  exports.handler(fakeEvent, fakeContext).then((res) => {
    console.log('Lambda response:', res);
  });
}
```

## 💻 Code Example — Advanced

```javascript
// advanced-lambda.js — production-style Lambda: DB connection reuse,
// error handling, cold-start optimization, and an S3 event trigger handler.

const { DynamoDBClient } = require('@aws-sdk/client-dynamodb'); // npm install @aws-sdk/client-dynamodb
const { DynamoDBDocumentClient, GetCommand, PutCommand } = require('@aws-sdk/lib-dynamodb');

// ─── COLD START OPTIMIZATION ──────────────────────────────────────────────
// Code OUTSIDE the handler runs only ONCE per container (on cold start).
// Reusing the DB client across warm invocations avoids reconnecting every time.
const client = new DynamoDBClient({ region: process.env.AWS_REGION || 'ap-south-1' });
const ddb = DynamoDBDocumentClient.from(client);

const TABLE_NAME = process.env.ORDERS_TABLE; // injected via environment variable

// ─── 1. HTTP API HANDLER (API Gateway → Lambda) ───────────────────────────
exports.httpHandler = async (event) => {
  try {
    // API Gateway HTTP API (payload v2.0) puts the method/path here
    const method = event.requestContext?.http?.method;
    const orderId = event.pathParameters?.orderId;

    if (!orderId) {
      // 400 for missing required input — fail fast, don't let DB call throw
      return { statusCode: 400, body: JSON.stringify({ error: 'orderId is required' }) };
    }

    if (method === 'GET') {
      // Fetch order from DynamoDB (reused client = faster warm invocations)
      const result = await ddb.send(
        new GetCommand({ TableName: TABLE_NAME, Key: { orderId } })
      );

      if (!result.Item) {
        return { statusCode: 404, body: JSON.stringify({ error: 'Order not found' }) };
      }

      return { statusCode: 200, body: JSON.stringify(result.Item) };
    }

    // Unsupported method
    return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  } catch (err) {
    // ALWAYS catch — an uncaught error in Lambda shows as a generic 500
    // with a stack trace leak unless you handle it yourself
    console.error('Lambda error:', err);
    return { statusCode: 500, body: JSON.stringify({ error: 'Internal server error' }) };
  }
};

// ─── 2. S3 EVENT-DRIVEN HANDLER (file upload trigger) ─────────────────────
exports.s3Handler = async (event) => {
  // S3 can batch multiple records in one invocation — process all of them
  const results = await Promise.allSettled(
    event.Records.map(async (record) => {
      const bucket = record.s3.bucket.name;
      const key = decodeURIComponent(record.s3.object.key.replace(/\+/g, ' '));

      console.log(`New file uploaded: s3://${bucket}/${key}`);

      // Example: record the upload in DynamoDB for audit trail
      await ddb.send(
        new PutCommand({
          TableName: TABLE_NAME,
          Item: { orderId: `upload-${Date.now()}`, bucket, key, uploadedAt: new Date().toISOString() },
        })
      );
    })
  );

  // Log any failures without crashing the whole batch (partial failure handling)
  results.forEach((r, i) => {
    if (r.status === 'rejected') {
      console.error(`Failed processing record ${i}:`, r.reason);
    }
  });
};

// ─── 3. SQS QUEUE HANDLER (async job processing) ──────────────────────────
exports.sqsHandler = async (event) => {
  // Each SQS message is a separate record; partial batch failures can be
  // reported back so only failed messages are retried (batchItemFailures)
  const batchItemFailures = [];

  for (const record of event.Records) {
    try {
      const body = JSON.parse(record.body); // SQS message body is a string
      console.log('Processing queued job:', body);
      // ... do the actual work (send email, update inventory, etc.)
    } catch (err) {
      console.error('Failed to process message:', record.messageId, err);
      batchItemFailures.push({ itemIdentifier: record.messageId }); // retry only this one
    }
  }

  return { batchItemFailures };
};
```

---

## 🟠 Express.js Integration

```javascript
// server.js — an EXISTING Express app, wrapped to run on Lambda unchanged.
// This is the standard way teams migrate a running Express API to serverless
// without rewriting routes: `serverless-http` adapts Express's (req, res) model
// to Lambda's (event, context) model.

const express = require('express');
const serverlessHttp = require('serverless-http'); // npm install serverless-http

const app = express();
app.use(express.json());

// Normal Express routes — exactly as you'd write for any server
app.get('/orders/:orderId', async (req, res) => {
  const { orderId } = req.params;
  // ... fetch order from DB (same code as a traditional server)
  res.json({ orderId, status: 'confirmed' });
});

app.post('/orders', async (req, res) => {
  const { items, userId } = req.body;
  // ... create order (same business logic, unchanged)
  res.status(201).json({ orderId: 'ord_123', items, userId });
});

// LOCAL DEVELOPMENT: run as a normal server with `node server.js`
if (require.main === module) {
  app.listen(3000, () => console.log('Local Express server on :3000'));
}

// LAMBDA DEPLOYMENT: export the wrapped handler — API Gateway calls THIS
// serverless-http translates API Gateway's event into an Express req/res,
// runs the full middleware chain, then translates res back into Lambda's
// expected {statusCode, headers, body} response shape.
module.exports.handler = serverlessHttp(app);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating a new DB connection inside the handler on every call
```javascript
// WRONG: new connection every single invocation — slow + exhausts DB connections
exports.handler = async (event) => {
  const client = new DynamoDBClient({ region: 'ap-south-1' }); // created every call!
  // ... use client
};

// CORRECT: create the client OUTSIDE the handler — reused across warm invocations
const client = new DynamoDBClient({ region: 'ap-south-1' }); // once per container
exports.handler = async (event) => {
  // ... use the already-created client
};
```

❌ **Mistake 2:** Not setting a timeout that matches the workload
```javascript
// WRONG: default Lambda timeout is only 3 seconds — a slow DB query or
// external API call gets killed mid-flight with no clear error
// (set in AWS console/serverless.yml, not in code, but the mistake is forgetting it)

// CORRECT: explicitly configure timeout based on the slowest expected operation
// serverless.yml:
// functions:
//   processOrder:
//     timeout: 15  # seconds — enough for a slow payment gateway call
//     memorySize: 256
```

❌ **Mistake 3:** Returning raw objects instead of the API Gateway response shape
```javascript
// WRONG: API Gateway expects a specific shape — this breaks the HTTP response
exports.handler = async (event) => {
  return { orderId: '123', status: 'ok' }; // missing statusCode/body!
};

// CORRECT: always return {statusCode, body} with body as a JSON STRING
exports.handler = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ orderId: '123', status: 'ok' }),
  };
};
```

---

## 🧠 Tricky Interview Question

**Q: Why does the SAME Lambda function sometimes respond in 5ms and sometimes take 800ms, for identical requests?**

```javascript
// server.js (same file every time)
exports.handler = async (event) => {
  const start = Date.now();
  const client = new DynamoDBClient({ region: 'ap-south-1' }); // outside? inside? matters!
  const result = await doWork(client, event);
  console.log(`Took ${Date.now() - start}ms`);
  return { statusCode: 200, body: JSON.stringify(result) };
};
```

**Answer:** This is the **cold start vs. warm start** problem. On a **cold start**, AWS has to: provision a new execution environment (micro-VM/container), download your code, start the Node.js runtime, run all the code OUTSIDE the handler (imports, DB client creation), and only then run the handler body — this can take 200ms-1s+ depending on package size and language runtime. On a **warm start**, AWS reuses an already-initialized environment from a previous invocation (if it hasn't been idle too long) — the handler runs immediately with everything already set up, giving 5-50ms responses. Mitigations: (1) keep deployment package small (fewer dependencies = faster init), (2) initialize DB clients/SDK objects OUTSIDE the handler so they're reused on warm starts, (3) use **Provisioned Concurrency** to keep a fixed number of environments pre-warmed for latency-sensitive APIs, (4) avoid bundling unused packages.

---

## ⚫ Interview Questions + Answers

**Q1: What is a "cold start" in AWS Lambda and how do you reduce it?**
A1: A cold start happens when AWS must create a brand-new execution environment for a function — downloading code, starting the runtime, and running top-level (outside-handler) code before the handler itself executes. This adds latency (hundreds of ms to a few seconds). Reduce it by: keeping the deployment package small, moving SDK/DB client initialization outside the handler, using a lighter runtime, avoiding unnecessary npm packages, and using Provisioned Concurrency for latency-critical functions.

**Q2: What are the key limits of AWS Lambda you must design around?**
A2: Max execution timeout: 15 minutes. Max memory: 10,240 MB (CPU scales with memory). Max deployment package: 50 MB zipped (250 MB unzipped) directly, or up to 10 GB via container images. Max payload (sync invocation, e.g. API Gateway): 6 MB request/response. Max /tmp storage: up to 10 GB (ephemeral, wiped between cold starts). Concurrent executions: default soft limit (often 1,000) shared across the account/region, can be raised. These limits mean Lambda is unsuited for long-running jobs, huge file processing in a single call, or very large payloads without chunking.

**Q3: When would you choose Lambda over a traditional Express server on EC2?**
A3: Choose Lambda for: bursty/unpredictable traffic (auto-scales instantly without pre-provisioning), event-driven tasks (S3 upload processing, queue consumers, scheduled cron jobs), low-traffic APIs where paying for 24/7 EC2 is wasteful, and teams wanting zero server/OS maintenance. Choose a traditional server when: you need WebSocket/long-lived connections, consistently high sustained traffic (EC2/containers become cheaper than per-invocation billing at scale), need for sub-10ms predictable latency without any cold-start risk, or heavy in-memory caching across requests (Lambda environments are ephemeral and not shared reliably).

**Q4: How does API Gateway + Lambda work together for an HTTP API?**
A4: API Gateway acts as the HTTP front door — it receives the HTTP request, matches it against configured routes/methods, and transforms it into a Lambda "event" object (containing path, query params, headers, body, etc.) via the Lambda proxy integration. It invokes the Lambda function synchronously, waits for the response, and expects a specific shape back (`{statusCode, headers, body}`), which it translates into the actual HTTP response sent to the client. This lets you build a full REST/HTTP API without running any server process yourself.

**Q5: What are some common event-driven triggers for Lambda besides API Gateway, and give a real use case for each?**
A5: **S3** — trigger on object upload, e.g. auto-resize a Swiggy restaurant's uploaded dish photo. **SQS** — process queued jobs asynchronously, e.g. sending order confirmation emails without blocking the main checkout request. **DynamoDB Streams** — react to table changes in real time, e.g. sync an order status change to a search index or send a push notification. **EventBridge (CloudWatch Events)** — scheduled/cron-like triggers, e.g. a nightly Lambda that generates a sales report. **SNS** — fan-out notifications, e.g. notify multiple downstream services when a payment is confirmed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Traffic is bursty, unpredictable, or low-volume (pay-per-use beats idle server cost)
- The workload is event-driven: file uploads, queue messages, scheduled jobs, webhooks
- You want zero server/OS maintenance and automatic scaling
- Individual tasks finish well within 15 minutes and don't need persistent connections

❌ Avoid when:
- You need WebSockets or long-lived persistent connections
- Traffic is consistently very high — dedicated servers/containers become cheaper at scale
- Latency must be sub-10ms with zero cold-start tolerance and Provisioned Concurrency cost isn't acceptable
- The task needs heavy shared in-memory state/caching across requests

---

## 📊 Visual Diagram
```
AWS LAMBDA REQUEST FLOW (API Gateway trigger):
────────────────────────────────────────────────────────────────────

  CLIENT                API GATEWAY              LAMBDA (your Node.js code)
    │                        │                           │
    │── GET /orders/123 ────▶│                           │
    │                        │── invoke(event) ─────────▶│
    │                        │                     [COLD START?]
    │                        │                     ┌───────────────┐
    │                        │                     │ new container  │
    │                        │                     │ load code       │
    │                        │                     │ run top-level   │
    │                        │                     │ code (DB init)  │
    │                        │                     └───────────────┘
    │                        │                     run handler(event)
    │                        │◀── {statusCode,body}─────│
    │◀── HTTP response ──────│                           │
    │                        │                           │
                        [container stays warm for a few minutes]
                        [next request reuses it = fast "warm start"]

EVENT-DRIVEN TRIGGERS:
   S3 upload ────────▶ Lambda (resize image)
   SQS message ──────▶ Lambda (process job)
   DynamoDB change ──▶ Lambda (sync search index)
   EventBridge cron ─▶ Lambda (nightly report)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lambda | Serverless function execution service | बिना server चलाए code run karne ki service |
| Handler | Entry-point function AWS calls | AWS द्वारा call होने वाला entry function |
| Cold Start | First invocation delay (new environment) | नया environment banने से hone wali delay |
| Warm Start | Fast reuse of existing environment | पहले से ready environment ka reuse |
| API Gateway | HTTP front door routing to Lambda | HTTP requests ko Lambda तक route करने वाला service |
| Trigger | Event source invoking Lambda | Lambda ko invoke karne wala event source |
| Provisioned Concurrency | Pre-warmed environments to avoid cold starts | पहले से warm रखे गए environments |
| Event Object | Trigger data passed to handler | Handler ko diya gaya trigger ka data |
| Timeout | Max execution duration allowed (≤15 min) | Max execution time allowed |

---

## ⚡ 3-Line Summary
**English:**
1. AWS Lambda runs your Node.js handler function only when triggered — no server to run 24/7, billed per invocation + execution time.
2. Triggers include API Gateway (HTTP), S3 (uploads), SQS (queues), DynamoDB Streams, and EventBridge (cron) — Lambda is ideal for bursty, event-driven workloads.
3. Cold starts add latency on new environments; reduce them by initializing DB/SDK clients outside the handler and keeping the package small.

**Hindi:**
1. AWS Lambda tumhara Node.js handler sirf trigger hone par chalata hai — koi server 24/7 nahi, billing per invocation + execution time ke hisaab se।
2. Triggers mein API Gateway (HTTP), S3 (uploads), SQS (queues), DynamoDB Streams, EventBridge (cron) shamil hain — bursty, event-driven kaam ke liye perfect।
3. Cold start naye environment par latency badhata hai; DB/SDK client ko handler ke bahar banakar aur package chhota rakhkar ise kam kiya ja sakta hai।

---

## ➡️ Next Topic
**266. Serverless Framework** — Lambda functions ko Infrastructure-as-Code (serverless.yml) se deploy karna, local testing aur deployment workflow automate karna।
