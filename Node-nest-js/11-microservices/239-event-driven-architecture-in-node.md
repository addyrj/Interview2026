# 239. Event-Driven Architecture in Node
# हिंदी में: Node में Event-Driven Architecture

---

## 🔵 Simple Definition (English)
Event-driven architecture (EDA) structures a system around producing, detecting, and reacting to **events** (things that happened — "OrderPlaced", "PaymentCompleted") rather than services directly calling each other's methods. Services publish events when something notable happens, and other services subscribe and react independently, without the publisher knowing who's listening.

## 🔵 सरल परिभाषा (Hindi)
Event-driven architecture (EDA) एक system को **events** (जो हुआ — "OrderPlaced", "PaymentCompleted") produce, detect, और react करने के around structure करता है, services के एक-दूसरे के methods directly call करने के बजाय। Services जब कुछ notable होता है तब events publish करती हैं, और दूसरी services independently subscribe करके react करती हैं, publisher को यह जाने बिना कि कौन सुन रहा है।

---

## 🔴 Problem it Solves
Direct service-to-service calls (Order Service calls Email Service, calls SMS Service, calls Analytics Service...) tightly couple services: adding a new reaction to "order placed" requires modifying the Order Service's code, and if any downstream call fails/is slow, it can block or break the whole chain. EDA solves this by inverting the dependency: the Order Service just announces "order was placed" and doesn't know or care who reacts. New consumers can be added later without touching the producer at all — enabling truly independent evolution of services.

## 🔴 यह क्यों बना? (Hindi)
Direct service-to-service calls (Order Service, Email Service को call करती है, फिर SMS Service, फिर Analytics Service...) services को tightly couple करती हैं: "order placed" पर नया reaction जोड़ने के लिए Order Service का code modify करना पड़ता है, और अगर कोई downstream call fail/slow हो, तो पूरी chain block या break हो सकती है। EDA dependency को invert करके यह solve करता है: Order Service सिर्फ announce करती है "order placed हुआ" और उसे पता या care नहीं कि कौन react करता है। नए consumers बाद में बिना producer को touch किए add किए जा सकते हैं — services का truly independent evolution enable करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → A service performs an action and publishes an **event** describing what happened (past tense: "OrderPlaced", not a command like "SendEmail").
Step 2 → The event is published to an event bus/broker (in-process EventEmitter for simple cases, or RabbitMQ/Kafka for distributed systems).
Step 3 → Zero, one, or many subscribers independently receive the event and react according to their own logic.
Step 4 → The publisher has NO knowledge of who (if anyone) is listening — this is the key decoupling.
Step 5 → New behaviors are added by registering a new subscriber, with zero changes to the publisher.
Step 6 → Events often carry enough data for subscribers to act without needing to call back the publisher synchronously.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक service कोई action perform करती है और एक **event** publish करती है जो describe करता है कि क्या हुआ (past tense: "OrderPlaced", command नहीं जैसे "SendEmail")।
Step 2 → Event एक event bus/broker पर publish होता है (simple cases के लिए in-process EventEmitter, या distributed systems के लिए RabbitMQ/Kafka)।
Step 3 → शून्य, एक, या कई subscribers independently event receive करके अपनी logic के अनुसार react करते हैं।
Step 4 → Publisher को यह पता नहीं होता कि कौन (अगर कोई भी) सुन रहा है — यह key decoupling है।
Step 5 → नया behavior एक नया subscriber register करके add होता है, publisher में zero changes के साथ।
Step 6 → Events में अक्सर इतना data होता है कि subscribers publisher को synchronously call back किए बिना act कर सकें।

---

## 🟡 Real World Example
**Razorpay settlement system:** When a payment succeeds, the Payment Service emits a "PaymentSucceeded" event. Over time, Razorpay has added MORE reactions to this single event without touching the Payment Service code: the Settlement Service schedules a payout, the Analytics Service updates dashboards, the Fraud Service re-scores the merchant's risk profile, and a Notification Service alerts the merchant. Each new feature was added as a NEW subscriber — the core payment-processing code never had to change.

## 🟡 Real Example Hindi mein
**Razorpay settlement system:** जब payment succeed होती है, Payment Service एक "PaymentSucceeded" event emit करती है। समय के साथ, Razorpay ने Payment Service code को touch किए बिना इस single event पर MORE reactions add की हैं: Settlement Service payout schedule करती है, Analytics Service dashboards update करती है, Fraud Service merchant का risk profile re-score करती है, और एक Notification Service merchant को alert करती है। हर नया feature एक NEW subscriber के रूप में add हुआ — core payment-processing code को कभी बदलना नहीं पड़ा।

---

## 💻 Code Example — Basic

```javascript
// event-driven-basic.js — in-process event-driven design using Node's built-in EventEmitter
// Run: node event-driven-basic.js

const EventEmitter = require('events');

// A central event bus for the whole app (in real distributed systems: RabbitMQ/Kafka instead)
class OrderEventBus extends EventEmitter {}
const orderEvents = new OrderEventBus();

// ─── PUBLISHER: Order Service only knows how to announce events ─────────────
function placeOrder(order) {
  console.log('Order placed:', order.id);
  // Publish the event — does NOT know or care who's listening
  orderEvents.emit('OrderPlaced', order);
}

// ─── SUBSCRIBERS: added independently, Order Service doesn't know about these ──
orderEvents.on('OrderPlaced', (order) => {
  console.log(`[Email Service] Sending confirmation email for order ${order.id}`);
});

orderEvents.on('OrderPlaced', (order) => {
  console.log(`[Inventory Service] Decrementing stock for order ${order.id}`);
});

orderEvents.on('OrderPlaced', (order) => {
  console.log(`[Analytics Service] Logging order event ${order.id}`);
});

// Trigger the flow
placeOrder({ id: 'order_1', amount: 599 });
// All three subscribers react independently, in registration order
```

## 💻 Code Example — Advanced

```javascript
// event-driven-advanced.js — distributed event-driven pattern with async subscribers and error isolation
const EventEmitter = require('events');

class RobustEventBus extends EventEmitter {
  // Override emit to make subscriber failures NOT crash other subscribers or the publisher
  async emitSafe(eventName, payload) {
    const listeners = this.listeners(eventName);
    // Run all subscribers independently; one failing should not stop others
    const results = await Promise.allSettled(
      listeners.map(listener => Promise.resolve().then(() => listener(payload)))
    );

    results.forEach((result, i) => {
      if (result.status === 'rejected') {
        console.error(`Subscriber ${i} for event "${eventName}" failed:`, result.reason.message);
        // In production: publish to a dead-letter log / alert, don't let it crash the app
      }
    });
  }
}

const bus = new RobustEventBus();

bus.on('PaymentSucceeded', async (payment) => {
  console.log(`[Settlement] Scheduling payout for ${payment.merchantId}`);
});

bus.on('PaymentSucceeded', async (payment) => {
  throw new Error('Fraud Service temporarily down');   // simulate a failing subscriber
});

bus.on('PaymentSucceeded', async (payment) => {
  console.log(`[Analytics] Recording transaction ${payment.id}`);
});

async function processPayment(payment) {
  console.log('Payment processed:', payment.id);
  await bus.emitSafe('PaymentSucceeded', payment);
  console.log('All subscribers notified (failures logged, not thrown)');
}

processPayment({ id: 'txn_1', merchantId: 'merchant_99' });

// NOTE: in a real distributed system, replace EventEmitter with a message broker
// (RabbitMQ/Kafka) so events survive process restarts and can be consumed across services.
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const EventEmitter = require('events');

const app = express();
app.use(express.json());

const appEvents = new EventEmitter();

// Register reactions ONCE at startup — fully decoupled from route handlers
appEvents.on('UserSignedUp', (user) => {
  console.log(`[Welcome Email] Sending welcome email to ${user.email}`);
});
appEvents.on('UserSignedUp', (user) => {
  console.log(`[Analytics] New signup recorded: ${user.id}`);
});

app.post('/signup', async (req, res) => {
  const user = { id: `user_${Date.now()}`, email: req.body.email };
  await saveUserToDb(user);

  // Route handler only announces the event — doesn't know/care about downstream reactions
  appEvents.emit('UserSignedUp', user);

  res.status(201).json({ user, message: 'Signed up successfully' });
});

async function saveUserToDb(user) { return user; }

app.listen(3000, () => console.log('Signup API with event-driven side-effects on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using in-process `EventEmitter` for cross-SERVICE communication (not just within one process)
✅ Correct: `EventEmitter` only works within a single Node.js process — use a message broker (RabbitMQ/Kafka) for events that need to cross process/service boundaries

```javascript
// Wrong — assuming EventEmitter events reach another microservice
emitter.emit('OrderPlaced', order);   // only listeners in THIS process will ever see this

// Right — publish to a broker so other services (in other processes) can subscribe
await channel.publish('orders_exchange', 'order.placed', Buffer.from(JSON.stringify(order)));
```

❌ Mistake 2: Letting a slow or failing subscriber block the publisher (if emit is awaited synchronously without isolation)
✅ Correct: Isolate subscriber failures/slowness so the publisher's own flow isn't affected

```javascript
// Wrong — publisher awaits subscriber directly, one slow subscriber delays everything
for (const listener of emitter.listeners('event')) { await listener(data); }

// Right — fire-and-forget or Promise.allSettled with error isolation (see Advanced example)
```

---

## 🧠 Tricky Interview Question

```javascript
const EventEmitter = require('events');
const emitter = new EventEmitter();

emitter.on('data', () => { throw new Error('Subscriber crashed'); });
emitter.emit('data');
console.log('After emit');
```
Answer: Node's default `EventEmitter.emit()` calls listeners SYNCHRONOUSLY, so an uncaught exception thrown inside a listener propagates up through `emit()` and, if not caught, crashes the entire process (since it becomes an uncaught exception) — "After emit" never prints. This is a classic gotcha: EventEmitter does NOT automatically isolate listener failures from the emitter or from each other, which is why production event-driven systems either wrap listeners in try/catch, use `Promise.allSettled` for async listeners (as in the Advanced example), or rely on a message broker that isolates consumer failures entirely as separate processes.

---

## ⚫ Interview Questions + Answers

Q1: What is the core difference between event-driven architecture and direct service-to-service calls?
A1: In direct calls, Service A explicitly knows about and calls Service B, C, D — tightly coupling A to all its downstream dependents; adding a new reaction means modifying A's code. In event-driven architecture, Service A just announces "X happened" without knowing who (if anyone) reacts — new subscribers can be added or removed without ANY change to the publisher, achieving loose coupling and independent evolvability of services.

Q2: What are the trade-offs of event-driven architecture compared to direct synchronous calls?
A2: Benefits: loose coupling, easier to add new features (new subscribers), better fault isolation, natural fit for asynchronous/eventual-consistency workflows. Trade-offs: harder to trace a request's full flow (events scatter across many subscribers, making debugging/tracing require distributed tracing tools), eventual consistency instead of immediate consistency (subscribers react with some delay), and potential for subtle bugs if event ordering/idempotency isn't carefully handled.

Q3: How would you design the events in an event-driven e-commerce order flow? What naming convention would you use?
A3: Events should be named in past tense describing facts that happened (not commands): "OrderPlaced", "PaymentCompleted", "OrderShipped", "OrderCancelled" — NOT "SendEmail" or "UpdateInventory" (those are commands, tightly tying the event to a specific action, which defeats decoupling). Each event should carry enough contextual data (order ID, items, amounts, timestamps) for subscribers to act independently without needing to call back the publisher for more info.

Q4: What's the risk of using Node's built-in `EventEmitter` for a "microservices" architecture?
A4: `EventEmitter` is strictly in-process — events never leave the Node.js process they're emitted in. If "microservices" means separate processes/containers (which it usually does), `EventEmitter` alone cannot be the mechanism for inter-service event communication; you need an external broker (RabbitMQ, Kafka, Redis Pub/Sub, or a cloud event bus) that can deliver events across process/network boundaries. `EventEmitter` is still useful WITHIN a single service for internal decoupling (e.g., decoupling route handlers from side-effect logic), just not between services.

Q5: How do you handle event ordering and duplicate delivery in an event-driven system?
A5: Ordering: most brokers only guarantee order within a single partition/queue/key (e.g., Kafka guarantees order per partition if you key messages consistently, like by order ID) — don't assume global ordering across all events unless specifically guaranteed and needed. Duplicates: since most real-world brokers provide at-least-once delivery, subscribers must be idempotent (e.g., checking "have I already processed this event ID?" using a processed-events table/set) to safely handle redelivery without duplicating side effects like double-charging or double-emailing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple independent systems need to react to the same business fact (order placed, user signed up)
- You want to add new reactions/features without modifying existing producer code
- Eventual consistency is acceptable for the use case

❌ Avoid when:
- The caller needs an immediate, synchronous result (e.g., "is this payment approved right now?") — direct request/response is simpler and clearer
- The system is small enough that direct calls are easier to trace and reason about, and the decoupling benefit isn't worth the added complexity (debugging, tracing, eventual consistency)

---

## 📊 Visual Diagram
```
TRADITIONAL (tightly coupled):
  Order Service ──calls──▶ Email Service
                ──calls──▶ SMS Service
                ──calls──▶ Analytics Service
  (Order Service must know about and call each one; adding a new one = code change here)

EVENT-DRIVEN (decoupled):
  Order Service ──emits "OrderPlaced"──▶ Event Bus/Broker
                                              │
                            ┌─────────────────┼─────────────────┐
                            ▼                 ▼                 ▼
                       Email Svc          SMS Svc          Analytics Svc
                  (subscribes independently, Order Service doesn't know any of them)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event | A fact that happened, published for others to react to | जो हुआ, react करने के लिए publish किया गया fact |
| Publisher | Service that emits events | Events emit करने वाली service |
| Subscriber | Service that reacts to events | Events पर react करने वाली service |
| Loose coupling | Publisher doesn't know its subscribers | Publisher को अपने subscribers का पता नहीं |
| Event bus | Mechanism distributing events to subscribers | Subscribers तक events distribute करने वाला mechanism |
| Idempotent subscriber | Safe to process the same event twice | Same event दोबारा process करना safe हो |

---

## ⚡ 3-Line Summary
**English:**
1. Event-driven architecture decouples services by having producers announce facts (events) without knowing who reacts.
2. In-process `EventEmitter` works within a single Node process; cross-service events need a broker (RabbitMQ/Kafka).
3. Subscribers must be isolated from each other's failures and designed to be idempotent against duplicate delivery.

**Hindi:**
1. Event-driven architecture services को decouple करता है producers को facts (events) announce करने देकर बिना यह जाने कि कौन react करता है।
2. In-process `EventEmitter` एक single Node process के अंदर काम करता है; cross-service events के लिए broker (RabbitMQ/Kafka) चाहिए।
3. Subscribers को एक-दूसरे की failures से isolated होना चाहिए और duplicate delivery के against idempotent design होना चाहिए।

---

## ➡️ Next Topic
**240. CQRS Pattern in Node** — Separating read and write models, often paired with event-driven architecture.
