# 234. RabbitMQ with Node.js
# हिंदी में: Node.js के साथ RabbitMQ

---

## 🔵 Simple Definition (English)
RabbitMQ is a mature, widely-used open-source message broker that implements the AMQP protocol. It routes messages from producers to consumers through **exchanges** and **queues**, supporting flexible routing patterns (direct, topic, fanout). In Node.js, the `amqplib` package is the standard client for connecting to RabbitMQ.

## 🔵 सरल परिभाषा (Hindi)
RabbitMQ एक mature, widely-used open-source message broker है जो AMQP protocol implement करता है। यह messages को producers से consumers तक **exchanges** और **queues** के through route करता है, flexible routing patterns (direct, topic, fanout) support करते हुए। Node.js में, `amqplib` package RabbitMQ से connect करने के लिए standard client है।

---

## 🔴 Problem it Solves
Building a custom queue (e.g., on Redis) works for simple cases but lacks advanced routing, delivery guarantees, management tooling, and clustering/HA support that production systems need. RabbitMQ solves this by providing a battle-tested broker with: flexible routing (send a message to one, many, or filtered consumers based on routing keys), acknowledgments and durability guarantees, a management UI for monitoring queues, and clustering for high availability — all out of the box.

## 🔴 यह क्यों बना? (Hindi)
Custom queue बनाना (जैसे Redis पर) simple cases के लिए काम करता है लेकिन advanced routing, delivery guarantees, management tooling, और clustering/HA support की कमी होती है जो production systems को चाहिए। RabbitMQ एक battle-tested broker देकर यह solve करता है: flexible routing (routing keys के आधार पर एक, कई, या filtered consumers को message भेजना), acknowledgments और durability guarantees, monitoring के लिए management UI, और high availability के लिए clustering — सब out of the box।

---

## 🟢 How it Works — Step by Step

Step 1 → A producer connects to RabbitMQ and declares an **exchange** (direct, topic, fanout, or headers type).
Step 2 → A consumer declares a **queue** and **binds** it to the exchange with a routing key/pattern.
Step 3 → The producer publishes a message to the exchange with a routing key (not directly to the queue).
Step 4 → RabbitMQ's exchange routes the message to all queues whose binding matches the routing key.
Step 5 → Consumers subscribed to the queue receive the message and process it.
Step 6 → After successful processing, the consumer sends an `ack` (acknowledgment); RabbitMQ then removes the message from the queue. If the consumer disconnects without acking, RabbitMQ requeues the message for redelivery.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक producer RabbitMQ से connect करता है और एक **exchange** declare करता है (direct, topic, fanout, या headers type)।
Step 2 → एक consumer एक **queue** declare करता है और उसे exchange से routing key/pattern के साथ **bind** करता है।
Step 3 → Producer exchange पर एक routing key के साथ message publish करता है (queue पर directly नहीं)।
Step 4 → RabbitMQ का exchange message को उन सभी queues पर route करता है जिनका binding routing key से match करता है।
Step 5 → Queue को subscribe किए consumers message receive करके process करते हैं।
Step 6 → Successfully process होने के बाद, consumer `ack` (acknowledgment) भेजता है; RabbitMQ फिर message queue से हटा देता है। अगर consumer बिना ack के disconnect हो जाए, RabbitMQ redelivery के लिए message requeue करता है।

---

## 🟡 Real World Example
**Swiggy order routing by city:** Swiggy could use a **topic exchange** with routing keys like `order.bangalore.placed`, `order.mumbai.placed`. Each city's dedicated processing service binds a queue with a pattern like `order.bangalore.*` — only receiving messages relevant to its city. This lets Swiggy scale city-specific consumers independently (Bangalore has more orders during IPL season) while using one shared exchange for all order events.

## 🟡 Real Example Hindi mein
**Swiggy order routing by city:** Swiggy एक **topic exchange** use कर सकता है routing keys जैसे `order.bangalore.placed`, `order.mumbai.placed` के साथ। हर city की dedicated processing service `order.bangalore.*` जैसे pattern से queue bind करती है — सिर्फ अपने city से relevant messages receive करती है। यह Swiggy को city-specific consumers को independently scale करने देता है (IPL season में Bangalore में ज्यादा orders) जबकि सभी order events के लिए एक shared exchange use होता है।

---

## 💻 Code Example — Basic

```javascript
// rabbitmq-producer.js
// Run: node rabbitmq-producer.js (requires RabbitMQ running + npm i amqplib)

const amqp = require('amqplib');

async function publishOrder() {
  // Connect to RabbitMQ server
  const connection = await amqp.connect('amqp://localhost');
  const channel = await connection.createChannel();

  const queueName = 'order_queue';
  // Declare queue durable=true so it survives broker restarts
  await channel.assertQueue(queueName, { durable: true });

  const message = JSON.stringify({ orderId: 'order_123', amount: 599 });

  // Send message directly to the default exchange, routed by queue name
  channel.sendToQueue(queueName, Buffer.from(message), {
    persistent: true,   // message survives broker restart (written to disk)
  });

  console.log('Sent:', message);

  // Close connection after a short delay to ensure message is flushed
  setTimeout(() => connection.close(), 500);
}

publishOrder();
```

```javascript
// rabbitmq-consumer.js
// Run: node rabbitmq-consumer.js

const amqp = require('amqplib');

async function consumeOrders() {
  const connection = await amqp.connect('amqp://localhost');
  const channel = await connection.createChannel();

  const queueName = 'order_queue';
  await channel.assertQueue(queueName, { durable: true });

  console.log('Waiting for orders...');

  channel.consume(queueName, (msg) => {
    if (msg !== null) {
      const order = JSON.parse(msg.content.toString());
      console.log('Processing order:', order.orderId);

      // Acknowledge AFTER successful processing — removes message from queue
      channel.ack(msg);
    }
  }, { noAck: false });   // noAck:false means we manually control acknowledgment
}

consumeOrders();
```

## 💻 Code Example — Advanced

```javascript
// rabbitmq-topic-exchange.js — production pattern: topic exchange with routing keys
const amqp = require('amqplib');

async function setupTopicRouting() {
  const connection = await amqp.connect(process.env.RABBITMQ_URL || 'amqp://localhost');
  const channel = await connection.createChannel();

  const exchangeName = 'orders_exchange';
  await channel.assertExchange(exchangeName, 'topic', { durable: true });

  // ─── Consumer for Bangalore-specific orders ──────────────────────────────
  const bangaloreQueue = await channel.assertQueue('bangalore_orders', { durable: true });
  await channel.bindQueue(bangaloreQueue.queue, exchangeName, 'order.bangalore.*');

  // ─── Consumer for ALL cities (e.g., a global analytics service) ─────────
  const analyticsQueue = await channel.assertQueue('analytics_all_orders', { durable: true });
  await channel.bindQueue(analyticsQueue.queue, exchangeName, 'order.*.placed');

  // Set prefetch to limit how many unacked messages a consumer holds at once
  // (prevents one consumer from hogging all messages if multiple consumers exist)
  await channel.prefetch(5);

  channel.consume(bangaloreQueue.queue, (msg) => {
    if (msg) {
      console.log('[Bangalore] Processing:', msg.content.toString());
      channel.ack(msg);
    }
  });

  channel.consume(analyticsQueue.queue, (msg) => {
    if (msg) {
      console.log('[Analytics] Logging:', msg.content.toString());
      channel.ack(msg);
    }
  });

  return { channel, exchangeName };
}

async function publishCityOrder(channel, exchangeName, city, order) {
  const routingKey = `order.${city}.placed`;   // e.g., "order.bangalore.placed"
  channel.publish(exchangeName, routingKey, Buffer.from(JSON.stringify(order)), {
    persistent: true,
  });
  console.log(`Published with routing key: ${routingKey}`);
}

(async () => {
  const { channel, exchangeName } = await setupTopicRouting();
  await publishCityOrder(channel, exchangeName, 'bangalore', { orderId: 'o1', amount: 450 });
  await publishCityOrder(channel, exchangeName, 'mumbai', { orderId: 'o2', amount: 300 });
  // Bangalore consumer gets only o1; Analytics consumer gets BOTH o1 and o2
})();
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const amqp = require('amqplib');

const app = express();
app.use(express.json());

let channel;   // reuse a single channel across requests — don't reconnect per request

async function initRabbitMQ() {
  const connection = await amqp.connect(process.env.RABBITMQ_URL || 'amqp://localhost');
  channel = await connection.createChannel();
  await channel.assertQueue('order_queue', { durable: true });

  // Handle connection errors — reconnect logic needed in production
  connection.on('error', (err) => console.error('RabbitMQ connection error:', err.message));
}

app.post('/orders', async (req, res) => {
  const order = { id: `order_${Date.now()}`, items: req.body.items };

  // Publish to RabbitMQ — fast, async, doesn't block the HTTP response
  channel.sendToQueue('order_queue', Buffer.from(JSON.stringify(order)), { persistent: true });

  res.status(201).json({ order, message: 'Order queued for processing' });
});

initRabbitMQ().then(() => {
  app.listen(3000, () => console.log('Order API connected to RabbitMQ, listening on 3000'));
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not setting `durable: true` on queues or `persistent: true` on messages
✅ Correct: Both are needed together — otherwise messages are lost if RabbitMQ restarts

```javascript
// Wrong — messages lost on broker restart
await channel.assertQueue('q', { durable: false });
channel.sendToQueue('q', Buffer.from(msg));

// Right
await channel.assertQueue('q', { durable: true });
channel.sendToQueue('q', Buffer.from(msg), { persistent: true });
```

❌ Mistake 2: Forgetting `channel.ack(msg)` or using `noAck: true` carelessly
✅ Correct: Manually ack after successful processing so failed messages are redelivered instead of silently lost

```javascript
// Wrong — message removed immediately even if processing later fails
channel.consume('q', (msg) => { process(msg); }, { noAck: true });

// Right
channel.consume('q', async (msg) => {
  try { await process(msg); channel.ack(msg); }
  catch (err) { channel.nack(msg, false, true); }  // requeue on failure
}, { noAck: false });
```

---

## 🧠 Tricky Interview Question

```javascript
// Two consumers (C1, C2) are both bound to the SAME queue (not separate queues).
// 10 messages are published. How are they distributed?
```
Answer: RabbitMQ uses **round-robin dispatch** by default when multiple consumers subscribe to the same queue — each message goes to exactly ONE consumer (not both), roughly alternating between them. This is the "competing consumers" pattern used for load-balancing work across multiple worker instances. If you want BOTH consumers to get every message, they need separate queues each bound to a fanout/topic exchange — not sharing a single queue.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between an exchange and a queue in RabbitMQ?
A1: A queue is where messages are actually stored and from which consumers receive them. An exchange is a routing component — producers never publish directly to a queue; they publish to an exchange with a routing key, and the exchange decides (based on its type and bindings) which queue(s) the message should go to. This separation allows flexible routing (one message can fan out to multiple queues, or be filtered by routing key) without the producer knowing about consumers.

Q2: What are the main exchange types in RabbitMQ and when would you use each?
A2: Direct exchange routes a message to queues whose binding key exactly matches the routing key (simple point-to-point routing). Fanout exchange broadcasts a message to ALL bound queues, ignoring routing keys (good for "notify everyone" scenarios). Topic exchange matches routing keys against wildcard patterns (`*` for one word, `#` for multiple), allowing flexible hierarchical routing like `order.bangalore.placed`. Headers exchange routes based on message header attributes rather than routing keys (less common).

Q3: What happens if a consumer crashes while processing a message it hasn't acked yet?
A3: RabbitMQ detects the consumer's channel/connection closing and automatically requeues any unacknowledged messages that consumer held, redelivering them to another available consumer (or the same one after it restarts). This is what gives RabbitMQ at-least-once delivery semantics. It's why consumers must be idempotent — a message could be partially processed before the crash and then redelivered and processed again.

Q4: What is `prefetch` (QoS) in RabbitMQ and why does it matter?
A4: `channel.prefetch(n)` limits how many unacknowledged messages a consumer can hold at once. Without it, RabbitMQ might push ALL available messages to the first connected consumer, starving other consumers and overwhelming the first one's memory. Setting a reasonable prefetch (e.g., 5-20 depending on processing time) ensures fair distribution across multiple consumer instances and prevents one worker from being overloaded while others sit idle.

Q5: How do you handle "poison messages" (messages that always fail processing) in RabbitMQ?
A5: Use a **dead-letter exchange (DLX)**: configure a queue with `x-dead-letter-exchange` so that messages which are rejected (nacked without requeue) or exceed a TTL/retry count are automatically routed to a separate dead-letter queue instead of being retried forever. This isolates permanently-failing messages for manual inspection/alerting, preventing them from blocking the main queue or looping endlessly between consumer and broker.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need flexible routing (topic/fanout patterns) between producers and multiple consumer types
- Reliable delivery with acknowledgments and dead-lettering is required
- You want a mature broker with a management UI and clustering support for HA

❌ Avoid when:
- Extremely high-throughput event streaming with long-term replay is needed (Kafka is often better suited there)
- The use case is trivial (a single simple background job) where a lighter solution (Bull/BullMQ on Redis) is simpler to operate

---

## 📊 Visual Diagram
```
  Producer
     │ publish(exchange, routingKey, message)
     ▼
┌──────────────┐
│   Exchange    │  (direct / topic / fanout)
└──────┬───────┘
       │ routes based on binding + routing key
   ┌───┴────┬─────────┐
   ▼        ▼         ▼
 Queue A  Queue B   Queue C
   │        │         │
   ▼        ▼         ▼
Consumer1 Consumer2 Consumer3
  (ack)     (ack)     (ack)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exchange | Routes messages to queues | Messages को queues पर route करता है |
| Binding | Link between exchange and queue with a key | Exchange और queue के बीच key से link |
| Routing key | Label used to route a message | Message route करने के लिए label |
| ack/nack | Acknowledge/reject a message | Message को acknowledge/reject करना |
| Prefetch | Max unacked messages per consumer | हर consumer का max unacked messages |
| Dead-letter exchange | Destination for permanently failed messages | Permanently fail हुए messages की जगह |

---

## ⚡ 3-Line Summary
**English:**
1. RabbitMQ routes messages through exchanges to queues based on routing keys and binding patterns, using `amqplib` in Node.js.
2. Durable queues + persistent messages + manual acknowledgment together ensure reliable, at-least-once delivery.
3. Prefetch and dead-letter exchanges keep consumer load fair and isolate permanently failing messages.

**Hindi:**
1. RabbitMQ messages को exchanges से होते हुए routing keys और binding patterns के आधार पर queues पर route करता है, Node.js में `amqplib` use करके।
2. Durable queues + persistent messages + manual acknowledgment मिलकर reliable, at-least-once delivery ensure करते हैं।
3. Prefetch और dead-letter exchanges consumer load fair रखते हैं और permanently fail होने वाले messages को isolate करते हैं।

---

## ➡️ Next Topic
**235. Kafka with Node.js (kafkajs)** — High-throughput event streaming for large-scale, replayable event pipelines.
