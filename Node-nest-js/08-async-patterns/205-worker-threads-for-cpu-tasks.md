# 205. Worker Threads for CPU Tasks
# हिंदी में: CPU Tasks के लिए Worker Threads

---

## 🔵 Simple Definition (English)
**Worker Threads** (`worker_threads` core module) let you run JavaScript in truly parallel, separate threads within the same Node.js process — specifically designed for CPU-intensive work (image processing, heavy computation, parsing huge files) that would otherwise block the single main-thread Event Loop and freeze every other request the server is handling.

## 🔵 सरल परिभाषा (Hindi)
**Worker Threads** (`worker_threads` core module) से Node.js process के अंदर अलग, truly parallel threads में JavaScript चला सकते हैं — specifically CPU-intensive काम (image processing, heavy computation, बड़ी files parse करना) के लिए बनाया गया है जो otherwise single main-thread Event Loop को block कर देता और सारे दूसरे requests freeze हो जाते।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Node.js runs your JS on ONE main thread. Async I/O doesn't block it,
  but SYNCHRONOUS CPU-heavy work (big loops, image resizing, crypto
  hashing, JSON parsing of huge payloads) DOES block it —
  while that computation runs, NO other request can be handled,
  NO timer fires, NOTHING else happens — the whole server freezes

WORKER THREADS SOLUTION:
  Spawn a separate thread (with its own V8 instance + Event Loop)
  to run the CPU-heavy function
  Main thread stays free to keep handling other requests
  Communicate results back via message passing (postMessage/on('message'))
  True parallelism — different threads can use different CPU cores
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: Node.js एक thread पर JS चलाता है। Async I/O block नहीं करता,
पर sync CPU-heavy काम (बड़े loops, image resize, crypto hash) block करता है
उस दौरान कोई भी दूसरा request handle नहीं हो सकता — पूरा server freeze

Worker threads solution: अलग thread spawn करो CPU-heavy काम के लिए
Main thread बाकी requests handle करता रहे
Message passing से result वापस आता है — true parallelism
```

---

## 🟢 How it Works — Step by Step

Step 1 → Main thread creates a `new Worker('./worker-file.js', { workerData })` — this spawns a NEW OS thread running its own independent V8 instance
Step 2 → The worker file runs its code in that separate thread — CPU-heavy computation here does NOT block the main thread's Event Loop
Step 3 → Communication happens via message passing: main thread sends data via `worker.postMessage(data)`, worker receives via `parentPort.on('message', ...)`
Step 4 → Worker sends results back via `parentPort.postMessage(result)`, main thread receives via `worker.on('message', ...)`
Step 5 → Worker is terminated when done (`worker.terminate()`) or exits naturally; a pool of workers can be maintained for repeated CPU tasks to avoid the overhead of spawning a new thread every time

## 🟢 कैसे काम करता है? (Hindi)
```
1. Main thread new Worker() से अलग OS thread spawn करता है
2. Worker file अपने अलग V8 instance में चलता है — CPU काम main thread को block नहीं करता
3. postMessage() से data भेजा जाता है, parentPort.on('message') से receive होता है
4. Worker result वापस postMessage() से भेजता है
5. काम खत्म होने पर worker terminate होता है, या pool maintain किया जाता है
```

---

## 🟡 Real World Example
**Flipkart product image processing on upload:** When a seller uploads 50 high-resolution product photos, resizing/compressing each into multiple sizes (thumbnail, medium, full) is CPU-intensive. If done synchronously on the main thread, uploading images for one seller would freeze the server for EVERY other user browsing the site at that moment. Flippkart's backend spawns worker threads (or a worker pool) to handle image processing in parallel across available CPU cores, keeping the main thread free to keep serving browsing/search/checkout requests for everyone else.

## 🟡 Real Example Hindi mein
**Flipkart image processing:** Seller 50 high-res photos upload करता है, resize/compress करना CPU-intensive है। Main thread पर synchronously करने से सबके लिए server freeze हो जाएगा। Worker threads/pool से parallel processing होती है, main thread free रहता है।

---

## 💻 Code Example — Basic

```javascript
// main.js — Run: node main.js  (requires worker.js in the same folder)
const { Worker } = require('worker_threads');

console.log('1: Main thread starting worker...');

// Spawn a worker, passing initial data via workerData
const worker = new Worker('./worker.js', {
  workerData: { number: 40 },  // compute the 40th Fibonacci number (CPU-heavy, recursive)
});

// Listen for the result message from the worker
worker.on('message', (result) => {
  console.log('3: Worker computed result:', result);
});

worker.on('error', (err) => {
  console.error('Worker error:', err.message);
});

worker.on('exit', (code) => {
  console.log(`Worker exited with code ${code}`);
});

console.log('2: Main thread continues running — NOT blocked by the worker!');
```

```javascript
// worker.js — runs in the separate thread spawned above
const { parentPort, workerData } = require('worker_threads');

// Deliberately slow, CPU-heavy recursive function (bad fibonacci — for demo purposes)
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);  // exponential time — genuinely CPU-heavy
}

const result = fibonacci(workerData.number);  // this blocks THIS thread, not the main one
parentPort.postMessage(result);  // send the result back to main thread
```

## 💻 Code Example — Advanced

```javascript
// advanced-worker-pool.js
// Production pattern: a reusable worker pool to avoid spawning a new
// thread for every single task (thread creation has real overhead).
// Run: node advanced-worker-pool.js  (requires image-worker.js in the same folder)
const { Worker } = require('worker_threads');
const os = require('os');

class WorkerPool {
  constructor(workerFile, poolSize = os.cpus().length) {
    this.workerFile = workerFile;
    this.pool = [];      // idle workers ready to take a task
    this.queue = [];      // pending tasks waiting for a free worker

    for (let i = 0; i < poolSize; i++) {
      this._addWorker();
    }
  }

  _addWorker() {
    const worker = new Worker(this.workerFile);
    worker.isIdle = true;
    this.pool.push(worker);
  }

  runTask(data) {
    return new Promise((resolve, reject) => {
      const availableWorker = this.pool.find((w) => w.isIdle);
      if (availableWorker) {
        this._assign(availableWorker, data, resolve, reject);
      } else {
        this.queue.push({ data, resolve, reject });  // wait for a free worker
      }
    });
  }

  _assign(worker, data, resolve, reject) {
    worker.isIdle = false;

    const onMessage = (result) => {
      cleanup();
      resolve(result);
      this._checkQueue(worker);  // offer this now-free worker to the next queued task
    };
    const onError = (err) => {
      cleanup();
      reject(err);
      this._checkQueue(worker);
    };
    function cleanup() {
      worker.off('message', onMessage);
      worker.off('error', onError);
    }

    worker.on('message', onMessage);
    worker.on('error', onError);
    worker.postMessage(data);
  }

  _checkQueue(worker) {
    worker.isIdle = true;
    if (this.queue.length > 0) {
      const { data, resolve, reject } = this.queue.shift();
      this._assign(worker, data, resolve, reject);
    }
  }

  async destroy() {
    await Promise.all(this.pool.map((w) => w.terminate()));
  }
}

const pool = new WorkerPool('./image-worker.js', 4);  // 4 workers for 4 CPU cores

async function processUploadedImages(imagePaths) {
  const results = await Promise.all(
    imagePaths.map((path) => pool.runTask({ path }))
  );
  console.log('All images processed:', results);
  await pool.destroy();
}

processUploadedImages(['img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg', 'img5.jpg']);
```

```javascript
// image-worker.js — referenced by the pool above
const { parentPort } = require('worker_threads');

parentPort.on('message', ({ path }) => {
  // Simulate CPU-heavy image resizing/compression work
  const start = Date.now();
  let dummy = 0;
  for (let i = 0; i < 1e8; i++) dummy += i;  // simulated heavy computation
  parentPort.postMessage({ path, processedIn: Date.now() - start });
});
```

---

## 🟠 Express.js Integration

```javascript
// Express route offloading CPU-heavy work to a worker thread, keeping
// the main thread free to handle other concurrent requests.
const express = require('express');
const { Worker } = require('worker_threads');
const path = require('path');

const app = express();
app.use(express.json());

function runInWorker(workerFile, data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(workerFile, { workerData: data });
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
    });
  });
}

app.post('/api/reports/generate', async (req, res) => {
  try {
    // Report generation (heavy aggregation/calculation) runs in a worker thread,
    // NOT blocking the Event Loop that's also serving other users' requests right now
    const report = await runInWorker(
      path.join(__dirname, 'report-worker.js'),
      { reportType: req.body.type }
    );
    res.json(report);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(3000, () => console.log('Server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using Worker Threads for I/O-bound work (DB queries, API calls) — that's already non-blocking via the Event Loop and doesn't need a separate thread; it just adds overhead.
✅ Correct: Reserve Worker Threads specifically for CPU-bound (synchronous, computation-heavy) work; keep I/O-bound work on the main thread with async/await.

```javascript
// Wrong — DB query is already async, no benefit from a worker thread
const worker = new Worker('./db-query-worker.js');  // unnecessary overhead

// Right — just await it directly on the main thread
const result = await db.query('SELECT * FROM users');
```

❌ Mistake 2: Spawning a brand-new `Worker` for every single incoming request under high load — thread creation has real overhead (tens of milliseconds, memory per thread) and can exhaust resources.
✅ Correct: Maintain a reusable worker pool (see Advanced example) rather than creating/destroying workers per-request.

❌ Mistake 3: Forgetting that workers do NOT share memory/variables with the main thread by default — passing large objects via `postMessage` copies (serializes) them, which can itself be slow for huge data; use `SharedArrayBuffer`/`Atomics` or transferable objects for genuinely shared binary data.
✅ Correct: Pass only the minimal data needed, or use `workerData`/transfer lists for large buffers to avoid expensive copying.

---

## 🧠 Tricky Interview Question

**Question:** You spawn a Worker Thread to compute something CPU-heavy. While it's running, you make an HTTP request from the MAIN thread to an external API. Does the worker's CPU-heavy computation delay that HTTP request's response?

Answer: **No.** Because the worker runs on a genuinely separate OS thread with its own V8 instance and its own Event Loop, its CPU-bound computation does NOT occupy the main thread's Event Loop at all. The main thread remains completely free to process the HTTP request's async I/O (sending the request, awaiting the response) concurrently with the worker's computation. This is the entire point of Worker Threads — true parallelism for CPU work, running alongside (not blocking) the main thread's normal async I/O handling. Contrast this with running the same heavy computation directly ON the main thread: THAT would block the Event Loop, delaying every other operation, including that HTTP request, until the computation finished.

---

## ⚫ Interview Questions + Answers

Q1: Why can't you just use async/await or Promises to avoid blocking the Event Loop with CPU-heavy work?
A1: Because async/await and Promises only provide concurrency for I/O-bound operations — they don't make SYNCHRONOUS CPU computation (like a tight loop, recursive Fibonacci, or JSON parsing a huge string) run in the background. The code inside an `await`ed function still executes synchronously on the SAME main thread when it actually runs; if that code is CPU-heavy, it blocks the Event Loop regardless of `async`/`await` syntax. Worker Threads are needed for genuine parallelism of CPU-bound work.

Q2: How do the main thread and a worker thread communicate?
A2: Via message passing — `worker.postMessage(data)` sends data from main to worker (received via `parentPort.on('message', ...)` inside the worker file), and `parentPort.postMessage(result)` sends data back (received via `worker.on('message', ...)` on the main thread). Data is structured-cloned (copied), not shared by reference, unless you explicitly use `SharedArrayBuffer`.

Q3: What's the difference between Worker Threads and the Cluster module?
A3: Worker Threads run multiple threads WITHIN a single process, sharing the same process memory space (though JS values aren't shared by default — only via explicit mechanisms), ideal for CPU-bound parallelism within one app instance. The Cluster module forks multiple SEPARATE OS processes, each with its own memory space and its own V8 instance, typically used to utilize multiple CPU cores for handling MORE CONCURRENT HTTP CONNECTIONS (not necessarily CPU-heavy work) via load balancing across processes.

Q4: Why is maintaining a worker pool better than spawning a new worker per task?
A4: Spawning a thread has real overhead — creating a new V8 instance, initializing the JS runtime inside it takes measurable time (often tens of milliseconds) and memory. A pool pre-spawns a fixed number of workers once and reuses them for many tasks over time, amortizing that startup cost and avoiding the risk of unbounded resource usage if many requests arrive simultaneously.

Q5: Can Worker Threads directly share JavaScript objects/variables with the main thread?
A5: No — by default, data passed via `postMessage` is structured-cloned (deep-copied), meaning changes in one thread don't automatically appear in the other. For genuinely shared, mutable binary data across threads, Node.js supports `SharedArrayBuffer` combined with `Atomics` for safe concurrent access, but regular JS objects/closures are never implicitly shared between threads.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Doing genuinely CPU-intensive, synchronous work: image/video processing, complex calculations, parsing huge files, cryptographic hashing, data compression
- You need true parallelism across CPU cores for compute-bound tasks within a single app instance

❌ Avoid when:
- The work is I/O-bound (DB queries, API calls, file reads via async APIs) — already non-blocking, no benefit from a worker thread
- The CPU work is trivially small/fast — thread spawn/communication overhead would outweigh any benefit
- You need shared mutable state without serialization overhead — consider `SharedArrayBuffer` carefully or reconsider the architecture

---

## 📊 Visual Diagram
```
WORKER THREADS vs BLOCKING MAIN THREAD
──────────────────────────────────────────
WITHOUT WORKER THREADS:
  Main Thread: [Request A][CPU work.......][Request B waits][Request B]
                            ▲ everything frozen during this

WITH WORKER THREADS:
  Main Thread:  [Request A][Request B][Request C] ← stays responsive
  Worker Thread:          [CPU work......................] ← runs in parallel
                               │
                     postMessage(result) ──▶ main thread receives it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Worker Thread | Separate thread for CPU-bound work | CPU-bound काम के लिए अलग thread |
| parentPort | Worker's channel back to main thread | Worker का main thread से channel |
| postMessage | Sends data between threads | Threads के बीच data भेजना |
| Worker pool | Reusable set of pre-spawned workers | Pre-spawned workers का reusable set |
| SharedArrayBuffer | True shared memory between threads | Threads के बीच true shared memory |
| CPU-bound vs I/O-bound | Computation-heavy vs waiting-on-I/O work | Computation-heavy vs I/O-wait वाला काम |

---

## ⚡ 3-Line Summary
English:
1. Worker Threads run CPU-heavy JavaScript on genuinely separate threads, keeping the main thread's Event Loop free.
2. Use `postMessage`/`parentPort` for communication, and maintain a worker pool to avoid per-task thread-spawn overhead.
3. Only use them for CPU-bound work — I/O-bound work is already handled efficiently by Node's async model without workers.

Hindi:
1. Worker Threads CPU-heavy JavaScript को अलग threads पर चलाते हैं, main thread का Event Loop free रहता है।
2. `postMessage`/`parentPort` से communication होता है, worker pool से per-task overhead बचाओ।
3. सिर्फ CPU-bound काम के लिए use करो — I/O-bound काम पहले से ही Node के async model से efficient है।

---

## ➡️ Next Topic
**206. Cluster for Multi-Core** — Scaling a Node.js server across multiple CPU cores using separate processes.
