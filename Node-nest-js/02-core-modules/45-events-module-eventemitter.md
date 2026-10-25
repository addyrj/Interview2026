# 45. events Module — EventEmitter
# हिंदी में: events Module — EventEmitter Basics

---

## 🔵 Simple Definition (English)
The **`events`** module exports the **`EventEmitter`** class — the foundation of Node.js's event-driven architecture. An object can `emit()` named events, and other code can `on()` (listen) for those events and react. Almost every core Node API (streams, HTTP server, `process`, TCP sockets) is built on top of `EventEmitter`.

## 🔵 सरल परिभाषा (Hindi)
**`events`** module **`EventEmitter`** class export करता है — Node.js के event-driven architecture की foundation। कोई object named events `emit()` कर सकता है, और दूसरा code उन events को `on()` से listen करके react कर सकता है। लगभग हर core Node API (streams, HTTP server, `process`, TCP sockets) `EventEmitter` पर बना है।

---

## 🔴 Problem it Solves
Without events, code must constantly poll ("is data ready yet? is data ready yet?") or use deeply nested callbacks to react to things happening asynchronously at unpredictable times (a new HTTP connection, a chunk of file data arriving, a child process finishing). `EventEmitter` decouples the "thing that happens" from "the code that reacts to it" — a producer just announces `emit('something-happened', data)` without knowing or caring who's listening, and listeners subscribe independently. This pattern scales to any number of listeners and keeps producer/consumer code loosely coupled.

## 🔴 यह क्यों बना? (Hindi)
Events के बिना, code को लगातार poll करना पड़ता ("data ready है क्या?") या deeply nested callbacks use करने पड़ते असामान्य समय पर होने वाली async events (नया HTTP connection, file data chunk, child process खत्म होना) को handle करने के लिए। `EventEmitter` "event होना" को "event पर react करना" से decouple करता है — producer सिर्फ `emit()` करता है, listener की फ़िक्र नहीं करता; listeners independently subscribe करते हैं। यह pattern किसी भी संख्या के listeners तक scale करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an emitter: `const emitter = new EventEmitter();` (or extend it: `class MyClass extends EventEmitter`).
Step 2 → Register listeners: `emitter.on('eventName', (data) => { ... })` — can register multiple listeners for the same event, they all run in registration order.
Step 3 → Emit the event: `emitter.emit('eventName', data)` — synchronously calls every registered listener in order, passing `data` as arguments.
Step 4 → One-time listeners: `emitter.once('eventName', fn)` — automatically removed after first invocation.
Step 5 → Error handling: the special `'error'` event — if emitted with no listener attached, Node **throws and crashes the process**. Always attach an `'error'` listener on any EventEmitter that might emit one.
Step 6 → Cleanup: `emitter.removeListener('eventName', fn)` or `emitter.off('eventName', fn)` to unregister, preventing memory leaks.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Emitter बनाओ: `new EventEmitter()` या extend करो।
Step 2 → Listeners register करो: `emitter.on('eventName', fn)` — एक ही event के लिए multiple listeners हो सकते हैं, सभी registration order में चलते हैं।
Step 3 → Event emit करो: `emitter.emit('eventName', data)` — synchronously हर registered listener को call करता है।
Step 4 → One-time listener: `emitter.once()` — पहली call के बाद automatically remove हो जाता है।
Step 5 → Error handling: special `'error'` event — बिना listener के emit होने पर Node **process crash कर देता है**। हमेशा `'error'` listener attach करो।
Step 6 → Cleanup: `removeListener()`/`off()` से unregister करो, memory leak से बचने के लिए।

---

## 🟡 Real World Example
**Swiggy order tracking system:** An `OrderTracker` class extends `EventEmitter`. When the restaurant accepts the order, it emits `'accepted'`. When the delivery partner picks it up, it emits `'picked-up'`. The notification service listens for `'accepted'` to send a push notification, the analytics service listens for the same event to log metrics, and the SMS service listens for `'picked-up'`. All three services react independently without the `OrderTracker` knowing they exist — adding a new listener (like a WhatsApp notification service) requires zero changes to `OrderTracker` itself.

## 🟡 Real Example Hindi mein
**Swiggy order tracking:** `OrderTracker` class `EventEmitter` extend करती है। Restaurant order accept करे तो `'accepted'` emit होता है। Delivery partner pickup करे तो `'picked-up'`। Notification service, analytics service, SMS service — सब independently listen करते हैं, बिना `OrderTracker` को पता चले। नया listener जोड़ने के लिए `OrderTracker` में कोई बदलाव नहीं चाहिए।

---

## 💻 Code Example — Basic
```javascript
// events-basics.js
const EventEmitter = require('events'); // import EventEmitter class

const emitter = new EventEmitter(); // create a new emitter instance

// 1. Register a listener for the 'greet' event
emitter.on('greet', (name) => {
  console.log(`Hello, ${name}!`); // runs every time 'greet' is emitted
});

// 2. Emit the event -- synchronously calls all listeners
emitter.emit('greet', 'Rahul'); // Output: Hello, Rahul!
emitter.emit('greet', 'Priya'); // Output: Hello, Priya!

// 3. once() -- listener fires only ONE time, then auto-removed
emitter.once('first-visit', () => {
  console.log('Welcome! This is your first visit.');
});
emitter.emit('first-visit'); // fires
emitter.emit('first-visit'); // does NOT fire again

// 4. Multiple listeners for the same event -- run in registration order
emitter.on('order-placed', () => console.log('1. Send confirmation email'));
emitter.on('order-placed', () => console.log('2. Update inventory'));
emitter.on('order-placed', () => console.log('3. Log analytics event'));
emitter.emit('order-placed');
// Output (in order):
// 1. Send confirmation email
// 2. Update inventory
// 3. Log analytics event

// 5. ALWAYS handle 'error' events -- unhandled 'error' crashes the process!
emitter.on('error', (err) => console.error('Caught error:', err.message));
emitter.emit('error', new Error('Something went wrong'));
```

## 💻 Code Example — Advanced
```javascript
// events-advanced.js -- extending EventEmitter in a real class (production pattern)
const EventEmitter = require('events');

class OrderTracker extends EventEmitter {
  constructor(orderId) {
    super(); // MUST call super() to initialize EventEmitter internals
    this.orderId = orderId;
    this.status = 'placed';
  }

  accept() {
    this.status = 'accepted';
    this.emit('accepted', { orderId: this.orderId, timestamp: Date.now() });
  }

  pickup() {
    this.status = 'picked-up';
    this.emit('picked-up', { orderId: this.orderId, timestamp: Date.now() });
  }

  deliver() {
    this.status = 'delivered';
    this.emit('delivered', { orderId: this.orderId, timestamp: Date.now() });
  }

  fail(reason) {
    // emit 'error' carefully -- always ensure a listener exists before calling fail()
    this.emit('error', new Error(`Order ${this.orderId} failed: ${reason}`));
  }
}

const tracker = new OrderTracker('ORD-12345');

// Independent services subscribe without tracker knowing about them
tracker.on('accepted', (data) => console.log(`[Notification] Order ${data.orderId} accepted!`));
tracker.on('accepted', (data) => console.log(`[Analytics] Logging acceptance event`));
tracker.on('picked-up', (data) => console.log(`[SMS] Your order is on the way!`));
tracker.on('delivered', (data) => console.log(`[Notification] Order delivered!`));
tracker.on('error', (err) => console.error(`[ErrorHandler] ${err.message}`));

// Managing listener limits -- default max is 10, warns if exceeded (helps catch leaks)
tracker.setMaxListeners(20); // raise limit if you legitimately need more listeners

// Checking listener count (useful for debugging memory leaks)
console.log('Listeners for "accepted":', tracker.listenerCount('accepted')); // 2

// Simulate order lifecycle
tracker.accept();
tracker.pickup();
tracker.deliver();

// Removing a listener to prevent memory leaks (e.g. when a component unmounts)
function logHandler(data) { console.log('temp logger', data); }
tracker.on('delivered', logHandler);
tracker.off('delivered', logHandler); // removed before next emit -- won't fire
tracker.emit('delivered', { orderId: tracker.orderId });
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const EventEmitter = require('events');
const app = express();

// App-wide event bus for decoupling business logic from side effects
const orderEvents = new EventEmitter();

// Side-effect listeners registered once at startup
orderEvents.on('order-created', (order) => {
  console.log(`[Email Service] Sending confirmation for order ${order.id}`);
  // sendConfirmationEmail(order) -- in real app
});

orderEvents.on('order-created', (order) => {
  console.log(`[Inventory Service] Reducing stock for order ${order.id}`);
  // updateInventory(order) -- in real app
});

orderEvents.on('error', (err) => {
  console.error('[OrderEvents] Unhandled error:', err.message);
});

app.use(express.json());

app.post('/orders', (req, res) => {
  const order = { id: Date.now(), ...req.body };
  // Save order to DB here (not shown)...

  // Emit event -- all registered services react independently.
  // Route handler stays FAST and focused on the HTTP response.
  orderEvents.emit('order-created', order);

  res.status(201).json({ message: 'Order created', order });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Emitting `'error'` without any listener attached
```javascript
// Wrong -- crashes the entire Node.js process!
const emitter = new EventEmitter();
emitter.emit('error', new Error('boom')); // throws uncaught, process exits

// Correct -- always attach an error listener first
emitter.on('error', (err) => console.error('Handled:', err.message));
emitter.emit('error', new Error('boom')); // handled gracefully
```

❌ Mistake 2: Forgetting to call `super()` when extending EventEmitter
```javascript
// Wrong
class MyEmitter extends EventEmitter {
  constructor() {
    // missing super() -- internal listener storage never initialized
  }
}

// Correct
class MyEmitter extends EventEmitter {
  constructor() {
    super(); // REQUIRED -- sets up internal event registry
  }
}
```

❌ Mistake 3: Adding listeners repeatedly without removing them (memory leak)
```javascript
// Wrong -- adds a new listener every request, accumulates forever
app.get('/track/:id', (req, res) => {
  tracker.on('update', (data) => res.json(data)); // leak! never removed
});

// Correct -- use once() for single-use listeners, or clean up explicitly
app.get('/track/:id', (req, res) => {
  tracker.once('update', (data) => res.json(data)); // auto-removed after firing
});
```

---

## 🧠 Tricky Interview Question
```javascript
const EventEmitter = require('events');
const emitter = new EventEmitter();

emitter.on('data', () => console.log('Listener A'));
emitter.emit('data');
emitter.on('data', () => console.log('Listener B'));
emitter.emit('data');
```
Answer: Output is `Listener A`, then `Listener A` followed by `Listener B`. The first `emit('data')` only triggers Listener A because Listener B hasn't been registered yet. `emit()` calls whatever listeners are CURRENTLY registered at the moment it's called — it's not "subscribe once, fire for all future and past emits." This matters in real systems: if you emit an event before all your service listeners have finished registering during app startup, some listeners silently miss that event forever (no queuing/buffering happens).

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `on()` and `once()`?
A1: `on(event, listener)` registers a listener that fires EVERY time the event is emitted, for the emitter's entire lifetime (until explicitly removed). `once(event, listener)` registers a listener that fires only on the FIRST emission, then Node automatically removes it — useful for things that logically happen once, like a "ready" or "connected" event.

Q2: What happens if you `emit('error')` with no `'error'` listener attached?
A2: Node.js treats this as an unhandled exception and CRASHES the process (throws the error synchronously up the call stack, and if nothing catches it, the process exits). This is a deliberate safety mechanism to force developers to handle errors from EventEmitter-based APIs (like streams) rather than silently swallowing them.

Q3: Is `EventEmitter` synchronous or asynchronous?
A3: `emit()` is SYNCHRONOUS — it calls all registered listeners in order, one after another, on the same tick, before `emit()` itself returns. If a listener throws, it propagates up through `emit()` immediately. This differs from Promises/callbacks which are inherently async. If you need async behavior, each listener must handle its own async logic internally (e.g., using `setImmediate` or by returning/awaiting a Promise independently).

Q4: What is the default max listener limit and why does it exist?
A4: By default, `EventEmitter` warns (via a `MaxListenersExceededWarning`) if more than 10 listeners are added for a single event on one emitter. This isn't a hard limit — it's a leak-detection heuristic, since adding listeners repeatedly in a loop (forgetting to clean up) is a common source of memory leaks. You can raise it with `emitter.setMaxListeners(n)` if your use case genuinely needs more listeners.

Q5: Name 3 built-in Node.js APIs that are built on top of `EventEmitter`.
A5: (1) **Streams** — `Readable`/`Writable` emit `'data'`, `'end'`, `'error'`, `'finish'`. (2) **HTTP server** — `http.Server` emits `'request'`, `'connection'`, `'close'`. (3) **`process`** global object — emits `'exit'`, `'uncaughtException'`, `'unhandledRejection'`. Also: `net.Socket`, `child_process` (`'exit'`, `'message'`), and `fs.watch()`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Decoupling multiple independent reactions to one occurrence (notifications, logging, analytics all reacting to "order created")
- Building a custom class that naturally has lifecycle events (connection opened/closed, job started/finished)
- You need a pub-sub pattern within a single process (not across processes/servers)

❌ Avoid when:
- You need events across multiple processes/servers — use a message queue (RabbitMQ, Kafka, Redis pub-sub) instead
- A simple callback or Promise would be clearer (single consumer, one-time async result) — don't over-engineer with events
- You need guaranteed delivery/ordering/persistence — EventEmitter has none of that; a missed listener means a missed event forever

---

## 📊 Visual Diagram
```
EVENTEMITTER PATTERN:

  Producer                    EventEmitter                 Consumers (listeners)
  ┌──────────┐                                              ┌──────────────────┐
  │ Order    │   .emit('accepted', data)                    │ Notification Svc │
  │ created  │ ───────────────────────────►  'accepted' ───►│ (sends push)      │
  └──────────┘                                  event    ───►├──────────────────┤
                                                          ───►│ Analytics Svc     │
                                                              │ (logs metric)     │
                                                              └──────────────────┘
                     Producer doesn't know who's listening
                     Listeners don't know who's producing
                     Fully decoupled, synchronous dispatch

  emit() is SYNCHRONOUS:
  emit('x') → listener1() → listener2() → listener3() → emit() returns
              (all run on the SAME tick, in registration order)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EventEmitter | Base class for event-driven objects | Event-driven objects की base class |
| emit() | Trigger/fire an event | Event को trigger करना |
| on() | Register a persistent listener | Permanent listener register करना |
| once() | Register a one-time listener | एक-बार चलने वाला listener |
| listener | Function that reacts to an event | Event पर react करने वाला function |
| 'error' event | Special event, crashes if unhandled | खास event, बिना handler crash करता है |
| maxListeners | Leak-detection warning threshold | Memory leak detection की सीमा |

---

## ⚡ 3-Line Summary
English: `EventEmitter` is the pub-sub foundation of Node.js — producers `emit()` events, listeners `on()`/`once()` react, fully decoupled. `emit()` runs synchronously and only triggers listeners registered at that exact moment. Always attach an `'error'` listener — unhandled error events crash the process.

Hindi: `EventEmitter` Node.js का pub-sub foundation है — producers `emit()` करते हैं, listeners `on()`/`once()` से react करते हैं। `emit()` synchronously चलता है और सिर्फ उसी समय registered listeners को trigger करता है। हमेशा `'error'` listener attach करो — नहीं तो process crash होता है।

---

## ➡️ Next Topic
**46. EventEmitter — Complete Guide** — advanced patterns: `prependListener`, `eventNames()`, custom async event handling, and real memory-leak debugging.
