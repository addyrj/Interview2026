# 75. Microtasks — Promise callbacks
# हिंदी में: Microtasks — Promise Callbacks

---

## 🔵 Simple Definition (English)
**Promise callbacks** (`.then()`, `.catch()`, `.finally()`, and `await` continuations) are scheduled on the **microtask queue** — a standard JavaScript (V8 engine) concept, not Node-specific. This queue is drained completely after `process.nextTick`'s queue, but still BEFORE the event loop moves to any of its 6 phases (Timers, Poll, etc.).

## 🔵 सरल परिभाषा (Hindi)
**Promise callbacks** (`.then()`, `.catch()`, `.finally()`, और `await` के बाद का code) **microtask queue** में schedule होते हैं — ये JavaScript (V8 engine) का standard concept है, Node-specific नहीं। ये queue `process.nextTick` queue के बाद drain होती है, लेकिन event loop के किसी भी phase (Timers, Poll, etc.) में जाने से पहले।

---

## 🔴 Problem it Solves
```
NEED: Promises need a way to schedule their .then() callbacks that's
      MORE immediate than macrotasks (setTimeout, I/O) but still async
      (doesn't block the current synchronous call stack).

WITHOUT MICROTASKS:
  If Promise.then() callbacks were scheduled like setTimeout (macrotasks),
  simple async chains would be needlessly slow — waiting for an entire
  event loop phase cycle for EACH .then() in a chain.

WITH MICROTASK QUEUE:
  Promise().then().then().then() chains resolve as fast as possible —
  all microtasks drain BEFORE moving to the next macrotask (phase),
  giving async/await code near-synchronous responsiveness.
```

## 🔴 यह क्यों बना? (Hindi)
```
Promises को .then() callbacks schedule करने का तरीका चाहिए था जो
setTimeout जैसे macrotasks से ज्यादा तुरंत हो, पर फिर भी async रहे
Microtask queue से Promise chains जल्दी resolve होते हैं —
सारे microtasks पहले drain होते हैं, फिर अगला macrotask/phase
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → A Promise resolves/rejects, OR an `await` continuation is ready
Step 2 → Its .then()/.catch()/continuation callback is pushed to the
          MICROTASK QUEUE (managed by the V8 engine itself, not libuv)
Step 3 → Current synchronous call stack finishes executing
Step 4 → process.nextTick queue drains FIRST (Node-specific, higher priority)
Step 5 → THEN the microtask queue (Promises) drains COMPLETELY —
          if a .then() callback creates ANOTHER resolved promise,
          that ALSO runs before moving on (chains resolve fully)
Step 6 → ONLY once both queues are empty does the event loop proceed
          to its next phase (Timers, Poll, etc.)
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Promise resolve/reject होती है, या await continuation ready होता है
2. उसका callback MICROTASK QUEUE में जाता है (V8 engine manage करता है)
3. Current sync code खत्म होता है
4. पहले process.nextTick queue drain होती है
5. फिर microtask (Promise) queue पूरी तरह drain होती है
6. दोनों queue खाली होने पर ही event loop next phase में जाता है
```

---

## 🟡 Real World Example
**Amazon checkout flow:** A checkout API does `await validateCart()` then `await checkInventory()` then `await calculatePrice()` — each `await` is essentially a `.then()` continuation on the microtask queue. Because microtasks drain fully before any macrotask (like a pending `setTimeout` health-check ping), these three sequential awaited operations (if their underlying promises are already resolved/near-instant, e.g., from cache) execute back-to-back almost synchronously, giving users a snappy checkout experience without unnecessary event-loop-phase delays between each step.

## 🟡 Real Example Hindi mein
**Amazon checkout:** Checkout API `await validateCart()` → `await checkInventory()` → `await calculatePrice()` करता है। हर `await` microtask queue पर continuation है। Microtasks macrotasks (जैसे pending setTimeout) से पहले पूरी तरह drain होते हैं, तो ये steps जल्दी back-to-back चलते हैं बिना unnecessary delay के।

---

## 💻 Code Example — Basic

```javascript
// promise-microtask-basic.js
// Run: node promise-microtask-basic.js

console.log('1: sync start');

Promise.resolve().then(() => {
  console.log('3: promise.then');
});

setTimeout(() => {
  console.log('4: setTimeout (macrotask, runs AFTER all microtasks)');
}, 0);

console.log('2: sync end');

// OUTPUT:
// 1: sync start
// 2: sync end
// 3: promise.then
// 4: setTimeout
// Explanation: Promise microtask runs after sync code but BEFORE
// setTimeout, because the entire microtask queue drains before the
// event loop even considers moving to the Timers phase.

// async/await is just sugar over .then() — same microtask scheduling:
async function example() {
  console.log('A: inside async function, sync part');
  await null;  // yields to microtask queue here
  console.log('B: after await — this is a MICROTASK continuation');
}
example();
console.log('C: after calling example() (sync)');
// Output order: A, C, B — because the code after `await` only runs
// once the current synchronous execution finishes and the microtask runs
```

## 💻 Code Example — Advanced

```javascript
// promise-microtask-advanced.js — chained promises all drain before next phase

console.log('START');

Promise.resolve()
  .then(() => {
    console.log('chain step 1');
    return Promise.resolve();  // returning a promise chains ANOTHER microtask
  })
  .then(() => {
    console.log('chain step 2');
  })
  .then(() => {
    console.log('chain step 3');
  });

setImmediate(() => console.log('setImmediate (macrotask, Check phase)'));
setTimeout(() => console.log('setTimeout (macrotask, Timers phase)'), 0);

process.nextTick(() => console.log('nextTick (even higher priority than Promise)'));

console.log('END');

// OUTPUT:
// START
// END
// nextTick (even higher priority than Promise)
// chain step 1
// chain step 2
// chain step 3
// setImmediate (macrotask, Check phase)   <- order vs setTimeout varies
// setTimeout (macrotask, Timers phase)
//
// KEY INSIGHT: ALL THREE promise chain steps run before EITHER macrotask,
// because each .then() in the chain re-queues a new microtask, and the
// microtask queue must be FULLY empty before any macrotask phase runs.

// Real-world risk: an infinite promise chain can ALSO starve the event
// loop, just like recursive process.nextTick:
let count = 0;
function infiniteChain() {
  return Promise.resolve().then(() => {
    count++;
    if (count < 1000) return infiniteChain();  // keep re-queuing microtasks
  });
}
// infiniteChain(); // uncomment to see — 1000 is safe, but Infinity would freeze I/O
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// Promise chains in middleware/route handlers rely entirely on microtask
// scheduling — understanding this helps reason about perceived latency
app.get('/checkout', async (req, res) => {
  console.log('1: handler start');

  // Each await here is a microtask continuation — if validateCart and
  // checkInventory resolve from in-memory cache (already-resolved promises),
  // they run back-to-back almost instantly, with NO event-loop-phase delay
  const cart = await validateCart(req.body.cartId);
  const inStock = await checkInventory(cart);
  const price = await calculatePrice(cart);

  res.json({ cart, inStock, price });
});

function validateCart(id) { return Promise.resolve({ id, items: 3 }); }
function checkInventory(cart) { return Promise.resolve(true); }
function calculatePrice(cart) { return Promise.resolve(999); }

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Assuming `setTimeout(fn, 0)` runs before a `Promise.then()`
```javascript
// WRONG assumption
setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => console.log('promise'));
// Output: 'promise' ALWAYS before 'timeout' — microtasks always
// drain completely before the event loop even reaches the Timers phase
```

❌ **Mistake 2:** Long/infinite Promise chains starving the event loop
```javascript
// WRONG: recursive synchronous-resolution promise chain never lets I/O run
function badLoop() {
  return Promise.resolve().then(badLoop);  // infinite microtask recursion!
}
// badLoop(); // this would freeze the server — no HTTP requests ever processed

// CORRECT: break the chain with a macrotask periodically
function safeLoop(i = 0) {
  if (i >= 1_000_000) return;
  return Promise.resolve().then(() => {
    // do small chunk of work
    setImmediate(() => safeLoop(i + 1));  // yields to Check phase occasionally
  });
}
```

---

## 🧠 Tricky Interview Question

```javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
process.nextTick(() => console.log('4'));
Promise.resolve().then(() => console.log('5'));
console.log('6');
```

**Answer:** Output: `1`, `6`, `4`, `3`, `5`, `2`. Explanation: sync code (`1`, `6`) runs first. Then `process.nextTick` (`4`) — Node's own highest-priority queue, drained before the Promise microtask queue. Then the Promise microtask queue drains IN ORDER of scheduling (`3` then `5`) — both were already resolved, queued one after another. Finally, `setTimeout` (`2`) runs in the Timers phase, only after BOTH the nextTick and Promise microtask queues are completely empty.

---

## ⚫ Interview Questions + Answers

**Q1: What is the microtask queue, and is it a Node.js-specific concept?**
A1: No — it's a standard JavaScript engine (V8) concept used for scheduling Promise `.then()`/`.catch()`/`.finally()` callbacks and `await` continuations. It exists in browsers too. Node.js layers its own `process.nextTick` queue ON TOP, giving nextTick even higher priority than the standard microtask queue.

**Q2: What's the priority order between `process.nextTick` and Promise microtasks?**
A2: `process.nextTick` queue drains FIRST, completely, before the Promise microtask queue is even touched. This is Node-specific behavior — `process.nextTick` isn't part of the ECMAScript spec; it's a Node addition that predates widespread Promise use and was given top priority.

**Q3: Why do ALL microtasks run before the NEXT macrotask/phase, not just one?**
A3: Because the event loop's design drains the ENTIRE microtask queue (including newly queued microtasks added during draining) before considering moving to the next phase. This ensures Promise chains (`.then().then().then()`) resolve "atomically" relative to macrotasks — you never see a `setTimeout` callback interleave in the MIDDLE of a synchronously-resolving promise chain.

**Q4: Can an infinite Promise chain cause the same starvation problem as recursive `process.nextTick`?**
A4: Yes. If a `.then()` callback keeps returning an already-resolved Promise that re-queues itself, the microtask queue never empties, so the event loop never reaches any phase (Timers, Poll, I/O) — effectively freezing the server to all external I/O, similar to recursive `nextTick` starvation.

**Q5: How does `async`/`await` relate to the microtask queue?**
A5: `async`/`await` is syntactic sugar over Promises. Every `await` expression suspends the function and schedules its continuation as a microtask once the awaited value resolves. So reasoning about `await` timing is identical to reasoning about `.then()` timing — both go through the same microtask queue.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Writing async code with Promises/`async`/`await` — this IS the default mechanism, you don't "opt in" manually
- You need operations to resolve as fast as possible relative to timers/I/O

❌ **Avoid when:**
- Writing long recursive promise chains without any macrotask yield — breaks I/O responsiveness, same risk as recursive nextTick

---

## 📊 Visual Diagram

```
MICROTASK QUEUE vs process.nextTick vs MACROTASKS:
──────────────────────────────────────────────────────

  Sync code finishes
         │
         ▼
  ┌──────────────────────────┐
  │  process.nextTick QUEUE   │  ← Node-specific, HIGHEST priority
  │  (drained completely)     │
  └────────────┬───────────────┘
               ▼
  ┌──────────────────────────┐
  │  MICROTASK QUEUE           │  ← standard JS/V8 (Promise .then/.catch/.finally, await)
  │  (drained completely,       │
  │   including newly added)    │
  └────────────┬───────────────┘
               ▼
  ┌──────────────────────────┐
  │  EVENT LOOP PHASES          │  ← MACROTASKS
  │  Timers → Poll → Check ...  │
  └──────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Microtask Queue | V8 queue for Promise callbacks | Promise callbacks की V8 queue |
| Macrotask | Phase-based callback (setTimeout, I/O) | Phase-based callback |
| `.then()` | Promise resolution callback | Promise resolve होने का callback |
| `await` | Sugar over .then(), microtask continuation | .then() का sugar, microtask continuation |

---

## ⚡ 3-Line Summary
English:
1. Promise callbacks (`.then`, `.catch`, `await` continuations) run on the standard JS microtask queue, which drains completely before any event loop phase (macrotask) runs.
2. Priority order: sync code → `process.nextTick` → Promise microtasks → event loop phases (Timers, Poll, Check).
3. Long/infinite promise chains can starve I/O just like recursive nextTick — always leave room for macrotasks to run.

Hindi:
1. Promise callbacks (`.then`, `.catch`, `await`) standard JS microtask queue पर चलते हैं, जो किसी भी event loop phase (macrotask) से पहले पूरी तरह drain होती है।
2. Priority order: sync code → `process.nextTick` → Promise microtasks → event loop phases।
3. Long/infinite promise chains भी I/O को starve कर सकते हैं recursive nextTick जैसे — हमेशा macrotasks को चलने का मौका दो।

---

## ➡️ Next Topic
**76. process.nextTick vs setImmediate** — Direct comparison of these two commonly confused scheduling APIs।
