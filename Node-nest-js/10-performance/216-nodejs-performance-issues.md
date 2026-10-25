# 216. Node.js Performance Issues
# हिंदी में: Node.js Performance Issues — Overview और Common Bottlenecks

---

## 🔵 Simple Definition (English)
Node.js performance issues usually come from one of a few recurring causes: **blocking the single-threaded event loop** with synchronous/CPU-heavy code, **memory leaks** causing growing RAM usage and eventual crashes, **unoptimized database queries** (N+1, missing indexes), **too many small I/O calls** instead of batching, and **not using multiple CPU cores** (Node is single-threaded per process by default).

## 🔵 सरल परिभाषा (Hindi)
Node.js performance issues आम तौर पर इन कारणों से आती हैं: **single-threaded event loop को block करना** synchronous/CPU-heavy code से, **memory leaks** जो RAM usage बढ़ाते रहते हैं और crash कराते हैं, **unoptimized database queries** (N+1, missing indexes), **बहुत सारी छोटी I/O calls** batch किए बिना, और **multiple CPU cores use न करना** (Node default में per-process single-threaded है)।

---

## 🔴 Problem it Solves
Many Node.js apps start fast in development with light traffic, then degrade badly under production load — response times climb from 50ms to 5 seconds, memory usage grows until the process crashes (OOM), or the server can only use 1 of 8 available CPU cores leaving 87% of hardware idle. Understanding WHERE performance problems typically come from (event loop blocking, leaks, DB, I/O patterns, single-core usage) lets you diagnose systematically instead of guessing, and apply the right fix (worker threads, clustering, streaming, caching, query optimization) for the right problem.

## 🔴 यह क्यों बना? (Hindi)
बहुत सारे Node.js apps development में light traffic पर fast चलते हैं, फिर production load में बुरी तरह degrade हो जाते हैं — response time 50ms से 5 seconds तक पहुँच जाता है, memory usage बढ़ता रहता है जब तक process crash (OOM) न हो जाए, या server सिर्फ 8 में से 1 CPU core use कर पाता है बाकी 87% hardware idle रहता है। ये समझना कि performance problems कहाँ से आती हैं (event loop blocking, leaks, DB, I/O patterns, single-core usage) systematic diagnosis करने देता है, guess करने के बजाय।

---

## 🟢 How it Works — Step by Step

Step 1 → **Identify symptom**: slow response times? Growing memory over hours/days? High CPU on one core while others idle? Timeouts under load?
Step 2 → **Profile, don't guess**: use `node --prof`, Chrome DevTools, `clinic.js`, or APM tools (New Relic, Datadog) to find the actual bottleneck
Step 3 → **Match symptom to cause**: CPU spikes + slow everything → event loop blocked by sync code. Growing RSS memory → leak (listeners, caches, closures). Slow specific endpoint → check its DB queries (N+1, missing index)
Step 4 → **Apply the targeted fix**: move CPU-heavy work to worker threads/a queue, fix the leak source, add DB indexes/batch queries, enable clustering for multi-core
Step 5 → **Re-measure** after the fix to confirm improvement — performance work is iterative, not one-shot

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Symptom पहचानो**: slow response times? घंटों/दिनों में बढ़ता memory? एक CPU core पर high usage बाकी idle? Load में timeouts?
Step 2 → **Guess नहीं, Profile करो**: actual bottleneck ढूंढने के लिए `node --prof`, Chrome DevTools, `clinic.js`, या APM tools (New Relic, Datadog) use करो
Step 3 → **Symptom को cause से match करो**: CPU spike + सब कुछ slow → event loop sync code से blocked। बढ़ता RSS memory → leak (listeners, caches, closures)। खास endpoint slow → उसकी DB queries check करो
Step 4 → **Targeted fix apply करो**: CPU-heavy काम worker threads/queue में भेजो, leak का source ठीक करो, DB indexes/batch queries add करो, multi-core के लिए clustering enable करो
Step 5 → Fix के बाद **फिर से measure** करो improvement confirm करने के लिए

---

## 🟡 Real World Example
**Swiggy's order-status API started timing out under peak lunch-hour load.** Investigation found: (1) a synchronous `JSON.parse()` on a huge cached menu object blocking the event loop for 200ms per request, (2) an N+1 query fetching restaurant details one-by-one instead of a single batched query, and (3) the server running as a single Node process despite having 8 CPU cores available. Fixes: moved JSON parsing to a worker thread, batched the restaurant query with a single `WHERE id IN (...)`, and deployed with PM2 cluster mode across all 8 cores — P99 latency dropped from 4.2s to 180ms.

## 🟡 Real Example Hindi mein
**Swiggy का order-status API peak lunch-hour load में timeout होने लगा।** Investigation में मिला: (1) एक synchronous `JSON.parse()` बड़े cached menu object पर event loop को 200ms तक block कर रहा था, (2) एक N+1 query restaurant details को एक-एक करके fetch कर रही थी single batched query के बजाय, (3) server सिर्फ एक Node process के रूप में चल रहा था जबकि 8 CPU cores available थे। Fixes: JSON parsing worker thread में move किया, restaurant query को single `WHERE id IN (...)` से batch किया, PM2 cluster mode से सभी 8 cores पर deploy किया — P99 latency 4.2s से 180ms हो गई।

---

## 💻 Code Example — Basic

```javascript
// performance-killer.js — demonstrates a common event-loop-blocking mistake
const express = require('express');
const app = express();

// BAD: synchronous, CPU-heavy work directly in a request handler
app.get('/report', (req, res) => {
  let total = 0;
  // This loop blocks the ENTIRE event loop — no other request can be
  // processed anywhere in the app until this finishes!
  for (let i = 0; i < 5_000_000_000; i++) {
    total += i;
  }
  res.json({ total });
});

// While /report is running, even this simple endpoint becomes unresponsive:
app.get('/health', (req, res) => {
  res.json({ status: 'ok' }); // blocked behind /report's loop!
});

app.listen(3000);
// Test it: curl /report & then immediately curl /health
// /health will NOT respond until /report's loop finishes — proving blocking
```

```javascript
// measuring-event-loop-lag.js — a simple way to detect event loop blocking
// A healthy event loop processes this check every ~interval with minimal delay

let lastCheck = Date.now();
const INTERVAL_MS = 500;

setInterval(() => {
  const now = Date.now();
  const actualDelay = now - lastCheck;
  const lag = actualDelay - INTERVAL_MS; // how much extra delay beyond expected

  if (lag > 100) {
    // If lag is consistently high, something is blocking the event loop
    console.warn(`Event loop lag detected: ${lag}ms`);
  }
  lastCheck = now;
}, INTERVAL_MS);

// In production, use the `perf_hooks` module's monitorEventLoopDelay() instead:
const { monitorEventLoopDelay } = require('perf_hooks');
const histogram = monitorEventLoopDelay({ resolution: 20 });
histogram.enable();
setInterval(() => {
  console.log(`Event loop delay — mean: ${histogram.mean / 1e6}ms, max: ${histogram.max / 1e6}ms`);
  histogram.reset();
}, 5000);
```

## 💻 Code Example — Advanced

```javascript
// fixed-version.js — the SAME /report endpoint fixed with a worker thread
const express = require('express');
const { Worker } = require('worker_threads');
const path = require('path');

const app = express();

app.get('/report', (req, res) => {
  // Offload the CPU-heavy work to a worker thread — event loop stays free
  const worker = new Worker(path.join(__dirname, 'heavy-calc-worker.js'));

  worker.on('message', (total) => {
    res.json({ total });
    worker.terminate(); // clean up the worker after use
  });

  worker.on('error', (err) => {
    res.status(500).json({ error: err.message });
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' }); // now responds instantly even during /report!
});

app.listen(3000);
```

```javascript
// heavy-calc-worker.js — runs in a SEPARATE thread, doesn't block main event loop
const { parentPort } = require('worker_threads');

let total = 0;
for (let i = 0; i < 5_000_000_000; i++) {
  total += i;
}
// Send the result back to the main thread when done
parentPort.postMessage(total);

// ─── N+1 QUERY FIX EXAMPLE ──────────────────────────────────────────────────
// BAD: N+1 — one query per restaurant (if 50 orders, this is 50 extra queries!)
async function getOrdersWithRestaurantsBad(orderIds) {
  const orders = await Order.find({ _id: { $in: orderIds } });
  for (const order of orders) {
    order.restaurant = await Restaurant.findById(order.restaurantId); // N queries!
  }
  return orders;
}

// GOOD: batch into a SINGLE query using $in
async function getOrdersWithRestaurantsGood(orderIds) {
  const orders = await Order.find({ _id: { $in: orderIds } });
  const restaurantIds = orders.map(o => o.restaurantId);
  const restaurants = await Restaurant.find({ _id: { $in: restaurantIds } }); // 1 query!

  const restaurantMap = new Map(restaurants.map(r => [r._id.toString(), r]));
  orders.forEach(order => {
    order.restaurant = restaurantMap.get(order.restaurantId.toString());
  });
  return orders;
}
```

---

## 🟠 Express.js Integration

```javascript
// middleware/responseTime.js — measure and log slow requests in production
function responseTimeLogger(req, res, next) {
  const startTime = process.hrtime.bigint(); // high-precision timer

  res.on('finish', () => {
    const endTime = process.hrtime.bigint();
    const durationMs = Number(endTime - startTime) / 1_000_000;

    if (durationMs > 500) {
      // Log/alert on slow requests — these are your performance investigation leads
      console.warn(`SLOW REQUEST: ${req.method} ${req.path} took ${durationMs.toFixed(1)}ms`);
    }
  });
  next();
}

app.use(responseTimeLogger);

// Use clustering to utilize all CPU cores (fixes single-core bottleneck)
// cluster.js
const cluster = require('cluster');
const os = require('os');

if (cluster.isPrimary) {
  const numCPUs = os.cpus().length;
  for (let i = 0; i < numCPUs; i++) cluster.fork(); // one worker process per core
  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} died, restarting...`);
    cluster.fork(); // auto-restart on crash
  });
} else {
  require('./app'); // each worker runs the actual Express app
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Optimizing based on guesses instead of profiling data
```javascript
// WRONG: "I think the DB is slow" → spends days optimizing DB queries
// when the real bottleneck was a synchronous regex on every request

// CORRECT: profile first with --prof, Chrome DevTools, or clinic.js
// node --prof app.js → node --prof-process isolate-*.log > profile.txt
// Find the ACTUAL hot function before optimizing anything
```

❌ Mistake 2: Running a single Node process on a multi-core production server
```javascript
// WRONG: app.listen(3000) directly — only uses 1 of e.g. 8 CPU cores
require('./app').listen(3000);

// CORRECT: use cluster module or PM2 cluster mode to use all cores
// pm2 start app.js -i max   (uses all available CPU cores automatically)
```

---

## 🧠 Tricky Interview Question

```javascript
app.get('/slow', (req, res) => {
  const data = JSON.parse(fs.readFileSync('./huge-50mb-file.json')); // sync read + parse
  res.json({ count: data.length });
});
// ❓ Why does THIS single endpoint slow down ALL other unrelated endpoints
// on the same server, even ones with zero shared code?
```
Answer: Because Node.js runs JavaScript on a **single thread** sharing one event loop across the ENTIRE process. `fs.readFileSync()` (synchronous file read) and `JSON.parse()` on a 50MB file are both **blocking, CPU/IO-bound synchronous operations** that occupy the one JS thread completely. While this code runs, the event loop cannot process ANY other callback — not other requests, not timers, not other routes — regardless of whether they share code. The fix: use `fs.promises.readFile()` (non-blocking I/O) and, if `JSON.parse()` itself is the bottleneck on huge files, move it to a worker thread since `JSON.parse` has no async variant.

---

## ⚫ Interview Questions + Answers

Q1: What are the 5 most common categories of Node.js performance problems?
A1: (1) Event loop blocking (sync/CPU-heavy code in request handlers), (2) memory leaks (growing RAM, eventual OOM crash), (3) inefficient database access (N+1 queries, missing indexes, no connection pooling), (4) too many small I/O operations instead of batching/caching, (5) not utilizing multiple CPU cores (single process on a multi-core machine).

Q2: How do you measure event loop lag in production?
A2: Use `perf_hooks.monitorEventLoopDelay()` (built into Node) to get a histogram of actual vs expected event loop delay, or third-party APM tools (New Relic, Datadog, Clinic.js `clinic doctor`) that visualize event loop lag over time alongside CPU/memory metrics.

Q3: Why doesn't adding more CPU cores automatically make a single Node process faster?
A3: A single Node.js process is single-threaded for JS execution (regardless of how many CPU cores the machine has) — Node uses one core for your JS code by default (libuv's thread pool handles some async I/O separately, but your JS logic itself runs on one thread). To use multiple cores, you must explicitly fork multiple processes (via `cluster` module or PM2 `-i max`) or offload CPU work to `worker_threads`.

Q4: What's the difference between a CPU-bound and I/O-bound performance problem, and why does the fix differ?
A4: I/O-bound (DB queries, network calls, file reads) means the thread is WAITING, not computing — Node handles this efficiently via its non-blocking async I/O model; fixes focus on reducing round-trips, adding caching, batching queries. CPU-bound (heavy computation, large JSON parsing, image processing, crypto) means the thread is ACTIVELY BUSY computing and blocks everything else; fixes focus on offloading to worker threads, horizontal scaling (clustering), or algorithmic optimization.

Q5: What profiling tools would you use to diagnose a production Node.js performance issue?
A5: `node --prof` + `--prof-process` for a CPU profile, Chrome DevTools' `--inspect` flag for live CPU/memory profiling, `clinic.js` (`clinic doctor`, `clinic flame`) for visual flame graphs identifying hot functions, `0x` for flame graphs, and APM tools (New Relic, Datadog, AppDynamics) for continuous production monitoring with alerting on latency/memory trends.

---

## 🔷 When to Use + When Not to Use
✅ Use this diagnostic mindset when:
- Response times degrade under real production load but seem fine in dev/testing
- Memory usage grows steadily over hours/days (leak suspicion)
- Server has multiple CPU cores but CPU usage graph shows only ~12.5% (1 of 8 cores) utilized

❌ Don't prematurely optimize when:
- The app has low traffic and response times are already well within SLA — profiling/optimizing here wastes engineering time better spent on features
- You haven't profiled yet — never optimize based on assumption alone

---

## 📊 Visual Diagram
```
NODE.JS PERFORMANCE PROBLEM MAP:
──────────────────────────────────────────────────────────
Symptom                          →  Likely Cause           →  Fix
──────────────────────────────────────────────────────────
All endpoints slow together      →  Event loop blocked     →  Worker threads,
                                     by sync/CPU-heavy code     async I/O
Memory grows over hours/days     →  Memory leak             →  Fix listener/cache
                                     (listeners, caches)        leaks, heap snapshot
One endpoint consistently slow   →  Bad DB query (N+1,       →  Add index, batch
                                     missing index)              query, $in
CPU maxed on 1 core, others idle →  Single process, no       →  cluster module,
                                     multi-core usage            PM2 -i max
High latency under burst traffic →  No caching, repeated     →  Redis cache,
                                     expensive computation       memoization
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop blocking | Sync code freezing the whole process | Sync code से पूरा process freeze होना |
| Memory leak | Memory that's never freed, grows over time | कभी free न होने वाली memory |
| N+1 query | One query becomes N+1 due to loop | Loop की वजह से एक query N+1 बन जाना |
| Profiling | Measuring where time/memory is actually spent | असल में समय/memory कहाँ जा रहा measure करना |
| Clustering | Running multiple processes across CPU cores | CPU cores पर कई processes चलाना |
| Event loop lag | Delay beyond expected timer interval | Expected interval से ज़्यादा delay |

---

## ⚡ 3-Line Summary
English:
1. Node.js performance problems usually trace back to event loop blocking, memory leaks, bad DB queries, or underusing available CPU cores.
2. Always profile first (Chrome DevTools, clinic.js, `--prof`) to find the real bottleneck — never optimize based on guesses.
3. Match the fix to the cause: worker threads/async I/O for blocking, leak-hunting for memory, query batching/indexing for DB, clustering for multi-core utilization.

Hindi:
1. Node.js performance problems ज़्यादातर event loop blocking, memory leaks, गलत DB queries, या available CPU cores का कम इस्तेमाल से आती हैं।
2. हमेशा पहले profile करो (Chrome DevTools, clinic.js, `--prof`) असली bottleneck ढूंढने के लिए — कभी guess से optimize मत करो।
3. Fix को cause से match करो: blocking के लिए worker threads/async I/O, memory के लिए leak-hunting, DB के लिए query batching/indexing, multi-core के लिए clustering।

---

## ➡️ Next Topic
**217. Memory Leaks — How to Find + Fix** — Node.js apps में memory leaks के common causes और heap snapshots से उन्हें debug करना।
