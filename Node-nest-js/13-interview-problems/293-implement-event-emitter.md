# 293. Implement Event Emitter
# हिंदी में: Event Emitter खुद बनाना (Implementation)

---

## 🔵 Simple Definition (English)
Implementing your own **EventEmitter** means building the `on`/`emit`/`off`/`once` machinery that Node's built-in `events` module provides — a map of event names to arrays of listener functions, called synchronously when `emit()` fires. This is a classic interview exercise to prove you understand the Observer pattern internals.

## 🔵 सरल परिभाषा (Hindi)
खुद का **EventEmitter** बनाने का मतलब है `on`/`emit`/`off`/`once` जैसी machinery खुद implement करना — event names को listener functions के arrays से map करना, जो `emit()` call होने पर synchronously चलते हैं। यह एक classic interview exercise है जो Observer pattern की internals समझ दिखाती है।

---

## 🔴 Problem it Solves
Many systems need decoupled components to react to events without being tightly coupled (direct function calls). Implementing EventEmitter from scratch demonstrates understanding of: data structures for listener storage, synchronous vs asynchronous dispatch, memory leak risks (unremoved listeners), and the `once` auto-removal pattern — all foundational to understanding how Node's core (`http`, `stream`, `process`) is built on EventEmitter.

## 🔴 यह क्यों बना? (Hindi)
बहुत से systems को decoupled components चाहिए जो events पर react करें बिना tightly coupled (direct function calls) हुए। EventEmitter खुद बनाना दिखाता है: listener storage के लिए data structures, synchronous vs asynchronous dispatch, memory leak risk (listeners न हटाना), और `once` auto-removal pattern — ये सब समझना ज़रूरी है क्योंकि Node का core (`http`, `stream`, `process`) EventEmitter पर ही बना है।

---

## 🟢 How it Works — Step by Step

Step 1 → Maintain an internal object/Map: `{ eventName: [listener1, listener2, ...] }`.
Step 2 → `on(event, listener)` pushes the listener into that event's array (creating the array if it doesn't exist).
Step 3 → `emit(event, ...args)` looks up the array for that event and calls each listener synchronously with `...args`.
Step 4 → `off(event, listener)` finds and removes that specific listener from the array (reference equality).
Step 5 → `once(event, listener)` wraps the listener in a function that calls the original then immediately unregisters itself.
Step 6 → Optionally cap `maxListeners` per event and warn on exceeding it (Node does this — default 10) to catch memory leaks.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Internal object/Map रखो: `{ eventName: [listener1, listener2, ...] }`।
Step 2 → `on(event, listener)` उस event के array में listener push करता है (न हो तो array बनाता है)।
Step 3 → `emit(event, ...args)` उस event का array लेकर हर listener को synchronously `...args` के साथ call करता है।
Step 4 → `off(event, listener)` array से वह specific listener (reference equality से) हटाता है।
Step 5 → `once(event, listener)` original listener को wrap करके एक function बनाता है जो call होने पर खुद को unregister कर लेता है।
Step 6 → `maxListeners` per event optional cap लगाओ और exceed होने पर warn करो (Node default 10 करता है) — memory leaks पकड़ने के लिए।

---

## 🟡 Real World Example
**Flipkart's order pipeline** internally uses an EventEmitter-based bus: `OrderService` emits `order:placed`, and independent modules — `InventoryService`, `NotificationService`, `AnalyticsService` — each `.on('order:placed', ...)` without `OrderService` knowing they exist. This is exactly the pattern you implement from scratch here; understanding the internals helps you debug real issues like "why did my listener fire twice" (forgot to `off` an old one) or "why is memory growing" (listeners never removed on disconnect).

## 🟡 Real Example Hindi mein
**Flipkart का order pipeline** internally EventEmitter-based bus use करता है: `OrderService` `order:placed` emit करता है, और independent modules — `InventoryService`, `NotificationService`, `AnalyticsService` — हर एक `.on('order:placed', ...)` करते हैं बिना `OrderService` को उनके बारे में पता हुए। यही pattern आप यहाँ scratch से implement करते हो; internals समझना real issues debug करने में मदद करता है जैसे "listener दो बार क्यों चला" (पुराना `off` करना भूल गए) या "memory क्यों बढ़ रही" (disconnect पर listeners कभी नहीं हटे)।

---

## 💻 Code Example — Basic

```javascript
// my-event-emitter-basic.js
// A minimal EventEmitter implementation from scratch. Run: node my-event-emitter-basic.js

class MyEventEmitter {
  constructor() {
    this.listeners = {}; // { eventName: [fn1, fn2, ...] }
  }

  // Register a listener for an event
  on(event, listener) {
    if (!this.listeners[event]) this.listeners[event] = []; // lazily create the array
    this.listeners[event].push(listener);
    return this; // enable chaining: emitter.on('a', fn).on('b', fn2)
  }

  // Remove a specific listener for an event
  off(event, listener) {
    if (!this.listeners[event]) return this;
    // Filter out the matching listener by reference
    this.listeners[event] = this.listeners[event].filter(l => l !== listener);
    return this;
  }

  // Fire all listeners for an event, synchronously, in registration order
  emit(event, ...args) {
    if (!this.listeners[event]) return false; // no listeners -> nothing to do
    // Slice to a copy — protects against a listener mutating the array mid-iteration
    this.listeners[event].slice().forEach(listener => listener(...args));
    return true;
  }

  // Register a listener that auto-removes itself after firing once
  once(event, listener) {
    const wrapper = (...args) => {
      this.off(event, wrapper); // remove BEFORE calling, in case listener re-emits same event
      listener(...args);
    };
    this.on(event, wrapper);
    return this;
  }
}

// --- Demo ---
const emitter = new MyEventEmitter();

function onOrderPlaced(orderId) {
  console.log(`Listener A: order ${orderId} placed`);
}
emitter.on('order:placed', onOrderPlaced);

emitter.once('order:placed', (orderId) => {
  console.log(`Listener B (once): order ${orderId} placed — won't fire again`);
});

emitter.emit('order:placed', 'ORD001'); // both fire
emitter.emit('order:placed', 'ORD002'); // only A fires, B already removed

emitter.off('order:placed', onOrderPlaced);
emitter.emit('order:placed', 'ORD003'); // nothing fires now
```

## 💻 Code Example — Advanced

```javascript
// my-event-emitter-advanced.js
// Production-style EventEmitter: maxListeners guard, error event handling, wildcard support, async-safe emit

class RobustEventEmitter {
  constructor({ maxListeners = 10 } = {}) {
    this.listeners = new Map(); // Map gives cleaner has()/delete() semantics than plain object
    this.maxListeners = maxListeners;
  }

  on(event, listener) {
    if (typeof listener !== 'function') throw new TypeError('listener must be a function');

    if (!this.listeners.has(event)) this.listeners.set(event, []);
    const arr = this.listeners.get(event);
    arr.push(listener);

    // Memory-leak guard — Node's real EventEmitter does exactly this (default limit 10)
    if (arr.length > this.maxListeners) {
      console.warn(
        `Warning: possible EventEmitter memory leak detected. ` +
        `${arr.length} listeners added for event "${event}". Use setMaxListeners() to increase limit.`
      );
    }
    return this;
  }

  off(event, listener) {
    const arr = this.listeners.get(event);
    if (!arr) return this;
    const idx = arr.indexOf(listener);
    if (idx !== -1) arr.splice(idx, 1);
    if (arr.length === 0) this.listeners.delete(event); // cleanup empty arrays
    return this;
  }

  once(event, listener) {
    const wrapper = (...args) => {
      this.off(event, wrapper);
      listener(...args);
    };
    wrapper.original = listener; // keep reference so off(event, listener) can also find/remove a 'once' wrapper
    this.on(event, wrapper);
    return this;
  }

  // emit catches synchronous listener errors so one bad listener doesn't crash emit() for others
  emit(event, ...args) {
    const arr = this.listeners.get(event);

    // Special case: 'error' event with no listeners should throw (mirrors Node's real behavior)
    if (event === 'error' && (!arr || arr.length === 0)) {
      throw args[0] instanceof Error ? args[0] : new Error(String(args[0]));
    }

    if (!arr || arr.length === 0) return false;

    arr.slice().forEach(listener => {
      try {
        listener(...args);
      } catch (err) {
        // Isolate failures — emit the error as its own event instead of crashing the whole emit loop
        if (event !== 'error') this.emit('error', err);
        else throw err; // avoid infinite loop if error listener itself throws
      }
    });
    return true;
  }

  listenerCount(event) {
    return this.listeners.get(event)?.length || 0;
  }

  removeAllListeners(event) {
    if (event) this.listeners.delete(event);
    else this.listeners.clear();
    return this;
  }
}

// --- Demo: isolated listener failure doesn't crash other listeners ---
const bus = new RobustEventEmitter({ maxListeners: 2 });
bus.on('error', (err) => console.error('Caught isolated error:', err.message));

bus.on('data', () => { throw new Error('listener 1 crashed'); });
bus.on('data', () => console.log('listener 2 still ran fine'));

bus.emit('data');
console.log('listenerCount for data:', bus.listenerCount('data'));

module.exports = { MyEventEmitter: RobustEventEmitter };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — using a custom EventEmitter as an in-process event bus for order processing
const express = require('express');
const { MyEventEmitter } = require('./my-event-emitter-advanced');

const app = express();
app.use(express.json());

const bus = new MyEventEmitter();

// Decoupled listeners — none of these know about each other or about Express
bus.on('order:placed', (order) => console.log(`[Inventory] reserving stock for ${order.id}`));
bus.on('order:placed', (order) => console.log(`[Notification] sending confirmation for ${order.id}`));
bus.on('error', (err) => console.error('[Bus Error]', err.message));

app.post('/orders', (req, res) => {
  const order = { id: 'ORD' + Date.now(), ...req.body };
  // Save to DB here in real app...
  bus.emit('order:placed', order); // fire event, handlers run synchronously before response
  res.status(201).json(order);
});

app.listen(3000, () => console.log('Server with custom event bus on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutating the listeners array while iterating during `emit` (e.g., a listener calls `off` on another listener)
✅ Correct: Iterate over a copy (`.slice()`) so removals mid-emit don't skip/break iteration

```javascript
// Wrong — if listener2 calls emitter.off(event, listener3) during iteration, forEach can skip entries
this.listeners[event].forEach(l => l(...args));

// Right — iterate a snapshot copy
this.listeners[event].slice().forEach(l => l(...args));
```

❌ Mistake 2: Not handling errors thrown inside listeners — one bad listener crashes the whole process
✅ Correct: Wrap each listener call in try/catch and route failures to an 'error' event instead of letting them propagate uncaught

```javascript
// Wrong
arr.forEach(l => l(...args)); // one throw here stops ALL remaining listeners from running

// Right
arr.forEach(l => { try { l(...args); } catch (e) { this.emit('error', e); } });
```

---

## 🧠 Tricky Interview Question

```javascript
const emitter = new MyEventEmitter();

emitter.once('greet', () => console.log('hello once'));
emitter.emit('greet'); // fires -> removes itself
emitter.emit('greet'); // ???

// Separately:
function fn() { console.log('fn called'); }
emitter.on('x', fn);
emitter.on('x', fn); // same function reference added TWICE
emitter.emit('x');
emitter.off('x', fn); // removes only ONE instance
emitter.emit('x');
```
Answer: First block: only `"hello once"` prints once — the second `emit('greet')` finds no listeners since `once` removed itself after firing. Second block: `emit('x')` after double `on(fn)` prints `"fn called"` **twice** (same function registered twice = two separate array entries, both fire). After one `off(x, fn)`, only ONE instance is removed (because of `indexOf` + `splice` removing just the first match), so the final `emit('x')` still prints `"fn called"` **once more** — this mirrors Node's real `EventEmitter` behavior exactly, and is a common gotcha: `off`/`removeListener` only removes ONE matching instance per call, not all of them.

---

## ⚫ Interview Questions + Answers

Q1: Why does `emit()` call listeners synchronously instead of queuing them as microtasks?
A1: Node's real `EventEmitter.emit()` is intentionally synchronous — it calls every listener immediately, in registration order, before returning. This gives predictable ordering and avoids surprises where code after `emit()` runs before listeners do. If you need async behavior, listeners themselves can be async functions, but `emit()` doesn't await them.

Q2: What happens if you emit an 'error' event with no listeners attached, in Node's real EventEmitter?
A2: Node throws the error synchronously (crashing the process if uncaught), specifically because 'error' is treated as a special event — this is a deliberate design to force developers to handle errors explicitly rather than silently swallowing them.

Q3: How would you implement a `once` listener without wrapping it in an extra function?
A3: You generally can't avoid a wrapper cleanly, because `once` needs to call `off` upon firing — but since `off` typically matches by function reference, the wrapper must either be returned/tracked or store a reference to the original (as shown via `wrapper.original`) so that calling `off(event, originalListener)` can also find and remove the wrapped version.

Q4: Why does Node warn about "possible EventEmitter memory leak detected"?
A4: Because each `.on()` call without a matching cleanup accumulates listeners in the array — in long-running servers, repeatedly attaching listeners (e.g., inside a request handler without removing old ones) causes unbounded memory growth and, eventually, the listeners firing many times for a single event. The default cap of 10 is a sane heuristic trip-wire, adjustable via `setMaxListeners()`.

Q5: How is Node's `Stream`, `http.Server`, and `process` all related to EventEmitter?
A5: They all **extend** `EventEmitter` internally. `http.Server` emits `'request'`, `'connection'`, `'close'`; streams emit `'data'`, `'end'`, `'error'`; `process` emits `'exit'`, `'uncaughtException'`. Understanding EventEmitter internals (like you built here) directly explains how these core Node APIs notify your code of lifecycle events.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need decoupled, in-process pub/sub communication between modules
- Building libraries/frameworks that need lifecycle hooks (open/close/error/data events)

❌ Avoid when:
- Cross-process or cross-service communication is needed (use a real message queue/broker, not in-memory EventEmitter)
- You need guaranteed delivery/ordering/persistence (EventEmitter is fire-and-forget, in-memory only)

---

## 📊 Visual Diagram
```
 emitter.on('order:placed', A) ──┐
 emitter.on('order:placed', B) ──┼──▶ listeners['order:placed'] = [A, B]
 emitter.once('order:placed', C)─┘                  (C is wrapped: calls off() then C)

 emitter.emit('order:placed', data)
          │
          ▼
   for each listener in [A, B, wrappedC].slice():
          call listener(data)   ← synchronous, in order
          │
          ▼
   wrappedC removes itself from array after firing
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Observer pattern | Subjects notify subscribed observers | Subjects, subscribed observers को notify करते हैं |
| Listener | Function registered to respond to an event | Event पर respond करने वाला function |
| Synchronous dispatch | Listeners called immediately, in order | Listeners तुरंत, order में call होते हैं |
| Memory leak (listeners) | Unremoved listeners accumulating over time | न हटे listeners का समय के साथ जमा होना |
| Wrapper function | Function wrapping another to add behavior | दूसरे function को wrap करने वाला function |

---

## ⚡ 3-Line Summary
English: A custom EventEmitter maps event names to listener arrays, calls them synchronously on `emit`, and implements `once` via a self-removing wrapper. Production versions add max-listener leak warnings and isolate listener errors so one failure doesn't break others.
Hindi: Custom EventEmitter event names को listener arrays में map करता है, `emit` पर उन्हें synchronously call करता है, और `once` को self-removing wrapper से implement करता है। Production versions max-listener leak warning और listener error isolation भी add करते हैं।

---

## ➡️ Next Topic
**294. Implement Rate Limiter** — token bucket and sliding window algorithms from scratch.
