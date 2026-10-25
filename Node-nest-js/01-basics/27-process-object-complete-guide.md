# 27. process Object — Complete Guide
# हिंदी में: process Object — पूरी Guide

---

## 🔵 Simple Definition (English)
`process` is a **global object** in Node.js that gives information about, and control over, the current running Node.js process — things like environment variables (`process.env`), command-line arguments (`process.argv`), exit codes (`process.exit()`), memory usage, platform info, and process lifecycle events (`exit`, `SIGTERM`, `uncaughtException`).

## 🔵 सरल परिभाषा (Hindi)
`process` Node.js में एक **global object** है जो current चल रहे Node.js process की information देता है और उस पर control देता है — जैसे environment variables (`process.env`), command-line arguments (`process.argv`), exit codes (`process.exit()`), memory usage, platform info, और process lifecycle events (`exit`, `SIGTERM`, `uncaughtException`)।

---

## 🔴 Problem it Solves
A running program needs to interact with its operating environment — read config passed via environment variables, know how it was invoked (flags/args), clean up resources before shutting down, respond to OS signals (like `Ctrl+C` or `kubectl delete pod` sending `SIGTERM`), and catch otherwise-fatal errors to avoid silent crashes in production. Without a unified interface, each of these would require separate low-level OS APIs. Node exposes all of it through one global `process` object, available everywhere without `require()`.

## 🔴 यह क्यों बना? (Hindi)
Running program को अपने operating environment से interact करना होता है — environment variables से config पढ़ना, कैसे invoke हुआ जानना (flags/args), shutdown से पहले resources clean करना, OS signals का response देना (जैसे `Ctrl+C` या `kubectl delete pod` से आने वाला `SIGTERM`), और otherwise-fatal errors catch करना ताकि production में silent crash न हो। बिना unified interface के, हर एक के लिए अलग low-level OS APIs चाहिए होते। Node यह सब एक global `process` object से देता है, हर जगह available, बिना `require()` के।

---

## 🟢 How it Works — Step by Step

Step 1 → `process` is injected as a global by the Node runtime (technically a singleton instance of `EventEmitter`) — no import needed.
Step 2 → `process.env` holds all environment variables as a plain object (always strings).
Step 3 → `process.argv` is an array: `[nodePath, scriptPath, ...userArgs]`.
Step 4 → `process.exit(code)` immediately terminates the process with the given exit code (0 = success, non-zero = error) — but SKIPS pending async I/O, so use carefully.
Step 5 → `process.on('SIGTERM', handler)` / `process.on('SIGINT', handler)` let you intercept OS signals for graceful shutdown (close DB connections, finish in-flight requests).
Step 6 → `process.on('uncaughtException', handler)` and `process.on('unhandledRejection', handler)` are last-resort safety nets for errors that weren't caught anywhere else — should log and then exit, NOT be used to "ignore" errors.
Step 7 → `process.memoryUsage()`, `process.cpuUsage()`, `process.uptime()`, `process.version`, `process.platform` expose runtime diagnostics.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `process` Node runtime द्वारा global की तरह inject होता है (technically एक `EventEmitter` का singleton instance) — कोई import नहीं चाहिए।
Step 2 → `process.env` सभी environment variables को plain object की तरह रखता है (हमेशा strings)।
Step 3 → `process.argv` एक array है: `[nodePath, scriptPath, ...userArgs]`।
Step 4 → `process.exit(code)` process को तुरंत terminate करता है दिए गए exit code के साथ (0 = success, non-zero = error) — पर pending async I/O को SKIP कर देता है, इसलिए carefully use करो।
Step 5 → `process.on('SIGTERM', handler)` / `process.on('SIGINT', handler)` से OS signals intercept करो graceful shutdown के लिए (DB connections close करना, in-flight requests finish करना)।
Step 6 → `process.on('uncaughtException', handler)` और `process.on('unhandledRejection', handler)` उन errors के लिए last-resort safety nets हैं जो कहीं catch नहीं हुए — log करके exit करना चाहिए, errors को "ignore" करने के लिए इनका use मत करो।
Step 7 → `process.memoryUsage()`, `process.cpuUsage()`, `process.uptime()`, `process.version`, `process.platform` runtime diagnostics expose करते हैं।

---

## 🟡 Real World Example
**Paytm's payment-processing microservice on Kubernetes:** When Kubernetes scales down a pod or deploys a new version, it sends `SIGTERM` to the running process, then waits a grace period (default 30s) before force-killing with `SIGKILL`. The service listens for `SIGTERM` via `process.on('SIGTERM', ...)`, stops accepting new HTTP requests, waits for in-flight payment requests to finish, closes the database pool, and THEN calls `process.exit(0)` — ensuring no payment gets dropped mid-transaction during a routine deployment.

## 🟡 Real Example Hindi mein
**Paytm का payment-processing microservice Kubernetes पर:** जब Kubernetes किसी pod को scale down करता है या नया version deploy करता है, running process को `SIGTERM` भेजता है, फिर grace period (default 30s) wait करता है force-kill (`SIGKILL`) से पहले। Service `process.on('SIGTERM', ...)` से सुनता है, नए HTTP requests accept करना बंद करता है, in-flight payment requests finish होने का wait करता है, database pool close करता है, और फिर `process.exit(0)` call करता है — ensure करता है कि routine deployment के दौरान बीच में कोई payment drop न हो।

---

## 💻 Code Example — Basic

```javascript
// processBasics.js — exploring the global process object
console.log('Node version:', process.version);        // e.g. v20.11.0
console.log('Platform:', process.platform);            // e.g. 'darwin', 'linux', 'win32'
console.log('PID:', process.pid);                       // process ID assigned by OS
console.log('Current working directory:', process.cwd()); // shell's launch directory
console.log('Uptime (seconds):', process.uptime());     // how long this process has run

// Command-line arguments
console.log('argv:', process.argv);
// run: node processBasics.js hello 123
// → [ '/path/to/node', '/path/to/processBasics.js', 'hello', '123' ]

// Environment variables (always strings, even for numbers/booleans)
console.log('NODE_ENV:', process.env.NODE_ENV || 'development');

// Memory usage snapshot
const mem = process.memoryUsage();
console.log(`Heap used: ${(mem.heapUsed / 1024 / 1024).toFixed(2)} MB`);
```

## 💻 Code Example — Advanced

```javascript
// gracefulShutdown.js — production-grade signal handling
const http = require('http');

const server = http.createServer((req, res) => {
  res.end('OK');
});

server.listen(3000, () => console.log(`Server listening (PID: ${process.pid})`));

// Track in-flight connections so we don't kill active requests
let isShuttingDown = false;

function gracefulShutdown(signal) {
  if (isShuttingDown) return; // avoid double-handling if signal fires twice
  isShuttingDown = true;
  console.log(`Received ${signal}. Starting graceful shutdown...`);

  // Stop accepting NEW connections immediately
  server.close(() => {
    console.log('All connections closed. Exiting.');
    process.exit(0); // clean exit after all requests finished
  });

  // Safety net: force-exit if shutdown takes too long (hung connections)
  setTimeout(() => {
    console.error('Forced shutdown after timeout.');
    process.exit(1); // non-zero = exited due to a problem
  }, 10000).unref(); // unref() lets this timer not keep the process alive by itself
}

// Listen for Kubernetes/Docker/PM2 termination signal
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
// Listen for Ctrl+C in terminal
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Last-resort safety nets — log and exit, never silently swallow
process.on('uncaughtException', (err) => {
  console.error('FATAL uncaught exception:', err);
  process.exit(1); // crash deliberately — a process in unknown state is dangerous to keep running
});

process.on('unhandledRejection', (reason) => {
  console.error('FATAL unhandled promise rejection:', reason);
  process.exit(1);
});
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app using process for env config and graceful shutdown
const express = require('express');
const app = express();

// Read config from environment, with sane defaults
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

app.get('/health', (req, res) => {
  // Expose process diagnostics via a health-check endpoint (common in microservices)
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    pid: process.pid,
    env: NODE_ENV,
  });
});

const server = app.listen(PORT, () => {
  console.log(`[${NODE_ENV}] Server running on port ${PORT} (PID ${process.pid})`);
});

// Graceful shutdown on container orchestrator signals
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server...');
  server.close(() => process.exit(0));
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling `process.exit()` carelessly, cutting off pending async work
```javascript
// Wrong — exits immediately, log might not flush, DB write might not complete
fs.writeFile('./log.txt', 'data', () => {});
process.exit(0); // file write may be CUT OFF — exit doesn't wait for callbacks

// Right — let the event loop drain naturally, or exit only after confirmed completion
fs.writeFile('./log.txt', 'data', (err) => {
  if (err) process.exitCode = 1; // set exit code without forcing immediate exit
  // process exits naturally once the event loop has nothing left to do
});
```

❌ Mistake 2: Using `uncaughtException` to "recover" and keep running
```javascript
// Wrong — swallowing fatal errors and continuing leaves the process in an
// unknown, possibly corrupted state (memory leaks, half-open connections)
process.on('uncaughtException', (err) => {
  console.log('Error happened, ignoring:', err.message); // DANGEROUS — no exit!
});

// Right — log thoroughly, clean up, and exit; let a process manager (PM2/K8s) restart it
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception, shutting down:', err);
  process.exit(1); // deliberate crash, process manager restarts fresh
});
```

---

## 🧠 Tricky Interview Question

```javascript
console.log('A');
process.nextTick(() => console.log('B'));
setTimeout(() => console.log('C'), 0);
Promise.resolve().then(() => console.log('D'));
console.log('E');
```
Answer: Output order is **`A`, `E`, `B`, `D`, `C`**. Synchronous code (`A`, `E`) runs first, top to bottom. Then `process.nextTick()` callbacks run BEFORE Promise microtasks in Node's queue ordering (`nextTick` queue is processed before the microtask/Promise queue, after each phase of the event loop). Then Promise `.then()` callbacks (`D`) run as microtasks. Finally, `setTimeout(..., 0)` (`C`) runs in the next event loop iteration's timers phase — macro-tasks always run after all available microtasks and nextTick callbacks are drained.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `process.exit()` and `process.exitCode`?
A1: `process.exit(code)` immediately and forcefully terminates the process, abandoning any pending I/O or timers — risky because async operations in flight (file writes, DB commits) may not complete. `process.exitCode = code` just SETS the exit code the process will use when it exits NATURALLY (once the event loop has no more work) — this is the safer approach, letting Node finish pending callbacks before shutting down.

Q2: What's the difference between `SIGTERM` and `SIGKILL`?
A2: `SIGTERM` is a polite termination request that a process CAN catch and handle (e.g., for graceful shutdown — closing DB connections, finishing requests) via `process.on('SIGTERM', handler)`. `SIGKILL` cannot be caught, ignored, or handled at all — the OS kills the process immediately, no cleanup possible. Orchestrators like Kubernetes send `SIGTERM` first, then `SIGKILL` after a grace period if the process hasn't exited — which is why implementing proper `SIGTERM` handling matters for zero-downtime deploys.

Q3: What is `process.nextTick()` and how does it differ from `setImmediate()`?
A3: `process.nextTick(callback)` queues a callback to run at the END of the current operation, BEFORE the event loop continues to the next phase — it has the highest priority among async scheduling mechanisms, even before Promise microtasks. `setImmediate(callback)` schedules a callback to run in the "check" phase of the NEXT event loop iteration, after I/O callbacks. `nextTick` can starve the event loop if called recursively (added before every other phase); `setImmediate` doesn't have this risk since it waits for the next full loop iteration.

Q4: Why is handling `unhandledRejection` important in production Node apps?
A4: If a Promise rejects and nothing calls `.catch()` on it, Node emits an `unhandledRejection` event on `process`. Without a handler, Node (since v15) treats this as a fatal error and crashes the process by default — matching `uncaughtException` behavior. Registering a handler lets you log the error with context (useful for debugging which Promise chain was missing a `.catch()`) before deliberately exiting, rather than crashing with a cryptic stack trace or (in older Node versions) silently leaking the rejected promise.

Q5: How do you read configuration safely from `process.env`, considering types?
A5: All values in `process.env` are STRINGS, even if they look like numbers or booleans. `process.env.PORT` is `"3000"` (string), not `3000` (number) — code expecting a number must explicitly convert: `const port = Number(process.env.PORT) || 3000;`. For booleans: `process.env.DEBUG === 'true'` (string comparison), NOT `Boolean(process.env.DEBUG)` (which is truthy for ANY non-empty string, including `"false"`!). This is a very common source of subtle config bugs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reading runtime config (`process.env`), command-line input (`process.argv`).
- Implementing graceful shutdown for containerized/orchestrated deployments.
- Adding global safety nets for truly unexpected errors (`uncaughtException`/`unhandledRejection`) as a LAST resort, not primary error handling.
- Exposing health-check/diagnostic endpoints (`process.uptime()`, `process.memoryUsage()`).

❌ Avoid when:
- Using `process.exit()` as a general error-handling mechanism inside request handlers (crashes the WHOLE server for one bad request — handle errors locally instead with try/catch or middleware).
- Relying on `uncaughtException` to "fix" errors instead of fixing the actual bug — it's a safety net, not error-handling strategy.

---

## 📊 Visual Diagram
```
PROCESS OBJECT — KEY SURFACES:
──────────────────────────────────────────────────────────
  process
    ├── env              → environment variables (strings)
    ├── argv              → [nodePath, scriptPath, ...args]
    ├── pid / platform / version → identity & runtime info
    ├── cwd() / uptime() / memoryUsage() / cpuUsage() → diagnostics
    ├── exit(code) / exitCode → terminate / set exit status
    ├── nextTick(cb)      → highest-priority async callback queue
    └── on(event, handler)
          ├── 'SIGTERM'/'SIGINT'       → OS signals (graceful shutdown)
          ├── 'exit'                   → fires right before process ends
          ├── 'uncaughtException'      → last-resort sync error catcher
          └── 'unhandledRejection'      → last-resort Promise rejection catcher

SIGTERM GRACEFUL SHUTDOWN FLOW:
  K8s sends SIGTERM → stop accepting new requests → finish in-flight requests
       → close DB pool → process.exit(0)
  (if too slow) → K8s sends SIGKILL after grace period → force kill, no cleanup
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| process.env | Environment variables object | Environment variables |
| process.argv | Command-line arguments array | Command-line arguments |
| process.exit() | Force-terminate the process | Process को force terminate करना |
| process.exitCode | Exit code set for natural exit | Natural exit का code |
| SIGTERM | Graceful termination signal | Graceful termination signal |
| SIGKILL | Forced termination signal (uncatchable) | Force kill signal |
| uncaughtException | Last-resort sync error handler | Last-resort error handler |
| unhandledRejection | Last-resort Promise rejection handler | Last-resort rejection handler |
| process.nextTick() | Highest priority async callback | सबसे high priority callback |

---

## ⚡ 3-Line Summary
English: `process` is Node's global object for environment info, command-line args, and lifecycle control — `process.env`, `process.argv`, `process.exit()`. Handle `SIGTERM`/`SIGINT` for graceful shutdown in production, and use `uncaughtException`/`unhandledRejection` only as last-resort safety nets that log and exit, never to silently recover. All `process.env` values are strings — always explicitly convert types.
Hindi: `process` Node का global object है environment info, command-line args, और lifecycle control के लिए — `process.env`, `process.argv`, `process.exit()`। Production में graceful shutdown के लिए `SIGTERM`/`SIGINT` handle करो, और `uncaughtException`/`unhandledRejection` को केवल last-resort safety nets की तरह use करो जो log करके exit करें, silently recover करने के लिए नहीं। `process.env` के सभी values strings होते हैं — हमेशा explicitly type convert करो।

---

## ➡️ Next Topic
**28. process.env — Environment Variables** — deep dive into reading, setting, and securely managing environment-based configuration.
