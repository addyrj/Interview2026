# 62. timer Module (setTimeout, setInterval, setImmediate)
# हिंदी में: Timer Functions — setTimeout, setInterval, setImmediate

---

## 🔵 Simple Definition (English)
Node's timer functions — **`setTimeout(fn, ms)`** (run once after a delay), **`setInterval(fn, ms)`** (run repeatedly every interval), **`setImmediate(fn)`** (run once, immediately after the current I/O phase) — schedule code to run LATER, asynchronously, without blocking the current execution. They're global functions (no `require()` needed for the basics, though `timers/promises` offers Promise-based versions).

## 🔵 सरल परिभाषा (Hindi)
Node के timer functions — **`setTimeout(fn, ms)`** (एक बार delay के बाद चलना), **`setInterval(fn, ms)`** (हर interval पर repeatedly चलना), **`setImmediate(fn)`** (current I/O phase के बाद एक बार चलना) — code को बाद में, asynchronously चलाने के लिए schedule करते हैं, current execution को block किए बिना। ये global functions हैं।

---

## 🔴 Problem it Solves
JavaScript needs a way to defer execution — delaying a retry, polling periodically, or yielding control back to the event loop to let pending I/O callbacks run before continuing CPU-heavy work. Without timers, you'd have no way to schedule "do this later" or "do this repeatedly" without busy-waiting (which would peg the CPU and block everything else). Node's timers integrate with libuv's event loop, letting scheduled callbacks run at the right phase without blocking other operations in the meantime.

## 🔴 यह क्यों बना? (Hindi)
JavaScript को execution defer करने का तरीका चाहिए — retry delay करना, periodically poll करना, या heavy काम के बीच event loop को control वापस देना ताकि pending I/O callbacks चल सकें। Timers के बिना busy-waiting करना पड़ता (जो CPU को लॉक कर देता)। Node के timers libuv के event loop से integrate होते हैं, scheduled callbacks सही phase पर चलते हैं बिना बाकी operations को block किए।

---

## 🟢 How it Works — Step by Step

Step 1 → **`setTimeout(callback, delayMs, ...args)`**: schedules `callback` to run ONCE after AT LEAST `delayMs` milliseconds (not exact — depends on event loop load). Returns a `Timeout` object; `clearTimeout(id)` cancels it before it fires.
Step 2 → **`setInterval(callback, intervalMs)`**: schedules `callback` to run REPEATEDLY every `intervalMs`, until `clearInterval(id)` is called. Important: if `callback` itself takes longer than `intervalMs`, intervals can overlap/queue up (a common source of bugs).
Step 3 → **`setImmediate(callback)`**: schedules `callback` to run in the CHECK phase of the event loop, immediately after the current POLL phase (I/O callbacks) completes — useful for deferring work until after I/O events have been processed, but before the next event loop tick's timers.
Step 4 → **Timer phase ordering**: in a FRESH event loop tick (not inside an I/O callback), `setTimeout(fn, 0)` and `setImmediate(fn)` order is NOT guaranteed (depends on system performance). INSIDE an I/O callback, `setImmediate()` ALWAYS fires before `setTimeout(fn, 0)` — because `setImmediate` runs in the check phase, which comes right after poll (I/O), while `setTimeout` has to wait for the NEXT loop iteration's timer phase.
Step 5 → **`process.nextTick(callback)`** (related but distinct, not in `timers`): runs EVEN SOONER than `setImmediate` — before the event loop even continues to its next phase, processed after the current operation completes but before I/O events.
Step 6 → **`timers/promises`** module (Node 15+): `const { setTimeout } = require('timers/promises'); await setTimeout(1000);` — Promise-based delays for use with `async/await`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **`setTimeout()`**: `callback` को कम से कम `delayMs` के बाद एक बार चलाता है। `clearTimeout(id)` से cancel कर सकते हो।
Step 2 → **`setInterval()`**: `callback` को repeatedly चलाता है, `clearInterval(id)` तक। अगर callback interval से लंबा चले, overlap हो सकता है।
Step 3 → **`setImmediate()`**: current I/O (poll phase) के बाद check phase में चलता है।
Step 4 → **Phase ordering**: fresh tick में `setTimeout(fn,0)` vs `setImmediate()` order guaranteed नहीं; I/O callback के अंदर `setImmediate()` हमेशा पहले चलता है।
Step 5 → **`process.nextTick()`**: `setImmediate` से भी पहले चलता है, current operation के बाद तुरंत।
Step 6 → **`timers/promises`**: Promise-based delays, `async/await` के साथ।

---

## 🟡 Real World Example
**Swiggy's order-timeout handling:** When a customer places an order, the backend starts a `setTimeout(checkOrderStatus, 30 * 60 * 1000)` (30 minutes) — if the order hasn't been marked "delivered" by then, it triggers a customer-support alert. If the order IS delivered before 30 minutes, `clearTimeout()` cancels the pending check, preventing unnecessary work. Meanwhile, their delivery-partner location-polling service uses `setInterval(pollLocations, 5000)` to fetch GPS updates every 5 seconds — careful attention is paid to ensure the polling function completes well within the 5-second window to avoid overlapping calls piling up.

## 🟡 Real Example Hindi mein
**Swiggy का order-timeout handling:** Order place होने पर backend `setTimeout(checkOrderStatus, 30*60*1000)` start करता है — 30 minutes में deliver न हो तो support alert। Delivered हो जाए तो `clearTimeout()` से cancel। Delivery-partner location polling `setInterval(poll, 5000)` से हर 5 seconds — care रखा जाता है कि function 5 seconds के अंदर पूरा हो, overlap न हो।

---

## 💻 Code Example — Basic
```javascript
// timers-basics.js

// 1. setTimeout -- run once after a delay
console.log('Start');
const timeoutId = setTimeout(() => {
  console.log('This runs after 1 second');
}, 1000);
console.log('End (this prints BEFORE the timeout fires)');

// 2. clearTimeout -- cancel a scheduled timeout before it fires
const willBeCancelled = setTimeout(() => console.log('You should never see this'), 2000);
clearTimeout(willBeCancelled); // cancelled before the 2 seconds pass

// 3. setInterval -- run repeatedly, with clearInterval to stop it
let count = 0;
const intervalId = setInterval(() => {
  count++;
  console.log('Interval tick:', count);
  if (count >= 3) {
    clearInterval(intervalId); // MUST clear, or it runs forever
    console.log('Interval stopped');
  }
}, 500);

// 4. setImmediate -- runs after the current I/O/poll phase
setImmediate(() => console.log('setImmediate callback'));
console.log('Synchronous code runs before setImmediate callback');

// 5. timers/promises -- Promise-based delay for async/await
const { setTimeout: delay } = require('timers/promises');
async function delayedGreeting() {
  console.log('Waiting 1 second...');
  await delay(1000);
  console.log('Done waiting!');
}
delayedGreeting();
```

## 💻 Code Example — Advanced
```javascript
// timers-advanced.js -- production patterns
const { setTimeout: delay } = require('timers/promises');

// ─── 1. RETRY WITH EXPONENTIAL BACKOFF USING setTimeout ──────────────────────
async function retryWithBackoff(fn, maxRetries = 5) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxRetries) throw err;
      const backoffMs = Math.min(1000 * 2 ** attempt, 30000); // exponential, capped at 30s
      console.log(`Attempt ${attempt} failed, retrying in ${backoffMs}ms`);
      await delay(backoffMs);
    }
  }
}

// ─── 2. SAFE POLLING PATTERN (avoiding overlapping setInterval calls) ────────
function safePolling(fn, intervalMs) {
  let isRunning = false;
  const id = setInterval(async () => {
    if (isRunning) return; // skip this tick if the previous call hasn't finished
    isRunning = true;
    try {
      await fn();
    } catch (err) {
      console.error('Polling error:', err.message);
    } finally {
      isRunning = false;
    }
  }, intervalMs);
  return () => clearInterval(id); // return a cleanup function
}

// ─── 3. TIMEOUT WRAPPER FOR A PROMISE (race against a deadline) ─────────────
function withTimeout(promise, timeoutMs, timeoutMessage = 'Operation timed out') {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error(timeoutMessage)), timeoutMs)
    ),
  ]);
}

async function fetchWithTimeout(url, ms) {
  try {
    const response = await withTimeout(fetch(url), ms, `Request to ${url} timed out`);
    return response;
  } catch (err) {
    console.error(err.message);
    throw err;
  }
}

// ─── 4. DEMONSTRATING TIMER PHASE ORDERING (nextTick vs setImmediate vs setTimeout) ─
const fs = require('fs');

fs.readFile(__filename, () => { // inside an I/O callback (poll phase)
  setTimeout(() => console.log('1. setTimeout'), 0);
  setImmediate(() => console.log('2. setImmediate')); // ALWAYS fires before setTimeout here
  process.nextTick(() => console.log('0. process.nextTick')); // fires before BOTH
});
// Guaranteed order inside an I/O callback: nextTick -> setImmediate -> setTimeout

module.exports = { retryWithBackoff, safePolling, withTimeout, fetchWithTimeout };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const { setTimeout: delay } = require('timers/promises');
const app = express();

// 1. REQUEST TIMEOUT MIDDLEWARE USING setTimeout + Promise.race
function requestTimeout(ms) {
  return (req, res, next) => {
    const timer = setTimeout(() => {
      if (!res.headersSent) res.status(504).json({ error: 'Request timed out' });
    }, ms);
    res.on('finish', () => clearTimeout(timer)); // cancel the timeout once response completes
    next();
  };
}
app.use(requestTimeout(5000)); // 5-second timeout for all routes

// 2. DELAYED/SCHEDULED TASK AFTER A RESPONSE (e.g. sending a follow-up notification)
app.post('/orders', express.json(), (req, res) => {
  const order = { id: Date.now(), ...req.body };
  res.status(201).json(order); // respond immediately

  // Schedule a follow-up reminder 30 minutes later, independent of this request/response cycle
  setTimeout(() => {
    console.log(`Checking status of order ${order.id}...`);
    // checkOrderStatusAndNotify(order.id) -- real logic here
  }, 30 * 60 * 1000);
});

// 3. BACKGROUND POLLING JOB STARTED ALONGSIDE THE SERVER
let isPolling = false;
function startBackgroundSync() {
  setInterval(async () => {
    if (isPolling) return; // avoid overlap if previous sync is still running
    isPolling = true;
    try {
      console.log('Syncing inventory from warehouse API...');
      // await syncInventoryData();
    } finally {
      isPolling = false;
    }
  }, 60000); // every 60 seconds
}
startBackgroundSync();

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to `clearInterval()`, causing a memory/resource leak
```javascript
// Wrong -- interval runs forever, even after the relevant work is done, leaking resources
function startPolling() {
  setInterval(() => checkStatus(), 1000); // never cleared!
}

// Correct -- always store the ID and clear it when no longer needed
function startPolling() {
  const id = setInterval(() => checkStatus(), 1000);
  return () => clearInterval(id); // caller can stop polling when appropriate
}
```

❌ Mistake 2: Assuming `setTimeout(fn, ms)` guarantees EXACT timing
```javascript
// Wrong assumption -- treating setTimeout as a precise scheduler
setTimeout(() => console.log('Exactly 100ms later'), 100);
// In reality: fires AT LEAST 100ms later, possibly much later if the event loop is busy

// Correct mindset -- treat the delay as a MINIMUM, not a guarantee, especially under load
setTimeout(() => console.log('At least 100ms later, possibly more'), 100);
```

❌ Mistake 3: Letting `setInterval` callbacks overlap when the callback itself is slow/async
```javascript
// Wrong -- if checkStatus() takes 3 seconds but interval is 1 second, calls pile up
setInterval(async () => { await checkStatus(); }, 1000); // multiple concurrent calls possible

// Correct -- use a flag or recursive setTimeout to ensure sequential execution
let running = false;
setInterval(async () => {
  if (running) return;
  running = true;
  await checkStatus();
  running = false;
}, 1000);
```

---

## 🧠 Tricky Interview Question
```javascript
console.log('1');

setTimeout(() => console.log('2'), 0);

Promise.resolve().then(() => console.log('3'));

process.nextTick(() => console.log('4'));

console.log('5');
```
Answer: Output is `1`, `5`, `4`, `3`, `2`. Here's why: `1` and `5` are SYNCHRONOUS code, running immediately before anything async. Among the async callbacks, Node processes the **microtask queue** (which includes `process.nextTick` callbacks AND Promise `.then()` callbacks) BEFORE moving to the next **macrotask** (timer) phase. Within the microtask queue, `process.nextTick()` callbacks are processed BEFORE Promise callbacks (Node-specific prioritization) — so `4` (nextTick) prints before `3` (Promise.then). Only after the ENTIRE microtask queue drains does Node proceed to the timer phase, firing the `setTimeout` callback, printing `2` LAST — even though it was scheduled with a `0`ms delay, it still waits behind all microtasks.

---

## ⚫ Interview Questions + Answers

Q1: Does `setTimeout(fn, 0)` run immediately (synchronously)?
A1: No — even with a 0ms delay, `setTimeout` always schedules the callback to run ASYNCHRONOUSLY, in the next iteration of the event loop's timer phase, AFTER the current synchronous code finishes AND after the microtask queue (Promises, `process.nextTick`) has been fully drained. It never runs synchronously, regardless of the delay value.

Q2: What's the difference between `setImmediate()` and `setTimeout(fn, 0)`?
A2: Both schedule a callback to run "as soon as possible" asynchronously, but they execute in DIFFERENT event loop phases: `setImmediate()` runs in the CHECK phase (right after the current POLL/I/O phase). `setTimeout(fn, 0)` runs in the TIMERS phase (at the start of the next loop iteration). When called from WITHIN an I/O callback, `setImmediate()` is GUARANTEED to fire first (since check comes right after poll). When called from the TOP-LEVEL/main module (not inside I/O), the order between them is NOT guaranteed and can vary based on system performance.

Q3: Why can `setInterval` callbacks "pile up" or overlap, and how do you prevent it?
A3: `setInterval` schedules a new invocation every `intervalMs` REGARDLESS of whether the previous invocation's callback has finished — if the callback does async work (a DB query, an API call) that takes LONGER than the interval, multiple invocations can end up running concurrently, potentially causing race conditions or resource exhaustion. Prevent it with a guard flag (`if (running) return;`) or by using a recursive `setTimeout` pattern instead, which only schedules the NEXT call after the current one finishes.

Q4: What is `process.nextTick()`, and how does its priority compare to `setImmediate()` and Promise callbacks?
A4: `process.nextTick()` schedules a callback to run at the very END of the current operation, BEFORE the event loop continues to any other phase — it has the HIGHEST priority among Node's async scheduling mechanisms. Priority order (highest to lowest): `process.nextTick()` callbacks → Promise `.then()`/microtask callbacks → `setTimeout`/`setInterval` (timers phase) → I/O callbacks (poll phase) → `setImmediate()` (check phase) → close callbacks. Excessive use of `process.nextTick()` recursively can starve the event loop (I/O never gets a chance to run), which is why it should be used sparingly.

Q5: How would you implement a Promise-based delay function, and does Node provide one built-in?
A5: Manually: `function delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }`, then `await delay(1000);`. Node 15+ provides this built-in via `require('timers/promises')`: `const { setTimeout } = require('timers/promises'); await setTimeout(1000);` — functionally identical but standardized and avoids reinventing the wrapper in every project.

---

## 🔷 When to Use + When Not to Use
✅ Use `setTimeout` when:
- Delaying a single action (retry after backoff, debouncing, scheduled follow-ups)

✅ Use `setInterval` when:
- Polling or repeating an action at a fixed cadence (with overlap protection)

✅ Use `setImmediate` when:
- You need to defer work until after the current I/O phase completes, without an arbitrary delay value

❌ Avoid when:
- You need PRECISE, real-time-accurate scheduling — Node's timers are best-effort, not hard real-time guarantees
- Using `setInterval` without overlap protection for async callbacks that might run longer than the interval

---

## 📊 Visual Diagram
```
EVENT LOOP PHASES (simplified) AND TIMER PLACEMENT:

  ┌───────────────────────────┐
  │     TIMERS phase            │  ← setTimeout, setInterval callbacks run here
  ├───────────────────────────┤
  │   Pending callbacks          │
  ├───────────────────────────┤
  │   POLL phase (I/O)           │  ← fs/network callbacks run here
  ├───────────────────────────┤
  │   CHECK phase                │  ← setImmediate callbacks run here
  ├───────────────────────────┤
  │   CLOSE callbacks            │
  └───────────────────────────┘
          (loop repeats)

  process.nextTick() + Promise microtasks run BETWEEN every phase transition,
  BEFORE the event loop proceeds to the next phase.

PRIORITY ORDER (highest to lowest):
  process.nextTick()  >  Promise .then()  >  setTimeout/setInterval  >  I/O  >  setImmediate
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| setTimeout | Run once after a delay | Delay के बाद एक बार चलना |
| setInterval | Run repeatedly at an interval | Interval पर repeatedly चलना |
| setImmediate | Run after current I/O phase | Current I/O phase के बाद चलना |
| process.nextTick | Highest-priority microtask | सबसे high-priority microtask |
| clearTimeout/clearInterval | Cancel a scheduled timer | Scheduled timer cancel करना |
| timers/promises | Promise-based timer APIs | Promise-based timer APIs |

---

## ⚡ 3-Line Summary
English: `setTimeout`/`setInterval` schedule delayed/repeated execution; `setImmediate` runs right after the current I/O phase. Timing is best-effort, not exact — delays are minimums, not guarantees. `process.nextTick()` and Promise microtasks always run before the next timer phase, with `nextTick` having the highest priority of all.

Hindi: `setTimeout`/`setInterval` delayed/repeated execution schedule करते हैं; `setImmediate` current I/O phase के बाद चलता है। Timing best-effort है, exact नहीं। `process.nextTick()` और Promise microtasks हमेशा next timer phase से पहले चलते हैं, `nextTick` सबसे high priority।

---

## ➡️ Next Topic
**63. assert Module** — Node's built-in assertion library for writing tests and runtime invariant checks.
