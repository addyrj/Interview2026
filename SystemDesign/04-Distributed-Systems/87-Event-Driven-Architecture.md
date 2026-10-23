# 87. Event-Driven Architecture (EDA)
# हिंदी में: Event-Driven Architecture — services एक-दूसरे को सीधे कॉल करने की जगह "कुछ हुआ" (event) की घोषणा करती हैं, और जिसे ज़रूरत हो वो उस event पर प्रतिक्रिया करता है

---

## 🔵 Simple Definition (English)
In an **event-driven architecture**, services communicate by **producing and consuming events**: immutable facts that something happened (`OrderPlaced`, `PaymentCaptured`, `RiderAssigned`). Producers publish events to a **broker** (Kafka, SNS/EventBridge, RabbitMQ) **without knowing who consumes them**. Consumers subscribe and react **asynchronously**.
It enables **loose coupling, independent scaling, extensibility and real-time reactions**.

## 🔵 सरल परिभाषा (Hindi)
EDA में service दूसरी services को सीधे नहीं बुलाती, बल्कि घोषणा करती है "ऑर्डर बन गया" (event)। जिस भी service को इससे मतलब है — notification, delivery, analytics — वो ख़ुद सुनकर अपना काम करती है।
Producer को पता नहीं होता कि कौन सुन रहा है — इससे services अलग-अलग रहती हैं और नए फ़ीचर जोड़ना आसान होता है।

---

## 🔴 Problem it Solves
With synchronous request/response between many services:
```
Order Service → calls Notification, Delivery, Loyalty, Analytics, Fraud, Restaurant ... directly
```
- **Tight coupling:** Order Service must know every downstream and change when one is added.
- **Availability multiplies down:** any downstream failure fails or slows order placement.
- **Latency:** the user waits for all calls.
- **Hard to extend:** a new "send coupon after first order" feature means editing Order Service again.

With events: Order Service publishes `OrderPlaced` **once**; any number of services react. New features **subscribe** without touching the producer.

## 🔴 यह क्यों बना? (Hindi)
सीधे कॉल्स में Order service को हर service (notification, delivery, loyalty, analytics) के बारे में पता होना चाहिए; कोई एक गिरे तो ऑर्डर फ़ेल; यूज़र सबका इंतज़ार करे; नया फ़ीचर = Order service में फिर बदलाव।
Events में Order service बस एक बार `OrderPlaced` बोलती है — बाक़ी सब ख़ुद सुनकर काम करते हैं, नया फ़ीचर सिर्फ़ subscribe करके जुड़ जाता है।

---

## 🟢 How it Works — Step by Step

```
                       ┌──────────────── Event Broker (Kafka / EventBridge / SNS) ────────────────┐
 Order Svc ─ OrderPlaced ►│ topic: orders                                                         │
 Payment Svc ─ PaymentCaptured ►│ topic: payments                                                  │
 Delivery Svc ─ RiderAssigned ►│ topic: delivery                                                   │
                       └───┬──────────────┬──────────────┬──────────────┬──────────────┬──────────┘
                           ▼              ▼              ▼              ▼              ▼
                   Notification     Restaurant      Analytics      Loyalty        Search/Read
                   (push/SMS)       (KDS screen)    (ClickHouse)   (points)       models (CQRS)
Producers don't know consumers. Consumers own their reactions and their data.
```

### Event types (important distinction)

```
1. Event notification (thin)     { type: "OrderPlaced", orderId: 9001 }
   → consumer calls back for details if needed  (small, but extra calls & coupling to producer API)

2. Event-carried state transfer (fat)
   { type: "OrderPlaced", orderId, userId, items[], total, address, restaurantId, placedAt }
   → consumer has everything; can keep its own local copy (no callback) ⭐ common

3. Domain event vs integration event
   Domain event: internal to a service's model
   Integration event: public contract for other services (versioned, stable)

4. Commands vs events
   Command: "SendEmail" — directed to ONE handler, may be rejected (imperative)
   Event:   "OrderPlaced" — fact in the past, broadcast, can't be rejected (declarative)
```

### Event design rules

```
✓ Name in PAST TENSE: OrderPlaced, PaymentFailed (facts, not requests)
✓ Include: eventId (UUID), eventType, version, occurredAt, producer, correlationId/traceId,
           aggregateId (key for ordering), payload
✓ Immutable; never change meaning of an existing field
✓ Schema registry + compatibility rules (backward compatible changes only: add optional fields)
✓ Partition/order by aggregate id (orderId) when order matters
✓ Publish via OUTBOX (no dual writes)
✓ Consumers idempotent + DLQ
```

### Envelope example (CloudEvents-style)
```json
{
  "id": "evt_7f3a1c",
  "type": "food.order.placed.v1",
  "source": "order-service",
  "time": "2026-10-18T13:20:05Z",
  "subject": "order/9001",
  "traceparent": "00-4bf92f...-01",
  "data": { "orderId": 9001, "userId": 42, "restaurantId": 7, "total": 450, "items": [ { "id": 101, "qty": 2 } ] }
}
```

### Challenges

```
Eventual consistency      → UI must handle "processing" states (Topic 67)
Debugging/observability   → flows are implicit → distributed tracing with correlation ids, event catalogs
Ordering & duplicates     → per-key partitions, idempotent consumers
Schema evolution          → versioning, registry, consumer-tolerant parsing
"Event spaghetti"         → too many services reacting to too many events → hard to reason about
                            → document flows, use orchestration (sagas) for critical workflows
Replays                   → consumers must handle reprocessing safely
Testing                   → contract tests for events, local broker in CI
```

### EDA styles
```
Pub/sub events (notification)   → most microservices
Event streaming (Kafka)         → continuous processing, analytics, CDC
Event sourcing (Topic 72)       → events as source of truth
Choreography (Topic 70)         → workflows emerge from reactions
Serverless EDA                  → EventBridge/SNS + Lambda
```

## 🟢 कैसे काम करता है? (Hindi)
1. कुछ होने पर service एक event publish करती है (भूतकाल में नाम: `OrderPlaced`), broker (Kafka/SNS) पर।
2. जो services subscribe हैं (notification, analytics, loyalty) वो अपने आप, अपनी रफ़्तार से प्रतिक्रिया करती हैं।
3. "Fat" event में पूरी जानकारी होती है ताकि consumer को वापस कॉल न करना पड़े; event id, version, समय, trace id हमेशा रखो।
4. Command ("SendEmail" — एक को आदेश) और event ("OrderPlaced" — सबको तथ्य) अलग हैं।
5. चुनौतियाँ: eventual consistency, debugging (trace ids), duplicates/ordering (idempotency, key), schema versioning — ज़रूरी workflows के लिए orchestration।

---

## 🟡 Real World Example

**Zomato/Swiggy order lifecycle** — `OrderPlaced` → restaurant tablet rings, rider assignment begins, the customer gets a push. `OrderPickedUp` → live tracking starts. `OrderDelivered` → rating prompt, loyalty points, invoice email, analytics. Each is a separate consumer, and new features (like "Gold membership savings") are added by subscribing.

**Netflix** — playback, viewing and personalization events flow through Kafka into many consumers (recommendations, A/B analysis, billing signals) in real time.

**Uber** — trip state events drive pricing, ETAs, safety features, receipts and driver earnings, each consumed independently.

**Banks (UPI notifications)** — a transaction event triggers SMS, push, fraud scoring, statement updates and rewards asynchronously, while the payment itself completes synchronously.

## 🟡 Real Example Hindi में
Zomato में `OrderPlaced` से रेस्टोरेंट का tablet बजता है, rider assign होता है, ग्राहक को push जाता है; `OrderDelivered` से rating, loyalty points, invoice — हर काम अलग consumer करता है।
UPI transaction होते ही event से SMS, push, fraud जाँच, rewards अलग-अलग होते हैं, जबकि पेमेंट ख़ुद synchronous होता है।

---

## 🟠 My Stack Example

### Shared event contracts (monorepo package)
```ts
// packages/events/order.ts
import { z } from 'zod';
export const OrderPlacedV1 = z.object({
  id: z.string().uuid(), type: z.literal('food.order.placed.v1'), time: z.string(), source: z.string(),
  data: z.object({ orderId: z.number(), userId: z.number(), restaurantId: z.number(), total: z.number(),
                   items: z.array(z.object({ id: z.number(), qty: z.number() })) }),
}).passthrough();                                   // tolerant reader: allow new fields
export type OrderPlacedV1 = z.infer<typeof OrderPlacedV1>;
```

### Producer: outbox → Kafka (Node)
```js
await withTx(async (tx) => {
  const order = await createOrder(tx, input);
  await tx.query('INSERT INTO outbox(aggregate_id, event_type, payload) VALUES ($1,$2,$3)', [
    order.id, 'food.order.placed.v1',
    { id: crypto.randomUUID(), type: 'food.order.placed.v1', source: 'order-service', time: new Date().toISOString(),
      data: { orderId: order.id, userId: order.userId, restaurantId: order.restaurantId, total: order.total, items: order.items } },
  ]);
});
// relay publishes to topic "orders" with key = orderId (Topic 68)
```

### Consumers (each its own service, own DB)
```js
// loyalty-service
onEvent('food.order.delivered.v1', async (evt, tx) => {
  if (await seen(tx, evt.id)) return;                                  // idempotent
  await tx.query('UPDATE loyalty SET points = points + $1 WHERE user_id = $2', [Math.floor(evt.data.total / 100), evt.data.userId]);
  await markSeen(tx, evt.id);
});

// notification-service
onEvent('food.order.placed.v1', async (evt) => pushService.send(evt.data.userId, 'Order placed! 🎉 Restaurant is confirming.'));
```

### FastAPI consumer — analytics
```python
async for msg in consumer:                                   # topic "orders", group "analytics"
    evt = json.loads(msg.value)
    if evt["type"] == "food.order.placed.v1":
        await clickhouse.insert("order_events", [evt["data"] | {"event_time": evt["time"]}])
    await consumer.commit()
```

### Serverless EDA on AWS (EventBridge rule)
```json
{
  "Source": ["order-service"],
  "DetailType": ["food.order.placed.v1"],
  "Detail": { "total": [{ "numeric": [">", 2000] }] }
}
// → target: Lambda "notify-high-value-orders"; archive + replay enabled on the bus
```

### Observability for events
```
- Propagate traceparent in event headers → OpenTelemetry links producer & consumer spans
- Event catalog (AsyncAPI spec / EventCatalog) documenting topics, schemas, owners, consumers
- Metrics per consumer: lag, processing time, error rate, DLQ size
```

### Frontend/mobile in an event-driven backend
```
Client places order (sync API, gets 201 with orderId)
Backend events flow → notification service pushes status updates over WebSocket / FCM
App shows a live timeline: Placed → Accepted → Preparing → Picked up → Delivered
```

---

## ⚫ Interview Questions + Answers

**Q1: What is event-driven architecture and what are its benefits?**
A1: An architecture where components communicate by publishing and consuming events (immutable facts about state changes) through a broker, rather than calling each other directly. Benefits: loose coupling (producers don't know consumers), easy extensibility (new consumers subscribe without changing producers), better resilience and availability (consumers can be down and catch up later), independent scaling, real-time reactions, and natural support for audit, analytics and CQRS read models.

**Q2: What's the difference between an event and a command?**
A2: An event states that something already happened (`OrderPlaced`). It's broadcast to any interested consumers, the producer doesn't care who handles it, and it can't be rejected. A command is a request for a specific action (`SendInvoice`, `ChargeCard`), directed at one handler that may accept or reject it. Events are named in the past tense, commands in the imperative. Mixing them up leads to hidden coupling.

**Q3: Thin events vs fat events?**
A3: Thin (notification) events carry only identifiers. Consumers call the producer's API for details, which keeps events small but adds latency, load and runtime coupling, and the data may have changed since the event. Fat (event-carried state transfer) events include the relevant state, so consumers can act and keep local copies without callbacks. They're larger, and you must manage schema evolution and avoid sensitive data. Fat events are usually preferred for integration.

**Q4: What are the main challenges of EDA and how do you address them?**
A4: Eventual consistency (design UX and processes for it). Observability (correlation and trace IDs in event headers, distributed tracing, an event catalog). Duplicates and ordering (idempotent consumers, partition by aggregate key). Reliable publishing (transactional outbox or CDC). Schema evolution (versioned events, schema registry, tolerant readers). Error handling (retries, DLQs). Complexity from implicit flows (documentation, and orchestration for critical multi-step workflows).

**Q5: When should you NOT use event-driven communication?**
A5: When the caller needs an immediate answer to continue (authentication, price calculation, stock check at checkout, fraud decisions that block a payment); for simple CRUD systems with few services, where a broker adds unnecessary complexity; when strict strong consistency is required across steps (keep them in one service or transaction); and for request/response queries. Most systems mix synchronous APIs for queries and critical decisions with events for side effects and integration.

---

## 🔷 Trade-offs
✅ Advantages:
- Loose coupling, extensibility, resilience, independent scaling, real-time processing, audit trail.

❌ Disadvantages:
- Eventual consistency, harder debugging and testing, duplicates/ordering concerns.
- Schema governance needed; risk of "event spaghetti"; broker becomes critical infrastructure.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event | Immutable fact that something happened | कुछ हुआ, उसका अटल तथ्य |
| Producer / Consumer | Publishes / reacts to events | event भेजने / सुनने वाला |
| Broker | Event transport (Kafka, SNS) | event पहुँचाने वाला |
| Command | Request for an action | काम का आदेश |
| Event notification | Thin event with IDs | सिर्फ़ id वाला event |
| Event-carried state transfer | Fat event with data | पूरी जानकारी वाला event |
| Schema registry | Central event schemas | event ढाँचों का भंडार |
| Correlation ID | Links related events | जुड़े events की पहचान |
| Event catalog | Documentation of events | events की सूची/दस्तावेज़ |

---

## ⚡ 3-Line Summary
**English:**
1. EDA: services publish past-tense events to a broker; any number of consumers react asynchronously — loose coupling and extensibility.
2. Design events as versioned, immutable, fat (usually) contracts with ids, trace ids and keys; publish via outbox; consume idempotently.
3. Accept eventual consistency, invest in tracing/schemas/DLQs, and keep sync calls for decisions needing immediate answers.

**Hindi:**
1. EDA: services भूतकाल वाले events broker पर डालती हैं; कितनी भी services सुनकर काम करती हैं।
2. Events versioned, अटल, पूरी जानकारी वाले, id और trace id के साथ; outbox से भेजो, idempotent तरीके से लो।
3. Eventual consistency स्वीकार करो, tracing/schemas/DLQ रखो; तुरंत जवाब वाले फ़ैसलों के लिए sync calls।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Event-Driven Architecture](https://www.youtube.com/results?search_query=event+driven+architecture+bytebytego) | Events vs commands, pub/sub, choreography |
| 📺 YouTube | [Gaurav Sen — Event Driven Systems](https://www.youtube.com/results?search_query=event+driven+architecture+gaurav+sen) | Decoupling services, eventual consistency tradeoffs |
| 📝 Article | [Martin Fowler — Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html) | Four patterns: event notification, event-carried state, event sourcing, CQRS |
| 📝 Article | [AWS — Event-Driven Architecture](https://aws.amazon.com/event-driven-architecture/) | EventBridge, SNS/SQS patterns in production |
| 🐙 GitHub | [awesome-event-driven-architecture](https://github.com/lutzroeder/awesome-event-driven-architecture) | Curated list of EDA patterns, frameworks, case studies |

---

## ➡️ Next Topic Suggestion
**88. Distributed Locks** — Sometimes only ONE instance in the whole cluster may do something (run a job, process a payment, update a shared resource). Next: distributed locks with Redis, DB and etcd, leases, fencing tokens, and why they're trickier than they look.
