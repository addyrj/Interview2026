# 67. Event Loop Phases — Deep Dive
# हिंदी में: Event Loop के 6 Phases — Detail में

---

## 🔵 Simple Definition (English)
The Event Loop runs in phases. Each phase has a FIFO queue of callbacks to execute. When Node.js enters a phase, it runs all callbacks in that phase's queue (up to a system limit), then moves to the next phase. Between each phase, Node.js processes **microtasks** (process.nextTick + Promise callbacks) completely before moving on. Understanding phases is critical for predicting execution order in Node.js and debugging timing issues.

## 🔵 सरल परिभाषा (Hindi)
Event Loop phases में run होता है। हर phase का अपना FIFO callback queue होता है। Node.js हर phase में उस phase के सभी callbacks run करता है, फिर अगले phase में जाता है। Phases के बीच: **microtasks** (process.nextTick + Promise callbacks) completely run होते हैं। Execution order predict करने और timing issues debug करने के लिए phases की understanding critical है।

---

## 🔴 Problem Understanding Phases Solves
```
WITHOUT KNOWING PHASES:
  setTimeout(() => console.log('A'), 0);
  setImmediate(() => console.log('B'));
  fs.readFile('./file', () => {
    setTimeout(() => console.log('C'), 0);
    setImmediate(() => console.log('D'));
  });
  
  Output? → Can't predict without knowing phases
  
WITH KNOWING PHASES:
  Outside I/O: A and B order uncertain (depends on OS timer)
  Inside I/O callback: D ALWAYS before C
  (because after POLL phase, goes to CHECK immediately, skipping TIMERS)
  
  Answer: A or B (uncertain) → then D → then C
```

---

## 🟢 The 6 Phases in Detail

```
THE 6 PHASES:
──────────────────────────────────────────────────────────────────

PHASE 1: TIMERS
  What runs: setTimeout() and setInterval() callbacks
  
  Timing: NOT exactly on schedule — runs callbacks whose threshold
  has passed. "setTimeout(fn, 100)" means: run fn when ≥100ms elapsed
  
  Key: setInterval doesn't drift — adjusts next fire time after each run
  
  Example:
    setTimeout(() => console.log('timer'), 100);
    // Runs in TIMERS phase after 100ms has passed
    // Actual delay might be 102ms due to system load

  ────────────────────────────────────────────────────────────────
  [between every phase: drain microtask queues]
  
PHASE 2: PENDING CALLBACKS
  What runs: I/O callbacks deferred from previous iteration
  
  When: Some I/O callbacks can't run in the POLL phase of the iteration
  they completed (e.g., network error callbacks on Linux, TCP errors)
  
  Rare: most developers never need to think about this phase
  
  ────────────────────────────────────────────────────────────────
  [between every phase: drain microtask queues]

PHASE 3: IDLE, PREPARE
  What runs: Internal Node.js use only
  
  You can't schedule callbacks here directly
  Used by libuv internally to prepare for the POLL phase
  
  ────────────────────────────────────────────────────────────────
  [between every phase: drain microtask queues]

PHASE 4: POLL ← MOST IMPORTANT
  What runs: New I/O callbacks
  
  This is where Node.js spends most of its time:
  - Retrieves completed I/O events (file reads, network, etc.)
  - Executes their callbacks
  - BLOCKS HERE if:
      * No timers are scheduled
      * Poll queue is empty
      * Waiting for I/O to complete
  - STOPS BLOCKING when:
      * A timer threshold is reached (goes to TIMERS phase)
      * setImmediate scheduled (goes to CHECK phase)
      * I/O completes (processes it)
  
  Example:
    fs.readFile('./data.json', callback)
    // callback runs in POLL phase when file read completes

  ────────────────────────────────────────────────────────────────
  [between every phase: drain microtask queues]

PHASE 5: CHECK
  What runs: setImmediate() callbacks
  
  setImmediate ALWAYS runs after current I/O callbacks complete
  (not after a timer delay — immediately after POLL)
  
  Key insight: setImmediate inside POLL callback runs BEFORE setTimeout
  because after POLL → goes directly to CHECK (phase 5)
  before looping back to TIMERS (phase 1)

  ────────────────────────────────────────────────────────────────
  [between every phase: drain microtask queues]

PHASE 6: CLOSE CALLBACKS
  What runs: 'close' event callbacks
  
  Examples:
    socket.on('close', callback)
    stream.on('close', callback)
    http.Server close events
  
  Cleanup phase: resources being freed

  ────────────────────────────────────────────────────────────────
  [microtasks] → loop back to PHASE 1 TIMERS

MICROTASK QUEUE (between ALL phases):
  Order within microtasks:
  1. process.nextTick() queue (ALL nextTick callbacks first)
  2. Promise microtask queue (ALL Promise.then callbacks)
  
  BOTH queues drain COMPLETELY before moving to next phase
  
  Danger: infinite process.nextTick loop → phases never advance
```

---

## 🟡 Real World Example
**PhonePe payment webhook:** Server receives payment status from Razorpay. The webhook handler: reads DB (POLL phase I/O), updates order status (POLL phase), sends SMS notification (queued with setImmediate — CHECK phase), logs to audit trail (setTimeout 0 — TIMERS phase, next iteration). The developer chose `setImmediate` for SMS because it runs in same Event Loop iteration (after current I/O). `setTimeout(0)` for logging because it's lower priority — acceptable if it runs in next iteration.

---

## 💻 Code Example — Basic

```javascript
// event-loop-phases-demo.js
// Run: node event-loop-phases-demo.js
// Study the output order carefully

const fs = require('fs');

// ─── DEMONSTRATION OF ALL PHASES ─────────────────────────────────────────────

console.log('START');  // synchronous

// PHASE 5: CHECK — setImmediate
setImmediate(() => console.log('setImmediate (CHECK phase)'));

// PHASE 1: TIMERS — setTimeout
setTimeout(() => console.log('setTimeout 0ms (TIMERS phase)'), 0);
setTimeout(() => console.log('setTimeout 50ms (TIMERS phase)'), 50);

// MICROTASK: process.nextTick (highest priority)
process.nextTick(() => {
  console.log('nextTick 1 (microtask)');
  process.nextTick(() => console.log('nextTick 2 nested (microtask)'));
  // Nested nextTick runs before Promise!
});

// MICROTASK: Promise.then (after nextTick)
Promise.resolve()
  .then(() => console.log('Promise 1 (microtask)'))
  .then(() => console.log('Promise 2 chained (microtask)'));

// PHASE 4: POLL — I/O callback
fs.readFile(__filename, 'utf8', (err, data) => {
  console.log('fs.readFile (POLL phase)');
  
  // INSIDE I/O CALLBACK: setImmediate ALWAYS before setTimeout!
  setImmediate(() => console.log('  setImmediate INSIDE I/O (CHECK phase)'));
  setTimeout(() => console.log('  setTimeout INSIDE I/O (TIMERS, next iteration)'), 0);
  
  process.nextTick(() => console.log('  nextTick INSIDE I/O (microtask, runs immediately)'));
  Promise.resolve().then(() => console.log('  Promise INSIDE I/O (microtask)'));
});

console.log('END');  // synchronous

// EXPECTED OUTPUT:
// START
// END
// nextTick 1 (microtask)
// nextTick 2 nested (microtask)    ← nested nextTick before Promise!
// Promise 1 (microtask)
// Promise 2 chained (microtask)
// setTimeout 0ms (TIMERS phase)    ← OR setImmediate first (uncertain in main script)
// setImmediate (CHECK phase)       ← uncertain order with setTimeout in main script
// setTimeout 50ms (TIMERS phase)
// fs.readFile (POLL phase)
//   nextTick INSIDE I/O (microtask, runs immediately)
//   Promise INSIDE I/O (microtask)
//   setImmediate INSIDE I/O (CHECK phase)    ← ALWAYS before setTimeout inside I/O!
//   setTimeout INSIDE I/O (TIMERS, next iteration)  ← next loop iteration
```

## 💻 Code Example — Advanced

```javascript
// advanced-phases.js — Practical patterns using phase knowledge

const fs = require('fs');
const https = require('https');

// ─── 1. BREAKING UP CPU WORK WITH setImmediate ────────────────────────────────
// Problem: large array processing blocks Event Loop
// Solution: process in chunks, yielding between chunks with setImmediate

function processInChunks(items, processFn, onComplete) {
  const CHUNK_SIZE = 100;  // process 100 items, then yield
  let index = 0;

  function processNextChunk() {
    const end = Math.min(index + CHUNK_SIZE, items.length);
    
    for (; index < end; index++) {
      processFn(items[index]);
    }

    if (index < items.length) {
      // Yield to Event Loop: let I/O callbacks run, then continue
      setImmediate(processNextChunk);
      // setImmediate (CHECK phase) runs AFTER POLL phase
      // → any pending I/O callbacks get a chance to run between chunks!
    } else {
      onComplete();
    }
  }

  processNextChunk();
}

// Usage:
const million = Array.from({ length: 1_000_000 }, (_, i) => i);
processInChunks(
  million,
  (item) => { /* process each item */ },
  () => console.log('All items processed!')
);
// HTTP requests can still be handled between chunks!

// ─── 2. setImmediate vs setTimeout timing ────────────────────────────────────
// Outside I/O: order non-deterministic (depends on OS timer precision)
setTimeout(() => {}, 0);    // sometimes before setImmediate
setImmediate(() => {});      // sometimes before setTimeout

// BUT inside I/O callback: setImmediate ALWAYS first
fs.readFile(__filename, () => {
  setTimeout(() => console.log('timeout'), 0);   // next iteration TIMERS
  setImmediate(() => console.log('immediate'));   // this iteration CHECK
  // 'immediate' ALWAYS prints before 'timeout'
});

// ─── 3. process.nextTick for deferring in same iteration ─────────────────────
class EventEmitter {
  on(event, listener) {
    this._listeners = this._listeners || {};
    this._listeners[event] = listener;
  }

  emit(event, data) {
    const listener = this._listeners?.[event];
    if (listener) {
      // Defer to next tick: caller code runs completely first
      process.nextTick(() => listener(data));
      // Why? API consistency: whether you register before or after emit,
      // the behavior is consistent (listener always async)
    }
  }
}

// ─── 4. UNDERSTANDING TIMER DRIFT ────────────────────────────────────────────
// setInterval timer drift demo
let count = 0;
const start = Date.now();

const interval = setInterval(() => {
  count++;
  const expected = count * 100;
  const actual = Date.now() - start;
  const drift = actual - expected;
  
  console.log(`Tick ${count}: expected ${expected}ms, actual ${actual}ms, drift +${drift}ms`);
  
  if (count >= 5) clearInterval(interval);
}, 100);

// If Event Loop is blocked 50ms:
// Tick 1: 100ms ✅
// Tick 2: 250ms! (expected 200ms) ← drift from blocking
// Node.js compensates: adjusts next interval fire time

// ─── 5. nextTick FLOOD — danger ──────────────────────────────────────────────
// DANGER: nextTick callbacks that queue more nextTick callbacks
// starve the Event Loop — I/O callbacks never run!

// WRONG:
function recursiveNextTick(count) {
  if (count <= 0) return;
  process.nextTick(() => {
    // This will prevent I/O callbacks from ever running!
    recursiveNextTick(count - 1);  // ← queues another nextTick
  });
}
// recursiveNextTick(1000000);  // DON'T run this — blocks Event Loop

// CORRECT for recursive async work: setImmediate (allows I/O between iterations)
function recursiveImmediate(count) {
  if (count <= 0) return;
  setImmediate(() => {
    // CHECK phase: I/O (POLL phase) can run before this in each iteration
    recursiveImmediate(count - 1);
  });
}
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// ─── HOW PHASES AFFECT EXPRESS ────────────────────────────────────────────────

// Route handlers run in POLL phase (from HTTP I/O callback)
app.get('/data', async (req, res) => {
  // This is running in POLL phase

  const data = await db.query('SELECT...');  // awaits POLL phase completion
  
  // After await: continues in new POLL phase iteration
  
  // setImmediate inside handler: runs in CHECK phase, same iteration
  setImmediate(() => {
    // Log after response is sent — doesn't block response
    logToAnalytics(req.url, data.length);
  });
  
  res.json(data);  // sends response synchronously
});

// ─── USING process.nextTick IN MIDDLEWARE ─────────────────────────────────────
const requestIdMiddleware = (req, res, next) => {
  req.requestId = generateId();
  
  // process.nextTick ensures consistent async behavior:
  // "call next on next tick" instead of synchronously
  process.nextTick(next);
  // Useful when: middleware may or may not be async,
  // and you want consistent behavior regardless
};

// ─── HEAVY PROCESSING: use setImmediate to yield ─────────────────────────────
app.post('/process-csv', async (req, res) => {
  const rows = parseCsv(req.body.csv);  // might be large
  const results = [];
  
  // Process CSV in chunks, yielding between chunks
  await new Promise(resolve => {
    processInChunks(
      rows,
      (row) => results.push(transformRow(row)),
      resolve  // called when done
    );
  });
  
  res.json({ processed: results.length });
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting exact timer timing
```javascript
// WRONG assumption: setTimeout(fn, 100) fires at exactly 100ms
setTimeout(() => {
  // Fires at ≥100ms, not exactly 100ms
  // If Event Loop is busy processing I/O, it might fire at 150ms
}, 100);

// CORRECT: Use for minimum delay, not exact timing
// For exact timing: external clock service, or accept ±10ms variance
```

❌ **Mistake 2:** setImmediate vs setTimeout confusion inside vs outside I/O
```javascript
// OUTSIDE I/O callback: order is NOT guaranteed
setTimeout(() => console.log('A'), 0);  // might be first
setImmediate(() => console.log('B'));    // might be first

// INSIDE I/O callback: setImmediate ALWAYS first
fs.readFile('./file', () => {
  setTimeout(() => console.log('A'), 0);    // SECOND (next iteration)
  setImmediate(() => console.log('B'));      // FIRST (same iteration CHECK)
});
```

❌ **Mistake 3:** infinite process.nextTick
```javascript
// WRONG: this starves I/O — HTTP requests never processed!
process.nextTick(function tick() {
  process.nextTick(tick);  // schedules itself recursively
});

// CORRECT: use setImmediate for recursive work
setImmediate(function tick() {
  setImmediate(tick);  // yields to POLL phase each iteration
});
```

---

## 🧠 Tricky Interview Question

**Q: Why does `setImmediate` always run before `setTimeout(fn, 0)` inside an I/O callback?**

**Answer:** When inside an I/O callback, you're currently in the **POLL** phase (phase 4). The Event Loop has already passed the **TIMERS** phase (phase 1) for this iteration. After POLL, the Loop goes to **CHECK** phase (phase 5) where `setImmediate` callbacks run — WITHOUT looping back to TIMERS first. `setTimeout(fn, 0)` must wait for the next iteration's TIMERS phase. So the sequence inside an I/O callback: current POLL → microtasks → CHECK (setImmediate runs!) → CLOSE → back to TIMERS (setTimeout runs). This is why inside I/O, `setImmediate` is guaranteed to run before `setTimeout(fn, 0)`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the POLL phase and why is it the most important?**
A1: The POLL phase (phase 4) is where Node.js spends most of its time. It: (1) retrieves completed I/O events from the OS (epoll/kqueue/IOCP), (2) executes their callbacks (file reads, network responses, database responses), (3) blocks and waits if poll queue is empty and no timers are due — this is how Node.js waits for new I/O without busy-waiting. Most of your application code runs in the POLL phase (db query callbacks, HTTP request handlers, file operation callbacks). It's the heart of Node.js's non-blocking model.

**Q2: What happens between phases?**
A2: Between each phase, Node.js drains the **microtask queues** completely: (1) First: all `process.nextTick()` callbacks (in the order queued). (2) Then: all `Promise.then()` callbacks. If a nextTick or Promise callback schedules more nextTick/Promise callbacks, those also run before moving to the next phase. This means microtasks always run "at the end of the current operation, before the next phase." The critical implication: an infinite loop of `process.nextTick` callbacks starves the Event Loop — I/O callbacks never get to run.

**Q3: What is the difference between `process.nextTick` and `Promise.then` timing?**
A3: Both are microtasks running between phases, but `process.nextTick` has its own queue processed FIRST, before the Promise microtask queue. This is historical (nextTick predates Promises in Node.js) and preserved for backwards compatibility. Example: if you schedule both `process.nextTick(fn1)` and `Promise.resolve().then(fn2)`, `fn1` always runs before `fn2`. If `fn1` itself calls `process.nextTick(fn3)`, then `fn3` also runs before `fn2` (nextTick queue drains completely first).

**Q4: When would you use `setImmediate` vs `setTimeout(fn, 0)`?**
A4: Use `setImmediate` when: (1) you want to run code after current I/O callbacks complete (same iteration), (2) breaking up CPU work in chunks where I/O should interleave, (3) performance matters (CHECK phase is directly after POLL). Use `setTimeout(fn, 0)` when: (1) compatibility (all environments have setTimeout, not all have setImmediate), (2) you want browser-compatible code, (3) the exact phase doesn't matter, just "next async slot." Key rule: inside I/O callbacks, use `setImmediate` — it's unambiguous. In main script: either works, but `setImmediate` is cleaner if you specifically want "after I/O."

**Q5: What is timer resolution and why does `setTimeout(fn, 0)` not fire at exactly 0ms?**
A5: `setTimeout(fn, 0)` sets a minimum delay of 0ms, but the actual minimum in Node.js is typically 1ms (spec says minimum 4ms in browsers). The TIMERS phase only runs callbacks whose threshold HAS PASSED — not exactly when it passes. If Node.js is busy processing I/O callbacks when the timer fires, the timer callback waits until the POLL phase completes and the loop returns to TIMERS. Additionally, OS timer resolution varies (~1-10ms). So `setTimeout(fn, 0)` might actually fire anywhere from 1-15ms after being scheduled. For precise timing, use `process.hrtime()` for measurement and accept scheduling imprecision.

---

## 📊 Visual Diagram

```
EVENT LOOP PHASES CYCLE:
──────────────────────────────────────────────────────────────────

  ┌────────────────────────────────────────────────────────────┐
  │                   MICROTASKS                               │
  │  process.nextTick queue → Promise.then queue              │
  │  (run COMPLETELY between every phase transition)           │
  └────────────────────────────────────────────────────────────┘
                 ↑↑↑ runs between every phase below ↑↑↑

  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 1: TIMERS                                             │
  │  setTimeout() ≥ threshold → run callback                    │
  │  setInterval() ≥ threshold → run callback                   │
  └──────────────────────────┬───────────────────────────────────┘
                             │ [microtasks]
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 2: PENDING I/O CALLBACKS                              │
  │  Deferred I/O from previous iteration (rare)                │
  └──────────────────────────┬───────────────────────────────────┘
                             │ [microtasks]
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 3: IDLE / PREPARE (internal)                          │
  └──────────────────────────┬───────────────────────────────────┘
                             │ [microtasks]
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 4: POLL ← most time spent here                        │
  │  ● Execute I/O callbacks (fs, net, db)                       │
  │  ● Block waiting for I/O if queue empty                     │
  │  ● Stop blocking if: timer threshold reached OR setImmediate │
  └──────────────────────────┬───────────────────────────────────┘
                             │ [microtasks]
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 5: CHECK                                              │
  │  setImmediate() callbacks run here                           │
  │  Runs directly AFTER POLL — before looping to TIMERS         │
  └──────────────────────────┬───────────────────────────────────┘
                             │ [microtasks]
                             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PHASE 6: CLOSE CALLBACKS                                    │
  │  socket.on('close', ...), stream.on('close', ...)           │
  └──────────────────────────┬───────────────────────────────────┘
                             │ [microtasks]
                             │
                             └──────── back to PHASE 1 TIMERS

  INSIDE I/O CALLBACK: setImmediate runs in same iteration (CHECK)
                        setTimeout(0) runs in NEXT iteration (TIMERS)
  OUTSIDE I/O:          Order between setImmediate and setTimeout(0) is non-deterministic
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TIMERS phase | Runs setTimeout/setInterval callbacks | setTimeout/setInterval callbacks |
| POLL phase | Retrieves + runs I/O callbacks | I/O callbacks run होती हैं |
| CHECK phase | Runs setImmediate callbacks | setImmediate callbacks |
| Microtask | nextTick + Promise, run between phases | Phases के बीच run होने वाले tasks |
| Phase queue | FIFO queue of callbacks per phase | हर phase का callback queue |
| Timer threshold | Minimum delay before setTimeout fires | setTimeout fire होने का minimum delay |
| setImmediate | Phase 5 (CHECK) callback | Phase 5 में run होने वाली callback |
| I/O starvation | I/O callbacks never run due to nextTick flood | nextTick flood से I/O block |

---

## ⚡ 3-Line Summary
**English:**
1. Event Loop: 6 phases (TIMERS → POLL → CHECK → CLOSE) with microtasks (nextTick → Promise) draining completely between each phase.
2. Critical rule: inside an I/O callback, `setImmediate` ALWAYS runs before `setTimeout(fn, 0)` — because CHECK phase comes directly after POLL, before looping back to TIMERS.
3. Avoid infinite `process.nextTick` chains — they starve the POLL phase; use `setImmediate` for recursive async work to allow I/O between iterations.

**Hindi:**
1. Event Loop: 6 phases, phases के बीच microtasks (nextTick → Promise) completely run।
2. Rule: I/O callback के अंदर `setImmediate` ALWAYS `setTimeout(0)` से पहले — CHECK phase POLL के directly बाद आती है।
3. Infinite `process.nextTick` avoid करो — I/O starve होता है; recursive work के लिए `setImmediate` use करो।

---

## ➡️ Next Topic
**68. process.nextTick vs setImmediate** — Deep comparison with practical use cases।
