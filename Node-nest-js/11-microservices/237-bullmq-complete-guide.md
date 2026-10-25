# 237. BullMQ — Complete Guide
# हिंदी में: BullMQ — Complete Guide

---

## 🔵 Simple Definition (English)
BullMQ is the modern, actively maintained successor to Bull — a Redis-backed job queue library for Node.js with a cleaner architecture, better TypeScript support, atomic Redis Lua-script operations for reliability, and advanced features like job flows (parent-child dependencies), rate limiting, and improved repeatable jobs.

## 🔵 सरल परिभाषा (Hindi)
BullMQ Bull का modern, actively maintained successor है — Node.js के लिए एक Redis-backed job queue library जिसमें cleaner architecture, better TypeScript support, reliability के लिए atomic Redis Lua-script operations, और advanced features जैसे job flows (parent-child dependencies), rate limiting, और improved repeatable jobs होते हैं।

---

## 🔴 Problem it Solves
Bull (the original) works well but has some architectural limitations: less robust handling of edge cases around atomicity, weaker TypeScript support, and no native way to express job dependencies (e.g., "run job B only after jobs A1, A2, A3 all complete"). BullMQ rewrites the core with atomic Redis operations (avoiding race conditions), first-class TypeScript types, and a Flow Producer API for defining complex job dependency graphs — solving real production pain points like orchestrating multi-step pipelines (e.g., "resize image, THEN generate thumbnail, THEN notify user") without hand-rolled coordination logic.

## 🔴 यह क्यों बना? (Hindi)
Bull (original) अच्छे से काम करता है लेकिन कुछ architectural limitations हैं: atomicity के edge cases को less robust तरीके से handle करना, weaker TypeScript support, और job dependencies express करने का कोई native तरीका नहीं (जैसे "job B सिर्फ तब चलाओ जब jobs A1, A2, A3 सब complete हो जाएं")। BullMQ core को atomic Redis operations से rewrite करता है (race conditions avoid करना), first-class TypeScript types, और complex job dependency graphs define करने के लिए Flow Producer API — multi-step pipelines (जैसे "image resize करो, FIR thumbnail generate करो, FIR user को notify करो") को hand-rolled coordination logic के बिना orchestrate करने जैसी real production problems solve करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create a `Queue` instance (for adding jobs) and a separate `Worker` instance (for processing jobs) — BullMQ explicitly separates these two concerns (unlike Bull's single Queue object doing both).
Step 2 → Jobs are added via `queue.add(name, data, opts)`; BullMQ stores job state in Redis using atomic Lua scripts.
Step 3 → A `Worker` connects and processes jobs with a handler function; multiple workers can run across processes/machines for horizontal scaling.
Step 4 → `QueueEvents` lets you listen to job lifecycle events (completed, failed, progress) from any process, not just the worker.
Step 5 → `FlowProducer` lets you define parent-child job trees — a parent job only starts once all its children complete, enabling pipeline orchestration.
Step 6 → Built-in rate limiting (`limiter` option) and repeatable jobs (cron-like) are configured declaratively on the queue/worker.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक `Queue` instance बनाओ (jobs add करने के लिए) और एक अलग `Worker` instance (jobs process करने के लिए) — BullMQ इन दोनों concerns को explicitly अलग करता है (Bull के single Queue object के विपरीत जो दोनों करता है)।
Step 2 → Jobs `queue.add(name, data, opts)` से add होते हैं; BullMQ job state को Redis में atomic Lua scripts से store करता है।
Step 3 → एक `Worker` connect होकर handler function से jobs process करता है; horizontal scaling के लिए processes/machines में multiple workers चल सकते हैं।
Step 4 → `QueueEvents` किसी भी process से job lifecycle events (completed, failed, progress) सुनने देता है, सिर्फ worker से नहीं।
Step 5 → `FlowProducer` parent-child job trees define करने देता है — parent job सिर्फ तब शुरू होता है जब उसके सभी children complete हो जाएं, pipeline orchestration enable करता है।
Step 6 → Built-in rate limiting (`limiter` option) और repeatable jobs (cron-like) declaratively queue/worker पर configure होते हैं।

---

## 🟡 Real World Example
**Paytm video KYC pipeline:** When a user submits a video for KYC verification, the process involves multiple dependent steps: (1) extract frames from video, (2) run face-detection on each frame, (3) run liveness-check, (4) only after ALL of those succeed, run final approval scoring. BullMQ's `FlowProducer` models this exactly as a job tree — the "final approval" parent job automatically waits for all child jobs (frame extraction, face detection, liveness check) to complete before it even starts, without any manual polling/coordination code.

## 🟡 Real Example Hindi mein
**Paytm video KYC pipeline:** जब user KYC verification के लिए video submit करता है, process में multiple dependent steps होते हैं: (1) video से frames extract करना, (2) हर frame पर face-detection run करना, (3) liveness-check run करना, (4) इन सब के succeed होने के बाद ही, final approval scoring run करना। BullMQ का `FlowProducer` इसे exactly एक job tree जैसे model करता है — "final approval" parent job automatically तब तक wait करता है जब तक सभी child jobs (frame extraction, face detection, liveness check) complete न हो जाएं, बिना किसी manual polling/coordination code के।

---

## 💻 Code Example — Basic

```javascript
// bullmq-basic.js
// Run: node bullmq-basic.js (requires Redis + npm i bullmq)

const { Queue, Worker } = require('bullmq');

const connection = { host: '127.0.0.1', port: 6379 };

// ─── QUEUE: adding jobs (producer side) ──────────────────────────────────────
const notificationQueue = new Queue('notifications', { connection });

async function sendNotification(userId, message) {
  await notificationQueue.add('push-notification', { userId, message });
  console.log('Notification job added for user:', userId);
}

// ─── WORKER: processing jobs (consumer side, separate from Queue) ───────────
const worker = new Worker('notifications', async (job) => {
  const { userId, message } = job.data;
  console.log(`Sending push notification to ${userId}: ${message}`);
  await new Promise(r => setTimeout(r, 500));   // simulate push notification API call
  return { delivered: true };
}, { connection });

worker.on('completed', (job) => console.log(`Job ${job.id} completed`));
worker.on('failed', (job, err) => console.error(`Job ${job.id} failed:`, err.message));

sendNotification('user_42', 'Your order has shipped!');
```

## 💻 Code Example — Advanced

```javascript
// bullmq-flow-advanced.js — job dependencies (flows), rate limiting, repeatable jobs
const { Queue, Worker, FlowProducer } = require('bullmq');

const connection = { host: '127.0.0.1', port: 6379 };
const flowProducer = new FlowProducer({ connection });

// ─── FLOW: parent job waits for children to complete ────────────────────────
async function startKycPipeline(videoId) {
  const flow = await flowProducer.add({
    name: 'final-approval',
    queueName: 'kyc-approval',
    data: { videoId },
    children: [
      { name: 'extract-frames', queueName: 'kyc-processing', data: { videoId } },
      { name: 'face-detection', queueName: 'kyc-processing', data: { videoId } },
      { name: 'liveness-check', queueName: 'kyc-processing', data: { videoId } },
    ],
  });
  console.log('KYC pipeline started, parent job:', flow.job.id);
}

// Worker for child processing jobs — can run with controlled concurrency
const processingWorker = new Worker('kyc-processing', async (job) => {
  console.log(`Running ${job.name} for video ${job.data.videoId}`);
  await new Promise(r => setTimeout(r, 1000));
  return { step: job.name, passed: true };
}, { connection, concurrency: 3 });

// Worker for the final approval — only runs after ALL children (above) complete
const approvalWorker = new Worker('kyc-approval', async (job) => {
  // job.getChildrenValues() gives access to results from all child jobs
  const childResults = await job.getChildrenValues();
  console.log('All child steps done, results:', childResults);
  console.log(`Running final approval for video ${job.data.videoId}`);
  return { approved: true };
}, { connection });

// ─── RATE LIMITING: process at most 10 jobs per second (e.g., 3rd-party API limit) ──
const rateLimitedQueue = new Queue('sms-sending', { connection });
const smsWorker = new Worker('sms-sending', async (job) => {
  console.log('Sending SMS to', job.data.phone);
}, {
  connection,
  limiter: { max: 10, duration: 1000 },   // max 10 jobs per 1000ms across all workers
});

// ─── REPEATABLE JOB: cron-like scheduling ────────────────────────────────────
async function scheduleDailyReport() {
  await rateLimitedQueue.add('daily-report', {}, {
    repeat: { pattern: '0 9 * * *' },   // every day at 9 AM
  });
}

startKycPipeline('video_123');
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { Queue, QueueEvents } = require('bullmq');

const app = express();
app.use(express.json());

const connection = { host: '127.0.0.1', port: 6379 };
const reportQueue = new Queue('report-generation', { connection });
const queueEvents = new QueueEvents('report-generation', { connection });

app.post('/reports', async (req, res) => {
  const job = await reportQueue.add('generate-report', { userId: req.body.userId });
  res.status(202).json({ jobId: job.id });
});

// Use QueueEvents (works even from a process that isn't the worker) to track completion
app.get('/reports/:jobId/wait', async (req, res) => {
  const job = await reportQueue.getJob(req.params.jobId);
  if (!job) return res.status(404).json({ error: 'Job not found' });

  try {
    // waitUntilFinished resolves/rejects based on QueueEvents — works across processes
    const result = await job.waitUntilFinished(queueEvents, 30000);   // 30s timeout
    res.json({ status: 'completed', result });
  } catch (err) {
    res.status(500).json({ status: 'failed', error: err.message });
  }
});

app.listen(3000, () => console.log('Report API (BullMQ) on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mixing Bull and BullMQ Redis key formats (they're NOT compatible)
✅ Correct: Migrate fully to BullMQ (or use separate Redis key prefixes) — don't let Bull and BullMQ share the same queue name/keys

```javascript
// Wrong — Bull and BullMQ use different internal Redis data structures for the "same" queue name
const bullQueue = new (require('bull'))('orders');
const bullmqQueue = new (require('bullmq').Queue)('orders');   // will NOT see Bull's jobs correctly

// Right — pick one library per queue; migrate fully, don't run both against the same queue name
```

❌ Mistake 2: Creating a new `Queue`/`Worker` connection per request instead of reusing a single instance
✅ Correct: Instantiate Queue/Worker once at startup and reuse — they manage their own Redis connections efficiently

```javascript
// Wrong
app.post('/jobs', async (req, res) => {
  const queue = new Queue('jobs', { connection });   // new connection every request!
  await queue.add('task', req.body);
});

// Right
const queue = new Queue('jobs', { connection });   // created once, outside the handler
app.post('/jobs', async (req, res) => { await queue.add('task', req.body); });
```

---

## 🧠 Tricky Interview Question

```javascript
// In a BullMQ flow, the parent job is "final-approval" with 3 children.
// One child job fails permanently (exhausts all retry attempts).
// Does the parent job ever run?
```
Answer: No — by default, a parent job in a BullMQ flow only proceeds once ALL children reach a `completed` state. If a child permanently fails, the parent remains stuck waiting (it does not auto-run or auto-fail unless you explicitly configure failure propagation / check child states). In production, you typically add monitoring/alerting on failed child jobs and a mechanism (e.g., a periodic check or `failParentOnFailure` option in newer BullMQ versions) to handle this case — otherwise the parent job queue entry can sit indefinitely waiting on a child that will never complete.

---

## ⚫ Interview Questions + Answers

Q1: What are the main improvements of BullMQ over Bull?
A1: BullMQ separates `Queue` (adding jobs) and `Worker` (processing jobs) into distinct classes for clearer architecture, uses atomic Lua-script-based Redis operations for stronger reliability/consistency guarantees, has first-class TypeScript support, supports job "Flows" (parent-child dependency graphs via `FlowProducer`), has more robust rate limiting, and is actively maintained (Bull is in maintenance-only mode). BullMQ is the recommended choice for new projects.

Q2: What is a "Flow" in BullMQ and what problem does it solve?
A2: A Flow is a tree of jobs where a parent job depends on one or more child jobs completing first. It solves the problem of orchestrating multi-step pipelines (e.g., "do steps A, B, C in parallel, then only run step D once all three finish") without hand-rolling coordination logic (like manually polling Redis or using a separate counter to track "how many of my sub-tasks are done"). The parent job automatically becomes processable only once all its children are `completed`, and can access their results via `job.getChildrenValues()`.

Q3: How does BullMQ handle rate limiting, and why is it useful?
A3: The `limiter` option on a Worker (`{ max: N, duration: ms }`) caps how many jobs the worker(s) process within a time window, regardless of how many jobs are waiting. This is essential when the job's work calls a third-party API with a strict rate limit (e.g., an SMS gateway allowing only 10 requests/sec) — without it, BullMQ would process jobs as fast as possible and get the API calls throttled/rejected.

Q4: Why does BullMQ separate `Queue` and `Worker` into different classes instead of one object (like Bull)?
A4: This separation reflects the real architectural split in production: the producer (e.g., a web API adding jobs) often runs in a completely different process/service than the consumer (dedicated worker processes). By making `Queue` (producer-facing, lightweight) and `Worker` (consumer-facing, does the actual processing) distinct, BullMQ makes it natural and type-safe to import only what each process needs — an API server only needs `Queue`, while a worker service only needs `Worker`.

Q5: How do repeatable jobs work in BullMQ, and what's a caveat to watch for?
A5: Repeatable jobs are scheduled via a cron pattern or fixed interval (`{ repeat: { pattern: '0 9 * * *' } }` or `{ repeat: { every: 60000 } }`), and BullMQ's internal scheduler automatically re-adds the job to the queue at each scheduled time, without needing an external cron daemon. A key caveat: if you call `queue.add()` with the same repeat options multiple times (e.g., on every app restart), it can create duplicate repeatable job schedulers unless you use a consistent `jobId`/key — so repeatable job registration should typically happen once, idempotently, not on every deploy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Starting a NEW project needing a Redis-backed job queue (preferred over Bull now)
- You need job dependency orchestration (Flows) for multi-step pipelines
- You want strong TypeScript support and active library maintenance

❌ Avoid when:
- You have an existing, stable Bull-based system and migration cost outweighs the benefit (though migration is often worthwhile long-term)
- Your use case needs Kafka-style high-throughput event streaming with replay, not task-queue semantics

---

## 📊 Visual Diagram
```
BullMQ Flow example (KYC pipeline):

                ┌───────────────────┐
                │ final-approval     │  (parent — waits for ALL children)
                └─────────┬─────────┘
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
 extract-frames      face-detection       liveness-check
  (child job)          (child job)          (child job)

Parent job becomes processable ONLY when all 3 children are "completed".
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Queue | Producer-facing API for adding jobs | Jobs add करने का producer-facing API |
| Worker | Consumer that processes jobs | Jobs process करने वाला consumer |
| FlowProducer | API for creating parent-child job trees | Parent-child job trees बनाने का API |
| QueueEvents | Listen to job events from any process | किसी भी process से job events सुनना |
| Rate limiter | Caps job processing rate | Job processing rate को cap करना |
| Repeatable job | Cron-like recurring job | Cron जैसा recurring job |

---

## ⚡ 3-Line Summary
**English:**
1. BullMQ is the modern, TypeScript-first successor to Bull, with Queue and Worker as separate classes and atomic Redis operations.
2. FlowProducer enables parent-child job dependency graphs, solving multi-step pipeline orchestration cleanly.
3. Built-in rate limiting and improved repeatable jobs make BullMQ suitable for production-grade background processing.

**Hindi:**
1. BullMQ Bull का modern, TypeScript-first successor है, Queue और Worker अलग classes के रूप में और atomic Redis operations के साथ।
2. FlowProducer parent-child job dependency graphs enable करता है, multi-step pipeline orchestration को cleanly solve करता है।
3. Built-in rate limiting और improved repeatable jobs BullMQ को production-grade background processing के लिए suitable बनाते हैं।

---

## ➡️ Next Topic
**238. Cron Jobs in Node (node-cron)** — Simple time-based scheduled tasks without a full job queue.
