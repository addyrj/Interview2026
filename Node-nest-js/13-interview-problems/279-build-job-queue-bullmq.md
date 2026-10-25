# 279. Build Job Queue (BullMQ)
# हिंदी में: BullMQ से Job Queue बनाना

---

## 🔵 Simple Definition (English)
**BullMQ** is a Redis-backed job queue library for Node.js, letting you offload slow or resource-intensive work (sending emails, generating reports, processing images) to background **workers** instead of blocking the HTTP request. The API responds instantly, and a separate worker process picks up and executes the job asynchronously.

## 🔵 सरल परिभाषा (Hindi)
**BullMQ** एक Redis-backed job queue library है Node.js के लिए, जो slow/resource-intensive काम (emails भेजना, reports generate करना, image processing) को background **workers** पर offload करती है, HTTP request को block किए बिना। API instantly respond करता है, और अलग worker process job को asynchronously pick करके execute करता है।

---

## 🔴 Problem it Solves
If an API endpoint does slow work synchronously (e.g. sending 10,000 promotional emails, generating a large PDF report), the HTTP request hangs until it's done — users see a spinner for 30+ seconds, and the server thread/connection is tied up, limiting throughput. Job queues decouple "accept the request" from "do the work": the API immediately responds "job accepted, we'll process it," pushes the job onto a queue, and a separate worker (potentially on a different machine) processes it in the background, with retries if it fails.

## 🔴 यह क्यों बना? (Hindi)
अगर API endpoint synchronously slow काम करे (10,000 promotional emails भेजना, बड़ी PDF report बनाना), तो HTTP request तब तक hang रहता है — users 30+ सेकंड तक spinner देखते हैं। Job queues "request accept करना" को "काम करना" से अलग करती हैं: API immediately respond करता है "job accepted", queue में job डालता है, और अलग worker (शायद अलग machine पर) background में process करता है, fail होने पर retries के साथ।

---

## 🟢 How it Works — Step by Step

Step 1 → Install BullMQ and connect to Redis (`npm install bullmq`) — Redis stores the queue state.
Step 2 → Create a **Queue** instance: `new Queue('email-queue', { connection })` — this is what your API code uses to ADD jobs.
Step 3 → `queue.add('send-welcome-email', { userId, email })` — enqueues a job with a name and data payload; returns immediately.
Step 4 → Create a separate **Worker** process: `new Worker('email-queue', processorFn, { connection })` — this is what actually RUNS jobs, typically in its own Node process (not the web server process).
Step 5 → The worker's processor function receives each job, does the actual work (call an email API), and either resolves (job succeeds) or throws (job fails, triggering retry logic).
Step 6 → Configure **retries** with exponential backoff: `{ attempts: 3, backoff: { type: 'exponential', delay: 1000 } }` — transient failures (e.g. email API temporarily down) get retried automatically.
Step 7 → Use **events** (`completed`, `failed`, `progress`) to track job status, and a **QueueEvents** listener or dashboard (Bull Board) for monitoring.
Step 8 → Jobs can be delayed (`{ delay: 60000 }` — run in 1 minute), prioritized, or scheduled as repeatable (cron-like) jobs.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → BullMQ install करो, Redis से connect करो।
Step 2 → **Queue** instance बनाओ — API code इसी से jobs ADD करता है।
Step 3 → `queue.add(name, data)` — job enqueue, immediately return।
Step 4 → अलग **Worker** process बनाओ — ये actually jobs RUN करता है।
Step 5 → Worker का processor function job पढ़ता है, actual काम करता है, resolve (success) या throw (fail)।
Step 6 → **Retries** configure करो exponential backoff के साथ।
Step 7 → **Events** (`completed`, `failed`, `progress`) से status track करो, monitoring dashboard use करो।
Step 8 → Jobs delayed, prioritized, या repeatable (cron-like) हो सकते हैं।

---

## 🟡 Real World Example
**Paytm's** invoice generation system uses BullMQ: when a user requests their monthly transaction statement (potentially thousands of transactions, requiring PDF rendering), the API immediately returns `{ status: 'processing', jobId: 'abc123' }` instead of making the user wait. A separate fleet of worker processes (scaled independently from the web servers based on queue depth) pulls jobs, generates the PDF, uploads it to S3, and sends a push notification with the download link once done. If PDF generation fails due to a transient rendering library crash, BullMQ automatically retries up to 3 times before marking it permanently failed and alerting the on-call engineer.

## 🟡 Real Example Hindi mein
**Paytm** का invoice generation system BullMQ use करता है: जब user monthly statement request करता है, API immediately `{ status: 'processing', jobId }` return करता है, user को wait नहीं कराता। अलग worker processes (queue depth के आधार पर independently scaled) jobs pull करते हैं, PDF बनाते हैं, S3 पर upload करते हैं, download link के साथ notification भेजते हैं। Transient failure पर BullMQ automatically 3 बार तक retry करता है।

---

## 💻 Code Example — Basic

```javascript
// basic-queue.js — minimal producer + worker
// npm install bullmq ioredis
// Requires a local Redis server running
// Run producer: node basic-queue.js add
// Run worker:   node basic-queue.js worker

const { Queue, Worker } = require('bullmq');

const connection = { host: '127.0.0.1', port: 6379 };
const queueName = 'email-queue';

async function addJob() {
  const queue = new Queue(queueName, { connection });

  // Add a job with a name and data payload — returns immediately
  await queue.add('send-welcome-email', { userId: 101, email: 'user@example.com' });
  console.log('Job added to queue');

  await queue.close();
}

function startWorker() {
  const worker = new Worker(
    queueName,
    async (job) => {
      // This function RUNS the job — simulating sending an email
      console.log(`Processing job ${job.id}: sending email to ${job.data.email}`);
      await new Promise((resolve) => setTimeout(resolve, 1000)); // simulate API call
      console.log(`Email sent to ${job.data.email}`);
      return { sent: true }; // becomes the job's return value
    },
    { connection }
  );

  worker.on('completed', (job) => console.log(`Job ${job.id} completed`));
  worker.on('failed', (job, err) => console.error(`Job ${job.id} failed:`, err.message));

  console.log('Worker listening for jobs...');
}

const mode = process.argv[2];
if (mode === 'add') addJob();
else if (mode === 'worker') startWorker();
else console.log('Usage: node basic-queue.js [add|worker]');
```

## 💻 Code Example — Advanced

```javascript
// advanced-queue.js — retries, backoff, delayed jobs, progress tracking
// npm install bullmq ioredis

const { Queue, Worker, QueueEvents } = require('bullmq');

const connection = { host: '127.0.0.1', port: 6379 };
const queueName = 'report-generation';

// ─── PRODUCER: API code that enqueues jobs ──────────────────────────────────
async function enqueueReportJob(userId, reportType) {
  const queue = new Queue(queueName, { connection });

  const job = await queue.add(
    'generate-report',
    { userId, reportType },
    {
      attempts: 3,                                   // retry up to 3 times on failure
      backoff: { type: 'exponential', delay: 2000 },  // wait 2s, 4s, 8s between retries
      removeOnComplete: { age: 3600 },                // auto-cleanup completed jobs after 1hr
      removeOnFail: { age: 86400 },                   // keep failed jobs 24hrs for debugging
    }
  );

  await queue.close();
  return job.id; // return this to the client so they can poll status
}

// ─── WORKER: separate process that does the actual work ───────────────────
function startReportWorker() {
  const worker = new Worker(
    queueName,
    async (job) => {
      const { userId, reportType } = job.data;

      // Report progress — useful for long-running jobs, pollable by clients
      await job.updateProgress(10);
      console.log(`Fetching data for user ${userId}...`);
      await new Promise((r) => setTimeout(r, 500));

      await job.updateProgress(50);
      console.log(`Rendering ${reportType} report...`);

      // Simulate occasional transient failure to demonstrate retry behavior
      if (Math.random() < 0.3) {
        throw new Error('PDF rendering service temporarily unavailable');
      }

      await job.updateProgress(90);
      const reportUrl = `https://cdn.example.com/reports/${userId}-${Date.now()}.pdf`;

      await job.updateProgress(100);
      return { reportUrl }; // this becomes job.returnvalue, accessible later
    },
    { connection, concurrency: 5 } // process up to 5 jobs in parallel per worker instance
  );

  worker.on('completed', (job, result) => {
    console.log(`Job ${job.id} done:`, result);
    // e.g. send a push notification to the user with result.reportUrl
  });

  worker.on('failed', (job, err) => {
    // After ALL retry attempts exhausted, this fires — alert on-call/log to Sentry
    console.error(`Job ${job.id} permanently failed after ${job.attemptsMade} attempts:`, err.message);
  });

  return worker;
}

// ─── CHECKING JOB STATUS (e.g. from an API endpoint) ───────────────────────
async function getJobStatus(jobId) {
  const queue = new Queue(queueName, { connection });
  const job = await queue.getJob(jobId);
  if (!job) return { status: 'not_found' };

  const state = await job.getState(); // 'waiting' | 'active' | 'completed' | 'failed' | 'delayed'
  await queue.close();
  return { status: state, progress: job.progress, result: job.returnvalue };
}

module.exports = { enqueueReportJob, startReportWorker, getJobStatus };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { enqueueReportJob, getJobStatus } = require('./advanced-queue');

const app = express();
app.use(express.json());

// Client requests a report — API responds IMMEDIATELY, doesn't wait for generation
app.post('/api/reports', async (req, res) => {
  const { userId, reportType } = req.body;
  const jobId = await enqueueReportJob(userId, reportType);

  // 202 Accepted — request accepted, processing is async
  res.status(202).json({
    message: 'Report generation started',
    jobId,
    statusUrl: `/api/reports/${jobId}/status`,
  });
});

// Client polls this endpoint to check progress/completion
app.get('/api/reports/:jobId/status', async (req, res) => {
  const status = await getJobStatus(req.params.jobId);
  res.json(status);
});

app.listen(3000, () => console.log('API server on port 3000'));

// In a SEPARATE process (worker.js), run:
// const { startReportWorker } = require('./advanced-queue');
// startReportWorker();
// Deploy this as its own PM2 process / container, scaled independently from the API
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running the worker in the SAME process as the web server
✅ Correct: Run workers as separate processes (own PM2 app, own container) — a heavy job shouldn't compete with the Event Loop for incoming HTTP requests, and you want to scale API servers and workers independently based on their own load patterns.

```javascript
// Wrong: worker started inside the same server.js that handles HTTP requests
const app = express();
new Worker('queue', processorFn, { connection }); // competes with request handling!
app.listen(3000);

// Right: server.js only enqueues; worker.js (separate process/container) only processes
// server.js:  queue.add('job-name', data);
// worker.js:  new Worker('queue', processorFn, { connection });
```

❌ Mistake 2: Not handling job failures — silent data loss when retries exhaust
✅ Correct: Listen for the `failed` event and alert/log — a job that fails all 3 retries and is never looked at means that email/report/payment-confirmation silently never happened.

```javascript
// Wrong: no failure handling — job disappears from view after retries exhaust
const worker = new Worker(queueName, processorFn, { connection });

// Right: explicit failure handling with alerting
worker.on('failed', (job, err) => {
  console.error(`Job ${job.id} failed permanently:`, err.message);
  // sendToSentry(err); notifyOnCall(`Job ${job.id} failed: ${job.name}`);
});
```

---

## 🧠 Tricky Interview Question

```javascript
// A worker crashes (process killed) WHILE actively processing a job.
// What happens to that job?
const worker = new Worker(queueName, async (job) => {
  await doSomethingThatTakes10Seconds(job.data);
  // process gets killed (OOM, deploy restart) at second 5, mid-job
}, { connection });
```
Answer: BullMQ uses a "lock" mechanism — while a worker is processing a job, it periodically renews a lock (`lockDuration`, default 30s) signaling "I'm still alive and working on this." If the worker process dies without releasing the lock (crash, not graceful shutdown), the lock eventually EXPIRES (after `lockDuration` with no renewal), and BullMQ considers the job "stalled." A stalled job is automatically moved back to the waiting state and picked up by another available worker (or the same worker after restart) — it gets RE-PROCESSED from the beginning, not resumed mid-way. This means job processors must be designed to be safely re-runnable (idempotent) — e.g. if the job sends an email, a crash-and-retry could send a duplicate email unless you track "already sent" state separately (e.g. check a DB flag before sending).

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between a Queue, a Worker, and a Job in BullMQ?
A1: **Queue** is the producer-side API — used to ADD jobs (`queue.add()`) and inspect/manage the queue (pause, get job counts). **Worker** is the consumer-side process that PULLS jobs off the queue and executes a processor function on each. **Job** is a single unit of work with a name, data payload, options (retries, delay, priority), and lifecycle state (waiting → active → completed/failed). Multiple Worker instances (even across different machines) can connect to the same queue and share the workload — BullMQ handles distributing jobs so no two workers process the same job simultaneously.

Q2: How do you implement job prioritization in BullMQ?
A2: Pass a `priority` option when adding a job: `queue.add('name', data, { priority: 1 })` — lower numbers mean HIGHER priority (processed first). Use cases: a premium user's report generation request should jump ahead of free-tier users' queued jobs. Note: priority adds some overhead (BullMQ needs to maintain a sorted structure) so it's used selectively, not for every queue.

Q3: How would you prevent duplicate jobs from being processed twice (e.g. a user double-clicking "Generate Report")?
A3: Use a deterministic `jobId` based on the business key instead of letting BullMQ auto-generate one: `queue.add('generate-report', data, { jobId: `report-${userId}-${reportType}-${date}` })`. If a job with that exact ID already exists and hasn't completed, BullMQ will reject/ignore the duplicate add rather than creating a second job — a form of idempotency at the queue level.

Q4: What's the purpose of `removeOnComplete`/`removeOnFail` options, and why not just keep all job history forever?
A4: By default, BullMQ keeps completed/failed job records in Redis indefinitely, which grows Redis memory usage unboundedly over time in a high-throughput system. `removeOnComplete`/`removeOnFail` (with `age` or `count` limits) auto-prune old job records, keeping Redis memory bounded while still retaining recent history for debugging. Production systems almost always set these — unbounded growth is a common "it worked in testing but Redis ran out of memory after 3 months in production" incident.

Q5: How does BullMQ's retry with exponential backoff help with transient failures, and when is it the WRONG choice?
A5: Exponential backoff (`{ attempts: 3, backoff: { type: 'exponential', delay: 1000 } }`) retries after increasing delays (1s, 2s, 4s...), giving a temporarily-down dependency (email API, payment gateway) time to recover rather than hammering it immediately. It's the WRONG choice for errors that are NOT transient — e.g. a validation error (malformed job data) will fail identically on every retry, wasting time/resources; such errors should be caught and NOT re-thrown (or use a specific non-retryable error type) so the job fails immediately instead of retrying 3 times pointlessly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any slow operation that shouldn't block the HTTP response (emails, reports, image/video processing, bulk notifications)
- Work that benefits from retry-on-failure semantics (calling flaky third-party APIs)
- You need to scale background processing capacity independently from your web servers

❌ Avoid when:
- The operation is fast enough to complete within a normal request-response cycle (sub-second) — adding a queue is unnecessary complexity
- You need the result synchronously in the SAME request (can't respond "processing" and have the client poll) — though even here, polling/websocket patterns often work better than blocking

---

## 📊 Visual Diagram
```
API SERVER (producer)              REDIS (queue storage)         WORKER PROCESS(ES)
──────────────────────              ──────────────────────        ────────────────────
POST /api/reports
   │
   ▼
queue.add('generate-report', data) ──► [waiting: job#1] ◄──pull── Worker picks up job#1
   │                                                                    │
   ▼                                                                    ▼
202 Accepted, jobId returned                                   [active: job#1]
   │                                                                    │
   │  (client polls status)                                     process job (slow work)
   │                                                                    │
   ▼                                                              success? ──► [completed]
GET /status → "completed", result                                  │
                                                                      fail?  ──► retry with backoff
                                                                              (up to N attempts)
                                                                      all retries fail ──► [failed]
                                                                              → alert on-call
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Queue | Producer-side API to add jobs | Jobs add करने का producer-side API |
| Worker | Process that executes queued jobs | Queued jobs execute करने वाला process |
| Job | Single unit of background work | Background काम की एक unit |
| Backoff | Increasing delay between retries | Retries के बीच बढ़ता delay |
| Stalled Job | Job whose worker died mid-processing | Worker crash होने पर अटका job |
| Idempotent | Safe to run multiple times with same result | कई बार चलाने पर भी same result |

---

## ⚡ 3-Line Summary
English: 1. BullMQ offloads slow work to background workers via a Redis-backed queue, letting the API respond instantly instead of blocking. 2. Always run workers as separate processes from the web server, and handle `failed` events explicitly — silent job failures mean silent business-logic failures. 3. Design job processors to be idempotent, since crashed/stalled jobs are re-processed from scratch, not resumed mid-way.
Hindi: 1. BullMQ Redis-backed queue के through slow काम background workers पर offload करता है, API instantly respond करता है। 2. Workers हमेशा web server से अलग process में चलाओ, `failed` events explicitly handle करो। 3. Job processors को idempotent design करो, crashed jobs scratch से re-process होते हैं, resume नहीं।

---

## ➡️ Next Topic
**280. Build Webhook Handler** — incoming webhooks (Razorpay/Stripe-style) को securely receive और verify करना।
