# 191. Async Series + Parallel Execution
# हिंदी में: Async Tasks को Series और Parallel में चलाना — Order, Concurrency Limit और Error Handling

---

## 🔵 Simple Definition (English)
Series execution means running async tasks one after another, so the next task starts only when the previous one finishes. Parallel execution means starting all tasks together and waiting for all of them. Interviews test whether you can pick the right one, keep the result order, and stop a flood of work when there are too many tasks.

## 🔵 सरल परिभाषा (Hindi)
Series execution का मतलब है async tasks को एक के बाद एक चलाना, यानी अगला task तभी शुरू हो जब पिछला पूरा हो जाए। Parallel execution का मतलब है सारे tasks एक साथ शुरू करना और सबके पूरे होने का इंतज़ार करना। Interview में देखा जाता है कि आप सही तरीका चुन सकते हैं, results का क्रम बनाए रख सकते हैं, और बहुत सारे काम एक साथ आने पर उन्हें काबू में रख सकते हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Given a list of async tasks (API calls, DB reads, file uploads), run them either one by one (series) or all together (parallel). Return the results in the same order as the input, even when tasks finish in a different order. For a large list, run at most `N` tasks at the same time.

Without this pattern, code either becomes slow (every call waits for the last one) or dangerous (10,000 requests fire at once and the server or the payment gateway starts rejecting them). A `forEach` with an `async` callback looks correct but does not wait at all.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** Async tasks (API calls, DB reads, file uploads) की list दी हो, तो उन्हें या तो एक-एक करके (series) या एक साथ (parallel) चलाओ। Results वही क्रम रखें जो input का है, भले ही tasks अलग-अलग समय पर खत्म हों। बड़ी list के लिए एक समय पर सिर्फ `N` tasks चलें।

इस pattern के बिना code या तो धीमा होता है (हर call आख़िरी call का इंतज़ार करता है) या खतरनाक (10,000 requests एक साथ जाती हैं और server या payment gateway उन्हें reject करने लगता है)। `async` callback वाला `forEach` सही दिखता है, पर वह बिल्कुल इंतज़ार नहीं करता।

---

## 🟢 How it Works — Step by Step

Step 1 → A task is written as a function `() => promise`, so it starts only when we call it.
Step 2 → Series: `for...of` with `await` calls one task, waits, then calls the next.
Step 3 → Parallel: `tasks.map((t) => t())` starts all tasks now, and `Promise.all` waits for all of them.
Step 4 → Both methods return results in input order, not in finishing order.
Step 5 → A concurrency limit starts `N` "runners"; each runner takes the next item when it is free.
Step 6 → If any task fails, `Promise.all` rejects at once; series stops before the remaining tasks run.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Task को function `() => promise` के रूप में लिखा जाता है, ताकि वह तभी शुरू हो जब हम उसे call करें।
Step 2 → Series में `for...of` और `await` से एक task call होता है, उसके पूरा होने का इंतज़ार होता है, फिर अगला।
Step 3 → Parallel में `tasks.map((t) => t())` सारे tasks अभी शुरू करता है, और `Promise.all` उन सबका इंतज़ार करता है।
Step 4 → दोनों तरीकों में results input के क्रम में मिलते हैं, finish होने के क्रम में नहीं।
Step 5 → Concurrency limit में `N` "runners" शुरू होते हैं; जो runner खाली होता है वह अगला item उठा लेता है।
Step 6 → कोई task fail हो तो `Promise.all` तुरंत reject होता है; series बाकी tasks चलने से पहले ही रुक जाती है।

---

## 🟡 Real World Example
Zomato's checkout screen needs the cart total, the delivery fee, and the coupon discount. These three calls do not depend on each other, so they run in parallel. But the payment step must run in series: first reserve the amount, then capture it, then send the receipt. A bulk job that sends 50,000 SMS alerts for a sale uses a limit of 20 at a time, so the SMS provider does not block the account.

Scenario: A Paytm bulk refund job has 5 refunds. Each refund must finish before the next one starts, because of a shared ledger lock. The same job also fetches the user name and phone for each refund in parallel, with at most 2 lookups at the same time.

## 🟡 Real Example Hindi mein
Zomato के checkout screen को cart total, delivery fee और coupon discount चाहिए। ये तीनों calls एक-दूसरे पर निर्भर नहीं हैं, इसलिए parallel चलते हैं। लेकिन payment step series में चलता है: पहले amount reserve करो, फिर capture करो, फिर receipt भेजो। Sale के लिए 50,000 SMS alerts भेजने वाला bulk job एक समय पर सिर्फ 20 भेजता है, ताकि SMS provider account block न करे।

उदाहरण: Paytm के bulk refund job में 5 refunds हैं। Shared ledger lock की वजह से हर refund पूरा होने के बाद ही अगला शुरू होना चाहिए। उसी job में हर refund के लिए user का नाम और phone भी लाने हैं, और वह काम एक समय पर सिर्फ 2 lookups के साथ parallel चलता है।

---

## 💻 Code Example — Basic
```javascript
// Helper: returns a promise that resolves with `value` after `ms` milliseconds (simulates a network call)
const delay = (ms, value) =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms)); // setTimeout calls resolve later

// Helper: a small wrapper so the log lines are easy to find
const log = (msg) => console.log(msg); // print one line

// Series: run tasks one after another; each task is a FUNCTION so it starts only when we call it
async function series(tasks) {
  const results = [];                           // array to collect results in input order
  for (const task of tasks) {                   // go through the tasks one by one
    results.push(await task());                 // call the task, wait for it to finish, then store its result
  }
  return results;                               // all tasks done: return results in the same order
}

// Parallel: start every task right away, then wait for all of them together
async function parallel(tasks) {
  return Promise.all(tasks.map((task) => task())); // map calls each task now; Promise.all waits for all
}

// Demo task: logs when it starts and ends, and returns a value after `ms`
const makeTask = (name, ms) => async () => {    // returns a function; calling it starts the work
  log(`start ${name}`);                         // runs at the moment the task is called
  const result = await delay(ms, `${name}-done`); // wait `ms` milliseconds, then get the value
  log(`end ${name}`);                           // runs after the wait is over
  return result;                                // value that goes into the results array
};

// Three tasks with different durations: A is slowest, B is fastest
const tasks = [makeTask("A", 300), makeTask("B", 100), makeTask("C", 200)];

(async () => {                                  // async IIFE so we can use await at top level
  log("== series ==");                         // header line for the first demo
  console.log(await series(tasks));            // A finishes, then B starts, then C
  log("== parallel ==");                      // header line for the second demo
  console.log(await parallel(tasks));         // A, B, C all start together
})();

// Expected output:
// == series ==
// start A
// end A
// start B
// end B
// start C
// end C
// [ 'A-done', 'B-done', 'C-done' ]
// == parallel ==
// start A
// start B
// start C
// end B
// end C
// end A
// [ 'A-done', 'B-done', 'C-done' ]
```

## 💻 Code Example — Advanced
```javascript
// Helper: wait `ms` milliseconds (same idea as the basic example)
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms)); // resolve after ms

// mapLimit: process items with at most `limit` tasks running at the same time, results keep input order
async function mapLimit(items, limit, worker) {
  // Guard: a limit must be a whole number of at least 1, otherwise nothing would ever run
  if (!Number.isInteger(limit) || limit < 1) throw new RangeError("limit must be a positive integer");

  const results = new Array(items.length);      // one slot per item, so results[i] matches items[i]
  let nextIndex = 0;                            // shared pointer to the next item nobody has taken yet

  async function runner() {                     // a runner keeps taking items until none are left
    while (nextIndex < items.length) {          // is there still an unclaimed item?
      const index = nextIndex++;                // claim this item; no other runner can get the same index
      results[index] = await worker(items[index], index); // run the worker and store its result in its slot
    }
  }

  // Start up to `limit` runners, but never more runners than there are items
  const runners = Array.from({ length: Math.min(limit, items.length) }, () => runner());
  await Promise.all(runners);                   // resolves when every runner has run out of items
  return results;                               // same order as the input, even though items finished at different times
}

// Demo: five jobs that take different times; at most 2 run at once
const jobMs = [500, 100, 300, 200, 400];        // duration of each job in milliseconds

(async () => {
  const out = await mapLimit(jobMs, 2, async (ms, i) => {  // worker gets (item, index)
    console.log(`job ${i} start (${ms}ms)`);     // show when the job begins
    await delay(ms);                            // simulate the work
    console.log(`job ${i} end`);                // show when the job finishes
    return ms / 100;                            // this value goes into the results array
  });
  console.log(out);                             // results in input order: [5, 1, 3, 2, 4]
})();

// Time:  O(n) calls to the worker; total wall-clock time is about (sum of durations) / limit in the best case
// Space: O(n) for the results array; O(limit) extra for the runner promises
```

### Edge Cases
```javascript
// Edge 1: empty input must return an empty array, not hang or throw
(async () => {
  console.log(await Promise.all([]));          // Expected output: []
  console.log(await Promise.all([].map(async (x) => x))); // Expected output: []
})();

// Edge 2: series stops at the first failure, so later tasks are never called
let calls = 0;                                  // counts how many tasks were actually started
const failing = [
  async () => { calls++; return "ok"; },        // first task succeeds
  async () => { calls++; throw new Error("payment failed"); }, // second task fails
  async () => { calls++; return "never"; },     // third task must not run
];
(async () => {
  try {
    for (const task of failing) await task();   // same loop shape as series()
  } catch (e) {
    console.log("stopped:", e.message, "calls:", calls); // Expected output: stopped: payment failed calls: 2
  }
})();

// Edge 3: allSettled reports every result, so one failure does not hide the others
Promise.allSettled([Promise.resolve(1), Promise.reject(new Error("x"))]).then((r) => {
  console.log(r.map((x) => x.status).join(","));  // Expected output: fulfilled,rejected
});
```

---

## 🟠 Express.js Integration
An order summary page needs three independent services: the order, the restaurant, and the rating. They run in parallel. The rating is optional, so its failure must not break the page. The order is required, so its failure returns a 404.

```javascript
// Express.js: GET /api/orders/:id/summary calls three services in parallel
const express = require("express");             // web framework (install with: npm i express)
const app = express();                          // create the Express app

// Fake service calls; in real code these would be HTTP or database calls
const getOrder = async (id) => ({ id, item: "Paneer Tikka", total: 320 }); // order service
const getRestaurant = async () => ({ name: "Punjab Grill" });              // restaurant service
const getRating = async () => { throw new Error("rating service down"); }; // rating service that is failing

app.get("/api/orders/:id/summary", async (req, res, next) => { // async route handler
  try {                                         // catch errors from awaited code
    const id = req.params.id;                   // read the order id from the URL path
    // Run all three calls at the same time; allSettled never throws, it reports each outcome
    const [order, restaurant, rating] = await Promise.allSettled([
      getOrder(id),                             // required data
      getRestaurant(id),                        // useful data
      getRating(id),                            // optional data
    ]);

    if (order.status === "rejected") {          // the order is required, so stop here
      return res.status(404).json({ error: "order not found" }); // send 404 with a message
    }

    res.json({                                  // send the combined summary as JSON
      order: order.value,                       // the order data
      restaurant: restaurant.status === "fulfilled" ? restaurant.value : null, // null if it failed
      rating: rating.status === "fulfilled" ? rating.value : null,            // null if it failed
    });
  } catch (err) {                               // any unexpected error ends up here
    next(err);                                  // hand it to Express's error middleware
  }
});

app.listen(3000, () => console.log("Summary API on 3000")); // start listening
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Using `forEach` with an `async` callback
✅ Correct: `forEach` ignores the promises returned by its callback. Use `for...of` for series, or `Promise.all` with `map` for parallel.

```javascript
// Wrong: forEach does not wait, so "all saved" prints before any save
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms)); // wait ms milliseconds
const ids = [1, 2, 3];                          // ids to save
ids.forEach(async (id) => { await delay(10); console.log("saved", id); }); // callbacks are not awaited
console.log("all saved");                       // Expected output: all saved (printed first)
```

```javascript
// Right: for...of inside an async function waits for each save before the next one
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms)); // wait ms milliseconds
const ids = [1, 2, 3];                          // ids to save
(async () => {                                  // async IIFE so we can await inside
  for (const id of ids) { await delay(10); console.log("saved", id); } // one by one
  console.log("all saved");                     // Expected output: saved 1, saved 2, saved 3, all saved
})();
```

❌ **Mistake 2:** Creating promises early and calling it "series"
✅ Correct: a promise starts running the moment it is created. Store a function instead, and call it only when you want the work to start.

```javascript
// Wrong: both works start immediately, even though we await them one after another later
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms)); // value after ms
const work = (name) => { console.log("start", name); return delay(50, name); }; // logs when CALLED
const p1 = work("A");                           // A starts now
const p2 = work("B");                           // B also starts now (no waiting)
(async () => {
  console.log("got", await p1);                 // Expected output: start A, start B, got A, got B
  console.log("got", await p2);                 // Expected output: got B (printed last)
})();
```

```javascript
// Right: calling work() inside the async function starts each one only after the previous finishes
const delay = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms)); // value after ms
const work = (name) => { console.log("start", name); return delay(50, name); }; // logs when CALLED
(async () => {
  console.log("got", await work("A"));          // Expected output: start A, got A
  console.log("got", await work("B"));          // Expected output: start B, got B
})();
```

---

## 🧠 Tricky Interview Question
```javascript
const delay = (ms) => new Promise((r) => setTimeout(r, ms)); // wait ms milliseconds

[1, 2, 3].forEach(async (n) => {               // forEach runs the callback three times
  await delay(10);                              // each callback waits 10 ms
  console.log("forEach", n);                    // logs after its own wait
});

console.log("after forEach");                   // runs right away, before any timer fires
```
Answer:
```
after forEach
forEach 1
forEach 2
forEach 3
```
`forEach` calls each async callback and then ignores the promises they return, so the synchronous `console.log("after forEach")` runs first. The three timers were created in order and all last 10 ms, so Node fires them in creation order, and the logs come out as 1, 2, 3. Interviewers ask this because it looks like a loop that waits, but it does not.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between series and parallel async execution?**
A1: Series starts a task only after the previous one finishes, so total time is the sum of all durations. Parallel starts all tasks together, so total time is roughly the longest single task. Use series when tasks depend on each other or share a lock, and parallel when they are independent.

**Q2: How does `Promise.all` keep results in order when tasks finish at different times?**
A2: `Promise.all` stores each result at the index of its promise in the input array, not in the order of completion. The output array always matches the input order.

**Q3: Why does `forEach(async ...)` not work for sequential awaits?**
A3: `forEach` does not look at the return value of its callback. The promises are created, but nothing waits for them. Use `for...of` with `await`, or `Promise.all(arr.map(async ...))` for parallel work.

**Q4: How do you limit concurrency to N tasks at a time?**
A4: Start N runner functions. Each runner takes the next unclaimed index from a shared counter, awaits the work, and repeats until there are no items left. `mapLimit` in the advanced example does this, and it keeps the results in input order.

**Q5: When do you use `Promise.all`, `Promise.allSettled`, and `Promise.race`?**
A5: `Promise.all` is for "all must succeed" and rejects on the first failure. `Promise.allSettled` waits for every task and reports each outcome, which suits optional data. `Promise.race` settles with the first task to finish, which suits timeouts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tasks are independent and you want the total time to be the longest task, not the sum (parallel)
- Each step needs the previous step's result or a shared lock (series)
- You process a large list and must cap the load on a server or API (concurrency limit)

❌ Avoid when:
- Tasks depend on each other but you run them in parallel anyway (wrong results)
- You start 10,000 requests with `Promise.all` and no limit (rate limits, memory spikes)
- You need to process a huge stream; use an async iterator or a queue, not an array of promises

---

## 📊 Visual Diagram
```
Series:    A (300ms) -> B (100ms) -> C (200ms)      total = 600ms
Parallel:  A (300ms)                              total = 300ms (longest)
           B (100ms)
           C (200ms)
Limit 2:   runner 1: job0(500) ----> job2(300) ----> job4(400)
           runner 2: job1(100) -> job3(200) ---->
           results array: always [r0, r1, r2, r3, r4] in input order
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Series | Tasks run one after another | एक के बाद एक चलना |
| Parallel | Tasks start together and are awaited together | सब एक साथ शुरू होना |
| Promise.all | Resolves with all values, rejects on first failure | सभी सफल हों तो सभी results, वरना पहली error |
| Promise.allSettled | Waits for all and reports each status | सबके नतीजे status के साथ |
| Concurrency limit | Maximum number of tasks running at once | एक समय पर चलने वाले tasks की सीमा |
| Runner | A loop that keeps taking work until none is left | काम उठाने वाला loop |
| Eager start | A promise starts running as soon as it is created | Promise बनते ही काम शुरू होना |

---

## ⚡ 3-Line Summary
English:
1. Series uses `for...of` with `await`; parallel uses `Promise.all` over `map`.
2. Pass functions, not promises, so each task starts only when you call it.
3. For large lists, cap concurrency with a runner pool like `mapLimit`, and keep results in input order.

Hindi:
1. Series में `for...of` और `await` चलता है; parallel में `map` के साथ `Promise.all` चलता है।
2. Promises की जगह functions दो, ताकि हर task तभी शुरू हो जब तुम उसे call करो।
3. बड़ी list के लिए runner pool (जैसे `mapLimit`) से concurrency सीमित करो, और results input के क्रम में रखो।

---

## ➡️ Next Topic
**192. Promise Chaining Problems** — now that you can run many async tasks, the next problem is how to pass results through a chain of `.then` steps, handle errors in the middle, and build retry and timeout helpers on top.
