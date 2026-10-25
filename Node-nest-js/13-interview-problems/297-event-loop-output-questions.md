# 297. Event Loop Output Questions
# हिंदी में: Event Loop Output Questions (Tricky)

---

## 🔵 Simple Definition (English)
These are "predict the console output order" questions mixing `setTimeout`, `setImmediate`, `process.nextTick`, Promises (microtasks), and synchronous code — testing whether you truly understand Node's Event Loop phases and the microtask/macrotask priority. They're a staple of senior Node.js interviews.

## 🔵 सरल परिभाषा (Hindi)
यह "console output का order predict करो" questions हैं जो `setTimeout`, `setImmediate`, `process.nextTick`, Promises (microtasks), और synchronous code को mix करते हैं — यह test करते हैं कि आप Node के Event Loop phases और microtask/macrotask priority सच में समझते हैं या नहीं। Senior Node.js interviews में यह common होते हैं।

---

## 🔴 Problem it Solves
Understanding execution order is critical for debugging real bugs: race conditions, callbacks firing in unexpected order, UI updates happening before data is ready, or resource cleanup running too early/late. These questions force you to internalize the actual phase-by-phase mechanics rather than a hand-wavy "async stuff happens later" mental model.

## 🔴 यह क्यों बना? (Hindi)
Execution order समझना real bugs debug करने के लिए critical है: race conditions, callbacks unexpected order में fire होना, data ready होने से पहले UI update होना, या resource cleanup बहुत जल्दी/देर से चलना। ये questions आपको actual phase-by-phase mechanics internalize करने पर मजबूर करते हैं, न कि hand-wavy "async चीज़ें बाद में होती हैं" वाली mental model पर।

---

## 🟢 How it Works — Step by Step

Step 1 → Run ALL synchronous code first (the main script, top to bottom) — this is the "call stack" phase.
Step 2 → After the current synchronous execution (and after each callback), drain the **microtask queue** completely: `process.nextTick` callbacks FIRST, then Promise `.then`/`.catch`/`.finally` callbacks — and if a microtask schedules another microtask, that gets drained too before moving on.
Step 3 → Then proceed through the Event Loop's **macrotask phases** in order: **Timers** (`setTimeout`/`setInterval` callbacks whose time has elapsed) → **Pending callbacks** → **Poll** (I/O callbacks) → **Check** (`setImmediate`) → **Close callbacks**.
Step 4 → After EACH macrotask callback (e.g., each individual `setTimeout` callback), the microtask queue is drained AGAIN before the next macrotask runs.
Step 5 → `setImmediate` vs `setTimeout(fn, 0)` ordering is NOT guaranteed outside an I/O cycle, but INSIDE an I/O callback, `setImmediate` always fires before `setTimeout`.
Step 6 → `process.nextTick` always runs before ANY Promise microtask in Node.js (this is Node-specific, not standard JS/browser behavior).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पहले सारा synchronous code चलता है (main script, top to bottom) — यह "call stack" phase है।
Step 2 → Current synchronous execution के बाद (और हर callback के बाद), **microtask queue** पूरी तरह drain होती है: पहले `process.nextTick` callbacks, फिर Promise `.then`/`.catch`/`.finally` callbacks — और अगर एक microtask दूसरी microtask schedule करे, वह भी आगे बढ़ने से पहले drain होती है।
Step 3 → फिर Event Loop के **macrotask phases** order में चलते हैं: **Timers** (`setTimeout`/`setInterval` जिनका time हो गया) → **Pending callbacks** → **Poll** (I/O callbacks) → **Check** (`setImmediate`) → **Close callbacks**।
Step 4 → हर macrotask callback के बाद (जैसे हर individual `setTimeout` callback), microtask queue फिर से drain होती है अगले macrotask से पहले।
Step 5 → `setImmediate` बनाम `setTimeout(fn, 0)` का order I/O cycle के बाहर guaranteed नहीं है, पर I/O callback के अंदर `setImmediate` हमेशा `setTimeout` से पहले चलता है।
Step 6 → `process.nextTick` हमेशा किसी भी Promise microtask से पहले चलता है Node.js में (यह Node-specific है, standard JS/browser behavior नहीं)।

---

## 🟡 Real World Example
**Razorpay's webhook handler** race: a developer wrote `res.status(200).json({received:true}); processPayment(event);` expecting the response to definitely flush before `processPayment` starts logging — but a `process.nextTick` inside response serialization combined with an unexpected microtask ordering caused a log line to print before the response actually left the socket, confusing on-call engineers during an incident review. Understanding exact Event Loop ordering would have predicted this instead of needing production debugging.

## 🟡 Real Example Hindi mein
**Razorpay का webhook handler** race: developer ने `res.status(200).json({received:true}); processPayment(event);` लिखा यह assume करके कि response definitely flush हो जाएगा `processPayment` के logging शुरू होने से पहले — लेकिन response serialization के अंदर एक `process.nextTick` और unexpected microtask ordering की वजह से log line response socket से निकलने से पहले print हो गई, incident review में on-call engineers confuse हो गए। Exact Event Loop ordering समझना इसे production debugging के बिना predict कर देता।

---

## 💻 Code Example — Basic

```javascript
// eventloop-q1.js — Classic ordering question. Run: node eventloop-q1.js
console.log('1: sync start');

setTimeout(() => console.log('2: setTimeout'), 0);

Promise.resolve().then(() => console.log('3: promise then'));

process.nextTick(() => console.log('4: nextTick'));

console.log('5: sync end');

// EXPECTED OUTPUT ORDER:
// 1: sync start
// 5: sync end
// 4: nextTick        <- nextTick queue drains FIRST, before promise microtasks
// 3: promise then    <- then promise/microtask queue
// 2: setTimeout       <- then macrotask (timers phase), AFTER all microtasks
```

## 💻 Code Example — Advanced

```javascript
// eventloop-q2.js — Nested microtasks + setImmediate + I/O phase ordering (more advanced).
// Run: node eventloop-q2.js
const fs = require('fs');

console.log('A: sync start');

setTimeout(() => console.log('B: timeout 0'), 0);

setImmediate(() => console.log('C: immediate'));

fs.readFile(__filename, () => {
  // Inside an I/O callback (poll phase) — order between timeout/immediate becomes DETERMINISTIC here
  console.log('D: fs.readFile callback (poll phase)');
  setTimeout(() => console.log('E: timeout inside I/O'), 0);
  setImmediate(() => console.log('F: immediate inside I/O')); // ALWAYS before E, inside I/O callbacks
});

Promise.resolve().then(() => {
  console.log('G: promise 1');
  // Nested microtask — queued microtask gets drained before moving to next macrotask phase
  Promise.resolve().then(() => console.log('H: nested promise'));
});

process.nextTick(() => console.log('I: nextTick'));

console.log('J: sync end');

// EXPECTED OUTPUT (typical, though B vs C order outside I/O is NOT strictly guaranteed by spec):
// A: sync start
// J: sync end
// I: nextTick
// G: promise 1
// H: nested promise
// B: timeout 0        (or C, order can vary here — NOT inside I/O yet)
// C: immediate         (or B)
// D: fs.readFile callback (poll phase)
// F: immediate inside I/O   <- GUARANTEED before E, because this runs inside an I/O callback
// E: timeout inside I/O
```

---

## 🟠 Express.js Integration

```javascript
// server.js — a REAL bug caused by misunderstanding Event Loop ordering in request handling
const express = require('express');
const app = express();

app.get('/order', (req, res) => {
  let orderStatus = 'pending';

  // BUG: developer assumed this runs "immediately after" but it's actually queued as a microtask
  Promise.resolve().then(() => {
    orderStatus = 'confirmed'; // this runs AFTER the synchronous code below, not before!
  });

  // This synchronous line runs BEFORE the .then() callback above, so it reads the OLD value
  console.log('Status at response time:', orderStatus); // prints "pending", NOT "confirmed"
  res.json({ status: orderStatus }); // sends "pending" — likely not what was intended

  // FIX: await the promise before using its result
  // app.get('/order', async (req, res) => {
  //   let orderStatus = 'pending';
  //   await Promise.resolve().then(() => { orderStatus = 'confirmed'; });
  //   res.json({ status: orderStatus }); // now correctly "confirmed"
  // });
});

app.listen(3000, () => console.log('Buggy-by-design demo server on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming `setTimeout(fn, 0)` runs "immediately" like synchronous code
✅ Correct: It ALWAYS runs after the current synchronous code AND after all queued microtasks (nextTick + Promises), no matter how small the delay

```javascript
// Wrong assumption
setTimeout(() => console.log('fires right away'), 0);
console.log('this actually prints FIRST'); // sync code always wins over any timer

// Right mental model: 0ms just means "as soon as possible in the Timers phase", not "now"
```

❌ Mistake 2: Thinking `setImmediate` always fires before `setTimeout(fn, 0)` (or vice versa) at the TOP LEVEL
✅ Correct: At the top level (main module, not inside I/O), the order between them is NOT guaranteed — it depends on process startup timing. It's only deterministic INSIDE an I/O callback.

```javascript
// Wrong — treating this as reliably ordered at top level
setTimeout(() => console.log('timeout'), 0);
setImmediate(() => console.log('immediate'));
// Order here can vary run to run!

// Right — if order matters, use I/O callback context or explicit chaining instead
fs.readFile(__filename, () => {
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate')); // guaranteed to print first, here
});
```

---

## 🧠 Tricky Interview Question

```javascript
// The ultimate combo question:
console.log('start');

setTimeout(() => console.log('timeout 1'), 0);

Promise.resolve()
  .then(() => {
    console.log('promise 1');
    process.nextTick(() => console.log('nextTick inside promise'));
  })
  .then(() => console.log('promise 2'));

process.nextTick(() => {
  console.log('nextTick 1');
  Promise.resolve().then(() => console.log('promise inside nextTick'));
});

console.log('end');
```
Answer: Output is: `start`, `end`, `nextTick 1`, `promise 1`, `promise inside nextTick`, `nextTick inside promise`, `promise 2`, `timeout 1`.
Walkthrough: (1) Sync code runs first: `start`, `end`. (2) Microtask queue drains — `nextTick 1` runs (nextTick queue has priority), which SCHEDULES a new promise `.then` (queued to microtask/promise queue, processed after current nextTick queue empties but this is added to the END of the promise queue). (3) Then the already-queued `promise 1` .then callback runs, printing `promise 1`, and schedules `nextTick inside promise` — crucially, Node checks the nextTick queue again before continuing the promise queue (nextTick ALWAYS jumps ahead of pending promise callbacks), so `promise inside nextTick` (queued in step 2) actually resolves after `promise 1`'s nextTick is processed. The key insight: **every time the nextTick queue is non-empty, it fully drains before the next promise microtask runs**, even mid-way through chained `.then()` calls. (4) Finally, after all microtasks settle, `timeout 1` runs in the Timers phase.

---

## ⚫ Interview Questions + Answers

Q1: What are the six phases of the Node.js Event Loop, in order?
A1: Timers → Pending callbacks (I/O error callbacks) → Idle/Prepare (internal) → Poll (I/O callbacks, waits here if nothing else to do) → Check (`setImmediate`) → Close callbacks (`socket.on('close')`). Microtasks (nextTick + Promises) drain between EVERY phase transition and after every individual callback.

Q2: Why does `process.nextTick` run before Promise callbacks in Node.js specifically?
A2: Node.js implements two separate microtask queues: the "nextTick queue" and the "Promise/microtask queue". By design, Node fully drains the nextTick queue before processing ANY promise microtask, at every checkpoint. This is Node-specific behavior (not part of the ECMAScript spec) — browsers only have the Promise microtask queue, no `process.nextTick` equivalent with this priority.

Q3: Can `process.nextTick` callbacks cause starvation of the Event Loop?
A3: Yes — if a `nextTick` callback recursively schedules another `nextTick`, it can create an infinite loop that NEVER lets the Event Loop proceed to I/O, timers, or anything else, effectively starving the whole application (this is a documented footgun; `setImmediate` recursion doesn't have this problem since it yields to the Poll phase each cycle).

Q4: In what phase does `setImmediate` run relative to I/O callbacks?
A4: `setImmediate` runs in the "Check" phase, which comes immediately after the "Poll" phase (where I/O callbacks like `fs.readFile` run) in the SAME loop iteration. This is why calling `setImmediate` inside an I/O callback deterministically fires before any `setTimeout(fn, 0)` scheduled in the same callback — the timer has to wait for the NEXT loop iteration's Timers phase, while `setImmediate` runs in the Check phase of the CURRENT iteration.

Q5: How would you debug a real production issue where callbacks seem to run "out of order"?
A5: Add `console.log` with precise labels at every scheduling point AND every execution point (not just execution), use `async_hooks` or `--trace-sync-io` for deeper tracing, and mentally simulate: synchronous code first, then nextTick queue fully, then Promise queue fully, then proceed through macrotask phases — draining micro-queues after every single macrotask callback.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging callback/promise ordering bugs in production
- Studying for senior Node.js interviews where Event Loop internals are commonly tested

❌ Avoid when:
- Over-relying on exact ordering between unrelated async operations in actual production code (write code that doesn't DEPEND on fragile ordering guarantees between setTimeout/setImmediate at the top level — use explicit chaining/await instead)

---

## 📊 Visual Diagram
```
 ┌─────────────────────────────────────────────────────────────┐
 │ 1. Run all synchronous code (call stack)                     │
 │ 2. Drain microtasks: nextTick queue FULLY, then Promise queue│
 │    (repeat until BOTH are empty)                              │
 └───────────────────────────┬────────────────────────────────┘
                              ▼
      ┌─── Timers ──▶ Pending CB ──▶ Poll (I/O) ──▶ Check ──▶ Close CB ───┐
      │   (setTimeout)              (fs, net)    (setImmediate)          │
      └──────────────────────────────┬───────────────────────────────────┘
                                      │ after EVERY callback here,
                                      ▼ microtask queues drain again
                              (back to step 2, repeat)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Microtask | nextTick/Promise callbacks, highest priority | nextTick/Promise callbacks, सबसे high priority |
| Macrotask | Timer/I/O/Immediate callbacks, run per phase | Timer/I/O/Immediate callbacks, हर phase में |
| Poll phase | Where I/O callbacks execute | जहाँ I/O callbacks चलते हैं |
| Check phase | Where setImmediate callbacks execute | जहाँ setImmediate callbacks चलते हैं |
| Starvation | Event loop blocked by endless microtasks | Endless microtasks से event loop block होना |

---

## ⚡ 3-Line Summary
English: Node always finishes synchronous code first, then fully drains nextTick, then fully drains Promise microtasks, then proceeds through Timers → Poll → Check macrotask phases — repeating the microtask drain after every single callback. `setImmediate` vs `setTimeout(0)` ordering is only guaranteed deterministic inside an I/O callback.
Hindi: Node हमेशा पहले synchronous code खत्म करता है, फिर nextTick पूरा drain करता है, फिर Promise microtasks पूरे drain करता है, फिर Timers → Poll → Check macrotask phases से गुज़रता है — हर single callback के बाद microtask drain repeat होता है। `setImmediate` बनाम `setTimeout(0)` का order सिर्फ I/O callback के अंदर guaranteed deterministic है।

---

## ➡️ Next Topic
**298. Async/Await Tricky Questions** — common gotchas with error handling, parallel vs sequential await, and loop pitfalls.
