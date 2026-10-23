# 68. Distributed Transactions
# हिंदी में: Distributed Transaction — एक ही business काम जिसमें कई अलग databases/services का डेटा एक साथ, सही-सही बदलना हो (सब या कुछ नहीं)

---

## 🔵 Simple Definition (English)
A **distributed transaction** is a single logical operation that must update data in **multiple independent systems** (different databases, microservices, message brokers, external APIs) so that the overall result is **consistent**: either all parts take effect, or the system ends in a well-defined, correct state.
Since a local ACID transaction covers only **one database**, distributed transactions need **coordination patterns**: **Two-Phase Commit (2PC)**, **Sagas**, the **Transactional Outbox**, **idempotency**, and **reconciliation**.

## 🔵 सरल परिभाषा (Hindi)
जब एक काम (जैसे ऑर्डर देना) में कई services/databases (order, payment, inventory) का डेटा बदलना हो, तो वो distributed transaction है।
एक DB का transaction सिर्फ़ उसी DB को संभालता है; कई systems के लिए 2PC, Saga, Outbox जैसे तरीके चाहिए ताकि सब सही रहे।

---

## 🔴 Problem it Solves
Placing an order in a microservices food app:
```
1. Order Service      → create order        (orders DB)
2. Payment Service    → charge ₹450         (payments DB + Razorpay)
3. Inventory/Restaurant → reserve items     (restaurant DB)
4. Delivery Service   → assign rider        (delivery DB)
```
Failures can happen **between any two steps**: payment charged but order not saved; stock reserved but payment failed; the service crashes after step 2. Without coordination:
- **Money taken, no order** (angry customers, refunds, legal risk).
- **Order confirmed, but restaurant never received it**.
- **Inconsistent data** across services, discovered days later.

You can't wrap all of this in `BEGIN … COMMIT`. That's the distributed transaction problem.

## 🔴 यह क्यों बना? (Hindi)
ऑर्डर देने में order, payment, inventory, delivery — चार अलग services और DBs। किसी भी दो कदम के बीच कुछ फ़ेल हो सकता है: पैसे कटे पर ऑर्डर नहीं बना, या stock रुका पर पेमेंट फ़ेल।
इन सबको एक `BEGIN … COMMIT` में नहीं डाल सकते — इसीलिए distributed transactions के ख़ास तरीके चाहिए।

---

## 🟢 How it Works — Step by Step

### Why it's hard

```
- No shared transaction manager across independent DBs / services / third-party APIs
- Network failures make outcomes UNKNOWN (did the payment call succeed?)
- Services fail independently and at different times
- Locks across systems for long = poor availability & throughput
- External APIs (bank, SMS, Razorpay) can't participate in your rollback
```

### The approaches (overview)

```
┌───────────────────────────┬──────────────────────────────────────┬───────────────────────────┐
│ Approach                  │ Idea                                 │ Consistency / Trade-off   │
├───────────────────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Avoid it (design)         │ Keep data needing atomicity in ONE   │ Best when possible ✅     │
│                           │ service/DB (right boundaries)        │                           │
│ Two-Phase Commit (2PC/XA) │ Coordinator: prepare all → commit all│ Atomic, but blocking,     │
│                           │ (Topic 69)                           │ slow, fragile             │
│ Saga (Topic 70)           │ Sequence of LOCAL txns + compensating│ Eventual consistency,     │
│                           │ actions on failure                   │ highly available ⭐        │
│ Transactional Outbox      │ Write data + event in same local txn;│ Guarantees no lost events │
│                           │ relay publishes later                │ ⭐ (used with sagas)       │
│ Idempotent consumers      │ Dedup so retries are safe (Topic 64) │ Required for at-least-once│
│ TCC (Try-Confirm-Cancel)  │ Reserve → confirm or cancel           │ Explicit reservations     │
│ Reconciliation jobs       │ Periodically detect & fix mismatches │ Safety net (finance!)     │
│ Distributed SQL           │ Spanner/CockroachDB do it internally │ Strong, but one DB system │
└───────────────────────────┴──────────────────────────────────────┴───────────────────────────┘
```

### The dual-write problem (most common bug)

```
❌ Code that writes to DB and publishes to Kafka separately:
   await db.insert(order)          ✓
   await kafka.publish(OrderPlaced) 💥 crash / network error → event lost forever
   (or publish succeeds, DB insert fails → ghost event)

✅ Transactional Outbox:
   BEGIN
     INSERT INTO orders ...
     INSERT INTO outbox(event_type, payload) ...
   COMMIT                           ← both or neither (same DB)
   Relay process / CDC (Debezium) reads outbox → publishes to Kafka → marks sent
   (at-least-once → consumers must be idempotent)
```

### TCC — Try / Confirm / Cancel (reservation pattern)

```
Try:     inventory.reserve(items, ttl=10min)   payment.authorize(₹450) (hold, not capture)
Confirm: inventory.commit(reservation)          payment.capture(auth)
Cancel:  inventory.release(reservation)         payment.void(auth)
Reservations expire automatically if the coordinator dies → no permanent locks.
(This is how card payments work: authorize → capture/void; also hotel/flight holds)
```

### Uncertain outcomes (timeouts)
```
Payment API call times out → DID it charge? Unknown!
→ Never assume. Use idempotency keys and QUERY the status (GET /payments?order_id=...),
  or wait for the webhook. Mark order "PAYMENT_PENDING" until resolved.
```

## 🟢 कैसे काम करता है? (Hindi)
1. सबसे अच्छा: service boundaries ऐसे रखो कि जिन चीज़ों को एक साथ बदलना है वो एक ही DB में हों।
2. 2PC: एक coordinator सबसे पूछता है "तैयार?", सब हाँ कहें तो "commit" — सही पर धीमा और अटकने वाला।
3. Saga: हर service अपना local transaction करती है; बीच में फ़ेल हुआ तो पिछले कदम उल्टे (compensate) किए जाते हैं — जैसे refund।
4. Outbox: डेटा और event एक ही local transaction में सेव करो, फिर अलग process event भेजे — event कभी नहीं खोता।
5. Timeout पर मान मत लो — status पूछो/webhook का इंतज़ार करो; idempotency और reconciliation हमेशा रखो।

---

## 🟡 Real World Example

**UPI failed transactions** — "money debited but transaction failed" happens when steps across the payer bank, NPCI and payee bank don't all complete. The system uses reversal (compensation) and reconciliation, and RBI mandates auto-reversal within T+1 days with penalties for delays. That's a saga plus reconciliation at national scale.

**Uber / Swiggy order flows** — implemented as sagas orchestrated by workflow engines (Uber built **Cadence**, now **Temporal**): create order, authorize payment, confirm restaurant, assign courier, with compensations like refunds and cancellations.

**Booking.com / MakeMyTrip** — a flight + hotel package uses holds (TCC): hold the seat, hold the room, take payment, then confirm both, or release the holds.

**Shopify / e-commerce** — orders, payments (via gateways) and inventory are coordinated with outbox events and idempotent consumers, plus nightly reconciliation against payment gateway settlement reports.

## 🟡 Real Example Hindi में
UPI में "पैसे कटे पर transaction फ़ेल" — कई बैंकों के बीच का कदम अधूरा रह गया; reversal (compensation) और reconciliation से पैसे लौटते हैं, RBI नियम के अनुसार T+1 में।
Uber ने Cadence (अब Temporal) बनाया ताकि ऑर्डर का पूरा flow saga की तरह चले — फ़ेल होने पर refund/cancel अपने आप।

---

## 🟠 My Stack Example

### Outbox table + relay (Node + Postgres)
```sql
CREATE TABLE outbox (
  id BIGSERIAL PRIMARY KEY,
  aggregate_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ
);
CREATE INDEX ON outbox (id) WHERE published_at IS NULL;
```
```js
// 1) business write + event in ONE local transaction
await withTx(async (tx) => {
  const { rows: [o] } = await tx.query(
    "INSERT INTO orders(user_id, total, status) VALUES ($1,$2,'PENDING_PAYMENT') RETURNING id", [uid, total]);
  await tx.query('INSERT INTO outbox(aggregate_id, event_type, payload) VALUES ($1,$2,$3)',
                 [o.id, 'OrderCreated', { orderId: o.id, userId: uid, total }]);
});

// 2) relay worker: publish unsent events (at-least-once)
async function relay() {
  await withTx(async (tx) => {
    const { rows } = await tx.query(
      'SELECT * FROM outbox WHERE published_at IS NULL ORDER BY id LIMIT 100 FOR UPDATE SKIP LOCKED');
    for (const e of rows) {
      await producer.send({ topic: e.event_type, messages: [{ key: e.aggregate_id, value: JSON.stringify({ id: e.id, ...e.payload }) }] });
      await tx.query('UPDATE outbox SET published_at = now() WHERE id = $1', [e.id]);
    }
  });
}
setInterval(relay, 500);
// (Production alternative: Debezium CDC reading the WAL → Kafka, no polling)
```

### Handling an uncertain payment call
```js
async function chargeOrder(order) {
  try {
    const p = await razorpay.payments.capture(order.paymentId, order.total, 'INR');   // idempotent by paymentId
    await markPaid(order.id, p.id);
  } catch (e) {
    if (isTimeout(e)) {
      await setStatus(order.id, 'PAYMENT_UNKNOWN');   // don't guess
      await queue.add('verify-payment', { orderId: order.id }, { delay: 30_000 });   // query status later
    } else {
      await setStatus(order.id, 'PAYMENT_FAILED');    // triggers compensation (release stock)
    }
  }
}
```

### Reconciliation job (finance safety net) — FastAPI/cron
```python
async def reconcile_payments(day: date):
    gateway = {p["order_id"]: p for p in await razorpay_settlements(day)}     # what the gateway says
    ours = {o.id: o for o in await orders_with_payments(day)}                 # what we think
    for oid, p in gateway.items():
        o = ours.get(oid)
        if not o:                      alert("Captured payment with no order", oid)  # refund/repair
        elif o.status != "PAID":       await mark_paid(oid, p["id"])                 # missed webhook
    for oid, o in ours.items():
        if o.status == "PAID" and oid not in gateway: alert("Order PAID but not settled", oid)
```

### Workflow engines (orchestrated sagas) — Temporal (TypeScript)
```ts
export async function placeOrderWorkflow(input: OrderInput) {
  const orderId = await createOrder(input);
  try {
    await authorizePayment(orderId, input.total);
    await confirmWithRestaurant(orderId);
    await assignRider(orderId);
  } catch (err) {
    await voidPayment(orderId).catch(() => {});      // compensations
    await cancelOrder(orderId, String(err));
    throw err;
  }
}
// Temporal persists every step → survives crashes, retries activities, guarantees completion.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a distributed transaction and why is it hard?**
A1: An operation that must change state across multiple independent resources (databases, services, brokers, external APIs) atomically or consistently. It's hard because there's no shared transaction manager, components fail independently, networks make outcomes uncertain (timeouts), holding locks across systems kills availability, and external systems can't be rolled back. Solutions trade strict atomicity for coordination patterns: 2PC, sagas, outbox, TCC, idempotency and reconciliation.

**Q2: What is the dual-write problem and how does the outbox pattern solve it?**
A2: Writing to a database and then publishing to a message broker (or calling another service) as two separate operations. A crash between them leaves the systems inconsistent: a lost event or a ghost event. The outbox pattern writes the business change and an "event" row in the same local DB transaction, so they're atomic. A separate relay (polling or CDC like Debezium) reliably publishes outbox rows to the broker. Delivery is at-least-once, so consumers must be idempotent.

**Q3: 2PC vs Saga — when to use each?**
A3: 2PC gives atomic commit across participants that support prepare/commit (XA databases, some brokers). Use it within a tightly controlled environment, with short transactions and few participants. It blocks if the coordinator fails and hurts availability and latency. A saga breaks the operation into local transactions with compensating actions, giving eventual consistency, high availability, and support for long-running flows and external APIs. It's the standard for microservices, but requires designing compensations and handling intermediate states.

**Q4: What do you do when a call to an external payment API times out?**
A4: Treat the outcome as unknown, never as failure or success. Mark the order as payment pending or unknown. Retry the same request with the same idempotency key, or query the provider's status endpoint, or wait for its webhook. Use a delayed verification job. Only after confirmation, proceed or compensate. Reconcile daily with the provider's settlement reports.

**Q5: How do you design an order + payment + inventory flow across microservices?**
A5: The order service creates the order (PENDING) plus an outbox event in one transaction. Inventory reserves stock with a TTL (TCC Try). Payment authorizes (holds) the amount with an idempotency key. On success: confirm the reservation, capture the payment, mark the order CONFIRMED. On any failure or timeout: compensate (release stock, void or refund the payment, cancel the order). Orchestrate with a workflow engine or choreograph via events, with idempotent consumers, a DLQ, monitoring of stuck states and reconciliation jobs.

---

## 🔷 Trade-offs
✅ 2PC: true atomicity — ❌ blocking, latency, coordinator SPOF, limited participant support.
✅ Saga + outbox: available, scalable, works with external APIs — ❌ eventual consistency, compensation logic, intermediate states visible.
✅ Avoiding distribution (right boundaries / single DB): simplest — ❌ not always possible.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Distributed transaction | Atomic change across systems | कई systems में एक साथ बदलाव |
| Dual write | Writing two systems separately | दो जगह अलग-अलग लिखना |
| Transactional outbox | Event stored with data in same txn | डेटा के साथ event सेव करना |
| CDC | Change data capture from DB log | DB log से बदलाव पढ़ना |
| Compensation | Action that undoes a previous step | पिछला कदम उल्टा करना |
| TCC | Try-Confirm-Cancel reservations | पहले रोकना, फिर पक्का/रद्द |
| Reconciliation | Comparing records to fix mismatches | रिकॉर्ड मिलाकर गड़बड़ी ठीक करना |
| Uncertain outcome | Don't know if remote op succeeded | पता नहीं काम हुआ या नहीं |
| Workflow engine | Durable orchestrator (Temporal) | flow चलाने वाला टिकाऊ इंजन |

---

## ⚡ 3-Line Summary
**English:**
1. Distributed transactions update multiple independent systems; local ACID doesn't cover them.
2. Prefer good boundaries; otherwise use sagas (compensations) + transactional outbox + idempotent consumers; 2PC only in tight, controlled cases; TCC for reservations.
3. Treat timeouts as unknown, query/await confirmation, and always reconcile (especially money).

**Hindi:**
1. Distributed transaction = कई systems में एक साथ बदलाव; एक DB का transaction काफ़ी नहीं।
2. सही boundaries रखो; वरना Saga + Outbox + idempotent consumers; 2PC सिर्फ़ सीमित जगह; TCC reservations के लिए।
3. Timeout को "पता नहीं" मानो, status पूछो, और पैसे का reconciliation हमेशा करो।

---

## ➡️ Next Topic Suggestion
**69. Two Phase Commit (2PC)** — Next: the classic atomic commit protocol in detail: the prepare and commit phases, why it blocks, XA transactions, and where it's still used today.
