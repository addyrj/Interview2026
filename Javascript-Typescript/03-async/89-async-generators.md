# 89. Async Generators
# हिंदी में: Async Generators — समय के साथ Values एक-एक करके देना (async function* और for await...of)

---

## 🔵 Simple Definition (English)
An async generator is a function declared with `async function*`. It can `yield` values over time, pausing between them while it waits for async work. You consume it with `for await...of`, which asks for the next value only when the loop is ready for it.

## 🔵 सरल परिभाषा (Hindi)
Async generator एक function है जिसे `async function*` से declare किया जाता है। यह समय के साथ values `yield` कर सकता है, और async काम का इंतज़ार करते हुए बीच में रुक सकता है। इसे `for await...of` से consume करते हैं, जो अगली value तभी मांगता है जब loop उसके लिए तैयार हो।

---

## 🔴 Problem it Solves
Many APIs return data in pages (100 orders at a time), or data arrives as a stream (a large CSV or log file). Loading everything into an array first uses too much memory and delays the first result. Plain generators are lazy but synchronous, and promises return one value only. Async generators combine both: lazy, one value at a time, and each step can wait for I/O.

## 🔴 यह क्यों बना? (Hindi)
बहुत सारे APIs data को pages में देते हैं (एक बार में 100 orders), या data stream की तरह आता है (बड़ी CSV या log file)। पहले सारा data array में लोड करने से memory ज़्यादा लगती है और पहला result देर से मिलता है। सामान्य generators lazy होते हैं पर synchronous होते हैं, और promise सिर्फ एक value देता है। Async generators दोनों को जोड़ते हैं: lazy, एक बार में एक value, और हर step I/O का इंतज़ार कर सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `async function* gen()` creates an async generator; calling it returns an async iterator (nothing runs yet)
Step 2 → `await` and `yield` can both appear inside the body
Step 3 → Each `gen.next()` returns a Promise of `{ value, done }`
Step 4 → `for await (const x of gen())` calls `next()` for you, one value at a time
Step 5 → `yield` pauses the generator until the consumer asks for the next value
Step 6 → If the consumer breaks out of the loop, `return()` is called, so `finally` blocks in the generator run (cleanup)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `async function* gen()` एक async generator बनाता है; इसे call करने पर async iterator मिलता है (अभी कुछ नहीं चलता)
Step 2 → Body में `await` और `yield` दोनों हो सकते हैं
Step 3 → हर `gen.next()` एक Promise देता है जो `{ value, done }` के साथ resolve होता है
Step 4 → `for await (const x of gen())` आपके लिए `next()` call करता है, एक बार में एक value
Step 5 → `yield` generator को तब तक रोकता है जब तक consumer अगली value न मांगे
Step 6 → अगर consumer loop से break करे, तो `return()` call होता है, इसलिए generator के `finally` blocks चलते हैं (cleanup)

---

## 🟡 Real World Example
Flipkart's seller dashboard exports 2 lakh orders. Loading all of them at once would exhaust memory. An async generator fetches one page of 100 orders, yields each order to a CSV writer, then fetches the next page only when the writer is ready. If the seller cancels the export (break), no more pages are requested.

## 🟡 Real Example Hindi mein
Flipkart के seller dashboard में 2 लाख orders export होने हैं। सब एक साथ लोड करने से memory खत्म हो जाएगी। एक async generator 100 orders का एक page लाता है, हर order को CSV writer को `yield` करता है, और अगला page तभी लाता है जब writer तैयार हो। अगर seller export cancel कर दे (break), तो आगे के pages request ही नहीं होते।

---

## 💻 Code Example — Basic
```javascript
// Helper: resolves after ms milliseconds
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// An async generator: yields a countdown, one value every 50ms
async function* countdown(n) {                 // async function* = async generator
  while (n > 0) {                              // keep going while n is positive
    await delay(50);                           // async work before each value
    yield n;                                   // hand n to the consumer, then pause here
    n--;                                       // runs only when the consumer asks for more
  }
  return "liftoff";                            // final return value (not yielded in for...of)
}

// Helper: async iterable from a plain array of promises
async function* fromPromises(list) {
  for (const p of list) {                      // go through the list in order
    yield await p;                             // wait for each promise, then yield its value
  }
}

(async () => {
  // 1. for await...of: consume the countdown
  for await (const n of countdown(3)) {        // asks for next() automatically
    console.log("count:", n);                  // 3, then 2, then 1
  }

  // 2. Manual next(): see the { value, done } objects directly
  const gen = countdown(1);                     // nothing has run yet
  console.log(await gen.next());               // { value: 1, done: false }
  console.log(await gen.next());               // { value: 'liftoff', done: true }

  // 3. Consume an array of promises as a stream
  for await (const v of fromPromises([Promise.resolve("a"), delay(10).then(() => "b")])) {
    console.log("value:", v);                  // a, then b
  }
})();
```

**Expected output (basic):**
```
count: 3
count: 2
count: 1
{ value: 1, done: false }
{ value: 'liftoff', done: true }
value: a
value: b
```

## 💻 Code Example — Advanced
```javascript
// Advanced: a paginated API as an async generator, lazy page loading, and cleanup on early break.

// Helper: resolves after ms
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Fake paginated API: page -> { items, next }. next is null on the last page.
const PAGES = {
  1: { items: ["order-1", "order-2"], next: 2 },
  2: { items: ["order-3", "order-4"], next: 3 },
  3: { items: ["order-5"], next: null },
};
let pagesRequested = 0;                        // count network calls to prove laziness

async function fetchPage(page) {              // simulate a network call
  await delay(20);                             // 20ms latency
  pagesRequested++;                            // count this request
  return PAGES[page];                          // return the page data
}

// Async generator: yields every order across all pages, loading pages on demand
async function* allOrders() {
  let page = 1;                                // start at page 1
  try {
    while (page !== null) {                    // loop until there is no next page
      const { items, next } = await fetchPage(page); // load ONE page
      for (const order of items) {             // yield each order from this page
        yield order;                           // pause until the consumer wants the next one
      }
      page = next;                             // move to the next page (null when finished)
    }
  } finally {
    // Runs when the generator finishes OR when the consumer breaks early (return() is called)
    console.log("generator cleanup");          // release connections or log the export end
  }
}

// Consumer: stop after order-4 (so page 3 should never be requested)
(async () => {
  for await (const order of allOrders()) {     // one order at a time
    console.log("order:", order);              // order-1, order-2, order-3, order-4
    if (order === "order-4") break;            // early exit: triggers generator cleanup
  }
  console.log("pages requested:", pagesRequested); // 2 (page 3 was never fetched)
})();
```

**Expected output (advanced):**
```
order: order-1
order: order-2
order: order-3
order: order-4
generator cleanup
pages requested: 2
```

---

## 🟠 Express.js Integration
Async generators fit Express well for streaming large responses. The route loops with `for await...of`, writes each chunk with `res.write`, and waits for `drain` when the socket buffer is full (backpressure). If the client disconnects, the loop stops, so no more database pages are read.

```javascript
// Express.js example: stream a big export as NDJSON using an async generator
const express = require("express");                 // import Express
const { once } = require("events");                 // helper to await a single event
const app = express();                              // create the app

// Fake paged data source (real code: a database cursor or paginated API)
async function* orderRows() {
  for (let page = 1; page <= 3; page++) {           // 3 pages of data
    const rows = [{ id: page * 10 + 1 }, { id: page * 10 + 2 }]; // two rows per page
    for (const row of rows) yield row;              // yield rows one at a time
  }
}

app.get("/export/orders", async (req, res, next) => {
  res.type("application/x-ndjson");                 // one JSON object per line
  try {
    for await (const row of orderRows()) {          // pull rows lazily
      if (res.destroyed) break;                     // client left: stop reading data
      const ok = res.write(JSON.stringify(row) + "\n"); // write one line
      if (!ok) await once(res, "drain");            // buffer full: wait (backpressure)
    }
    res.end();                                      // finish the response
  } catch (err) {
    next(err);                                      // error before the response ended
  }
});

app.listen(3000);                                   // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using a plain `for...of` on an async generator (it has no synchronous iterator)
✅ **Correct:** Use `for await...of` for async iterables.

```javascript
// Wrong: TypeError, the async generator is not a sync iterable
for (const n of countdown(3)) {
  console.log(n);
}

// Right
for await (const n of countdown(3)) {
  console.log(n);
}
```

❌ **Mistake 2:** Expecting `yield` inside a normal callback (`forEach`) to work
✅ **Correct:** `yield` only works directly inside the generator body, so use `for...of`.

```javascript
// Wrong: SyntaxError, yield is not allowed in a nested arrow function
async function* bad(items) {
  items.forEach((item) => {
    yield item;                 // SyntaxError
  });
}

// Right
async function* good(items) {
  for (const item of items) {   // for...of keeps yield in the generator body
    yield item;
  }
}
```

❌ **Mistake 3:** Collecting the whole stream into an array just to loop over it later
✅ **Correct:** Process values as they arrive, so memory stays low and the first result comes early.

```javascript
// Wrong: loads every page before the first row is written
const all = [];
for await (const row of orderRows()) all.push(row);
writeAll(all);

// Right: process each row as it is produced
for await (const row of orderRows()) writeRow(row);
```

---

## 🧠 Tricky Interview Output Question
```javascript
async function* gen() {
  console.log("start");          // runs only when next() is first called
  yield 1;                       // pause here and give 1
  console.log("after yield");    // runs when the next value is requested
  yield 2;                       // pause again and give 2
}

const it = gen();                // creates the generator: body has NOT run
console.log("created");           // printed first

(async () => {
  console.log(await it.next());  // what is printed, and in which order?
  console.log("between");
  console.log(await it.next());  // what now?
})();
```
**Answer:**
```
created
start
{ value: 1, done: false }
between
after yield
{ value: 2, done: false }
```
**Why:** Calling `gen()` only creates the generator object, so nothing in the body runs and `created` prints first. The IIFE then calls `it.next()`, which starts the body synchronously: `start` prints, and the body reaches `yield 1`. The first `next()` promise resolves with `{ value: 1, done: false }`, and `await` lets the IIFE print it. The loop then prints `between`. The second `next()` resumes the body after the first `yield`, so `after yield` prints. Then `yield 2` resolves the second promise. The generator stays paused between values, which is what makes it lazy.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a generator and an async generator?
A1: A generator (`function*`) is synchronous and each `next()` returns `{ value, done }` directly. An async generator (`async function*`) returns a promise from `next()`, so each step can `await` I/O.

Q2: What does `for await...of` do?
A2: It calls `next()` on the async iterable, awaits each returned promise, and runs the loop body with `value` until `done` is `true`. It works with async generators and with arrays of promises.

Q3: What happens when you `break` out of a `for await` loop?
A3: JavaScript calls the iterator's `return()` method. For an async generator, that resumes it with a return, so its `finally` blocks run. This is the way to release resources when a consumer stops early.

Q4: Is an async generator lazy?
A4: Yes. Nothing runs until the first `next()` call, and each step runs only when the consumer asks for it. This is why paginated APIs fetch the next page only when needed.

Q5: When would you prefer a stream or an async generator over `Promise.all`?
A5: When the data is large, arrives over time, or should be processed as it comes. `Promise.all` waits for everything and holds all results in memory, while an async generator yields one value at a time.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The data comes in pages or chunks (paginated APIs, cursors, file reads)
- You want to process values as they arrive, with low memory use
- You need early exit with proper cleanup (`break` plus `finally`)
- You are streaming large responses from Express

❌ Avoid when:
- You need all results at once and the data is small; `Promise.all` or a plain array is simpler
- The steps are fully independent and can run in parallel; use a concurrency limiter (topic 82)
- You only need a single async value; a plain `async` function is enough

---

## 📊 Visual Diagram
```
for await (const order of allOrders())       allOrders() generator body
   │                                              │
   ├── next() ─────────────────────────────►  fetchPage(1) ... await (20ms)
   │   ◄────────── { value: "order-1" } ────── yield "order-1"  (paused)
   │
   ├── next() ─────────────────────────────►  resumes, yields "order-2" (paused)
   │   ◄────────── { value: "order-2" }
   │
   ├── next() ─────────────────────────────►  page done, fetchPage(2) ... await
   │   ◄────────── { value: "order-3" }
   │
   └── break (order-4) ──► return() ──► finally { cleanup }   page 3 never requested
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Async generator | `async function*` that yields values over time | समय के साथ values देने वाला async function* |
| `yield` | Pause and give a value to the consumer | Value देकर रुक जाना |
| `for await...of` | Loop over an async iterable | Async iterable पर loop |
| Async iterator | Object with `next()` returning a promise | `next()` से promise देने वाला object |
| `return()` | Called on early `break`; runs `finally` | Early break पर चलने वाला method |
| Lazy | Work happens only when requested | माँगने पर ही काम होना |
| Backpressure | Slowing the producer when the consumer is slow | Consumer धीमा हो तो producer को रोकना |

---

## ⚡ 3-Line Summary
**English:**
1. `async function*` yields values over time, and each `next()` returns a promise of `{ value, done }`.
2. `for await...of` consumes them one at a time, and `break` triggers cleanup in `finally`.
3. Use async generators for paginated or streamed data, so memory stays low and pages load on demand.

**Hindi:**
1. `async function*` समय के साथ values देता है, और हर `next()` `{ value, done }` का promise देता है।
2. `for await...of` उन्हें एक-एक करके consume करता है, और `break` से `finally` में cleanup होता है।
3. Pages या stream वाले data के लिए async generators इस्तेमाल करो, ताकि memory कम रहे और pages माँगने पर लोड हों।

---

## ➡️ Next Topic
**90. Concurrency vs Parallelism** — You now have all the async tools. Next, understand the big picture: why Node.js handles many requests with one thread (concurrency), when you really need multiple cores (parallelism), and how that differs from what `Promise.all` does.
