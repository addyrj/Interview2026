# 226. Cluster Mode — Multi Core
# हिंदी में: Cluster Mode — सभी CPU Cores का इस्तेमाल करना

---

## 🔵 Simple Definition (English)
A single Node.js process runs JavaScript on **one thread**, using only one CPU core regardless of how many are available. The built-in **`cluster` module** forks multiple copies (worker processes) of your app — one per CPU core — all sharing the same server port, so incoming requests get load-balanced across all cores, letting a multi-core machine handle multiple times the traffic of a single process.

## 🔵 सरल परिभाषा (Hindi)
एक single Node.js process JavaScript को **एक thread** पर चलाता है, सिर्फ एक CPU core use करता है भले ही कितने भी available हों। Built-in **`cluster` module** तुम्हारे app की कई copies (worker processes) fork करता है — एक हर CPU core के लिए — सब same server port share करते हैं, incoming requests सभी cores में load-balanced होते हैं, एक multi-core machine single process से कई गुना ज़्यादा traffic handle कर सकता है।

---

## 🔴 Problem it Solves
A production server with 8 CPU cores running `node app.js` directly uses only 1 core — the other 7 sit idle no matter how much traffic arrives, because Node's JS execution is fundamentally single-threaded per process. This wastes 87.5% of available compute capacity. The `cluster` module solves this WITHOUT rewriting application code — it forks N worker processes (typically N = number of CPU cores), each an independent copy of the app with its own event loop, and the OS/Node's load balancer distributes incoming connections across them, achieving near-linear throughput scaling with core count.

## 🔴 यह क्यों बना? (Hindi)
8 CPU cores वाला production server जो directly `node app.js` चलाता है सिर्फ 1 core use करता है — बाकी 7 idle रहते हैं traffic कुछ भी हो, क्योंकि Node का JS execution fundamentally per-process single-threaded है। ये 87.5% available compute capacity waste करता है। `cluster` module ये solve करता है application code rewrite किए बिना — ये N worker processes fork करता है (आम तौर पर N = CPU cores की संख्या), हर एक independent copy अपने event loop के साथ, और OS/Node का load balancer incoming connections को उनमें distribute करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → A **primary (master) process** starts first and checks `cluster.isPrimary` — it doesn't handle requests directly, it manages workers
Step 2 → The primary calls `cluster.fork()` once per CPU core (via `os.cpus().length`), creating that many **worker processes**, each running the full app code independently
Step 3 → All workers bind to the SAME port — Node's cluster module handles this via the primary process, which internally load-balances incoming connections to workers (round-robin on most platforms)
Step 4 → Each worker has its own event loop, memory space, and V8 instance — a slow/blocking operation in one worker does NOT affect other workers' ability to handle requests
Step 5 → If a worker crashes, the primary's `'exit'` event fires — production setups typically `cluster.fork()` again immediately to replace the dead worker, maintaining full capacity
Step 6 → Workers do NOT share in-memory state (each has its own memory) — shared state (sessions, caches) must go through an external store like Redis, not a local JS variable

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक **primary (master) process** पहले start होता है और `cluster.isPrimary` check करता है — ये directly requests handle नहीं करता, workers manage करता है
Step 2 → Primary हर CPU core के लिए एक बार `cluster.fork()` call करता है (`os.cpus().length` से), इतने ही **worker processes** बनाता है, हर एक independently पूरा app code चलाता है
Step 3 → सभी workers SAME port पर bind होते हैं — Node का cluster module primary process के through ये handle करता है, incoming connections को internally workers में load-balance करता है
Step 4 → हर worker का अपना event loop, memory space, V8 instance होता है — एक worker में slow/blocking operation दूसरे workers को affect नहीं करता
Step 5 → अगर कोई worker crash हो, primary का `'exit'` event fire होता है — production setups आम तौर पर तुरंत `cluster.fork()` फिर करते हैं dead worker को replace करने के लिए
Step 6 → Workers in-memory state share नहीं करते (हर एक की अपनी memory) — shared state (sessions, caches) को external store (Redis) से जाना चाहिए, local JS variable से नहीं

---

## 🟡 Real World Example
**Zomato's order-API server** runs on machines with 8 CPU cores each. Running a single `node server.js` process used only 1 core, handling ~2,000 requests/second before CPU saturation. Switching to `cluster` mode with 8 workers (one per core) allowed the SAME machine to handle ~14,000 requests/second — close to linear scaling — because each worker independently processes its own share of requests on its own core. They also moved session storage from local memory to Redis BEFORE enabling clustering, since each worker has separate memory and a user's session needed to be visible regardless of which worker handled their next request.

## 🟡 Real Example Hindi mein
**Zomato का order-API server** हर एक 8 CPU cores वाली machines पर चलता है। Single `node server.js` process सिर्फ 1 core use करता था, CPU saturation से पहले ~2,000 requests/second handle करता था। `cluster` mode में 8 workers (per core) पर switch करने से same machine ~14,000 requests/second handle करने लगी — near-linear scaling — क्योंकि हर worker independently अपने core पर अपना हिस्सा requests process करता है। Clustering enable करने से पहले उन्होंने session storage local memory से Redis में move किया क्योंकि हर worker की अलग memory होती है।

---

## 💻 Code Example — Basic

```javascript
// cluster-basic.js — classic cluster module setup
const cluster = require('cluster');
const os = require('os');
const http = require('http');

const numCPUs = os.cpus().length; // e.g., 8 on an 8-core machine

if (cluster.isPrimary) {
  console.log(`Primary process ${process.pid} is running`);
  console.log(`Forking ${numCPUs} workers...`);

  // Fork one worker per CPU core
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  // If a worker dies, log it and fork a replacement to maintain capacity
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died (code: ${code}). Forking a replacement...`);
    cluster.fork();
  });

} else {
  // This code runs in EACH worker process — the actual app logic
  http.createServer((req, res) => {
    res.writeHead(200);
    res.end(`Handled by worker ${process.pid}\n`);
  }).listen(3000);

  console.log(`Worker ${process.pid} started and listening on port 3000`);
}

// Run: node cluster-basic.js
// Then: for i in {1..10}; do curl localhost:3000; done
// Notice different requests being handled by DIFFERENT worker PIDs —
// proof that load is being distributed across multiple processes/cores
```

## 💻 Code Example — Advanced

```javascript
// cluster-production.js — production-grade cluster setup with Express,
// graceful shutdown, health monitoring, and shared-state awareness
const cluster = require('cluster');
const os = require('os');
const express = require('express');

const numCPUs = os.cpus().length;
// Leave 1 core free for OS/other processes on smaller machines, if desired:
const WORKER_COUNT = process.env.WORKER_COUNT || numCPUs;

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid}: starting ${WORKER_COUNT} workers`);

  const workers = {};

  function forkWorker() {
    const worker = cluster.fork();
    workers[worker.id] = worker;

    worker.on('message', (msg) => {
      // Workers can send messages to the primary (e.g., for aggregated metrics)
      if (msg.type === 'metrics') {
        console.log(`Worker ${worker.process.pid} metrics:`, msg.data);
      }
    });
  }

  for (let i = 0; i < WORKER_COUNT; i++) forkWorker();

  cluster.on('exit', (worker, code, signal) => {
    delete workers[worker.id];
    if (!worker.exitedAfterDisconnect) {
      // Unexpected crash (not a graceful shutdown) — replace it
      console.error(`Worker ${worker.process.pid} crashed unexpectedly. Restarting...`);
      forkWorker();
    }
  });

  // GRACEFUL SHUTDOWN: on SIGTERM, tell all workers to finish in-flight
  // requests and exit cleanly, instead of killing them abruptly
  process.on('SIGTERM', () => {
    console.log('Primary received SIGTERM, shutting down workers gracefully...');
    for (const id in workers) {
      workers[id].send('shutdown'); // custom message telling worker to drain
    }
  });

} else {
  // WORKER PROCESS: the actual Express app
  const app = express();

  app.get('/', (req, res) => {
    res.json({ handledBy: process.pid, workerId: cluster.worker.id });
  });

  app.get('/health', (req, res) => res.json({ status: 'ok', pid: process.pid }));

  const server = app.listen(3000, () => {
    console.log(`Worker ${process.pid} listening`);
  });

  // Listen for the graceful shutdown signal from the primary
  process.on('message', (msg) => {
    if (msg === 'shutdown') {
      console.log(`Worker ${process.pid} draining connections...`);
      server.close(() => {
        process.exit(0); // exit only after existing connections finish
      });
    }
  });
}

// ─── IMPORTANT: SHARED STATE MUST GO THROUGH REDIS, NOT LOCAL MEMORY ──────
// WRONG (works with 1 worker, breaks with cluster):
// const sessionCache = new Map(); // each worker has its OWN separate Map!

// CORRECT: use Redis so ALL workers see the same session data regardless
// of which worker handles a given user's request
// const redisClient = require('./redisClient');
// await redisClient.set(`session:${sessionId}`, JSON.stringify(data));
```

---

## 🟠 Express.js Integration

```javascript
// server.js — the standard production pattern: separate app.js (Express routes)
// from the cluster-aware entry point that forks workers running that app

// app.js — pure Express app, no clustering logic here
const express = require('express');
function createApp() {
  const app = express();
  app.get('/api/orders', async (req, res) => {
    const orders = await getOrdersFromDb(); // uses shared Redis/DB, not local memory
    res.json(orders);
  });
  return app;
}
module.exports = { createApp };

// cluster-entry.js — the file you actually run in production
const cluster = require('cluster');
const os = require('os');
const { createApp } = require('./app');

if (cluster.isPrimary) {
  const numCPUs = os.cpus().length;
  for (let i = 0; i < numCPUs; i++) cluster.fork();
  cluster.on('exit', () => cluster.fork()); // auto-restart crashed workers
} else {
  const app = createApp();
  app.listen(process.env.PORT || 3000);
}

// package.json:
// "scripts": { "start": "node cluster-entry.js" }
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing shared application state (sessions, in-memory caches) locally per worker
```javascript
// WRONG: this Map only exists in ONE worker's memory — a user whose first
// request hits worker 1 and second request hits worker 3 would see
// INCONSISTENT state (worker 3 has no idea about worker 1's cache entry)
const sessionStore = new Map();

// CORRECT: use Redis (or another shared external store) so state is
// consistent regardless of which worker handles any given request
const redis = require('ioredis').createClient();
await redis.set(`session:${id}`, JSON.stringify(data));
```

❌ Mistake 2: Not handling worker crashes, letting the fleet silently shrink over time
```javascript
// WRONG: no 'exit' handler — if workers crash under load (e.g., due to a
// bug triggered by specific input), capacity silently decreases, eventually
// to zero, with no server actively listening anymore
for (let i = 0; i < numCPUs; i++) cluster.fork();
// missing: cluster.on('exit', ...) to replace dead workers!

// CORRECT: always replace crashed workers to maintain full capacity
cluster.on('exit', (worker, code, signal) => {
  console.error(`Worker ${worker.process.pid} died, restarting`);
  cluster.fork();
});
```

---

## 🧠 Tricky Interview Question

**Q: You run `cluster` with 8 workers, each with its own in-memory rate limiter (`Map` tracking request counts per IP). A client making 100 requests/second seems to bypass your "max 50 requests/second" rate limit. Why?**
Answer: Because each of the 8 workers has its OWN SEPARATE in-memory `Map` — the load balancer distributes the client's 100 requests roughly evenly across the 8 workers (about 12-13 requests per worker), and EACH worker independently thinks the client has only made ~12 requests, well under its own local 50/second limit. The rate limiter never sees the TRUE total across all workers combined. Fix: use a SHARED rate limiter backed by Redis (e.g., with `INCR` + `EXPIRE` commands, or a library like `rate-limiter-flexible` with a Redis store) so all workers check and update the SAME counter, correctly enforcing the limit across the entire cluster, not per-worker.

---

## ⚫ Interview Questions + Answers

Q1: What does `cluster.isPrimary` (formerly `cluster.isMaster`) check, and why does the code branch on it?
A1: It's `true` only in the ORIGINAL process that starts the app; `false` in each forked worker. The primary process's job is purely to fork and manage workers (and in some setups handle inter-worker communication), not to serve actual requests — the `if (cluster.isPrimary) { fork workers } else { run the app }` branch ensures the primary doesn't duplicate the app's server logic, while each worker runs the FULL app independently.

Q2: How does the cluster module distribute incoming connections to workers?
A2: On most platforms (Linux), the primary process listens on the port and uses a round-robin algorithm by default to hand off incoming connections to available workers. On Windows and some configurations, the OS kernel itself handles distribution directly to workers that share the listening socket. Either way, the net effect is incoming traffic spread roughly evenly across all worker processes.

Q3: Why can't workers share in-memory variables, and what's the correct way to share state?
A3: Each worker is a completely SEPARATE OS process with its own isolated memory space — forking doesn't share JS heap/variables (unlike `worker_threads`, which CAN share memory via `SharedArrayBuffer`). Any state that needs to be consistent across all workers (sessions, caches, rate limit counters) must live in an external shared store like Redis or a database, which all workers can read/write independently.

Q4: What's the difference between the `cluster` module and `pm2`'s cluster mode?
A4: `cluster` is Node's built-in low-level API requiring you to write the forking/restart/shutdown logic yourself. PM2 is a process manager built ON TOP of similar OS-level forking that provides this as a simple CLI flag (`pm2 start app.js -i max`), plus additional production features out of the box: automatic restarts, zero-downtime reloads, log aggregation, and monitoring — PM2 is generally preferred for production unless you need very custom cluster behavior that PM2 doesn't expose.

Q5: Does clustering help with memory-bound problems, or only CPU-bound ones?
A5: Clustering primarily helps with CPU-bound bottlenecks (utilizing multiple cores for JS execution) and with handling more CONCURRENT connections (since each worker has its own event loop capacity). It does NOT reduce per-request memory usage — in fact, running 8 workers means 8x the baseline memory footprint of your app (each worker loads its own copy of modules, caches, etc.), so clustering trades memory for CPU/concurrency scaling, and machines need enough RAM to support N full copies of the app.

---

## 🔷 When to Use + When Not to Use
✅ Use cluster mode when:
- Running on a multi-core machine and currently using only 1 core per process
- The app is CPU-bound or needs to handle high concurrent connection volume
- You've already moved shared state (sessions, caches, rate limits) to an external store like Redis

❌ Avoid or be careful when:
- Running in a serverless environment where the platform already handles horizontal scaling (clustering is redundant/conflicting there)
- The app still has significant local in-memory shared state that hasn't been externalized (will cause subtle bugs across workers)
- Memory is the primary constraint (clustering multiplies memory usage per core, which can be counterproductive on memory-limited instances)

---

## 📊 Visual Diagram
```
CLUSTER MODE ARCHITECTURE:
────────────────────────────────────────────────
                 ┌───────────────┐
                 │ Primary Process│
                 │ (manages workers,│
                 │  doesn't serve   │
                 │  requests itself)│
                 └────────┬────────┘
                          │ forks
       ┌──────────┬───────┼───────┬──────────┐
       ▼          ▼       ▼       ▼          ▼
   Worker 1   Worker 2  Worker 3  ...    Worker 8
   (Core 1)   (Core 2)  (Core 3)        (Core 8)
   own event  own event own event       own event
   loop       loop      loop            loop

  Incoming requests → load-balanced (round-robin) across all 8 workers

  Shared state (sessions, cache, rate limits) → MUST use Redis,
  since each worker has its OWN isolated memory
                          │
                          ▼
                    ┌───────────┐
                    │   Redis    │ ← shared across all workers
                    └───────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cluster module | Built-in API for forking multi-process workers | Multi-process workers बनाने का built-in API |
| Primary process | Manages workers, doesn't serve requests | Workers manage करने वाला process |
| Worker process | Independent copy running the actual app | App चलाने वाला independent process |
| Round-robin | Even distribution of connections across workers | Connections का बराबर distribution |
| Shared state | Data that must be consistent across all workers | सभी workers में consistent data |
| Graceful shutdown | Finishing in-flight requests before exiting | Exit से पहले requests पूरी करना |

---

## ⚡ 3-Line Summary
English:
1. The `cluster` module forks one worker process per CPU core, letting a Node.js app utilize all available cores instead of just one, achieving near-linear throughput scaling.
2. Always replace crashed workers via the `'exit'` event, and move shared state (sessions, caches, rate limits) to Redis since workers don't share in-memory data.
3. Use PM2's cluster mode (`-i max`) in production for a simpler, more feature-complete alternative to hand-rolling `cluster` module logic.

Hindi:
1. `cluster` module हर CPU core के लिए एक worker process fork करता है, Node.js app को सिर्फ एक core के बजाय सभी available cores use करने देता है — near-linear throughput scaling मिलती है।
2. हमेशा `'exit'` event से crashed workers replace करो, और shared state (sessions, caches, rate limits) को Redis में move करो क्योंकि workers in-memory data share नहीं करते।
3. Production में PM2 का cluster mode (`-i max`) use करो — `cluster` module logic हाथ से लिखने से simpler और ज़्यादा feature-complete alternative।

---

## ➡️ Next Topic
**227. PM2 Cluster Mode** — PM2 process manager से production-grade clustering, auto-restart, और zero-downtime deployment।
