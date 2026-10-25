# 46. EventEmitter — Complete Guide
# हिंदी में: EventEmitter — Advanced Patterns और Memory Leak Debugging

---

## 🔵 Simple Definition (English)
Beyond basic `on()`/`emit()`, `EventEmitter` has a full API for advanced control: `prependListener()` (run first), `eventNames()` (inspect registered events), `listenerCount()` (debug leaks), `removeAllListeners()` (cleanup), and static helpers like `EventEmitter.once(emitter, event)` which returns a Promise. This guide covers the patterns needed to use EventEmitter safely and efficiently in production systems.

## 🔵 सरल परिभाषा (Hindi)
Basic `on()`/`emit()` के आगे, `EventEmitter` में advanced control के लिए पूरा API है: `prependListener()` (पहले चलाने के लिए), `eventNames()` (registered events देखने के लिए), `listenerCount()` (leaks debug करने के लिए), `removeAllListeners()` (cleanup), और static helpers जैसे `EventEmitter.once(emitter, event)` जो Promise return करता है। यह guide production में EventEmitter को safely use करने के patterns cover करता है।

---

## 🔴 Problem it Solves
Basic `on()`/`emit()` is enough for simple cases, but real production systems hit edge cases: listeners added in a loop without cleanup causing memory leaks that slowly degrade server performance over days; needing a listener to run FIRST (before others) for setup/validation; needing to `await` an event instead of using a callback; needing to debug "why is this emitter using so much memory" in production. The extended EventEmitter API and Node's `events` module utilities (`once(emitter, event)`, `on(emitter, event)` as async iterator) solve these without external libraries.

## 🔴 यह क्यों बना? (Hindi)
Basic `on()`/`emit()` simple cases के लिए काफ़ी है, पर production systems में edge cases आते हैं: loop में listeners add होकर memory leak होना; किसी listener को सबसे पहले चलाना; event को `await` करना callback की जगह; production में "यह emitter इतनी memory क्यों use कर रहा" debug करना। Extended API और `events` module utilities (`once(emitter, event)`, async iterator) यह सब external libraries के बिना solve करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `prependListener(event, fn)` — adds the listener to the FRONT of the listener array, so it runs before previously-registered ones (rarely needed, but useful for setup/guard logic).
Step 2 → `eventNames()` — returns an array of all event names that currently have at least one listener — useful for runtime introspection/debugging.
Step 3 → `listenerCount(emitter, event)` (static) or `emitter.listenerCount(event)` — count active listeners for an event, the #1 tool for spotting leaks.
Step 4 → `removeAllListeners([event])` — strips all listeners for one event, or ALL events if no argument — used during cleanup/teardown (e.g. closing a connection).
Step 5 → `EventEmitter.once(emitter, eventName)` (Node 11+, static method, NOT the instance method) — returns a Promise that resolves with the event's arguments on the next emission — lets you `await` an event instead of nesting callbacks.
Step 6 → `events.on(emitter, eventName)` (Node 13+) — returns an async iterator, letting you `for await (const [data] of events.on(emitter, 'data'))` to process events as an async stream.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `prependListener()` — listener को array के आगे add करता है, पहले चलता है।
Step 2 → `eventNames()` — सभी active event names की list देता है।
Step 3 → `listenerCount()` — किसी event के active listeners count करता है, leak debug करने के लिए सबसे अच्छा tool।
Step 4 → `removeAllListeners([event])` — सारे listeners हटाता है, cleanup के लिए।
Step 5 → `EventEmitter.once(emitter, eventName)` (static) — Promise return करता है, `await` करने के लिए।
Step 6 → `events.on(emitter, eventName)` — async iterator देता है, `for await` से events process करने के लिए।

---

## 🟡 Real World Example
**Paytm's payment gateway connection pool:** A `PaymentGatewayConnection` EventEmitter-based class manages a pool of connections to the bank's API. Each connection object can emit `'connected'`, `'disconnected'`, `'error'`. During a production incident, the on-call engineer noticed memory climbing — using `connection.listenerCount('disconnected')` in a debug endpoint revealed 50,000 listeners on a single emitter (should've been 1) because a retry-handler was calling `.on()` in a loop without ever cleaning up. Fixing it meant switching to `.once()` and calling `removeAllListeners()` during reconnect.

## 🟡 Real Example Hindi mein
**Paytm payment gateway connection pool:** Production incident में memory climb हो रही थी — `listenerCount('disconnected')` check करने पर पता चला एक emitter पर 50,000 listeners थे (होने चाहिए थे 1), क्योंकि retry-handler loop में `.on()` call कर रहा था बिना cleanup के। Fix: `.once()` use करो और reconnect पर `removeAllListeners()` call करो।

---

## 💻 Code Example — Basic
```javascript
// eventemitter-advanced-basics.js
const EventEmitter = require('events');
const emitter = new EventEmitter();

// 1. prependListener -- runs BEFORE normally-registered listeners
emitter.on('request', () => console.log('2. Handle request'));
emitter.prependListener('request', () => console.log('1. Validate request (runs first)'));
emitter.emit('request');
// Output:
// 1. Validate request (runs first)
// 2. Handle request

// 2. eventNames() -- introspect which events have listeners
emitter.on('data', () => {});
emitter.on('error', () => {});
console.log(emitter.eventNames()); // [ 'request', 'data', 'error' ]

// 3. listenerCount() -- debugging tool for memory leaks
console.log(emitter.listenerCount('request')); // 2
console.log(emitter.listenerCount('nonexistent')); // 0

// 4. removeAllListeners() -- cleanup
emitter.removeAllListeners('data'); // remove only 'data' listeners
console.log(emitter.eventNames()); // [ 'request', 'error' ] -- 'data' gone

emitter.removeAllListeners(); // remove EVERYTHING
console.log(emitter.eventNames()); // []

// 5. getMaxListeners / setMaxListeners
const e2 = new EventEmitter();
console.log(e2.getMaxListeners()); // 10 (default)
e2.setMaxListeners(50); // raise limit for high-fanout emitters
```

## 💻 Code Example — Advanced
```javascript
// eventemitter-advanced-production.js
const EventEmitter = require('events');
const { once, on } = require('events'); // static module-level helpers

// ─── 1. AWAIT AN EVENT WITH events.once() (static, Promise-based) ────────────
async function waitForConnection(connector) {
  console.log('Waiting for connection...');
  const [connectionInfo] = await once(connector, 'connected'); // pauses until emitted
  console.log('Connected!', connectionInfo);
  return connectionInfo;
}

// ─── 2. ASYNC ITERATION OVER EVENTS WITH events.on() ──────────────────────────
async function processOrderStream(orderEmitter) {
  // for-await loop processes each emitted event one at a time, in order
  for await (const [order] of on(orderEmitter, 'order-placed')) {
    console.log('Processing order:', order.id);
    if (order.id === 'STOP') break; // break out of the async iterator cleanly
  }
  console.log('Stopped processing orders');
}

// ─── 3. MEMORY LEAK DETECTION PATTERN ─────────────────────────────────────────
class ConnectionPool extends EventEmitter {
  constructor() {
    super();
    this.setMaxListeners(20); // explicit limit based on expected usage
  }

  monitorLeaks() {
    // Run periodically (e.g. via setInterval) to catch leaks before they crash the app
    setInterval(() => {
      for (const eventName of this.eventNames()) {
        const count = this.listenerCount(eventName);
        if (count > 15) {
          console.warn(`[LEAK WARNING] Event "${eventName}" has ${count} listeners!`);
        }
      }
    }, 10000);
  }
}

// ─── 4. PROPER CLEANUP PATTERN (avoiding leaks in request-scoped listeners) ───
class RequestScopedListener {
  constructor(emitter) {
    this.emitter = emitter;
    this.handler = this.handleEvent.bind(this);
  }

  handleEvent(data) {
    console.log('Handling scoped event:', data);
  }

  attach() {
    this.emitter.on('update', this.handler);
  }

  detach() {
    // CRITICAL: always detach when the scope ends (request finishes, component unmounts)
    this.emitter.off('update', this.handler);
  }
}

// ─── DEMO ──────────────────────────────────────────────────────────────────────
(async () => {
  const connector = new EventEmitter();
  setTimeout(() => connector.emit('connected', { host: 'db.internal' }), 100);
  await waitForConnection(connector);

  const orderEmitter = new EventEmitter();
  setTimeout(() => orderEmitter.emit('order-placed', { id: 'ORD-1' }), 50);
  setTimeout(() => orderEmitter.emit('order-placed', { id: 'ORD-2' }), 100);
  setTimeout(() => orderEmitter.emit('order-placed', { id: 'STOP' }), 150);
  await processOrderStream(orderEmitter);
})();
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const EventEmitter = require('events');
const { once } = require('events');
const app = express();

const jobEvents = new EventEmitter();
jobEvents.setMaxListeners(100); // app-wide bus expects many concurrent listeners

// Simulate a background job system emitting completion events
function startBackgroundJob(jobId) {
  setTimeout(() => {
    jobEvents.emit(`job-complete-${jobId}`, { jobId, result: 'success' });
  }, 2000);
}

// Long-polling endpoint: wait for a specific job using events.once() + Promise
app.get('/jobs/:id/wait', async (req, res) => {
  const jobId = req.params.id;
  startBackgroundJob(jobId);

  try {
    // await the event directly -- cleaner than nested callbacks
    const [result] = await once(jobEvents, `job-complete-${jobId}`);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: 'Job wait failed' });
  }
});

// Debug endpoint to catch listener leaks in production
app.get('/debug/listeners', (req, res) => {
  const report = jobEvents.eventNames().map((name) => ({
    event: name,
    count: jobEvents.listenerCount(name),
  }));
  res.json(report);
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Confusing `EventEmitter.once(emitter, event)` (static, Promise) with `emitter.once(event, fn)` (instance, callback)
```javascript
// Wrong -- mixing them up causes confusing bugs
const { once } = require('events');
emitter.once('ready', data => console.log(data)); // instance method -- callback style, fine
const result = once(emitter, 'ready'); // static -- returns a PROMISE, not a value!
console.log(result); // Promise { <pending> } -- forgot to await it

// Correct
const [data] = await once(emitter, 'ready'); // static method MUST be awaited
```

❌ Mistake 2: Adding listeners inside request handlers without removing them
```javascript
// Wrong -- every request adds a new listener that's never removed (leak!)
app.get('/status', (req, res) => {
  dbEmitter.on('health-check', (status) => res.json(status));
});

// Correct -- use once() for single-fire use cases, or explicitly detach
app.get('/status', (req, res) => {
  dbEmitter.once('health-check', (status) => res.json(status));
  dbEmitter.emit('request-health-check');
});
```

❌ Mistake 3: Ignoring the `MaxListenersExceededWarning` instead of investigating it
```javascript
// Wrong -- silencing the symptom hides a real leak
emitter.setMaxListeners(0); // 0 = unlimited, hides the warning forever -- DANGEROUS

// Correct -- investigate WHY so many listeners exist; fix the root cause (leak)
// Only raise the limit deliberately if you've confirmed the high count is expected
emitter.setMaxListeners(50); // explicit, reasoned limit, not "unlimited"
```

---

## 🧠 Tricky Interview Question
```javascript
const EventEmitter = require('events');
const emitter = new EventEmitter();

emitter.on('x', () => console.log('A'));
emitter.on('x', () => {
  console.log('B');
  emitter.emit('x'); // emitting from WITHIN a listener
});
emitter.on('x', () => console.log('C'));

emitter.emit('x');
```
Answer: Output is `A`, `B`, `A`, `B`, `C`, `C` — wait, let's trace carefully: first `emit('x')` calls listeners in order: A logs "A", then B logs "B" and immediately calls `emitter.emit('x')` again (nested, synchronous) — this NESTED emit runs to completion first: A, B (which emits AGAIN — but JS doesn't infinite loop here because each nested emit completes fully)... Actually the real answer: nested emits called from within a listener execute fully (A, B, C) before returning control to continue the outer loop, and this repeats every time B fires until stack/logic stops it. In this exact example (B always re-emits unconditionally), it causes **infinite recursion and a stack overflow** (`RangeError: Maximum call stack size exceeded`). The key lesson: emitting the SAME event from within one of its own listeners, without a guard/base-case, causes unbounded recursion — a classic EventEmitter gotcha.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `emitter.once(event, fn)` and `EventEmitter.once(emitter, event)`?
A1: `emitter.once(event, fn)` is the INSTANCE method — registers a callback-style listener that fires once. `EventEmitter.once(emitter, event)` is a STATIC module-level function (Node 11+) that returns a PROMISE resolving with an array of the event's emitted arguments on the next occurrence — designed for `await`-based flows instead of callbacks. They solve the same "listen once" problem with different async styles.

Q2: How do you safely debug a suspected EventEmitter memory leak in production?
A2: Use `emitter.eventNames()` to list all events with active listeners, then `emitter.listenerCount(eventName)` for each to find abnormally high counts (the default warning threshold is 10). Periodically logging/alerting on these counts (e.g. in a health-check endpoint or interval) surfaces leaks before they degrade performance. The root cause is almost always listeners added repeatedly (in a loop, on every request) without a matching `removeListener`/`once`.

Q3: What does `prependListener()` do and when would you use it?
A3: It adds a listener to the FRONT of the internal listener array for an event, so it executes before previously-registered listeners (normal `on()` appends to the end). Rarely needed, but useful when a cross-cutting concern (e.g. a validation or logging listener) must run before business-logic listeners regardless of registration order.

Q4: What does `events.on(emitter, eventName)` (the async iterator helper) let you do that regular listeners can't?
A4: It converts an EventEmitter's event stream into an `AsyncIterable`, letting you use `for await (const [data] of events.on(emitter, 'event'))` to process events sequentially with normal control flow (`break`, `continue`, `try/catch`, `await` inside the loop body) — much cleaner than manually managing callback-based listener state for sequential/ordered async event processing.

Q5: Does calling `removeAllListeners()` with no arguments affect listeners for the `'error'` event too?
A5: Yes — `removeAllListeners()` with no argument removes ALL listeners for ALL events, including `'error'`. This is dangerous: if the emitter later emits an `'error'` event with no listener attached, it crashes the process. Best practice: always pass a specific event name to `removeAllListeners(eventName)` unless you are fully tearing down the emitter and know no further events (especially errors) will occur.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging memory leaks via `listenerCount()`/`eventNames()` in long-running servers
- Converting event-based APIs to async/await flows with `events.once()` or `events.on()`
- Building connection-pool/lifecycle classes that need ordered listener execution (`prependListener`)

❌ Avoid when:
- Simpler Promise-based APIs would suffice (don't force an EventEmitter pattern where a single async function call works)
- You need cross-process or persistent event delivery — use a real message broker instead
- `setMaxListeners(0)` (unlimited) as a quick fix — always find the real leak first

---

## 📊 Visual Diagram
```
LISTENER EXECUTION ORDER:

  prependListener(fn0)  ──┐
  on(fn1)                 ├──► emit() runs: fn0 → fn1 → fn2 (in this order)
  on(fn2)                ──┘

MEMORY LEAK DETECTION FLOW:

  emitter.eventNames()  →  ['connect', 'disconnect', 'error']
         │
         ▼
  for each event: emitter.listenerCount(event)
         │
         ▼
  'disconnect': 50,000  ←──  🚨 LEAK! (should be 1)
         │
         ▼
  Find the code calling .on('disconnect', ...) in a loop without cleanup
         │
         ▼
  Fix: use .once() OR explicitly .off()/.removeAllListeners() during teardown

ASYNC PATTERNS:
  Callback style:   emitter.once('ready', (data) => { ... })
  Promise style:     const [data] = await EventEmitter.once(emitter, 'ready')
  Async iterator:    for await (const [data] of events.on(emitter, 'ready')) { ... }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| prependListener | Add listener to front, runs first | Listener को आगे add करना |
| eventNames() | List all active event names | सभी active events की list |
| listenerCount() | Count listeners for leak detection | Leak detection के लिए listener count |
| removeAllListeners() | Strip listeners (one or all events) | सभी listeners हटाना |
| events.once() (static) | Promise-based single event await | Promise-based event await |
| events.on() (static) | Async iterator over events | Events पर async iterator |
| MaxListenersExceededWarning | Default leak-detection warning | Default leak warning |

---

## ⚡ 3-Line Summary
English: Beyond `on()`/`emit()`, EventEmitter offers `prependListener`, `eventNames()`, `listenerCount()` for leak debugging, and static `events.once()`/`events.on()` for Promise/async-iterator-based event handling. Always clean up listeners (`off`/`once`) to avoid memory leaks, and never emit the same event unconditionally from within its own listener (infinite recursion).

Hindi: `on()`/`emit()` के आगे, EventEmitter में `prependListener`, `eventNames()`, `listenerCount()` (leak debug के लिए), और static `events.once()`/`events.on()` (Promise/async-iterator के लिए) हैं। Listeners हमेशा cleanup करो, और अपने ही listener से unconditionally event emit मत करो (infinite recursion)।

---

## ➡️ Next Topic
**48. Readable Streams** — detailed look at Readable stream modes (paused vs flowing), `_read()` implementation, and real file/network streaming patterns.
