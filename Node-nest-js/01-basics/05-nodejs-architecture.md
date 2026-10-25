# 05. Node.js Architecture
# हिंदी में: Node.js Architecture

---

## 🔵 Simple Definition (English)
Node.js architecture is a layered system: your **JavaScript code** sits on top of **V8** (executes JS), which is connected via **C++ bindings** to **libuv** (handles async I/O, Event Loop, thread pool), which talks to the **Operating System**. Together these layers let single-threaded JS achieve massive I/O concurrency.

## 🔵 सरल परिभाषा (Hindi)
Node.js architecture एक layered system है: आपका **JavaScript code** **V8** पर चलता है (JS execute करता है), जो **C++ bindings** के through **libuv** से जुड़ा है (async I/O, Event Loop, thread pool handle करता है), जो **Operating System** से बात करता है। ये सब layers मिलकर single-threaded JS को massive I/O concurrency देते हैं।

---

## 🔴 Problem it Solves
Building a server runtime from scratch requires solving: (1) how to run JS fast (V8 solves this), (2) how to do async I/O portably across Linux/macOS/Windows without rewriting for each OS (libuv solves this), (3) how to expose OS features like files/sockets to JS safely (C++ bindings solve this). Node.js architecture is the deliberate combination of these three solved problems into one coherent runtime, instead of reinventing each piece.

## 🔴 यह क्यों बना? (Hindi)
Server runtime को scratch से बनाने के लिए तीन चीज़ें solve करनी थीं: (1) JS को तेज़ कैसे चलाएं (V8 solve करता है), (2) Linux/macOS/Windows पर बिना अलग-अलग code लिखे async I/O कैसे करें (libuv solve करता है), (3) OS features (files/sockets) को JS तक सुरक्षित तरीके से कैसे पहुंचाएं (C++ bindings solve करते हैं)। Node.js architecture इन तीनों solved problems को एक साथ जोड़ता है, हर एक को दोबारा बनाने के बजाय।

---

## 🟢 How it Works — Step by Step

Step 1 → **Your JS code** calls a Node.js API, e.g., `fs.readFile()`.
Step 2 → This is a JS-level function that internally calls into **Node.js's internal bindings layer** (written in C++, exposed to JS via V8's native API).
Step 3 → The binding calls into **libuv**, which decides: is this network I/O (use OS epoll/kqueue/IOCP) or fs/DNS/crypto (use the **thread pool**)?
Step 4 → libuv performs the operation asynchronously — either the OS notifies it via its event notification system, or a thread pool worker completes the task.
Step 5 → The result is handed back through the binding layer into a JS callback, which is queued into the correct **Event Loop phase**.
Step 6 → The **Event Loop**, running continuously on the main JS thread, executes that callback when its phase is reached, running your JS to handle the result.
Step 7 → This entire architecture is bundled as the single `node` executable — you don't install V8 and libuv separately, Node.js compiles them together.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → आपका **JS code** कोई Node.js API call करता है, जैसे `fs.readFile()`।
Step 2 → यह JS function अंदर से Node.js के **internal bindings layer** (C++ में लिखा, V8 के native API से JS को मिलता है) को call करता है।
Step 3 → Binding **libuv** को call करता है, जो decide करता है: यह network I/O है (OS epoll/kqueue/IOCP use करो) या fs/DNS/crypto है (**thread pool** use करो)?
Step 4 → libuv operation को async perform करता है — OS event notify करता है या thread pool worker task पूरा करता है।
Step 5 → Result binding layer के through JS callback तक वापस आता है, जो सही **Event Loop phase** में queue होता है।
Step 6 → **Event Loop**, main JS thread पर लगातार चलते हुए, उस phase पर पहुँचते ही callback run करता है।
Step 7 → यह पूरा architecture एक ही `node` executable में bundled है — V8 और libuv अलग से install नहीं करने पड़ते, Node.js उन्हें साथ compile करता है।

---

## 🟡 Real World Example
**Amazon-style order microservice:** A single Node.js process handles order creation. The route handler (JS) calls `db.query()` (goes through driver bindings → libuv's thread pool or network socket), calls `redis.get()` (network I/O via libuv's event notification), and writes an audit log via `fs.appendFile()` (thread pool). All three operations run concurrently without blocking each other, all orchestrated by one Event Loop on one thread, while the architecture underneath (V8 + bindings + libuv + OS) handles the real parallel work.

## 🟡 Real Example Hindi mein
**Amazon-style order microservice:** एक Node.js process order creation handle करता है। Route handler (JS) `db.query()` call करता है (driver bindings → libuv thread pool या network socket से), `redis.get()` call करता है (libuv के event notification से network I/O), और `fs.appendFile()` से audit log लिखता है (thread pool)। तीनों operations बिना एक-दूसरे को block किए concurrently चलते हैं, सब एक Event Loop एक thread पर manage करता है, जबकि नीचे का architecture (V8 + bindings + libuv + OS) असली parallel काम करता है।

---

## 💻 Code Example — Basic
```javascript
// architecture-layers-demo.js
// Shows different "layers" of Node's architecture being exercised at once

const fs = require('fs');        // goes through: JS API → C++ binding → libuv thread pool
const net = require('net');      // goes through: JS API → C++ binding → libuv + OS sockets
const crypto = require('crypto');// goes through: JS API → C++ binding → libuv thread pool

console.log('1. Synchronous JS (runs on V8, no libuv needed)');
let total = 0;
for (let i = 0; i < 1000; i++) total += i;
console.log('   Sum:', total);

console.log('2. File I/O (JS -> binding -> libuv thread pool)');
fs.readFile(__filename, 'utf8', (err, data) => {
  console.log('   File read via thread pool, size:', data.length);
});

console.log('3. Crypto hashing (JS -> binding -> libuv thread pool)');
crypto.pbkdf2('secret', 'salt', 10000, 64, 'sha512', (err, key) => {
  console.log('   Hash computed via thread pool:', key.toString('hex').slice(0, 10));
});

console.log('4. TCP server (JS -> binding -> libuv + OS network stack)');
const server = net.createServer((socket) => {
  socket.end('Hello from TCP server\n');
});
server.listen(4000, () => {
  console.log('   TCP server listening on :4000 (OS-level async I/O, no thread pool)');
});
```

## 💻 Code Example — Advanced
```javascript
// architecture-worker-threads-demo.js
// Shows how worker_threads fit INTO the architecture for CPU-bound work
// (a 4th execution path alongside main thread + libuv thread pool)

const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const path = require('path');

if (isMainThread) {
  // ─── MAIN THREAD: this is the "JS thread" running the Event Loop ───────────
  function runHeavyTaskInWorker(n) {
    return new Promise((resolve, reject) => {
      // Spawns a REAL OS thread with its OWN V8 instance + Event Loop
      const worker = new Worker(__filename, { workerData: n });
      worker.on('message', resolve);
      worker.on('error', reject);
    });
  }

  async function main() {
    console.log('Main thread stays free to serve other requests');
    const start = Date.now();

    // Run 2 heavy Fibonacci computations in PARALLEL worker threads
    // This is TRUE parallelism, unlike the libuv thread pool which is for I/O
    const [r1, r2] = await Promise.all([
      runHeavyTaskInWorker(40),
      runHeavyTaskInWorker(41),
    ]);

    console.log(`Results: ${r1}, ${r2} (took ${Date.now() - start}ms)`);
  }
  main();
} else {
  // ─── WORKER THREAD: separate thread, separate V8 instance ─────────────────
  function fib(n) {
    return n <= 1 ? n : fib(n - 1) + fib(n - 2); // CPU-bound, blocks THIS thread only
  }
  const result = fib(workerData);
  parentPort.postMessage(result); // send result back to main thread
}
```

---

## 🟠 Express.js Integration
```javascript
// Express sits ON TOP of Node's http module, which sits on the full architecture below
const express = require('express');
const app = express();

app.get('/health', (req, res) => {
  // This handler runs on the MAIN thread's Event Loop (via V8)
  res.json({ status: 'ok', pid: process.pid, uptime: process.uptime() });
});

app.get('/compute-hash/:data', (req, res) => {
  // This call goes: Express(JS) -> Node crypto API(JS) -> C++ binding -> libuv thread pool
  const crypto = require('crypto');
  crypto.pbkdf2(req.params.data, 'salt', 50000, 64, 'sha512', (err, key) => {
    if (err) return res.status(500).json({ error: 'Hash failed' });
    res.json({ hash: key.toString('hex') });
  });
  // Main Event Loop is FREE to accept more requests while this hashes in the thread pool
});

app.listen(3000, () => console.log(`Express server (pid ${process.pid}) on :3000`));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Believing the thread pool handles ALL async operations (including network I/O)
```javascript
// Wrong belief: "network requests also use the 4-thread pool, so 5 concurrent
// HTTP calls would queue up"
// Reality: network I/O uses the OS's async notification system (epoll/kqueue/IOCP),
// NOT the thread pool. The thread pool is only for fs, dns.lookup, crypto, zlib.
const http = require('http');
for (let i = 0; i < 100; i++) {
  http.get('http://example.com'); // all 100 proceed via OS sockets, no thread pool limit
}
```

❌ Mistake 2: Spawning unlimited worker_threads for every small task (expensive to create)
```javascript
// Wrong — creating a new OS thread (with its own V8 instance) per request is costly
app.get('/task', (req, res) => {
  const worker = new Worker('./task.js'); // heavy startup cost, happens EVERY request
  worker.on('message', (result) => res.json(result));
});

// Correct — use a worker pool (e.g., `piscina` library) to reuse threads
const Piscina = require('piscina');
const pool = new Piscina({ filename: path.resolve('./task.js') });
app.get('/task', async (req, res) => {
  const result = await pool.run(req.query);
  res.json(result);
});
```

---

## 🧠 Tricky Interview Question

```javascript
const crypto = require('crypto');
console.time('parallel-hashes');

for (let i = 0; i < 6; i++) {
  crypto.pbkdf2('x', 'salt', 100000, 64, 'sha512', () => {
    console.log(`Hash ${i} done at`, Date.now() - start);
  });
}
const start = Date.now();
```
Answer: With the default `UV_THREADPOOL_SIZE=4`, the first 4 `pbkdf2` calls start immediately in parallel across the 4 thread pool threads, but the 5th and 6th calls must WAIT until a thread frees up. So you'll see 4 callbacks finish around roughly the same time, then the remaining 2 finish later, in two more waves (if work takes similar time). Increasing `UV_THREADPOOL_SIZE` (e.g., `process.env.UV_THREADPOOL_SIZE = 8` set before any libuv call) would let more run truly in parallel.

---

## ⚫ Interview Questions + Answers

Q1: What are the four main architectural layers of Node.js?
A1: (1) Your JavaScript application code, (2) Node.js core/bindings (built-in modules like `fs`, `http`, exposed via C++ bindings to V8), (3) V8 (executes JS, manages memory), (4) libuv (Event Loop, thread pool, async OS I/O abstraction).

Q2: Is the libuv thread pool the same as `worker_threads`?
A2: No. The libuv thread pool (default 4 threads) is used internally by Node core APIs (fs, dns.lookup, crypto, zlib) and is NOT directly accessible from JS. `worker_threads` lets you spawn your own full OS threads, each with a separate V8 instance and Event Loop, for your own CPU-bound JS code.

Q3: How does Node.js achieve cross-platform async I/O without separate code per OS?
A3: libuv abstracts the OS differences — it uses `epoll` on Linux, `kqueue` on macOS/BSD, and IOCP (I/O Completion Ports) on Windows internally, but exposes one unified API to Node.js, so Node core modules work identically everywhere.

Q4: What is the role of C++ bindings in the architecture?
A4: They're the bridge between JS (running in V8) and native functionality (libuv, OS syscalls). Node core modules like `fs` are partly implemented in C++ for performance and OS access, exposed to JavaScript through V8's native binding API.

Q5: Why is understanding this architecture important for production debugging?
A5: Because performance issues often trace to a specific layer — a slow endpoint might be Event Loop blocking (JS/V8 layer), thread pool saturation (libuv layer, fix with `UV_THREADPOOL_SIZE`), or OS-level socket limits (ulimit). Diagnosing correctly requires knowing which layer is responsible.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Explaining Node's concurrency model in system design interviews
- Diagnosing whether a bottleneck is CPU (Event Loop blocked), I/O (thread pool saturated), or network (OS/socket limits)

❌ Avoid when:
- You don't need this depth for day-to-day app development — most business logic doesn't require reasoning about libuv internals, only about async/await correctness

---

## 📊 Visual Diagram
```
NODE.JS FULL ARCHITECTURE STACK
──────────────────────────────────────────────────────
  ┌───────────────────────────────────────────────┐
  │   YOUR APPLICATION CODE (JavaScript)            │
  └───────────────────────┬─────────────────────────┘
                          │
  ┌───────────────────────▼─────────────────────────┐
  │   NODE.JS CORE MODULES (fs, http, crypto...)     │
  │   (JS wrappers calling into C++ bindings)        │
  └───────────────────────┬─────────────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        ▼                                     ▼
  ┌───────────┐                       ┌───────────────┐
  │    V8      │                       │  C++ BINDINGS  │
  │ (executes  │                       │ (bridge to     │
  │  your JS)  │                       │  native code)  │
  └───────────┘                       └───────┬───────┘
                                              ▼
                                      ┌───────────────┐
                                      │    LIBUV       │
                                      │ Event Loop     │
                                      │ Thread Pool(4) │
                                      │ OS Async I/O    │
                                      └───────┬───────┘
                                              ▼
                                      OPERATING SYSTEM
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bindings | C++ bridge exposing native code to JS | Native code को JS तक पहुंचाने वाला C++ bridge |
| Thread Pool | libuv's internal worker threads for fs/crypto/dns | fs/crypto/dns के लिए libuv के internal threads |
| worker_threads | Node API for spawning real parallel JS threads | Real parallel JS threads बनाने का Node API |
| Event Loop | Single-threaded loop picking ready callbacks | Ready callbacks चुनने वाला single thread loop |
| epoll/kqueue/IOCP | OS-specific async I/O notification mechanisms | OS की async I/O notification मशीनरी |
| Native module | Module with C/C++ code compiled for Node | C/C++ code से बना Node module |

---

## ⚡ 3-Line Summary
English:
1. Node.js architecture layers JS code on V8, connected via C++ bindings to libuv, which manages the Event Loop, thread pool, and OS-level async I/O.
2. Network I/O uses OS async mechanisms (epoll/kqueue/IOCP) directly; fs/crypto/dns/zlib use libuv's fixed-size thread pool — these are different concurrency paths.
3. `worker_threads` adds true parallel JS execution for CPU-bound work, complementing (not replacing) the thread pool and main Event Loop.

Hindi:
1. Node.js architecture में JS code V8 पर चलता है, C++ bindings से libuv से जुड़ा है, जो Event Loop, thread pool, और OS-level async I/O manage करता है।
2. Network I/O OS के async mechanism (epoll/kqueue/IOCP) directly use करता है; fs/crypto/dns/zlib libuv के fixed thread pool use करते हैं — दोनों अलग concurrency paths हैं।
3. `worker_threads` CPU-heavy काम के लिए real parallel JS execution देता है, यह thread pool और main Event Loop से अलग (पर साथ काम करने वाला) है।

---

## ➡️ Next Topic
**06. Single Threaded — What it Means** — Clarify exactly what "single-threaded" means for Node.js given everything we just saw about the thread pool and worker threads.
