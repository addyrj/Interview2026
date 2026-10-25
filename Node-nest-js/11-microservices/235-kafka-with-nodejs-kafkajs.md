# 235. Kafka with Node.js (kafkajs)
# हिंदी में: Node.js के साथ Kafka (kafkajs)

---

## 🔵 Simple Definition (English)
Apache Kafka is a distributed event streaming platform built for very high-throughput, durable, replayable message logs. Unlike RabbitMQ (which deletes messages after consumption), Kafka retains messages in ordered, partitioned **topics** for a configurable period, allowing multiple consumer groups to read the same data independently and even "replay" history. `kafkajs` is the most popular pure-JavaScript Kafka client for Node.js.

## 🔵 सरल परिभाषा (Hindi)
Apache Kafka एक distributed event streaming platform है जो बहुत high-throughput, durable, replayable message logs के लिए बनाया गया है। RabbitMQ के विपरीत (जो consumption के बाद messages delete करता है), Kafka messages को ordered, partitioned **topics** में एक configurable period के लिए retain करता है, जिससे multiple consumer groups same data को independently read कर सकें और history को "replay" भी कर सकें। `kafkajs` Node.js के लिए सबसे popular pure-JavaScript Kafka client है।

---

## 🔴 Problem it Solves
Traditional message queues (RabbitMQ) delete a message once it's consumed — fine for task distribution, but limiting for use cases like event sourcing, analytics pipelines, or feeding the same event stream to multiple independent systems that each need to process it at their own pace (or reprocess history after a bug fix). Kafka solves this by treating messages as an immutable, ordered, durable log that consumers read from at their own offset — multiple consumer groups can read the same topic independently, and a consumer can "rewind" to reprocess old events, which simple queues can't do.

## 🔴 यह क्यों बना? (Hindi)
Traditional message queues (RabbitMQ) consume होने के बाद message delete कर देती हैं — task distribution के लिए ठीक है, लेकिन event sourcing, analytics pipelines, या एक ही event stream को multiple independent systems तक पहुंचाने जैसे use cases के लिए limited है जिन्हें अपनी speed पर process करना है (या bug fix के बाद history reprocess करनी है)। Kafka messages को एक immutable, ordered, durable log की तरह treat करके यह solve करता है जिसे consumers अपने offset से पढ़ते हैं — multiple consumer groups एक ही topic को independently पढ़ सकते हैं, और एक consumer पुराने events reprocess करने के लिए "rewind" कर सकता है, जो simple queues नहीं कर सकते।

---

## 🟢 How it Works — Step by Step

Step 1 → Data is organized into **topics** (e.g., "order-events"), each split into multiple **partitions** for parallelism.
Step 2 → A **producer** sends messages to a topic; Kafka assigns each message to a partition (by key hash or round-robin).
Step 3 → Messages within a partition are strictly ordered and assigned an incrementing **offset**.
Step 4 → Messages are retained for a configured period (e.g., 7 days) regardless of consumption — they're NOT deleted on read.
Step 5 → **Consumer groups** subscribe to topics; Kafka assigns each partition to exactly one consumer within a group (parallelism across partitions).
Step 6 → Each consumer tracks its own **offset** (position) in each partition, committing progress so it can resume where it left off — or rewind to reprocess.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Data को **topics** में organize किया जाता है (जैसे "order-events"), हर एक को parallelism के लिए multiple **partitions** में split किया जाता है।
Step 2 → एक **producer** topic पर messages भेजता है; Kafka हर message को एक partition assign करता है (key hash या round-robin से)।
Step 3 → एक partition के अंदर messages strictly ordered होते हैं और एक incrementing **offset** assign होता है।
Step 4 → Messages एक configured period के लिए retain होते हैं (जैसे 7 दिन) consumption के बावजूद — read होने पर delete नहीं होते।
Step 5 → **Consumer groups** topics को subscribe करते हैं; Kafka group के अंदर हर partition को exactly एक consumer को assign करता है (partitions के across parallelism)।
Step 6 → हर consumer हर partition में अपना **offset** (position) track करता है, progress commit करता है ताकि वहीं से resume कर सके — या reprocess के लिए rewind कर सके।

---

## 🟡 Real World Example
**Flipkart's clickstream/analytics pipeline:** Every page view, search, and click on Flipkart generates an event published to a Kafka topic like `user-activity`. Multiple independent consumer groups read this SAME stream: a real-time recommendation engine (needs recent events fast), a fraud-detection system (scans for suspicious patterns), and a nightly batch analytics job (reprocesses the full day's events for reports). Because Kafka retains data instead of deleting it on consumption, all three can read the same events independently, and the batch job can even "replay" the whole day from offset 0.

## 🟡 Real Example Hindi mein
**Flipkart की clickstream/analytics pipeline:** Flipkart पर हर page view, search, और click एक event generate करता है जो `user-activity` नाम के Kafka topic पर publish होता है। Multiple independent consumer groups इसी stream को पढ़ते हैं: एक real-time recommendation engine (recent events जल्दी चाहिए), एक fraud-detection system (suspicious patterns scan करता है), और एक nightly batch analytics job (reports के लिए पूरे दिन के events reprocess करता है)। क्योंकि Kafka consumption पर data delete नहीं करता, तीनों independently events पढ़ सकते हैं, और batch job पूरे दिन को offset 0 से "replay" भी कर सकता है।

---

## 💻 Code Example — Basic

```javascript
// kafka-producer.js
// Run: node kafka-producer.js (requires Kafka running + npm i kafkajs)

const { Kafka } = require('kafkajs');

// Create a Kafka client pointing to one or more broker addresses
const kafka = new Kafka({
  clientId: 'order-service',
  brokers: ['localhost:9092'],
});

const producer = kafka.producer();

async function sendOrderEvent(order) {
  await producer.connect();

  // Send a message to the "order-events" topic
  await producer.send({
    topic: 'order-events',
    messages: [
      {
        key: order.id,                      // same key → same partition → ordering guaranteed per key
        value: JSON.stringify(order),
      },
    ],
  });

  console.log('Sent order event:', order.id);
  await producer.disconnect();
}

sendOrderEvent({ id: 'order_1', amount: 599, city: 'bangalore' });
```

```javascript
// kafka-consumer.js
// Run: node kafka-consumer.js

const { Kafka } = require('kafkajs');

const kafka = new Kafka({ clientId: 'analytics-service', brokers: ['localhost:9092'] });

// Consumers in the SAME group share partitions; different groupId = independent reading
const consumer = kafka.consumer({ groupId: 'analytics-group' });

async function run() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'order-events', fromBeginning: true });

  // eachMessage is called for every message received
  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const order = JSON.parse(message.value.toString());
      console.log(`[Partition ${partition}] Received order:`, order.id, 'offset:', message.offset);
      // Kafka auto-commits offset after this callback by default (configurable)
    },
  });
}

run().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// kafka-production-pattern.js — manual offset commit, retry, and consumer group scaling
const { Kafka, logLevel } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'order-processor',
  brokers: (process.env.KAFKA_BROKERS || 'localhost:9092').split(','),
  logLevel: logLevel.WARN,
  retry: { retries: 5 },   // built-in retry for broker connection issues
});

const consumer = kafka.consumer({
  groupId: 'order-processor-group',
  sessionTimeout: 30000,
});

async function startConsumer() {
  await consumer.connect();
  await consumer.subscribe({ topic: 'order-events', fromBeginning: false });

  await consumer.run({
    autoCommit: false,   // manually control offset commits for reliability
    eachMessage: async ({ topic, partition, message, heartbeat }) => {
      const order = JSON.parse(message.value.toString());

      try {
        await processOrder(order);   // business logic (e.g., update inventory)

        // Manually commit offset ONLY after successful processing
        await consumer.commitOffsets([
          { topic, partition, offset: (Number(message.offset) + 1).toString() },
        ]);
      } catch (err) {
        console.error(`Failed to process order ${order.id}:`, err.message);
        // In production: send to a separate "failed-orders" topic instead of crashing
        // Don't commit offset — message will be reprocessed on consumer restart
      }
    },
  });
}

async function processOrder(order) {
  // Simulate DB update
  console.log('Processing order for inventory update:', order.id);
}

// Producer with batching for high throughput
const producer = kafka.producer({ allowAutoTopicCreation: false });

async function sendBatch(orders) {
  await producer.connect();
  await producer.send({
    topic: 'order-events',
    messages: orders.map(o => ({ key: o.city, value: JSON.stringify(o) })),
    // key = city → all orders from same city go to same partition → per-city ordering
  });
  await producer.disconnect();
}

startConsumer().catch(console.error);
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { Kafka } = require('kafkajs');

const app = express();
app.use(express.json());

const kafka = new Kafka({ clientId: 'order-api', brokers: ['localhost:9092'] });
const producer = kafka.producer();

let producerReady = false;
producer.connect().then(() => { producerReady = true; console.log('Kafka producer connected'); });

app.post('/orders', async (req, res) => {
  if (!producerReady) return res.status(503).json({ error: 'Event system not ready' });

  const order = { id: `order_${Date.now()}`, items: req.body.items, city: req.body.city };

  // Save to DB synchronously (critical path), publish event async for downstream systems
  await saveOrderToDb(order);

  await producer.send({
    topic: 'order-events',
    messages: [{ key: order.city, value: JSON.stringify(order) }],
  });

  res.status(201).json({ order });
});

async function saveOrderToDb(order) { return order; }

app.listen(3000, () => console.log('Order API with Kafka producer on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating Kafka like a traditional task queue (expecting messages to disappear after consumption)
✅ Correct: Design consumers to track their own offset/progress — Kafka retains data regardless

```javascript
// Wrong assumption: "once my consumer reads it, it's gone" — FALSE, other consumer groups still see it
// Right: understand retention period (e.g., 7 days) and that multiple groups can read independently
```

❌ Mistake 2: Using `autoCommit: true` (default) when exactly-once-ish processing matters
✅ Correct: Use manual offset commits after successful processing to avoid losing/skipping messages on crash

```javascript
// Wrong — offset auto-commits even if processing later fails
await consumer.run({ eachMessage: async ({ message }) => { await riskyProcess(message); } });

// Right — commit only after success
await consumer.run({
  autoCommit: false,
  eachMessage: async ({ topic, partition, message }) => {
    await riskyProcess(message);
    await consumer.commitOffsets([{ topic, partition, offset: (Number(message.offset)+1).toString() }]);
  },
});
```

---

## 🧠 Tricky Interview Question

```javascript
// A topic has 4 partitions. A consumer group has 6 consumer instances.
// How many consumers actually receive messages?
```
Answer: Only 4 of the 6 consumers will be assigned a partition and actively receive messages — Kafka assigns at most ONE consumer per partition within a group, so with only 4 partitions, a maximum of 4 consumers can work in parallel. The other 2 consumers sit idle (useful as hot standbys if one of the active 4 crashes — Kafka rebalances and assigns the orphaned partition to an idle consumer). This is why the number of partitions caps your maximum consumer parallelism within a group.

---

## ⚫ Interview Questions + Answers

Q1: What is the key architectural difference between Kafka and RabbitMQ?
A1: RabbitMQ is a traditional message broker — messages are removed from a queue once acknowledged/consumed, optimized for task distribution and flexible routing. Kafka is a distributed, append-only log — messages are retained for a configured time regardless of consumption, organized into partitioned topics, optimized for extremely high throughput, ordered processing within a partition, and allowing multiple independent consumer groups to replay/reread the same data. Kafka is generally better for event streaming/analytics; RabbitMQ is often simpler for task queues and complex routing.

Q2: What is a partition in Kafka and why does it matter?
A2: A partition is an ordered, append-only sub-log within a topic. Partitioning allows a topic to be distributed across multiple brokers and consumed in parallel — each partition can be processed by a different consumer within a group, enabling horizontal scalability. Order is only guaranteed WITHIN a partition, not across the whole topic; this is why a message key (e.g., order ID or city) is often used to consistently route related messages to the same partition for in-order processing of a sequence.

Q3: What is a consumer group, and what happens when you add more consumers to it?
A3: A consumer group is a set of consumers that collectively consume a topic's partitions, with Kafka ensuring each partition is assigned to only one consumer within that group at a time (enabling parallel, non-duplicated processing). Adding more consumers (up to the number of partitions) increases processing parallelism/throughput. Adding MORE consumers than there are partitions results in some consumers being idle, since a partition can't be split across two consumers in the same group. Different groups are fully independent — each group gets its own copy of the entire data stream.

Q4: What does "offset" mean in Kafka, and how does it enable replay?
A4: An offset is a sequential ID identifying a message's position within a partition. Consumers track which offset they've processed up to (stored by Kafka itself, in an internal `__consumer_offsets` topic). Because messages aren't deleted on read, a consumer can intentionally reset its offset backward (e.g., to 0, or to a specific timestamp) to reprocess historical data — useful for recovering from bugs, backfilling a new consumer, or rebuilding derived data/analytics from scratch.

Q5: When would you choose Kafka over RabbitMQ for a Node.js system?
A5: Choose Kafka when: you need very high throughput event streaming (millions of events/sec), multiple independent systems need to consume the same event stream at different paces, you need long-term retention/replay capability (event sourcing, analytics, audit logs), or you need strict ordering guarantees per key across a huge volume of data. Choose RabbitMQ when: you need simpler task/work queue semantics, complex routing (topic/fanout patterns) is central to your design, or the operational overhead of running Kafka (ZooKeeper/KRaft, partition management) isn't justified for your scale.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- High-throughput event streaming with multiple independent consumers is needed
- You need durable, replayable event history (event sourcing, audit, analytics)
- Strict per-key ordering at scale matters

❌ Avoid when:
- A simple task queue (one producer, workers competing for jobs) is all you need — RabbitMQ/Bull is simpler
- Your team lacks the operational capacity to run and tune a Kafka cluster
- Low message volume doesn't justify Kafka's operational complexity

---

## 📊 Visual Diagram
```
Topic: order-events (3 partitions)
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Partition 0  │ │ Partition 1  │ │ Partition 2  │
│ [m1][m4][m7] │ │ [m2][m5][m8] │ │ [m3][m6][m9] │   (ordered within each)
└─────┬───────┘ └─────┬───────┘ └─────┬───────┘
      │               │               │
  Consumer Group A (3 consumers, one per partition — full parallelism)
      │               │               │
      ▼               ▼               ▼
   worker1          worker2         worker3

  Consumer Group B (independent — reads the SAME data separately)
      ▼
   analytics-job (can rewind to offset 0 and reread everything)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Topic | Named stream of events | Events का named stream |
| Partition | Ordered sub-log within a topic | Topic के अंदर ordered sub-log |
| Offset | Position of a message in a partition | Partition में message की position |
| Consumer group | Set of consumers sharing partition workload | Partitions की workload share करने वाले consumers |
| Retention | How long Kafka keeps messages | Kafka messages कितनी देर रखता है |
| Replay | Reprocessing old messages by resetting offset | Offset reset करके पुराने messages reprocess करना |

---

## ⚡ 3-Line Summary
**English:**
1. Kafka is a distributed, partitioned, durable event log — unlike RabbitMQ, it retains messages even after consumption, enabling replay.
2. Partitions enable parallelism; consumer groups split partition workload, with each partition assigned to only one consumer per group.
3. Manual offset commits (vs auto-commit) give control over exactly when progress is saved, important for reliable processing.

**Hindi:**
1. Kafka एक distributed, partitioned, durable event log है — RabbitMQ के विपरीत, यह consumption के बाद भी messages retain करता है, replay enable करता है।
2. Partitions parallelism enable करते हैं; consumer groups partition workload split करते हैं, हर partition group में सिर्फ एक consumer को assign होता है।
3. Manual offset commits (auto-commit के बजाय) control देते हैं कि progress कब save हो, reliable processing के लिए जरूरी।

---

## ➡️ Next Topic
**236. Bull Queue — Job Processing** — Redis-backed job queue for background processing in Node.js, simpler than Kafka/RabbitMQ for many use cases.
