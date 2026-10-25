# 198. async/await in Node.js
# हिंदी में: Node.js में async/await

---

## 🔵 Simple Definition (English)
**`async`/`await`** is syntactic sugar built on top of Promises that lets you write asynchronous code that LOOKS and READS like synchronous code. Marking a function `async` makes it always return a Promise; `await` pauses execution inside that function until the awaited Promise settles, without blocking the rest of the application (the Event Loop is free to do other work).

## 🔵 सरल परिभाषा (Hindi)
**`async`/`await`** Promises के ऊपर बना syntactic sugar है जो async code को synchronous code जैसा दिखने/पढ़ने देता है। Function को `async` mark करने से वो हमेशा Promise return करता है; `await` उस function के अंदर execution को pause करता है जब तक awaited Promise settle न हो जाए — बाकी application block नहीं होती (Event Loop free रहता है)।

---

## 🔴 Problem it Solves
```
PROBLEM WITH PURE PROMISES:
  .then() chains are flatter than callback hell, but still visually
  different from normal synchronous code — harder to use try/catch,
  harder to use normal if/else/for loops across async steps

ASYNC/AWAIT SOLUTION:
  Write async code that LOOKS synchronous:
    const user = await getUser(id);
    const orders = await getOrders(user.id);
  Use normal try/catch for error handling across MULTIPLE awaited steps
  Use normal control flow (if, for, while) naturally with awaited values
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: .then() chains callback hell से बेहतर हैं पर फिर भी normal code जैसे नहीं दिखते
async/await solution: async code synchronous जैसा दिखता है
await से normal try/catch, if/for/while control flow use कर सकते हैं
```

---

## 🟢 How it Works — Step by Step

Step 1 → Mark a function `async` — it now ALWAYS returns a Promise (even if you `return` a plain value, it gets auto-wrapped)
Step 2 → Inside an `async` function, `await somePromise` pauses that function's execution until the promise settles
Step 3 → If the awaited promise resolves, `await` returns the resolved value; if it rejects, `await` THROWS the rejection reason — catchable with normal `try/catch`
Step 4 → While one `async` function is paused at an `await`, the Event Loop is NOT blocked — other code (other requests, timers) continues running normally
Step 5 → Multiple independent `await`s should be run together with `Promise.all` to avoid accidentally serializing work that could run in parallel

## 🟢 कैसे काम करता है? (Hindi)
```
1. Function को async mark करो — हमेशा Promise return करता है
2. await promise को function का execution pause करता है जब तक settle न हो
3. Resolve हो तो value मिलती है, reject हो तो throw होता है — try/catch से catch होता है
4. await के दौरान Event Loop block नहीं होता, बाकी काम चलता रहता है
5. Independent awaits को Promise.all से parallel चलाओ, serialize मत करो
```

---

## 🟡 Real World Example
**Amazon checkout flow with async/await:** `async function checkout(cart) { const validated = await validateCart(cart); const priced = await applyPricing(validated); const payment = await chargeCard(priced); return createOrder(payment); }` — this reads top-to-bottom exactly like a synchronous function, but each `await` yields control back to the Event Loop so thousands of OTHER checkout requests can be processed concurrently on the same single thread. A single `try/catch` wraps the whole thing, so any failure at any step is caught in ONE place — unlike the nested callback version.

## 🟡 Real Example Hindi mein
**Amazon checkout:** हर step `await` से sequential दिखता है, पर Event Loop block नहीं होता — हजारों दूसरे checkouts parallel चल सकते हैं। एक `try/catch` पूरे flow को wrap करता है, कहीं भी fail हो तो एक जगह catch हो जाता है।

---

## 💻 Code Example — Basic

```javascript
// basic-async-await.js
// Run: node basic-async-await.js

function delay(ms, value) {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

// Marking a function 'async' lets you use 'await' inside it
async function main() {
  console.log('1: Start');

  // 'await' pauses here until the promise resolves — reads like sync code
  const result1 = await delay(1000, 'first value');
  console.log('2: Got:', result1);

  const result2 = await delay(500, 'second value');
  console.log('3: Got:', result2);

  console.log('4: Done');
  return 'final result';  // an async function ALWAYS returns a Promise wrapping this
}

main().then((finalValue) => {
  console.log('5: main() resolved with:', finalValue);
});

console.log('6: This logs BEFORE anything inside main() finishes (non-blocking)');

// OUTPUT ORDER: 1, 6, 2 (after 1s), 3 (after another 0.5s), 4, 5
```

## 💻 Code Example — Advanced

```javascript
// advanced-async-await.js
// Realistic order flow with try/catch error handling AND parallel awaits where appropriate

function validateCart(cart) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (cart.items.length === 0) return reject(new Error('Cart is empty'));
      resolve(cart);
    }, 50);
  });
}
function fetchShippingOptions() {
  return new Promise((resolve) => setTimeout(() => resolve(['standard', 'express']), 50));
}
function fetchCouponDiscount(code) {
  return new Promise((resolve) => setTimeout(() => resolve(code === 'SAVE10' ? 0.1 : 0), 50));
}
function chargePayment(cart, discount) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const total = cart.items.reduce((s, i) => s + i.price * i.qty, 0) * (1 - discount);
      if (total <= 0) return reject(new Error('Invalid total'));
      resolve({ ...cart, charged: total });
    }, 50);
  });
}

async function placeOrder(cart) {
  try {
    // Step 1: sequential — inventory check depends on validated cart
    const validatedCart = await validateCart(cart);

    // Step 2: these two are INDEPENDENT — run them in parallel with Promise.all,
    // NOT sequentially (that would waste time doubling the wait)
    const [shippingOptions, discount] = await Promise.all([
      fetchShippingOptions(),
      fetchCouponDiscount(validatedCart.couponCode),
    ]);
    console.log('Shipping options:', shippingOptions);

    // Step 3: depends on discount from step 2 — must be sequential
    const finalOrder = await chargePayment(validatedCart, discount);

    return finalOrder;
  } catch (err) {
    // ONE try/catch handles errors from ANY await above — no duplicated error checks!
    console.error('Order failed:', err.message);
    throw err;  // re-throw so caller knows it failed too
  }
}

(async () => {
  try {
    const order = await placeOrder({
      items: [{ name: 'Phone', price: 20000, qty: 1 }],
      couponCode: 'SAVE10',
    });
    console.log('Order placed:', order);
  } catch (err) {
    console.error('Top-level handler: order placement failed');
  }
})();  // IIFE (Immediately Invoked Function Expression) to run async code at top level
```

---

## 🟠 Express.js Integration

```javascript
// Express route handlers as async functions — the standard modern pattern
const express = require('express');
const app = express();
app.use(express.json());

function findUserById(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id === '0') return reject(new Error('Invalid ID'));
      resolve({ id, name: 'Aditya' });
    }, 50);
  });
}

// IMPORTANT: Express does NOT automatically catch rejected promises from async
// handlers in older Express versions — you must try/catch yourself (or use a wrapper)
app.get('/api/users/:id', async (req, res) => {
  try {
    const user = await findUserById(req.params.id);
    res.json(user);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// A reusable wrapper to avoid repeating try/catch in every single route (common pattern)
function asyncHandler(fn) {
  return (req, res, next) => fn(req, res, next).catch(next);  // forwards errors to Express error middleware
}

app.get('/api/users/:id/safe', asyncHandler(async (req, res) => {
  const user = await findUserById(req.params.id);
  res.json(user);
}));

// Central error-handling middleware catches anything forwarded via next(err)
app.use((err, req, res, next) => {
  res.status(400).json({ error: err.message });
});

app.listen(3000, () => console.log('Server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `try/catch` around `await` in Express route handlers — an unhandled rejection can crash the process or hang the request (depending on Express version/config).
✅ Correct: Always wrap `await` calls in `try/catch`, or use a wrapper utility (`asyncHandler`) that forwards errors to `next(err)`.

```javascript
// Wrong — unhandled rejection if findUserById throws
app.get('/api/users/:id', async (req, res) => {
  const user = await findUserById(req.params.id);
  res.json(user);
});

// Right
app.get('/api/users/:id', async (req, res) => {
  try {
    const user = await findUserById(req.params.id);
    res.json(user);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});
```

❌ Mistake 2: Awaiting independent operations sequentially instead of using `Promise.all`, needlessly doubling/tripling total wait time.
✅ Correct: `const [a, b] = await Promise.all([fnA(), fnB()])` when `a` and `b` don't depend on each other.

```javascript
// Wrong — waits for A, THEN starts B — total time = A + B
const a = await fnA();
const b = await fnB();

// Right — both start immediately, total time = max(A, B)
const [a, b] = await Promise.all([fnA(), fnB()]);
```

❌ Mistake 3: Using `await` inside a `.forEach()` loop, expecting it to wait between iterations — `forEach` doesn't await its callback's return value, so all iterations fire concurrently/unordered.
✅ Correct: Use a plain `for...of` loop for sequential awaits, or `Promise.all(array.map(...))` for parallel.

---

## 🧠 Tricky Interview Question

```javascript
async function getValue() {
  return 42;  // NOT explicitly a Promise
}

async function run() {
  const result = getValue();  // notice: missing 'await' here!
  console.log(result);
  const awaited = await getValue();
  console.log(awaited);
}

run();
```
What is logged?
Answer:
```
Promise { 42 }
42
```
**Explanation:** `getValue()` is an `async` function, so calling it ALWAYS returns a Promise, even though the function body just does `return 42` with no explicit Promise wrapping. Without `await`, `result` holds the Promise object itself (logged as `Promise { 42 }` in Node's console), not the unwrapped value. Only `await getValue()` unwraps it to the actual value `42`. This is a very common beginner mistake: forgetting that EVERY `async` function's return value is implicitly wrapped in a Promise, and you must `await` (or `.then()`) it to get the real value.

---

## ⚫ Interview Questions + Answers

Q1: What does marking a function `async` actually change about it?
A1: It guarantees the function ALWAYS returns a Promise — if you `return` a plain value, it's automatically wrapped in a resolved Promise; if you `throw`, the returned Promise is automatically rejected with that error. It also enables the use of the `await` keyword inside that function's body.

Q2: Does `await` block the entire Node.js process?
A2: No. `await` only pauses execution WITHIN the current async function — it yields control back to the Event Loop, which continues processing other callbacks, timers, and incoming requests on the same thread. Only the code inside that specific async function waits; everything else in the application keeps running concurrently.

Q3: How do you handle errors in async/await code?
A3: Wrap `await` calls in a standard `try/catch` block — if the awaited promise rejects, `await` throws that rejection as a catchable exception. This replaces having to check `err` after every single callback or chain multiple `.catch()`s — one `try/catch` can cover several sequential `await`s.

Q4: What's wrong with using `await` inside `Array.prototype.forEach`?
A4: `forEach`'s callback return value is ignored — it doesn't wait for promises returned inside it, so if you put `await` inside a `forEach` callback, each iteration fires its async work but `forEach` itself doesn't wait between iterations, and the overall `forEach` call completes before any of the awaited work finishes. Use `for...of` for true sequential awaiting, or `Promise.all(arr.map(async item => ...))` for parallel awaiting with a result array.

Q5: How would you run several async operations in parallel using async/await, and what if you need ALL results even if some fail?
A5: Use `const results = await Promise.all([p1, p2, p3])` when you need everything to succeed (it rejects as soon as any one fails). If you need results from all of them regardless of individual failures, use `const results = await Promise.allSettled([p1, p2, p3])`, which never rejects and gives you a `{status, value|reason}` object per promise.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing any modern async flow in Node.js — it's the default, preferred style over raw Promises/callbacks for readability
- Needing standard `try/catch` error handling across multiple async steps
- Needing normal control flow (loops, conditionals) mixed naturally with async operations

❌ Avoid when:
- You genuinely need fine-grained control over promise scheduling that raw `.then()` chaining expresses more naturally (rare)
- Working with VERY old Node.js versions without async/await support (pre-Node 7.6 — essentially a non-issue today)

---

## 📊 Visual Diagram
```
ASYNC/AWAIT UNDER THE HOOD
──────────────────────────────────────────
async function run() {
  console.log('A');
  await somePromise;   // function PAUSES here,
  console.log('B');    // control returns to Event Loop
}                       // 'B' resumes once somePromise settles

run();
console.log('C');

EXECUTION ORDER:
  A   (sync, runs immediately up to the first await)
  C   (caller continues — run() didn't block it)
  B   (resumes once the awaited promise settles, via microtask)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| async function | Function that always returns a Promise | हमेशा Promise return करने वाला function |
| await | Pauses function until promise settles | Promise settle होने तक function pause |
| try/catch | Error handling for awaited rejections | Awaited rejection के लिए error handling |
| IIFE | Immediately invoked function expression | तुरंत चलने वाला function expression |
| Sequential vs parallel await | Waiting one-by-one vs together | एक-एक करके vs साथ में wait करना |

---

## ⚡ 3-Line Summary
English:
1. `async`/`await` is sugar over Promises that lets async code read like synchronous code, with standard `try/catch` for errors.
2. `await` pauses only the current async function, not the whole Event Loop — other work continues concurrently.
3. Use `Promise.all` for independent parallel `await`s; sequential `await`s should only be used when steps truly depend on each other.

Hindi:
1. `async`/`await` Promises के ऊपर sugar है, async code synchronous जैसा दिखता है, normal try/catch से errors handle होते हैं।
2. `await` सिर्फ current async function को pause करता है, Event Loop नहीं रुकता।
3. Independent kaam ke liye `Promise.all` use करो, sequential await सिर्फ तब जब steps एक-दूसरे पर depend करें।

---

## ➡️ Next Topic
**199. Error Handling — try/catch** — Deep dive into robust error handling patterns across sync and async Node.js code.
