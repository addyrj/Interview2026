# 83. Kafka — Event Streaming
# हिंदी में: Kafka — एक distributed "event log" जिसमें करोड़ों events क्रम से लिखे जाते हैं, दिनों तक सुरक्षित रहते हैं, और कई services अपनी-अपनी जगह (offset) से उन्हें पढ़ सकती हैं

---

## 🔵 Simple Definition (English)
**Apache Kafka** is a **distributed, durable, append-only commit log** for **event streaming**. Producers write events to **topics**, which are split into **partitions** spread across **brokers**. Each event in a partition has an **offset**. Consumers in **consumer groups** read at their own pace by tracking offsets. Events are **retained** (hours to forever) and can be **replayed**.
It handles **millions of events per second** with high durability, and is the backbone for event-driven microservices, CDC, analytics pipelines and stream processing.

## 🔵 सरल परिभाषा (Hindi)
Kafka एक बहुत बड़ा, कई सर्वरों पर फैला "log" है — producers events (जैसे order.placed) topics में लिखते हैं, जो partitions में बँटे होते हैं।
Consumers अपनी जगह (offset) याद रखकर पढ़ते हैं; events दिनों तक रहते हैं, इसलिए दोबारा पढ़ (replay) भी सकते हो। प्रति सेकंड लाखों events संभालता है।

---

## 🔴 Problem it Solves
LinkedIn (2010) had dozens of systems that each needed data from each other (activity events, metrics, DB changes) → **N×M point-to-point pipelines**, fragile and slow. Traditional queues deleted messages after consumption, couldn't handle **massive throughput**, and couldn't let **many independent consumers** read the same data.

Kafka gave:
- **One central, durable event backbone**: producers write once, any number of consumers read.
- **Very high throughput** (sequential disk writes, batching, zero-copy).
- **Retention + replay**: new services can read history; bugs can be fixed by reprocessing.
- **Ordering per key** (partition) and **horizontal scaling** via partitions.

## 🔴 यह क्यों बना? (Hindi)
LinkedIn में दर्जनों systems को एक-दूसरे का डेटा चाहिए था — हर जोड़ी के लिए अलग pipeline, कमज़ोर और धीमी। पुरानी queues पढ़ते ही message मिटा देती थीं और भारी ट्रैफ़िक नहीं संभालती थीं।
Kafka ने एक केंद्रीय, टिकाऊ event रास्ता दिया — एक बार लिखो, कितनी भी services पढ़ें, बहुत तेज़, और पुराना डेटा दोबारा पढ़ने की सुविधा।

---

## 🟢 How it Works — Step by Step

### Topics, partitions, offsets

```
Topic: order-events  (3 partitions, replication factor 3)

Partition 0: [0][1][2][3][4][5][6] ← new events appended at the end
Partition 1: [0][1][2][3][4]
Partition 2: [0][1][2][3][4][5]
              ↑ offset = position in the partition (immutable log)

Producer: partition = hash(key) % 3     key = orderId → all events of an order go to SAME partition
          → ORDER guaranteed per key (per partition), not across the topic
```

### Brokers & replication

```
Broker 1: P0 (leader)   P1 (follower)  P2 (follower)
Broker 2: P1 (leader)   P2 (follower)  P0 (follower)
Broker 3: P2 (leader)   P0 (follower)  P1 (follower)

Writes go to the partition LEADER; followers replicate.
ISR (in-sync replicas) = followers caught up.
acks=all + min.insync.replicas=2 → a write is acknowledged only when ≥2 replicas have it → durable.
Leader dies → controller elects a new leader from ISR (KRaft mode: Raft-based metadata, no ZooKeeper).
```

### Consumer groups

```
Topic order-events (3 partitions)

Group "notification-svc":  C1 ← P0, P1      C2 ← P2         (partitions split among members)
Group "analytics-svc":     C1 ← P0, P1, P2                  (independent offsets — reads ALL)
Group "search-indexer":    C1 ← P0   C2 ← P1   C3 ← P2

- Within a group: each partition → exactly ONE consumer (competing consumers, ordered processing)
- Across groups: every group gets every event (pub/sub)
- Max useful consumers in a group = number of partitions
- Rebalance: when consumers join/leave, partitions are reassigned
- Offsets committed to __consumer_offsets → resume after restart
```

### Why Kafka is so fast
```
- Append-only sequential disk writes (fast even on HDD) + OS page cache
- Batching + compression (lz4/zstd) of many messages
- Zero-copy (sendfile) from disk to network
- Partitioning = parallelism across brokers & consumers
- Consumers pull at their own rate (no per-message broker bookkeeping like ACK per message)
```

### Delivery semantics
```
Producer: acks=0 (fire & forget) | acks=1 (leader only) | acks=all (durable) ⭐
          enable.idempotence=true → no duplicates from producer retries (per partition)
Consumer: commit offset AFTER processing → at-least-once ⭐ (must be idempotent)
          commit BEFORE processing → at-most-once
Exactly-once: Kafka transactions (read-process-write within Kafka, e.g. Kafka Streams)
```

### Retention & compaction
```
Time/size retention: keep 7 days (or N GB) then delete old segments
Log compaction: keep only the LATEST event per key (e.g. user profile changelog) → like a table
Tiered storage: old segments in S3, cheap long retention
```

### Ecosystem
```
Kafka Connect   → source/sink connectors (Debezium CDC from Postgres/MySQL, S3 sink, Elastic sink)
Schema Registry → Avro/Protobuf/JSON schemas, compatibility checks
Kafka Streams / Flink / ksqlDB → stream processing (aggregations, joins, windows)
Managed: AWS MSK, Confluent Cloud, Aiven, Redpanda (Kafka-compatible)
```

### Kafka vs RabbitMQ/SQS (when NOT to use Kafka)
```
Choose Kafka: event streaming, many consumers of same data, replay, high throughput, CDC, analytics
Choose RabbitMQ/SQS/BullMQ: simple job queues, per-message delays/priorities/retries, complex routing,
low volume, no ops team → Kafka has more operational overhead.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Topic (जैसे order-events) partitions में बँटा है; हर partition एक log है जिसमें हर event का एक offset (क्रम संख्या) है।
2. Producer key (जैसे orderId) से partition चुनता है — एक key के सारे events एक partition में, इसलिए उनका क्रम पक्का।
3. हर partition की copies कई brokers पर; `acks=all` से write तभी पक्का जब कई copies में पहुँचे।
4. Consumer group में हर partition एक consumer को; अलग groups (notification, analytics) सब events अपने-अपने offset से पढ़ते हैं।
5. Events दिनों तक रहते हैं — नई service पुराना इतिहास पढ़ सकती है; consumer को idempotent रखो (at-least-once)।

---

## 🟡 Real World Example

**LinkedIn** — created Kafka (2011). It now processes trillions of messages per day for activity tracking, metrics, the feed and data pipelines.

**Uber** — one of the largest Kafka users: trip events, driver GPS updates, surge pricing, payments and logs flow through Kafka to many services and to Hadoop/Pinot for analytics.

**Netflix** — the Keystone pipeline uses Kafka for trillions of events per day (viewing events, logs) feeding real-time and batch analytics.

**Indian companies (Swiggy, Zomato, Flipkart, PhonePe, Razorpay)** — Kafka is the event backbone: order lifecycle events, delivery-partner location streams, payment events, CDC from MySQL/Postgres to search and analytics, and real-time fraud detection.

## 🟡 Real Example Hindi में
Kafka LinkedIn ने बनाया — आज रोज़ खरबों messages। Uber में trip, ड्राइवर GPS, surge pricing सब Kafka से बहता है; Netflix के viewing events भी।
Swiggy, Flipkart, PhonePe, Razorpay में Kafka मुख्य event रास्ता है — order events, लोकेशन stream, payments, और DB से search/analytics तक CDC।

---

## 🟠 My Stack Example

### Producer (Node.js — kafkajs)
```js
import { Kafka, CompressionTypes } from 'kafkajs';
const kafka = new Kafka({ clientId: 'order-service', brokers: process.env.KAFKA_BROKERS.split(',') });
const producer = kafka.producer({ idempotent: true, maxInFlightRequests: 5 });   // no dup on retries
await producer.connect();

export async function publishOrderEvent(type, order) {
  await producer.send({
    topic: 'order-events',
    acks: -1,                                       // all in-sync replicas
    compression: CompressionTypes.GZIP,
    messages: [{
      key: String(order.id),                        // same order → same partition → ordered
      value: JSON.stringify({ eventId: crypto.randomUUID(), type, orderId: order.id, status: order.status, at: new Date().toISOString() }),
      headers: { 'schema-version': '1', 'trace-id': currentTraceId() },
    }],
  });
}
```

### Consumer group (Node.js) — at-least-once, idempotent
```js
const consumer = kafka.consumer({ groupId: 'notification-svc' });
await consumer.connect();
await consumer.subscribe({ topic: 'order-events', fromBeginning: false });

await consumer.run({
  autoCommit: false,
  eachMessage: async ({ topic, partition, message }) => {
    const evt = JSON.parse(message.value.toString());
    const fresh = await db.query('INSERT INTO processed_events(id) VALUES ($1) ON CONFLICT DO NOTHING RETURNING id', [evt.eventId]);
    if (fresh.rowCount) {
      if (evt.type === 'OrderDelivered') await push.send(evt.orderId, 'Your order is delivered 🎉');
    }
    await consumer.commitOffsets([{ topic, partition, offset: (BigInt(message.offset) + 1n).toString() }]);  // commit after processing
  },
});
```

### Python consumer (FastAPI side service) — aiokafka
```python
consumer = AIOKafkaConsumer("order-events", bootstrap_servers=BROKERS, group_id="analytics-svc",
                            enable_auto_commit=False, auto_offset_reset="earliest")
await consumer.start()
async for msg in consumer:
    evt = json.loads(msg.value)
    await upsert_daily_stats(evt)                    # idempotent upsert keyed by eventId
    await consumer.commit()
```

### Topic design (CLI)
```bash
kafka-topics.sh --create --topic order-events --partitions 12 --replication-factor 3 \
  --config min.insync.replicas=2 --config retention.ms=604800000      # 7 days
kafka-consumer-groups.sh --describe --group notification-svc           # LAG per partition ← monitor this!
```

### CDC with Debezium (Postgres → Kafka) — no dual writes
```json
{
  "name": "orders-cdc",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "db", "database.dbname": "app", "database.user": "debezium",
    "table.include.list": "public.orders,public.outbox",
    "topic.prefix": "app", "plugin.name": "pgoutput"
  }
}
```

### Docker Compose (local, KRaft mode, no ZooKeeper)
```yaml
kafka:
  image: bitnami/kafka:3.7
  environment:
    KAFKA_CFG_NODE_ID: 1
    KAFKA_CFG_PROCESS_ROLES: broker,controller
    KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
    KAFKA_CFG_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
    KAFKA_CFG_CONTROLLER_LISTENER_NAMES: CONTROLLER
```

### Choosing partition count & key
```
Partitions = max parallelism of a consumer group; choose for future throughput (e.g. 12–48),
increasing later re-maps keys (breaks per-key order during transition).
Key = entity whose events must stay ordered (orderId, userId, deliveryPartnerId).
Hot key (one huge tenant) → hot partition → consider key salting for non-ordered data.
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain Kafka's architecture: topics, partitions, offsets, brokers.**
A1: A topic is a named stream of events, split into partitions: ordered, append-only logs distributed across brokers (servers). Each event in a partition has a sequential offset. Partitions are replicated across brokers with one leader and followers (in-sync replicas). Producers write to partition leaders, choosing the partition by key hash. Consumers read sequentially by offset. Metadata and leader election are handled by the controller quorum (KRaft) or, in older versions, ZooKeeper.

**Q2: How does Kafka guarantee ordering?**
A2: Only within a partition: events are appended and read in offset order. To keep all events for an entity ordered, use the entity ID as the message key, so they hash to the same partition, and process each partition with a single consumer thread. There's no global ordering across partitions. With idempotent producers, retries don't reorder or duplicate within a partition.

**Q3: What are consumer groups and how do they scale?**
A3: A consumer group is a set of consumers sharing a subscription. Each partition is assigned to exactly one consumer in the group, so partitions are processed in parallel and in order. Adding consumers (up to the partition count) scales throughput. Different groups each receive all events independently, with their own committed offsets. Membership changes trigger rebalances. Consumer lag (latest offset minus committed offset) is the key metric.

**Q4: How do you avoid losing or duplicating messages in Kafka?**
A4: No loss: producer `acks=all` with `min.insync.replicas=2` and replication factor 3, retries enabled, and consumers committing offsets only after processing. No duplicates: idempotent producers prevent producer-side duplicates, but consumer-side redelivery after crashes still happens, so make consumers idempotent (dedup by event ID or upsert). For read-process-write pipelines within Kafka, use transactions (exactly-once semantics, as in Kafka Streams).

**Q5: Kafka vs RabbitMQ — how do you choose?**
A5: Kafka is a distributed log: very high throughput, retention and replay, many independent consumer groups reading the same stream, per-partition ordering, and an ecosystem for CDC and stream processing. It's best for event streaming, analytics, event sourcing and integration backbones. RabbitMQ is a traditional broker: flexible routing (exchanges), per-message acks, priorities, delays and TTLs, lower ops complexity at modest scale, and messages deleted after consumption. It's best for task and job queues and RPC-like work distribution. Many companies use both.

---

## 🔷 Trade-offs
✅ Advantages:
- Huge throughput, durability (replication), retention & replay, many consumers, ordering per key, rich ecosystem (CDC, streams).

❌ Disadvantages:
- Operational complexity (partitions, rebalances, upgrades) unless managed (MSK/Confluent).
- No per-message delays/priorities natively; retries/DLQ patterns are DIY.
- Ordering only per partition; partition count changes are disruptive.
- Overkill for small apps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Topic | Named event stream | events की धारा |
| Partition | Ordered log shard of a topic | topic का क्रमबद्ध हिस्सा |
| Offset | Position of event in partition | event की क्रम संख्या |
| Broker | Kafka server | Kafka सर्वर |
| Consumer group | Consumers sharing partitions | partitions बाँटने वाले consumers |
| Replication factor | Copies per partition | हर partition की copies |
| ISR | In-sync replicas | साथ चलती copies |
| Consumer lag | How far behind a consumer is | consumer कितना पीछे |
| Log compaction | Keep latest per key | हर key का आख़िरी event |
| CDC / Debezium | Stream DB changes into Kafka | DB बदलाव Kafka में |

---

## ⚡ 3-Line Summary
**English:**
1. Kafka = distributed, replicated, append-only log: topics → partitions → offsets; producers append, consumers read by offset.
2. Ordering per partition (use entity key); consumer groups scale reads and give pub/sub across groups; retention enables replay.
3. Use acks=all + idempotent producer + commit-after-process + idempotent consumers; monitor lag; use for streaming/CDC, not tiny job queues.

**Hindi:**
1. Kafka = कई सर्वरों पर फैला log: topic → partition → offset; producer जोड़ता है, consumer offset से पढ़ता है।
2. क्रम सिर्फ़ partition में (entity key इस्तेमाल करो); consumer groups से स्केल; retention से replay।
3. acks=all, idempotent producer, प्रोसेस के बाद commit, idempotent consumer; lag पर नज़र।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Kafka explained](https://www.youtube.com/results?search_query=kafka+event+streaming+bytebytego) | Partitions, consumer groups, exactly-once visuals |
| 📺 YouTube | [Hussein Nasser — Kafka internals](https://www.youtube.com/results?search_query=kafka+internals+hussein+nasser) | Log segments, ISR, how brokers work |
| 📝 Article | [Kafka Official Docs — Introduction](https://kafka.apache.org/documentation/#introduction) | Topics, partitions, replication — authoritative source |
| 📝 Article | [Confluent — Kafka use cases](https://www.confluent.io/learn/apache-kafka/) | Event streaming patterns, exactly-once semantics |
| 🐙 GitHub | [system-design-primer — Message queues](https://github.com/donnemartin/system-design-primer#message-queues) | When to use Kafka vs RabbitMQ vs SQS |

---

## ➡️ Next Topic Suggestion
**84. RabbitMQ** — The classic message broker with powerful routing. Next: exchanges (direct, topic, fanout), queues, bindings, acks, prefetch, and when RabbitMQ beats Kafka.
