# 206. Cluster for Multi-Core
# हिंदी में: Multi-Core के लिए Cluster

---

## 🔵 Simple Definition (English)
Node.js's core **`cluster`** module lets you fork multiple copies of your server process — one per CPU core — all listening on the same port, with the OS/master process distributing incoming connections across them. Since a single Node.js process runs JS on only ONE thread, clustering is how you actually utilize ALL the CPU cores on a machine to handle more concurrent traffic.

## 🔵 सरल परिभाषा (Hindi)
Node.js का core **`cluster`** module आपके server process की कई copies fork करता है — हर CPU core के लिए एक — सब एक ही port पर सुनते हैं, master process incoming connections को उनके बीच बांटता है। चूंकि एक Node.js process सिर्फ एक thread पर JS चलाता है, clustering से मशीन के सारे CPU cores actually इस्तेमाल होते हैं ज्यादा concurrent traffic handle करने के लिए।

---

## 🔴 Problem it Solves
```
PROBLEM:
  A single Node.js process uses only ONE CPU core, no matter how many
  cores the machine has (8-core server, 16-core server — doesn't matter,
  Node's main thread only uses 1 by default)
  Under high traffic, that single core becomes the bottleneck,
  while 7 other cores sit idle doing nothing

CLUSTER SOLUTION:
  Fork N worker processes (commonly N = number of CPU cores)
  Each worker is a FULL, independent Node.js process with its own
  Event Loop, memory, everything
  The master process load-balances incoming connections across workers
  (typically round-robin on Linux) — now all cores are utilized
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: एक Node.js process सिर्फ एक CPU core इस्तेमाल करता है
8-core server हो तो भी सिर्फ 1 core use होता है, बाकी 7 idle
High traffic में वो 1 core bottleneck बन जाता है

Cluster solution: N worker processes fork करो (N = CPU cores की संख्या)
हर worker अपना अलग, independent Node.js process है
Master process connections को load-balance करता है सबके बीच
```

---

## 🟢 How it Works — Step by Step

Step 1 → A **master process** checks `cluster.isPrimary` (or `isMaster` in older Node) and, if true, calls `cluster.fork()` once per CPU core — spawning that many complete worker processes
Step 2 → Each **worker** runs the EXACT same server code (checked via `cluster.isPrimary` being false in the worker) and calls `app.listen(port)` — Node's cluster module makes this work even though multiple processes "listen" on the same port
Step 3 → The master process intercepts incoming connections and distributes them to workers (round-robin by default on Linux, OS-decided on Windows)
Step 4 → Each worker handles its assigned requests completely independently — they do NOT share memory; if a worker crashes, the master can detect it (`cluster.on('exit', ...)`) and fork a replacement to maintain capacity
Step 5 → Shared state (sessions, caches) must live OUTSIDE the cluster workers (e.g., in Redis) since each worker has its own separate memory

## 🟢 कैसे काम करता है? (Hindi)
```
1. Master process cluster.isPrimary check करता है, fork() से per-core workers बनाता है
2. हर worker same server code चलाता है, app.listen() करता है
3. Master connections को workers के बीच distribute करता है (round-robin)
4. हर worker independently requests handle करता है, memory share नहीं होती
5. Worker crash हो तो master नया fork कर सकता है
```

---

## 🟡 Real World Example
**Zomato's checkout API server on an 8-core machine:** Without clustering, Zomato's checkout API would run on a single core, capping throughput at whatever one core can handle — maybe 2,000 requests/sec. With the `cluster` module (or, in practice, something like PM2's cluster mode, which wraps this), 8 worker processes run simultaneously on the same machine, each handling its own share of incoming checkout requests, roughly 8x-ing throughput on the same hardware — with the master auto-restarting any worker that crashes to keep all 8 "lanes" available.

## 🟡 Real Example Hindi mein
**Zomato checkout API server, 8-core machine:** बिना cluster के सिर्फ 1 core use होता, throughput limited रहता। Cluster module से 8 worker processes एक साथ चलते हैं, हर एक अपने हिस्से के requests handle करता है — throughput roughly 8x हो जाता है।

---

## 💻 Code Example — Basic

```javascript
// basic-cluster.js
// Run: node basic-cluster.js   then open http://localhost:3000 and refresh several times
const cluster = require('cluster');
const http = require('http');
const os = require('os');

const numCPUs = os.cpus().length;  // e.g., 8 on an 8-core machine

if (cluster.isPrimary) {
  console.log(`Master process ${process.pid} is running`);
  console.log(`Forking ${numCPUs} workers...`);

  // Fork one worker per CPU core
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  // If a worker dies, fork a replacement to maintain capacity
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died, forking a replacement`);
    cluster.fork();
  });
} else {
  // THIS code runs in EACH worker process — the actual server logic
  http.createServer((req, res) => {
    res.writeHead(200);
    res.end(`Handled by worker PID: ${process.pid}\n`);
  }).listen(3000);

  console.log(`Worker ${process.pid} started`);
}

// Refreshing the browser repeatedly will show DIFFERENT PIDs handling
// different requests — proof that load is distributed across workers
```

## 💻 Code Example — Advanced

```javascript
// advanced-cluster.js
// Production-style cluster setup: graceful shutdown, worker health tracking,
// and keeping a stable number of workers alive.
const cluster = require('cluster');
const express = require('express');
const os = require('os');

const numWorkers = os.cpus().length;

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} starting ${numWorkers} workers`);

  const workers = new Map();

  function spawnWorker() {
    const worker = cluster.fork();
    workers.set(worker.id, worker);

    worker.on('message', (msg) => {
      if (msg.type === 'health') {
        console.log(`Worker ${worker.process.pid} reports: healthy, ${msg.requestCount} requests served`);
      }
    });
  }

  for (let i = 0; i < numWorkers; i++) spawnWorker();

  // Automatically replace crashed workers, but avoid infinite restart loops
  // on repeated immediate crashes (basic backoff check)
  cluster.on('exit', (worker, code, signal) => {
    workers.delete(worker.id);
    if (signal !== 'SIGTERM') {  // SIGTERM means intentional shutdown, don't respawn
      console.log(`Worker ${worker.process.pid} crashed (code ${code}). Spawning replacement.`);
      spawnWorker();
    }
  });

  // Graceful shutdown: tell all workers to stop accepting new connections
  process.on('SIGTERM', () => {
    console.log('Primary received SIGTERM, shutting down workers gracefully...');
    for (const worker of workers.values()) {
      worker.send('shutdown');  // custom message telling the worker to wind down
    }
  });
} else {
  // Worker process: the actual Express app
  const app = express();
  let requestCount = 0;

  app.get('/', (req, res) => {
    requestCount++;
    res.json({ pid: process.pid, requestCount });
  });

  const server = app.listen(3000, () => {
    console.log(`Worker ${process.pid} listening`);
  });

  // Report health periodically to the primary process
  setInterval(() => {
    process.send({ type: 'health', requestCount });
  }, 10000);

  // Listen for the shutdown signal from the primary
  process.on('message', (msg) => {
    if (msg === 'shutdown') {
      console.log(`Worker ${process.pid} shutting down gracefully`);
      server.close(() => process.exit(0));  // finish in-flight requests, then exit
    }
  });
}
```

---

## 🟠 Express.js Integration

```javascript
// Typical production pattern: separate cluster bootstrap file wraps a normal Express app
// cluster-entry.js
const cluster = require('cluster');
const os = require('os');

if (cluster.isPrimary) {
  const numWorkers = os.cpus().length;
  console.log(`Starting ${numWorkers} workers`);
  for (let i = 0; i < numWorkers; i++) cluster.fork();
  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} exited, restarting`);
    cluster.fork();
  });
} else {
  // The Express app itself is UNCHANGED by clustering — it doesn't know/care
  require('./app.js');  // app.js just does normal: const app = express(); app.listen(3000)
}

// In practice, most teams use PM2 ('pm2 start app.js -i max') instead of hand-rolling
// this cluster bootstrap, since PM2 handles worker management, logs, and zero-downtime
// reloads out of the box.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming workers share memory/state (in-memory cache, session store, in-memory counters) — each worker is a COMPLETELY SEPARATE process with its own memory.
✅ Correct: Use an external shared store (Redis, a database) for any state that must be consistent across all workers.

```javascript
// Wrong — each worker has its OWN separate inMemoryCache, inconsistent across workers
let inMemoryCache = {};
app.get('/data', (req, res) => res.json(inMemoryCache));

// Right — shared store accessible from any worker
const cache = await redisClient.get('data');
```

❌ Mistake 2: Not handling worker crashes — if a worker dies and nothing re-forks it, your effective capacity silently shrinks over time until no workers are left.
✅ Correct: Listen for `cluster.on('exit', ...)` and fork a replacement (with care to avoid infinite crash-restart loops on a systemic bug).

❌ Mistake 3: Running CPU-heavy synchronous work inside a worker thinking clustering "parallelizes" it the same way Worker Threads do — clustering distributes INCOMING CONNECTIONS across processes, it doesn't split ONE request's CPU-heavy computation across multiple cores.
✅ Correct: Use clustering to scale concurrent REQUEST throughput; use Worker Threads (within a single worker process) if a SINGLE request itself needs CPU-heavy parallel computation.

---

## 🧠 Tricky Interview Question

**Question:** You have an 8-core machine running a clustered Node.js app with 8 workers. A single incoming request triggers a CPU-heavy synchronous computation taking 2 seconds. How many OTHER requests can be affected during those 2 seconds?

Answer: Only requests routed to **that SAME worker process** are blocked for those 2 seconds — the other 7 worker processes, each with their own independent Event Loop, continue handling their own assigned requests completely unaffected. This is the key benefit of clustering: it CONTAINS the blast radius of one worker's blocking operation to roughly `1/N` of your total capacity (here, 1/8), rather than the whole server freezing as it would with a single, non-clustered process. However, it's still NOT a fix for CPU-heavy code — within that one affected worker, every request routed to it during those 2 seconds still has to wait; the real fix for genuinely CPU-heavy per-request work is Worker Threads INSIDE each worker process, combined with clustering for overall throughput.

---

## ⚫ Interview Questions + Answers

Q1: Why does a single Node.js process fail to use all CPU cores on a machine?
A1: Node.js's JavaScript execution (the Event Loop and your JS code) runs on a single main thread by design — even though libuv's internal thread pool handles some I/O operations in the background, your actual application logic only executes on that one thread, which the OS schedules onto exactly one CPU core at a time. To use multiple cores for your application logic, you need multiple OS processes (cluster) or threads (worker_threads).

Q2: How does the `cluster` module let multiple processes listen on the same port?
A2: The primary (master) process actually creates the listening socket and, instead of handling connections itself, distributes incoming connections to worker processes (via internal IPC and file descriptor passing) — from the outside, it looks like one server on one port, but internally the primary is load-balancing across N independent worker processes, each running its own copy of your server code.

Q3: Do clustered workers share memory or state?
A3: No — each worker is a fully separate OS process with its own isolated memory space. In-memory variables, caches, or session stores in one worker are NOT visible to other workers. Any state that needs to be consistent across all workers (sessions, rate-limit counters, caches) must live in an external shared store like Redis or a database.

Q4: What's the difference between using `cluster` directly vs using PM2's cluster mode?
A4: `cluster` is Node's low-level core module requiring you to hand-write the fork/restart/shutdown logic yourself. PM2 (a popular process manager) wraps this same underlying mechanism but adds production-grade features out of the box: automatic restarts on crash, zero-downtime reloads, log aggregation, monitoring, and a simple CLI (`pm2 start app.js -i max`) — most production teams use PM2 (or similar tools/Kubernetes-level orchestration) rather than hand-rolling cluster bootstrap code.

Q5: Does clustering help with a single request that needs heavy CPU computation?
A5: Not directly — clustering increases how many CONCURRENT requests your server can handle in parallel (each worker handles its own requests on its own core), but it doesn't split ONE request's computation across multiple workers. For a single CPU-heavy task within one request, you'd combine clustering (for overall throughput) with Worker Threads (to offload that specific task within a worker so it doesn't block that worker's Event Loop).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want to utilize all CPU cores on a machine to handle more concurrent HTTP traffic
- Running a production Node.js server on a multi-core machine/container with spare cores otherwise idle

❌ Avoid when:
- Running inside an environment that already horizontally scales via multiple containers/pods per core (e.g., Kubernetes often runs one Node process per pod and scales pods instead) — clustering inside each pod can be redundant/conflict with that strategy
- A single CPU-heavy request's latency is the real problem — clustering doesn't fix that; use Worker Threads instead

---

## 📊 Visual Diagram
```
CLUSTER MODULE ARCHITECTURE
──────────────────────────────────────────
                Incoming requests
                       │
                       ▼
              ┌─────────────────┐
              │ Primary Process  │ (load balances connections)
              └────────┬─────────┘
          ┌────────────┼────────────┬────────────┐
          ▼            ▼            ▼            ▼
      Worker 1      Worker 2     Worker 3     Worker 4
    (core 1, own   (core 2, own (core 3, own (core 4, own
     memory)        memory)      memory)      memory)

  Shared state (sessions, cache) → MUST live in Redis/DB,
  NOT in any individual worker's memory
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cluster.isPrimary | True in the master process | Master process में true |
| fork() | Spawns a new worker process | नया worker process spawn करना |
| Round-robin | Default connection distribution strategy | Default connection बांटने की strategy |
| IPC | Inter-process communication | Processes के बीच communication |
| PM2 | Popular process manager wrapping cluster | Cluster को wrap करने वाला process manager |
| Isolated memory | Separate memory per worker process | हर worker का अलग memory |

---

## ⚡ 3-Line Summary
English:
1. The `cluster` module forks multiple OS processes (one per CPU core) all serving the same port, letting Node.js utilize all cores.
2. Each worker has completely isolated memory — shared state must live in an external store like Redis.
3. Clustering scales concurrent request throughput, not a single request's CPU-heavy computation — combine with Worker Threads for that.

Hindi:
1. `cluster` module per-core multiple OS processes fork करता है, एक ही port serve करते हैं — सारे cores use होते हैं।
2. हर worker की memory अलग होती है — shared state Redis जैसे external store में रखो।
3. Clustering concurrent throughput बढ़ाता है, single request के CPU काम के लिए Worker Threads चाहिए।

---

## ➡️ Next Topic
**207. PM2 — Process Manager** — The production-grade tool that wraps clustering, auto-restarts, and monitoring together.
