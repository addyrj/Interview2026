# 245. Graceful Shutdown
# हिंदी में: Graceful Shutdown

---

## 🔵 Simple Definition (English)
Graceful shutdown means a Node.js process, when told to stop (e.g., `SIGTERM` during a deployment or scale-down), finishes handling in-flight requests, closes database/queue connections cleanly, and only THEN exits — instead of dying abruptly and dropping active requests or leaving connections in a bad state.

## 🔵 सरल परिभाषा (Hindi)
Graceful shutdown का मतलब है कि एक Node.js process, जब उसे stop होने के लिए कहा जाए (जैसे deployment या scale-down के दौरान `SIGTERM`), in-flight requests को पूरा करता है, database/queue connections को cleanly close करता है, और सिर्फ तब exit करता है — अचानक मरने और active requests drop करने या connections को bad state में छोड़ने के बजाय।

---

## 🔴 Problem it Solves
When an orchestrator (Kubernetes, PM2, a deployment script) stops an instance — whether for a rolling deployment, scaling down, or auto-healing — simply killing the process immediately (`SIGKILL` or an abrupt `process.exit()`) can cut off requests mid-flight (users see errors), leave database transactions half-committed, or lose queued jobs that were being processed. Graceful shutdown solves this by giving the process a window to finish current work and clean up before actually terminating, making deployments and scaling operations invisible to users.

## 🔴 यह क्यों बना? (Hindi)
जब एक orchestrator (Kubernetes, PM2, एक deployment script) किसी instance को stop करता है — rolling deployment, scaling down, या auto-healing के लिए — process को immediately kill करना (`SIGKILL` या abrupt `process.exit()`) requests को mid-flight काट सकता है (users को errors दिखते हैं), database transactions को half-committed छोड़ सकता है, या process हो रहे queued jobs खो सकता है। Graceful shutdown process को current work पूरा करने और actually terminate होने से पहले clean up करने का एक window देकर यह solve करता है, deployments और scaling operations को users के लिए invisible बनाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → The process listens for termination signals, primarily `SIGTERM` (the standard "please shut down" signal sent by orchestrators) and `SIGINT` (Ctrl+C).
Step 2 → On receiving the signal, the app first stops ACCEPTING new connections/requests (e.g., `server.close()` on an HTTP server).
Step 3 → Already in-flight requests are allowed to finish normally (the HTTP server tracks and waits for active connections to complete).
Step 4 → Open resources are cleanly closed: database connection pools, Redis clients, message queue consumers (acking or releasing in-progress jobs appropriately).
Step 5 → A maximum shutdown timeout is enforced — if cleanup takes too long, the process force-exits anyway (to avoid hanging forever and blocking the orchestrator's deployment).
Step 6 → Only after cleanup (or timeout) does the process call `process.exit(0)`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Process termination signals सुनता है, मुख्यतः `SIGTERM` (orchestrators द्वारा भेजा जाने वाला standard "please shut down" signal) और `SIGINT` (Ctrl+C)।
Step 2 → Signal मिलने पर, app पहले नई connections/requests ACCEPT करना बंद करता है (जैसे HTTP server पर `server.close()`)।
Step 3 → पहले से in-flight requests को normally finish होने दिया जाता है (HTTP server active connections के complete होने तक track और wait करता है)।
Step 4 → Open resources cleanly close होते हैं: database connection pools, Redis clients, message queue consumers (appropriately in-progress jobs को ack या release करना)।
Step 5 → एक maximum shutdown timeout enforce होता है — अगर cleanup में बहुत समय लगे, process फिर भी force-exit हो जाता है (हमेशा के लिए hang होने और orchestrator की deployment block करने से बचने के लिए)।
Step 6 → Cleanup (या timeout) के बाद ही process `process.exit(0)` call करता है।

---

## 🟡 Real World Example
**Flipkart during a rolling deployment:** When Flipkart deploys a new version of the Order Service, Kubernetes sends `SIGTERM` to old pods one by one (not all at once). Each pod, on receiving `SIGTERM`, stops accepting new orders but finishes processing the 5-10 orders it's currently handling, properly closes its database connection pool, and exits cleanly within a 30-second grace period. Users whose requests were in-flight during the deployment never see an error — they're served correctly even as the underlying infrastructure changes beneath them.

## 🟡 Real Example Hindi mein
**Flipkart एक rolling deployment के दौरान:** जब Flipkart Order Service का नया version deploy करता है, Kubernetes old pods को एक-एक करके `SIGTERM` भेजता है (सब एक साथ नहीं)। हर pod, `SIGTERM` मिलने पर, नए orders accept करना बंद करता है लेकिन अभी process हो रहे 5-10 orders को पूरा करता है, अपने database connection pool को properly close करता है, और 30-second grace period के अंदर cleanly exit होता है। Users जिनकी requests deployment के दौरान in-flight थीं, उन्हें कभी error नहीं दिखती — वो correctly serve होते हैं भले ही underlying infrastructure उनके नीचे बदल रहा हो।

---

## 💻 Code Example — Basic

```javascript
// graceful-shutdown-basic.js
// Run: node graceful-shutdown-basic.js, then test with Ctrl+C (sends SIGINT)

const express = require('express');
const app = express();

app.get('/', (req, res) => {
  // Simulate a slow request to demonstrate graceful shutdown waiting for it
  setTimeout(() => res.send('Response after delay'), 3000);
});

const server = app.listen(3000, () => console.log('Server listening on 3000'));

// Listen for the termination signal
process.on('SIGINT', () => {
  console.log('\nSIGINT received. Shutting down gracefully...');

  // Stop accepting NEW connections, but let existing ones finish
  server.close(() => {
    console.log('All connections closed. Exiting.');
    process.exit(0);
  });
});

// Try: start a slow request (curl localhost:3000), then press Ctrl+C immediately —
// notice the server waits for that request to finish before actually exiting.
```

## 💻 Code Example — Advanced

```javascript
// graceful-shutdown-advanced.js — production pattern with DB, timeout, and multiple signals
const express = require('express');
const app = express();

app.get('/orders', async (req, res) => {
  const orders = await queryDatabase();
  res.json(orders);
});

async function queryDatabase() {
  await new Promise(r => setTimeout(r, 500));
  return [{ id: 1 }];
}

// Simulated resources that need cleanup
const dbPool = { close: async () => { console.log('DB pool closed'); } };
const redisClient = { quit: async () => { console.log('Redis client disconnected'); } };
const queueWorker = { stop: async () => { console.log('Queue worker stopped, in-progress job allowed to finish'); } };

const server = app.listen(3000, () => console.log(`Server (PID ${process.pid}) listening on 3000`));

let isShuttingDown = false;

async function gracefulShutdown(signal) {
  if (isShuttingDown) return;   // prevent handling the signal twice if it arrives again
  isShuttingDown = true;

  console.log(`${signal} received. Starting graceful shutdown...`);

  // Enforce a MAXIMUM shutdown time — don't hang forever if cleanup gets stuck
  const forceExitTimer = setTimeout(() => {
    console.error('Graceful shutdown timed out. Forcing exit.');
    process.exit(1);
  }, 10000);   // 10 second grace period

  try {
    // 1. Stop accepting new HTTP connections, wait for in-flight ones to finish
    await new Promise((resolve, reject) => {
      server.close((err) => (err ? reject(err) : resolve()));
    });
    console.log('HTTP server closed — no more new requests accepted');

    // 2. Clean up other resources in parallel
    await Promise.all([dbPool.close(), redisClient.quit(), queueWorker.stop()]);

    clearTimeout(forceExitTimer);
    console.log('Graceful shutdown complete');
    process.exit(0);
  } catch (err) {
    console.error('Error during shutdown:', err.message);
    clearTimeout(forceExitTimer);
    process.exit(1);
  }
}

// Handle both common termination signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));   // sent by Kubernetes/Docker
process.on('SIGINT', () => gracefulShutdown('SIGINT'));     // sent by Ctrl+C

// Also catch truly unexpected crashes to at least log before exiting
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err);
  gracefulShutdown('uncaughtException');
});
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

let activeRequests = 0;
let isShuttingDown = false;

// Middleware to track active requests and reject new ones during shutdown
app.use((req, res, next) => {
  if (isShuttingDown) {
    res.set('Connection', 'close');
    return res.status(503).json({ error: 'Server is shutting down, please retry' });
  }
  activeRequests++;
  res.on('finish', () => activeRequests--);
  next();
});

app.get('/health', (req, res) => res.sendStatus(isShuttingDown ? 503 : 200));
app.get('/orders', (req, res) => res.json({ orders: [] }));

const server = app.listen(3000, () => console.log('Server on 3000'));

process.on('SIGTERM', () => {
  console.log('SIGTERM received — marking as not ready, draining requests...');
  isShuttingDown = true;   // readiness probe now fails, LB stops sending new traffic

  server.close(() => {
    console.log(`Shutdown complete, ${activeRequests} requests were in flight`);
    process.exit(0);
  });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling `process.exit()` immediately on receiving `SIGTERM`, without waiting for in-flight requests
✅ Correct: Call `server.close()` first and exit only in its callback, after connections drain

```javascript
// Wrong — kills in-flight requests immediately
process.on('SIGTERM', () => process.exit(0));

// Right — waits for existing connections to finish first
process.on('SIGTERM', () => server.close(() => process.exit(0)));
```

❌ Mistake 2: No maximum shutdown timeout, so a stuck cleanup step hangs the process forever
✅ Correct: Always set a force-exit timer as a safety net

```javascript
// Wrong — if dbPool.close() hangs, the process never exits, and deployments stall
process.on('SIGTERM', async () => { await dbPool.close(); process.exit(0); });

// Right
process.on('SIGTERM', async () => {
  const timer = setTimeout(() => process.exit(1), 10000);
  await dbPool.close();
  clearTimeout(timer);
  process.exit(0);
});
```

---

## 🧠 Tricky Interview Question

```javascript
// A Node.js app inside a Docker container ignores SIGTERM entirely (no handler registered).
// Docker sends SIGTERM, waits 10 seconds (default grace period), then sends SIGKILL.
// What happens to in-flight requests when SIGKILL arrives?
```
Answer: `SIGKILL` cannot be caught, ignored, or handled by the application — it terminates the process immediately and unconditionally at the OS level, with absolutely no chance for cleanup code to run. Any requests still in-flight at that moment are abruptly cut off (clients see connection resets or timeouts), any uncommitted database writes may be left inconsistent, and any Redis/queue connections are closed uncleanly. This is exactly why apps MUST register a `SIGTERM` handler and complete their graceful shutdown within the orchestrator's grace period (commonly 10-30 seconds) — missing that window means Docker/Kubernetes escalates to `SIGKILL`, and all the graceful-shutdown intent is lost.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `SIGTERM` and `SIGKILL`, and why does it matter for Node.js apps?
A1: `SIGTERM` is a polite termination request that a process CAN catch and handle (e.g., to run cleanup code before exiting) — it's what orchestrators send first during normal shutdowns/deployments. `SIGKILL` is an immediate, unconditional termination that cannot be intercepted by the application at all — the OS kills the process instantly with zero chance to run any code. Node.js apps should handle `SIGTERM` to implement graceful shutdown; if that handling takes too long, the orchestrator eventually escalates to `SIGKILL`, at which point any pending cleanup is lost.

Q2: Why is it important to stop accepting NEW requests before waiting for existing ones to finish during shutdown?
A2: If the server kept accepting brand new requests while trying to shut down, the "in-flight request count" could never reach zero (new work keeps arriving), and shutdown could hang indefinitely or require force-killing anyway. Calling `server.close()` tells the HTTP server to immediately stop accepting NEW connections while still letting currently-open connections complete their response — this creates a finite, predictable shutdown window instead of an open-ended one.

Q3: Why should a graceful shutdown handler have a maximum timeout before forcing an exit?
A3: Cleanup steps (closing a hung database connection, waiting for a queue consumer to finish a stuck job) can occasionally get stuck or take unexpectedly long. Without a timeout, the process could hang forever waiting for cleanup to "finish," which blocks deployments (the orchestrator is waiting for the old pod to terminate) and delays rollouts. A force-exit timer (e.g., 10-30 seconds) guarantees the process eventually exits either way, trading a small risk of imperfect cleanup for guaranteed forward progress.

Q4: How does graceful shutdown interact with health check readiness endpoints?
A4: On receiving `SIGTERM`, a well-designed app should immediately start reporting "not ready" on its readiness endpoint (even before finishing in-flight requests) — this tells the load balancer/orchestrator to stop routing NEW traffic to this instance right away, which combined with `server.close()` and draining existing connections, ensures a smooth handoff without the instance having to deal with a flood of newly-arriving requests during its shutdown window.

Q5: What resources, besides the HTTP server, typically need explicit cleanup during graceful shutdown?
A5: Database connection pools (close cleanly so the DB server doesn't see abrupt disconnects), Redis/cache clients, message queue consumers (e.g., a RabbitMQ/Kafka consumer should stop consuming new messages and either finish or properly nack/requeue in-progress ones), open file handles/streams, and any background timers/intervals (`clearInterval`) that would otherwise keep the Node.js event loop alive and prevent a clean exit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running in any orchestrated/production environment (Kubernetes, Docker, PM2, cloud auto-scaling) where instances are routinely started/stopped
- Zero-downtime deployments and clean resource management matter
- The app holds stateful connections (DB pools, queue consumers) that shouldn't be abruptly severed

❌ Avoid when:
- A simple one-off local script with no persistent connections or in-flight work to protect (graceful shutdown logic would be unnecessary overhead)

---

## 📊 Visual Diagram
```
  Orchestrator sends SIGTERM
          │
          ▼
  ┌─────────────────────┐
  │ 1. Mark NOT READY     │  (readiness probe fails → LB stops routing new traffic)
  │ 2. server.close()     │  (stop accepting new connections)
  │ 3. Wait for in-flight │  (existing requests finish normally)
  │ 4. Close DB/Redis/    │
  │    queue connections  │
  │ 5. process.exit(0)    │
  └─────────────────────┘
          │
   (if step 3-4 takes too long)
          ▼
   force-exit timer fires → process.exit(1)
          │
   (if app never responds to SIGTERM at all)
          ▼
   orchestrator sends SIGKILL after grace period → immediate, unclean termination
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SIGTERM | Catchable termination signal | Catch किया जा सकने वाला termination signal |
| SIGKILL | Uncatchable, immediate termination | Catch न हो सकने वाला, immediate termination |
| Draining | Letting in-flight requests finish | In-flight requests को finish होने देना |
| Grace period | Time allowed before force-kill | Force-kill से पहले allowed time |
| server.close() | Stops accepting new connections | नई connections accept करना रोकना |

---

## ⚡ 3-Line Summary
**English:**
1. Graceful shutdown handles `SIGTERM` by stopping new requests, draining in-flight ones, and cleaning up resources before exiting.
2. Always enforce a maximum shutdown timeout to avoid hanging indefinitely and triggering `SIGKILL`.
3. Combine shutdown logic with readiness probes so load balancers stop routing traffic the moment shutdown begins.

**Hindi:**
1. Graceful shutdown `SIGTERM` को handle करता है नए requests रोककर, in-flight requests drain करके, और exit से पहले resources clean up करके।
2. हमेशा एक maximum shutdown timeout enforce करो ताकि indefinitely hang न हो और `SIGKILL` trigger न हो।
3. Shutdown logic को readiness probes के साथ combine करो ताकि load balancers shutdown शुरू होते ही traffic routing बंद कर दें।

---

## ➡️ Next Topic
**246. Docker + Node.js** — Containerizing Node.js apps for consistent, portable deployment.
