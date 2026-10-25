# 81. Promise Chaining
# हिंदी में: Promise Chaining — एक के बाद एक async काम जोड़ना

---

## 🔵 Simple Definition (English)
Promise chaining means calling `.then()` one after another, so each async step starts only after the previous step finishes. Every `.then()` returns a **new** Promise, so you can keep adding steps in a flat line instead of nesting them.

## 🔵 सरल परिभाषा (Hindi)
Promise chaining का मतलब है `.then()` को एक के बाद एक लगाना, ताकि हर async step तभी शुरू हो जब पिछला step पूरा हो जाए। हर `.then()` एक **नया** Promise लौटाता है, इसलिए steps को nesting की जगह सीधी लाइन में जोड़ा जा सकता है।

---

## 🔴 Problem it Solves
Before Promises, async steps were chained with nested callbacks. Each step depended on the previous result, so code grew to the right (the famous "pyramid of doom" or callback hell). Error handling had to be repeated at every level, and it was easy to forget one.

## 🔴 यह क्यों बना? (Hindi)
Promises से पहले हर async step का result अगले step को callback के अंदर पास किया जाता था। हर step का कोड दाईं तरफ बढ़ता जाता था (जिसे "pyramid of doom" या callback hell कहते हैं)। Error handling हर level पर दोहराना पड़ता था, और कोई एक level भूल जाना आसान था। Promise chaining ने इसे एक सपाट (flat) pipeline बना दिया।

---

## 🟢 How it Works — Step by Step

Step 1 → `promise.then(fn)` returns a NEW promise (not the same one)
Step 2 → Whatever `fn` returns becomes the value of that new promise
Step 3 → If `fn` returns a Promise, the chain WAITS for it, then continues with its value
Step 4 → If `fn` throws, the new promise is rejected and the next `.catch()` handles it
Step 5 → Errors skip `.then()` handlers until a `.catch()` (or `.then(_, onError)`) appears
Step 6 → `.finally()` runs in both cases and passes the result/error through unchanged

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `promise.then(fn)` एक NEW promise लौटाता है (वही पुराना नहीं)
Step 2 → `fn` जो return करता है, वही उस नए promise की value बन जाती है
Step 3 → अगर `fn` एक Promise return करे, तो chain उसका इंतज़ार करती है और फिर उसकी value के साथ आगे बढ़ती है
Step 4 → अगर `fn` throw करे, तो नया promise reject हो जाता है और अगला `.catch()` उसे संभालता है
Step 5 → Error `.then()` handlers को skip करती हुई तब तक जाती है जब तक कोई `.catch()` न मिल जाए
Step 6 → `.finally()` दोनों हालात में चलता है और result/error को जैसा है वैसा आगे भेजता है

---

## 🟡 Real World Example
Think about a Razorpay-style payment flow on a food app like Zomato or Swiggy. The steps depend on each other: first create an order on the server, then charge the customer, then verify the payment, then send the receipt. Each step needs the output of the one before it, so a promise chain is the natural fit.

```
createOrder(₹499)  →  charge card  →  verify signature  →  send receipt
   (network)          (network)         (network)           (email)
```

If the card charge fails, the chain jumps straight to the `.catch()` and the receipt is never sent. That is exactly what we want.

## 🟡 Real Example Hindi mein
मान लो Zomato या Swiggy पर आप ₹499 का खाना order करते हो। पहले server पर order बनता है, फिर payment charge होता है, फिर payment verify होता है, फिर receipt जाती है। हर step पिछले step के result पर निर्भर है, इसलिए promise chain सबसे सही तरीका है। अगर charge fail हो जाए, तो chain सीधे `.catch()` पर जाती है और receipt कभी नहीं भेजी जाती, जो हम चाहते भी हैं।

---

## 💻 Code Example — Basic
```javascript
// Fake async API calls: each one returns a Promise that resolves after a delay.
// Real world: these would be fetch() or database calls.

// Helper: returns a Promise that resolves with `value` after `ms` milliseconds
const delay = (ms, value) =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms)); // resolve after ms

// Step 1: create an order on the "server"
function createOrder(amount) {
  console.log(`Creating order for ₹${amount}`);       // log the step
  return delay(100, { orderId: "order_101", amount }); // return Promise<order>
}

// Step 2: charge the customer for that order
function makePayment(order) {
  console.log(`Paying for ${order.orderId}`);           // log the step
  return delay(100, { ...order, paymentId: "pay_xyz", status: "paid" }); // Promise<payment>
}

// Step 3: send the receipt
function sendReceipt(payment) {
  console.log(`Receipt sent for ${payment.paymentId}`); // log the step
  return delay(50, `Receipt for ₹${payment.amount} sent`); // Promise<string>
}

// The chain: each .then gets the value that the previous step resolved with
createOrder(499)                                  // start: Promise<order>
  .then((order) => makePayment(order))            // returned Promise is awaited automatically
  .then((payment) => sendReceipt(payment))        // gets the payment object
  .then((msg) => console.log("DONE:", msg))       // gets the receipt string
  .catch((err) => console.error("Failed:", err.message)); // any error in the chain lands here

// Simple value flow: each .then can transform the value
Promise.resolve(2)
  .then((x) => x * 10)     // 2 -> 20
  .then((x) => x + 1)      // 20 -> 21
  .then((x) => console.log("Transformed value:", x)); // prints 21
```

**Expected output (basic):** (the "Transformed value" chain has no timers, so it finishes first)
```
Creating order for ₹499
Transformed value: 21
Paying for order_101
Receipt sent for pay_xyz
DONE: Receipt for ₹499 sent
```

## 💻 Code Example — Advanced
```javascript
// Advanced: a reusable pipeline built with reduce, plus retry with exponential backoff.

// Helper: resolve with value after ms (used for waiting between retries)
const delay = (ms, value) =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

// Build one function that runs many steps in order as a single promise chain
function pipeline(...steps) {
  // reduce starts from Promise.resolve(input) and attaches each step with .then
  return (input) => steps.reduce((p, step) => p.then(step), Promise.resolve(input));
}

// Wrap an async function so it retries on failure with growing waits (50ms, 100ms, ...)
function withRetry(fn, retries = 3, baseMs = 50) {
  return (arg) => {
    // attempt(n) is itself a chain: run fn, and on failure chain a retry
    const attempt = (n) =>
      fn(arg).catch((err) => {          // fn rejected: handle it here
        if (n >= retries) throw err;    // no retries left: rethrow so the outer chain rejects
        const wait = baseMs * 2 ** n;   // exponential backoff: 50, 100, 200 ...
        console.log(`attempt ${n + 1} failed (${err.message}), retry in ${wait}ms`);
        return delay(wait).then(() => attempt(n + 1)); // chain the next attempt
      });
    return attempt(0);                  // start with attempt number 0
  };
}

// A flaky "payment gateway": fails the first two calls, succeeds on the third
let calls = 0;
function flakyGateway(amount) {
  calls++;                                                  // count every call
  if (calls < 3) return Promise.reject(new Error("gateway down")); // simulate failure
  return delay(10, { amount, ok: true });                   // success after 10ms
}

const payWithRetry = withRetry(flakyGateway, 3, 50);        // up to 3 retries

// Compose the full order flow as one pipeline
const processOrder = pipeline(
  (amount) => ({ amount, currency: "INR" }),                // step 1: build order object
  (order) => payWithRetry(order.amount),                    // step 2: pay with retry
  (result) => `paid ${result.amount}, ok=${result.ok}`      // step 3: format the result
);

processOrder(499)
  .then((summary) => console.log(summary))                  // print the final summary
  .catch((err) => console.error("Pipeline failed:", err.message)); // handle final failure
```

**Expected output (advanced):**
```
attempt 1 failed (gateway down), retry in 50ms
attempt 2 failed (gateway down), retry in 100ms
paid 499, ok=true
```

---

## 🟠 Express.js Integration
In an Express route handler, a promise chain is how you run several async calls in order (database, payment gateway, email). Always return the chain or use `.catch(next)` so errors reach Express's error middleware. Without this, a rejected promise becomes an unhandled rejection and the request hangs.

```javascript
// Express.js example: order route built as a promise chain
const express = require("express");        // import Express
const app = express();                     // create the app
app.use(express.json());                   // parse JSON request bodies

// Fake service functions (in a real app these talk to MongoDB, Razorpay, etc.)
const saveOrder = (body) => Promise.resolve({ id: "ord_1", ...body }); // save to DB
const charge = (order) => Promise.resolve({ ...order, paid: true });  // call gateway

app.post("/orders", (req, res, next) => {  // route handler receives req, res, next
  saveOrder(req.body)                      // step 1: save the order
    .then((order) => charge(order))        // step 2: charge (promise is awaited)
    .then((paid) => res.status(201).json(paid)) // step 3: send response
    .catch(next);                          // any error goes to Express error middleware
});

// Error middleware: Express calls this when next(err) is called
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message }); // send a clean error response
});

app.listen(3000);                          // start server on port 3000
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to `return` inside `.then()` (chain breaks, value becomes `undefined`)
✅ **Correct:** Always return the promise or value you want the next step to receive.

```javascript
// Wrong: the arrow function uses braces but does not return
fetchUser(1)
  .then((user) => { fetchOrders(user.id); })   // returns undefined, does not wait
  .then((orders) => console.log(orders));      // orders is undefined

// Right: return the promise so the chain waits for it
fetchUser(1)
  .then((user) => { return fetchOrders(user.id); }) // or: (user) => fetchOrders(user.id)
  .then((orders) => console.log(orders));           // orders is the real list
```

❌ **Mistake 2:** Nesting `.then()` calls inside `.then()` (brings back callback hell)
✅ **Correct:** Return the inner promise and chain it at the same level.

```javascript
// Wrong: nested, hard to read, error handling gets messy
getUser().then((user) => {
  getOrders(user.id).then((orders) => {
    console.log(orders);
  });
});

// Right: flat chain, one catch at the end
getUser()
  .then((user) => getOrders(user.id))
  .then((orders) => console.log(orders))
  .catch((err) => console.error(err));
```

❌ **Mistake 3:** Putting `.catch()` in the middle and assuming it covers later steps
✅ **Correct:** A `.catch()` only handles errors from steps BEFORE it. Later steps run normally.

```javascript
// Wrong mental model: the catch is not a safety net for the whole chain
Promise.reject(new Error("db down"))
  .catch((e) => console.log("caught:", e.message)) // prints "caught: db down"
  .then(() => console.log("next step")); // runs! catch recovered the chain

// Right: put one catch at the end if you want to stop on any error
Promise.reject(new Error("db down"))
  .then(() => console.log("next step")) // skipped because chain is rejected
  .catch((e) => console.log("caught:", e.message));
```

---

## 🧠 Tricky Interview Output Question
```javascript
console.log("start");

Promise.resolve(1)
  .then((x) => {
    console.log("A", x);       // step A runs first (after sync code)
    return x + 1;              // next value is 2
  })
  .then((x) => {
    throw new Error("boom " + x); // throws with message "boom 2"
  })
  .catch((e) => {
    console.log("B", e.message);  // catch receives the error
    return 10;                    // recovers: next value is 10
  })
  .then((x) => console.log("C", x))  // runs with 10
  .finally(() => console.log("D"));  // runs at the end, no value

console.log("end");
```
**Answer:**
```
start
end
A 1
B boom 2
C 10
D
```
**Why:** `console.log("start")` and `console.log("end")` are synchronous, so they print first. Promise callbacks are microtasks that run after the current script finishes, in chain order. The second `.then` throws, which rejects the chain. The `.catch` handles the error and returns `10`, which turns the chain back into a fulfilled state, so `C 10` prints. `.finally` runs last and receives no value.

---

## ⚫ Interview Questions + Answers

Q1: What does `.then()` return?
A1: A brand-new Promise. It is not the same promise it was called on. That new promise resolves with whatever the callback returns, or waits if the callback returns a promise.

Q2: What happens if a `.then()` callback throws an error?
A2: The promise returned by that `.then()` is rejected with the error. The next `.then()` with no error handler is skipped, and the chain continues until a `.catch()` or `.then(_, onError)` handles it.

Q3: Why do we return a promise inside `.then()` instead of calling it and ignoring it?
A3: If you return it, the chain waits for it and gets its resolved value, and errors in it are caught by the chain. If you don't return it, the next step runs immediately with `undefined`, and the error becomes an unhandled rejection.

Q4: What is the difference between `.then(a).catch(b)` and `.then(a, b)`?
A4: `.then(a, b)` handles a rejection only from the previous promise, not from `a` itself. `.then(a).catch(b)` also catches errors thrown inside `a`. Usually `.then(a).catch(b)` is what you want.

Q5: Does `.finally()` change the value passed down the chain?
A5: No. `.finally()` runs the callback with no arguments and passes the original value or error through. The only exception: if the `finally` callback itself throws or returns a rejected promise, that error replaces the original result.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Steps depend on each other (the output of step 1 is the input of step 2)
- You want one central place to handle errors for a sequence of async calls
- You are writing library code or code that must work without `async`/`await` support
- You need to transform values step by step (map-like pipelines)

❌ Avoid when:
- Steps are independent; run them in parallel with `Promise.all` instead of chaining
- The chain has many branches and conditions; `async`/`await` with `if` and `try` is easier to read
- You are adding `.then()` inside `.then()`; flatten it or return the inner promise

---

## 📊 Visual Diagram
```
createOrder()  ──resolve(order)──►  makePayment()  ──resolve(payment)──►  sendReceipt()
     │                                   │                                    │
     │ reject(err)                       │ reject(err)                        │ reject(err)
     ▼                                   ▼                                    ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │                          .catch(err => ...)                                  │
  └──────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
                                     .finally(() => ...)   (always runs)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `.then()` | Run a callback when a promise fulfills; returns a new promise | Promise पूरा होने पर callback चलाना |
| `.catch()` | Handle rejection from earlier steps | Earlier steps की error संभालना |
| `.finally()` | Run cleanup code in both success and error cases | दोनों हालात में चलने वाला code |
| Chaining | Attaching `.then` steps in a flat sequence | Steps को एक सीध में जोड़ना |
| Pass-through | A value flows unchanged through `.catch`/`.finally` | Value का बिना बदले आगे जाना |
| Callback hell | Deep nesting of callbacks | Callbacks का गहरा nesting |
| Microtask | A queued promise callback run after current code | Current code के बाद चलने वाला task |

---

## ⚡ 3-Line Summary
**English:**
1. Each `.then()` returns a new promise, so steps can be chained in a flat line.
2. Returned values pass to the next step; returned promises are awaited; thrown errors skip to the nearest `.catch()`.
3. Put one `.catch()` at the end, return inner promises, and use `.finally()` for cleanup.

**Hindi:**
1. हर `.then()` एक नया promise लौटाता है, इसलिए steps सीधी लाइन में जुड़ते हैं।
2. Return हुई value अगले step को जाती है; return हुआ promise await होता है; throw हुई error सबसे पास के `.catch()` पर जाती है।
3. एक `.catch()` आखिर में रखो, inner promise को return करो, और cleanup के लिए `.finally()` इस्तेमाल करो।

---

## ➡️ Next Topic
**82. Promise Methods (all, allSettled, race, any)** — Chaining handles steps in order. Next, learn how to run many promises together, and how each combinator (`all`, `allSettled`, `race`, `any`) behaves when some succeed or fail.
