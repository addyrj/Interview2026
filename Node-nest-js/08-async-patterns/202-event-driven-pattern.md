# 202. Event-Driven Pattern
# हिंदी में: Event-Driven Pattern

---

## 🔵 Simple Definition (English)
The **event-driven pattern** structures code around emitting and listening for named **events** rather than direct function calls — a component "emits" an event when something happens, and any number of independent listeners can react to it without the emitter knowing (or caring) who's listening. Node.js's core `EventEmitter` class (from the `events` module) is the foundation this pattern is built on, and it underlies almost everything in Node — HTTP servers, streams, and more.

## 🔵 सरल परिभाषा (Hindi)
**Event-driven pattern** code को named **events** emit करने और सुनने के इर्द-गिर्द structure करता है, direct function calls की जगह — कोई component कुछ होने पर event "emit" करता है, और कितने भी independent listeners उसपर react कर सकते हैं बिना emitter को जाने कि कौन सुन रहा है। Node.js का core `EventEmitter` class (`events` module से) इसी pattern की foundation है — HTTP servers, streams, सब इसी पर बने हैं।

---

## 🔴 Problem it Solves
```
PROBLEM WITHOUT EVENTS:
  Component A needs to notify Components B, C, D when something happens
  Direct approach: A calls b.notify(), c.notify(), d.notify() directly
  → A is now TIGHTLY COUPLED to B, C, D — must know about all of them
  → Adding a new listener E means modifying A's code
  → Hard to add/remove reactions dynamically at runtime

EVENT-DRIVEN SOLUTION:
  A just does: emitter.emit('somethingHappened', data)
  B, C, D independently do: emitter.on('somethingHappened', handler)
  → A has ZERO knowledge of B, C, D — fully decoupled
  → New listeners can be added anytime without touching A's code
  → Natural fit for async, real-time, plugin-style architectures
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: A को B, C, D को notify करना है तो direct calls से tightly coupled हो जाता है
नया listener जोड़ने के लिए A का code बदलना पड़ता
Event-driven solution: A सिर्फ emit करता है, B/C/D independently listen करते हैं
A को पता नहीं कौन सुन रहा है — fully decoupled
```

---

## 🟢 How it Works — Step by Step

Step 1 → Create an `EventEmitter` instance (or extend the class): `const emitter = new EventEmitter()`
Step 2 → Register one or more listeners for a named event: `emitter.on('eventName', (data) => {...})`
Step 3 → Elsewhere, trigger the event: `emitter.emit('eventName', data)` — this SYNCHRONOUSLY calls every registered listener, in the order they were registered, passing `data` as arguments
Step 4 → Listeners can be removed (`emitter.off()`/`removeListener()`), limited to run once (`emitter.once()`), and errors have a special convention: emitting an `'error'` event with no listener registered for it CRASHES the process
Step 5 → Node core modules (HTTP servers, streams, child processes) all extend `EventEmitter`, so `server.on('request', ...)`, `stream.on('data', ...)` are literally the same mechanism you use yourself

## 🟢 कैसे काम करता है? (Hindi)
```
1. EventEmitter instance बनाओ
2. emitter.on('eventName', handler) से listener register करो
3. emitter.emit('eventName', data) से event trigger करो — सब listeners sync call होते हैं
4. emitter.once() एक बार चलने वाले listener के लिए, 'error' event बिना listener crash कराता है
5. Node के core modules (HTTP, streams) खुद EventEmitter extend करते हैं
```

---

## 🟡 Real World Example
**Swiggy order lifecycle events:** When an order's status changes, the order service emits events like `orderPlaced`, `orderAccepted`, `orderPickedUp`, `orderDelivered`. Completely independent subsystems listen for these WITHOUT the order service knowing about any of them: the notification service listens for `orderPlaced` to SMS the customer, the analytics service listens for `orderDelivered` to log revenue metrics, the loyalty-points service listens for `orderDelivered` to credit reward points. If tomorrow they add a "send feedback survey" feature listening to `orderDelivered`, the order service's code never changes — it just keeps emitting the same event.

## 🟡 Real Example Hindi mein
**Swiggy order lifecycle:** Order status change होने पर `orderPlaced`, `orderDelivered` जैसे events emit होते हैं। Notification service, analytics service, loyalty-points service सब independently सुनते हैं, order service को पता नहीं कौन सुन रहा है। नया feature जोड़ने पर order service का code नहीं बदलता।

---

## 💻 Code Example — Basic

```javascript
// basic-event-emitter.js
// Run: node basic-event-emitter.js
const EventEmitter = require('events');

// Create an emitter instance
const orderEmitter = new EventEmitter();

// Register MULTIPLE independent listeners for the SAME event
orderEmitter.on('orderPlaced', (order) => {
  console.log(`[Notification] SMS sent for order ${order.id}`);
});

orderEmitter.on('orderPlaced', (order) => {
  console.log(`[Analytics] Logging order ${order.id} for metrics`);
});

// 'once' — this listener fires only on the FIRST emission, then auto-removes itself
orderEmitter.once('orderPlaced', (order) => {
  console.log(`[First-Order Bonus] Checking if ${order.id} is a first order`);
});

// Trigger the event — ALL listeners above run synchronously, in registration order
orderEmitter.emit('orderPlaced', { id: 'ord_1' });
orderEmitter.emit('orderPlaced', { id: 'ord_2' });  // 'once' listener does NOT fire again

// Output:
// [Notification] SMS sent for order ord_1
// [Analytics] Logging order ord_1 for metrics
// [First-Order Bonus] Checking if ord_1 is a first order
// [Notification] SMS sent for order ord_2
// [Analytics] Logging order ord_2 for metrics
```

## 💻 Code Example — Advanced

```javascript
// advanced-event-emitter.js
// Production pattern: extending EventEmitter in a custom class,
// proper 'error' event handling, and removing listeners to prevent leaks.
const EventEmitter = require('events');

class OrderService extends EventEmitter {
  placeOrder(order) {
    if (!order.amount || order.amount <= 0) {
      // Convention: emitting 'error' with no listener CRASHES the process.
      // Always have at least one 'error' listener registered before this can fire.
      return this.emit('error', new Error('Invalid order amount'));
    }
    const placedOrder = { ...order, id: 'ord_' + Date.now(), status: 'placed' };
    this.emit('orderPlaced', placedOrder);
    return placedOrder;
  }

  deliverOrder(orderId) {
    this.emit('orderDelivered', { id: orderId, deliveredAt: new Date() });
  }
}

const orderService = new OrderService();

// ALWAYS register an 'error' listener on any EventEmitter that might emit errors
orderService.on('error', (err) => {
  console.error('OrderService error:', err.message);
});

// Notification subsystem — fully decoupled listener
function notificationHandler(order) {
  console.log(`[Notification] Order ${order.id} placed, sending SMS`);
}
orderService.on('orderPlaced', notificationHandler);

// Loyalty subsystem — fires on delivery
orderService.on('orderDelivered', (order) => {
  console.log(`[Loyalty] Crediting points for order ${order.id}`);
});

// Prevent memory leaks: Node warns if more than 10 listeners are added to one event
// (configurable via setMaxListeners) — a sign something is wrong (listener leak)
console.log('Max listeners warning threshold:', orderService.getMaxListeners());  // default: 10

orderService.placeOrder({ amount: 500 });
orderService.deliverOrder('ord_999');

// Later, if a subsystem needs to stop listening (e.g., during shutdown):
orderService.off('orderPlaced', notificationHandler);  // cleanly remove this specific listener

orderService.placeOrder({ amount: -10 });  // triggers 'error' listener instead of crashing
```

---

## 🟠 Express.js Integration

```javascript
// Using an EventEmitter alongside Express to decouple business logic from side effects
const express = require('express');
const EventEmitter = require('events');

const app = express();
app.use(express.json());

// A single shared emitter for application-wide business events
const appEvents = new EventEmitter();
appEvents.on('error', (err) => console.error('App event error:', err.message));

// Decoupled listeners — none of these live inside the route handler
appEvents.on('userRegistered', (user) => {
  console.log(`[Email Service] Sending welcome email to ${user.email}`);
});
appEvents.on('userRegistered', (user) => {
  console.log(`[Analytics] New signup recorded: ${user.id}`);
});

app.post('/api/register', (req, res) => {
  const user = { id: 'u_' + Date.now(), email: req.body.email };
  // The route handler just emits — it doesn't know or care who's listening
  appEvents.emit('userRegistered', user);
  res.status(201).json(user);
});

app.listen(3000, () => console.log('Server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Emitting an `'error'` event with no `'error'` listener registered — this CRASHES the entire Node.js process, unlike any other event.
✅ Correct: Always register an `.on('error', handler)` on any EventEmitter before it can possibly emit errors.

```javascript
// Wrong — crashes the process if emitted
const emitter = new EventEmitter();
emitter.emit('error', new Error('boom'));  // uncaught — process crashes!

// Right
emitter.on('error', (err) => console.error(err));
emitter.emit('error', new Error('boom'));  // handled, no crash
```

❌ Mistake 2: Adding listeners repeatedly without ever removing them (e.g., inside a function called on every request), causing a "listener leak" — Node warns after 10 listeners on one event by default.
✅ Correct: Register listeners ONCE at setup time, or explicitly `.off()`/`.removeListener()` when done, especially in long-lived processes.

❌ Mistake 3: Expecting `emit()` to be asynchronous — it's actually SYNCHRONOUS; all listeners run immediately, in order, before `emit()` returns, which can block if a listener does heavy synchronous work.
✅ Correct: If a listener needs to do async work, have it kick off that async work itself (e.g., `setImmediate`, or an async function) rather than assuming `emit()` waits for it.

---

## 🧠 Tricky Interview Question

```javascript
const EventEmitter = require('events');
const emitter = new EventEmitter();

emitter.on('data', (val) => console.log('Listener 1:', val));
emitter.emit('data', 'first');

emitter.on('data', (val) => console.log('Listener 2:', val));
emitter.emit('data', 'second');
```
What is logged?
Answer:
```
Listener 1: first
Listener 1: second
Listener 2: second
```
**Explanation:** The first `emit('data', 'first')` call only triggers listeners registered BEFORE it ran — only "Listener 1" exists at that point. "Listener 2" is registered AFTER the first emit already happened, so it never sees `'first'`. The second `emit('data', 'second')` call now has BOTH listeners registered, so both fire. This demonstrates that `EventEmitter` doesn't "replay" past events to newly added listeners — a listener only reacts to events emitted AFTER it was registered, never before.

---

## ⚫ Interview Questions + Answers

Q1: What is `EventEmitter` and why is it central to Node.js?
A1: `EventEmitter` is Node's core class (from the `events` module) implementing the publish-subscribe pattern: `.on()` registers listeners, `.emit()` triggers them. It's central because Node's I/O-heavy, async-first design relies heavily on events to signal when things happen (data arrived, request received, stream ended) — HTTP servers, streams, child processes, and many other core APIs all extend `EventEmitter`.

Q2: What happens if you emit an `'error'` event with no listeners attached?
A2: Node.js treats `'error'` as a special event — if nothing is listening for it when it's emitted, Node throws the error and CRASHES the process (unlike any other event name, where emitting with no listeners is simply a no-op). This is a deliberate safety mechanism forcing developers to explicitly handle errors on any EventEmitter-based object.

Q3: Is `emitter.emit()` synchronous or asynchronous?
A3: Synchronous. All registered listeners for that event are called immediately, one after another, in the order they were registered, and `emit()` doesn't return until every listener has finished running (unless a listener itself kicks off separate async work, which `emit()` doesn't wait for).

Q4: What's the difference between `.on()` and `.once()`?
A4: `.on(event, handler)` registers a listener that runs EVERY time the event is emitted. `.once(event, handler)` registers a listener that runs only on the FIRST emission of that event, then automatically removes itself — useful for one-time setup reactions like "the first time this connects."

Q5: How do you prevent memory leaks with EventEmitter?
A5: Always remove listeners you no longer need via `.off()`/`.removeListener()`, especially in long-running processes or when creating new emitter instances repeatedly (e.g., per-request) without cleanup. Node's default max-listener warning (10 per event) is a safety net that surfaces potential leaks — you can raise it with `setMaxListeners()` if genuinely needed, but it's usually a signal to review your cleanup logic instead.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Decoupling independent subsystems that react to the same business event (notifications, analytics, audit logging)
- Building plugin-style architectures where listeners can be added/removed dynamically
- Working with Node core APIs (streams, HTTP servers) that are themselves event-driven

❌ Avoid when:
- A simple, direct function call would be clearer and there's genuinely only ONE consumer — events add indirection that isn't justified
- You need guaranteed, strict ORDERING or return values from "listeners" — events don't return values to the emitter; use direct calls/Promises instead

---

## 📊 Visual Diagram
```
EVENT-DRIVEN ARCHITECTURE
──────────────────────────────────────────
     OrderService (EventEmitter)
            │
     emit('orderPlaced', order)
            │
   ┌────────┼────────┬─────────────┐
   ▼        ▼        ▼             ▼
Notification Analytics Loyalty  (future listener,
  Service     Service  Service   added later —
(listens)   (listens) (listens)  OrderService code
                                   never changes)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EventEmitter | Core pub-sub class in Node | Node का core pub-sub class |
| emit() | Triggers an event, calls listeners | Event trigger करना, listeners call करना |
| on() / once() | Register persistent/one-time listener | Persistent/one-time listener register करना |
| Decoupling | Independence between components | Components के बीच independence |
| Listener leak | Too many unremoved listeners | ज्यादा unremoved listeners |

---

## ⚡ 3-Line Summary
English:
1. Event-driven pattern decouples emitters from listeners — one emits an event, any number of independent listeners can react.
2. `EventEmitter` is Node's core implementation; `emit()` runs listeners synchronously, in registration order.
3. Always register an `'error'` listener and clean up listeners you no longer need to avoid crashes and leaks.

Hindi:
1. Event-driven pattern emitter और listeners को decouple करता है — एक emit करता है, कई independent listeners react करते हैं।
2. `EventEmitter` Node का core implementation है, `emit()` listeners को sync, registration order में चलाता है।
3. हमेशा `'error'` listener register करो, बिना जरूरत के listeners हटाओ — leaks से बचो।

---

## ➡️ Next Topic
**203. Observer Pattern in Node** — A closely related design pattern that EventEmitter is essentially a built-in implementation of.
