# 83. CPU Intensive Tasks — How to Handle
# हिंदी में: CPU Intensive Tasks — कैसे Handle करें

---

## 🔵 Simple Definition (English)
CPU-intensive tasks (image resizing, PDF generation, large data transformation, complex calculations, encryption) are a poor fit for Node.js's single-threaded event loop — running them directly blocks everything. The solution is to offload them using **`worker_threads`** (for in-process parallelism), **`child_process`** (separate OS processes), the **`cluster`** module (multi-process scaling), or external services/queues (for very heavy workloads).

## 🔵 सरल परिभाषा (Hindi)
CPU-intensive tasks (image resizing, PDF generation, बड़ा data transformation, complex calculations, encryption) Node.js के single-threaded event loop के लिए सही fit नहीं हैं — directly चलाने से सब कुछ block हो जाता है। Solution है इन्हें offload करना **`worker_threads`** (in-process parallelism), **`child_process`** (अलग OS processes), **`cluster`** module (multi-process scaling), या external services/queues से।

---

## 🔴 Problem it Solves
```
THE MISMATCH:
  Node.js excels at I/O-BOUND workloads (lots of waiting on network/disk,
  little actual CPU work) — the event loop model shines here.

  But CPU-BOUND workloads (lots of actual computation, little waiting)
  are the OPPOSITE of what Node's single-threaded model is good at —
  one heavy computation blocks EVERYTHING else.

OPTIONS TO HANDLE CPU-INTENSIVE WORK:
  1. worker_threads   → spin up additional threads WITHIN the same
                         process, each with its own V8 instance +
                         event loop; good for moderate CPU work,
                         low overhead, can share memory (SharedArrayBuffer)
  2. child_process     → spawn a SEPARATE OS process (different memory
                         space); good for running other languages/tools,
                         CPU isolation, but higher overhead than workers
  3. cluster module    → fork MULTIPLE Node processes sharing the SAME
                         port, utilizing multi-core CPUs for handling
                         MORE REQUESTS (not for splitting ONE heavy task)
  4. External queue/service → offload to a dedicated worker service
                         (e.g., AWS Lambda, a Python microservice, a
                         job queue like BullMQ) for very heavy/specialized work
```

## 🔴 यह क्यों बना? (Hindi)
```
Node.js I/O-bound workloads में अच्छा है (ज्यादा wait, कम actual compute)
CPU-bound workloads (ज्यादा compute) इसके single-threaded model के विपरीत हैं
Solutions: worker_threads (same process में extra threads),
child_process (अलग process), cluster (multi-core पर ज्यादा requests handle),
external queue/service (बहुत heavy काम के लिए)
```

---

## 🟢 How it Works — Step by Step

```
worker_threads APPROACH:
Step 1 → Identify the CPU-heavy function (e.g., image resize, hash,
          complex report generation)
Step 2 → Move that function into a SEPARATE file (worker script)
Step 3 → In the main thread: new Worker('./worker.js', { workerData })
Step 4 → Worker runs on its OWN thread with its OWN V8 instance +
          event loop — doesn't block the main thread
Step 5 → Communicate results via worker.postMessage() /
          parentPort.postMessage() (structured clone, or SharedArrayBuffer
          for zero-copy shared memory)
Step 6 → Main thread listens via worker.on('message', ...) and
          continues handling OTHER requests the whole time

cluster APPROACH (for scaling REQUEST THROUGHPUT, not single-task speed):
Step 1 → A primary process forks N worker processes (typically = CPU core count)
Step 2 → All workers listen on the SAME port (OS load-balances between them)
Step 3 → Each worker handles requests independently — if ONE worker blocks
          on heavy sync code, OTHER workers can still serve requests
Step 4 → This increases TOTAL THROUGHPUT, but doesn't make any SINGLE
          heavy computation finish faster
```

## 🟢 कैसे काम करता है? (Hindi)
```
worker_threads: CPU-heavy function को अलग file में डालो, new Worker()
से start करो, अपने thread+event loop पर चलता है, message से result वापस
cluster: Primary process N worker processes fork करता है (CPU cores जितना),
सब same port पर listen करते हैं, एक worker block हो तो दूसरे चलते रहते हैं
(throughput बढ़ता है, single task की speed नहीं)
```

---

## 🟡 Real World Example
**Amazon invoice-PDF generation service:** Generating a detailed PDF invoice with embedded charts for thousands of orders at month-end is CPU-intensive. Instead of doing it in the main API process (which would block customer-facing order APIs), Amazon-style architectures use a `worker_threads` pool (4-8 workers) dedicated purely to PDF generation, fed via an internal job queue. The main API quickly enqueues jobs and returns `202 Accepted`, while workers process them in the background — keeping the customer-facing API snappy regardless of invoice generation load. Separately, the ENTIRE API layer runs under `cluster` (or PM2 in cluster mode) across all CPU cores to maximize overall request throughput.

## 🟡 Real Example Hindi mein
**Amazon invoice-PDF generation:** Month-end पर हजारों orders के PDF invoices generate करना CPU-intensive है। Main API process में करने से customer-facing APIs block हो जाएंगी। इसलिए `worker_threads` pool (4-8 workers) dedicated PDF generation के लिए use होता है, job queue से feed होता है। Main API जल्दी `202 Accepted` return करता है। पूरी API layer `cluster`/PM2 cluster mode में सभी CPU cores पर चलती है throughput बढ़ाने के लिए।

---

## 💻 Code Example — Basic

```javascript
// cpu-basic-worker.js — the WORKER file
// Run via: node cpu-basic-main.js (see below)

const { parentPort, workerData } = require('worker_threads');

function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);  // intentionally CPU-heavy
}

const result = fibonacci(workerData.n);
parentPort.postMessage({ result });  // send result back to main thread
```

```javascript
// cpu-basic-main.js — the MAIN thread file
// Run: node cpu-basic-main.js

const { Worker } = require('worker_threads');

console.log('Main thread: starting worker for fibonacci(35)...');

const worker = new Worker('./cpu-basic-worker.js', {
  workerData: { n: 35 },
});

worker.on('message', (msg) => {
  console.log('Main thread received result:', msg.result);
});

worker.on('error', (err) => console.error('Worker error:', err));

// PROOF the main thread is NOT blocked — this logs immediately,
// while the worker is still computing fibonacci(35) in the background
console.log('Main thread: still responsive, not blocked!');
setInterval(() => console.log('Main thread tick...'), 200).unref();
```

## 💻 Code Example — Advanced

```javascript
// cpu-advanced-pool.js — a reusable worker pool for repeated CPU tasks

const { Worker } = require('worker_threads');
const os = require('os');

class WorkerPool {
  constructor(workerScript, poolSize = os.cpus().length) {
    this.workerScript = workerScript;
    this.poolSize = poolSize;
    this.workers = [];
    this.queue = [];      // pending tasks waiting for a free worker
    this.freeWorkers = [];

    for (let i = 0; i < poolSize; i++) {
      this.addWorker();
    }
  }

  addWorker() {
    const worker = new Worker(this.workerScript);
    worker.on('message', (result) => {
      const { resolve } = worker.currentTask;
      worker.currentTask = null;
      resolve(result);
      this.freeWorkers.push(worker);
      this.processQueue();  // pick up next queued task if any
    });
    worker.on('error', (err) => {
      if (worker.currentTask) worker.currentTask.reject(err);
    });
    this.workers.push(worker);
    this.freeWorkers.push(worker);
  }

  runTask(data) {
    return new Promise((resolve, reject) => {
      this.queue.push({ data, resolve, reject });
      this.processQueue();
    });
  }

  processQueue() {
    if (this.queue.length === 0 || this.freeWorkers.length === 0) return;
    const worker = this.freeWorkers.pop();
    const task = this.queue.shift();
    worker.currentTask = task;
    worker.postMessage(task.data);
  }

  async destroy() {
    await Promise.all(this.workers.map((w) => w.terminate()));
  }
}

// Usage: pool sized to CPU core count, reused across many requests
(async () => {
  const pool = new WorkerPool('./cpu-basic-worker.js', 4);

  console.log('Submitting 10 fibonacci tasks to a pool of 4 workers...');
  const start = Date.now();

  const results = await Promise.all(
    Array.from({ length: 10 }, (_, i) => pool.runTask({ n: 30 + (i % 3) }))
  );

  console.log(`All 10 tasks done in ${Date.now() - start}ms`);
  console.log('Results:', results.map((r) => r.result));

  await pool.destroy();
})();
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { Worker } = require('worker_threads');
const app = express();

// Production pattern: reusable worker pool shared across requests,
// never spawn a new Worker PER REQUEST (that has startup overhead)
const workerPool = [];
const POOL_SIZE = 4;
for (let i = 0; i < POOL_SIZE; i++) {
  workerPool.push({ worker: new Worker('./report-worker.js'), busy: false });
}

function getAvailableWorker() {
  return workerPool.find((w) => !w.busy);
}

app.post('/generate-report', express.json(), (req, res) => {
  const slot = getAvailableWorker();

  if (!slot) {
    // All workers busy — either queue the request or reject with 503
    return res.status(503).json({ error: 'Server busy, try again shortly' });
  }

  slot.busy = true;
  slot.worker.postMessage(req.body);

  slot.worker.once('message', (report) => {
    slot.busy = false;
    res.json(report);
  });
});

// Meanwhile, run the ENTIRE app under cluster for multi-core throughput
// (see cluster.js module-level setup, not shown here) — cluster scales
// REQUEST HANDLING capacity, worker_threads handle individual HEAVY tasks

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Spawning a new Worker Thread for EVERY request
```javascript
// WRONG: Worker creation has real overhead (spinning up a new V8
// instance) — doing this per-request at high traffic is wasteful
app.get('/compute', (req, res) => {
  const worker = new Worker('./heavy.js');  // expensive, repeated every request!
  worker.on('message', (r) => res.json(r));
});

// CORRECT: maintain a reusable POOL of workers (see WorkerPool class above)
// and reuse them across many requests
```

❌ **Mistake 2:** Using `cluster` thinking it speeds up a SINGLE heavy computation
```javascript
// WRONG assumption: "cluster will make my one slow /report endpoint faster"
// cluster forks MULTIPLE INDEPENDENT processes, each still single-threaded
// internally — ONE request still runs on ONE worker process, blocking
// THAT process's event loop, just like before. cluster helps OVERALL
// THROUGHPUT (more concurrent requests handled), not individual task speed.

// CORRECT: for speeding up ONE heavy task, use worker_threads (parallelize
// the WORK itself) — cluster and worker_threads solve DIFFERENT problems
```

---

## 🧠 Tricky Interview Question

**Q: You have a Node.js API server with 4 CPU cores. A single endpoint does a 2-second CPU-bound computation. Will running the app under `cluster` with 4 worker processes make a SINGLE request to that endpoint finish faster?**

**Answer:** No. `cluster` creates 4 SEPARATE Node.js processes, each independently single-threaded. A SINGLE request still gets routed to ONE of those processes and runs on that process's ONE thread — the 2-second computation still takes 2 seconds, blocking that process's event loop for that duration. What `cluster` DOES improve: if 4 DIFFERENT requests arrive simultaneously, each can be handled by a DIFFERENT worker process in parallel, so your TOTAL THROUGHPUT (requests/second) improves roughly 4x — but any INDIVIDUAL heavy request isn't sped up. To actually speed up ONE heavy computation, you'd need to parallelize the ALGORITHM itself (e.g., split the work across multiple `worker_threads` and combine results) — a fundamentally different problem from `cluster`'s scaling.

---

## ⚫ Interview Questions + Answers

**Q1: What are the main options for handling CPU-intensive work in Node.js, and when would you use each?**
A1: (1) `worker_threads` — for moderate CPU-heavy JS computation that needs to run without blocking the main thread; low overhead, can share memory via `SharedArrayBuffer`. (2) `child_process` — for spawning separate OS processes, useful for running other languages/tools or needing full process isolation; higher overhead than workers. (3) `cluster` — for scaling REQUEST THROUGHPUT across CPU cores by running multiple Node processes behind the same port; doesn't speed up individual tasks. (4) External services/job queues (e.g., BullMQ + separate worker service) — for very heavy or specialized workloads that shouldn't live in the API process at all.

**Q2: Why can't you just "add more code" to make a CPU-bound function run faster on Node's single thread?**
A2: JavaScript on the main thread is fundamentally single-threaded — no matter how the code is structured, a CPU-bound computation occupies the ONE available thread for its full duration. The only ways to truly speed it up are: (a) algorithmic improvements (better Big-O), (b) parallelizing ACROSS multiple threads/processes (worker_threads/cluster/child_process), or (c) offloading to more suitable technology (e.g., a compiled language via FFI/native addons, or a dedicated compute service).

**Q3: What's the difference in overhead between `worker_threads` and `child_process`?**
A3: `worker_threads` are lighter-weight — they run within the SAME OS process, sharing some resources, with faster startup and the ability to share memory directly via `SharedArrayBuffer` (zero-copy). `child_process` spawns a COMPLETELY separate OS process with its own memory space — higher startup overhead, communication only via serialized IPC messages (no shared memory), but offers stronger isolation and the ability to run non-Node executables/scripts.

**Q4: How would you design a system to handle thousands of CPU-intensive PDF generation requests without degrading your main API's responsiveness?**
A4: Use a producer-consumer pattern: the main API process quickly validates the request, pushes a job onto a queue (in-memory via a worker pool for moderate load, or a persistent queue like BullMQ/Redis/RabbitMQ for high/durable load), and immediately responds (e.g., `202 Accepted` with a job ID). A separate pool of `worker_threads` (or entirely separate worker service instances) consumes jobs from the queue, processes them, and the client polls or gets notified (webhook/websocket) when done. This decouples heavy computation from the request-response cycle entirely.

**Q5: Can `worker_threads` share memory directly, and why would that matter for performance?**
A5: Yes, via `SharedArrayBuffer` — this allows ZERO-COPY sharing of binary data between the main thread and worker threads, avoiding the overhead of serializing/deserializing (structured clone) large payloads through `postMessage()`. This matters significantly for performance when passing large buffers (e.g., image data, large arrays) between threads repeatedly — regular message passing would otherwise copy the entire payload each time.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Image/video processing, PDF generation, complex calculations, large data transformations, encryption of big payloads
- Building a worker pool for repeated CPU-bound jobs

❌ **Avoid when:**
- The task is actually I/O-bound (network/disk wait) — that's what Node's async model already handles well, no offloading needed
- The task is trivially fast (microseconds) — offloading adds unnecessary complexity and overhead

---

## 📊 Visual Diagram

```
HANDLING CPU-INTENSIVE WORK — DECISION TREE:
──────────────────────────────────────────────────────

  Is the task CPU-bound (heavy computation, little I/O wait)?
         │
    No ──┴── Yes
    │          │
    ▼          ▼
  Use normal   Is it ONE heavy task that needs to run WITHOUT
  async/await  blocking other requests?
  (Node's          │
  strength)    Yes─┴─No
               │        │
               ▼        ▼
         worker_threads  Do you need MORE THROUGHPUT for
         (parallelize    MANY concurrent requests?
         within process)      │
                          Yes─┴─No
                          │        │
                          ▼        ▼
                       cluster   child_process /
                       module    external service
                       (multi-   (isolation, other
                       core      languages, very
                       scaling)  heavy workloads)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CPU-bound | Task limited by computation, not I/O wait | Computation से limited task, I/O wait नहीं |
| `worker_threads` | In-process parallel JS execution | Same process में parallel JS execution |
| `cluster` | Multi-process request throughput scaling | Multi-process request throughput scaling |
| `child_process` | Separate OS process execution | अलग OS process execution |
| SharedArrayBuffer | Zero-copy shared memory between threads | Threads के बीच zero-copy shared memory |

---

## ⚡ 3-Line Summary
English:
1. CPU-intensive work is a poor fit for Node's single-threaded event loop — it blocks everything if run directly on the main thread.
2. `worker_threads` parallelize heavy JS computation within a process; `cluster` scales request THROUGHPUT across cores (doesn't speed up single tasks); `child_process`/external services handle isolation or very heavy specialized work.
3. Always reuse a worker pool rather than spawning workers per-request, and offload truly heavy jobs to a queue-based architecture for scalability.

Hindi:
1. CPU-intensive काम Node के single-threaded event loop के लिए सही fit नहीं है — directly चलाने से सब block हो जाता है।
2. `worker_threads` process के अंदर heavy JS computation parallelize करता है; `cluster` cores पर request throughput बढ़ाता है (single task speed नहीं); `child_process`/external services isolation या बहुत heavy काम के लिए।
3. हर request पर worker spawn करने के बजाय worker pool reuse करो, और heavy jobs को queue-based architecture पर भेजो scalability के लिए।

---

## ➡️ Next Topic
**84. What is Express.js** — Introduction to the most popular Node.js web framework, built on top of the `http` module।
