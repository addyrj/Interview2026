# 195. Callbacks in Node.js
# हिंदी में: Node.js में Callbacks

---

## 🔵 Simple Definition (English)
A **callback** is simply a function passed as an argument to another function, to be called ("called back") once that function finishes its work — especially async work like reading a file or querying a database. It's the original, most fundamental way Node.js handles asynchronous operations, built directly into core modules like `fs` and `http`.

## 🔵 सरल परिभाषा (Hindi)
**Callback** एक function है जो किसी दूसरे function को argument के रूप में pass किया जाता है, ताकि वो काम पूरा होने पर उसे "call back" कर सके — especially async काम जैसे file read करना या database query करना। यह Node.js का सबसे fundamental तरीका है async operations handle करने का, `fs`, `http` जैसे core modules में built-in है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  JavaScript is single-threaded — if reading a 1GB file took 3 seconds
  and blocked the thread, EVERYTHING else (other requests, UI) would freeze

CALLBACK SOLUTION:
  "Start this operation, and here's a function to call WHEN you're done"
  fs.readFile('big.txt', (err, data) => { /* runs later, async */ })
  The main thread doesn't wait — it moves on, Event Loop calls the
  callback when the I/O operation completes
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: JavaScript single-threaded है — अगर बड़ी file read करने में
3 seconds लगें और thread block हो जाए, तो सब कुछ freeze हो जाएगा

Callback solution: "यह काम शुरू करो, पूरा होने पर इस function को call करना"
Main thread wait नहीं करता, Event Loop काम पूरा होने पर callback call करता है
```

---

## 🟢 How it Works — Step by Step

Step 1 → You call an async function and pass it a callback function as an argument
Step 2 → The async function (e.g., `fs.readFile`) starts the I/O operation and immediately returns — execution continues to the next line
Step 3 → The actual I/O work happens in the background (libuv thread pool for file I/O)
Step 4 → When the I/O completes, Node.js queues your callback to run on the Event Loop
Step 5 → Your callback executes with the result — by Node.js convention, the FIRST argument is always `error` (null if no error), the rest are the result data ("error-first callback" pattern)

## 🟢 कैसे काम करता है? (Hindi)
```
1. Async function को callback function pass करो
2. Async function I/O operation शुरू करके immediately return करता है
3. Actual काम background में होता है (libuv thread pool)
4. काम पूरा होने पर Node.js callback को Event Loop पर queue करता है
5. callback(err, data) pattern — पहला argument हमेशा error होता है (error-first callback)
```

---

## 🟡 Real World Example
**Flipkart order confirmation flow (pre-Promise era, still common in legacy code):** When an order is placed, the server needs to: (1) save the order to the database, (2) THEN deduct inventory, (3) THEN send a confirmation email. Each step depends on the previous one completing, and each is an async I/O operation. Using callbacks, each step is written as `doStepX(data, (err, result) => { if (err) return handleError(err); doStepXPlusOne(result, nextCallback); })` — this works, but as more steps are added, this is exactly how "callback hell" is born (next topic).

## 🟡 Real Example Hindi mein
**Flipkart order confirmation:** Order place होने पर: (1) DB में save, (2) inventory deduct, (3) confirmation email भेजना — हर step पिछले वाले पर depend करता है। Callbacks से हर step `doStepX(data, (err, result) => {...})` pattern में लिखा जाता है — यही आगे चलकर "callback hell" बनता है।

---

## 💻 Code Example — Basic

```javascript
// basic-callback.js
// Run: node basic-callback.js
const fs = require('fs');

console.log('1: Starting file read...');  // runs first (sync)

// fs.readFile is async — takes a callback as the LAST argument (Node.js convention)
fs.readFile(__filename, 'utf8', (err, data) => {
  // This callback runs LATER, once the file is fully read
  if (err) {
    // ERROR-FIRST CONVENTION: always check err first
    console.error('Error reading file:', err.message);
    return;
  }
  console.log('3: File read complete. Length:', data.length);
});

console.log('2: This runs BEFORE the callback (async, non-blocking)');

// OUTPUT ORDER:
// 1: Starting file read...
// 2: This runs BEFORE the callback (async, non-blocking)
// 3: File read complete. Length: <number>
```

## 💻 Code Example — Advanced

```javascript
// advanced-callback.js
// Simulates a real order-processing flow using error-first callbacks,
// chained sequentially (classic pre-Promise Node.js style).

function saveOrder(order, callback) {
  // Simulate async DB write with setTimeout
  setTimeout(() => {
    if (!order.itemId) {
      // Pass an Error as the first argument when something goes wrong
      return callback(new Error('Missing itemId'));
    }
    callback(null, { ...order, orderId: 'ord_' + Date.now() });  // success: err=null
  }, 100);
}

function deductInventory(order, callback) {
  setTimeout(() => {
    if (order.quantity > 100) {
      return callback(new Error('Insufficient inventory'));
    }
    callback(null, { ...order, inventoryDeducted: true });
  }, 100);
}

function sendConfirmationEmail(order, callback) {
  setTimeout(() => {
    callback(null, { ...order, emailSent: true });
  }, 100);
}

// Chain each step — classic "callback" style orchestration
function processOrder(order, finalCallback) {
  saveOrder(order, (err, savedOrder) => {
    if (err) return finalCallback(err);  // propagate error immediately, stop chain

    deductInventory(savedOrder, (err, updatedOrder) => {
      if (err) return finalCallback(err);

      sendConfirmationEmail(updatedOrder, (err, finalOrder) => {
        if (err) return finalCallback(err);
        finalCallback(null, finalOrder);  // success — pass final result up
      });
    });
  });
}

// Usage
processOrder({ itemId: 'item_1', quantity: 5 }, (err, result) => {
  if (err) {
    console.error('Order failed:', err.message);
    return;
  }
  console.log('Order processed successfully:', result);
});
```

---

## 🟠 Express.js Integration

```javascript
// Express route handlers are themselves callbacks! (req, res) => {...} is a callback
// passed to app.get(). Here we also use a callback-style DB layer inside it.
const express = require('express');
const app = express();

// Simulated callback-style "DB" function (like old mongodb/mysql drivers)
function findUserById(id, callback) {
  setTimeout(() => {
    if (id === '0') return callback(new Error('Invalid ID'));
    callback(null, { id, name: 'Aditya' });
  }, 50);
}

app.get('/api/users/:id', (req, res) => {
  // The route handler itself is a callback Express calls on matching requests
  findUserById(req.params.id, (err, user) => {
    // This inner callback runs once the "DB" responds
    if (err) {
      return res.status(400).json({ error: err.message });
    }
    res.json(user);
  });
});

app.listen(3000, () => console.log('Server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to check `err` first (ignoring the error-first convention), causing crashes when `data` is actually `undefined`.
✅ Correct: Always check `if (err) { ... return; }` before touching the result.

```javascript
// Wrong — crashes if err is set because data will be undefined
fs.readFile('file.txt', (err, data) => {
  console.log(data.length);  // throws if err occurred
});

// Right
fs.readFile('file.txt', (err, data) => {
  if (err) return console.error(err);
  console.log(data.length);
});
```

❌ Mistake 2: Forgetting to `return` after handling an error inside a callback, letting execution fall through to the success-path code below it.
✅ Correct: Always `return callback(err)` or `return;` immediately after error handling.

❌ Mistake 3: Calling the callback more than once (e.g., once in a `setTimeout` and once synchronously by mistake) — leads to double execution of downstream logic (e.g., sending two emails, double-charging a payment).
✅ Correct: Guard with a flag, or structure the function so only one code path can ever call the callback.

---

## 🧠 Tricky Interview Question

```javascript
function getData(callback) {
  console.log('A');
  setTimeout(() => {
    console.log('B');
    callback();
  }, 0);
  console.log('C');
}

getData(() => console.log('D'));
console.log('E');
```
What is the output order?
Answer:
```
A
C
E
B
D
```
**Explanation:** `getData` runs synchronously up to `console.log('C')` — the `setTimeout` callback is deferred, not executed immediately, even with a 0ms delay (it still goes through the Timers phase of the Event Loop after the current synchronous code finishes). So: `A`, `C` run inside `getData` (sync), then control returns to the caller, which logs `E` (also sync, still before any timer fires). Only once the call stack is fully empty does the Event Loop process the timer, logging `B`, then finally invoking the passed callback, logging `D`.

---

## ⚫ Interview Questions + Answers

Q1: What is a callback function in Node.js?
A1: A function passed as an argument to another function, intended to be invoked after that function completes its work — commonly used to handle the result of an asynchronous operation (file I/O, network requests, timers) without blocking the main thread.

Q2: What is the "error-first callback" convention?
A2: A Node.js core convention where every callback's first parameter is reserved for an error object (`null` if there was no error), and subsequent parameters carry the actual result data: `callback(err, data)`. This lets every caller handle errors consistently with `if (err) { ... }` before using the data.

Q3: Are callbacks synchronous or asynchronous?
A3: Callbacks themselves can be either — it depends on how the function calling them is implemented. `Array.prototype.map`'s callback runs synchronously. `fs.readFile`'s callback runs asynchronously (after I/O completes, via the Event Loop). The term "callback" just describes the pattern (a function passed to be called later); synchronicity is a property of the specific API, not the pattern itself.

Q4: What problems arise from deeply nested callbacks?
A4: Deeply nested callbacks create "callback hell" — code that grows rightward with each dependent async step, becomes hard to read, hard to handle errors consistently across all branches, and hard to compose/reuse. This was the primary motivation for Promises and later `async`/`await`.

Q5: Can you call a callback multiple times? What happens if you do?
A5: Technically yes, nothing stops you in plain JS, but it's almost always a bug. If a callback represents "this operation finished," calling it twice usually means downstream logic (like sending a response, charging money, sending an email) runs twice. Well-designed async functions should guarantee their callback fires exactly once — guard with flags or use Promises, which natively guarantee a `.then()` handler runs at most once per settled promise.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Working with legacy Node.js core APIs or older libraries that only expose callback-style APIs
- Writing simple, single-step async operations where nesting isn't a concern
- You understand the error-first convention and want minimal abstraction overhead

❌ Avoid when:
- Chaining multiple dependent async steps — prefer Promises/`async`-`await` for readability and consistent error handling
- You need to run multiple async operations in parallel and combine results — `Promise.all` is far cleaner than manual callback counting

---

## 📊 Visual Diagram
```
CALLBACK FLOW
──────────────────────────────────────────
  main code
    │
    ├─ call asyncFn(data, callback)
    │        │
    │        ├─ starts I/O (non-blocking)
    │        └─ returns immediately
    │
    ├─ main code continues running...
    │
    │   [later, when I/O completes]
    │
    └──────▶ Event Loop invokes callback(err, result)
                   │
                   ├─ if (err) handle error
                   └─ else use result
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Callback | Function passed to be called later | बाद में call होने वाला function |
| Error-first convention | callback(err, data) pattern | callback(err, data) pattern |
| Non-blocking | Doesn't wait for I/O | I/O के लिए wait नहीं करता |
| Call stack | Tracks sync function calls | Sync function calls track करता है |
| Higher-order function | Function taking/returning functions | Function लेने/देने वाला function |

---

## ⚡ 3-Line Summary
English:
1. A callback is a function passed to another function to be invoked once its (often async) work completes.
2. Node.js core APIs follow the error-first convention: `callback(err, data)` — always check `err` first.
3. Callbacks are foundational but become unwieldy when chaining many dependent steps — leading to "callback hell."

Hindi:
1. Callback वो function है जो किसी function को pass किया जाता है, काम पूरा होने पर call होता है।
2. Node.js core APIs error-first convention follow करते हैं — पहले `err` check करो।
3. कई dependent steps chain करने पर callbacks unmanageable हो जाते हैं — "callback hell" बनता है।

---

## ➡️ Next Topic
**196. Callback Hell — Real Examples** — Seeing exactly how nested callbacks spiral out of control and why Promises were created.
