# 57. cluster Module
# हिंदी में: cluster Module — Multiple CPU Cores पर Scale करना

---

## 🔵 Simple Definition (English)
The **`cluster`** module (`require('cluster')`) lets a Node.js application fork multiple WORKER PROCESSES, each running a full copy of your app, all sharing the SAME server port. Since Node's event loop is single-threaded (uses only one CPU core by default), `cluster` is how you utilize a multi-core machine — a 4-core server can run 4 worker processes, roughly 4x the throughput for CPU-bound or high-concurrency workloads.

## 🔵 सरल परिभाषा (Hindi)
**`cluster`** module Node.js application को multiple WORKER PROCESSES में fork करने देता है, हर एक पूरा app का copy चलाता है, सभी एक ही server port share करते हैं। Node का event loop single-threaded है (default में एक ही CPU core use करता है), `cluster` से multi-core machine को use कर सकते हो — 4-core server पर 4 worker processes, लगभग 4x throughput।

---

## 🔴 Problem it Solves
A single Node.js process can only use one CPU core, no matter how many cores the server has — on an 8-core machine, running one Node process wastes 7/8ths of available compute capacity. Without `cluster`, scaling vertically (using more CPU) required running multiple separate Node processes manually and putting a load balancer (nginx, HAProxy) in front of them — extra infrastructure complexity. `cluster` solves this WITHIN Node itself: the built-in master process forks workers and automatically load-balances incoming connections across them, all sharing one listening port.

## 🔴 यह क्यों बना? (Hindi)
एक Node.js process सिर्फ एक CPU core use कर सकता है, server में चाहे कितने cores हों — 8-core machine पर एक Node process चलाने से 7/8 compute capacity waste होती है। `cluster` के बिना, vertically scale करने के लिए manually multiple Node processes चलाकर load balancer (nginx) लगाना पड़ता। `cluster` इसे Node के अंदर ही solve करता है — built-in master process workers को fork करता है और incoming connections automatically load-balance करता है, सभी एक ही port share करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `cluster.isPrimary` (formerly `isMaster`) checks whether the current process is the master/primary — your code branches: primary forks workers, workers run the actual server.
Step 2 → Primary process: `cluster.fork()` called N times (typically `os.cpus().length`) creates N worker processes, each a full copy of the Node process running your module.
Step 3 → Workers each call `http.createServer().listen(port)` independently — but the OS/Node coordinates so they all bind to the SAME port without conflict (the primary process actually holds the socket and distributes connections to workers, round-robin by default on most platforms).
Step 4 → `cluster.on('exit', (worker, code, signal) => {...})` in the primary lets you detect crashed workers and automatically `cluster.fork()` a replacement — key for high availability.
Step 5 → Workers are FULLY SEPARATE processes with independent memory — no shared variables between them (unlike threads). Communication between primary and workers happens via `worker.send()`/`process.on('message')`, similar to `child_process.fork()`.
Step 6 → Each worker handles a SUBSET of incoming requests — if one worker's event loop is busy, others can still process requests concurrently, improving overall resilience and throughput.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `cluster.isPrimary` check करता है कि current process primary है या worker।
Step 2 → Primary process: `cluster.fork()` N बार call करने से N worker processes बनते हैं, हर एक पूरा app copy।
Step 3 → Workers independently `http.createServer().listen(port)` call करते हैं — सभी same port पर bind होते हैं, primary connections distribute करता है।
Step 4 → `cluster.on('exit', ...)` से crashed worker detect करो और replacement `fork()` करो — high availability के लिए key।
Step 5 → Workers पूरी तरह अलग processes हैं, independent memory — shared variables नहीं (threads जैसे नहीं)।
Step 6 → हर worker requests का एक हिस्सा handle करता है — अगर एक worker busy है, दूसरे फिर भी process कर सकते हैं।

---

## 🟡 Real World Example
**Flipkart's checkout service during Big Billion Days sale:** A single Node.js process handling checkout requests would be a severe bottleneck during peak traffic (millions of concurrent users). Flipkart runs their checkout service behind `cluster` (or more commonly in production, PM2's cluster mode which wraps the same concept), spawning one worker per CPU core on each server instance. If one worker crashes due to an unexpected error in a specific request, the primary process detects the exit and immediately forks a replacement — other workers keep serving requests uninterrupted, preventing a single bad request from taking down the whole server.

## 🟡 Real Example Hindi mein
**Flipkart checkout service, Big Billion Days sale में:** एक Node process checkout requests handle करने में bottleneck बनता peak traffic में। Flipkart `cluster` (या PM2 cluster mode) के पीछे चलता है, हर CPU core के लिए एक worker। अगर एक worker crash हो, primary उसे detect करके replacement fork करता है — बाकी workers बिना रुके requests handle करते रहते हैं।

---

## 💻 Code Example — Basic
```javascript
// cluster-basics.js
const cluster = require('cluster');
const http = require('http');
const os = require('os');

const numCPUs = os.cpus().length; // number of available CPU cores

if (cluster.isPrimary) {
  console.log(`Primary process ${process.pid} is running`);
  console.log(`Forking ${numCPUs} workers...`);

  // Fork one worker per CPU core
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  // Listen for worker exit -- auto-restart crashed workers
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died (code: ${code}, signal: ${signal})`);
    console.log('Forking a replacement worker...');
    cluster.fork(); // keep the pool at full strength
  });
} else {
  // This code runs in EACH WORKER process
  http.createServer((req, res) => {
    res.writeHead(200);
    res.end(`Hello from worker ${process.pid}\n`);
  }).listen(3000);

  console.log(`Worker ${process.pid} started and listening`);
}

// Running this file: `node cluster-basics.js`
// Multiple requests to localhost:3000 will be handled by DIFFERENT worker PIDs
```

## 💻 Code Example — Advanced
```javascript
// cluster-advanced.js -- production patterns
const cluster = require('cluster');
const http = require('http');
const os = require('os');

const numCPUs = os.cpus().length;

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} starting ${numCPUs} workers`);

  const workers = {};

  function spawnWorker() {
    const worker = cluster.fork();
    workers[worker.id] = worker;

    // Graceful communication: track worker health via periodic heartbeat messages
    worker.on('message', (msg) => {
      if (msg.type === 'heartbeat') {
        workers[worker.id].lastHeartbeat = Date.now();
      }
    });

    return worker;
  }

  for (let i = 0; i < numCPUs; i++) spawnWorker();

  // ─── GRACEFUL RESTART ON CRASH (with backoff to avoid crash-loop storms) ────
  let restartCount = 0;
  cluster.on('exit', (worker, code, signal) => {
    delete workers[worker.id];
    if (code !== 0 && !worker.exitedAfterDisconnect) {
      restartCount++;
      console.error(`Worker ${worker.process.pid} crashed unexpectedly. Restarting...`);
      setTimeout(() => spawnWorker(), Math.min(restartCount * 1000, 10000)); // backoff
    }
  });

  // ─── ZERO-DOWNTIME RELOAD (restart workers one at a time, not all at once) ──
  function gracefulReloadAll() {
    const workerIds = Object.keys(workers);
    let i = 0;
    function reloadNext() {
      if (i >= workerIds.length) return console.log('All workers reloaded');
      const oldWorker = workers[workerIds[i]];
      const newWorker = spawnWorker(); // start a NEW worker before killing the old one

      newWorker.once('listening', () => {
        oldWorker.disconnect(); // gracefully stop accepting new connections on old worker
        i++;
        reloadNext();
      });
    }
    reloadNext();
  }

  process.on('SIGUSR2', gracefulReloadAll); // trigger with: kill -SIGUSR2 <primary_pid>

} else {
  // ─── WORKER PROCESS: the actual HTTP server logic ───────────────────────────
  const server = http.createServer((req, res) => {
    if (req.url === '/health') {
      return res.end('OK');
    }
    // Simulate some work
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ worker: process.pid, path: req.url }));
  });

  server.listen(3000, () => {
    console.log(`Worker ${process.pid} listening`);
  });

  // Send periodic heartbeat to primary (for health monitoring)
  setInterval(() => {
    process.send({ type: 'heartbeat', pid: process.pid, timestamp: Date.now() });
  }, 5000);

  // Graceful shutdown: finish in-flight requests before exiting
  process.on('disconnect', () => {
    server.close(() => process.exit(0));
  });
}
```

---

## 🟠 Express.js Integration
```javascript
// server.js -- Express app clustered across CPU cores
const cluster = require('cluster');
const os = require('os');
const express = require('express');

const numCPUs = os.cpus().length;

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} starting ${numCPUs} Express workers`);

  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code) => {
    console.log(`Worker ${worker.process.pid} exited (code ${code}) -- restarting`);
    cluster.fork(); // auto-restart on crash, keeps the service highly available
  });

} else {
  // Each worker runs its OWN independent Express app instance
  const app = express();

  app.use(express.json());

  app.get('/', (req, res) => {
    res.json({ message: 'Hello from Express!', handledBy: process.pid });
  });

  app.get('/health', (req, res) => res.json({ status: 'ok', pid: process.pid }));

  // IMPORTANT: in-memory state (e.g. a simple cache, counters) is PER-WORKER,
  // not shared across the cluster -- use Redis or a DB for shared state
  let requestCount = 0;
  app.use((req, res, next) => { requestCount++; next(); });
  app.get('/stats', (req, res) => res.json({ pid: process.pid, requestsOnThisWorker: requestCount }));

  app.listen(3000, () => console.log(`Worker ${process.pid} ready on port 3000`));
}

// Run: node server.js
// curl localhost:3000/stats multiple times -- notice different `pid` values as requests
// get load-balanced across different workers
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming in-memory state is shared across cluster workers
```javascript
// Wrong -- each worker has its OWN memory; this cache is per-worker, not global!
let requestCache = {};
app.get('/data/:id', (req, res) => {
  if (requestCache[req.params.id]) return res.json(requestCache[req.params.id]);
  // ...fetch and cache... but only visible to THIS worker, not others!
});

// Correct -- use a shared external store (Redis) for cross-worker shared state
const redis = require('redis').createClient();
app.get('/data/:id', async (req, res) => {
  const cached = await redis.get(req.params.id); // shared across ALL workers
  if (cached) return res.json(JSON.parse(cached));
});
```

❌ Mistake 2: Not handling worker crashes (no auto-restart)
```javascript
// Wrong -- if a worker crashes, the pool silently shrinks, reducing capacity
cluster.fork(); // fork workers once, never check for exits

// Correct -- always listen for 'exit' and restart
cluster.on('exit', (worker, code, signal) => {
  console.log(`Worker ${worker.process.pid} died, restarting...`);
  cluster.fork(); // maintain the configured pool size
});
```

❌ Mistake 3: Forking more workers than CPU cores (wastes resources, adds context-switch overhead)
```javascript
// Wrong -- arbitrarily forking too many workers
for (let i = 0; i < 50; i++) cluster.fork(); // on a 4-core machine, this is counterproductive

// Correct -- match worker count to available CPU cores (sometimes slightly less, reserving a core for the OS)
const numCPUs = require('os').cpus().length;
for (let i = 0; i < numCPUs; i++) cluster.fork();
```

---

## 🧠 Tricky Interview Question
```javascript
const cluster = require('cluster');

if (cluster.isPrimary) {
  let counter = 0;
  cluster.fork();
  cluster.fork();

  setInterval(() => console.log('Primary counter:', counter), 2000);
} else {
  let counter = 0;
  // Simulate each worker incrementing its own counter
  setInterval(() => { counter++; process.send({ counter }); }, 1000);
}
```
Answer: The primary's `counter` variable NEVER changes (stays at `0` forever) even though messages are sent via `process.send()`, because the primary code never attaches a `.on('message', ...)` listener to actually receive and act on those messages — but more fundamentally, even if it did listen, each WORKER maintains its OWN independent `counter` (separate memory space, separate process) — there is no shared memory between primary and workers, or between workers themselves. This illustrates the critical cluster/multi-process principle: variables are never automatically shared across processes; all cross-process state must be explicitly passed via IPC messages (`send()`/`on('message')`) or stored in an external shared system (Redis, a database).

---

## ⚫ Interview Questions + Answers

Q1: How does `cluster` allow multiple worker processes to listen on the SAME port without a "port already in use" error?
A1: The PRIMARY process actually creates and holds the listening socket (or on most platforms, uses the OS's `SO_REUSEPORT` capability). When a worker calls `.listen(port)`, Node's cluster internals intercept this and either have the primary pass the socket handle to the worker (round-robin scheduling, the default on most platforms) or let the OS itself distribute incoming connections across workers bound to the same port. Either way, you don't manually manage port conflicts — `cluster` handles it transparently.

Q2: If `cluster` doesn't share memory between workers, how do you handle data that needs to be consistent across all workers (e.g., a rate-limiting counter, cached session data)?
A2: Use an external, shared data store accessible by all workers equally — most commonly Redis (fast, supports atomic operations useful for counters/rate-limits) or a database. In-memory objects/variables in Node are per-process; cluster workers are fully separate OS processes with independent memory, so any state needing cross-worker consistency must live outside any single worker's process memory.

Q3: What happens to in-flight requests on a worker when it crashes, and how should you handle this for graceful degradation?
A3: In-flight requests on the CRASHED worker are lost (the connection drops, client sees a connection reset/error) — there's no built-in request retry or failover for requests already assigned to that worker. The primary process should listen for the `'exit'` event and immediately fork a replacement worker to restore capacity for FUTURE requests. For truly zero-downtime handling of the crash itself, you'd typically pair `cluster` with a reverse proxy/load balancer that can retry failed requests on a different backend, or rely on client-side retry logic.

Q4: Why might you choose PM2's cluster mode over using Node's `cluster` module directly?
A4: PM2 (a process manager) wraps `cluster`-like functionality with additional production features out of the box: automatic restart on crash with configurable backoff, zero-downtime reloads (`pm2 reload`), built-in logging/monitoring, and a simple CLI (`pm2 start app.js -i max`) instead of writing custom primary/worker branching logic yourself. Many teams prefer PM2 in production because it reduces the amount of custom cluster-management code they need to write and maintain.

Q5: Does `cluster` help with I/O-bound workloads (e.g., many concurrent database queries) the same way it helps CPU-bound workloads?
A5: It helps SOMEWHAT (more processes = more concurrent event loops = more connections handled in parallel, and isolates one slow/blocked worker from affecting others), but the benefit is most dramatic for CPU-bound code, since a SINGLE Node process's event loop can only use one CPU core — CPU-bound synchronous work on one worker doesn't block other workers at all. For purely I/O-bound work, a single well-tuned Node process (with its naturally async, non-blocking I/O model) can already handle a very high number of concurrent connections, so clustering mainly adds resilience and CPU parallelism rather than solving an I/O bottleneck directly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want to utilize all CPU cores on a multi-core server for a Node.js app
- You need basic resilience — if one worker crashes, others keep serving requests
- Running a stateless HTTP API/server where request handling can be distributed across processes

❌ Avoid when:
- Your app holds critical in-memory state that MUST be consistent and can't be moved to an external store (refactor first, or you'll get subtle bugs)
- You're already running multiple instances behind an external load balancer/orchestrator (Kubernetes, PM2 in cluster mode, Docker Swarm) — double-clustering adds unnecessary complexity
- The workload is single-request, short-lived scripts (clustering overhead isn't worth it)

---

## 📊 Visual Diagram
```
CLUSTER ARCHITECTURE:

                    ┌─────────────────────┐
   Incoming         │   PRIMARY PROCESS     │
   requests ───────►│   (holds the socket,  │
                     │    distributes conns) │
                     └──────────┬────────────┘
                                 │
           ┌─────────────┬──────┴──────┬─────────────┐
           ▼             ▼             ▼             ▼
      ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
      │ Worker 1│   │ Worker 2│   │ Worker 3│   │ Worker 4│
      │ (own    │   │ (own    │   │ (own    │   │ (own    │
      │  memory)│   │  memory)│   │  memory)│   │  memory)│
      └─────────┘   └─────────┘   └─────────┘   └─────────┘
       CPU core 1    CPU core 2    CPU core 3    CPU core 4

   All listen on SAME port (e.g. 3000) -- primary load-balances connections

   Worker crashes:
      Worker 2 ✗ ──► cluster.on('exit') fires in PRIMARY ──► cluster.fork() replaces it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cluster | Module for multi-process scaling | Multi-process scaling का module |
| Primary process | Coordinator that forks workers | Workers fork करने वाला coordinator |
| Worker process | Independent copy of the app | App का independent copy |
| cluster.fork() | Create a new worker | नया worker बनाना |
| Shared port | All workers listen on same port | सभी workers same port पर listen करते हैं |
| Independent memory | No shared variables between workers | Workers के बीच shared variables नहीं |

---

## ⚡ 3-Line Summary
English: `cluster` forks multiple worker processes (typically one per CPU core), all sharing the same server port, to utilize multi-core machines and add resilience against crashes. Workers have fully independent memory — no shared state without an external store like Redis. Always listen for `'exit'` and auto-restart crashed workers for high availability.

Hindi: `cluster` multiple worker processes fork करता है (हर CPU core के लिए एक), सभी same port share करते हैं, multi-core machines use करने और crashes से resilience के लिए। Workers की memory पूरी तरह independent है — बिना external store (Redis) shared state नहीं। हमेशा `'exit'` listen करो, crashed workers auto-restart करो।

---

## ➡️ Next Topic
**58. worker_threads Module** — true multi-threading within a single Node.js process, sharing memory, for CPU-intensive JavaScript computation.
