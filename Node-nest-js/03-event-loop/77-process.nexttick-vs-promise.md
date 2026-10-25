# 77. process.nextTick vs Promise
# हिंदी में: process.nextTick vs Promise — तुलना

---

## 🔵 Simple Definition (English)
Both **`process.nextTick()`** and **Promise callbacks** (`.then()`/`await`) are async scheduling mechanisms that run BEFORE any event loop phase. But they're two SEPARATE queues: Node drains the entire `nextTick` queue FIRST, then drains the entire Promise microtask queue. `process.nextTick` is Node-specific; Promise microtasks are a standard JavaScript engine (V8) feature shared with browsers.

## 🔵 सरल परिभाषा (Hindi)
**`process.nextTick()`** और **Promise callbacks** (`.then()`/`await`) दोनों async scheduling mechanisms हैं जो किसी भी event loop phase से पहले चलते हैं। लेकिन ये दो अलग queues हैं: Node पहले पूरी `nextTick` queue drain करता है, फिर पूरी Promise microtask queue। `process.nextTick` Node-specific है; Promise microtasks standard JavaScript (V8) feature है जो browsers में भी होता है।

---

## 🔴 Problem it Solves
```
HISTORICAL CONTEXT:
  process.nextTick() existed in Node.js BEFORE native Promises were
  standardized in JavaScript (ES2015). Node used it internally for
  consistent async callback timing in its core APIs (streams, events,
  fs callbacks).

  When Promises arrived, Node had to decide how the TWO queues relate.
  Decision: nextTick keeps its historical HIGHER priority, for backward
  compatibility with existing Node core behavior that depended on it.

WHY THIS MATTERS TODAY:
  Mixing process.nextTick and Promises in the same codebase without
  understanding their relative priority causes subtle ordering bugs,
  especially in libraries that need precise execution guarantees
  (e.g., ensuring cleanup code runs before a Promise chain continues).
```

## 🔴 यह क्यों बना? (Hindi)
```
process.nextTick() Promises के standardize होने से पहले से मौजूद था
Node internally इसे consistent async timing के लिए use करता था
जब Promises आए, Node ने decide किया कि nextTick higher priority रखेगा
backward compatibility के लिए
इसलिए दोनों को साथ mix करते वक्त priority समझना जरूरी है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Current synchronous operation completes
Step 2 → Node checks: is the nextTick queue non-empty?
Step 3 → If yes → run ALL callbacks in nextTick queue (including any
          NEW ones added by currently-running nextTick callbacks)
Step 4 → Once nextTick queue is FULLY empty → check Promise microtask queue
Step 5 → Run ALL Promise microtask callbacks (including newly chained ones)
Step 6 → Once BOTH queues are empty → event loop proceeds to next phase
Step 7 → If a Promise .then() callback calls process.nextTick(), that
          nextTick callback runs IMMEDIATELY after, before any further
          Promise microtasks — nextTick always cuts back in line!
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Current sync operation खत्म होता है
2. nextTick queue खाली नहीं है? तो सब callbacks run (नए added भी)
3. nextTick queue पूरी तरह खाली होने पर Promise microtask queue check होती है
4. सब Promise callbacks run होते हैं (नई chained भी)
5. दोनों खाली होने पर event loop next phase में जाता है
6. Promise callback के अंदर nextTick() call हो तो वो फिर से पहले चलता है
```

---

## 🟡 Real World Example
**Razorpay SDK internals:** Their internal retry-logic wrapper uses `process.nextTick()` to guarantee that error-normalization code runs IMMEDIATELY after an API call fails, before ANY user-attached `.then()`/`.catch()` Promise handler sees the error — ensuring the error object always has a consistent `{ code, message, retryable }` shape regardless of how deep the user's promise chain is. Because nextTick cuts ahead of Promise microtasks, this normalization is guaranteed to complete first, every time, without race conditions.

## 🟡 Real Example Hindi mein
**Razorpay SDK:** Internal retry-logic wrapper `process.nextTick()` से error-normalization code तुरंत चलाता है, API call fail होने के बाद, user के `.then()`/`.catch()` handlers से पहले — error object का shape हमेशा consistent रहता है `{ code, message, retryable }`। nextTick Promise microtasks से आगे cut करता है, इसलिए normalization हमेशा पहले complete होता है।

---

## 💻 Code Example — Basic

```javascript
// nexttick-vs-promise-basic.js
// Run: node nexttick-vs-promise-basic.js

console.log('1: sync start');

Promise.resolve().then(() => console.log('3: Promise.then'));
process.nextTick(() => console.log('2: process.nextTick'));

console.log('1b: sync end');

// OUTPUT:
// 1: sync start
// 1b: sync end
// 2: process.nextTick    <- nextTick queue drains FIRST
// 3: Promise.then        <- THEN Promise microtask queue
// Even though Promise.resolve().then() was scheduled FIRST in the code,
// process.nextTick still wins because Node checks its queue first, period.
```

## 💻 Code Example — Advanced

```javascript
// nexttick-vs-promise-advanced.js — demonstrating "nextTick cuts back in line"

console.log('START');

Promise.resolve().then(() => {
  console.log('promise 1');
  // Scheduling nextTick INSIDE a promise callback —
  // it still runs before the NEXT promise microtask!
  process.nextTick(() => console.log('nextTick scheduled inside promise 1'));
}).then(() => {
  console.log('promise 2');
});

Promise.resolve().then(() => {
  console.log('promise 3 (separate chain)');
});

// OUTPUT:
// START
// promise 1
// nextTick scheduled inside promise 1   <- cuts ahead!
// promise 3 (separate chain)
// promise 2
//
// WHY: After 'promise 1' runs, Node checks: is the nextTick queue
// non-empty? YES (just added) — so it drains that FIRST, before
// continuing to ANY further Promise microtasks (promise 2 or promise 3).
// This proves nextTick has priority even mid-Promise-chain execution.

// ─── Practical use: guaranteed error normalization before user code ─────────
function callApi() {
  return new Promise((resolve, reject) => {
    process.nextTick(() => {
      // Simulate normalizing an error before the promise settles
      reject(Object.assign(new Error('Payment failed'), { code: 'PAY_001', retryable: true }));
    });
  });
}

callApi().catch((err) => {
  console.log(`Normalized error — code: ${err.code}, retryable: ${err.retryable}`);
});
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// Middleware using nextTick to guarantee request-scoped setup completes
// before ANY promise-based route logic (even already-resolved promises) runs
app.use((req, res, next) => {
  req.startTime = null;
  process.nextTick(() => {
    req.startTime = Date.now();  // guaranteed to be set before next()
    next();
  });
});

app.get('/orders', async (req, res) => {
  // req.startTime is guaranteed to already be set, thanks to nextTick
  // priority over whatever microtasks might be pending from other code
  const orders = await Promise.resolve([{ id: 1 }, { id: 2 }]);
  const duration = Date.now() - req.startTime;
  res.json({ orders, tookMs: duration });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Assuming code order determines execution order between the two
```javascript
// WRONG assumption: "Promise was written first, so it runs first"
Promise.resolve().then(() => console.log('promise'));
process.nextTick(() => console.log('nextTick'));
// Output: 'nextTick' FIRST, regardless of code order — nextTick's
// queue is ALWAYS checked before the Promise microtask queue
```

❌ **Mistake 2:** Overusing `process.nextTick` where a simple Promise would suffice
```javascript
// WRONG: unnecessary use of a lower-level, higher-risk API
function getValue(cb) {
  process.nextTick(() => cb(null, 42));
}

// CORRECT (modern style): just use Promises/async-await — simpler,
// composable with .catch(), works with await, less footgun potential
function getValueAsync() {
  return Promise.resolve(42);
}
// Reserve process.nextTick for cases where you specifically need to
// beat Promise microtasks or interoperate with legacy callback APIs.
```

---

## 🧠 Tricky Interview Question

```javascript
async function main() {
  console.log('A');
  await null;
  console.log('B');
}

main();
process.nextTick(() => console.log('C'));
console.log('D');
```

**Answer:** Output: `A`, `D`, `C`, `B`. Explanation: `main()` runs synchronously until `await null` — so `A` logs immediately. `await null` suspends the function, scheduling its continuation (`console.log('B')`) as a PROMISE MICROTASK. Then `process.nextTick(...)` is registered. Then `console.log('D')` runs synchronously. Now the sync code is done: Node checks nextTick queue first → `C` logs. THEN the Promise microtask queue (from the `await`) runs → `B` logs. nextTick beats the await-continuation because nextTick's queue is always checked first.

---

## ⚫ Interview Questions + Answers

**Q1: Which runs first if both are scheduled: `process.nextTick` or `Promise.then`?**
A1: `process.nextTick` always runs first. Node fully drains the `nextTick` queue before even looking at the Promise microtask queue — this is true every single time, regardless of the order they were scheduled in code.

**Q2: Is `process.nextTick` part of the Promise/microtask spec?**
A2: No. `process.nextTick` is a Node.js-specific API, implemented as its own separate queue outside the ECMAScript microtask spec. Promise `.then()`/`await` continuations use the standard JS engine (V8) microtask queue, which is shared with browser environments. Node just happens to check its OWN nextTick queue with even higher priority.

**Q3: If a Promise `.then()` callback calls `process.nextTick()`, when does that nextTick callback run relative to OTHER pending Promise microtasks?**
A3: It runs IMMEDIATELY — before any further Promise microtasks continue. Because after each operation, Node always re-checks the nextTick queue first. So a nextTick scheduled from inside a `.then()` "cuts back in line" ahead of sibling/subsequent Promise callbacks.

**Q4: Why might overusing `process.nextTick` be considered bad practice in modern code?**
A4: It's a lower-level, Node-specific primitive originally designed for Node core's internal consistency needs. Promises/`async-await` are the standard, more composable, more readable, and cross-platform-consistent way to handle async flow today. Using `nextTick` everywhere instead of Promises reintroduces callback-style code and the associated readability/error-handling downsides, without real benefit for typical application logic.

**Q5: Give a scenario where you'd deliberately choose `process.nextTick` over a Promise.**
A5: When writing a library/SDK that needs to guarantee a callback runs with absolute priority — e.g., normalizing/attaching metadata to an object before ANY user-code Promise handler can observe it (as in the Razorpay SDK example), or ensuring EventEmitter listener setup completes before an event fires. These are edge cases requiring precise "beats everything else" timing, not typical application-level async logic.

---

## 🔷 When to Use + When Not to Use
✅ **Use `process.nextTick` when:**
- Writing low-level library/SDK code needing absolute priority execution over Promises
- Maintaining consistency with legacy Node core-style APIs

✅ **Use Promises/async-await when:**
- Writing regular application logic — the standard, readable, composable choice

❌ **Avoid:**
- Mixing both without understanding their priority relationship — leads to confusing bugs

---

## 📊 Visual Diagram

```
process.nextTick vs Promise — QUEUE PRIORITY:
──────────────────────────────────────────────────────

  Sync code / current operation completes
         │
         ▼
  ┌───────────────────────────────┐
  │  process.nextTick QUEUE         │  ← Node-specific
  │  (drain completely — ALWAYS      │     ALWAYS checked FIRST
  │   checked again after EVERY      │
  │   single operation, even mid-    │
  │   Promise-chain!)                │
  └───────────────┬───────────────────┘
                  ▼
  ┌───────────────────────────────┐
  │  PROMISE MICROTASK QUEUE         │  ← Standard JS/V8
  │  (.then/.catch/.finally/await)   │     Checked only AFTER
  │  (drain completely)              │     nextTick queue is empty
  └───────────────┬───────────────────┘
                  ▼
         Event Loop Phases (Timers, Poll, Check...)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `process.nextTick` | Node-specific, highest-priority queue | Node-specific, highest priority queue |
| Promise Microtask | Standard JS queue for .then/await | .then/await की standard JS queue |
| Queue Priority | Order in which queues are drained | Queues drain होने का order |
| Cuts in line | nextTick scheduled mid-Promise-chain runs first | Promise chain के बीच scheduled nextTick पहले चलता है |

---

## ⚡ 3-Line Summary
English:
1. `process.nextTick` and Promise callbacks are two SEPARATE queues — nextTick always drains completely first, before any Promise microtask runs.
2. This holds true even mid-execution: a `nextTick()` scheduled inside a `.then()` callback "cuts in line" ahead of sibling Promise microtasks.
3. Use Promises/async-await for normal app logic; reserve `process.nextTick` for library-level code needing absolute pre-Promise execution guarantees.

Hindi:
1. `process.nextTick` और Promise callbacks दो अलग queues हैं — nextTick हमेशा पहले पूरी तरह drain होती है, किसी भी Promise microtask से पहले।
2. ये mid-execution में भी true है: `.then()` के अंदर scheduled `nextTick()` sibling Promise microtasks से आगे चलता है।
3. Normal app logic के लिए Promises/async-await use करो; `process.nextTick` सिर्फ library-level, absolute priority वाले cases के लिए रखो।

---

## ➡️ Next Topic
**78. setTimeout vs setImmediate** — Comparing these two phase-based (macrotask) scheduling APIs directly।
