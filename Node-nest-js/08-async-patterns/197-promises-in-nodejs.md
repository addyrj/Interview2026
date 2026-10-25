# 197. Promises in Node.js
# हिंदी में: Node.js में Promises

---

## 🔵 Simple Definition (English)
A **Promise** is an object representing the eventual result of an asynchronous operation — it is either **pending**, **fulfilled** (resolved with a value), or **rejected** (failed with a reason). Instead of passing a callback deep into a function, you get back a Promise immediately and chain `.then()`/`.catch()` onto it, flattening nested callback code into a linear chain.

## 🔵 सरल परिभाषा (Hindi)
**Promise** एक object है जो किसी async operation के eventual result को represent करता है — यह या तो **pending** होता है, **fulfilled** (value के साथ resolve) या **rejected** (reason के साथ fail)। Callback deep pass करने की जगह, आपको तुरंत एक Promise मिलता है जिसपर `.then()`/`.catch()` chain किया जाता है — nested callback code linear chain में flatten हो जाता है।

---

## 🔴 Problem it Solves
```
PROBLEM: Callback hell — deeply nested, duplicated error handling

PROMISE SOLUTION:
  Each async step returns a Promise instead of taking a callback
  Chain with .then() — stays flat, no rightward drift
  ONE .catch() at the end handles errors from ANY step in the chain
  Promise.all() / Promise.race() make parallel composition trivial
  Promises have 3 states: pending → fulfilled OR rejected (settle once, immutable after)
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: Callback hell — गहरा nesting, duplicate error handling
Promise solution: हर step callback लेने की जगह Promise return करता है
.then() से chain करो — flat रहता है
एक .catch() पूरी chain के किसी भी error को handle करता है
```

---

## 🟢 How it Works — Step by Step

Step 1 → A Promise is created with `new Promise((resolve, reject) => {...})` — the function runs immediately (synchronously) and calls `resolve(value)` on success or `reject(error)` on failure
Step 2 → Once settled (resolved/rejected), the Promise is IMMUTABLE — it can never change state again
Step 3 → `.then(onFulfilled, onRejected)` registers callbacks that run when the promise settles — `.then()` itself returns a NEW promise, enabling chaining
Step 4 → `.catch(onRejected)` is shorthand for `.then(null, onRejected)` — catches any rejection from earlier in the chain
Step 5 → `.finally(cb)` runs regardless of success/failure — good for cleanup

## 🟢 कैसे काम करता है? (Hindi)
```
1. new Promise((resolve, reject) => {...}) से Promise बनता है
2. Settle (resolve/reject) होने के बाद Promise immutable हो जाता है
3. .then() callbacks register करता है, खुद एक नया promise return करता है — chaining होती है
4. .catch() किसी भी पिछले rejection को catch करता है
5. .finally() हमेशा चलता है, चाहे success हो या failure
```

---

## 🟡 Real World Example
**Paytm wallet-to-bank transfer:** Transferring money needs: verify wallet balance → debit wallet → call bank API → credit bank account → log transaction. With Promises, each step is a function returning a Promise, chained with `.then()`. If debiting the wallet succeeds but the bank API call fails, a single `.catch()` at the end catches it and triggers a rollback (credit the wallet back) — much cleaner than duplicating `if (err)` at every nesting level like the callback version would require.

## 🟡 Real Example Hindi mein
**Paytm wallet-to-bank transfer:** balance verify → wallet debit → bank API call → bank credit → transaction log। Promises से हर step function है जो Promise return करता है, `.then()` से chain होता है। कोई step fail हो तो एक `.catch()` catch करके rollback कर सकता है।

---

## 💻 Code Example — Basic

```javascript
// basic-promise.js
// Run: node basic-promise.js

// A function that RETURNS a Promise instead of taking a callback
function delay(ms, value) {
  return new Promise((resolve, reject) => {
    if (ms < 0) {
      return reject(new Error('Delay must be positive'));  // failure path
    }
    setTimeout(() => resolve(value), ms);  // success path
  });
}

console.log('1: Start');

delay(1000, 'Hello from Promise')
  .then((result) => {
    console.log('2: Resolved with:', result);  // runs after 1 second
    return delay(500, 'Second step');            // chain another async step
  })
  .then((result) => {
    console.log('3: Second step resolved with:', result);
  })
  .catch((err) => {
    console.error('Error:', err.message);  // catches failure from ANY .then() above
  })
  .finally(() => {
    console.log('4: Done (runs regardless of success/failure)');
  });

console.log('5: This logs immediately (Promise work is async)');

// OUTPUT ORDER: 1, 5, 2 (after 1s), 3 (after another 0.5s), 4
```

## 💻 Code Example — Advanced

```javascript
// advanced-promise.js
// Realistic order-processing flow rewritten from callback-hell into a flat Promise chain,
// plus Promise.all for running independent steps in parallel.

function validateCart(cart) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (cart.items.length === 0) return reject(new Error('Cart is empty'));
      resolve(cart);
    }, 50);
  });
}

function checkInventory(cart) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const outOfStock = cart.items.find((i) => i.qty > 50);
      if (outOfStock) return reject(new Error(`${outOfStock.name} out of stock`));
      resolve(cart);
    }, 50);
  });
}

function fetchShippingOptions(cart) {
  // Independent of coupon lookup below — can run in PARALLEL with it
  return new Promise((resolve) => setTimeout(() => resolve(['standard', 'express']), 50));
}

function fetchCouponDiscount(cart) {
  return new Promise((resolve) => setTimeout(() => resolve(cart.couponCode === 'SAVE10' ? 0.1 : 0), 50));
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

// Flat chain — no pyramid! One .catch() handles errors from ANY step above it.
validateCart({ items: [{ name: 'Phone', price: 20000, qty: 1 }], couponCode: 'SAVE10' })
  .then((cart) => checkInventory(cart))
  .then((cart) => {
    // Run two INDEPENDENT async steps in parallel using Promise.all
    return Promise.all([fetchShippingOptions(cart), fetchCouponDiscount(cart)])
      .then(([shippingOptions, discount]) => ({ cart, shippingOptions, discount }));
  })
  .then(({ cart, shippingOptions, discount }) => {
    console.log('Shipping options:', shippingOptions);
    return chargePayment(cart, discount);
  })
  .then((finalOrder) => {
    console.log('Order placed:', finalOrder);
  })
  .catch((err) => {
    // Catches failure from validateCart, checkInventory, chargePayment, OR Promise.all
    console.error('Order failed:', err.message);
  });
```

---

## 🟠 Express.js Integration

```javascript
// Express route handler using Promises (without async/await, for contrast)
const express = require('express');
const app = express();

function findUserById(id) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id === '0') return reject(new Error('Invalid ID'));
      resolve({ id, name: 'Aditya' });
    }, 50);
  });
}

app.get('/api/users/:id', (req, res) => {
  findUserById(req.params.id)
    .then((user) => res.json(user))                           // success path
    .catch((err) => res.status(400).json({ error: err.message })); // single error path for the whole chain
});

app.listen(3000, () => console.log('Server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to `return` a promise inside a `.then()` — breaks chaining, the next `.then()` runs before the inner async work finishes.
✅ Correct: Always `return` the promise from inside a `.then()` callback when you want the chain to wait for it.

```javascript
// Wrong — chain doesn't wait for delay(), next .then() runs too early
promise.then((val) => {
  delay(1000, 'x');       // not returned!
}).then((result) => {
  console.log(result);     // logs undefined immediately, not 'x' after 1s
});

// Right
promise.then((val) => {
  return delay(1000, 'x'); // returned — chain waits for it
}).then((result) => {
  console.log(result);     // logs 'x' after 1s
});
```

❌ Mistake 2: Not adding a `.catch()` at all, letting rejected promises become silent "unhandled promise rejection" warnings (and, in future Node versions, process crashes).
✅ Correct: Always end a Promise chain with `.catch()`, or wrap in try/catch if using async/await.

❌ Mistake 3: Nesting `.then()` calls instead of chaining them flat (recreating callback hell inside Promises).
✅ Correct: Return the next promise and chain with another `.then()` at the SAME indentation level, not nested inside the previous one.

---

## 🧠 Tricky Interview Question

```javascript
console.log('1');

Promise.resolve('2').then((val) => console.log(val));

Promise.resolve('3').then((val) => {
  console.log(val);
  return Promise.resolve('4');
}).then((val) => console.log(val));

console.log('5');
```
What is the output order?
Answer:
```
1
5
2
3
4
```
**Explanation:** `1` and `5` are synchronous, run first. Both `Promise.resolve()` calls queue their `.then()` callbacks as microtasks. Microtasks run in the order they were QUEUED once the synchronous code finishes: the first `.then` (`'2'`) was queued before the second chain's first `.then` (`'3'`), so `2` logs before `3`. After logging `3`, a NEW promise (`Promise.resolve('4')`) is returned and chained — this adds a new microtask that resolves on the NEXT microtask cycle, so `4` logs last, after `2` and `3` have already been processed.

---

## ⚫ Interview Questions + Answers

Q1: What are the three states of a Promise?
A1: **Pending** (initial state, operation not yet complete), **Fulfilled** (operation succeeded, has a resolved value), **Rejected** (operation failed, has a rejection reason). Once a promise moves from pending to fulfilled or rejected, it's "settled" and can never change state again — this immutability is a core guarantee of the Promise spec.

Q2: What's the difference between `.then(a, b)` and `.then(a).catch(b)`?
A2: `.then(onFulfilled, onRejected)` attaches the rejection handler to the SAME promise that `onFulfilled` is attached to — so it only catches a rejection of the original promise, NOT an error thrown inside `onFulfilled` itself. `.then(a).catch(b)` attaches `.catch()` to the promise returned by `.then(a)`, so it catches both the original rejection AND any error thrown inside `a`. `.catch()` chaining is generally safer/preferred.

Q3: What happens if you throw an error inside a `.then()` callback?
A3: It's automatically converted into a rejected promise — the chain's next `.catch()` (or `.then(null, onRejected)`) will catch it, just like an explicit `reject()` call. This is one of Promise's biggest advantages over callbacks: thrown errors anywhere in the chain are automatically funneled to error handlers downstream.

Q4: How do `Promise.all`, `Promise.race`, `Promise.allSettled`, and `Promise.any` differ?
A4: `Promise.all` resolves when ALL promises resolve (rejects immediately if ANY rejects). `Promise.race` settles as soon as the FIRST promise settles (resolve or reject). `Promise.allSettled` waits for ALL promises to settle regardless of outcome, returning an array of `{status, value/reason}` objects — never rejects itself. `Promise.any` resolves as soon as ANY promise resolves (rejects only if ALL reject).

Q5: Is the function passed to `new Promise(...)` executed synchronously or asynchronously?
A5: **Synchronously** — the executor function runs immediately when `new Promise()` is called, before the constructor even returns. Only the `.then()`/`.catch()` callbacks are deferred to the microtask queue. This surprises people who assume everything inside a Promise is automatically async — it's not; you have to explicitly do async work (like `setTimeout` or I/O) inside the executor for it to actually be asynchronous.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chaining multiple dependent async steps that need clean, linear error handling
- Composing parallel async operations with `Promise.all`/`Promise.allSettled`
- Wrapping legacy callback-based APIs to make them composable (`util.promisify`)

❌ Avoid when:
- A single, simple async operation with no chaining — a plain callback may be simpler
- You're writing in an environment that doesn't support Promises (very old Node versions) — use a polyfill or callbacks

---

## 📊 Visual Diagram
```
PROMISE LIFECYCLE
──────────────────────────────────────────
        new Promise((resolve, reject) => {...})
                     │
                     ▼
                  PENDING
                 /        \
         resolve(val)   reject(err)
               │              │
               ▼              ▼
          FULFILLED       REJECTED
               │              │
          .then(fn)      .catch(fn)
               │              │
        returns NEW promise (enables chaining)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pending | Not yet settled | अभी settle नहीं हुआ |
| Fulfilled | Resolved successfully | Successfully resolve हुआ |
| Rejected | Failed with a reason | किसी reason से fail हुआ |
| Microtask | High-priority queue for promise callbacks | Promise callbacks की high-priority queue |
| Chaining | Linking .then() calls sequentially | .then() calls को sequentially जोड़ना |
| util.promisify | Converts callback API to Promise API | Callback API को Promise API में बदलना |

---

## ⚡ 3-Line Summary
English:
1. A Promise represents the eventual result of an async operation, settling once into fulfilled or rejected.
2. `.then()` chaining flattens nested callbacks, and a single `.catch()` handles errors from any step in the chain.
3. Always `return` promises inside `.then()` to preserve chaining, and never leave a chain without a `.catch()`.

Hindi:
1. Promise किसी async operation के eventual result को represent करता है — fulfilled या rejected में settle होता है।
2. `.then()` chaining nested callbacks को flatten करता है, एक `.catch()` पूरी chain के errors handle करता है।
3. `.then()` के अंदर promise हमेशा `return` करो, chain को बिना `.catch()` मत छोड़ो।

---

## ➡️ Next Topic
**198. async/await in Node.js** — Syntactic sugar over Promises that makes async code read like synchronous code.
