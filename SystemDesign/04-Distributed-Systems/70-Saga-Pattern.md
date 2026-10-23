# 70. Saga Pattern
# हिंदी में: Saga — एक बड़े काम को कई छोटे local transactions में बाँटना; किसी कदम के फ़ेल होने पर पिछले कदमों को उल्टे (compensating) कामों से वापस करना

---

## 🔵 Simple Definition (English)
A **Saga** implements a business transaction that spans multiple services as a **sequence of local transactions**. Each step updates **its own service's database** and triggers the next step. If a step fails, the saga runs **compensating transactions** to **semantically undo** the previous completed steps (refund the payment, release the stock, cancel the order).
Two styles: **Choreography** (services react to each other's events) and **Orchestration** (a central orchestrator tells each service what to do).

## 🔵 सरल परिभाषा (Hindi)
Saga में बड़ा काम (जैसे ऑर्डर) कई छोटे कदमों में बँटता है — हर service अपना local transaction करती है और अगले को आगे बढ़ाती है।
कोई कदम फ़ेल हुआ तो पहले हो चुके कदमों को उल्टा करने वाले काम (compensation) चलते हैं — जैसे refund, stock वापस, ऑर्डर cancel।

---

## 🔴 Problem it Solves
In microservices, each service owns its database (Topic 99). 2PC across services is blocking, slow and often impossible (external APIs can't participate). But business flows still need consistency:
```
Order created → Payment charged → Restaurant confirms → Rider assigned
```
If the restaurant rejects the order after payment, the money must be returned. A saga gives **reliable, eventually consistent multi-service workflows** without distributed locks, and it supports **long-running** processes (minutes, hours, days).

## 🔴 यह क्यों बना? (Hindi)
Microservices में हर service का अपना DB है; उनके बीच 2PC धीमा और अक्सर नामुमकिन है (Razorpay जैसी बाहरी API उसमें शामिल नहीं हो सकती)।
Saga बिना distributed locks के कई services वाला काम भरोसेमंद बनाता है — और लंबे चलने वाले flows (घंटों/दिनों) के लिए भी काम करता है।

---

## 🟢 How it Works — Step by Step

### Steps and compensations (food order)

```
Step  Service        Local transaction (Ti)            Compensation (Ci)
────  ─────────────  ────────────────────────────────  ──────────────────────────────
T1    Order          create order (PENDING)            C1: cancel order
T2    Payment        authorize/charge ₹450             C2: refund / void
T3    Restaurant     accept order, reserve items       C3: cancel at restaurant
T4    Delivery       assign rider                      (last step — "pivot"; after this
                                                        we move forward only)
Success: T1 → T2 → T3 → T4 → order CONFIRMED
Failure at T3: T1 → T2 → T3 ✗ → C2 (refund) → C1 (cancel order) → order CANCELLED
```

### Style 1 — Choreography (event-driven, no central brain)

```
 Order Svc ──"OrderCreated"──► Kafka ──► Payment Svc
                                           │ charges
 Restaurant Svc ◄── "PaymentCompleted" ────┘
     │ rejects!
     └──"RestaurantRejected"──► Payment Svc → refund → "PaymentRefunded" ──► Order Svc → CANCELLED

✅ loose coupling, simple for 2–4 steps, no SPOF
❌ flow is implicit (hard to see/debug), cyclic dependencies, hard to add steps, "event spaghetti"
```

### Style 2 — Orchestration (central coordinator) ⭐ for complex flows

```
                ┌───────────────────────────┐
                │   Order Saga Orchestrator │  (state machine, persisted)
                └──┬──────┬──────┬──────┬───┘
     1.create order│      │      │      │
                   ▼      │      │      │
              Order Svc   │2.charge     │
                          ▼      │      │
                     Payment Svc │3.confirm
                                 ▼      │
                         Restaurant Svc │4.assign
                                        ▼
                                  Delivery Svc
 On failure → orchestrator calls compensations in reverse order.
✅ explicit flow, easy to monitor/change, central timeouts & retries
❌ orchestrator is extra component; risk of putting too much logic in it
Tools: Temporal, AWS Step Functions, Camunda/Zeebe, Netflix Conductor, Cadence
```

### Saga state machine (persisted)

```
PENDING → PAYMENT_AUTHORIZED → RESTAURANT_ACCEPTED → RIDER_ASSIGNED → CONFIRMED
     ↘ PAYMENT_FAILED → CANCELLED
                   ↘ RESTAURANT_REJECTED → REFUNDING → REFUNDED → CANCELLED
Store current state + step history in DB → resume after crashes.
```

### Rules for correct sagas

```
1. Every step is a LOCAL ACID transaction + publishes its event via OUTBOX (no dual writes)
2. Every step & compensation is IDEMPOTENT (messages may be redelivered)
3. Compensations are SEMANTIC undo, not DB rollback (refund ≠ "un-charge"; email sent can't be unsent
   → send "order cancelled" email)
4. Compensations must eventually SUCCEED → retry with backoff; alert humans if stuck
5. Order steps wisely: put steps that may fail EARLY, irreversible steps (send email, ship) LATE
   ("pivot transaction" = point of no return)
6. Handle lack of isolation: other requests can see intermediate states (order PENDING)
   → semantic locks (status flags), "pending" UI, commutative updates, re-read values
7. Timeouts for each step (restaurant doesn't respond in 5 min → compensate)
```

### Isolation anomalies & countermeasures
```
Sagas are ACD (no I). Dirty reads possible: someone sees "payment done" then it's refunded.
Countermeasures: semantic lock (order.status = PENDING blocks other edits), versioning,
reread-before-update, pessimistic view (show "Processing" until CONFIRMED).
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर कदम (order बनाना, payment, restaurant, rider) अपनी service में local transaction है, और हर कदम का एक उल्टा काम (compensation) तय है।
2. Choreography: services events से एक-दूसरे को जगाती हैं — आसान, पर बड़ा flow समझना मुश्किल।
3. Orchestration: एक orchestrator (Temporal/Step Functions) हर कदम बुलाता है, state सेव करता है, और फ़ेल होने पर उल्टे क्रम में compensations चलाता है।
4. हर कदम idempotent हो, events outbox से जाएँ, और compensation (refund) तब तक retry हो जब तक सफल न हो।
5. Saga में isolation नहीं होता — बीच की स्थिति (PENDING) दिखती है, इसलिए UI में "Processing…" दिखाओ और जो कदम फ़ेल हो सकते हैं उन्हें पहले रखो।

---

## 🟡 Real World Example

**Uber (Cadence → Temporal)** — trip and payment workflows run as orchestrated sagas in Cadence, which Uber built and open-sourced. The Temporal founders came from it, and companies like Netflix, Stripe, Coinbase, Snap and Swiggy-scale startups use Temporal for durable workflows.

**Netflix Conductor** — an open-source orchestration engine Netflix built for content-processing workflows (encode, QC, package, publish) with compensations and retries.

**Airline / travel bookings (MakeMyTrip, Booking.com)** — book flight, then hotel, then car. If the hotel fails, cancel the flight (refund, possibly with fees). These are long-running sagas, and some compensations involve humans.

**Swiggy Instamart / Zepto** — order placement reserves inventory at the dark store, captures payment, and assigns a picker and rider. Out-of-stock found during picking triggers a partial refund compensation.

## 🟡 Real Example Hindi में
Uber ने trip और payment के flows के लिए Cadence बनाया (अब Temporal) — Netflix, Stripe, Coinbase भी इसे इस्तेमाल करते हैं।
MakeMyTrip में flight → hotel → cab; hotel फ़ेल हुआ तो flight cancel/refund — यह लंबा saga है। Zepto/Instamart में packing के समय सामान न मिले तो उतने का refund — compensation।

---

## 🟠 My Stack Example

### Orchestrated saga with Temporal (TypeScript)
```ts
// workflows.ts
import { proxyActivities } from '@temporalio/workflow';
const act = proxyActivities<typeof import('./activities')>({
  startToCloseTimeout: '30s',
  retry: { maximumAttempts: 5, initialInterval: '1s', backoffCoefficient: 2 },
});

export async function orderSaga(input: { orderId: string; userId: string; total: number }) {
  const compensations: Array<() => Promise<void>> = [];
  try {
    await act.createOrder(input);                 compensations.unshift(() => act.cancelOrder(input.orderId));
    const pay = await act.chargePayment(input);   compensations.unshift(() => act.refundPayment(pay.paymentId));
    await act.confirmRestaurant(input.orderId);   compensations.unshift(() => act.cancelAtRestaurant(input.orderId));
    await act.assignRider(input.orderId);          // pivot: after this, only forward
    await act.markConfirmed(input.orderId);
  } catch (err) {
    for (const undo of compensations) await undo();   // Temporal retries each until success
    await act.notifyUser(input.userId, 'Your order was cancelled and refunded.');
    throw err;
  }
}

// activities.ts — each is idempotent (uses orderId as idempotency key)
export async function chargePayment({ orderId, total }) {
  return payments.charge({ amount: total, idempotencyKey: `charge-${orderId}` });
}
export async function refundPayment(paymentId: string) {
  return payments.refund({ paymentId, idempotencyKey: `refund-${paymentId}` });
}
```
Temporal persists workflow state, so if the worker crashes mid-saga, it resumes exactly where it stopped.

### Choreographed saga with Kafka (Node) — payment service
```js
consumer.run({
  eachMessage: async ({ topic, message }) => {
    const evt = JSON.parse(message.value);
    if (await alreadyProcessed(evt.eventId)) return;             // idempotent consumer

    if (topic === 'order.created') {
      await withTx(async (tx) => {
        const ok = await chargeWallet(tx, evt.userId, evt.total, `charge-${evt.orderId}`);
        await tx.query("INSERT INTO outbox(event_type, payload) VALUES ($1, $2)",
          [ok ? 'payment.completed' : 'payment.failed', { orderId: evt.orderId }]);
        await markProcessed(tx, evt.eventId);
      });
    }
    if (topic === 'restaurant.rejected') {                        // compensation trigger
      await withTx(async (tx) => {
        await refundWallet(tx, evt.orderId, `refund-${evt.orderId}`);
        await tx.query("INSERT INTO outbox(event_type, payload) VALUES ('payment.refunded', $1)", [{ orderId: evt.orderId }]);
        await markProcessed(tx, evt.eventId);
      });
    }
  },
});
```

### Saga state table (if you build your own orchestrator)
```sql
CREATE TABLE order_sagas (
  order_id     BIGINT PRIMARY KEY,
  state        TEXT NOT NULL,              -- PENDING, PAYMENT_DONE, RESTAURANT_OK, COMPENSATING, DONE, CANCELLED
  step_history JSONB NOT NULL DEFAULT '[]',
  deadline_at  TIMESTAMPTZ,                -- timeout for current step
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- watchdog job: SELECT * FROM order_sagas WHERE deadline_at < now() AND state NOT IN ('DONE','CANCELLED')
--               → retry step or start compensation
```

### AWS Step Functions (serverless orchestration)
```
States: CreateOrder → ChargePayment (Catch → RefundAndCancel) → ConfirmRestaurant (Catch → Refund → Cancel) → Done
Each state calls a Lambda/ECS task; Retry blocks with backoff; execution history visible in console.
```

### Mobile UX for sagas
```
After "Place order": show "Order placed — waiting for restaurant…" (PENDING)
Push/WebSocket updates as saga progresses → "Confirmed ✓" or "Restaurant couldn't accept. ₹450 refunded."
Never show "Confirmed" until the saga reaches CONFIRMED.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the Saga pattern?**
A1: A way to maintain data consistency across services without distributed transactions. A business transaction becomes a sequence of local transactions, each in one service, publishing events or replies that trigger the next step. If a step fails, previously completed steps are undone by compensating transactions (business-level reversals like refunds or cancellations). The result is eventual consistency, with high availability and support for long-running processes.

**Q2: Choreography vs orchestration — when to use which?**
A2: Choreography: services publish and subscribe to events with no central controller. It's loosely coupled and simple for a few steps, but the overall flow is implicit, harder to understand, debug and change, and risks cyclic dependencies. Orchestration: a central orchestrator (a state machine or a workflow engine like Temporal or Step Functions) commands each step and handles failures and compensations, giving explicit visibility, timeouts and easier evolution, at the cost of an extra component. I use orchestration for complex, business-critical flows like orders and payments.

**Q3: How do you guarantee a saga doesn't get stuck or lose steps?**
A3: Persist saga state durably (a workflow engine or a saga table). Publish step events via the transactional outbox. Make all steps and compensations idempotent and retry them with backoff. Set per-step timeouts with a watchdog that retries or triggers compensation. Alert on sagas stuck beyond SLAs, use DLQs for poison messages, and run reconciliation jobs. Workflow engines like Temporal provide most of this out of the box.

**Q4: What isolation problems do sagas have and how do you handle them?**
A4: Sagas lack isolation: intermediate states are visible and other transactions can interleave, giving dirty reads (seeing a payment that later gets refunded), lost updates, or decisions made on soon-to-be-compensated data. Countermeasures: semantic locks (status fields like PENDING that block conflicting actions), commutative updates, versioning or rereading before updating, ordering steps so risky ones come first, and UI that shows pending states until completion.

**Q5: Design compensations for: create order → charge card → reserve inventory → send confirmation email.**
A5: Reorder so the email is last (it can't be undone) and inventory reservation happens before charging if stock is the likely failure. Compensations: cancel order (mark CANCELLED); refund or void payment (an idempotent refund using the payment ID); release the inventory reservation (or let it expire via TTL). The email has no compensation, so send it only after the pivot step succeeds, or send a "cancelled" email if a later failure happens. Each compensation retries until success, with alerts if it fails.

---

## 🔷 Trade-offs
✅ Advantages:
- No distributed locks; high availability; works across services and external APIs; supports long-running flows.

❌ Disadvantages:
- Eventual consistency, no isolation (intermediate states visible).
- Must design and test compensations; some actions can't be truly undone.
- Debugging distributed flows is harder (needs tracing/visibility).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Saga | Sequence of local txns + compensations | छोटे transactions की कड़ी |
| Compensating transaction | Semantic undo of a step | कदम को उल्टा करने वाला काम |
| Choreography | Services react to events | events से आपसी तालमेल |
| Orchestration | Central coordinator drives steps | केंद्रीय संचालक |
| Pivot transaction | Point of no return | वापसी न होने वाला कदम |
| Semantic lock | Status flag preventing conflicts | स्थिति वाला ताला |
| Workflow engine | Durable saga runner (Temporal) | टिकाऊ flow इंजन |
| Idempotent step | Safe to retry | दोबारा चलाने पर सुरक्षित |
| Outbox | Reliable event publishing | भरोसेमंद event भेजना |

---

## ⚡ 3-Line Summary
**English:**
1. Saga = chain of local transactions across services; on failure, run compensations (refund, release, cancel) in reverse.
2. Choreography (events) for simple flows, orchestration (Temporal/Step Functions) for complex ones; use outbox + idempotent steps + timeouts.
3. Sagas give eventual consistency without isolation — order risky steps first, irreversible ones last, show pending states.

**Hindi:**
1. Saga = services में local transactions की कड़ी; फ़ेल होने पर उल्टे क्रम में compensations।
2. छोटे flow के लिए events (choreography), बड़े के लिए orchestrator; outbox, idempotency, timeouts ज़रूरी।
3. Isolation नहीं — जोखिम वाले कदम पहले, न उलटे जा सकने वाले आख़िर में, UI में pending दिखाओ।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Saga Pattern](https://www.youtube.com/results?search_query=saga+pattern+microservices+bytebytego) | Choreography vs orchestration visual walkthrough |
| 📺 YouTube | [Tech Dummies — Distributed Transactions](https://www.youtube.com/results?search_query=saga+pattern+distributed+transactions+microservices) | End-to-end e-commerce saga example |
| 📝 Article | [Martin Fowler — Saga pattern](https://martinfowler.com/articles/patterns-of-distributed-systems/saga.html) | Original pattern description with compensating transactions |
| 📝 Article | [microservices.io — Saga pattern](https://microservices.io/patterns/data/saga.html) | Chris Richardson's canonical explanation |
| 🐙 GitHub | [eventuate-tram-sagas](https://github.com/eventuate-tram/eventuate-tram-sagas) | Java library for Saga orchestration — see real implementation |

---

## ➡️ Next Topic Suggestion
**71. CQRS Pattern** — Sagas handle writes across services. Next: CQRS, separating the write model from read models so each can be optimized and scaled independently.
