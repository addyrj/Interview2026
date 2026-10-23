# 84. RabbitMQ
# हिंदी में: RabbitMQ — एक लोकप्रिय message broker जो exchanges और routing नियमों से messages को सही queues तक पहुँचाता है; jobs/tasks बाँटने के लिए बढ़िया

---

## 🔵 Simple Definition (English)
**RabbitMQ** is an open-source **message broker** implementing **AMQP 0-9-1** (plus MQTT, STOMP, Streams). Producers publish messages to **exchanges**; exchanges **route** them to **queues** based on **bindings** and **routing keys**; consumers receive from queues and **acknowledge** them. Once acked, messages are removed.
It excels at **task queues, flexible routing, per-message acknowledgement, priorities, TTLs and dead-lettering**.

## 🔵 सरल परिभाषा (Hindi)
RabbitMQ एक message broker है: producer message "exchange" को भेजता है, exchange नियमों (bindings, routing key) के हिसाब से सही "queue" में डालता है, और consumer queue से लेकर ACK करता है — फिर message हट जाता है।
Jobs बाँटने, लचीली routing, priority, TTL और DLQ के लिए बहुत अच्छा है।

---

## 🔴 Problem it Solves
Applications need to distribute **work** reliably:
- Send emails/SMS/push to the right channel per user preference.
- Route "payment.failed.upi" to fraud + support queues, but "payment.succeeded.*" to accounting.
- Process heavy jobs (PDF, video, ML inference) with **fair dispatch** across workers.
- Retry failed messages with **delays** and move poison messages to a **DLQ**.

RabbitMQ gives **smart routing in the broker**, so producers just publish with a routing key and don't need to know who consumes. It also provides reliable, acknowledged delivery with low latency.

## 🔴 यह क्यों बना? (Hindi)
काम भरोसे से बाँटना होता है: यूज़र की पसंद के हिसाब से email/SMS/push, "payment.failed.upi" को fraud और support queue में भेजना, भारी jobs को workers में बराबर बाँटना, फ़ेल messages को देर से दोबारा करना और ज़हरीले messages को DLQ में डालना।
RabbitMQ broker में ही smart routing देता है — producer को पता नहीं होना चाहिए कि consumer कौन है।

---

## 🟢 How it Works — Step by Step

### Core model

```
 Producer ──publish(routingKey="order.placed.mumbai")──► EXCHANGE ──(bindings)──► QUEUE(s) ──► Consumer(s)
                                                                                     │
                                                                          ACK → message removed
                                                                          NACK/requeue or → DLX (dead letter)
```

### Exchange types (most asked)

```
1. DIRECT  — routing key must EXACTLY match binding key
   publish key "email"  → queue_email
   publish key "sms"    → queue_sms

2. TOPIC   — pattern match on dot-separated keys:  * = one word, # = zero or more words
   binding "order.*.mumbai"  → matches order.placed.mumbai, order.cancelled.mumbai
   binding "order.#"         → matches order.placed, order.placed.mumbai.express
   binding "*.failed.#"      → payment.failed.upi, refund.failed

3. FANOUT  — ignore key; copy to ALL bound queues (broadcast / pub-sub)
   "cache.invalidate" → every app instance's queue

4. HEADERS — route by message header values (x-match: all/any) — rare

Default exchange: direct exchange where routing key = queue name (simple work queues)
```

### Work queue with fair dispatch

```
Queue "pdf-jobs" ── Worker A (prefetch=1)
                 ── Worker B (prefetch=1)
                 ── Worker C (prefetch=1)
prefetch (basic.qos) = max unacked messages per consumer
prefetch=1 → a busy worker doesn't get a new job until it acks → fair distribution of slow jobs
Higher prefetch (10–100) → better throughput for fast, small messages
```

### Reliability features

```
Durable queue + persistent messages → survive broker restart
Publisher confirms                  → broker confirms it stored the message (producer-side reliability)
Manual ACK (after processing)       → at-least-once; unacked messages redelivered if consumer dies
Quorum queues (Raft-based)           → replicated across nodes, recommended for HA (replace old mirrored queues)
Dead Letter Exchange (DLX)          → rejected / expired / over-length messages routed elsewhere
TTL per message/queue               → expire stale messages; also used for delayed retries
Priority queues                     → x-max-priority
Delayed messages                    → plugin (rabbitmq_delayed_message_exchange) or TTL + DLX trick
Streams (3.9+)                      → Kafka-like append-only log with replay inside RabbitMQ
```

### Retry with delay via TTL + DLX (classic pattern)

```
main_queue ──(consumer rejects)──► DLX "retry" ──► retry_queue_30s (TTL 30s, DLX back to "main")
                                                         │ after 30s expires
main_queue ◄─────────────────────────────────────────────┘
After N attempts (count header x-death) → route to final "dead" queue for humans
```

### RabbitMQ vs Kafka (quick recall)
```
RabbitMQ: smart broker, dumb consumers; push-based; per-message ack; routing; delete after ack;
          great for task queues, RPC, priorities, delays; moderate throughput (tens of thousands msg/s per node)
Kafka:    dumb broker, smart consumers; pull-based; offset per group; retention & replay;
          huge throughput; event streaming
```

## 🟢 कैसे काम करता है? (Hindi)
1. Producer message को routing key (जैसे `order.placed.mumbai`) के साथ exchange पर भेजता है।
2. Exchange प्रकार: direct (key बिल्कुल मेल), topic (pattern — `*` एक शब्द, `#` कितने भी), fanout (सबको), headers।
3. Bindings तय करती हैं कि कौन-सी queue कौन-से messages लेगी; consumers queue से लेकर काम करके ACK करते हैं।
4. `prefetch=1` से धीमे jobs workers में बराबर बँटते हैं; durable queue + persistent message + publisher confirms से messages नहीं खोते।
5. फ़ेल messages: TTL + DLX से देर से retry, कई बार फ़ेल तो dead queue; HA के लिए quorum queues।

---

## 🟡 Real World Example

**Celery + RabbitMQ (Instagram's early stack, many Django/FastAPI apps)** — Instagram used RabbitMQ with Celery for async tasks (feed fan-out, notifications) in its early years. This combination is still the default for many Python teams.

**Notification routing at consumer apps** — a topic exchange routes `notify.push.*`, `notify.sms.*` and `notify.email.*` to channel-specific worker pools, with priority queues so OTPs jump ahead of marketing messages.

**Banks and fintech (RBI-regulated)** — RabbitMQ (and IBM MQ) are common for reliable, acknowledged message delivery between core systems, with quorum queues for HA.

**Reddit / Mozilla / VMware** — have historically used RabbitMQ for job processing and service messaging.

## 🟡 Real Example Hindi में
Instagram शुरू में Celery + RabbitMQ से feed और notifications के async काम करता था — आज भी Python टीमों का यह आम जोड़ा है।
Notification सिस्टम में topic exchange से push, SMS, email अलग workers पर जाते हैं, और priority queue से OTP, marketing मैसेज से पहले जाते हैं।

---

## 🟠 My Stack Example

### Node.js — amqplib: topic exchange, durable quorum queue, confirms, manual ack
```js
import amqp from 'amqplib';
const conn = await amqp.connect(process.env.AMQP_URL);
const ch = await conn.createConfirmChannel();                  // publisher confirms

await ch.assertExchange('events', 'topic', { durable: true });
await ch.assertExchange('dlx', 'direct', { durable: true });
await ch.assertQueue('orders.notifications', {
  durable: true,
  arguments: { 'x-queue-type': 'quorum', 'x-dead-letter-exchange': 'dlx', 'x-dead-letter-routing-key': 'orders.notifications.dead' },
});
await ch.bindQueue('orders.notifications', 'events', 'order.*.*');   // all order events, any city
await ch.assertQueue('orders.notifications.dead', { durable: true });
await ch.bindQueue('orders.notifications.dead', 'dlx', 'orders.notifications.dead');

// producer
ch.publish('events', `order.placed.${city}`, Buffer.from(JSON.stringify({ eventId, orderId })),
  { persistent: true, contentType: 'application/json', messageId: eventId });
await ch.waitForConfirms();

// consumer
await ch.prefetch(10);
await ch.consume('orders.notifications', async (msg) => {
  try {
    const evt = JSON.parse(msg.content.toString());
    await handleIdempotently(evt);
    ch.ack(msg);
  } catch (e) {
    const attempts = (msg.properties.headers?.['x-delivery-count'] ?? 0);   // quorum queues track this
    if (attempts >= 5) ch.nack(msg, false, false);     // → DLX → dead queue
    else ch.nack(msg, false, true);                    // requeue (consider delayed retry instead)
  }
}, { noAck: false });
```

### Python — Celery with RabbitMQ (FastAPI)
```python
celery = Celery("app", broker="amqp://guest:guest@rabbitmq:5672//")
celery.conf.update(task_acks_late=True, worker_prefetch_multiplier=1,       # fair dispatch for slow tasks
                   task_routes={"tasks.send_otp": {"queue": "critical"}, "tasks.render_pdf": {"queue": "bulk"}},
                   task_queue_max_priority=10)

@celery.task(autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_otp(phone, code): sms.send(phone, f"OTP {code}")

# run workers per queue:  celery -A app worker -Q critical -c 20   |   celery -A app worker -Q bulk -c 4
```

### Fanout for cache invalidation across instances
```js
await ch.assertExchange('cache.invalidate', 'fanout', { durable: false });
const { queue } = await ch.assertQueue('', { exclusive: true });      // per-instance temp queue
await ch.bindQueue(queue, 'cache.invalidate', '');
ch.consume(queue, (m) => { l1Cache.delete(m.content.toString()); ch.ack(m); });
// publisher: ch.publish('cache.invalidate', '', Buffer.from('menu:42'))
```

### Docker Compose
```yaml
rabbitmq:
  image: rabbitmq:3.13-management
  ports: ["5672:5672", "15672:15672"]     # 15672 = management UI (queues, rates, unacked)
  volumes: ["rabbitdata:/var/lib/rabbitmq"]
```
Managed: Amazon MQ for RabbitMQ, CloudAMQP.

### What to monitor
```
Ready vs unacked messages per queue, publish/deliver/ack rates, consumer count,
memory & disk alarms (RabbitMQ blocks publishers when memory high!), DLQ size, connection churn
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain RabbitMQ's exchange, queue and binding model.**
A1: Producers publish to exchanges, never directly to queues (except via the default exchange). Exchanges route messages to queues according to bindings: a direct exchange needs an exact routing key match, a topic exchange matches patterns with `*` and `#`, fanout broadcasts to all bound queues, and headers matches on header values. Consumers subscribe to queues and acknowledge messages, and acked messages are removed.

**Q2: How do you make RabbitMQ messaging reliable?**
A2: Durable exchanges and queues, persistent messages, publisher confirms (the producer knows the broker stored the message), manual consumer acks after processing (at-least-once), quorum queues for replication across nodes, a dead-letter exchange for poison or expired messages, idempotent consumers to handle redelivery, and monitoring of memory and disk alarms and unacked counts.

**Q3: What is prefetch and why does it matter?**
A3: Prefetch (basic.qos) limits how many unacknowledged messages the broker pushes to a consumer. With a large prefetch, one consumer can hoard many messages while others sit idle, which is bad for slow, uneven jobs. Prefetch=1 gives fair dispatch for heavy tasks. Higher values improve throughput for small, fast messages. It also bounds consumer memory.

**Q4: How do you implement delayed retries in RabbitMQ?**
A4: Either use the delayed-message exchange plugin, or the TTL + DLX pattern: on failure, publish or dead-letter the message into a "retry" queue with a message TTL (e.g. 30 s) whose dead-letter exchange points back to the main exchange. When the TTL expires, the message returns to the main queue. Track attempts via headers (`x-death` or the delivery count) and route to a final dead queue after N attempts.

**Q5: When would you choose RabbitMQ over Kafka?**
A5: For task and job queues needing per-message acks, retries, delays, priorities and TTLs, complex routing logic in the broker (topic patterns, fanout per instance), RPC-style request and reply, lower latency at modest volume, and simpler operations for small teams. Choose Kafka when you need very high throughput, long retention and replay, many independent consumers of the same event stream, CDC and stream processing.

---

## 🔷 Trade-offs
✅ Advantages:
- Flexible routing, per-message acks, priorities, TTL, DLX, delays; mature, easy to start; low latency.

❌ Disadvantages:
- Lower throughput than Kafka at extreme scale; no long-term retention/replay (except Streams).
- Large backlogs hurt performance (memory/disk alarms); clustering/HA needs care (use quorum queues).
- Broker-side routing logic can become complex.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exchange | Receives & routes messages | messages को रास्ता देने वाला |
| Queue | Stores messages for consumers | messages रखने वाली queue |
| Binding | Rule linking exchange to queue | exchange-queue का नियम |
| Routing key | Label used for routing | routing का लेबल |
| Direct / Topic / Fanout | Exchange types | exchange के प्रकार |
| Prefetch | Max unacked per consumer | एक consumer के अधूरे messages |
| Publisher confirm | Broker confirms storage | broker की पुष्टि |
| Quorum queue | Raft-replicated queue | replicated queue |
| DLX | Dead letter exchange | फ़ेल messages का exchange |
| AMQP | Messaging protocol | messaging प्रोटोकॉल |

---

## ⚡ 3-Line Summary
**English:**
1. RabbitMQ: producers → exchanges (direct/topic/fanout/headers) → bindings → queues → consumers with acks.
2. Reliability via durable/persistent, publisher confirms, manual acks, quorum queues, DLX; prefetch controls fairness.
3. Best for task queues, routing, priorities and delayed retries; Kafka for high-throughput streaming and replay.

**Hindi:**
1. RabbitMQ: producer → exchange → binding → queue → consumer (ACK के साथ)।
2. भरोसे के लिए durable, confirms, manual ack, quorum queue, DLX; prefetch से बराबर बँटवारा।
3. Jobs, routing, priority, delayed retry के लिए बढ़िया; भारी streaming/replay के लिए Kafka।

---

## ➡️ Next Topic Suggestion
**85. AWS SQS + SNS** — The fully managed, zero-ops way to do queues and pub/sub on AWS. Next: SQS standard vs FIFO, visibility timeout, SNS fan-out to SQS, and serverless patterns with Lambda.
