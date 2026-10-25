# 296. Implement Pub/Sub
# हिंदी में: Pub/Sub System खुद बनाना (Implementation)

---

## 🔵 Simple Definition (English)
**Pub/Sub (Publish-Subscribe)** is a messaging pattern where publishers send messages to named **topics/channels** without knowing who's listening, and subscribers receive messages from topics they've subscribed to without knowing who published them. It's EventEmitter's cross-process, decoupled big sibling — Redis Pub/Sub, Kafka, and RabbitMQ topic exchanges all implement this pattern.

## 🔵 सरल परिभाषा (Hindi)
**Pub/Sub (Publish-Subscribe)** एक messaging pattern है जहाँ publishers named **topics/channels** पर messages भेजते हैं बिना यह जाने कि कौन सुन रहा है, और subscribers उन topics से messages पाते हैं जिन्हें उन्होंने subscribe किया बिना यह जाने कि किसने publish किया। यह EventEmitter का cross-process, decoupled बड़ा भाई है — Redis Pub/Sub, Kafka, RabbitMQ topic exchanges सब यह pattern implement करते हैं।

---

## 🔴 Problem it Solves
Direct service-to-service calls create tight coupling — if `OrderService` must call `InventoryService`, `NotificationService`, `AnalyticsService` directly, adding a new consumer means modifying `OrderService`. Pub/Sub decouples producers from consumers entirely: the publisher just announces "order placed happened" to a topic, and any number of services can subscribe/unsubscribe without the publisher ever knowing or changing.

## 🔴 यह क्यों बना? (Hindi)
Direct service-to-service calls tight coupling बनाते हैं — अगर `OrderService` को `InventoryService`, `NotificationService`, `AnalyticsService` directly call करना पड़े, तो नया consumer add करने पर `OrderService` modify करना पड़ेगा। Pub/Sub producers को consumers से पूरी तरह decouple करता है: publisher सिर्फ topic पर "order placed हुआ" announce करता है, कोई भी service subscribe/unsubscribe कर सकती है बिना publisher को कभी पता चले या बदले।

---

## 🟢 How it Works — Step by Step

Step 1 → A broker (in-process EventEmitter, or Redis/Kafka for cross-process) maintains a registry: `topic -> [subscriber callbacks]`.
Step 2 → `subscribe(topic, callback)` registers interest — the subscriber doesn't know about other subscribers or the publisher.
Step 3 → `publish(topic, message)` looks up all subscribers for that topic and delivers the message to each — the publisher doesn't know who (or how many) receives it.
Step 4 → `unsubscribe(topic, callback)` removes a specific subscriber.
Step 5 → In distributed systems (Redis Pub/Sub), the broker runs as a separate process/server — publishers and subscribers connect to it over the network, enabling cross-service, cross-machine communication (unlike in-process EventEmitter).
Step 6 → Advanced brokers add features: wildcard topic matching (`order.*`), message persistence/replay (Kafka), guaranteed delivery with acknowledgments (RabbitMQ), unlike simple fire-and-forget Pub/Sub.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक broker (in-process EventEmitter, या cross-process के लिए Redis/Kafka) registry रखता है: `topic -> [subscriber callbacks]`।
Step 2 → `subscribe(topic, callback)` interest register करता है — subscriber को दूसरे subscribers या publisher के बारे में पता नहीं होता।
Step 3 → `publish(topic, message)` उस topic के सभी subscribers ढूंढता है और message हर एक को deliver करता है — publisher को नहीं पता कौन (या कितने) receive करते हैं।
Step 4 → `unsubscribe(topic, callback)` specific subscriber हटाता है।
Step 5 → Distributed systems (Redis Pub/Sub) में broker अलग process/server के रूप में चलता है — publishers और subscribers network पर connect होते हैं, cross-service, cross-machine communication possible होती है (in-process EventEmitter के विपरीत)।
Step 6 → Advanced brokers extra features add करते हैं: wildcard topic matching (`order.*`), message persistence/replay (Kafka), guaranteed delivery with acknowledgments (RabbitMQ) — simple fire-and-forget Pub/Sub के विपरीत।

---

## 🟡 Real World Example
**Uber/Ola's real-time location system** uses Redis Pub/Sub: driver apps publish location updates to a channel like `driver:location:{driverId}`. The matching/tracking service, the rider's app's WebSocket gateway, and the analytics pipeline all independently subscribe to relevant channels. The driver app has zero knowledge of how many systems consume its location pings — it just publishes, and Redis fans the message out to every subscriber.

## 🟡 Real Example Hindi mein
**Uber/Ola का real-time location system** Redis Pub/Sub use करता है: driver apps location updates को `driver:location:{driverId}` जैसे channel पर publish करते हैं। Matching/tracking service, rider के app का WebSocket gateway, और analytics pipeline — सब independently relevant channels subscribe करते हैं। Driver app को ज़रा भी पता नहीं होता कि कितने systems उसकी location pings consume कर रहे हैं — वह सिर्फ publish करता है, Redis message को हर subscriber तक fan-out करता है।

---

## 💻 Code Example — Basic

```javascript
// pubsub-basic.js
// In-process Pub/Sub broker built from scratch (no Redis — runs with `node pubsub-basic.js`)

class PubSub {
  constructor() {
    this.topics = new Map(); // topic -> Set of subscriber callbacks
  }

  subscribe(topic, callback) {
    if (!this.topics.has(topic)) this.topics.set(topic, new Set());
    this.topics.get(topic).add(callback);
    // Return an unsubscribe function — common ergonomic pattern (like RxJS/React hooks)
    return () => this.unsubscribe(topic, callback);
  }

  unsubscribe(topic, callback) {
    this.topics.get(topic)?.delete(callback);
  }

  publish(topic, message) {
    const subscribers = this.topics.get(topic);
    if (!subscribers || subscribers.size === 0) {
      console.log(`No subscribers for topic "${topic}"`);
      return;
    }
    subscribers.forEach(cb => cb(message)); // deliver to every subscriber
  }
}

// --- Demo ---
const broker = new PubSub();

// InventoryService subscribes
broker.subscribe('order.placed', (order) => {
  console.log(`[Inventory] reserving stock for order ${order.id}`);
});

// NotificationService subscribes
const unsubscribeNotif = broker.subscribe('order.placed', (order) => {
  console.log(`[Notification] sending confirmation for order ${order.id}`);
});

// OrderService publishes — has NO idea who's listening
broker.publish('order.placed', { id: 'ORD001', total: 450 });

// Unsubscribe notification service, then publish again
unsubscribeNotif();
broker.publish('order.placed', { id: 'ORD002', total: 300 }); // only Inventory logs now
```

## 💻 Code Example — Advanced

```javascript
// pubsub-advanced.js
// Cross-process Pub/Sub using real Redis — multiple Node.js processes can publish/subscribe.
// npm i ioredis
const Redis = require('ioredis');

// Redis requires SEPARATE connections for pub and sub — a connection in subscribe mode
// can't issue normal commands, so we need two client instances.
const publisher = new Redis();
const subscriber = new Redis();

class RedisPubSub {
  constructor(pub, sub) {
    this.pub = pub;
    this.sub = sub;
    this.handlers = new Map(); // channel -> Set of local callbacks

    // Single Redis event listener fans out to all locally-registered callbacks for that channel
    this.sub.on('message', (channel, message) => {
      const callbacks = this.handlers.get(channel);
      if (!callbacks) return;
      let parsed;
      try { parsed = JSON.parse(message); } catch { parsed = message; }
      callbacks.forEach(cb => cb(parsed));
    });
  }

  async subscribe(channel, callback) {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
      await this.sub.subscribe(channel); // tell Redis server we want this channel
    }
    this.handlers.get(channel).add(callback);
  }

  async unsubscribe(channel, callback) {
    this.handlers.get(channel)?.delete(callback);
    if (this.handlers.get(channel)?.size === 0) {
      await this.sub.unsubscribe(channel); // stop receiving from Redis if no local listeners left
      this.handlers.delete(channel);
    }
  }

  async publish(channel, message) {
    // Redis Pub/Sub messages must be strings — serialize objects to JSON
    await this.pub.publish(channel, JSON.stringify(message));
  }
}

const bus = new RedisPubSub(publisher, subscriber);

// This could run in a COMPLETELY SEPARATE Node.js process (e.g., notification-service.js)
bus.subscribe('order.placed', (order) => {
  console.log(`[Notification Process] sending receipt for ${order.id}`);
});

// This could run in yet another process (e.g., analytics-service.js)
bus.subscribe('order.placed', (order) => {
  console.log(`[Analytics Process] recording order ${order.id}, total=${order.total}`);
});

// This simulates the order-service process publishing — in reality it's a different process entirely
async function main() {
  await bus.publish('order.placed', { id: 'ORD001', total: 450 });
}
main();

module.exports = { RedisPubSub };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express API that publishes events via Redis Pub/Sub for OTHER services to consume
const express = require('express');
const Redis = require('ioredis');

const app = express();
app.use(express.json());
const publisher = new Redis();

app.post('/orders', async (req, res) => {
  const order = { id: 'ORD' + Date.now(), ...req.body };

  // Save to DB (critical path) ...

  // Publish event for ANY subscribed service to react — notification, inventory, analytics
  // This API server has ZERO knowledge of which services (or how many) consume this event
  await publisher.publish('order.placed', JSON.stringify(order));

  res.status(201).json(order); // respond immediately, publishing is fire-and-forget
});

app.listen(3000, () => console.log('Order API (publisher) on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the SAME Redis connection for both publishing and subscribing
✅ Correct: Use two separate Redis client connections — once a connection enters subscribe mode, it can't execute normal commands like `publish`, `get`, `set`

```javascript
// Wrong — subscribing on this client blocks it from being used for publish/other commands
const redis = new Redis();
redis.subscribe('order.placed');
redis.publish('other.topic', 'x'); // throws or misbehaves

// Right — dedicated connections
const subscriber = new Redis();
const publisher = new Redis();
```

❌ Mistake 2: Assuming Redis Pub/Sub guarantees delivery to offline/disconnected subscribers
✅ Correct: Redis Pub/Sub is fire-and-forget — if a subscriber isn't connected at publish time, it NEVER receives that message (no persistence/replay). Use a real queue (Redis Streams, Kafka, RabbitMQ) if you need durability.

```javascript
// Wrong assumption — "my service was down for 2 minutes, I'll catch up on missed events"
// Redis Pub/Sub does NOT buffer missed messages for offline subscribers.

// Right — use Redis Streams (XADD/XREAD) or Kafka for at-least-once, replayable delivery
await redis.xadd('order-events', '*', 'event', JSON.stringify(order));
```

---

## 🧠 Tricky Interview Question

```javascript
// Process A subscribes to 'order.placed'
// Process B publishes to 'order.placed' BEFORE Process A has finished subscribing (race at startup)
```
Answer: Process A will **miss** that publish entirely. Redis Pub/Sub (like most basic pub/sub systems) has no message buffering or persistence — a message published to a channel is delivered only to subscribers connected and subscribed AT THAT EXACT MOMENT. If the subscription call (`SUBSCRIBE`) hasn't completed on the Redis server before the `PUBLISH` happens, that message is simply gone for that subscriber. This is a critical distinction from queue systems (RabbitMQ, Kafka, Redis Streams) where messages are durably stored and consumers can catch up on backlog — pub/sub trades durability for simplicity and low latency.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between Pub/Sub and a message queue (like RabbitMQ work queues)?
A1: Pub/Sub broadcasts each message to ALL current subscribers of a topic (fan-out, zero or more receivers). A queue typically delivers each message to exactly ONE consumer among a competing group (load-balanced work distribution), and messages persist until consumed/acked. Pub/Sub is for "notify everyone interested"; queues are for "process this job exactly once."

Q2: How would you implement wildcard topic subscriptions (e.g., subscribing to `order.*` to catch `order.placed`, `order.cancelled`, etc.)?
A2: Store subscriptions with their pattern, and on publish, iterate registered patterns checking if the published topic matches (convert wildcard pattern to regex: `order.*` → `/^order\..*$/`), delivering to all matching subscriber sets. Redis supports this natively via `PSUBSCRIBE` with glob-style patterns.

Q3: Why can't a single Redis connection both subscribe and run other commands?
A3: Once a Redis client issues `SUBSCRIBE`, the connection enters a special pub/sub mode where the server starts actively pushing messages down that same socket; the client/server protocol in this mode restricts the command set available (mostly just (un)subscribe variants and PING), so you need a separate connection for normal read/write commands.

Q4: How do you make Pub/Sub reliable (not lose messages if a subscriber is briefly down)?
A4: Switch to a persistence-backed primitive: Redis Streams (`XADD`/`XREAD` with consumer groups, which remember each consumer's last-read position) or a full message broker like Kafka/RabbitMQ, where messages are stored until explicitly acknowledged, allowing late or restarted consumers to catch up.

Q5: In a microservices architecture, when would you choose Pub/Sub over direct REST calls between services?
A5: When the producer shouldn't need to know or care who consumes an event, when you expect to add new consumers over time without touching the producer, and when a single event logically triggers multiple independent reactions (notification + analytics + inventory) that shouldn't block each other or the producer's response.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple independent services need to react to the same event without tight coupling
- Real-time fan-out broadcasting (chat rooms, live location, live scores)

❌ Avoid when:
- You need guaranteed delivery/replay for offline consumers (use a durable queue/stream instead)
- A simple direct function call or REST request between two tightly related services is clearer (don't over-engineer)

---

## 📊 Visual Diagram
```
                         ┌─────────────────────┐
  OrderService  ──PUBLISH──▶   Broker/Redis     │
  (publisher)             │  topic: order.placed │
                         └───────────┬──────────┘
                                     │ fan-out to ALL current subscribers
                 ┌───────────────────┼───────────────────┐
                 ▼                   ▼                   ▼
         InventoryService   NotificationService   AnalyticsService
         (subscriber)       (subscriber)          (subscriber)
         -- none of them know about each other or the publisher --
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Publisher | Sends messages to a topic | Topic पर message भेजने वाला |
| Subscriber | Receives messages from a topic | Topic से message पाने वाला |
| Fan-out | Delivering one message to many subscribers | एक message को कई subscribers तक पहुंचाना |
| Topic/Channel | Named category messages are grouped under | जिस नाम के under messages group होते हैं |
| Fire-and-forget | No guarantee of delivery or persistence | Delivery/persistence की कोई guarantee नहीं |

---

## ⚡ 3-Line Summary
English: Pub/Sub decouples publishers from subscribers entirely via named topics, with a broker (in-process EventEmitter or Redis/Kafka cross-process) fanning out each message to every current subscriber. Basic Pub/Sub (like Redis Pub/Sub) is fire-and-forget with no delivery guarantee for offline subscribers — use streams/queues when durability matters.
Hindi: Pub/Sub named topics के through publishers को subscribers से पूरी तरह decouple करता है, broker (in-process EventEmitter या Redis/Kafka cross-process) हर message को सभी current subscribers तक fan-out करता है। Basic Pub/Sub (Redis Pub/Sub जैसा) fire-and-forget है, offline subscribers के लिए कोई delivery guarantee नहीं — durability चाहिए तो streams/queues use करो।

---

## ➡️ Next Topic
**297. Event Loop Output Questions** — a curated set of tricky `setTimeout`/`Promise`/`process.nextTick` ordering questions.
