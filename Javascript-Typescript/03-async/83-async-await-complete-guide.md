# 83. async/await — Complete Guide
# हिंदी में: async/await — Promises को सीधे-सादे (synchronous jaisa) code की तरह लिखना

---

## 🔵 Simple Definition (English)
`async` marks a function so it always returns a Promise. `await` pauses only that async function until a Promise settles, then gives you its value. The rest of the program keeps running while it waits.

## 🔵 सरल परिभाषा (Hindi)
`async` किसी function को ऐसा बनाता है कि वह हमेशा एक Promise लौटाए। `await` सिर्फ उसी async function को रोकता है जब तक कोई Promise settle न हो जाए, फिर उसकी value देता है। बाकी program चलता रहता है।

---

## 🔴 Problem it Solves
Promise chains are correct but hard to read when there are `if` conditions, loops, and error paths. Variables from earlier steps have to be passed down through each `.then`, and branching logic becomes awkward. `async`/`await` lets you write the same logic with normal variables, `if`, `for`, and `try/catch`, while keeping the non-blocking behavior of promises.

## 🔴 यह क्यों बना? (Hindi)
Promise chain सही है, पर जब `if`, loop और error paths आते हैं तो पढ़ना मुश्किल हो जाता है। पिछले steps की variables को हर `.then` में आगे भेजना पड़ता है। `async`/`await` वही logic normal variables, `if`, `for` और `try/catch` के साथ लिखने देता है, और promises का non-blocking फायदा भी बना रहता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Writing `async function f()` means `f()` ALWAYS returns a Promise
Step 2 → A `return value` inside `f` resolves that promise with `value`
Step 3 → `await p` pauses `f` (not the whole program) until `p` settles
Step 4 → If `p` fulfills, `await` gives its value; if `p` rejects, `await` THROWS that error
Step 5 → Code after the first `await` runs later, as a microtask (the thread is free in between)
Step 6 → `await` only works inside an `async` function (or at the top level of an ES module)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `async function f()` लिखने पर `f()` हमेशा एक Promise लौटाता है
Step 2 → `f` के अंदर `return value` उस promise को `value` के साथ resolve करता है
Step 3 → `await p` सिर्फ `f` को रोकता है (पूरे program को नहीं) जब तक `p` settle न हो
Step 4 → अगर `p` fulfill हो तो `await` value देता है; अगर reject हो तो `await` वह error throw करता है
Step 5 → पहले `await` के बाद वाला code बाद में, microtask के रूप में चलता है (बीच में thread खाली रहता है)
Step 6 → `await` सिर्फ `async` function के अंदर (या ES module के top level पर) काम करता है

---

## 🟡 Real World Example
On Paytm or Razorpay checkout, the flow is: validate the cart, create a payment intent, redirect the user, wait for the webhook, then confirm the order. Each step needs the previous step's result, and some steps need an `if` (for example, "if the coupon is invalid, skip the discount"). `async`/`await` keeps that flow readable.

## 🟡 Real Example Hindi mein
Paytm या Razorpay checkout में flow ऐसा होता है: cart validate करो, payment intent बनाओ, user को redirect करो, webhook का इंतज़ार करो, फिर order confirm करो। हर step को पिछले step का result चाहिए, और कुछ steps में `if` भी आता है (जैसे "अगर coupon गलत है तो discount छोड़ दो")। `async`/`await` यह flow पढ़ने में आसान रखता है।

---

## 💻 Code Example — Basic
```javascript
// Helper: returns a Promise that resolves with `value` after `ms` milliseconds
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));

// An async function: the `return` value becomes the resolved value of the promise
async function getUser(id) {
  await delay(50);                       // pause THIS function for 50ms (program keeps running)
  return { id, name: "Aditya" };         // resolves the returned promise with this object
}

async function main() {                  // main is async so we can use await inside it
  console.log("typeof getUser:", typeof getUser);  // "function"

  const p = getUser(1);                  // calling an async function returns a Promise right away
  console.log("is promise:", p instanceof Promise); // true

  const user = await p;                  // wait for the promise and get its value
  console.log("user:", user);            // { id: 1, name: 'Aditya' }

  // Sequential: each await waits for the previous one to finish
  const start = Date.now();              // remember the start time in milliseconds
  const a = await getUser(2);            // waits 50ms
  const b = await getUser(3);            // waits another 50ms
  console.log("sequential ids:", a.id, b.id);                // 2 3
  console.log("took at least 100ms:", Date.now() - start >= 100); // true
}

main();                                  // start the program
```

**Expected output (basic):**
```
typeof getUser: function
is promise: true
user: { id: 1, name: 'Aditya' }
sequential ids: 2 3
took at least 100ms: true
```

## 💻 Code Example — Advanced
```javascript
// Advanced: sequential vs parallel awaits, timing checks, and safe error handling.

// Helper: resolves with value after ms
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));

// Two independent fake API calls, each takes 100ms
async function fetchUser(id) {
  await delay(100);                                    // simulate network latency
  return { id, name: `user${id}` };                    // user data
}

async function fetchOrders(userId) {
  await delay(100);                                    // simulate network latency
  return [{ orderId: 1, userId }];                     // order list
}

// BAD for independent calls: second call waits for the first (about 200ms total)
async function loadSequential(id) {
  const user = await fetchUser(id);                    // wait 100ms
  const orders = await fetchOrders(id);                // then wait another 100ms (not needed!)
  return { user, orders };                             // combine results
}

// GOOD for independent calls: start both, then wait for both (about 100ms total)
async function loadParallel(id) {
  const [user, orders] = await Promise.all([           // both calls start now
    fetchUser(id),                                     // promise 1
    fetchOrders(id),                                   // promise 2
  ]);
  return { user, orders };                             // combine results
}

// Helper: measure how long an async function takes
async function timed(fn) {
  const t0 = Date.now();                               // start time
  const result = await fn();                           // run and wait for the function
  return { ms: Date.now() - t0, result };              // elapsed ms and the result
}

// Error-safe wrapper: returns a default value instead of throwing
async function loadProfileSafe(id) {
  try {
    return await loadParallel(id);                     // await INSIDE try so rejections are caught
  } catch (err) {                                      // handles errors from loadParallel
    console.log("profile failed:", err.message);       // log for monitoring
    return { user: null, orders: [] };                 // safe fallback
  }
}

// Main demo
(async () => {
  const seq = await timed(() => loadSequential(1));    // about 200ms
  const par = await timed(() => loadParallel(1));      // about 100ms

  console.log("sequential took >= 190ms:", seq.ms >= 190);  // true
  console.log("parallel took < 190ms:", par.ms < 190);      // true
  console.log("same data:", JSON.stringify(seq.result) === JSON.stringify(par.result)); // true

  const profile = await loadProfileSafe(7);            // succeeds
  console.log("profile user:", profile.user.name);    // "user7"
})();
```

**Expected output (advanced):**
```
sequential took >= 190ms: true
parallel took < 190ms: true
same data: true
profile user: user7
```

---

## 🟠 Express.js Integration
`async` route handlers are the normal way to write Express routes today. Each `await` is a database or HTTP call, and the handler reads top to bottom like sync code. Note: Express 4 does NOT catch promise rejections from `async` handlers, so wrap the body in `try/catch` and call `next(err)`. Express 5 forwards rejected promises to error middleware automatically.

```javascript
// Express.js example: async/await in a route handler
const express = require("express");                 // import Express
const app = express();                              // create the app
app.use(express.json());                            // parse JSON bodies

// Fake database functions (in a real app: Mongoose, Prisma, or pg)
const findOrder = async (id) => (id === "o1" ? { id, total: 499 } : null);
const markPaid = async (order) => ({ ...order, status: "paid" });

app.post("/orders/:id/pay", async (req, res, next) => { // async handler
  try {
    const order = await findOrder(req.params.id);   // wait for the DB lookup
    if (!order) {                                    // normal if/else, no .then needed
      return res.status(404).json({ error: "order not found" });
    }
    const paid = await markPaid(order);              // wait for the update
    res.json(paid);                                  // send the result
  } catch (err) {                                    // DB failure lands here
    next(err);                                       // hand the error to Express error middleware
  }
});

app.use((err, req, res, next) => {                   // error middleware (4 args)
  res.status(500).json({ error: err.message });      // clean JSON error
});

app.listen(3000);                                    // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `await` inside `forEach` (the callbacks are not awaited)
✅ **Correct:** Use `for...of` for sequential work, or `Promise.all` with `map` for parallel work.

```javascript
// Wrong: forEach ignores the promises returned by its callbacks
ids.forEach(async (id) => {
  await saveOrder(id);           // these run, but the outer function does NOT wait
});
console.log("done");               // prints BEFORE the saves finish

// Right: sequential with for...of
for (const id of ids) {
  await saveOrder(id);           // waits for each save in turn
}

// Right: parallel with map + Promise.all
await Promise.all(ids.map((id) => saveOrder(id)));
```

❌ **Mistake 2:** Forgetting `async` on the function that uses `await`
✅ **Correct:** Any function that uses `await` must be declared `async`.

```javascript
// Wrong: SyntaxError (await is only valid inside async functions in this file type)
function getUser(id) {
  const user = await fetchUser(id); // SyntaxError
  return user;
}

// Right
async function getUser2(id) {
  const user = await fetchUser(id); // OK
  return user;
}
```

❌ **Mistake 3:** Awaiting independent calls one after another (slow)
✅ **Correct:** Start them first, then await them together.

```javascript
// Wrong: total time = sum of both calls
const user = await fetchUser(1);
const orders = await fetchOrders(1);

// Right: total time = slower of the two calls
const [user2, orders2] = await Promise.all([fetchUser(1), fetchOrders(1)]);
```

---

## 🧠 Tricky Interview Output Question
```javascript
async function f() {
  console.log(1);                  // runs synchronously when f() is called
  await null;                      // pauses f; the rest becomes a microtask
  console.log(2);                  // runs later, after the current sync code
  return 3;                        // resolves the promise returned by f()
}

console.log(0);                    // sync
f().then((v) => console.log("v", v)); // attach a callback to f's promise
console.log(4);                    // sync
```
**Answer:**
```
0
1
4
2
v 3
```
**Why:** Code runs top to bottom until something must wait. `console.log(0)` prints first. Calling `f()` runs its body up to `await null`, so `1` prints. `f()` then returns a pending promise, and `console.log(4)` runs. Only then does the microtask queue run: `f` resumes, prints `2`, and returns `3`, which resolves the promise. The `.then` callback is queued and prints `v 3`. The key point is that `await` always yields, even when it awaits a plain value like `null`.

---

## ⚫ Interview Questions + Answers

Q1: What does an `async` function return?
A1: Always a Promise. If the body returns a plain value, that value resolves the promise. If the body throws, the promise rejects.

Q2: Does `await` block the whole Node.js process?
A2: No. It pauses only the async function it is inside. The event loop keeps handling other requests and timers while that function waits.

Q3: What is the difference between `await` in sequence and `await` with `Promise.all`?
A3: Sequential awaits start each call only after the previous one finishes, so times add up. `Promise.all` starts all the calls first and waits for them together, so the total time is about the slowest call.

Q4: How do you handle errors with `async`/`await`?
A4: Wrap the `await` in `try/catch`. A rejected promise throws at the `await` line, so the catch block receives it. Remember that a `return promise` without `await` inside `try` is not caught.

Q5: Can you use `await` at the top level of a file?
A5: Only in ES modules (`.mjs` or `"type": "module"` in package.json) and in some runtimes. In a plain CommonJS `.js` file, wrap the code in an `async` function, as in the examples above.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Steps depend on each other and you need `if`, loops, or `try/catch` between them
- You want code that reads top to bottom like synchronous code
- You are writing Express route handlers or service functions that call I/O

❌ Avoid when:
- Calls are independent; start them with `Promise.all` instead of awaiting one by one
- You are inside a `forEach` callback; use `for...of` or `map` + `Promise.all`
- A tight CPU-heavy loop is involved; `await` does not make CPU work parallel

---

## 📊 Visual Diagram
```
main() starts
   │
   ├─ await getUser(1)  ─── main PAUSES ───────────────┐
   │                                                   │ event loop runs other
   │                                                   │ requests and timers
   │   (promise resolves)                              │
   ◄───────────────────────────────────────────────────┘
   │
   ├─ user = { id: 1, ... }   (value unwrapped by await)
   │
   ├─ await getUser(2)  ─── pause again ...
   │
   └─ function returns; its outer promise resolves
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `async` | Makes a function always return a Promise | Function को हमेशा Promise लौटाने वाला बनाना |
| `await` | Pauses the async function until a promise settles | Promise settle होने तक function को रोकना |
| Async function | Function declared with `async` | `async` से बना function |
| Unwrap | `await` gives the value, not the promise | Promise से असली value निकालना |
| Microtask | Code queued after an `await` resumes | `await` के बाद वापस आने वाला task |
| Sequential await | One await after another | एक के बाद एक await |
| Top-level await | `await` outside any function (ES modules only) | Function के बाहर await |

---

## ⚡ 3-Line Summary
**English:**
1. `async` functions always return a Promise; `await` pauses that function and unwraps the value.
2. Use `await` one by one only when each step depends on the previous; otherwise use `Promise.all`.
3. Use `try/catch` around `await` for errors, and never use `await` inside `forEach`.

**Hindi:**
1. `async` function हमेशा Promise लौटाता है; `await` उस function को रोकता है और value निकालता है।
2. एक-एक करके `await` तभी करो जब हर step पिछले पर निर्भर हो; वरना `Promise.all` इस्तेमाल करो।
3. Error के लिए `await` के चारों तरफ `try/catch` रखो, और `forEach` में `await` कभी मत करो।

---

## ➡️ Next Topic
**84. Error Handling in async/await** — Now that you can write async code with `await`, the next step is handling failures correctly: try/catch patterns, wrapping errors, and what happens when an error is never caught.
