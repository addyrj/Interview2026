# 82. Message Queues
# हिंदी में: Message Queue — एक बीच का डिब्बा जहाँ एक service काम (message) डाल देती है और दूसरी service अपनी रफ़्तार से उसे उठाकर करती है; दोनों को एक-दूसरे का इंतज़ार नहीं करना पड़ता

---

## 🔵 Simple Definition (English)
A **message queue** is a component that stores **messages** sent by **producers** until **consumers** process them. It enables **asynchronous communication**: the producer doesn't wait for the work to be done, only for the queue to accept the message.
It **decouples** services in **time** (consumer can be down), **speed** (absorbs bursts) and **knowledge** (producer doesn't know who consumes).
Examples: **RabbitMQ, AWS SQS, Kafka** (log-based), **Redis Streams/BullMQ**, Google Pub/Sub, Azure Service Bus, NATS.

## 🔵 सरल परिभाषा (Hindi)
Message queue एक बीच का डिब्बा है — producer काम (message) डालता है और तुरंत आगे बढ़ जाता है; consumer अपनी रफ़्तार से उठाकर काम करता है।
इससे services अलग रहती हैं: consumer बंद हो तो भी messages सुरक्षित, अचानक भीड़ queue में जमा हो जाती है, और producer को पता भी नहीं कि काम कौन करेगा।

---

## 🔴 Problem it Solves
With only synchronous calls:
- **Slow user requests:** placing an order waits for email, SMS, invoice PDF, analytics, loyalty points → 3 s.
- **Tight coupling:** if the email service is down, order placement fails.
- **Traffic spikes:** 50,000 orders in a minute during a sale → downstream services overwhelmed.
- **Retries:** where do failed tasks go? Lost on a crash.

Queues provide **async processing, buffering (load leveling), reliability (persist + retry), and decoupling**.

## 🔴 यह क्यों बना? (Hindi)
सब कुछ synchronous हो तो ऑर्डर देते समय email, SMS, invoice, analytics सबका इंतज़ार — 3 सेकंड; email service बंद तो ऑर्डर ही फ़ेल; सेल में भीड़ से सब गिर जाएँ; फ़ेल काम crash में खो जाएँ।
Queue से काम पीछे (async) होता है, भीड़ जमा होकर धीरे-धीरे निकलती है, messages सुरक्षित रहते हैं, और services एक-दूसरे पर निर्भर नहीं रहतीं।

---

## 🟢 How it Works — Step by Step

```
 Producer (Order API)                Queue (broker)                      Consumers (workers)
     │ 1. publish {orderId:9001}  ┌────────────────────┐ 3. receive    ┌─────────────┐
     │───────────────────────────►│ [m5][m4][m3][m2]   │──────────────►│ Email worker│ 4. process
     │◄── 2. ack (stored durably) │                    │               └──────┬──────┘
     │   → respond 201 to user    └────────────────────┘                      │ 5. ACK → message deleted
     │                                    ▲                                    │    (no ACK / crash →
     │                                    └──────── redeliver ─────────────────┘     redelivered later)
```

### Two messaging models

```
1. Point-to-point (work queue)      — each message processed by ONE consumer
   Producer → [queue] → Worker A | Worker B | Worker C   (competing consumers → scale out)
   Use: jobs/tasks (send email, resize image, generate invoice)   → SQS, RabbitMQ queue, BullMQ

2. Publish/Subscribe (fan-out)       — each message delivered to EVERY subscriber group
   Producer → [topic "order.placed"] → Notification svc
                                     → Analytics svc
                                     → Loyalty svc
   Use: events many services react to   → Kafka topics, SNS→SQS, RabbitMQ fanout exchange
```

### Delivery guarantees

```
At-most-once   → may lose messages, never duplicates (ack before processing) — metrics/logs
At-least-once  → never lose (ack after processing), may DUPLICATE ⭐ default in most systems
                 → consumers must be IDEMPOTENT (Topic 64)
Exactly-once   → hard; achievable within a system (Kafka transactions) or EFFECTIVELY via
                 at-least-once + idempotent consumers / dedup
```

### Key concepts

```
Acknowledgement (ACK)  → consumer confirms done; unacked → redelivered
Visibility timeout     → (SQS) message hidden while being processed; reappears if not deleted in time
Prefetch / batch size  → how many messages a consumer takes at once
Retry + backoff        → failed messages retried with delay
Dead Letter Queue (DLQ)→ messages failing N times moved aside for inspection (Topic 86)
Ordering               → FIFO per queue / per partition / per message group; global order is expensive
Durability             → persist to disk/replicate so broker crash doesn't lose messages
TTL / expiry           → stale messages dropped
Backpressure           → queue depth grows → scale consumers / slow producers
Poison message         → a message that always fails → DLQ
```

### Queue vs Log (RabbitMQ/SQS vs Kafka)

```
┌──────────────────────┬──────────────────────────────────┬──────────────────────────────────┐
│                      │ Traditional queue (RabbitMQ, SQS)│ Log/stream (Kafka, Kinesis)       │
├──────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ After consumption    │ Message deleted                  │ Retained (days/forever); offset  │
│                      │                                  │ per consumer group               │
│ Replay               │ No                               │ Yes (rewind offset)              │
│ Consumers            │ Compete for messages             │ Many groups each read all        │
│ Ordering             │ Per queue (FIFO variants)        │ Per partition                    │
│ Routing              │ Rich (RabbitMQ exchanges)        │ By topic + key                   │
│ Throughput           │ High                             │ Very high (millions/s)           │
│ Best for             │ Task/job queues, RPC-ish work,   │ Event streaming, event sourcing, │
│                      │ per-message retries/delays       │ analytics, CDC, many consumers   │
└──────────────────────┴──────────────────────────────────┴──────────────────────────────────┘
```

### When to use a queue vs a direct call
```
Use a queue when: work can be done later (email, PDF), you need buffering for spikes, the consumer
may be down, fan-out to many services, retries without blocking users, rate-limited downstreams.
Use a direct (sync) call when: the user needs the result NOW (price, auth, stock check), or it's a
simple query.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Producer message queue में डालता है; queue उसे सुरक्षित (disk/replica) रखकर "ack" देता है — producer तुरंत यूज़र को जवाब दे देता है।
2. Consumer message उठाता है, काम करता है, फिर ACK — तब message हटता है; ACK न आए (crash) तो message दोबारा मिलता है।
3. दो तरीके: work queue (हर message एक worker को) और pub/sub (हर message हर subscriber service को)।
4. ज़्यादातर सिस्टम "at-least-once" देते हैं — duplicate आ सकते हैं, इसलिए consumer idempotent होना चाहिए।
5. बार-बार फ़ेल होने वाला message DLQ में जाता है; queue लंबी हो तो और workers लगाओ।

---

## 🟡 Real World Example

**Swiggy/Zomato order placement** — the order API commits the order and publishes `order.placed`. Restaurant notification, delivery assignment, customer SMS, invoice generation, analytics and loyalty services all consume it asynchronously. The user sees "Order placed" in under a second.

**Uber** — uses Kafka at massive scale (trillions of messages per day) for trip events, driver locations, surge pricing inputs and analytics pipelines.

**Instagram** — photo upload returns quickly. Thumbnail generation, feed fan-out, content moderation and notifications happen via queues and workers.

**IRCTC / sale events** — queues absorb booking surges and process them at the rate the core booking system can handle (load leveling).

## 🟡 Real Example Hindi में
Swiggy में ऑर्डर बनते ही `order.placed` message जाता है — रेस्टोरेंट, डिलीवरी, SMS, invoice, analytics सब उसे बाद में उठाते हैं; यूज़र को 1 सेकंड में "Order placed" दिख जाता है।
Uber रोज़ खरबों messages Kafka से भेजता है। Instagram पर फ़ोटो upload तुरंत हो जाती है, thumbnails और notifications बाद में queue से बनते हैं।

---

## 🟠 My Stack Example

### Node.js — BullMQ (Redis) work queue with retries
```js
import { Queue, Worker } from 'bullmq';
const connection = { host: 'redis-queue', port: 6379 };
export const emailQueue = new Queue('emails', { connection });

// producer: inside API (after DB commit — or via outbox for strict reliability)
await emailQueue.add('order-confirmation', { orderId, to: user.email }, {
  jobId: `order-confirmation:${orderId}`,          // dedup: same job id won't be added twice
  attempts: 5, backoff: { type: 'exponential', delay: 2000 },
  removeOnComplete: 1000, removeOnFail: false,
});

// consumer: separate process/container
new Worker('emails', async (job) => {
  const order = await getOrder(job.data.orderId);
  await mailer.send(job.data.to, renderReceipt(order));     // provider idempotency key = job.id
}, { connection, concurrency: 20 });
```

### AWS SQS (Node SDK v3) — producer & long-polling consumer
```js
import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';
const sqs = new SQSClient({ region: 'ap-south-1' });

await sqs.send(new SendMessageCommand({ QueueUrl: Q, MessageBody: JSON.stringify({ orderId }) }));

async function poll() {
  while (true) {
    const { Messages = [] } = await sqs.send(new ReceiveMessageCommand({
      QueueUrl: Q, MaxNumberOfMessages: 10, WaitTimeSeconds: 20, VisibilityTimeout: 60 }));
    for (const m of Messages) {
      try {
        await handle(JSON.parse(m.Body));                       // idempotent!
        await sqs.send(new DeleteMessageCommand({ QueueUrl: Q, ReceiptHandle: m.ReceiptHandle }));  // ACK
      } catch (e) { logger.error({ e }); /* not deleted → reappears after visibility timeout → DLQ after N */ }
    }
  }
}
```

### Python — Celery (RabbitMQ/Redis) with FastAPI
```python
# tasks.py
celery = Celery("app", broker="amqp://rabbitmq", backend="redis://redis")

@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5}, acks_late=True)
def generate_invoice(self, order_id: int):
    if already_generated(order_id): return          # idempotent
    pdf = render_pdf(order_id); upload_to_s3(pdf); mark_generated(order_id)

# FastAPI endpoint
@app.post("/orders", status_code=201)
async def place(body: OrderIn, user=Depends(current_user)):
    order = await create_order(body, user)
    generate_invoice.delay(order.id)                # async
    return order
```

### Docker Compose
```yaml
services:
  redis-queue: { image: redis:7, command: ["redis-server", "--appendonly", "yes", "--maxmemory-policy", "noeviction"] }
  rabbitmq:    { image: rabbitmq:3-management, ports: ["15672:15672"] }
  api:         { build: ./api }
  worker:      { build: ./api, command: node dist/worker.js, deploy: { replicas: 3 } }
```

### Monitoring a queue
```
Queue depth (messages waiting), age of oldest message, processing rate, failure rate, DLQ size
Alert: oldest message age > 5 min, DLQ > 0, depth growing for 10 min
Autoscale workers on depth (KEDA on K8s, ECS step scaling on ApproximateNumberOfMessagesVisible)
```

### Mobile angle
Push notifications are the end of a queue pipeline: event → notification service (queue) → FCM/APNs. The app also keeps a local outbox of actions when offline, then sends them later. That's a client-side queue.

---

## ⚫ Interview Questions + Answers

**Q1: What is a message queue and why use one?**
A1: A broker that durably stores messages from producers until consumers process them, enabling asynchronous communication. Benefits: faster user-facing responses (slow work offloaded), decoupling (producer and consumer evolve and fail independently), load leveling during spikes, reliable retries and DLQs, fan-out to multiple services, and independent scaling of consumers.

**Q2: Point-to-point vs publish/subscribe?**
A2: Point-to-point (work queue): each message is processed by exactly one of the competing consumers, used for distributing tasks across workers. Pub/sub: each message is delivered to every subscriber (or every consumer group), used for broadcasting events that multiple services react to. Kafka consumer groups combine both: pub/sub across groups, competing consumers within a group.

**Q3: Explain at-most-once, at-least-once and exactly-once delivery.**
A3: At-most-once: ack before processing, so a crash loses the message but never duplicates it. At-least-once: ack after processing, so a crash causes redelivery and possible duplicates. This is the common default. Exactly-once: each message affects state once. True end-to-end exactly-once is hard, so it's achieved within a system (Kafka transactions) or effectively via at-least-once delivery plus idempotent consumers (dedup by message ID in the same transaction as the effect).

**Q4: How do you guarantee a message is published when the DB transaction commits?**
A4: Avoid dual writes (DB commit then publish, where a crash in between loses the event). Use the transactional outbox: insert the event into an outbox table in the same DB transaction as the business change, and have a relay process or CDC (Debezium) publish outbox rows to the broker and mark them sent. Delivery is at-least-once, so consumers deduplicate.

**Q5: Queue depth keeps growing. What do you do?**
A5: Determine whether consumers are too slow or failing. Check the error rate, the DLQ, processing time per message and downstream bottlenecks (DB, third-party rate limits). Scale consumers horizontally if the downstream can handle it, and batch processing. Fix poison messages (DLQ) and optimize handlers. Apply backpressure to or throttle producers for non-critical messages, add TTLs to drop stale work, and alert on oldest-message age.

---

## 🔷 Trade-offs
✅ Advantages:
- Decoupling, async speed, buffering spikes, reliable retries, independent scaling, fan-out.

❌ Disadvantages:
- Eventual consistency (work done later); harder debugging/tracing across async hops.
- Duplicates & ordering issues → idempotency needed.
- Another critical infrastructure component to run and monitor.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Message queue | Buffer between producer and consumer | बीच का डिब्बा |
| Producer / Consumer | Sender / processor of messages | भेजने वाला / करने वाला |
| Broker | Server managing queues | queue चलाने वाला सर्वर |
| ACK | Consumer confirms processing | काम पूरा होने की पुष्टि |
| At-least-once | No loss, may duplicate | कम से कम एक बार |
| Visibility timeout | Hidden while processing | प्रोसेसिंग के समय छिपा |
| Competing consumers | Workers share a queue | workers में बँटवारा |
| Pub/Sub | Broadcast to all subscribers | सबको भेजना |
| Load leveling | Smoothing spikes via queue | भीड़ को समान करना |
| Backpressure | Signal to slow producers | धीमा करने का संकेत |

---

## ⚡ 3-Line Summary
**English:**
1. Message queues let producers hand off work asynchronously; consumers process at their own pace with ACKs and retries.
2. Models: work queue (one consumer per message) vs pub/sub (all subscribers); most give at-least-once → idempotent consumers.
3. Use outbox for reliable publishing, DLQs for poison messages, and monitor depth/age; Kafka for streams, RabbitMQ/SQS/BullMQ for jobs.

**Hindi:**
1. Queue से काम async — producer डालकर आगे, consumer अपनी रफ़्तार से ACK के साथ करता है।
2. Work queue (एक को) बनाम pub/sub (सबको); ज़्यादातर at-least-once → consumer idempotent हो।
3. भरोसेमंद publish के लिए outbox, फ़ेल messages के लिए DLQ; streams के लिए Kafka, jobs के लिए SQS/RabbitMQ/BullMQ।

---

## ➡️ Next Topic Suggestion
**83. Kafka — Event Streaming** — The most important streaming platform in modern backends. Next: topics, partitions, offsets, consumer groups, replication, ordering, and how companies like Uber and LinkedIn use Kafka.
