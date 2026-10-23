# 01. What is Node.js?
# हिंदी में: Node.js क्या है?

---

## 🔵 Simple Definition (English)
**Node.js** is a JavaScript runtime built on Chrome's **V8 engine** that lets you run JavaScript outside the browser — on the server. It uses an **event-driven, non-blocking I/O model**, which means it can handle thousands of concurrent connections without creating a new thread per request. Created by Ryan Dahl in 2009, Node.js turned JavaScript from a client-only language into a full-stack language.

Key facts:
- **Single-threaded** but handles concurrency via Event Loop + async I/O
- **V8 engine** (same engine as Chrome) compiles JS to machine code
- **libuv** library handles async I/O, thread pool, Event Loop
- **npm** (Node Package Manager) — world's largest package registry

## 🔵 सरल परिभाषा (Hindi)
**Node.js** एक JavaScript runtime है जो Chrome के V8 engine पर बना है — browser के बाहर (server पर) JavaScript run करने देता है। यह **event-driven, non-blocking I/O model** use करता है — हजारों concurrent connections बिना new thread बनाए handle करता है।

Key facts:
- **Single-threaded** लेकिन Event Loop से concurrency
- **V8 engine** — Chrome वाला ही engine, JS को machine code में compile करता है
- **libuv** — async I/O, thread pool, Event Loop manage करता है
- **npm** — दुनिया का सबसे बड़ा package registry

---

## 🔴 Problem it Solves
```
BEFORE NODE.JS (2009):
  JavaScript = browser only language
  Server side = PHP, Java, Python, Ruby (each in their own language)
  Problem: Full-stack apps needed TWO languages
    Frontend: JavaScript
    Backend: PHP/Java/Python
  
  Traditional server (Apache + PHP):
    Request arrives → Create new OS thread (~1MB RAM)
    Thread BLOCKS waiting for database response
    1000 requests = 1000 threads = 1GB RAM just waiting
  
WITH NODE.JS:
  One language for full stack (JavaScript everywhere)
  
  Node.js server:
    Request arrives → Register callback → Immediately free
    Database query runs in background (libuv thread pool)
    Event Loop picks callback when DB responds
    1000 requests = ~50MB RAM (no blocking threads)

RESULT:
  LinkedIn moved from Rails to Node.js: 10x less servers
  PayPal doubled requests/second, 35% faster response time
  Netflix reduced startup time from 40 minutes to seconds
```

## 🔴 क्यों बनाया? (Hindi)
```
2009 से पहले: JavaScript = browser only
Full stack: frontend JS + backend PHP/Java = 2 languages
Apache: हर request = new thread = 1MB RAM block
1000 requests = 1GB RAM सिर्फ wait करने में

Node.js solution:
- Frontend + Backend दोनों JavaScript
- Threads block नहीं करते
- 10x कम servers पर same load handle
```

---

## 🟢 How it Works — Step by Step

```
NODE.JS ARCHITECTURE:
───────────────────────────────────────────────────────
  YOUR CODE (JavaScript)
        │
        ▼
  V8 ENGINE (Google)
  ├── Parses your JavaScript
  ├── Compiles to machine code (JIT compilation)
  ├── Manages memory (garbage collection)
  └── Executes synchronous code
        │
        ▼
  NODE.JS BINDINGS (C++)
  ├── Connects V8 to system APIs
  └── Exposes Node.js APIs (fs, http, crypto, etc.)
        │
        ▼
  LIBUV (C Library)
  ├── Event Loop (single-threaded)
  ├── Thread Pool (4 threads by default) → for CPU/I/O
  ├── Network I/O (epoll/kqueue/IOCP — OS specific)
  └── File System, DNS, Child Processes

EXECUTION FLOW:
  const data = fs.readFileSync('file.txt')    // BLOCKING (bad)
  const data = await fs.readFile('file.txt')  // NON-BLOCKING (good)
  
  Non-blocking:
  1. fs.readFile → libuv starts reading in thread pool
  2. V8 continues executing rest of code  
  3. Thread pool finishes → puts callback in Event Loop queue
  4. Event Loop picks callback → runs in V8
```

---

## 🟡 Real World Example
**Swiggy real-time order tracking:** 500,000 concurrent users watching their order status. Each user's browser sends a WebSocket connection to Node.js server. With threads (Java Tomcat): 500,000 threads × 1MB = 500GB RAM needed. With Node.js Event Loop: all 500,000 connections handled in one thread's Event Loop + async I/O. When a driver's location updates → database event → Node.js broadcasts to all connected clients instantly. Memory: ~2GB for all connections.

## 🟡 Real Example Hindi
**Swiggy order tracking:** 5 लाख users order track कर रहे हैं। Thread model: 5 लाख threads × 1MB = 500GB RAM। Node.js: एक thread, Event Loop से सब connections handle। Driver location update → DB event → Node.js सभी clients को broadcast। Memory: ~2GB total।

---

## 💻 Code Example — Basic

```javascript
// what-is-nodejs-demo.js
// Node.js basics: modules, async I/O, HTTP server

// ─── 1. CommonJS modules (built into Node.js) ─────────────────────────────────
const fs = require('fs');          // file system
const path = require('path');      // path utilities
const os = require('os');          // operating system info
const http = require('http');      // HTTP server

// ─── 2. Node.js global objects (not in browser!) ──────────────────────────────
console.log('Node.js version:', process.version);   // "v20.11.0"
console.log('Platform:', process.platform);          // "darwin" / "linux" / "win32"
console.log('CPU cores:', os.cpus().length);         // 8
console.log('Free memory:', Math.round(os.freemem() / 1e9) + 'GB');
console.log('Current directory:', __dirname);         // absolute path to this file
console.log('File name:', __filename);

// ─── 3. Non-blocking I/O (the whole point!) ───────────────────────────────────
console.log('Reading file... (non-blocking)');

fs.readFile(__filename, 'utf8', (err, data) => {
  // This callback runs AFTER file is read
  // Meanwhile, code below this call already executed!
  if (err) {
    console.error('Error reading file:', err.message);
    return;
  }
  console.log('File size:', data.length, 'characters');
});

console.log('This runs BEFORE file is read!');  // prints first

// ─── 4. Simple HTTP server ────────────────────────────────────────────────────
const server = http.createServer((req, res) => {
  // Called on EVERY incoming request
  if (req.url === '/' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      message: 'Hello from Node.js!',
      node: process.version,
      timestamp: new Date().toISOString(),
    }));
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

server.listen(3000, () => {
  console.log('Server running at http://localhost:3000');
});

// ─── 5. process.argv — command line arguments ─────────────────────────────────
// Run: node what-is-nodejs-demo.js --name Rahul
const args = process.argv.slice(2);  // [0] = node, [1] = script path
console.log('CLI args:', args);       // ['--name', 'Rahul']
```

## 💻 Code Example — Advanced

```javascript
// advanced-nodejs.js
// Production patterns: async/await, error handling, env vars

require('dotenv').config();  // loads .env into process.env
const http = require('http');
const { promisify } = require('util');  // converts callback APIs to promises
const fs = require('fs');
const { EventEmitter } = require('events');

// ─── 1. Async/await with Node.js core modules ─────────────────────────────────
const readFile = promisify(fs.readFile);   // fs.readFile → Promise
const writeFile = promisify(fs.writeFile);

async function processConfig() {
  try {
    const data = await readFile('./config.json', 'utf8');
    const config = JSON.parse(data);
    
    // Parallel reads — much faster than sequential!
    const [userConfig, dbConfig] = await Promise.all([
      readFile('./user-config.json', 'utf8'),
      readFile('./db-config.json', 'utf8'),
    ]);
    
    return { config, userConfig: JSON.parse(userConfig) };
  } catch (err) {
    console.error('Config error:', err.message);
    throw err;
  }
}

// ─── 2. Custom EventEmitter (Node.js Observer pattern) ───────────────────────
class OrderTracker extends EventEmitter {
  constructor() {
    super();
    this.orders = new Map();
  }

  placeOrder(orderId, items) {
    const order = { id: orderId, items, status: 'placed', createdAt: Date.now() };
    this.orders.set(orderId, order);
    this.emit('order:placed', order);  // fires event
    return order;
  }

  updateStatus(orderId, status) {
    const order = this.orders.get(orderId);
    if (!order) throw new Error(`Order ${orderId} not found`);
    order.status = status;
    this.emit('order:updated', { orderId, status });  // fires event
  }
}

const tracker = new OrderTracker();

// Listen to events (like addEventListener in browser)
tracker.on('order:placed', (order) => {
  console.log(`New order: ${order.id}, items: ${order.items.join(', ')}`);
  // Send push notification, email, etc.
});

tracker.on('order:updated', ({ orderId, status }) => {
  console.log(`Order ${orderId} status: ${status}`);
  // Notify user via WebSocket
});

tracker.placeOrder('ORD001', ['Butter Chicken', 'Naan']);
tracker.updateStatus('ORD001', 'preparing');
tracker.updateStatus('ORD001', 'out for delivery');

// ─── 3. Graceful shutdown (production must-have) ─────────────────────────────
const server = http.createServer((req, res) => {
  res.end('OK');
});

server.listen(3000);

// Handle SIGTERM (from Docker stop, PM2 restart, etc.)
process.on('SIGTERM', async () => {
  console.log('SIGTERM received. Shutting down gracefully...');
  
  server.close(() => {
    // Stop accepting new connections
    console.log('HTTP server closed');
    
    // Clean up resources: DB connections, Redis, etc.
    // await db.disconnect();
    // await redis.quit();
    
    process.exit(0);
  });
  
  // Force exit if cleanup takes too long
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 30000);
});

// Handle uncaught exceptions (should be rare — just for safety net)
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err);
  process.exit(1);  // Always exit — state is unknown
});

// Handle unhandled Promise rejections
process.on('unhandledRejection', (reason) => {
  console.error('Unhandled rejection:', reason);
  process.exit(1);
});
```

---

## 🟠 Express.js Integration

```javascript
// Node.js raw HTTP vs Express
const http = require('http');
const express = require('express');

// ─── RAW NODE.JS HTTP (painful) ───────────────────────────────────────────────
const rawServer = http.createServer((req, res) => {
  // Manual routing — gets messy fast
  if (req.url === '/users' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ users: [] }));
  } else if (req.url.startsWith('/users/') && req.method === 'GET') {
    const id = req.url.split('/')[2];  // parse manually
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ user: { id } }));
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
  }
  // No: body parsing, query params, middleware, validation...
  // All must be built manually
});

// ─── EXPRESS (the right way) ──────────────────────────────────────────────────
const app = express();
app.use(express.json());  // body parsing done!

app.get('/users', (req, res) => {
  const { page = 1, limit = 10 } = req.query;  // query params automatic
  res.json({ users: [], page, limit });
});

app.get('/users/:id', (req, res) => {
  const { id } = req.params;  // route params automatic
  res.json({ user: { id } });
});

// Express builds ON TOP of Node.js http module:
// app.listen() internally calls http.createServer(app).listen()
app.listen(3000, () => console.log('Express on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Blocking the Event Loop
```javascript
// WRONG: Synchronous file read in request handler
app.get('/file', (req, res) => {
  const data = fs.readFileSync('./huge-file.txt');  // BLOCKS all requests!
  res.send(data);
});

// CORRECT: Always use async
app.get('/file', async (req, res) => {
  const data = await fs.promises.readFile('./huge-file.txt');
  res.send(data);
});
```

❌ **Mistake 2:** Not handling Promise rejections
```javascript
// WRONG: Unhandled rejection crashes Node.js (v15+)
async function fetchData() {
  const data = await database.query('...');  // if this throws — crash!
  return data;
}
app.get('/data', (req, res) => {
  fetchData().then(data => res.json(data));  // no .catch()!
});

// CORRECT: Always catch async errors
app.get('/data', async (req, res, next) => {
  try {
    const data = await fetchData();
    res.json(data);
  } catch (err) {
    next(err);  // pass to Express error handler
  }
});
```

❌ **Mistake 3:** Confusing Node.js version support for APIs
```javascript
// fs.promises available from Node.js 10+
// fs/promises (import) available from Node.js 14+
// Always check: node --version before using newer APIs
const fs = require('fs/promises');  // Works in Node 14+
// vs
const { promises: fs } = require('fs');  // Works in Node 10+
```

---

## 🧠 Tricky Interview Question

**Q: Is Node.js truly single-threaded? What about the thread pool?**

**Answer:** Node.js JavaScript execution is single-threaded — your code runs on one thread (the Event Loop thread). But Node.js is NOT fully single-threaded: **libuv** maintains a thread pool (default: 4 threads, configurable via `UV_THREADPOOL_SIZE=8`). This pool handles: (1) file system operations (fs), (2) DNS lookups, (3) `crypto` module operations, (4) user-created threads via `worker_threads`. So: your JavaScript code = single thread. I/O operations = delegated to thread pool. When I/O completes, the callback is queued back to the Event Loop (single thread). This is why Node.js can be "non-blocking" despite one JS thread.

---

## ⚫ Interview Questions + Answers

**Q1: What is Node.js and how is it different from browser JavaScript?**
A1: Node.js is a server-side JavaScript runtime built on V8 + libuv. Differences: (1) No DOM, window, document — Node has process, fs, http instead. (2) Node uses CommonJS (`require`/`module.exports`) by default (also supports ESM). (3) Node has direct file system access, network sockets, OS APIs. (4) Node runs in a controlled server environment; browser JS is sandboxed for security. (5) Node's Event Loop integrates with libuv for OS-level async I/O; browser has its own event loop via Web APIs.

**Q2: What is V8 and what role does it play in Node.js?**
A2: V8 is Google's open-source JavaScript + WebAssembly engine, written in C++. Used in Chrome and Node.js. It: (1) parses JavaScript source code, (2) compiles it to machine code using JIT (Just-In-Time) compilation, (3) manages heap memory and garbage collection, (4) executes synchronous JavaScript. Node.js wraps V8 and adds: file system (libuv), networking, crypto, and other system APIs via C++ bindings. V8 does NOT handle async I/O — that's libuv's job.

**Q3: What is libuv?**
A3: libuv is a C library that provides: (1) The Event Loop (the phase-based loop that picks callbacks), (2) A thread pool (4 threads by default) for fs, DNS, crypto operations, (3) Cross-platform async I/O abstraction (epoll on Linux, kqueue on macOS, IOCP on Windows). Node.js uses libuv to make async operations work across operating systems uniformly. Without libuv, Node.js would need separate implementations for each OS.

**Q4: When should you use Node.js vs other backends?**
A4: Use Node.js for: (1) I/O-bound applications (APIs that call databases, external services — Node excels here), (2) Real-time apps (WebSockets, chat, live tracking), (3) Full-stack JavaScript teams (same language front+back), (4) Microservices (lightweight, fast startup). Prefer other runtimes for: (1) CPU-intensive work (video encoding, ML — Python, Go, Java are better), (2) Heavy computation (Go, Java, Rust are more efficient), (3) Teams already expert in another language.

**Q5: What is `process.env` and how do you use it?**
A5: `process.env` is a Node.js global object containing all environment variables as strings. Used to store: database credentials, API keys, port numbers, feature flags — anything that changes between environments (dev/staging/prod). Best practice: use `dotenv` library to load `.env` file into `process.env` in development. In production: set env vars via OS, Docker `-e`, or deployment platform (Heroku config vars, AWS Parameter Store). Never commit `.env` files to git — they contain secrets.

---

## 📊 Visual Diagram

```
NODE.JS ARCHITECTURE:
──────────────────────────────────────────────────────────

  YOUR JAVASCRIPT CODE
  ┌─────────────────────────────────────────────────────┐
  │  const data = await fs.readFile('config.json')      │
  │  const users = await db.query('SELECT * FROM users')│
  │  http.createServer((req, res) => {...})              │
  └────────────────────────┬────────────────────────────┘
                           │
                           ▼
  V8 ENGINE (JavaScript ↔ Machine Code)
  ┌─────────────────────────────────────────────────────┐
  │  Parse JS → Compile → Execute synchronous code      │
  │  Garbage Collection | Memory Management             │
  └────────────────────────┬────────────────────────────┘
                           │
                           ▼
  NODE.JS C++ BINDINGS (fs, http, crypto, etc.)
                           │
                           ▼
  LIBUV
  ┌─────────────────────────────────────────────────────┐
  │  Event Loop (1 thread)  │  Thread Pool (4 threads)  │
  │  ┌─────────────────┐    │  ┌──────────────────────┐ │
  │  │ Timers          │    │  │ fs operations        │ │
  │  │ I/O callbacks   │    │  │ DNS resolution       │ │
  │  │ Poll (I/O wait) │    │  │ crypto operations    │ │
  │  │ Check           │    │  │ zlib compression     │ │
  │  └─────────────────┘    │  └──────────────────────┘ │
  └─────────────────────────────────────────────────────┘
                           │
                           ▼
  OPERATING SYSTEM
  (Linux: epoll | macOS: kqueue | Windows: IOCP)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Runtime | Environment to execute code | Code execute करने का environment |
| V8 | Google's JS engine (compiles JS to machine code) | JS को machine code में compile करता है |
| libuv | C library for async I/O + Event Loop | Async I/O + Event Loop manage करता है |
| Non-blocking | Not waiting for I/O to finish | I/O finish होने का wait नहीं |
| Event-driven | Code runs when events occur | Events पर code run होता है |
| npm | Node Package Manager | Package manager |
| process | Global object with Node.js runtime info | Node.js runtime info का object |
| CommonJS | `require/module.exports` module system | Node.js का default module system |

---

## ⚡ 3-Line Summary
**English:**
1. Node.js is a JavaScript runtime built on Chrome's V8 engine + libuv library, enabling server-side JS execution with event-driven, non-blocking I/O — handling thousands of concurrent connections on one thread.
2. Architecture: V8 executes your synchronous JS; libuv's Event Loop + thread pool handle all async I/O (file system, network, DNS, crypto) without blocking the main thread.
3. Best for: I/O-bound APIs, real-time apps (WebSockets), full-stack JS teams; avoid for CPU-intensive tasks (use Worker Threads or a language like Go).

**Hindi:**
1. Node.js = V8 engine + libuv पर बना JavaScript runtime — server side JS, event-driven non-blocking I/O से single thread पर हजारों connections।
2. Architecture: V8 sync JS run करता है; libuv का Event Loop + thread pool सारे async I/O handle करते हैं बिना main thread block किए।
3. Best for: I/O-heavy APIs, real-time apps; avoid for: CPU-intensive work (Worker Threads या Go use करो)।

---

## ➡️ Next Topic
**02. Node.js vs Browser JavaScript** — What's different, what's same।
