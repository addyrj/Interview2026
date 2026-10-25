# 90. Concurrency vs Parallelism
# हिंदी में: Concurrency बनाम Parallelism — एक Thread में कई काम और कई Cores पर काम

---

## 🔵 Simple Definition (English)
Concurrency means handling many tasks in overlapping time, by switching between them while they wait (for I/O, timers, network). Parallelism means running several tasks at the same instant on different CPU cores. Node.js is concurrent on one thread by default, and it becomes parallel only when you use multiple threads or processes.

## 🔵 सरल परिभाषा (Hindi)
Concurrency का मतलब है कई कामों को एक ही समय के दायरे में संभालना, जब कोई काम इंतज़ार (I/O, timers, network) कर रहा हो तो दूसरे पर जाना। Parallelism का मतलब है कई कामों को एक ही पल में अलग-अलग CPU cores पर चलाना। Node.js डिफ़ॉल्ट रूप से एक thread पर concurrent है, और सिर्फ तब parallel बनता है जब आप कई threads या processes इस्तेमाल करो।

---

## 🔴 Problem it Solves
A web server must handle thousands of users at once. If it used one thread per request (like old Java servers), each thread would sit idle while waiting for the database. Memory and context switching would grow fast. Node.js solves this with one thread and an event loop, so waiting work does not block others. But CPU-heavy work (image resizing, encryption, big JSON parsing) still blocks that single thread, so it needs real parallelism through worker threads or cluster.

## 🔴 यह क्यों बना? (Hindi)
Web server को एक साथ हज़ारों users संभालने होते हैं। अगर हर request के लिए एक thread हो (जैसे पुराने Java servers), तो हर thread database का इंतज़ार करते हुए खाली बैठा रहता है, और memory व context switching बहुत बढ़ जाती है। Node.js एक thread और event loop से यह हल करता है, ताकि इंतज़ार करता हुआ काम दूसरों को न रोके। पर CPU-heavy काम (image resize, encryption, बड़ा JSON parse) अभी भी उस एक thread को रोकता है, इसलिए उसे worker threads या cluster से असली parallelism चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 → Node.js runs your JavaScript on one main thread (the event loop)
Step 2 → When code calls I/O (fetch, DB, file read), Node hands the work to the OS or a thread pool and continues
Step 3 → When the I/O finishes, its callback or promise is queued, and the event loop runs it
Step 4 → So many requests are in progress at once (concurrency), but only one JS callback runs at a time
Step 5 → CPU-heavy JS code keeps the main thread busy, so timers and other requests wait
Step 6 → Worker threads run JS on other cores (true parallelism) and talk to the main thread with messages

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Node.js आपका JavaScript एक main thread (event loop) पर चलाता है
Step 2 → Code जब I/O (fetch, DB, file read) call करता है, तो Node काम OS या thread pool को दे देता है और आगे बढ़ता है
Step 3 → I/O खत्म होने पर उसका callback या promise queue में जाता है, और event loop उसे चलाता है
Step 4 → इस तरह बहुत सारी requests एक साथ चलती हैं (concurrency), पर एक समय पर सिर्फ एक JS callback चलता है
Step 5 → CPU-heavy JS code main thread को व्यस्त रखता है, इसलिए timers और बाकी requests इंतज़ार करते हैं
Step 6 → Worker threads दूसरे cores पर JS चलाते हैं (असली parallelism) और messages से main thread से बात करते हैं

---

## 🟡 Real World Example
A Paytm or Razorpay server receives 5,000 payment-status requests per second. Almost all of the time is spent waiting for the bank API and the database, so one Node.js process handles them concurrently. But a nightly job that generates PDF invoices for 2 lakh orders is CPU-heavy. Running it on the main thread would freeze payment requests, so it runs on worker threads, one per core, in parallel.

## 🟡 Real Example Hindi mein
Paytm या Razorpay के server पर हर सेकंड 5,000 payment-status requests आती हैं। ज़्यादातर समय वे bank API और database का इंतज़ार करती हैं, इसलिए एक Node.js process इन्हें concurrently संभाल लेता है। पर रात का एक job जो 2 लाख orders के PDF invoices बनाता है, CPU-heavy है। उसे main thread पर चलाने से payment requests रुक जाएँगी, इसलिए वह worker threads पर, हर core पर एक, parallel में चलता है।

---

## 💻 Code Example — Basic
```javascript
// Concurrency on ONE thread: tasks wait (I/O simulated by timers) and overlap in time.

// Helper: resolves after ms (stands in for network or disk waiting)
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// A download task: starts, waits (thread is free while waiting), then finishes
async function download(name, ms) {
  console.log(`${name} started`);              // runs right away when called
  await delay(ms);                             // thread is free here; other tasks run
  console.log(`${name} finished after ${ms}ms`); // runs when its timer fires
}

(async () => {
  // Both tasks are in progress at the same time on ONE thread (concurrency)
  await Promise.all([
    download("file-A", 200),                   // slower task
    download("file-B", 100),                   // faster task
  ]);
  console.log("all downloads done");           // after both complete
})();
```

**Expected output (basic):**
```
file-A started
file-B started
file-B finished after 100ms
file-A finished after 200ms
all downloads done
```

## 💻 Code Example — Advanced
```javascript
// Advanced: (1) a busy loop blocks the event loop, (2) worker threads give real parallelism.
const { Worker } = require("worker_threads");        // built-in module for worker threads

// Part 1: CPU work on the main thread blocks timers (no parallelism here)
const start = Date.now();                             // mark the start time
setTimeout(() => console.log("timer fired"), 0);      // wants to run as soon as possible
while (Date.now() - start < 100) {}                   // busy loop: holds the thread for 100ms
console.log("busy loop finished");                    // prints BEFORE the timer callback

// Part 2: the same kind of CPU work on two worker threads at the same time
// Each worker sums a range of numbers; the code runs as a string in a separate thread
const workerCode = `
  const { parentPort, workerData } = require("worker_threads");  // worker-side imports
  let sum = 0;                                         // running total in this worker
  for (let i = workerData.from; i <= workerData.to; i++) {       // sum the assigned range
    sum += i;                                          // add each number
  }
  parentPort.postMessage(sum);                         // send the result back to main
`;

// Helper: start one worker for a range and resolve with its sum
function sumRange(from, to) {
  return new Promise((resolve, reject) => {           // promise for the worker's result
    const worker = new Worker(workerCode, {           // create a worker thread from code
      eval: true,                                     // treat the string as JavaScript code
      workerData: { from, to },                       // data passed to the worker
    });
    worker.once("message", resolve);                  // first message is the sum
    worker.once("error", reject);                     // error inside the worker
  });
}

// Main: split 1..3,000,000 into two halves and run both at once
const N = 3000000;                                    // total numbers
(async () => {
  const [a, b] = await Promise.all([                  // both workers run in parallel
    sumRange(1, N / 2),                               // first half on core 1
    sumRange(N / 2 + 1, N),                           // second half on core 2
  ]);
  const total = a + b;                                // combine the two partial sums
  const formula = (N * (N + 1)) / 2;                  // closed-form check: n(n+1)/2
  console.log("parallel total:", total);              // 4500001500000
  console.log("matches formula:", total === formula); // true
})();
```

**Expected output (advanced):**
```
busy loop finished
timer fired
parallel total: 4500001500000
matches formula: true
```

---

## 🟠 Express.js Integration
An Express route that makes several independent I/O calls should run them concurrently with `Promise.all`, so the response takes as long as the slowest call, not the sum. A CPU-heavy route (like hashing or PDF generation) should move work to a worker thread, so other requests are not delayed.

```javascript
// Express.js example: concurrency for I/O, a worker for CPU work
const express = require("express");                 // import Express
const { Worker } = require("worker_threads");       // built-in worker threads
const app = express();                              // create the app

// Fake I/O calls (in a real app: database and bank API calls)
const getOrder = (id) => new Promise((r) => setTimeout(() => r({ id, total: 499 }), 100));
const getBankStatus = (id) => new Promise((r) => setTimeout(() => r({ id, status: "paid" }), 150));

app.get("/orders/:id/summary", async (req, res, next) => {
  try {
    const id = req.params.id;                       // order id from the URL
    // Concurrency: both I/O calls run at the same time (about 150ms, not 250ms)
    const [order, bank] = await Promise.all([getOrder(id), getBankStatus(id)]);
    res.json({ ...order, bankStatus: bank.status }); // combine and respond
  } catch (err) {
    next(err);                                      // any failure goes to error middleware
  }
});

// CPU-heavy route: run work in a worker thread so the event loop stays free
app.get("/invoices/:id/pdf-size", (req, res, next) => {
  const worker = new Worker(                        // start a worker for this job
    `const { parentPort } = require("worker_threads");
     let x = 0; for (let i = 0; i < 5e7; i++) x += i;  // heavy loop (stands in for PDF work)
     parentPort.postMessage(x);`,
    { eval: true }                                  // run the string as code
  );
  worker.once("message", (value) => res.json({ id: req.params.id, check: value })); // reply
  worker.once("error", next);                       // worker failure -> error middleware
});

app.listen(3000);                                   // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Thinking `Promise.all` runs code in parallel on multiple cores
✅ **Correct:** `Promise.all` gives concurrency on one thread. Only worker threads or processes run JS in parallel.

```javascript
// Wrong belief: "these 4 CPU-heavy functions run on 4 cores"
await Promise.all([hashPassword(a), hashPassword(b), hashPassword(c), hashPassword(d)]);
// Each function is synchronous CPU work, so they run one after another on the main thread

// Right: move the CPU work to workers (or use a library that does it in the libuv thread pool)
```

❌ **Mistake 2:** Running a long CPU loop on the main thread in an HTTP handler
✅ **Correct:** Move the heavy work to a worker thread, or split it into small chunks with `setImmediate`.

```javascript
// Wrong: all other requests wait while this loop runs
app.get("/report", (req, res) => {
  let total = 0;
  for (let i = 0; i < 1e9; i++) total += i;   // blocks the event loop for seconds
  res.json({ total });
});

// Right: offload to a worker (see the Express example above)
```

❌ **Mistake 3:** Starting many workers for tiny tasks
✅ **Correct:** Creating a worker has a startup cost. Reuse workers (a pool) for many small jobs, and use workers only for CPU-heavy work.

```javascript
// Wrong: one new worker per tiny request costs more than the work itself
const w = new Worker(code, { eval: true });

// Right: keep a pool of N workers and send jobs to free ones
```

---

## 🧠 Tricky Interview Output Question
```javascript
const start = Date.now();

setTimeout(() => console.log("A", Date.now() - start >= 50), 50);  // due at 50ms

while (Date.now() - start < 200) {}                 // busy 200ms on the main thread

setTimeout(() => console.log("B"), 0);              // due at about 200ms + 1ms
Promise.resolve().then(() => console.log("C"));     // microtask
console.log("D");                                   // synchronous
```
**Answer:**
```
D
C
A true
B
```
**Why:** `D` is synchronous code, so it prints first. After the script finishes, Node runs microtasks before any timer, so `C` prints next. Then the event loop runs timers. Both timers are overdue by the time the loop gets to them, because the busy loop blocked the thread for 200ms. Node runs expired timers in order of their due time: `A` was due at 50ms, and `B` was scheduled after the busy loop, so it is due at about 201ms. Therefore `A true` prints before `B`. Blocking the thread delays every timer, but it does not change the order in which they were due.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between concurrency and parallelism?
A1: Concurrency is managing many tasks in overlapping time, switching when one waits. Parallelism is running tasks at the same instant on multiple cores. Node.js is concurrent on one thread by default.

Q2: Is Node.js single-threaded?
A2: The JavaScript code runs on one main thread, but Node uses other threads internally (libuv thread pool for file system, DNS, and crypto work). You get true JS parallelism only with `worker_threads` or `cluster`.

Q3: Why does `Promise.all` not make CPU work faster?
A3: Each CPU-bound function runs to completion on the same thread before the next one starts. `Promise.all` only helps when the tasks spend time waiting for I/O.

Q4: When should you use worker threads?
A4: For CPU-heavy work that would block the event loop: image processing, encryption, large parsing, or heavy calculations. Avoid them for I/O, since I/O is already concurrent.

Q5: What is the difference between `worker_threads` and `cluster`?
A5: `cluster` starts multiple processes that share a server port, mainly for handling more HTTP requests across cores. `worker_threads` runs JS in threads inside one process and can share memory through `SharedArrayBuffer`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your app waits on I/O (database, HTTP, files), so concurrency handles many requests with one thread
- You have CPU-heavy tasks that must not block other requests (use worker threads)
- You want to use all CPU cores for a web server (use `cluster` or a process manager like PM2)

❌ Avoid when:
- The work is tiny; the overhead of threads or processes is bigger than the work
- You assume `Promise.all` will speed up CPU work
- You need shared mutable state across workers without careful synchronization

---

## 📊 Visual Diagram
```
CONCURRENCY (one thread, many waits overlap)

  time ─────────────────────────────────────────────────────►
  Main thread:  [start A][start B]·····[B done][A done]
  file-A:       ├───────── waiting (I/O) ──────────┤
  file-B:       ├──── waiting (I/O) ────┤

PARALLELISM (several threads, same instant)

  Core 1:  [ sum 1..1.5M      ]
  Core 2:  [ sum 1.5M..3M     ]   ──► total = a + b
  Main:    [ waits for both messages ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Concurrency | Many tasks progressing in overlapping time | कई कामों का एक ही समय के दायरे में आगे बढ़ना |
| Parallelism | Tasks running at the same instant on cores | एक ही पल में कई cores पर काम |
| Event loop | Loop that runs callbacks when work is ready | तैयार callbacks चलाने वाला loop |
| I/O-bound | Work that spends time waiting for the outside world | बाहरी दुनिया का इंतज़ार करने वाला काम |
| CPU-bound | Work that keeps the processor busy | Processor को व्यस्त रखने वाला काम |
| `worker_threads` | Node module for JS in separate threads | अलग threads में JS चलाने वाला module |
| `cluster` | Node module for multiple processes sharing a port | एक port साझा करने वाले कई processes |
| Blocking | A long sync task that delays everything else | लंबा sync काम जो बाकी सब रोक दे |

---

## ⚡ 3-Line Summary
**English:**
1. Concurrency overlaps waiting; Node.js does it on one thread, which suits I/O-heavy servers.
2. Parallelism runs code at the same instant on many cores; in Node you need `worker_threads` or `cluster`.
3. `Promise.all` gives concurrency, not CPU parallelism, so move heavy CPU work to workers.

**Hindi:**
1. Concurrency इंतज़ार को आपस में मिलाता है; Node.js यह एक thread पर करता है, जो I/O-heavy servers के लिए सही है।
2. Parallelism एक ही पल में कई cores पर code चलाता है; Node में इसके लिए `worker_threads` या `cluster` चाहिए।
3. `Promise.all` concurrency देता है, CPU parallelism नहीं, इसलिए भारी CPU काम को workers पर ले जाओ।

---

## ➡️ Next Topic
**Event Loop in depth (next topic in the Node.js async section)** — With the async model clear, study the event loop phases (timers, poll, `setImmediate`, microtasks), which explain the exact order of output you saw in this topic.
