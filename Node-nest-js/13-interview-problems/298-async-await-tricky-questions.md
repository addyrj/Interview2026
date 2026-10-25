# 298. Async/Await Tricky Questions
# हिंदी में: Async/Await Tricky Questions

---

## 🔵 Simple Definition (English)
These are interview questions probing subtle `async`/`await` behaviors: how errors propagate, sequential vs parallel execution pitfalls, `await` inside loops, and how `async` functions ALWAYS return a Promise even when they look synchronous. Misunderstanding these causes real production bugs — slow APIs (accidental sequential awaits) or silently swallowed errors.

## 🔵 सरल परिभाषा (Hindi)
यह interview questions हैं जो subtle `async`/`await` behaviors test करते हैं: errors कैसे propagate होते हैं, sequential बनाम parallel execution की गलतियाँ, loops के अंदर `await`, और कैसे `async` functions हमेशा Promise return करते हैं भले ही वे synchronous लगें। यह गलत समझना real production bugs लाता है — slow APIs (accidental sequential awaits) या silently swallowed errors।

---

## 🔴 Problem it Solves
Async/await syntax makes asynchronous code LOOK synchronous, which lulls developers into sequential-style thinking even when operations are actually independent and should run in parallel. These questions force a precise mental model: `await` only pauses the CURRENT async function, not the whole program, and every `async function` call returns a Promise immediately.

## 🔴 यह क्यों बना? (Hindi)
Async/await syntax asynchronous code को synchronous जैसा दिखाता है, जिससे developers sequential-style सोचने लगते हैं भले ही operations actually independent हों और parallel चलना चाहिए। ये questions एक precise mental model force करते हैं: `await` सिर्फ CURRENT async function को pause करता है, पूरे program को नहीं, और हर `async function` call तुरंत एक Promise return करती है।

---

## 🟢 How it Works — Step by Step

Step 1 → An `async function` always returns a Promise — even `async function f() { return 5; }` returns `Promise<5>`, not `5` directly.
Step 2 → `await expr` pauses execution of the current async function (not the whole thread) until `expr` (a Promise) settles, then resumes with the resolved value or throws the rejection as a regular exception.
Step 3 → Code AFTER the async function call (that didn't `await` it) continues running immediately — the caller doesn't block unless IT also awaits.
Step 4 → Sequential awaits (`await a(); await b();`) run one after another even if `a()` and `b()` don't depend on each other — wasting time. Use `Promise.all([a(), b()])` to run independent async operations in parallel.
Step 5 → `await` inside a `for` loop runs iterations sequentially (one at a time) — intentional when order/rate matters, a bug when it's just slow for no reason.
Step 6 → Errors thrown inside an `async` function become a REJECTED promise — you must `try/catch` around the `await`, or `.catch()` on the call, or they become unhandled rejections.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `async function` हमेशा Promise return करता है — even `async function f() { return 5; }` `Promise<5>` return करता है, सीधे `5` नहीं।
Step 2 → `await expr` current async function का execution pause करता है (पूरे thread का नहीं) जब तक `expr` (Promise) settle न हो, फिर resolved value के साथ resume होता है या rejection को regular exception की तरह throw करता है।
Step 3 → Async function call के बाद का code (जिसने await नहीं किया) तुरंत चलता रहता है — caller block नहीं होता जब तक वह खुद भी await न करे।
Step 4 → Sequential awaits (`await a(); await b();`) एक के बाद एक चलते हैं भले ही `a()` और `b()` एक दूसरे पर dependent न हों — समय बर्बाद होता है। Independent async operations parallel चलाने के लिए `Promise.all([a(), b()])` use करो।
Step 5 → `for` loop के अंदर `await` iterations को sequentially (एक-एक करके) चलाता है — जब order/rate matter करे तो intentional, बिना वजह slow करे तो bug।
Step 6 → `async` function के अंदर throw हुआ error एक REJECTED promise बन जाता है — `await` के around `try/catch` चाहिए, या call पर `.catch()`, वरना यह unhandled rejection बन जाता है।

---

## 🟡 Real World Example
**Flipkart's checkout API** had a performance bug: the handler did `await validateCoupon(); await checkInventory(); await calculateShippingCost();` sequentially — three independent API calls taking 200ms each, totaling 600ms, when they had zero dependency on each other. Rewriting as `await Promise.all([validateCoupon(), checkInventory(), calculateShippingCost()])` cut checkout latency to ~200ms (the slowest of the three) — a textbook async/await ordering fix with direct revenue impact (faster checkout = fewer abandoned carts).

## 🟡 Real Example Hindi mein
**Flipkart का checkout API** में एक performance bug था: handler ने `await validateCoupon(); await checkInventory(); await calculateShippingCost();` sequentially किया — तीन independent API calls, हर एक 200ms, total 600ms, जबकि एक दूसरे पर कोई dependency नहीं थी। `await Promise.all([validateCoupon(), checkInventory(), calculateShippingCost()])` में rewrite करने से checkout latency ~200ms (तीनों में सबसे slow वाला) हो गई — एक textbook async/await ordering fix जिसका direct revenue impact था (faster checkout = कम abandoned carts)।

---

## 💻 Code Example — Basic

```javascript
// async-basic.js — core async/await gotchas. Run: node async-basic.js

async function getUser() {
  return { id: 1, name: 'Rahul' }; // looks sync, but ACTUALLY returns a Promise
}

async function demo() {
  const userPromise = getUser();   // does NOT block — returns a Promise immediately
  console.log(userPromise);         // prints: Promise { pending } or { <resolved>: {...} } depending on timing

  const user = await userPromise;   // NOW we wait for it to resolve
  console.log('Resolved user:', user);
}

demo();
console.log('This line runs BEFORE "Resolved user" log — demo() does not block the caller!');

// --- Sequential vs parallel timing demo ---
function delay(ms, label) {
  return new Promise(resolve => setTimeout(() => resolve(label), ms));
}

async function sequential() {
  const start = Date.now();
  const a = await delay(100, 'A'); // waits 100ms
  const b = await delay(100, 'B'); // THEN waits another 100ms -> total ~200ms
  console.log(`Sequential: ${a}, ${b}, took ${Date.now() - start}ms`);
}

async function parallel() {
  const start = Date.now();
  const [a, b] = await Promise.all([delay(100, 'A'), delay(100, 'B')]); // both start together -> total ~100ms
  console.log(`Parallel: ${a}, ${b}, took ${Date.now() - start}ms`);
}

sequential().then(() => parallel());
```

## 💻 Code Example — Advanced

```javascript
// async-advanced.js — error handling, loop pitfalls, and unhandled rejection traps.
// Run: node async-advanced.js

// --- Pitfall 1: await inside forEach does NOT work as expected ---
async function brokenLoop(items) {
  // forEach doesn't await the callback's promise — all calls fire "in parallel" with NO waiting,
  // and the function returns before any of them finish!
  items.forEach(async (item) => {
    await delay(50);
    console.log('forEach processed:', item); // prints out of order, AFTER brokenLoop() already returned
  });
  console.log('brokenLoop finished (but items likely not processed yet!)');
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

// --- Fix: use a real for...of loop, which DOES respect await ---
async function correctSequentialLoop(items) {
  for (const item of items) {
    await delay(50);
    console.log('for...of processed:', item); // guaranteed in order, guaranteed before function resolves
  }
  console.log('correctSequentialLoop truly finished');
}

// --- Fix for PARALLEL processing with controlled concurrency ---
async function correctParallelLoop(items) {
  await Promise.all(items.map(async (item) => {
    await delay(50);
    console.log('parallel processed:', item); // order NOT guaranteed, but all finish before Promise.all resolves
  }));
  console.log('correctParallelLoop truly finished');
}

// --- Pitfall 2: error handling with Promise.all — ONE rejection rejects ALL ---
async function demoPromiseAllFailure() {
  const results = [
    Promise.resolve('ok1'),
    Promise.reject(new Error('task2 failed')),
    Promise.resolve('ok3'),
  ];
  try {
    await Promise.all(results); // rejects immediately on the FIRST rejection — ok3's result is lost/ignored
  } catch (err) {
    console.log('Promise.all caught:', err.message);
  }

  // Fix: use Promise.allSettled to get ALL results regardless of individual failures
  const settled = await Promise.allSettled(results);
  settled.forEach((r, i) => {
    console.log(`Task ${i}:`, r.status === 'fulfilled' ? r.value : `FAILED: ${r.reason.message}`);
  });
}

// --- Pitfall 3: forgetting try/catch -> unhandled rejection crashes the process (Node 15+) ---
async function riskyOperation() {
  throw new Error('something broke');
}

async function safeCaller() {
  try {
    await riskyOperation();
  } catch (err) {
    console.log('Caught safely:', err.message); // without try/catch, this becomes an unhandled rejection
  }
}

(async () => {
  await brokenLoop(['x', 'y']);
  await correctSequentialLoop(['a', 'b']);
  await correctParallelLoop(['p', 'q']);
  await demoPromiseAllFailure();
  await safeCaller();
})();
```

---

## 🟠 Express.js Integration

```javascript
// server.js — real checkout endpoint demonstrating the parallel-vs-sequential fix
const express = require('express');
const app = express();

// Simulated independent service calls
const validateCoupon = () => new Promise(r => setTimeout(() => r({ valid: true }), 200));
const checkInventory = () => new Promise(r => setTimeout(() => r({ inStock: true }), 200));
const calculateShipping = () => new Promise(r => setTimeout(() => r({ cost: 40 }), 200));

// SLOW version — sequential awaits, ~600ms total
app.post('/checkout/slow', async (req, res) => {
  const coupon = await validateCoupon();
  const inventory = await checkInventory();
  const shipping = await calculateShipping();
  res.json({ coupon, inventory, shipping });
});

// FAST version — parallel via Promise.all, ~200ms total (bounded by the slowest call)
app.post('/checkout/fast', async (req, res) => {
  try {
    const [coupon, inventory, shipping] = await Promise.all([
      validateCoupon(),
      checkInventory(),
      calculateShipping(),
    ]);
    res.json({ coupon, inventory, shipping });
  } catch (err) {
    // If ANY of the three fails, we land here — decide whether partial success is acceptable
    res.status(500).json({ error: 'Checkout validation failed', details: err.message });
  }
});

app.listen(3000, () => console.log('Checkout demo on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `await` inside `.forEach()`, expecting it to wait for each iteration
✅ Correct: Use `for...of` for sequential awaiting, or `Promise.all(items.map(...))` for parallel awaiting

```javascript
// Wrong — forEach ignores the returned promises entirely, no waiting happens
items.forEach(async (item) => { await process(item); });

// Right — sequential
for (const item of items) { await process(item); }

// Right — parallel
await Promise.all(items.map(item => process(item)));
```

❌ Mistake 2: Not catching errors from an async function called without `await`
✅ Correct: Either `await` it inside a try/catch, or attach `.catch()` explicitly — never call-and-forget an async function that can reject

```javascript
// Wrong — fire-and-forget with no error handling = unhandled rejection crash risk
asyncOperationThatMightFail();

// Right
asyncOperationThatMightFail().catch(err => console.error('Background task failed:', err));
```

---

## 🧠 Tricky Interview Question

```javascript
async function foo() {
  console.log('1');
  await null; // even awaiting a non-promise value still yields to the microtask queue!
  console.log('2');
}

console.log('3');
foo();
console.log('4');

// What's the order?
```
Answer: Output is `3`, `1`, `4`, `2`. Walkthrough: `console.log('3')` runs synchronously. `foo()` is called — it runs synchronously UP TO the first `await`, printing `1`. The moment it hits `await null`, even though `null` isn't a Promise, the `await` operator STILL defers the rest of the function to the microtask queue (JavaScript wraps any awaited value in `Promise.resolve()` internally) — so execution returns control to the caller immediately. `console.log('4')` then runs synchronously. Only after the current synchronous stack fully unwinds does the microtask queue drain, resuming `foo()` to print `2`. This proves: **everything after the first `await` in an async function is effectively deferred, even if you await a plain value, not just a real pending Promise.**

---

## ⚫ Interview Questions + Answers

Q1: Does `await` block the entire Node.js process/thread?
A1: No. `await` only pauses the execution of the CURRENT async function, yielding control back to the Event Loop. Other code (other requests, timers, I/O callbacks) continues to run normally while that function is "paused" waiting for its Promise to settle. This is the entire point of async/await — non-blocking concurrency with synchronous-looking syntax.

Q2: What happens if you `await` a value that's not a Promise, like `await 5`?
A2: JavaScript automatically wraps it as `Promise.resolve(5)` and resolves immediately — execution still yields to the microtask queue (as shown in the tricky question above) before continuing, meaning even a trivial `await` introduces an asynchronous boundary.

Q3: What's the difference between `Promise.all`, `Promise.allSettled`, `Promise.race`, and `Promise.any`?
A3: `Promise.all` resolves with all results IF all succeed, rejects immediately on the FIRST failure (losing other results). `Promise.allSettled` always resolves with an array of `{status, value|reason}` for every promise, regardless of failures. `Promise.race` settles as soon as the FIRST promise settles (resolve or reject). `Promise.any` resolves as soon as the FIRST promise FULFILLS, only rejecting if ALL reject.

Q4: How do you add a timeout to an `await`ed operation that might hang forever?
A4: Race it against a timeout promise: `await Promise.race([actualOperation(), new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))])`. Whichever settles first wins; if the timeout fires first, the actual operation's eventual settlement is simply ignored (though it keeps running in the background unless explicitly cancelled, e.g., via `AbortController`).

Q5: Why can an unhandled promise rejection crash a Node.js process (since Node 15)?
A5: Prior to Node 15, unhandled rejections only printed a deprecation warning. Since Node 15, by default, an unhandled rejection triggers the same behavior as an uncaught exception — terminating the process — because silently swallowing a failed async operation is considered dangerous (state may be inconsistent). This is why EVERY async operation that can fail must have a `.catch()` or be inside a `try/catch` with an `await`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing any asynchronous logic — async/await is the modern standard over raw `.then()` chains for readability

❌ Avoid when:
- You need truly parallel independent operations but reach for sequential `await` out of habit — always ask "do these depend on each other?" before awaiting one-by-one

---

## 📊 Visual Diagram
```
 async function foo() {
   console.log('A');     // runs SYNCHRONOUSLY when foo() is called
   await somePromise;     // <-- function PAUSES here, returns a pending Promise to caller
   console.log('B');     // deferred to microtask queue, runs AFTER somePromise settles
 }

 Caller:
   foo();                 // returns immediately after 'A' prints (Promise is pending)
   console.log('C');      // runs BEFORE 'B' — caller is NOT blocked by foo()'s internal await
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Async function | Function that always returns a Promise | वह function जो हमेशा Promise return करे |
| Await | Pauses async function until Promise settles | Promise settle होने तक async function pause करे |
| Sequential | One after another, waiting each time | एक के बाद एक, हर बार wait करते हुए |
| Parallel | Multiple operations started together | कई operations साथ में शुरू |
| Unhandled rejection | Uncaught Promise failure | बिना catch हुई Promise failure |

---

## ⚡ 3-Line Summary
English: `await` pauses only the current async function, not the whole program, and even awaiting a non-Promise value defers execution to the microtask queue. Use `Promise.all` for independent parallel operations and `for...of` (not `forEach`) for truly sequential awaited loops; always handle rejections explicitly.
Hindi: `await` सिर्फ current async function को pause करता है, पूरे program को नहीं, और non-Promise value await करने पर भी execution microtask queue में defer होता है। Independent parallel operations के लिए `Promise.all` use करो और truly sequential awaited loops के लिए `for...of` (`forEach` नहीं); rejections हमेशा explicitly handle करो।

---

## ➡️ Next Topic
**299. Stream + Buffer Questions** — backpressure, chunked data handling, and common streaming interview gotchas.
