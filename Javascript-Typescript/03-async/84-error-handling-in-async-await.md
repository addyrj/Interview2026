# 84. Error Handling in async/await
# हिंदी में: async/await में Error Handling — try/catch, Error Wrapping और Unhandled Rejections

---

## 🔵 Simple Definition (English)
In `async`/`await` code, a rejected promise throws at the `await` line, so you handle it with `try/catch` just like a normal synchronous error. Errors you do not catch become rejections that bubble up and, if nobody handles them, become unhandled rejections.

## 🔵 सरल परिभाषा (Hindi)
`async`/`await` code में rejected promise, `await` वाली line पर throw होता है, इसलिए उसे normal sync error की तरह `try/catch` से संभालते हैं। जो error catch नहीं होती, वह rejection बनकर ऊपर जाती है, और अगर कोई उसे नहीं संभालता तो वह unhandled rejection बन जाती है।

---

## 🔴 Problem it Solves
With callbacks, errors were passed as the first argument (`err`) and people often forgot to check it, so bugs were silent. With promises, a missing `.catch` causes an unhandled rejection that can crash Node.js in newer versions. `async`/`await` lets us reuse the familiar `try/catch`, but it has traps: a `return` of a rejected promise inside `try` is not caught, and errors from `setTimeout` callbacks are not caught at all.

## 🔴 यह क्यों बना? (Hindi)
Callbacks में error पहले argument (`err`) में आती थी और लोग उसे check करना भूल जाते थे, इसलिए bugs चुपचाप रह जाते थे। Promises में `.catch` छूट जाए तो unhandled rejection आती है, और नए Node.js versions में यह process crash कर सकती है। `async`/`await` में पुराना `try/catch` इस्तेमाल होता है, पर इसके कुछ जाल हैं: `try` के अंदर बिना `await` के return हुआ rejected promise catch नहीं होता, और `setTimeout` callbacks की errors बिल्कुल catch नहीं होतीं।

---

## 🟢 How it Works — Step by Step

Step 1 → `await p` throws if `p` rejects, at the exact line of the `await`
Step 2 → `try/catch` catches that thrown error, just like a sync `throw`
Step 3 → `finally` runs in every case (success, caught error, or uncaught error)
Step 4 → `return promise` inside `try` WITHOUT `await` skips the catch (the rejection goes to the caller)
Step 5 → If an async function throws and its caller doesn't handle the returned promise, it becomes an unhandled rejection
Step 6 → Node.js listens for `unhandledRejection` and by default treats it as a fatal error in modern versions

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `await p` throw करता है अगर `p` reject हो, ठीक उसी `await` वाली line पर
Step 2 → `try/catch` वह thrown error पकड़ता है, बिल्कुल sync `throw` की तरह
Step 3 → `finally` हर हाल में चलता है (सफल, पकड़ी गई error, या बिना पकड़ी error)
Step 4 → `try` के अंदर `await` के बिना `return promise` करने पर catch छूट जाता है (rejection caller तक जाती है)
Step 5 → अगर async function throw करे और caller उसके returned promise को handle न करे, तो वह unhandled rejection बन जाती है
Step 6 → Node.js `unhandledRejection` को सुनता है, और नए versions में डिफ़ॉल्ट रूप से इसे fatal मानता है

---

## 🟡 Real World Example
In a Zomato-style order service, placing an order might call the payment gateway, the inventory service, and the notification service. If payment fails, the order must not be created. If the notification fails, the order should still succeed, and the failure should be logged. Good error handling means each `await` is wrapped in the right place, with the right fallback.

## 🟡 Real Example Hindi mein
Zomato जैसी order service में order लगाने पर payment gateway, inventory और notification service को call होता है। अगर payment fail हो, तो order नहीं बनना चाहिए। अगर notification fail हो, तो order फिर भी सफल होना चाहिए, और उस failure को log करना चाहिए। अच्छा error handling मतलब हर `await` को सही जगह wrap करना, सही fallback के साथ।

---

## 💻 Code Example — Basic
```javascript
// Helper: returns a Promise that resolves after `ms` milliseconds
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Fake payment call: rejects when the amount is over the card limit
async function chargeCard(amount) {
  await delay(20);                                   // simulate network latency
  if (amount > 1000) throw new Error("Card limit exceeded"); // reject (throw inside async = rejection)
  return { ok: true, amount };                       // success result
}

// Place an order with try/catch/finally
async function placeOrder(amount) {
  try {
    const res = await chargeCard(amount);            // if chargeCard rejects, await THROWS here
    console.log("paid:", res.amount);                // runs only on success
    return "success";                                // returned value (finally still runs after)
  } catch (err) {                                    // catches the error from await above
    console.log("payment failed:", err.message);     // log the reason
    return "failed";                                 // return a safe result instead of crashing
  } finally {
    console.log("finished attempt for", amount);     // runs in every case
  }
}

// Run two orders one after another
(async () => {
  console.log(await placeOrder(499));                // success path
  console.log(await placeOrder(5000));               // failure path
})();
```

**Expected output (basic):**
```
paid: 499
finished attempt for 499
success
payment failed: Card limit exceeded
finished attempt for 5000
failed
```

## 💻 Code Example — Advanced
```javascript
// Advanced: custom error classes, wrapping with `cause`, a safe wrapper, and a global safety net.

// Helper: resolves after ms
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Base application error with an HTTP-style status code
class AppError extends Error {
  constructor(message, { status = 500, cause } = {}) {  // options object with defaults
    super(message, { cause });                          // `cause` keeps the original error (ES2022)
    this.name = "AppError";                             // name shows in logs and stack traces
    this.status = status;                               // status code for the HTTP layer
  }
}

// Specific error for "not found" cases
class NotFoundError extends AppError {
  constructor(what) {
    super(`${what} not found`, { status: 404 });        // 404 status, message from the argument
    this.name = "NotFoundError";                        // more specific name
  }
}

// Fake database layer: can return null, return data, or throw a low-level error
const db = {
  async findOrder(id) {
    await delay(10);                                    // simulate a query
    if (id === "boom") throw new Error("connection reset"); // low-level failure
    if (id !== "o1") return null;                       // not found
    return { id: "o1", total: 499 };                    // found
  },
};

// Business function: wraps low-level errors into AppError, keeps the original as `cause`
async function getOrder(id) {
  let order;                                            // declared outside try to use after it
  try {
    order = await db.findOrder(id);                     // may throw a low-level error
  } catch (err) {                                       // low-level error caught here
    throw new AppError("database read failed", { cause: err }); // rethrow a clean error
  }
  if (!order) throw new NotFoundError(`order ${id}`);   // business rule: missing order
  return order;                                         // success
}

// Safe wrapper: never throws, always returns { ok, ... } so callers stay simple
const safe = (fn) => async (...args) => {               // higher-order function
  try {
    return { ok: true, data: await fn(...args) };       // success shape
  } catch (err) {
    return { ok: false, status: err.status ?? 500, message: err.message }; // error shape
  }
};

const safeGetOrder = safe(getOrder);                    // wrapped version of getOrder

// Global safety net: runs when a promise rejects with no handler at all
process.on("unhandledRejection", (reason) => {          // listen for unhandled rejections
  console.log("global handler caught:", reason.message); // log instead of crashing (demo only)
});

// Demo
(async () => {
  console.log(await safeGetOrder("o1"));                // ok: true with data
  console.log(await safeGetOrder("zzz"));               // ok: false, status 404
  console.log(await safeGetOrder("boom"));              // ok: false, status 500

  try {
    await getOrder("boom");                             // call directly to read the cause
  } catch (err) {
    console.log(err instanceof AppError, err.cause.message); // true, "connection reset"
  }

  Promise.reject(new Error("forgotten promise"));       // no await, no catch: unhandled
})();
```

**Expected output (advanced):**
```
{ ok: true, data: { id: 'o1', total: 499 } }
{ ok: false, status: 404, message: 'order zzz not found' }
{ ok: false, status: 500, message: 'database read failed' }
true connection reset
global handler caught: forgotten promise
```

---

## 🟠 Express.js Integration
Express 4 does not catch rejected promises returned by route handlers, so an `async` handler that throws leaves the request hanging. The usual fix is a small wrapper that forwards rejections to `next(err)`. Express 5 does this by default. The error middleware then turns the `AppError` into a clean response using its `status`.

```javascript
// Express.js example: async error handling with a wrapper and error middleware
const express = require("express");                 // import Express
const app = express();                              // create the app

// Wrapper: any rejection from the async handler is forwarded to next(err)
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

// Custom error with an HTTP status
class NotFoundError extends Error {
  constructor(what) {
    super(`${what} not found`);                     // message
    this.status = 404;                              // status used by error middleware
  }
}

// Fake data layer
const findOrder = async (id) => (id === "o1" ? { id, total: 499 } : null); // null = not found

app.get("/orders/:id", asyncHandler(async (req, res) => {
  const order = await findOrder(req.params.id);     // may reject on DB failure (goes to next)
  if (!order) throw new NotFoundError(`order ${req.params.id}`); // thrown -> next(err)
  res.json(order);                                  // success response
}));

// Error middleware: must have exactly 4 parameters so Express treats it as error handler
app.use((err, req, res, next) => {
  res.status(err.status || 500).json({ error: err.message }); // send status and message
});

app.listen(3000);                                   // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Returning a rejected promise from `try` without `await` (the catch never runs)
✅ **Correct:** Use `return await` inside `try` so the rejection is caught locally.

```javascript
// Wrong: the rejection bypasses the catch and goes to the caller
async function wrong() {
  try {
    return fetchData();          // returns the promise; catch does NOT see its rejection
  } catch (err) {
    console.log("never printed for async errors");
  }
}

// Right: await inside try so the catch sees the rejection
async function right() {
  try {
    return await fetchData();    // rejection is thrown at this line, so catch runs
  } catch (err) {
    console.log("caught:", err.message);
  }
}
```

❌ **Mistake 2:** Errors inside `setTimeout` callbacks are not caught by `try/catch` around the timer
✅ **Correct:** Wrap the work inside the callback, or convert the timer to a promise and await it.

```javascript
// Wrong: the try is finished before the timer callback runs
try {
  setTimeout(() => { throw new Error("late"); }, 10); // thrown later, outside this try
} catch (err) {
  console.log("never runs");
}

// Right: put try/catch inside the callback
setTimeout(() => {
  try {
    throw new Error("late");     // now the catch is in the same callback
  } catch (err) {
    console.log("caught:", err.message);
  }
}, 10);
```

❌ **Mistake 3:** Swallowing errors with an empty `catch`
✅ **Correct:** Log, rethrow, or convert to a meaningful error. Never hide it silently.

```javascript
// Wrong: the bug disappears, and the caller gets undefined
async function getUser(id) {
  try {
    return await db.find(id);
  } catch (e) {}                 // empty catch: nothing logged, nothing thrown
}

// Right: add context and rethrow
async function getUser2(id) {
  try {
    return await db.find(id);
  } catch (e) {
    throw new Error(`getUser(${id}) failed`, { cause: e }); // keep the original
  }
}
```

---

## 🧠 Tricky Interview Output Question
```javascript
async function a() {
  try {
    return Promise.reject(new Error("oops"));  // returned WITHOUT await
  } catch (e) {
    console.log("caught in a");                // is this printed?
    return "from catch";
  }
}

a()
  .then((v) => console.log("ok:", v))         // is this called?
  .catch((e) => console.log("outer:", e.message));
```
**Answer:**
```
outer: oops
```
**Why:** `return Promise.reject(...)` does not throw inside `try`. It returns a rejected promise, and the `try/catch` has already finished its job by the time that rejection is handled. The async function therefore resolves its own promise with that rejected promise, which makes the outer promise reject with `oops`. The `catch` block never runs, so `caught in a` is never printed, and the `.then` is skipped. Adding `await` before `Promise.reject(...)` fixes this.

---

## ⚫ Interview Questions + Answers

Q1: How does `await` report a rejected promise?
A1: It throws the rejection reason at the line of the `await`. You catch it with `try/catch` like any other thrown error.

Q2: Why does `return promise` inside `try` skip the catch?
A2: Because `return` without `await` does not wait inside the `try`. The `try` block completes normally and the rejected promise is handed to the caller. Use `return await` to catch it locally.

Q3: What is an unhandled rejection and why does it matter?
A3: It is a rejected promise with no `.catch` or `try/catch` attached. Node.js emits `unhandledRejection`, and in modern Node versions the default behavior is to crash the process. This is why every promise chain should end in a handler.

Q4: What is the purpose of `finally` in `async` code?
A4: `finally` runs cleanup code (closing connections, releasing locks, stopping spinners) whether the `try` succeeded or failed. It does not swallow the error unless you add a `return` inside it.

Q5: How do you attach a cause to a re-thrown error?
A5: Use `new Error(message, { cause: originalError })` (ES2022). The original error stays available as `err.cause`, which keeps the stack trace useful for debugging.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a clear, local place to handle an error (`try/catch` around the `await`)
- You need to convert low-level errors to application errors (wrap with `cause`)
- You have a cleanup step that must always run (`finally`)
- You have Express routes, where a wrapper forwards rejections to `next(err)`

❌ Avoid when:
- You put an empty `catch` that hides bugs
- You use `try/catch` for flow control on normal results (return a value instead)
- You expect `try/catch` to catch errors in timers, event listeners, or un-awaited promises

---

## 📊 Visual Diagram
```
async function placeOrder()
   │
   ├─ try {
   │     await chargeCard()  ── rejects ──┐
   │  }                                   │
   │                                      ▼
   ├─ catch (err)  ◄──── thrown at the await line
   │     log + return "failed"           (caught here)
   │
   └─ finally { always runs }

If there were NO catch:
   placeOrder() promise REJECTS ──► caller must handle it
                                      │
                                      └─ no handler? ──► unhandledRejection ──► crash (modern Node)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `try/catch` | Handle errors thrown inside a block | Block के अंदर की error संभालना |
| `finally` | Code that always runs after try/catch | हर हाल में चलने वाला code |
| Unhandled rejection | Rejected promise with no handler | बिना handler वाली rejection |
| `cause` | Original error attached to a new error | नई error के साथ पुरानी error का link |
| Error wrapping | Converting one error into a clearer one | Error को साफ़ error में बदलना |
| Error middleware | Express function with 4 args for errors | Errors के लिए Express middleware |
| Fail fast | Stop at the first error and surface it | पहली error पर रुक जाना |

---

## ⚡ 3-Line Summary
**English:**
1. `await` throws rejections, so handle them with `try/catch` at the line where they can happen.
2. Use `return await` inside `try`, and never leave a promise without a handler.
3. Wrap errors with `cause` for context, use `finally` for cleanup, and use an error wrapper in Express.

**Hindi:**
1. `await` rejection को throw करता है, इसलिए उसी line के आसपास `try/catch` से संभालो।
2. `try` के अंदर `return await` इस्तेमाल करो, और कोई promise बिना handler के मत छोड़ो।
3. Context के लिए `cause` के साथ wrap करो, cleanup के लिए `finally`, और Express में error wrapper।

---

## ➡️ Next Topic
**85. Fetch API** — Now you know how to handle errors in `async` code. Next, apply it to the real thing: the browser and Node.js `fetch` API, including checking `response.ok` (a common gap, because `fetch` does not reject on HTTP 404 or 500).
