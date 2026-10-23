# 66. Event Loop — Complete Guide
# हिंदी में: Event Loop — Node.js का दिल

---

## 🔵 Simple Definition (English)
The **Event Loop** is what makes Node.js non-blocking — it's a loop that continuously checks: "Is there any pending I/O operation done? Any timer fired? Any callback to run?" Since Node.js is single-threaded, the Event Loop is the mechanism that lets it handle thousands of concurrent requests without creating a new thread per request. It delegates slow I/O to libuv's thread pool, then picks up the result via callbacks when done.

## 🔵 सरल परिभाषा (Hindi)
**Event Loop** Node.js को non-blocking बनाता है — एक loop जो continuously check करता है: "कोई I/O operation complete हुआ? Timer fire हुआ? कोई callback run करनी है?" Node.js single-threaded है, लेकिन Event Loop की वजह से हजारों concurrent requests handle होती हैं — हर request के लिए new thread नहीं बनता। Slow I/O को libuv thread pool को delegate करता है, complete होने पर callback via Event Loop pick up होती है।

---

## 🔴 Problem it Solves
```
TRADITIONAL SERVER (Apache, PHP):
  Request arrives → Create new thread → Handle request → Destroy thread
  1000 requests → 1000 threads → 1000 × 1MB RAM = 1GB RAM used!
  Threads waiting for DB → wasting CPU doing nothing
  Thread creation is expensive

NODE.JS EVENT LOOP SOLUTION:
  Request arrives → Register callback → Move on
  I/O completes → Event Loop picks callback → Run it
  1000 requests → 1 thread (+ libuv pool) → ~50MB RAM
  Never blocks waiting — always processing something

RESULT:
  Node.js handles C10K problem (10,000 concurrent connections)
  On single thread!
```

## 🔴 यह क्यों बना? (Hindi)
```
Traditional servers: हर request = new thread = RAM waste
1000 requests = 1000 threads → out of memory
Node.js: एक thread, Event Loop से सब handle
I/O wait में time waste नहीं — loop चलता रहता है
```

---

## 🟢 How it Works — Step by Step

```
EVENT LOOP EXECUTION ORDER:
──────────────────────────────────────────────────────
  Node.js starts:
  1. Synchronous code runs FIRST (call stack)
  2. Event Loop starts → 6 phases:

  Phase 1: TIMERS
    → Runs callbacks from setTimeout + setInterval
      (not exactly on time — minimum threshold)

  Phase 2: PENDING CALLBACKS
    → I/O callbacks deferred from previous loop iteration
      (TCP errors, etc.)

  Phase 3: IDLE + PREPARE (internal only)

  Phase 4: POLL
    → NEW I/O events: fs.readFile, http requests
    → Blocks here if no timers pending + callback queue empty
    → Picks up completed I/O callbacks and runs them

  Phase 5: CHECK
    → setImmediate callbacks run here

  Phase 6: CLOSE CALLBACKS
    → socket.on('close', ...) etc.

  BETWEEN EACH PHASE:
  → Microtasks queue: process.nextTick() callbacks first
  → Then: Promise .then() callbacks
  → Microtasks run COMPLETELY before moving to next phase!

  LOOP:
  Runs forever → waiting for work
  Exits when: no more callbacks pending + no active I/O
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Synchronous code पहले run होता है (call stack)
2. Event Loop 6 phases में घूमता है:
   Timers → Pending → Poll (I/O wait) → Check → Close
3. Phases के बीच: process.nextTick() → then Promise.then()
4. जब कोई काम नहीं → process exit
```

---

## 🟡 Real World Example
**Razorpay payment API:** 10,000 payment requests arrive simultaneously. Each request needs: (1) Validate input (sync — fast), (2) Check fraud DB (async I/O — slow), (3) Call payment gateway (async HTTP — slow). With threads: 10,000 threads created, each blocking on DB + HTTP. With Node.js Event Loop: 10,000 requests start → I/O delegated to thread pool → Event Loop keeps picking up completed callbacks → all handled on 1 thread. Memory stays under 100MB.

## 🟡 Real Example Hindi मे
**Razorpay:** 10,000 payment requests → हर request को DB check + payment gateway call चाहिए। Thread model: 10,000 threads blocking on I/O = RAM explode। Node.js: I/O delegate करो, Event Loop completed callbacks pick करता रहे = 1 thread, 100MB से कम RAM।

---

## 💻 Code Example — Basic

```javascript
// event-loop-demo.js
// Run: node event-loop-demo.js
// Watch the ORDER of output carefully!

console.log('1: Script START');  // sync — runs first

// Timer: Phase 1 of event loop
setTimeout(() => {
  console.log('4: setTimeout 0ms');
}, 0);

// setImmediate: Phase 5 of event loop (CHECK phase)
setImmediate(() => {
  console.log('5: setImmediate');
});

// process.nextTick: microtask queue (runs BEFORE any phase)
process.nextTick(() => {
  console.log('3: process.nextTick');
});

// Promise: microtask queue (runs after nextTick)
Promise.resolve().then(() => {
  console.log('3b: Promise.then');
});

console.log('2: Script END');  // sync — runs before callbacks

// OUTPUT ORDER:
// 1: Script START
// 2: Script END
// 3: process.nextTick
// 3b: Promise.then
// 4: setTimeout 0ms
// 5: setImmediate

// WHY?
// Sync code runs first (lines 1, 2)
// Microtasks (nextTick, Promise) run before Event Loop phases
// Timer (setTimeout) runs in Phase 1
// setImmediate runs in Phase 5 (CHECK)
```

## 💻 Code Example — Advanced

```javascript
// advanced-event-loop.js
// Real-world simulation: I/O + timers + microtasks together

const fs = require('fs');  // file system module

console.log('START');

// 1. File I/O → POLL phase
fs.readFile(__filename, () => {  // reads this file itself
  console.log('fs.readFile callback');  // runs in POLL phase

  // INSIDE I/O callback: setTimeout vs setImmediate
  // When INSIDE a poll callback:
  // setImmediate ALWAYS runs before setTimeout!
  // (because we're already past timers phase)
  setTimeout(() => {
    console.log('setTimeout inside readFile');
  }, 0);

  setImmediate(() => {
    console.log('setImmediate inside readFile');  // runs FIRST
  });
});

// 2. Timer
setTimeout(() => {
  console.log('setTimeout 100ms');
}, 100);

// 3. setImmediate in main script
setImmediate(() => {
  console.log('setImmediate in main script');
});

// 4. process.nextTick — microtask
process.nextTick(() => {
  console.log('nextTick 1');
  // nextTick inside nextTick — runs BEFORE Promise!
  process.nextTick(() => {
    console.log('nextTick 2 (nested)');
  });
});

// 5. Promise
Promise.resolve().then(() => {
  console.log('Promise resolved');
});

console.log('END');

// OUTPUT:
// START
// END
// nextTick 1
// nextTick 2 (nested)    ← nested nextTick runs before Promise!
// Promise resolved
// setImmediate in main script
// fs.readFile callback   ← POLL phase (I/O)
// setImmediate inside readFile   ← CHECK phase (after POLL)
// setTimeout inside readFile     ← TIMERS phase (next loop!)
// setTimeout 100ms
```

---

## 🟠 Express.js Integration

```javascript
// How Event Loop affects Express.js request handling:
const express = require('express');
const app = express();

// ❌ WRONG: Blocking the Event Loop (kills all other requests!)
app.get('/bad', (req, res) => {
  // Synchronous CPU-heavy operation — BLOCKS Event Loop!
  let result = 0;
  for (let i = 0; i < 10_000_000_000; i++) {  // 10 billion iterations
    result += i;
  }
  res.json({ result });  // ALL OTHER REQUESTS WAIT while this runs!
});

// ✅ CORRECT: Non-blocking async
app.get('/good/db', async (req, res) => {
  // Database query is async — Event Loop is FREE during I/O wait
  const users = await db.query('SELECT * FROM users');  // non-blocking
  res.json(users);
  // While waiting for DB, Event Loop handles OTHER requests!
});

// ✅ CORRECT: CPU-heavy work → Worker Thread
const { Worker } = require('worker_threads');
app.get('/good/cpu', (req, res) => {
  const worker = new Worker('./heavy-calc.js');  // separate thread
  worker.on('message', result => res.json({ result }));
  // Main thread (Event Loop) is FREE while worker calculates
});

// ⚡ PRODUCTION TIP: process.nextTick for immediate callbacks
app.get('/data', (req, res) => {
  // Force callback to run at start of next iteration
  // Useful for: ensuring cleanup before response
  process.nextTick(() => {
    // This runs before any I/O events in current iteration
    cleanupCache();
  });
  res.json({ status: 'ok' });
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Blocking the Event Loop with synchronous code
```javascript
// WRONG: Synchronous heavy computation = ALL requests blocked
app.get('/process', (req, res) => {
  const result = JSON.parse(hugeJsonString);  // blocks if > 1MB
  res.json(result);
});

// CORRECT: Use streaming or worker threads for large data
app.get('/process', async (req, res) => {
  const result = await processInWorker(hugeJsonString);
  res.json(result);
});
```

❌ **Mistake 2:** Thinking setTimeout(fn, 0) runs immediately
```javascript
// WRONG assumption: setTimeout 0 = "runs next"
setTimeout(() => console.log('first'), 0);
console.log('second');
// Output: "second" first, then "first"
// Sync code ALWAYS runs before any callback
```

❌ **Mistake 3:** Infinite process.nextTick loop
```javascript
// WRONG: Starvation — I/O callbacks NEVER run!
function infiniteNextTick() {
  process.nextTick(infiniteNextTick);  // keeps queuing itself
}
infiniteNextTick();
// Event Loop never gets to POLL phase → no I/O callbacks ever run
// Your HTTP requests time out, DB queries never return
```

---

## 🧠 Tricky Interview Question

**What is the output of this code? Explain why:**

```javascript
setTimeout(() => console.log('timeout'), 0);
setImmediate(() => console.log('immediate'));
Promise.resolve().then(() => console.log('promise'));
process.nextTick(() => console.log('nextTick'));
console.log('sync');
```

**Answer:**
```
sync
nextTick
promise
immediate  (or timeout — ORDER NOT GUARANTEED in main script)
timeout    (or immediate)
```

**Explanation:** (1) `sync` — synchronous, runs first always. (2) `nextTick` — microtask, runs before any Event Loop phase. (3) `promise` — microtask (Promise), runs after nextTick, before phases. (4) `immediate` and `timeout` — their order is **not guaranteed** in the main script (outside I/O callbacks). It depends on how fast the OS timer fires. **However**: Inside an I/O callback (like `fs.readFile`), `setImmediate` ALWAYS comes before `setTimeout(0)` because we've already passed the Timers phase.

---

## ⚫ Interview Questions + Answers

**Q1: What is the Event Loop and why does Node.js need it?**
A1: The Event Loop is a mechanism that makes Node.js non-blocking despite being single-threaded. It monitors: the call stack (sync code), callback queues (timers, I/O callbacks), and microtask queues (nextTick, Promises). When the call stack is empty, it picks the next callback to execute. Node.js needs it because instead of blocking while waiting for I/O (like threads do), it registers a callback and continues. The Event Loop picks up the callback when I/O completes.

**Q2: What are the 6 phases of the Event Loop?**
A2: (1) Timers: runs `setTimeout` + `setInterval` callbacks. (2) Pending Callbacks: I/O callbacks deferred from previous iteration. (3) Idle/Prepare: internal use. (4) Poll: retrieves new I/O events, executes callbacks — blocks here waiting if nothing else is pending. (5) Check: runs `setImmediate` callbacks. (6) Close Callbacks: socket/stream close events. Between phases: microtasks run (process.nextTick first, then Promises).

**Q3: What is the order of execution: setTimeout, setImmediate, nextTick, Promise?**
A3: Order: (1) `process.nextTick` — microtask, highest priority, runs between any two phases. (2) `Promise.then` — microtask, runs after all nextTick callbacks. (3) `setTimeout(fn, 0)` — Timers phase. (4) `setImmediate` — Check phase. Note: setImmediate vs setTimeout order in main script is non-deterministic, but inside an I/O callback, setImmediate ALWAYS runs first.

**Q4: What does "blocking the Event Loop" mean? How do you avoid it?**
A4: Blocking means running synchronous CPU-heavy code that takes long enough to delay the Event Loop from processing other callbacks. During this time, ALL other requests wait. Common causes: `JSON.parse` on huge objects, regex backtracking, crypto operations, `fs.readFileSync` in request handlers. Fixes: (1) Async I/O APIs (`fs.readFile` not `fs.readFileSync`), (2) Worker Threads for CPU-heavy work, (3) Break up large loops with `setImmediate`.

**Q5: Why does process.nextTick run before Promise callbacks?**
A5: Both are microtasks but `process.nextTick` has its own queue that's processed first, then the Promise microtask queue. This is by design in Node.js — `nextTick` was introduced before Promises and was given higher priority. Practical implication: if you schedule both `process.nextTick` and `Promise.resolve().then`, nextTick always runs first. Be careful with recursive `process.nextTick` calls — they can starve I/O callbacks (nextTick queue must drain completely before moving forward).

---

## 🔷 When to Use + When Not to Use
✅ **process.nextTick:** Ensure callback runs before any I/O in current iteration; API design where you want to guarantee async behavior even for sync results.

✅ **setImmediate:** Run something after current I/O callbacks; break up CPU work in chunks (allows I/O between chunks).

✅ **setTimeout(0):** When you need a minimum delay or want timer phase ordering.

❌ **Don't:** Block the Event Loop with sync operations in production servers.

❌ **Don't:** Use recursive process.nextTick — starves I/O.

---

## 📊 Visual Diagram

```
NODE.JS EVENT LOOP:
──────────────────────────────────────────────────────

  ┌─────────────────────────────────┐
  │        CALL STACK               │
  │   (sync code runs here first)   │
  └──────────────┬──────────────────┘
                 │ empty
                 ▼
  ┌──────────────────────────────────────────┐
  │           MICROTASK QUEUES               │
  │  process.nextTick() → Promise.then()     │
  │  (run COMPLETELY between each phase!)    │
  └──────────────────────────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────────┐
  │           EVENT LOOP PHASES              │
  │                                          │
  │  1. TIMERS    → setTimeout, setInterval  │
  │     ↓ [microtasks]                       │
  │  2. PENDING   → deferred I/O callbacks   │
  │     ↓ [microtasks]                       │
  │  3. IDLE/PREPARE (internal)              │
  │     ↓ [microtasks]                       │
  │  4. POLL      → fs, http, db I/O ←──────┼── libuv thread pool
  │     ↓ [microtasks]                       │   (4 default threads)
  │  5. CHECK     → setImmediate             │
  │     ↓ [microtasks]                       │
  │  6. CLOSE     → socket.close callbacks  │
  │     ↓ [microtasks]                       │
  └──────────────────────────────────────────┘
         │
         └──────── loop back to 1. TIMERS

  EXECUTION ORDER (in main script):
  sync → nextTick → Promise → (timers/setImmediate unclear) → I/O callbacks
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event Loop | Mechanism for async execution | Async execution का mechanism |
| Call Stack | LIFO stack for sync execution | Sync code run करने का LIFO stack |
| Microtask Queue | nextTick + Promise callbacks | High-priority callbacks queue |
| Poll Phase | Picks up completed I/O | Completed I/O callbacks उठाता है |
| libuv | C library for async I/O + thread pool | Async I/O + threads manage करता है |
| setImmediate | Check phase callback | Check phase में run होने वाली callback |
| process.nextTick | Runs before next Event Loop phase | अगले phase से पहले run होता है |
| Non-blocking | Not waiting for I/O completion | I/O complete होने का wait नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. Event Loop is Node.js's single-threaded async mechanism — it cycles through 6 phases (Timers → Poll → Check etc.) picking up callbacks from timers, I/O completions, and more.
2. Priority order: sync code → `process.nextTick` → `Promise.then` → Timers (setTimeout) → I/O callbacks (Poll) → setImmediate (Check).
3. Never block the Event Loop with sync CPU work — use Worker Threads for CPU-intensive tasks; all I/O should use async APIs.

**Hindi:**
1. Event Loop Node.js का single-threaded async mechanism है — 6 phases cycle करता है callbacks pick करते हुए।
2. Priority: sync → process.nextTick → Promise.then → setTimeout → I/O callbacks → setImmediate।
3. कभी Event Loop block मत करो sync CPU work से — CPU tasks के लिए Worker Threads use करो।

---

## ➡️ Next Topic
**67. Event Loop Phases** — Each phase in detail with timing guarantees।
