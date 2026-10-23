# 07. Non-Blocking I/O
# हिंदी में: Non-Blocking I/O — रुको मत, आगे बढ़ो

---

## 🔵 Simple Definition (English)
**Non-blocking I/O** means: when your code starts an I/O operation (reading a file, querying a database, making an HTTP request), it does NOT wait for the operation to complete. Instead, it registers a callback and moves on. When the I/O completes (handled by libuv's thread pool in the background), the callback is placed in the Event Loop queue and executed when the call stack is empty. Contrast with **blocking I/O** where execution stops and waits until the I/O operation finishes.

## 🔵 सरल परिभाषा (Hindi)
**Non-blocking I/O** मतलब: जब code I/O operation start करता है (file read, DB query, HTTP request), वो complete होने का wait नहीं करता। Callback register करता है और आगे बढ़ जाता है। जब I/O complete होता है (libuv thread pool background में handle करता है), callback Event Loop queue में जाता है। **Blocking I/O** में execution रुक जाती है जब तक I/O finish नहीं होता।

---

## 🔴 Problem it Solves
```
BLOCKING I/O DISASTER (Traditional server):
  Request 1: "Get user from DB"
    Thread 1: → [waiting for DB... 100ms] → response sent
  
  Request 2 arrives during DB wait:
    Thread 2: created (1MB RAM) → [waiting...] → response
  Request 3: Thread 3 → [waiting...]
  ...
  Request 1000: Thread 1000 → [waiting...]
  
  1000 threads × 1MB = 1GB RAM just waiting for DB!
  Context switching between 1000 threads = CPU waste
  Can't scale past ~5000 threads on most servers

NON-BLOCKING I/O SOLUTION (Node.js):
  Request 1: "Get user from DB"
    → Register callback → IMMEDIATELY move on
    → DB query running in background (libuv thread pool)
  
  Request 2 arrives: ALSO registered and moved on
  Request 3: Also registered
  ...
  Request 1000: Also registered
  
  DB responds for Request 1 → callback in queue → executed
  DB responds for Request 2 → callback in queue → executed
  
  All 1000 requests: 1 JavaScript thread + 4 libuv threads = ~50MB RAM!
```

---

## 🟢 How it Works

```
BLOCKING vs NON-BLOCKING:
──────────────────────────────────────────────────────────

BLOCKING (fs.readFileSync):
  Time → ─────────────────────────────────────────────────
  Thread: [read file 100ms block][process][read file 100ms block][process]
           ←────────waiting────→          ←────────waiting────→
           Thread does NOTHING useful while waiting

NON-BLOCKING (fs.readFile with callback):
  Time → ─────────────────────────────────────────────────
  Thread: [register callback][other work][other work][callback!][callback!]
  libuv:                     [reading...file1done]   [reading...file2done]
                              ↑──background──↑        ↑──background──↑
  Thread never idles — always doing something productive!

I/O OPERATIONS THAT ARE ASYNC IN NODE:
  ✅ File system (fs.readFile, fs.writeFile, fs.stat)
  ✅ Network (http.request, https.get, fetch)
  ✅ Database queries (all DB drivers: pg, mysql2, mongoose)
  ✅ DNS lookups (dns.resolve)
  ✅ Child processes (exec, spawn)
  ✅ Timer delays (setTimeout, setInterval)

SYNC OPERATIONS (always blocking):
  ❌ fs.readFileSync, fs.writeFileSync (avoidable)
  ❌ JSON.parse on large strings (unavoidable, use streams)
  ❌ RegExp on huge strings (regex backtracking)
  ❌ Crypto operations (unless async version used)
  ❌ for/while loops (CPU work)
```

---

## 🟡 Real World Example
**PhonePe payment processing:** 2 million transactions/day. Each transaction: validate input, check fraud rules (DB), debit account (DB write), credit merchant (DB write), send notification (HTTP). With blocking: each step waits for previous — ~400ms total, thread blocked throughout. With non-blocking: each DB/HTTP call starts and releases thread; thread only used when computation needed. Same server handles 20x more transactions because thread is always productive, never waiting.

## 🟡 Real Example Hindi
**PhonePe:** 20 लाख transactions रोज़। हर transaction: validate → fraud check (DB) → debit (DB write) → credit (DB write) → notification (HTTP)। Blocking: हर step wait करे, thread 400ms block। Non-blocking: हर DB/HTTP call start करो, thread release, callback पर वापस आओ। Same server 20x ज़्यादा transactions handle करता है।

---

## 💻 Code Example — Basic

```javascript
// non-blocking-io-demo.js
const fs = require('fs');

console.log('=== BLOCKING vs NON-BLOCKING ===\n');

// ─── 1. BLOCKING I/O ─────────────────────────────────────────────────────────
console.log('--- Blocking I/O ---');
console.log('Before readFileSync');
const data = fs.readFileSync(__filename, 'utf8');  // STOPS here until file read
console.log('After readFileSync — file size:', data.length, 'chars');
console.log('NOTE: no other requests can be handled while this blocks!\n');

// ─── 2. NON-BLOCKING I/O (callback style) ────────────────────────────────────
console.log('--- Non-Blocking I/O (callback) ---');
console.log('Before readFile (async)');

fs.readFile(__filename, 'utf8', (err, data) => {
  // This runs LATER — after Event Loop picks it up
  if (err) {
    console.error('Error:', err.message);
    return;
  }
  console.log('readFile callback ran — file size:', data.length, 'chars');
  // Other requests could have been handled while this was reading!
});

console.log('After readFile call — already moved on!');
// ^^^ This prints BEFORE the callback above!

// ─── 3. NON-BLOCKING I/O (promise/async style — modern) ─────────────────────
async function readFileAsync() {
  console.log('\n--- Non-Blocking I/O (async/await) ---');
  console.log('Before await');

  try {
    const content = await fs.promises.readFile(__filename, 'utf8');
    console.log('await completed — file size:', content.length, 'chars');
  } catch (err) {
    console.error('Error:', err.message);
  }

  console.log('After await');
}

readFileAsync();
console.log('After readFileAsync() call — runs before await completes!');

// OUTPUT ORDER:
// Before readFileSync
// After readFileSync — file size: X chars
// Before readFile (async)
// After readFile call — already moved on!    ← async moved on immediately
// Before await
// After readFileAsync() call                 ← also moved on
// readFile callback ran — file size: X chars  ← callback when done
// await completed — file size: X chars        ← await when done
// After await
```

## 💻 Code Example — Advanced

```javascript
// advanced-non-blocking.js
// Real-world patterns: parallel I/O, streaming, error handling

const fs = require('fs');
const https = require('https');

// ─── 1. PARALLEL I/O (most important pattern!) ────────────────────────────────
// WRONG: Sequential — adds wait times
async function getUserDataSequential(userId) {
  const user = await db.query(`SELECT * FROM users WHERE id = ?`, [userId]);  // 100ms
  const orders = await db.query(`SELECT * FROM orders WHERE user_id = ?`, [userId]);  // 100ms
  const reviews = await db.query(`SELECT * FROM reviews WHERE user_id = ?`, [userId]);  // 100ms
  // Total: 300ms — waiting one by one!
  return { user, orders, reviews };
}

// CORRECT: Parallel — all start at same time
async function getUserDataParallel(userId) {
  const [user, orders, reviews] = await Promise.all([
    db.query(`SELECT * FROM users WHERE id = ?`, [userId]),    // starts simultaneously
    db.query(`SELECT * FROM orders WHERE user_id = ?`, [userId]),  // starts simultaneously
    db.query(`SELECT * FROM reviews WHERE user_id = ?`, [userId]), // starts simultaneously
  ]);
  // Total: ~100ms (limited by slowest query, not sum!)
  return { user, orders, reviews };
}

// ─── 2. STREAMS — Non-blocking for LARGE files ───────────────────────────────
// Reading 10GB log file: DON'T do readFile (loads all into RAM!)
// DO: use streams — reads chunk by chunk, non-blocking

function processLargeLogFile(filePath) {
  return new Promise((resolve, reject) => {
    let lineCount = 0;
    let errorCount = 0;
    let buffer = '';

    // createReadStream reads in chunks (64KB default) — never loads full file
    const stream = fs.createReadStream(filePath, { encoding: 'utf8', highWaterMark: 64 * 1024 });

    stream.on('data', (chunk) => {
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';  // keep incomplete last line

      lines.forEach(line => {
        lineCount++;
        if (line.includes('ERROR')) errorCount++;
      });
    });

    stream.on('end', () => {
      resolve({ lineCount, errorCount });
    });

    stream.on('error', reject);
  });
}

// ─── 3. HTTP request (non-blocking network I/O) ──────────────────────────────
function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      
      res.on('data', chunk => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (err) {
          reject(new Error('Invalid JSON response'));
        }
      });
    }).on('error', reject);
  });
}

// ─── 4. UV_THREADPOOL_SIZE — tuning libuv's thread pool ──────────────────────
// Default: 4 threads
// Increase for I/O-heavy apps:
// UV_THREADPOOL_SIZE=16 node server.js

// When to increase:
// - Many concurrent file operations
// - Heavy crypto usage (bcrypt, crypto)
// - Many DNS lookups
// Check CPU cores: more threads than cores = diminishing returns
console.log('libuv thread pool size:', process.env.UV_THREADPOOL_SIZE || 4);

// ─── 5. Detecting blocking code (profiling) ──────────────────────────────────
// clinic.js — npm install -g clinic
// clinic doctor -- node server.js
// clinic flame -- node server.js
// Opens browser with flamegraph showing where time is spent
// Blocking operations show up as tall, wide bars
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// ─── BLOCKING ENDPOINT (never do this) ───────────────────────────────────────
app.get('/sync-bad', (req, res) => {
  // ❌ Blocks Event Loop — all other requests wait!
  const data = fs.readFileSync('./large-file.json');  // 500ms block
  const parsed = JSON.parse(data);                    // 200ms block
  res.json(parsed);
  // During these 700ms: EVERY OTHER REQUEST IS STUCK WAITING
});

// ─── NON-BLOCKING ENDPOINT (correct) ─────────────────────────────────────────
app.get('/async-good', async (req, res) => {
  // ✅ Non-blocking — other requests served during file read
  const data = await fs.promises.readFile('./large-file.json');
  const parsed = JSON.parse(data);  // parsing is sync — acceptable for small files
  res.json(parsed);
});

// ─── PARALLEL DB CALLS ───────────────────────────────────────────────────────
app.get('/dashboard/:userId', async (req, res) => {
  const { userId } = req.params;

  // ❌ Sequential (slow):
  // const user = await User.findById(userId);
  // const orders = await Order.find({ userId });
  // const notifications = await Notification.find({ userId });

  // ✅ Parallel (fast — all start simultaneously):
  const [user, orders, notifications] = await Promise.all([
    User.findById(userId),
    Order.find({ userId }).limit(5).sort({ createdAt: -1 }),
    Notification.find({ userId, read: false }).limit(10),
  ]);

  res.json({ user, orders, notifications });
});

// ─── LARGE FILE DOWNLOAD (stream to response) ────────────────────────────────
app.get('/download/:filename', (req, res) => {
  const { filename } = req.params;
  const filePath = path.join(__dirname, 'uploads', filename);

  // ❌ WRONG: readFile loads entire file into RAM
  // const data = await fs.promises.readFile(filePath);
  // res.send(data);

  // ✅ CORRECT: pipe stream directly to response
  // File content flows chunk by chunk — minimal memory usage
  res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
  fs.createReadStream(filePath).pipe(res);
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `readFileSync` in request handlers
```javascript
// WRONG in production server:
app.get('/config', (req, res) => {
  const config = JSON.parse(fs.readFileSync('./config.json'));  // blocks!
  res.json(config);
});

// CORRECT: Read config once at startup (not per request)
let appConfig;
(async () => {
  appConfig = JSON.parse(await fs.promises.readFile('./config.json'));
  app.listen(3000);
})();

app.get('/config', (req, res) => {
  res.json(appConfig);  // already in memory, no I/O
});
```

❌ **Mistake 2:** Sequential when parallel is possible
```javascript
// SLOW: 3 queries × 100ms each = 300ms total
const user = await db.findUser(id);
const posts = await db.findPosts(id);
const followers = await db.findFollowers(id);

// FAST: all run simultaneously, total = 100ms (slowest query)
const [user, posts, followers] = await Promise.all([
  db.findUser(id),
  db.findPosts(id),
  db.findFollowers(id),
]);
```

❌ **Mistake 3:** Forgetting to handle errors in async code
```javascript
// WRONG: unhandled rejection crashes server
app.get('/data', async (req, res) => {
  const data = await db.query('SELECT...');  // throws if DB down
  res.json(data);
});

// CORRECT: try/catch or express-async-errors middleware
app.get('/data', async (req, res, next) => {
  try {
    const data = await db.query('SELECT...');
    res.json(data);
  } catch (err) {
    next(err);  // to Express error handler
  }
});
```

---

## 🧠 Tricky Interview Question

**Q: If Node.js is single-threaded, how does `fs.readFile` not block?**

**Answer:** `fs.readFile` delegates the actual file I/O to **libuv's thread pool** (4 threads by default). Here's the exact flow: (1) Your JS code calls `fs.readFile(path, callback)`. (2) Node.js hands this to libuv. (3) libuv assigns it to one of its 4 worker threads. (4) That thread does the actual OS-level blocking file read — but it's a libuv thread, NOT the Event Loop (JS) thread. (5) When the read completes, libuv puts the callback in the Event Loop's queue. (6) Event Loop (JS thread), when free, picks up the callback and executes it. So: your JS thread never blocks — the blocking happens in libuv's thread pool invisibly.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between blocking and non-blocking I/O?**
A1: Blocking I/O: execution thread waits until the I/O operation completes — the thread is "blocked," doing nothing useful. `fs.readFileSync` is blocking. Non-blocking I/O: thread initiates the I/O operation, registers a callback, and immediately continues. libuv handles the actual I/O in background. When complete, the callback is queued. `fs.readFile(path, callback)` and `await fs.promises.readFile(path)` are non-blocking. Critical difference: with 1000 concurrent requests, blocking needs 1000 threads (1GB RAM); non-blocking handles all 1000 on 1 thread (~50MB RAM).

**Q2: What is the `UV_THREADPOOL_SIZE` environment variable?**
A2: libuv's default thread pool is 4 threads. These handle: file I/O, DNS lookups, `crypto` module (bcrypt, hash), zlib compression. For apps with many concurrent heavy operations (many file reads, many bcrypt hashes, many DNS lookups), 4 threads can become a bottleneck. `UV_THREADPOOL_SIZE=16 node server.js` increases the pool. Max useful size ≈ number of CPU cores (more threads than cores = more context switching, not more throughput). Default of 4 is fine for most web APIs.

**Q3: When should you use `Promise.all` vs sequential `await`?**
A3: Use `Promise.all` when operations are **independent** (don't depend on each other's results). All operations start simultaneously — total time = time of slowest operation. Use sequential `await` when operations **depend on each other**: `const user = await findUser(id)` → then `const orders = await findOrders(user.id)` (need user.id first). Also use sequential when you want to fail fast without starting subsequent operations. Use `Promise.allSettled` when you want all results even if some fail.

**Q4: What are Node.js Streams and how do they relate to non-blocking I/O?**
A4: Streams are an abstraction for consuming/producing data in chunks (non-blocking, chunk by chunk) instead of loading everything into memory at once. Types: Readable (fs.createReadStream), Writable (fs.createWriteStream), Transform (zlib.createGzip). Key benefit: reading a 10GB file with `readFile` loads 10GB into RAM; `createReadStream` pipes 64KB chunks at a time — constant ~64KB RAM usage. Streams are inherently non-blocking: they emit `data` events as chunks arrive, and the Event Loop stays free between chunks. Express `res` object is a Writable stream — `stream.pipe(res)` is very efficient for file downloads.

**Q5: How do you detect if your Node.js app is blocking the Event Loop?**
A5: Tools: (1) `clinic doctor` / `clinic flame` (npm clinic) — starts server, runs load test, shows flame graph of where time is spent. (2) `--prof` flag: `node --prof server.js` generates V8 profiling log. (3) `event-loop-lag` npm package — measures how many ms the Event Loop is delayed responding to a timer (anything >50ms is concerning). (4) `perf_hooks` built-in: `const { performance } = require('perf_hooks')`. Signs of blocking: response times suddenly very high under load, `event-loop-lag` > 50ms, flamegraph shows wide synchronous blocks.

---

## 📊 Visual Diagram

```
BLOCKING vs NON-BLOCKING:
──────────────────────────────────────────────────────────

BLOCKING (readFileSync):
  Time:  0ms     100ms    200ms    300ms
  JS:    [READ1-WAIT][READ2-WAIT][READ3-WAIT]
         ↑ blocked! ↑ blocked! ↑ blocked!
         Nothing else can run

NON-BLOCKING (readFile async):
  Time:  0ms    10ms      100ms    110ms
  JS:    [start][start][start] [CB1][CB2][CB3]
          ↑start↑          ↑↑↑ callbacks when done
  libuv: [READ1.................done]
          [READ2.................done]
           [READ3.................done]
  
  JS thread runs callbacks as they complete
  libuv thread pool does the actual reading

PARALLEL QUERIES (Promise.all):
  Sequential:
    time: ──[query1 100ms]──[query2 100ms]──[query3 100ms]── = 300ms

  Parallel (Promise.all):
    time: ──[query1 100ms]── = 100ms
              [query2 100ms]
              [query3 100ms]
    All run simultaneously, total = slowest
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blocking I/O | Thread waits for I/O to complete | Thread I/O complete होने तक wait करे |
| Non-blocking I/O | Thread continues, callback later | Thread आगे बढ़े, callback बाद में |
| Callback | Function called when async op done | Async operation complete पर call होने वाला function |
| Promise.all | Run multiple promises in parallel | Multiple async operations एक साथ run |
| libuv thread pool | Background threads for I/O | Background में I/O करने वाले threads |
| Stream | Process data in chunks | Data chunks में process करना |
| UV_THREADPOOL_SIZE | libuv thread pool count | libuv के thread pool का size |

---

## ⚡ 3-Line Summary
**English:**
1. Non-blocking I/O means: start I/O → register callback → move on immediately; when I/O completes (in libuv's thread pool), the callback runs via the Event Loop — the JS thread is never idle waiting.
2. The pattern: use `fs.promises.readFile` over `fs.readFileSync`, and use `Promise.all([...])` for independent operations that can run simultaneously.
3. Blocking the Event Loop is the #1 Node.js performance mistake — profile with `clinic doctor` or `perf_hooks` to find synchronous hot paths.

**Hindi:**
1. Non-blocking I/O: I/O start करो → callback register करो → आगे बढ़ो; I/O complete होने पर callback Event Loop से run होती है — JS thread कभी wait में idle नहीं।
2. Pattern: `fs.promises.readFile` use करो `readFileSync` की जगह; independent operations के लिए `Promise.all([...])`।
3. Event Loop block करना Node.js की #1 performance mistake है — `clinic doctor` से profile करो।

---

## ➡️ Next Topic
**08. CommonJS vs ES Modules** — `require` vs `import`, default exports, named exports।
