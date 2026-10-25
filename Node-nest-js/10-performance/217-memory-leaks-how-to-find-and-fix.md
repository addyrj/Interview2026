# 217. Memory Leaks — How to Find + Fix
# हिंदी में: Memory Leaks — कैसे ढूंढें और ठीक करें

---

## 🔵 Simple Definition (English)
A **memory leak** happens when your app keeps allocating memory that is never released, even though it's no longer needed — RAM usage grows continuously until the process crashes with "out of memory" (OOM). In Node.js, leaks almost always come from objects that JavaScript's garbage collector CAN'T free because something still holds a reference to them (forgotten event listeners, growing caches/arrays, uncleaned timers, closures capturing large objects).

## 🔵 सरल परिभाषा (Hindi)
**Memory leak** तब होता है जब app memory allocate करता रहता है जो कभी release नहीं होती, भले ही उसकी ज़रूरत न हो — RAM usage लगातार बढ़ता रहता है जब तक process "out of memory" (OOM) से crash न हो जाए। Node.js में leaks almost हमेशा उन objects से आती हैं जिन्हें JavaScript का garbage collector free नहीं कर पाता क्योंकि कोई चीज़ अभी भी उनका reference रखे हुए है (भूले हुए event listeners, बढ़ते caches/arrays, cleanup न हुए timers, closures जो बड़े objects capture करते हैं)।

---

## 🔴 Problem it Solves
A leaking Node.js server works fine for the first hour, then gets progressively slower as the garbage collector has to work harder scanning a bloated heap, and eventually crashes with `FATAL ERROR: Reached heap limit, Allocation failed`, taking down all active connections. This is especially dangerous in production because it's silent until it suddenly isn't — understanding common leak patterns and tools to find them (heap snapshots, `--inspect`, comparing memory over time) lets you catch and fix leaks before they cause outages.

## 🔴 यह क्यों बना? (Hindi)
Leaking Node.js server पहले घंटे ठीक चलता है, फिर धीरे-धीरे slow होता जाता है क्योंकि garbage collector को bloated heap scan करने में ज़्यादा मेहनत करनी पड़ती है, और आखिर में `FATAL ERROR: Reached heap limit, Allocation failed` से crash हो जाता है, सभी active connections गिरा देता है। Production में ये खतरनाक है क्योंकि silently होता है जब तक अचानक नहीं होता — common leak patterns और उन्हें ढूंढने के tools (heap snapshots, `--inspect`, समय के साथ memory compare करना) समझना leaks को outage से पहले पकड़ने और ठीक करने देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Spot the symptom**: monitor `process.memoryUsage().rss` (or an APM dashboard) over hours — a leak shows a steady UPWARD trend that never comes back down after garbage collection
Step 2 → **Reproduce under load**: hit the suspected endpoint repeatedly (load test tool like `autocannon`) while watching memory climb
Step 3 → **Take heap snapshots**: use Chrome DevTools (`node --inspect`) to take 2-3 snapshots over time, then compare — objects that keep growing in count between snapshots are the leak
Step 4 → **Identify the leaking reference**: common culprits — event listeners added but never removed, global/module-level arrays/Maps that only grow, `setInterval`/`setTimeout` never cleared, closures holding large data
Step 5 → **Fix the root cause**: remove listeners (`removeListener`), clear timers (`clearInterval`), bound caches (LRU with max size), release closure references after use
Step 6 → **Re-verify**: repeat the load test and confirm memory now stabilizes (grows then plateaus with GC, instead of climbing forever)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Symptom पहचानो**: घंटों तक `process.memoryUsage().rss` (या APM dashboard) monitor करो — leak में upward trend दिखता है जो GC के बाद भी नीचे नहीं आता
Step 2 → **Load में reproduce करो**: suspected endpoint को बार-बार hit करो (जैसे `autocannon`) memory बढ़ता देखते हुए
Step 3 → **Heap snapshots लो**: Chrome DevTools (`node --inspect`) से समय के साथ 2-3 snapshots लो, फिर compare करो — जो objects count में बढ़ते रहें वो leak हैं
Step 4 → **Leaking reference पहचानो**: common culprits — added पर कभी न removed event listeners, सिर्फ बढ़ते global/module arrays/Maps, कभी clear न हुए timers, बड़े data capture करने वाले closures
Step 5 → **Root cause fix करो**: listeners हटाओ (`removeListener`), timers clear करो (`clearInterval`), bounded caches (max size के साथ LRU), closure references release करो
Step 6 → **फिर verify करो**: load test repeat करके confirm करो कि memory अब stabilize हो रहा है

---

## 🟡 Real World Example
**Paytm's notification service** was crashing every ~6 hours in production with OOM errors. Investigation with heap snapshots revealed: every time a user connected via WebSocket, the code did `eventEmitter.on('notification', handler)` but NEVER called `removeListener` when the user disconnected. Over thousands of connect/disconnect cycles per hour, the `EventEmitter`'s internal listener array grew unbounded, each holding a closure referencing the full `socket` object (which itself references buffers, request data). Fix: track handlers per connection and call `eventEmitter.removeListener('notification', handler)` in the `disconnect` event — memory usage stabilized immediately.

## 🟡 Real Example Hindi mein
**Paytm की notification service** production में हर ~6 घंटे में OOM errors से crash हो रही थी। Heap snapshots से investigation में मिला: हर बार जब कोई user WebSocket से connect होता, code `eventEmitter.on('notification', handler)` करता था पर disconnect पर कभी `removeListener` call नहीं करता था। हज़ारों connect/disconnect cycles के बाद, `EventEmitter` का internal listener array unbounded बढ़ता गया। Fix: हर connection का handler track करो और `disconnect` event में `removeListener` call करो — memory usage तुरंत stabilize हो गया।

---

## 💻 Code Example — Basic

```javascript
// leak-demo.js — classic memory leak: unbounded array growth
const express = require('express');
const app = express();

// LEAK: this array is never cleared and grows forever as requests come in
const requestLog = [];

app.get('/track', (req, res) => {
  // Every request pushes a new object — nothing ever removes old entries
  requestLog.push({
    url: req.url,
    timestamp: Date.now(),
    headers: req.headers, // ← also holds a reference to the full headers object
  });
  res.json({ logSize: requestLog.length });
});

// Watch RSS grow forever: curl /track in a loop and check process.memoryUsage()
app.get('/memory', (req, res) => {
  const mem = process.memoryUsage();
  res.json({
    rss: `${(mem.rss / 1024 / 1024).toFixed(1)} MB`,       // total process memory
    heapUsed: `${(mem.heapUsed / 1024 / 1024).toFixed(1)} MB`, // JS heap in use
  });
});

app.listen(3000);
// Run: for i in {1..100000}; do curl -s localhost:3000/track > /dev/null; done
// Then: curl localhost:3000/memory — RSS keeps climbing, never plateaus
```

```javascript
// fixed-demo.js — bounded log, old entries evicted (no leak)
const express = require('express');
const app = express();

const MAX_LOG_SIZE = 1000; // hard cap — prevents unbounded growth
const requestLog = [];

app.get('/track', (req, res) => {
  requestLog.push({ url: req.url, timestamp: Date.now() });

  // FIX: evict the oldest entry once we exceed the cap
  if (requestLog.length > MAX_LOG_SIZE) {
    requestLog.shift(); // removes oldest — keeps memory bounded
  }
  res.json({ logSize: requestLog.length });
});

app.listen(3000);
// Now RSS grows initially then plateaus around the cap — no leak
```

## 💻 Code Example — Advanced

```javascript
// listener-leak-demo.js — the EventEmitter listener leak pattern (very common)
const EventEmitter = require('events');
const notifier = new EventEmitter();

// BAD: a new listener is added on every "connection" and NEVER removed
function handleConnection(socketId) {
  const handler = (data) => {
    console.log(`Notifying ${socketId}:`, data);
  };
  notifier.on('notification', handler);
  // Missing: no corresponding removeListener call on disconnect!
  // Node will even warn: "MaxListenersExceededWarning" after 10 listeners
}

// GOOD: track the handler reference and remove it on cleanup
const activeHandlers = new Map(); // socketId -> handler function

function handleConnectionFixed(socketId) {
  const handler = (data) => {
    console.log(`Notifying ${socketId}:`, data);
  };
  notifier.on('notification', handler);
  activeHandlers.set(socketId, handler); // keep reference for later removal
}

function handleDisconnect(socketId) {
  const handler = activeHandlers.get(socketId);
  if (handler) {
    notifier.removeListener('notification', handler); // FIX: cleanup on disconnect
    activeHandlers.delete(socketId);
  }
}

// ─── CLOSURE LEAK PATTERN ─────────────────────────────────────────────────
// BAD: setInterval captures `largeBuffer` in its closure forever, and the
// interval is never cleared — both the timer AND the buffer leak
function startBadPolling() {
  const largeBuffer = Buffer.alloc(50 * 1024 * 1024); // 50MB buffer
  setInterval(() => {
    // This closure holds a reference to largeBuffer, keeping it alive forever
    console.log('polling...', largeBuffer.length);
  }, 5000);
  // No clearInterval() stored anywhere — this timer runs forever,
  // and largeBuffer can NEVER be garbage collected
}

// GOOD: store the interval handle and clear it when done; avoid capturing
// large unnecessary data in the closure
function startGoodPolling() {
  const intervalId = setInterval(() => {
    console.log('polling...');
  }, 5000);

  // Return a cleanup function the caller MUST invoke when done
  return function stopPolling() {
    clearInterval(intervalId); // releases the timer AND breaks the closure's hold
  };
}

// ─── HEAP SNAPSHOT ANALYSIS (programmatic) ───────────────────────────────
// npm install heapdump  (or use `node --inspect` + Chrome DevTools manually)
const heapdump = require('heapdump');

process.on('SIGUSR2', () => {
  // Trigger with: kill -USR2 <pid>  — writes a .heapsnapshot file to inspect
  heapdump.writeSnapshot(`./heap-${Date.now()}.heapsnapshot`, (err, filename) => {
    console.log('Heap snapshot written to', filename);
  });
});
```

---

## 🟠 Express.js Integration

```javascript
// monitoring/memoryMonitor.js — alert when memory crosses a threshold
const EventEmitter = require('events');

function startMemoryMonitor(app) {
  let lastRss = 0;
  let consecutiveIncreases = 0;

  setInterval(() => {
    const mem = process.memoryUsage();
    const rssMB = mem.rss / 1024 / 1024;

    // Simple leak heuristic: RSS consistently increasing over many checks
    if (rssMB > lastRss) {
      consecutiveIncreases++;
    } else {
      consecutiveIncreases = 0;
    }
    lastRss = rssMB;

    if (consecutiveIncreases > 20) {
      // In production: send alert to Slack/PagerDuty here
      console.error(`ALERT: Memory has grown for ${consecutiveIncreases} consecutive checks — possible leak. RSS: ${rssMB.toFixed(1)}MB`);
    }

    if (rssMB > 1024) { // 1GB threshold example
      console.error(`CRITICAL: RSS at ${rssMB.toFixed(1)}MB — consider restarting or investigating`);
    }
  }, 30_000); // check every 30 seconds
}

// In server.js:
startMemoryMonitor(app);

// Expose a debug endpoint (protect this in production!) to check memory live
app.get('/admin/memory', (req, res) => {
  const mem = process.memoryUsage();
  res.json({
    rss: (mem.rss / 1024 / 1024).toFixed(1) + ' MB',
    heapUsed: (mem.heapUsed / 1024 / 1024).toFixed(1) + ' MB',
    heapTotal: (mem.heapTotal / 1024 / 1024).toFixed(1) + ' MB',
    external: (mem.external / 1024 / 1024).toFixed(1) + ' MB',
  });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Adding event listeners inside a route handler/loop without ever removing them
```javascript
// WRONG: a new listener is registered on EVERY request — accumulates forever
app.get('/subscribe', (req, res) => {
  someEmitter.on('event', (data) => res.write(data)); // never removed!
});

// CORRECT: remove the listener once it's no longer needed (e.g., on response end)
app.get('/subscribe', (req, res) => {
  const handler = (data) => res.write(data);
  someEmitter.on('event', handler);
  res.on('close', () => someEmitter.removeListener('event', handler)); // cleanup
});
```

❌ Mistake 2: Using a plain object/Map as an unbounded cache
```javascript
// WRONG: cache grows forever, one entry per unique key ever seen
const cache = {};
function getCached(key, computeFn) {
  if (!cache[key]) cache[key] = computeFn();
  return cache[key];
}

// CORRECT: use a bounded LRU cache (e.g., npm 'lru-cache') with a max size
const { LRUCache } = require('lru-cache');
const cache = new LRUCache({ max: 500 }); // evicts least-recently-used beyond 500 entries
function getCachedFixed(key, computeFn) {
  if (!cache.has(key)) cache.set(key, computeFn());
  return cache.get(key);
}
```

---

## 🧠 Tricky Interview Question

```javascript
function createLogger() {
  const logs = [];
  return function log(message) {
    logs.push(message); // closure captures `logs`
    if (logs.length > 1000000) console.log('Too many logs!');
  };
}
const log = createLogger();
setInterval(() => log('heartbeat'), 10);
// ❓ Is this a memory leak? Why or why not?
```
Answer: **Yes, this IS a memory leak.** The closure returned by `createLogger()` holds a reference to the `logs` array via closure scope. Since `log()` is called every 10ms forever (via `setInterval` that's never cleared) and ALWAYS pushes to `logs` without ever removing old entries, the array grows unbounded — exactly like the `requestLog` example above, just hidden inside a closure instead of a module-level variable. The JS garbage collector CANNOT free `logs` because the returned `log` function (referenced by the still-running `setInterval`) keeps a live reference to it forever. Fix: bound the array size (shift old entries) or avoid accumulating state that's never needed again.

---

## ⚫ Interview Questions + Answers

Q1: What are the most common causes of memory leaks in Node.js?
A1: (1) Event listeners added but never removed (`EventEmitter.on()` without matching `removeListener`), (2) global/module-level arrays, objects, or Maps used as unbounded caches, (3) `setInterval`/`setTimeout` that are never cleared, keeping their closures (and any data they reference) alive forever, (4) closures capturing large objects/buffers longer than needed, (5) detached DOM-like references in server-rendering contexts, (6) unclosed database connections/streams piling up.

Q2: How do you take and analyze a heap snapshot in Node.js?
A2: Run the app with `node --inspect app.js`, open `chrome://inspect` in Chrome, click "inspect" to open DevTools, go to the Memory tab, and take a heap snapshot. Take 2-3 snapshots over time while exercising the suspected leaky code path, then use the "Comparison" view between snapshots — objects whose count keeps growing between snapshots (not stabilizing) are the leak source. The "Retainers" panel shows WHAT is holding a reference to the leaking object.

Q3: What's the difference between `rss`, `heapUsed`, and `heapTotal` in `process.memoryUsage()`?
A3: `rss` (Resident Set Size) is the total memory allocated to the Node process by the OS, including the V8 heap, buffers, and native code — the number to watch for OOM risk. `heapUsed` is the amount of the V8 JS heap currently in use. `heapTotal` is the total size V8 has allocated for the heap (may be larger than `heapUsed` since V8 pre-allocates). `external` is memory used by C++ objects bound to JS (like Buffers).

Q4: Why does `EventEmitter` warn "MaxListenersExceededWarning" and how does it relate to leaks?
A4: By default, `EventEmitter` warns when more than 10 listeners are added for a single event — this is a safety net specifically designed to catch the common leak pattern of adding listeners in a loop/per-request without removal. It's not a hard limit (`setMaxListeners()` can raise it), but seeing this warning is almost always a sign of a real leak that should be investigated, not silenced by just raising the limit.

Q5: How would you set up ongoing production monitoring to catch memory leaks before they cause an outage?
A5: Track `process.memoryUsage().rss` over time via an APM tool (New Relic, Datadog) or a custom metric pushed to Prometheus/Grafana, and alert when RSS shows a sustained upward trend without plateauing after garbage collection. Also configure a safety-net process manager (PM2, Kubernetes liveness probes) to automatically restart a process if memory exceeds a hard threshold, buying time to investigate without a full outage.

---

## 🔷 When to Use + When Not to Use
✅ Investigate memory leaks when:
- RSS/heap usage shows a steady upward trend over hours that never comes back down
- The process crashes periodically with OOM / "Reached heap limit" errors
- Response times degrade gradually the longer the process has been running

❌ Don't chase a "leak" when:
- Memory grows then plateaus (normal behavior — V8 pre-allocates heap space, this isn't a leak)
- A short-lived script/one-off process exits soon anyway (leaks only matter for long-running processes)

---

## 📊 Visual Diagram
```
MEMORY LEAK vs NORMAL GC BEHAVIOR:
──────────────────────────────────────────────
Normal (healthy):              Leak (unhealthy):
RSS                             RSS
 │     ╱╲    ╱╲    ╱╲            │           ╱─────
 │    ╱  ╲  ╱  ╲  ╱  ╲           │         ╱
 │   ╱    ╲╱    ╲╱    ╲          │       ╱
 │  ╱                            │     ╱
 │_╱____________________ time    │   ╱
  (grows then GC reclaims it)    │ ╱
                                  │╱________________ time
                                  (grows forever → OOM crash)

LEAK HUNTING PROCESS:
  1. Notice RSS trending up in monitoring
  2. node --inspect → Chrome DevTools → Memory tab
  3. Take snapshot 1 → exercise suspected code → snapshot 2
  4. Compare → find objects with growing count
  5. Check "Retainers" → find the reference keeping them alive
  6. Fix: removeListener / clearInterval / bounded cache
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memory leak | Memory never released, grows over time | कभी release न होने वाली memory |
| RSS | Total OS-allocated memory for the process | Process की total OS memory |
| Heap snapshot | Point-in-time capture of all JS objects in memory | किसी समय पर सभी objects का capture |
| Retainers | What's holding a reference to an object | Object को live रखने वाला reference |
| LRU cache | Bounded cache that evicts oldest/unused entries | Max size वाला cache |
| Closure leak | Closure keeps large data alive unnecessarily | Closure से data unnecessarily alive रहना |
| MaxListenersExceededWarning | Warning for >10 listeners on one event | 10 से ज़्यादा listeners की warning |

---

## ⚡ 3-Line Summary
English:
1. A memory leak happens when something keeps a reference to objects that are no longer needed, preventing garbage collection — common causes: unremoved event listeners, unbounded caches/arrays, uncleared timers.
2. Diagnose with heap snapshots (`node --inspect` + Chrome DevTools) comparing memory state over time to find objects that keep growing in count.
3. Fix by removing listeners on cleanup, bounding caches (LRU), clearing timers, and avoiding closures that hold large data longer than necessary.

Hindi:
1. Memory leak तब होता है जब कुछ उन objects का reference रखे रहता है जिनकी ज़रूरत नहीं — common causes: न हटाए गए event listeners, unbounded caches/arrays, clear न हुए timers।
2. Heap snapshots (`node --inspect` + Chrome DevTools) से diagnose करो, समय के साथ memory state compare करके देखो कौन से objects count में बढ़ते रहते हैं।
3. Cleanup पर listeners हटाओ, caches को bound (LRU) करो, timers clear करो, और बड़े data को ज़रूरत से ज़्यादा समय तक रखने वाले closures से बचो।

---

## ➡️ Next Topic
**218. CPU Profiling in Node** — CPU-heavy functions को profile करके असली performance bottleneck ढूंढना।
