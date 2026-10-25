# 192. Promise Chaining Problems
# हिंदी में: Promise Chaining के Problems — Value Flow, Error Handling, Retry और Timeout

---

## 🔵 Simple Definition (English)
Promise chaining means calling `.then`, `.catch`, and `.finally` one after another, where each step receives the value returned by the step before it. Interview problems check whether you know how values flow through the chain, how an error skips to the next `catch`, and how to build retry and timeout helpers from plain promise chains.

## 🔵 सरल परिभाषा (Hindi)
Promise chaining का मतलब है `.then`, `.catch` और `.finally` को एक के बाद एक लगाना, जहाँ हर step को पिछले step का return किया हुआ value मिलता है। Interview के सवाल देखते हैं कि value chain में कैसे आगे जाती है, error बीच में कैसे अगले `catch` तक पहुँचता है, और सादी promise chains से retry और timeout helpers कैसे बनते हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Write a pipeline that loads a user, then loads that user's orders, then computes a total. If a step fails, the pipeline should recover or report the error. Add a retry for flaky calls and a timeout for slow calls, using only promise chains.

Before promises, this flow was written with nested callbacks (the "pyramid of doom"). Errors were checked at every level, and it was easy to forget one. Chaining keeps the steps flat, and one `catch` at the end can handle failures from any step above it.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** एक pipeline लिखो जो पहले user लोड करे, फिर उसके orders लोड करे, फिर total निकाले। अगर कोई step fail हो तो pipeline recover करे या error बताए। Flaky calls के लिए retry और धीमी calls के लिए timeout भी जोड़ो, सिर्फ promise chains से।

Promises से पहले यह flow nested callbacks में लिखा जाता था ("pyramid of doom")। हर level पर error चेक करना पड़ता था, और कोई एक check भूल जाना आसान था। Chaining steps को सीधा रखती है, और आख़िर में एक `catch` ऊपर के किसी भी step की error पकड़ सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `.then(fn)` runs `fn` with the resolved value and wraps its return value in a new promise.
Step 2 → If `fn` returns a promise, the chain waits for it and passes its resolved value on (flattening).
Step 3 → If `fn` throws, the next `.then` success handler is skipped, and the next `.catch` gets the error.
Step 4 → A `.catch` that returns a value recovers, and the chain continues with that value.
Step 5 → `.finally` runs in both cases and passes the original value or error through unchanged.
Step 6 → Forgetting `return` makes the next step receive `undefined`, and it may run before a promise you started.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `.then(fn)` `fn` को resolved value के साथ चलाता है और उसके return value को नए promise में लपेटता है।
Step 2 → अगर `fn` कोई promise return करे, तो chain उसका इंतज़ार करती है और उसका resolved value आगे भेजती है (flattening)।
Step 3 → अगर `fn` throw करे, तो अगला `.then` success handler छोड़ दिया जाता है, और अगला `.catch` error पाता है।
Step 4 → `.catch` जो value return करे वह recover करता है, और chain उसी value से आगे चलती है।
Step 5 → `.finally` दोनों हालात में चलता है और original value या error को बिना बदले आगे भेजता है।
Step 6 → `return` भूल जाने से अगला step `undefined` पाता है, और वह आपके शुरू किए promise से पहले भी चल सकता है।

---

## 🟡 Real World Example
Swiggy's order page loads the user profile, then the active orders, then computes the amount to show. If the orders service is slow, the page should give up after 2 seconds and show a message, not hang. A Razorpay webhook handler retries a failed ledger write 3 times before it logs the event for manual review.

Scenario: A Flipkart checkout calls `getCart`, then `reserveStock`, then `createOrder`. If `reserveStock` fails with a timeout, the chain catches it, releases the cart lock in `finally`, and shows "stock busy, try again". The user never sees a half-created order.

## 🟡 Real Example Hindi mein
Swiggy का order page पहले user profile लोड करता है, फिर active orders, फिर दिखाने वाली amount निकालता है। अगर orders service धीमी हो, तो page 2 सेकंड बाद हार मानकर message दिखाए, न कि अटका रहे। Razorpay का webhook handler ledger write fail होने पर 3 बार retry करता है, फिर event को manual review के लिए log करता है।

उदाहरण: Flipkart checkout `getCart`, फिर `reserveStock`, फिर `createOrder` call करता है। अगर `reserveStock` timeout से fail हो, तो chain उसे पकड़ती है, `finally` में cart lock हटाती है, और "stock busy, फिर से कोशिश करें" दिखाती है। User को आधा बना order कभी नहीं दिखता।

---

## 💻 Code Example — Basic
```javascript
// Chain 1: each .then receives the value returned by the previous step
Promise.resolve(2)                              // start with a resolved promise that holds 2
  .then((x) => x * 3)                           // 2 * 3 = 6; this return value goes to the next step
  .then((x) => x + 1)                           // 6 + 1 = 7
  .then((x) => console.log("result:", x));      // Expected output: result: 7

// Helper for the next examples: resolve with value after ms milliseconds
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));

// Chain 2: returning a promise from .then makes the chain wait for it (flattening)
delay(20, "user")                               // first step resolves with "user" after 20 ms
  .then((name) => delay(20, name.toUpperCase())) // return a promise: the chain waits for it
  .then((v) => console.log("flattened:", v));   // Expected output: flattened: USER

// Chain 3: forgetting return gives the next step undefined
Promise.resolve(5)
  .then((x) => { x * 2; })                      // braces but no return, so this returns undefined
  .then((y) => console.log("forgot return:", y)); // Expected output: forgot return: undefined

// Chain 4: an error skips the success steps and goes to the next catch
Promise.resolve("order-1")
  .then((id) => { throw new Error(`payment failed for ${id}`); }) // throwing jumps to the next rejection handler
  .then(() => console.log("skipped"))           // this success handler is never called
  .catch((e) => { console.log("caught:", e.message); return "fallback"; }) // recover with a value
  .then((v) => console.log("after catch:", v))  // runs normally with "fallback"
  .finally(() => console.log("finally runs"));  // always runs; does not change the value

// Chain 5: then(onOk, onErr) does NOT catch errors thrown inside onOk
Promise.resolve(1)
  .then(
    () => { throw new Error("bad in success handler"); }, // this error...
    () => console.log("never printed"),                   // ...is not handled by this second argument
  )
  .catch((e) => console.log("catch got:", e.message));     // Expected output: catch got: bad in success handler
```

## 💻 Code Example — Advanced
```javascript
// Helper: resolve with value after ms milliseconds
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));

// pipeAsync: run steps one after another; each step may return a plain value or a promise
const pipeAsync = (...steps) => (input) =>      // returns a function that takes the first input
  steps.reduce(
    (chain, step) => chain.then(step),          // attach the next step to the end of the chain
    Promise.resolve(input),                     // start with the input as a resolved promise
  );

// retry: call fn; if it rejects, try again until `times` attempts are used up
function retry(fn, times) {
  return fn().catch((err) => {                  // first attempt; a rejection lands in this catch
    if (times <= 1) throw err;                  // no attempts left: rethrow the last error
    console.log(`attempt failed (${err.message}), ${times - 1} left`); // log the failure
    return retry(fn, times - 1);                // return the new attempt so the chain waits for it
  });
}

// withTimeout: reject if promise does not settle within ms; always clear the timer afterwards
function withTimeout(promise, ms) {
  let timer;                                    // holds the timer id so we can clear it later
  const timeout = new Promise((_, reject) => {  // this promise rejects after ms milliseconds
    timer = setTimeout(() => reject(new Error(`timeout after ${ms}ms`)), ms);
  });
  return Promise.race([promise, timeout])       // whichever settles first wins
    .finally(() => clearTimeout(timer));        // remove the timer whether it won or lost
}

// Demo 1: pipeAsync: +1, then *2 (async), then -3 (after a 5 ms delay)
const calc = pipeAsync(
  (x) => x + 1,                                 // 4 + 1 = 5
  async (x) => x * 2,                           // 5 * 2 = 10 (async step)
  (x) => delay(5, x - 3),                       // 10 - 3 = 7, returned after 5 ms
);
calc(4).then((v) => console.log("pipe:", v));  // Expected output: pipe: 7 (printed after the 5 ms delay)

// Demo 2: retry: the first two calls fail, the third succeeds
let attempts = 0;                               // counts how many times flaky() was called
const flaky = () => {
  attempts++;                                   // count this call
  return attempts < 3
    ? Promise.reject(new Error(`boom ${attempts}`)) // fail on attempts 1 and 2
    : Promise.resolve("connected");             // succeed on attempt 3
};
retry(flaky, 3).then((v) => console.log("retry:", v, "attempts:", attempts)); // retry: connected attempts: 3

// Demo 3: withTimeout: a fast task wins, a slow task loses
withTimeout(delay(5, "fast"), 50)               // 5 ms work with a 50 ms limit
  .then((v) => console.log("value:", v));       // Expected output: value: fast
withTimeout(delay(50, "slow"), 10)              // 50 ms work with a 10 ms limit
  .catch((e) => console.log("error:", e.message)); // Expected output: error: timeout after 10ms

// Time:  O(k) for a pipeline of k steps; retry adds up to `times` attempts; withTimeout is O(1) extra
// Space: O(1) per chain step; the pending promise and the timer are released when the chain settles
```

### Edge Cases
```javascript
// Edge 1: a non-function argument to .then is ignored, so the value passes through
Promise.resolve(10)
  .then(5)                                      // 5 is not a function, so .then ignores it
  .then((x) => console.log("passed through:", x)); // Expected output: passed through: 10

// Edge 2: catch returns a value, so the chain recovers and continues
Promise.reject(new Error("down"))
  .catch(() => "cached")                        // recover with a default value
  .then((v) => console.log("recovered:", v));   // Expected output: recovered: cached

// Edge 3: finally does not change the value, but a throw inside finally replaces it
Promise.resolve("keep me")
  .finally(() => "ignored")                     // return value of finally is ignored
  .then((v) => console.log("value:", v));       // Expected output: value: keep me
```

---

## 🟠 Express.js Integration
A checkout route is a real promise chain: validate the cart, charge the card, send the receipt, then respond. One `.catch` at the end turns any failed step into an HTTP error, so no step can crash the server.

```javascript
// Express.js: POST /api/checkout runs validate -> charge -> receipt as one promise chain
const express = require("express");             // web framework (install with: npm i express)
const app = express();                          // create the Express app
app.use(express.json());                        // parse JSON request bodies into req.body

// Fake async steps; real code would call a cart service, a payment gateway, and an email service
const validateCart = async (cart) => {          // reject if the cart is unusable
  if (!cart.items || cart.items.length === 0) throw new Error("cart is empty");
  return cart;                                  // pass the cart to the next step
};
const chargeCard = async (cart) => ({ paymentId: "pay_123", amount: cart.total }); // pretend payment
const sendReceipt = async (payment) => ({ sent: true, paymentId: payment.paymentId }); // pretend email

app.post("/api/checkout", (req, res) => {       // a normal handler that returns the chain's result
  validateCart(req.body)                        // step 1: check the cart from the request body
    .then((cart) => chargeCard(cart))           // step 2: charge; returning the promise makes the chain wait
    .then((payment) => sendReceipt(payment))    // step 3: send the receipt with the payment data
    .then((receipt) => res.status(201).json(receipt)) // step 4: success, 201 Created
    .catch((err) => res.status(400).json({ error: err.message })); // any failed step lands here
});

app.listen(3000, () => console.log("Checkout API on 3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Using `{ }` in an arrow function without `return`
✅ Correct: with curly braces, you must write `return` yourself. Without it, the next step gets `undefined`.

```javascript
// Wrong: the braces block has no return, so the next step receives undefined
Promise.resolve(5)
  .then((x) => { x * 2; })                      // computes 10 and throws it away
  .then((y) => console.log("wrong:", y));       // Expected output: wrong: undefined

// Right: a short arrow returns the expression, or write return inside the braces
Promise.resolve(5)
  .then((x) => x * 2)                           // returns 10
  .then((y) => console.log("right:", y));       // Expected output: right: 10
```

❌ **Mistake 2:** Starting a promise inside `.then` without returning it
✅ Correct: if you do not return the inner promise, the chain does not wait for it. The next step runs too early.

```javascript
// Wrong: the inner promise is started but not returned
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));
Promise.resolve("u1")
  .then((id) => { delay(20, "profile").then((p) => console.log("profile loaded", p)); }) // no return
  .then(() => console.log("next step runs first"));  // Expected output: next step runs first, then profile loaded profile
```

```javascript
// Right: return the inner promise so the chain waits for it
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));
Promise.resolve("u1")
  .then((id) => delay(20, "profile").then((p) => console.log("profile loaded", p))) // returned
  .then(() => console.log("next step runs after loading")); // Expected output: profile loaded profile, then next step runs after loading
```

---

## 🧠 Tricky Interview Question
```javascript
Promise.resolve(1)
  .then((x) => { console.log("a", x); return x + 1; })   // logs a 1 and returns 2
  .then((x) => { console.log("b", x); })                  // logs b 2 and returns undefined
  .then((x) => { console.log("c", x); throw new Error("oops"); }) // logs c undefined, then throws
  .then(() => console.log("d"))                           // skipped because of the error above
  .catch((e) => { console.log("e", e.message); return 99; }) // logs e oops, recovers with 99
  .then((x) => console.log("f", x));                      // logs f 99
console.log("sync end");                                 // runs before any .then callback
```
Answer:
```
sync end
a 1
b 2
c undefined
e oops
f 99
```
`console.log("sync end")` runs first, because `.then` callbacks always run later, as microtasks. After that, the chain runs one step at a time. Step "b" gets `2`, but returns nothing, so step "c" gets `undefined`. The throw in "c" skips "d" and lands in the `catch`, which returns 99 and lets "f" run with that value.

---

## ⚫ Interview Questions + Answers

**Q1: What does a `.then` callback receive, and what does it return?**
A1: It receives the resolved value of the previous step. It returns a new promise, which resolves with whatever the callback returns, or with the resolved value if the callback returns a promise.

**Q2: Why does a `.catch` in the middle of a chain stop the error from reaching later steps?**
A2: A `.catch` returns a new promise. If it returns a normal value, that promise resolves, and the chain continues as a success. Errors only pass through when there is no handler for them.

**Q3: What is the difference between `.then(ok, err)` and `.then(ok).catch(err)`?**
A3: `.then(ok, err)` handles errors from the earlier promise only. An error thrown inside `ok` is not caught by `err`. `.then(ok).catch(err)` catches errors from both the earlier promise and `ok`.

**Q4: Does `.finally` change the value of the chain?**
A4: No. Its return value is ignored, and the original value or error passes through. If `finally` throws, however, that new error replaces the original.

**Q5: How do you write retry with promise chains?**
A5: Call the function, then attach a `.catch` that checks the remaining attempts. If attempts remain, `return retry(fn, times - 1)`, so the outer chain waits for the next attempt. Otherwise, rethrow the error.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A fixed sequence of async steps passes values from one to the next
- You want one `catch` at the end to handle errors from every step above it
- You need a small helper such as retry, timeout, or cleanup in `finally`

❌ Avoid when:
- Steps are independent; use `Promise.all` so they run in parallel (see topic 191)
- The flow has many branches and loops; `async/await` with `try/catch` reads better
- You forget `return` in nested code; it is easy to lose errors and ordering

---

## 📊 Visual Diagram
```
Promise.resolve(1)
   |  then(x => { log; return x + 1 })     -> value 2
   v
   |  then(x => { log; })                  -> value undefined
   v
   |  then(x => { log; throw })            -> REJECTED (oops)
   v
   |  then(() => log("d"))                 -> skipped (rejected passes through)
   v
   |  catch(e => { log; return 99 })       -> RESOLVED with 99 (recovered)
   v
   |  then(x => log("f", x))              -> prints f 99
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chaining | Attaching `.then`/`.catch` steps one after another | एक के बाद एक steps जोड़ना |
| Flattening | A returned promise is waited for, not wrapped twice | Returned promise का इंतज़ार होना |
| Recovery | A `.catch` returns a value and the chain continues | `catch` से chain का फिर से चलना |
| finally | Runs in both cases and passes the value through | दोनों हालात में चलने वाला हिस्सा |
| Retry | Attempt the call again after a failure | Fail होने पर फिर से कोशिश |
| Timeout | Reject if work takes longer than a limit | तय समय से ज़्यादा लगे तो reject |
| Pyramid of doom | Deeply nested callbacks | गहराई से nested callbacks |

---

## ⚡ 3-Line Summary
English:
1. Each `.then` gets the previous return value, and a returned promise is waited for.
2. An error skips success steps and lands in the next `.catch`; a returned value from `catch` recovers the chain.
3. Always `return` inside chains, and build retry and timeout with `.catch` and `Promise.race`.

Hindi:
1. हर `.then` को पिछला return value मिलता है, और return हुआ promise का इंतज़ार होता है।
2. Error success steps छोड़कर अगले `.catch` में जाती है; `catch` से लौटाया value chain को recover करता है।
3. Chain में हमेशा `return` लिखो, और retry व timeout `.catch` और `Promise.race` से बनाओ।

---

## ➡️ Next Topic
**193. Event Loop Output Questions** — now that you can predict how a promise chain runs, the next topic explains the order of microtasks, macrotasks, and timers that decides when each `.then` callback actually runs.
