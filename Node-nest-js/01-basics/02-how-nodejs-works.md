# 02. How Node.js Works
# हिंदी में: Node.js कैसे काम करता है?

---

## 🔵 Simple Definition (English)
Node.js works by running your JavaScript on **V8** (which executes synchronous code) while handing off all I/O operations (file, network, DB) to **libuv**, which manages a background **Event Loop** and a **thread pool**. When an async operation finishes, its callback is queued and picked up by the Event Loop on the single JS thread.

## 🔵 सरल परिभाषा (Hindi)
Node.js आपका JavaScript **V8** पर चलाता है (sync code execute करता है) और सारे I/O operations (file, network, DB) **libuv** को दे देता है, जो background में **Event Loop** और **thread pool** manage करता है। Async operation पूरा होने पर उसका callback queue में जाता है और single JS thread पर Event Loop उसे उठाता है।

---

## 🔴 Problem it Solves
Before understanding "how Node works," developers coming from Java/PHP assume: "one request = one thread, thread waits for I/O." That model wastes memory and limits concurrency. Node needed a mechanism to handle thousands of connections with ONE thread — the answer is: never let the JS thread wait. Every I/O call registers a callback and returns immediately; a separate native layer (libuv) does the actual waiting.

## 🔴 यह क्यों बना? (Hindi)
Java/PHP background वाले developers सोचते हैं: "एक request = एक thread, thread I/O का wait करता है।" यह model memory waste करता है और concurrency limit करता है। Node को एक तरीका चाहिए था जिससे एक ही thread हज़ारों connections handle कर सके — solution: JS thread को कभी wait मत करने दो। हर I/O call callback register करके तुरंत return हो जाता है; असली waiting libuv (native layer) करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Your `.js` file is loaded; V8 parses and compiles it to bytecode/machine code (JIT).
Step 2 → Top-level (synchronous) code executes immediately on the single JS thread — this is the "main script run."
Step 3 → Any async API call (`fs.readFile`, `http.get`, `setTimeout`, DB query) is registered with libuv and the call returns immediately — code does NOT wait here.
Step 4 → libuv either uses OS-level async mechanisms (epoll/kqueue/IOCP for network) or delegates to its internal **thread pool** (for fs, DNS, crypto, zlib) to actually perform the work in the background.
Step 5 → Once the operation finishes, its callback/promise resolution is placed into the appropriate **Event Loop phase queue** (timers, pending callbacks, poll, check, close).
Step 6 → The **Event Loop**, running on the single JS thread, cycles through its phases, and when it reaches a phase with a ready callback, it executes that callback — synchronously, to completion, before moving to the next callback.
Step 7 → This cycle (Steps 3–6) repeats until there is no more code to run and no more pending timers/I/O — then the process exits.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → आपकी `.js` file load होती है; V8 उसे parse और compile करता है (JIT)।
Step 2 → Top-level synchronous code तुरंत single JS thread पर run होता है।
Step 3 → कोई भी async call (`fs.readFile`, `http.get`, `setTimeout`, DB query) libuv के पास register होती है और call तुरंत return हो जाती है — यहाँ wait नहीं होता।
Step 4 → libuv OS-level async mechanism (epoll/kqueue/IOCP, network के लिए) use करता है या अपने **thread pool** (fs, DNS, crypto, zlib के लिए) में काम भेजता है।
Step 5 → काम पूरा होने पर उसका callback Event Loop की सही phase queue में रखा जाता है (timers, pending callbacks, poll, check, close)।
Step 6 → **Event Loop** single JS thread पर अपनी phases घूमता है, और जहाँ callback ready मिलता है उसे पूरा run करता है, अगले callback से पहले।
Step 7 → यह cycle (Step 3–6) तब तक चलता है जब तक कोई code या pending timer/I/O बाकी न रहे — फिर process exit हो जाता है।

---

## 🟡 Real World Example
**Zomato restaurant search API:** When 10,000 users search restaurants simultaneously, each request triggers a DB query (via `pg` or `mongoose`). Node.js doesn't spin up 10,000 threads — it fires all 10,000 queries async, the single JS thread moves on to accept more requests, and as each DB response arrives, libuv queues the callback. The Event Loop processes each response and sends the JSON back. This is why a 2-core Node server can outperform a 2-core thread-per-request server under heavy I/O load.

## 🟡 Real Example Hindi mein
**Zomato restaurant search API:** जब 10,000 users एक साथ restaurant search करते हैं, हर request एक DB query trigger करती है। Node.js 10,000 threads नहीं बनाता — सारी queries async fire होती हैं, single JS thread और requests accept करता रहता है, और जैसे ही DB response आता है, libuv callback को queue करता है। Event Loop हर response process करके JSON भेजता है। इसलिए एक 2-core Node server, heavy I/O load में thread-per-request server से बेहतर perform कर सकता है।

---

## 💻 Code Example — Basic
```javascript
// how-nodejs-works-basic.js
// Demonstrates: sync code runs first, async callbacks run later, order matters

const fs = require('fs');

console.log('1: Start of script');          // runs immediately (sync)

// This schedules a callback for "later" — code does NOT wait here
fs.readFile(__filename, 'utf8', (err, data) => {
  console.log('4: File read complete, length =', data.length); // runs LAST (async callback)
});

setTimeout(() => {
  console.log('3: Timer fired after 0ms');  // runs after sync code, in timers phase
}, 0);

console.log('2: End of script (sync code)'); // runs immediately (sync)

// Expected output order: 1, 2, 3, 4 (roughly — fs callback usually after timer)
// This PROVES Node.js does not block on readFile; it schedules and moves on.
```

## 💻 Code Example — Advanced
```javascript
// how-nodejs-works-advanced.js
// Shows: thread pool usage via crypto, and measuring concurrency

const crypto = require('crypto');
const { performance } = require('perf_hooks');

// pbkdf2 is CPU-heavy and runs on libuv's THREAD POOL (default 4 threads)
function hashPasswordAsync(password) {
  return new Promise((resolve, reject) => {
    // 100000 iterations — deliberately heavy to show thread pool behavior
    crypto.pbkdf2(password, 'salt', 100000, 64, 'sha512', (err, derivedKey) => {
      if (err) return reject(err);
      resolve(derivedKey.toString('hex'));
    });
  });
}

async function demo() {
  const start = performance.now();

  // Fire 4 hashing operations in parallel — all 4 fit in the default thread pool
  // so they run roughly at the SAME time (not one after another)
  const results = await Promise.all([
    hashPasswordAsync('user1-pass'),
    hashPasswordAsync('user2-pass'),
    hashPasswordAsync('user3-pass'),
    hashPasswordAsync('user4-pass'),
  ]);

  console.log('4 hashes done in', (performance.now() - start).toFixed(1), 'ms');
  console.log('Hash sample:', results[0].slice(0, 16), '...');

  // A 5th call would have to WAIT for a free thread pool slot (default size = 4)
  // Fix in production: process.env.UV_THREADPOOL_SIZE = 8 (set BEFORE any libuv call)
}

demo().catch((err) => console.error('Hashing failed:', err));
```

---

## 🟠 Express.js Integration
```javascript
// Express request handling shows Node's non-blocking model in action
const express = require('express');
const app = express();

app.get('/order/:id', async (req, res) => {
  console.log(`Request received for order ${req.params.id}`);

  // Simulates an async DB call — Event Loop is FREE to serve other
  // requests while this "await" is pending (no thread is blocked)
  const order = await fakeDbLookup(req.params.id);

  res.json(order);
});

function fakeDbLookup(id) {
  return new Promise((resolve) => {
    setTimeout(() => resolve({ id, status: 'preparing', eta: '20 mins' }), 300);
  });
}

// Even with a 300ms "DB delay" per request, this server can handle thousands
// of concurrent /order/:id requests because the Event Loop never blocks on I/O
app.listen(3000, () => console.log('Zomato-style order API on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming Node.js is fully single-threaded (including I/O)
✅ Correct: Only JS execution is single-threaded. libuv uses a thread pool for fs/crypto/dns/zlib, and the OS kernel handles network I/O asynchronously.

```javascript
// Wrong assumption: "there's only one thread doing everything"
// Right understanding:
console.log(process.env.UV_THREADPOOL_SIZE || 4); // default thread pool size for fs/crypto/dns
```

❌ Mistake 2: Writing long synchronous CPU loops inside request handlers, blocking the Event Loop for everyone
```javascript
// Wrong — blocks Event Loop for ALL connected clients
app.get('/report', (req, res) => {
  let sum = 0;
  for (let i = 0; i < 10_000_000_000; i++) sum += i; // freezes server
  res.json({ sum });
});

// Right — offload CPU work to a worker_thread, keep Event Loop free
const { Worker } = require('worker_threads');
app.get('/report', (req, res) => {
  const worker = new Worker('./heavy-sum-worker.js');
  worker.on('message', (sum) => res.json({ sum }));
});
```

---

## 🧠 Tricky Interview Question

```javascript
console.log('A');

setTimeout(() => console.log('B'), 0);

fs.readFile(__filename, () => console.log('C'));

Promise.resolve().then(() => console.log('D'));

console.log('E');
```
Answer: Output is `A, E, D, B, C` (order of B/C can vary by OS, but D always comes before B and C). Reasoning: `A` and `E` are synchronous, so they run first. Microtasks (Promise `.then`) run before the next Event Loop phase, so `D` runs next. Then the Event Loop proceeds to the **timers** phase (`setTimeout` → `B`) before the **poll** phase where fs I/O callbacks (`C`) land — on most systems timers phase is visited before poll for a 0ms timer registered early, giving `B` before `C`, but this is not 100% guaranteed across all platforms.

---

## ⚫ Interview Questions + Answers

Q1: Does Node.js ever use multiple threads?
A1: Yes. JavaScript execution itself is single-threaded, but Node relies on libuv's thread pool (default 4, tunable via `UV_THREADPOOL_SIZE`) for fs, DNS lookups, crypto, and zlib, plus you can spawn explicit OS threads via `worker_threads` for CPU-heavy work.

Q2: What exactly does the Event Loop do?
A2: It's a loop with distinct phases (timers → pending callbacks → poll → check → close callbacks) that continuously checks for completed async operations and runs their callbacks on the single JS thread, one at a time, to completion.

Q3: What's the difference between the "call stack," "task queue," and "microtask queue"?
A3: The call stack runs synchronous JS code right now. The microtask queue (Promises, `queueMicrotask`) is drained completely after the current stack empties, before the Event Loop moves to the next phase. The macrotask/task queue (timers, I/O callbacks) is processed one task per Event Loop phase.

Q4: Why does a single `setTimeout(fn, 0)` not always run exactly at 0ms?
A4: It's scheduled for the earliest moment the Event Loop reaches the "timers" phase, but the Event Loop must first finish the current phase and drain the microtask queue — so there's always some delay, often a few ms minimum.

Q5: How does Node.js achieve high throughput with only one JS thread?
A5: By never blocking that thread on I/O. All I/O is delegated to libuv (via OS async APIs or the thread pool), and results come back as callbacks. Since most server work is I/O-bound (waiting on DB/network), the thread spends almost all its time doing useful JS work, not waiting.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building I/O-heavy APIs (REST, GraphQL) that mostly wait on DB/network calls
- Real-time apps needing many concurrent lightweight connections (chat, live tracking)

❌ Avoid when:
- The workload is CPU-bound and sustained (video transcoding, heavy ML inference) — use worker_threads, or a different runtime like Go/Rust for the hot path

---

## 📊 Visual Diagram
```
REQUEST LIFECYCLE IN NODE.JS
─────────────────────────────────────────────
  Client Request
        │
        ▼
  ┌─────────────┐
  │  JS Thread   │ ── runs handler code synchronously
  │  (V8)        │     until it hits an async call
  └──────┬───────┘
         │  fs.readFile() / db.query() / http.get()
         ▼
  ┌─────────────────────┐
  │   libuv              │
  │  ┌────────────────┐  │
  │  │ OS async I/O    │  │  (network via epoll/kqueue/IOCP)
  │  └────────────────┘  │
  │  ┌────────────────┐  │
  │  │ Thread Pool (4) │  │  (fs, dns, crypto, zlib)
  │  └────────────────┘  │
  └──────────┬───────────┘
             │  operation done → callback queued
             ▼
  ┌─────────────────────┐
  │   EVENT LOOP          │  picks callback, runs on JS thread
  │  timers→poll→check    │
  └──────────┬───────────┘
             ▼
     Response sent to client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event Loop | Mechanism that picks and runs ready callbacks | Ready callbacks चुनकर run करने वाला mechanism |
| Thread Pool | Pool of OS threads libuv uses for fs/crypto/dns | fs/crypto/dns के लिए libuv का thread pool |
| Call Stack | Where synchronous JS currently executes | जहाँ sync JS execute होता है |
| Microtask | Promise callbacks, run before next Event Loop phase | Promise callbacks, next phase से पहले run |
| Macrotask | Timer/I/O callbacks, one per Event Loop phase | Timer/I/O callbacks |
| JIT | Just-In-Time compilation of JS to machine code | JS को machine code में तुरंत compile करना |
| UV_THREADPOOL_SIZE | Env var to resize libuv thread pool | Thread pool size बदलने वाला env var |

---

## ⚡ 3-Line Summary
English:
1. Node.js runs your synchronous JS on one V8 thread, while delegating all I/O to libuv's Event Loop and thread pool.
2. Async operations register a callback and return immediately; libuv does the actual waiting/work in the background (OS async APIs or thread pool).
3. The Event Loop continuously picks up completed callbacks and runs them on the JS thread — this is why Node scales well for I/O-bound workloads but poorly for sustained CPU-bound work.

Hindi:
1. Node.js आपका sync JS एक V8 thread पर run करता है, और सारा I/O libuv के Event Loop और thread pool को दे देता है।
2. Async operation callback register करके तुरंत return हो जाता है; असली wait/काम libuv background में करता है (OS async APIs या thread pool)।
3. Event Loop लगातार पूरे हुए callbacks उठाकर JS thread पर run करता है — इसलिए Node I/O-heavy workload में अच्छा scale करता है पर लगातार CPU-heavy काम में कमज़ोर।

---

## ➡️ Next Topic
**03. Node.js vs Browser JavaScript** — Same language, completely different environment and APIs; understanding this boundary prevents confusion when moving between frontend and backend code.
