# 58. worker_threads Module
# हिंदी में: worker_threads Module — True Multi-threading in Node.js

---

## 🔵 Simple Definition (English)
The **`worker_threads`** module (`require('worker_threads')`) provides TRUE multi-threading within a SINGLE Node.js process — multiple JavaScript threads, each with its own event loop, that can optionally SHARE memory via `SharedArrayBuffer`. Unlike `child_process`/`cluster` (separate OS processes, no shared memory), worker threads are lighter-weight (less overhead to start) and support efficient data sharing — ideal for CPU-intensive JavaScript computation.

## 🔵 सरल परिभाषा (Hindi)
**`worker_threads`** module एक ही Node.js process के अंदर TRUE multi-threading देता है — multiple JavaScript threads, हर एक का अपना event loop, जो चाहें तो `SharedArrayBuffer` से memory SHARE कर सकते हैं। `child_process`/`cluster` (अलग OS processes, memory share नहीं) के विपरीत, worker threads lighter-weight हैं (कम startup overhead) और efficient data sharing support करते हैं — CPU-intensive JavaScript computation के लिए best।

---

## 🔴 Problem it Solves
Before `worker_threads` (added in Node 10, stable in Node 12), the only way to run parallel JavaScript was `child_process`/`cluster`, which spin up entirely separate OS processes — heavyweight (significant memory/startup cost per process) and require serialization (JSON) for ANY data exchange, even large arrays/buffers. Many CPU-bound tasks (image processing, complex calculations, parsing huge JSON) don't need separate processes — they need a lightweight thread that can share large binary data (`SharedArrayBuffer`) efficiently WITHOUT copying it, while still not blocking the main thread's event loop.

## 🔴 यह क्यों बना? (Hindi)
`worker_threads` से पहले (Node 10 में आया, Node 12 में stable), parallel JavaScript चलाने का सिर्फ `child_process`/`cluster` तरीका था — heavyweight (हर process का memory/startup cost ज़्यादा), और किसी भी data exchange के लिए serialization (JSON) चाहिए, बड़े arrays/buffers के लिए भी। कई CPU-bound tasks को अलग processes नहीं चाहिए — उन्हें lightweight thread चाहिए जो बड़ा binary data (`SharedArrayBuffer`) efficiently बिना copy किए share कर सके, main thread का event loop block न करते हुए।

---

## 🟢 How it Works — Step by Step

Step 1 → Create a worker: `new Worker('./worker-file.js')` — runs the given file in a new thread, with its own V8 instance and event loop, but within the SAME process.
Step 2 → `isMainThread` (boolean) lets a single file's code branch between main-thread and worker-thread logic, similar to `cluster.isPrimary`.
Step 3 → Pass initial data: `new Worker('./worker.js', { workerData: {...} })` — the worker accesses it via `require('worker_threads').workerData`.
Step 4 → Message passing: `worker.postMessage(data)` from main thread, `parentPort.on('message', fn)` in the worker (and vice versa for worker-to-main) — data is STRUCTURED-CLONED (deep copy) by default, similar to `postMessage` in browsers.
Step 5 → `SharedArrayBuffer` + `Atomics` enable TRUE shared memory between threads — no copying, direct read/write access from both main and worker threads, useful for high-performance numeric data sharing (but requires careful synchronization to avoid race conditions).
Step 6 → `worker.on('exit', code => {...})` and `worker.on('error', err => {...})` handle lifecycle events; `worker.terminate()` forcibly stops a worker.
Step 7 → **Worker Pools**: creating a new worker has startup cost (though less than a process) — for repeated tasks, reuse a pool of pre-started workers (via libraries like `piscina` or `workerpool`) rather than spawning a new one per task.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Worker बनाना: `new Worker('./worker-file.js')` — same process में नया thread, अपना V8 instance और event loop।
Step 2 → `isMainThread` से main-thread vs worker-thread logic branch करो।
Step 3 → Initial data: `workerData` option से, worker में `workerData` से access।
Step 4 → Message passing: `postMessage()`/`parentPort.on('message')` — data structured-clone (deep copy) होता है।
Step 5 → `SharedArrayBuffer` + `Atomics` से TRUE shared memory — copy नहीं, direct access, careful synchronization चाहिए।
Step 6 → `'exit'`, `'error'` events handle करो; `worker.terminate()` से forcibly रोको।
Step 7 → **Worker Pools**: repeated tasks के लिए pre-started workers reuse करो (हर task पर नया worker मत बनाओ)।

---

## 🟡 Real World Example
**Razorpay's fraud-detection scoring engine:** For every transaction, a complex scoring algorithm (analyzing transaction patterns, running statistical models) needs to run — this is CPU-intensive JavaScript that would otherwise block the main event loop handling other payment requests. Razorpay's backend offloads this scoring computation to a pool of `worker_threads`, passing transaction data via `postMessage()` and receiving a fraud score back — the main thread stays responsive to accept new incoming payment requests while scoring happens in parallel across multiple worker threads, all within the SAME Node process (lower overhead than spinning up separate processes per request).

## 🟡 Real Example Hindi mein
**Razorpay का fraud-detection scoring engine:** हर transaction के लिए complex scoring algorithm चलना चाहिए — CPU-intensive JavaScript जो main event loop को block कर सकता है। Razorpay backend इस computation को `worker_threads` pool में offload करता है, `postMessage()` से data भेजता है, fraud score वापस पाता है — main thread responsive रहता है, scoring parallel में होती है, same process के अंदर (अलग processes से कम overhead)।

---

## 💻 Code Example — Basic
```javascript
// worker-threads-basics.js
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

if (isMainThread) {
  // ─── MAIN THREAD CODE ──────────────────────────────────────────────────────
  console.log('Main thread starting a worker...');

  const worker = new Worker(__filename, {
    workerData: { numbers: [1, 2, 3, 4, 5] }, // data passed to the worker on creation
  });

  worker.on('message', (result) => {
    console.log('Received result from worker:', result); // 15 (sum of squares etc.)
  });

  worker.on('error', (err) => console.error('Worker error:', err));
  worker.on('exit', (code) => console.log('Worker exited with code', code));

  worker.postMessage({ action: 'compute', value: 10 }); // send an additional message

} else {
  // ─── WORKER THREAD CODE (same file, runs because isMainThread is false here) ─
  console.log('Worker thread started with data:', workerData);

  // Perform CPU-intensive work using the initial workerData
  const sumOfSquares = workerData.numbers.reduce((sum, n) => sum + n * n, 0);
  parentPort.postMessage(sumOfSquares); // send result back to main thread

  // Listen for additional messages from the main thread
  parentPort.on('message', (msg) => {
    console.log('Worker received message:', msg);
  });
}

// Run: node worker-threads-basics.js
```

## 💻 Code Example — Advanced
```javascript
// worker-threads-advanced.js -- production patterns
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const path = require('path');

// ─── 1. PROMISIFIED WORKER EXECUTION (clean async interface) ─────────────────
function runWorkerTask(workerFile, data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(workerFile, { workerData: data });
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
    });
  });
}

// ─── 2. SIMPLE WORKER POOL (reuse workers instead of creating one per task) ──
class WorkerPool {
  constructor(workerFile, poolSize) {
    this.workerFile = workerFile;
    this.poolSize = poolSize;
    this.workers = [];
    this.queue = [];
    this.freeWorkers = [];
    this.initPool();
  }

  initPool() {
    for (let i = 0; i < this.poolSize; i++) {
      const worker = new Worker(this.workerFile);
      worker.on('message', (result) => {
        worker.currentResolve(result);
        this.freeWorkers.push(worker); // return worker to pool once done
        this.processQueue();
      });
      this.workers.push(worker);
      this.freeWorkers.push(worker);
    }
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
    const { data, resolve } = this.queue.shift();
    worker.currentResolve = resolve;
    worker.postMessage(data);
  }

  async terminateAll() {
    await Promise.all(this.workers.map((w) => w.terminate()));
  }
}

// ─── 3. SHARED MEMORY WITH SharedArrayBuffer + Atomics (advanced, true parallelism) ─
function demonstrateSharedMemory() {
  // SharedArrayBuffer is visible to BOTH main thread and worker -- no copying needed
  const sharedBuffer = new SharedArrayBuffer(4); // 4 bytes = 1 Int32
  const sharedArray = new Int32Array(sharedBuffer);
  sharedArray[0] = 0;

  const worker = new Worker(__filename, {
    workerData: { sharedBuffer, mode: 'increment' },
  });

  worker.on('exit', () => {
    console.log('Final shared value (main thread view):', sharedArray[0]); // reflects worker's writes!
  });
}

if (!isMainThread && workerData?.mode === 'increment') {
  const sharedArray = new Int32Array(workerData.sharedBuffer);
  // Atomics.add ensures thread-safe increment (no race condition)
  Atomics.add(sharedArray, 0, 42);
  process.exit(0);
}

module.exports = { runWorkerTask, WorkerPool };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const { Worker } = require('worker_threads');
const path = require('path');
const app = express();

// Helper to run a one-off worker task as a Promise
function runInWorker(workerFile, data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(workerFile, { workerData: data });
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => code !== 0 && reject(new Error(`Worker exited ${code}`)));
  });
}

app.use(express.json());

// 1. OFFLOAD CPU-INTENSIVE JSON PARSING/TRANSFORMATION TO A WORKER THREAD
app.post('/process-large-dataset', async (req, res) => {
  try {
    // ./workers/data-processor.js does heavy computation on req.body.dataset
    const result = await runInWorker(
      path.join(__dirname, 'workers', 'data-processor.js'),
      { dataset: req.body.dataset }
    );
    res.json({ result });
  } catch (err) {
    res.status(500).json({ error: 'Processing failed: ' + err.message });
  }
});

// 2. FRAUD SCORING WITH A WORKER (keeps event loop free for other payment requests)
app.post('/score-transaction', async (req, res) => {
  try {
    const score = await runInWorker(
      path.join(__dirname, 'workers', 'fraud-scorer.js'),
      { transaction: req.body }
    );
    res.json({ fraudScore: score });
  } catch (err) {
    res.status(500).json({ error: 'Scoring failed' });
  }
});

app.listen(3000);

// Example ./workers/fraud-scorer.js:
// const { parentPort, workerData } = require('worker_threads');
// function computeScore(transaction) { /* CPU-heavy statistical logic */ return Math.random(); }
// parentPort.postMessage(computeScore(workerData.transaction));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating a new worker for every single small task (high overhead)
```javascript
// Wrong -- spawning a worker has real startup cost; doing this per-request is wasteful
app.get('/compute/:n', (req, res) => {
  const worker = new Worker('./compute-worker.js', { workerData: { n: req.params.n } });
  worker.on('message', (result) => res.json({ result }));
}); // under high traffic, this creates/destroys hundreds of workers per second

// Correct -- use a worker POOL, reusing a fixed number of long-lived workers
const pool = new WorkerPool('./compute-worker.js', 4); // sized to CPU cores
app.get('/compute/:n', async (req, res) => {
  const result = await pool.runTask({ n: req.params.n });
  res.json({ result });
});
```

❌ Mistake 2: Assuming regular variables are automatically shared between main thread and worker
```javascript
// Wrong -- worker threads do NOT share regular JS memory by default
let counter = 0;
const worker = new Worker('./worker.js');
// worker incrementing its own 'counter' variable has NO effect on this one

// Correct -- use postMessage for data exchange, or SharedArrayBuffer for true shared memory
const sharedBuffer = new SharedArrayBuffer(4);
const sharedArray = new Int32Array(sharedBuffer);
const worker = new Worker('./worker.js', { workerData: { sharedBuffer } });
// now both main thread and worker can read/write the SAME underlying memory
```

❌ Mistake 3: Using `worker_threads` for I/O-bound work instead of CPU-bound work
```javascript
// Wrong -- offloading a simple DB query to a worker thread adds overhead for no benefit
const worker = new Worker('./db-query-worker.js'); // DB query is already async/non-blocking!

// Correct -- worker_threads shine for CPU-BOUND work; I/O is already handled efficiently
// by Node's event loop without needing a separate thread
await db.query('SELECT * FROM orders'); // just await it directly, no worker needed
```

---

## 🧠 Tricky Interview Question
```javascript
const { Worker, isMainThread } = require('worker_threads');

if (isMainThread) {
  console.log('Main thread, PID:', process.pid);
  const worker = new Worker(__filename);
} else {
  console.log('Worker thread, PID:', process.pid);
}
```
Answer: Both lines print the SAME PID (`process.pid`) for main thread and worker thread! This is a key distinction from `child_process`/`cluster`: worker threads run within the SAME operating system PROCESS as the main thread — they are genuinely THREADS (lighter-weight), not separate processes. Only the `cluster`/`child_process` modules create new OS processes with distinct PIDs. This is exactly why `worker_threads` has lower overhead than `cluster` for spinning up parallel execution contexts, and why `SharedArrayBuffer`-based true memory sharing is possible (threads within one process can share memory; separate processes cannot without IPC/shared OS resources).

---

## ⚫ Interview Questions + Answers

Q1: What's the fundamental architectural difference between `worker_threads` and `child_process`/`cluster`?
A1: `worker_threads` creates multiple THREADS within the SAME operating system process — they share the same PID, can share memory via `SharedArrayBuffer`, and have lower startup/memory overhead. `child_process`/`cluster` creates entirely separate OS PROCESSES, each with its own PID, completely independent memory space, and higher overhead per instance — all cross-process communication requires serialization (even via IPC).

Q2: How do you share data between the main thread and a worker thread, and what are the two approaches?
A2: (1) **Message passing** (default, most common): `worker.postMessage(data)` / `parentPort.postMessage(data)` — data is STRUCTURED-CLONED (a deep copy is made), safe but has copying overhead for large data. (2) **Shared memory**: using `SharedArrayBuffer` passed via `workerData` or `postMessage` — both threads get a VIEW into the exact same underlying memory block, with zero copying, but requires `Atomics` operations for safe concurrent read/write to avoid race conditions.

Q3: Why would you use a worker pool instead of creating a new `Worker` for every task?
A3: Creating a `Worker` has real startup cost — initializing a new V8 isolate and event loop takes measurable time (milliseconds), which adds up under high request volume if done per-task. A worker pool (keeping a fixed number of long-lived workers that receive tasks via messages and report results) amortizes this startup cost across many tasks, giving much better throughput for repeated/frequent CPU-bound work — this is the pattern libraries like `piscina` and `workerpool` implement.

Q4: When should you choose `worker_threads` over `cluster` for a given problem?
A4: Choose `worker_threads` when: the work is CPU-bound JavaScript computation (not just "handle more HTTP connections"), you need to share large binary data efficiently (via `SharedArrayBuffer`) without copying, or you want lower per-instance overhead than full OS processes. Choose `cluster` when: you primarily want to scale HTTP request handling across CPU cores for a stateless server, and process-level isolation (one crashed worker/process doesn't affect others' memory at all) is more important than low overhead or shared memory.

Q5: Does using `worker_threads` eliminate the need to worry about blocking the event loop?
A5: No — it moves the CPU-intensive work OFF the main thread's event loop (good!), but the worker thread ITSELF still has its own single event loop that can be blocked by synchronous CPU-heavy code running inside it. The benefit is that blocking the WORKER's event loop doesn't affect the MAIN thread (or other workers) — but within that worker, the same single-threaded, non-blocking-is-better principles still apply if the worker needs to handle multiple tasks concurrently.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- CPU-intensive JavaScript computation (image processing, cryptography, data transformation, complex algorithms) that would otherwise block the main event loop
- You need to share large binary data efficiently between parallel execution contexts (`SharedArrayBuffer`)
- Lower overhead than `child_process`/`cluster` is important (many short-lived parallel tasks)

❌ Avoid when:
- The work is I/O-bound (database queries, network calls, file reads) — Node's async I/O already handles this without needing threads
- You need full process-level isolation (a crash in one thread CAN, in some cases, affect the process, unlike fully separate processes)
- The task is trivial/fast — the overhead of thread communication outweighs any benefit

---

## 📊 Visual Diagram
```
WORKER_THREADS vs CLUSTER/CHILD_PROCESS:

  worker_threads (same OS process):          cluster/child_process (separate processes):
  ┌─────────────────────────────┐            ┌──────────┐  ┌──────────┐
  │   Process (1 PID)             │            │ Process A│  │ Process B│
  │  ┌────────┐    ┌────────┐     │           │ (PID 1)  │  │ (PID 2)  │
  │  │ Main    │    │ Worker  │    │           └──────────┘  └──────────┘
  │  │ Thread  │◄──►│ Thread  │    │                 ▲             ▲
  │  └────────┘    └────────┘     │                 └─── IPC ──────┘
  │       ▲ shared memory via      │            (no shared memory, only
  │       └── SharedArrayBuffer ───┘             message-passing via pipes)
  └─────────────────────────────┘

  Lower overhead, shared memory possible      Higher overhead, full isolation
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| worker_threads | Multi-threading within one process | एक process के अंदर multi-threading |
| isMainThread | Distinguishes main vs worker code | Main vs worker code की पहचान |
| parentPort | Worker's channel to communicate with main | Main से communicate करने का channel |
| SharedArrayBuffer | Memory shared between threads | Threads के बीच shared memory |
| Atomics | Thread-safe operations on shared memory | Shared memory पर thread-safe operations |
| Worker pool | Reusable set of long-lived workers | Reusable long-lived workers का set |

---

## ⚡ 3-Line Summary
English: `worker_threads` enables true multi-threading within one Node.js process, sharing the same PID but running independent JavaScript execution contexts, optionally sharing memory via `SharedArrayBuffer`. It's lighter-weight than `cluster`/`child_process` and ideal for offloading CPU-intensive computation. Use worker pools for repeated tasks to avoid per-task worker startup overhead.

Hindi: `worker_threads` एक Node.js process के अंदर true multi-threading देता है, same PID share करते हुए independent JavaScript execution contexts चलाता है, `SharedArrayBuffer` से memory share कर सकता है। `cluster`/`child_process` से lighter-weight है, CPU-intensive computation offload करने के लिए ideal। Repeated tasks के लिए worker pools use करो।

---

## ➡️ Next Topic
**59. cluster vs worker_threads** — side-by-side architectural comparison and decision criteria for choosing between process-based and thread-based scaling.
