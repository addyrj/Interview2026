# 74. Microtasks — process.nextTick
# हिंदी में: Microtasks — process.nextTick

---

## 🔵 Simple Definition (English)
**`process.nextTick(callback)`** schedules a callback to run at the very end of the CURRENT operation, before the event loop proceeds to the next phase — even before Promise callbacks. It's the HIGHEST priority async scheduling mechanism in Node.js. It is NOT part of the official "microtask" spec (that's Promises), but Node treats it with even higher priority than microtasks.

## 🔵 सरल परिभाषा (Hindi)
**`process.nextTick(callback)`** callback को current operation के बिल्कुल end में run करने के लिए schedule करता है, event loop के next phase में जाने से पहले — Promise callbacks से भी पहले। ये Node.js में सबसे highest priority वाला async scheduling mechanism है।

---

## 🔴 Problem it Solves
```
NEED: Sometimes an API needs to guarantee ASYNC behavior consistently,
      even when the result is available synchronously — to avoid
      "sometimes sync, sometimes async" bugs (Zalgo problem).

EXAMPLE PROBLEM:
  function getData(cb) {
    if (cache.has(key)) {
      cb(cache.get(key));       // SYNCHRONOUS call
    } else {
      fetchFromDb(key, cb);     // ASYNCHRONOUS call
    }
  }
  // Caller can't predict if cb runs sync or async — causes subtle bugs
  // (e.g., try/catch around getData() won't catch errors from async cb)

WITH process.nextTick:
  function getData(cb) {
    if (cache.has(key)) {
      process.nextTick(() => cb(cache.get(key)));  // FORCE async
    } else {
      fetchFromDb(key, cb);
    }
  }
  // Now cb ALWAYS runs asynchronously — consistent, predictable behavior
```

## 🔴 यह क्यों बना? (Hindi)
```
कभी-कभी API को हमेशा async behavior guarantee करना होता है,
भले ही result sync में available हो (Zalgo problem से बचने के लिए)
process.nextTick से callback को force async बनाया जा सकता है
Caller हमेशा consistent async behavior पर depend कर सकता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → process.nextTick(callback) is called
Step 2 → callback is pushed onto the "nextTick queue"
Step 3 → Current synchronous operation finishes executing
Step 4 → BEFORE the event loop moves to ANY phase (or even to the
          Promise microtask queue), Node fully DRAINS the nextTick queue
Step 5 → If a nextTick callback schedules ANOTHER nextTick, that ALSO
          runs before moving on (can cause starvation if done recursively!)
Step 6 → Once nextTick queue is empty → Promise microtask queue drains
Step 7 → THEN the event loop proceeds to its next phase (Timers, etc.)
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. process.nextTick(callback) call होता है
2. callback "nextTick queue" में जाता है
3. Current sync operation खत्म होता है
4. Event loop किसी phase या Promise queue में जाने से पहले nextTick queue पूरी तरह drain करता है
5. nested nextTick भी इसी iteration में run होता है (recursive होने पर starvation हो सकता है)
6. फिर Promise queue, फिर event loop phases
```

---

## 🟡 Real World Example
**Paytm's EventEmitter pattern:** When Paytm's internal SDK emits an event immediately after object construction (e.g., `new PaymentSession()` which should emit `'ready'`), they use `process.nextTick()` to ensure listeners attached AFTER construction (but in the same synchronous block) still receive the event — because the emit is deferred to nextTick, giving calling code a chance to attach `.on('ready', ...)` before the event actually fires. This is the exact pattern Node's core `EventEmitter`-based APIs use internally.

## 🟡 Real Example Hindi mein
**Paytm SDK:** Object construction के ठीक बाद event emit करना है (`new PaymentSession()` → `'ready'` event)। `process.nextTick()` से emit थोड़ा delay होता है ताकि calling code को `.on('ready')` attach करने का मौका मिले construction के बाद भी, event fire होने से पहले।

---

## 💻 Code Example — Basic

```javascript
// nexttick-basic.js
// Run: node nexttick-basic.js

console.log('1: sync start');

process.nextTick(() => {
  console.log('3: nextTick callback');
});

console.log('2: sync end');

// OUTPUT:
// 1: sync start
// 2: sync end
// 3: nextTick callback
// Explanation: nextTick runs AFTER current sync code finishes,
// but BEFORE the event loop moves to any phase (Timers, Poll, etc.)

// Classic use case: forcing consistent async behavior
function getUser(id, callback) {
  const cache = { 1: { id: 1, name: 'Rahul' } };
  if (cache[id]) {
    // Without nextTick, this would call back SYNCHRONOUSLY, unlike the else branch
    process.nextTick(() => callback(null, cache[id]));
  } else {
    setTimeout(() => callback(null, { id, name: 'Fetched from DB' }), 100);
  }
}

getUser(1, (err, user) => console.log('4: got user (always async):', user));
console.log('This always logs before "got user" regardless of cache hit/miss');
```

## 💻 Code Example — Advanced

```javascript
// nexttick-advanced.js — EventEmitter pattern using nextTick for safe event timing

const EventEmitter = require('events');

class PaymentSession extends EventEmitter {
  constructor(orderId) {
    super();
    this.orderId = orderId;
    this.status = 'initializing';

    // Defer the 'ready' emit to nextTick — gives the CALLER a chance
    // to attach .on('ready', ...) listeners AFTER construction but
    // in the same synchronous block, before the event actually fires
    process.nextTick(() => {
      this.status = 'ready';
      this.emit('ready', { orderId: this.orderId });
    });
  }
}

const session = new PaymentSession('ORD-9001');

// This listener is attached AFTER the constructor runs, but BEFORE
// the nextTick-deferred emit fires — so it correctly receives the event!
session.on('ready', (data) => {
  console.log('Session ready:', data);
});

// WITHOUT process.nextTick in the constructor, emit('ready') would fire
// SYNCHRONOUSLY during construction — before this .on() call even runs,
// and the listener would MISS the event entirely.

// ─── Demonstrating starvation risk ──────────────────────────────────────────
let count = 0;
function riskyRecursiveNextTick() {
  count++;
  if (count < 5) {
    process.nextTick(riskyRecursiveNextTick);  // keeps re-queuing itself
  } else {
    console.log('Finished 5 recursive nextTicks — if this were unbounded,');
    console.log('it would starve the event loop, blocking ALL I/O forever!');
  }
}
process.nextTick(riskyRecursiveNextTick);
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// Real use: ensure response cleanup logic runs consistently async,
// even when some fast-path logic completes synchronously
app.get('/orders/:id', (req, res) => {
  const cachedOrder = getCachedOrder(req.params.id);

  if (cachedOrder) {
    // Force async behavior even for the cache-hit fast path, so that
    // middleware/logging that expects consistent timing isn't broken
    process.nextTick(() => {
      res.json(cachedOrder);
    });
  } else {
    fetchOrderFromDb(req.params.id).then((order) => res.json(order));
  }
});

function getCachedOrder(id) { return id === '1' ? { id, cached: true } : null; }
function fetchOrderFromDb(id) {
  return new Promise((resolve) => setTimeout(() => resolve({ id, cached: false }), 50));
}

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Recursive `process.nextTick` starving the event loop
```javascript
// WRONG: infinite recursion — I/O callbacks (HTTP requests, DB responses)
// NEVER get a chance to run because nextTick queue never empties!
function loop() {
  process.nextTick(loop);
}
loop();
// Your server will accept connections but NEVER respond — total freeze

// CORRECT: use setImmediate for repeated work instead, which yields
// to the Poll phase (I/O) between iterations
function safeLoop() {
  setImmediate(safeLoop);
}
```

❌ **Mistake 2:** Thinking `process.nextTick` is the same as microtasks (Promises)
```javascript
// WRONG assumption: they're interchangeable
process.nextTick(() => console.log('A'));
Promise.resolve().then(() => console.log('B'));
// Output: 'A' always before 'B' — nextTick queue is checked and
// FULLY drained before the Promise microtask queue, every single time
```

---

## 🧠 Tricky Interview Question

```javascript
process.nextTick(() => {
  console.log('nextTick 1');
  process.nextTick(() => console.log('nextTick 2 (nested)'));
});
Promise.resolve().then(() => console.log('promise 1'));
console.log('sync');
```

**Answer:** Output: `sync`, `nextTick 1`, `nextTick 2 (nested)`, `promise 1`. Explanation: sync code runs first. Then Node drains the ENTIRE nextTick queue, including nested ones scheduled DURING draining — `nextTick 1` runs, and the nested `nextTick 2` it schedules gets added to the SAME queue being drained, so it also runs before moving on. ONLY after the nextTick queue is completely empty does the Promise microtask queue get processed (`promise 1`).

---

## ⚫ Interview Questions + Answers

**Q1: What is `process.nextTick()` and when does it execute?**
A1: It schedules a callback to run at the end of the current operation, before the event loop continues to any phase and even before Promise callbacks. It has the HIGHEST priority of any async scheduling mechanism in Node.js.

**Q2: Why does Node.js provide `process.nextTick()` when Promises already exist?**
A2: `process.nextTick` predates Promises in Node.js and is used internally by Node core (EventEmitter, streams, error handling) to guarantee consistent async behavior and to defer operations just enough to let synchronous setup code finish. It's lower-level and has higher scheduling priority than Promise microtasks, useful when you need the absolute earliest possible async execution point.

**Q3: What's the danger of recursive `process.nextTick()` calls?**
A3: Since Node fully drains the nextTick queue (including newly added items during draining) before moving to ANY event loop phase, infinite or long recursive nextTick chains will starve I/O entirely — your server accepts connections but never processes their callbacks, timers never fire, and the process appears "frozen" despite still running.

**Q4: Give a real use case for `process.nextTick()`.**
A4: Ensuring an EventEmitter-based API always emits events asynchronously, even for operations that could complete synchronously (e.g., in a constructor) — this gives calling code a reliable window to attach listeners before the event fires, avoiding the "sometimes sync, sometimes async" (Zalgo) bug class.

**Q5: What's the execution order of: sync code, `process.nextTick`, `Promise.then`, `setTimeout`, `setImmediate`?**
A5: sync code → `process.nextTick` (fully drained) → `Promise.then` (fully drained) → Timers phase (`setTimeout`) → Poll phase (I/O) → Check phase (`setImmediate`) → Close Callbacks. nextTick and Promise microtasks both run BETWEEN every phase transition, not just once at the start.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Forcing consistent async behavior for an API that might otherwise resolve synchronously
- Deferring an EventEmitter emit so listeners can be attached first
- Error handling patterns requiring the earliest possible async callback

❌ **Avoid when:**
- Doing repeated/looping work — use `setImmediate` instead (yields to I/O)
- You just need "run later" — a simple `setTimeout` or `Promise` is more appropriate and less risky

---

## 📊 Visual Diagram

```
process.nextTick PRIORITY:
──────────────────────────────────────────────────────

  Current synchronous operation finishes
         │
         ▼
  ┌─────────────────────────────────────┐
  │  nextTick QUEUE (drained COMPLETELY) │  ← HIGHEST priority
  │  (including any NEW nextTicks added  │
  │   during this draining!)             │
  └──────────────────┬────────────────────┘
                     ▼
  ┌─────────────────────────────────────┐
  │  PROMISE MICROTASK QUEUE (drained)   │  ← runs AFTER nextTick
  └──────────────────┬────────────────────┘
                     ▼
         Event Loop phases (Timers, Poll, Check...)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `process.nextTick()` | Highest-priority async scheduler | सबसे high-priority async scheduler |
| nextTick Queue | Queue drained before any phase | कोई phase से पहले drain होने वाली queue |
| Zalgo problem | Inconsistent sync/async callback timing | Inconsistent sync/async callback timing |
| Starvation | I/O never runs due to recursive nextTick | Recursive nextTick से I/O कभी नहीं चलना |

---

## ⚡ 3-Line Summary
English:
1. `process.nextTick()` schedules a callback to run at the end of the current operation, with the HIGHEST priority — before Promises and before any event loop phase.
2. The nextTick queue is drained completely (including newly added items) before Node moves on — recursive use can starve I/O entirely.
3. Common use: forcing consistent async behavior for APIs/EventEmitters that could otherwise resolve synchronously.

Hindi:
1. `process.nextTick()` callback को current operation के end में सबसे highest priority से schedule करता है — Promises और किसी भी event loop phase से पहले।
2. nextTick queue पूरी तरह drain होती है (नए added items के साथ भी) आगे बढ़ने से पहले — recursive use I/O को starve कर सकता है।
3. Common use: APIs/EventEmitters के लिए consistent async behavior force करना।

---

## ➡️ Next Topic
**75. Microtasks — Promise callbacks** — How Promise `.then()` callbacks are scheduled, and their priority relative to process.nextTick।
