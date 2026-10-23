# 14. Microservices Architecture
# हिंदी में: Microservices — बड़े ऐप को छोटी-छोटी, स्वतंत्र services में बाँटना, जिनका अपना कोड, अपना deploy और अपना database होता है

---

## 🔵 Simple Definition (English)
**Microservices** is an architecture where an application is built as a set of **small, independent services**, each owning **one business capability** (orders, payments, delivery), with its **own codebase, own database, and independent deployment**. Services talk over the network (REST, gRPC, events).

## 🔵 सरल परिभाषा (Hindi)
Microservices में एक बड़ा ऐप कई छोटी services में बँटा होता है — हर service एक काम करती है (जैसे order, payment), उसका अपना DB होता है और वो अलग से deploy होती है।
Services आपस में network से (API या events) बात करती हैं।

---

## 🔴 Problem it Solves
When a monolith becomes very large (100+ developers, millions of lines):
- **Deploy bottleneck:** every team waits for one shared release train.
- **No fault isolation:** a bug in "recommendations" crashes "checkout".
- **Can't scale parts independently:** search needs 50 servers, profile needs 2, but you must scale everything.
- **One tech stack:** the ML team wants Python, the real-time team wants Go.
- **Ownership is unclear:** nobody fully understands the whole codebase.

Microservices let **each team own, build, deploy and scale its service independently**, which is organizational scaling first and technical scaling second.

## 🔴 यह क्यों बना? (Hindi)
जब monolith बहुत बड़ा हो जाता है तो सब टीमें एक deploy का इंतज़ार करती हैं, एक हिस्से का bug पूरा ऐप गिरा देता है, और सिर्फ़ एक हिस्से को स्केल नहीं कर सकते।
Microservices में हर टीम अपनी service की मालिक होती है — अलग deploy, अलग स्केल, अलग टेक्नोलॉजी।

---

## 🟢 How it Works — Step by Step

### Architecture

```
          📱 RN App      🌐 Next.js Web     🏪 Restaurant App
               └──────────────┼─────────────────┘
                              ▼
                     ┌─────────────────┐
                     │  API Gateway /  │   auth, routing, rate limit (Topic 93)
                     │  BFF            │
                     └────────┬────────┘
     ┌──────────────┬─────────┼─────────┬──────────────┬───────────────┐
     ▼              ▼         ▼         ▼              ▼               ▼
 ┌────────┐   ┌─────────┐ ┌────────┐ ┌─────────┐ ┌───────────┐ ┌────────────┐
 │ User   │   │ Catalog │ │ Order  │ │ Payment │ │ Delivery  │ │ Notification│
 │ Svc    │   │ Svc     │ │ Svc    │ │ Svc     │ │ Svc (Go)  │ │ Svc        │
 │ Node   │   │ Node    │ │ Node   │ │ Java    │ │           │ │ Python     │
 └───┬────┘   └────┬────┘ └───┬────┘ └────┬────┘ └─────┬─────┘ └─────┬──────┘
     ▼             ▼          ▼           ▼            ▼             ▲
  Postgres    Elastic+Mongo Postgres   Postgres     Redis+PostGIS    │
                              │                                      │
                              └──── "OrderPlaced" ──► Kafka ─────────┘
                                                        (events)
```

### Key principles

```
1. Single responsibility     → one business capability per service (bounded context)
2. Database per service      → no other service touches my tables (Topic 99)
3. Independent deployment    → deploy Order Svc 10×/day without touching Payment
4. Decentralized             → each team picks tools; own CI/CD; "you build it, you run it"
5. Smart endpoints, dumb pipes → logic in services, simple transport (HTTP/Kafka)
6. Design for failure        → timeouts, retries, circuit breakers (Topics 73–79)
7. Observability             → logs, metrics, traces across services (Topics 100–102)
```

### Communication styles

```
SYNCHRONOUS (request/response)          ASYNCHRONOUS (events/messages)
 Order ──REST/gRPC──► Payment           Order ──"OrderPlaced"──► Kafka ──► Notification
 "charge ₹450, wait for answer"                                     └──► Analytics
                                                                    └──► Delivery
 ✅ simple, immediate answer             ✅ loose coupling, resilient, scalable
 ❌ caller blocked; failures cascade     ❌ eventual consistency, harder debugging
 Use: need answer NOW (auth, price)     Use: side effects, fan-out, workflows
```

### The hard parts (what interviewers want to hear)

```
Problem                          Solution
──────────────────────────────   ─────────────────────────────────────────────
Transactions across services     Saga pattern (Topic 70), outbox pattern
Data duplication / joins          Events + local read copies, CQRS (Topic 71)
Finding services                  Service discovery / DNS / K8s (Topic 92)
Cascading failures                Timeouts, circuit breaker, bulkhead
Debugging a request over 8 svcs   Distributed tracing (OpenTelemetry, Jaeger)
Versioning service APIs           Backward-compatible contracts, consumer tests
Many deploy pipelines             Kubernetes, Helm, GitOps, templates
Network latency adds up           Fewer hops, batch calls, gRPC, caching
Security between services         mTLS / service mesh (Topic 94)
```

### Monolith vs Microservices

```
┌────────────────────┬─────────────────────┬──────────────────────────┐
│                    │ Monolith            │ Microservices            │
├────────────────────┼─────────────────────┼──────────────────────────┤
│ Codebase           │ One                 │ Many                     │
│ Deploy             │ All together        │ Independent              │
│ Database           │ Shared              │ Per service              │
│ Calls              │ In-process (ns)     │ Network (ms) — can fail  │
│ Transactions       │ ACID, easy          │ Sagas, eventual          │
│ Scaling            │ Whole app           │ Per service              │
│ Fault isolation    │ Low                 │ High (if designed well)  │
│ Ops complexity     │ Low                 │ High (K8s, tracing, ...) │
│ Team fit           │ 1–30 devs           │ Many autonomous teams    │
└────────────────────┴─────────────────────┴──────────────────────────┘
⚠️ Anti-pattern: "Distributed monolith" — services that must be deployed together and
share a DB. You get ALL the costs of microservices and NONE of the benefits.
```

## 🟢 कैसे काम करता है? (Hindi)
1. ऐप को business के हिसाब से बाँटते हैं — User, Order, Payment, Delivery services।
2. हर service का अपना DB होता है; कोई दूसरी service सीधे उसकी टेबल नहीं छूती।
3. Client की request API Gateway से होकर सही service तक जाती है।
4. तुरंत जवाब चाहिए तो REST/gRPC (sync); बाक़ी काम events (Kafka) से (async)।
5. मुश्किलें: कई services में transaction (Saga), debugging (tracing), और network failure (circuit breaker)।

---

## 🟡 Real World Example

**Netflix** — the pioneer. After a major database corruption in 2008, they moved from a monolith to **1000+ microservices** on AWS. They built Eureka (discovery), Hystrix (circuit breaker), Zuul (gateway) and Chaos Monkey (randomly killing services to test resilience).

**Swiggy** — split into services: listing/search, cart, order management, payments, delivery assignment (DE allocation), pricing, offers and notifications. Delivery assignment needs huge real-time computation during dinner peaks, so it scales independently from the menu service.

**Uber** — went to ~4,000 microservices. That created so much complexity that they introduced **DOMA (Domain-Oriented Microservice Architecture)**, grouping services into domains with gateways. Lesson: too many tiny services is also a problem.

**Segment** — moved from microservices *back* to a monolith (2018) because 140+ services with tiny teams caused more operational pain than benefit.

## 🟡 Real Example Hindi में
Netflix ने 2008 में बड़ी DB ख़राबी के बाद monolith छोड़कर 1000+ microservices बनाए और Chaos Monkey जैसे टूल बनाए।
Swiggy में डिलीवरी असाइनमेंट service रात के खाने के समय अलग से स्केल होती है। Uber के 4000 services इतने उलझ गए कि उन्हें फिर domains में समूह बनाना पड़ा — बहुत छोटी services भी मुसीबत हैं।

---

## 🟠 My Stack Example

### Order service (Node) calls Payment service (FastAPI) synchronously — with timeouts
```js
// order-service/src/clients/payment.ts
const PAYMENT_URL = process.env.PAYMENT_URL ?? 'http://payment-service:8000'; // Docker/K8s DNS

export async function chargePayment(orderId: string, amount: number, traceHeaders: Record<string,string>) {
  const ctrl = AbortSignal.timeout(3000);                    // never wait forever
  const res = await fetch(`${PAYMENT_URL}/v1/charges`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': orderId, ...traceHeaders },
    body: JSON.stringify({ orderId, amount }),
    signal: ctrl,
  });
  if (!res.ok) throw new PaymentError(res.status);
  return res.json();
}
```

### Order service publishes an event (async) — via Outbox pattern
```js
await db.tx(async (t) => {
  const order = await t.one('INSERT INTO orders(...) VALUES(...) RETURNING *', [...]);
  await t.none('INSERT INTO outbox(topic, payload) VALUES($1, $2)',
               ['order.placed', JSON.stringify({ orderId: order.id, userId })]);
});
// A relay process reads `outbox` and publishes to Kafka/SQS, then marks rows sent.
// → the DB write and the event can never get out of sync.
```

### Notification service (FastAPI/Python) consumes it
```python
from aiokafka import AIOKafkaConsumer

async def run():
    consumer = AIOKafkaConsumer("order.placed", bootstrap_servers="kafka:9092", group_id="notification-svc")
    await consumer.start()
    async for msg in consumer:
        event = json.loads(msg.value)
        if await already_processed(event["orderId"]):     # idempotent consumer
            continue
        await send_push(event["userId"], "Your order is placed 🎉")
        await mark_processed(event["orderId"])
```

### docker-compose for local dev
```yaml
services:
  gateway:        { build: ./gateway, ports: ["8080:8080"] }
  user-service:   { build: ./user-service,   environment: { DATABASE_URL: postgres://...@user-db/users } }
  order-service:  { build: ./order-service,  environment: { DATABASE_URL: postgres://...@order-db/orders, PAYMENT_URL: http://payment-service:8000 } }
  payment-service:{ build: ./payment-service }
  notification-service: { build: ./notification-service }
  user-db:  { image: postgres:16 }
  order-db: { image: postgres:16 }
  kafka:    { image: bitnami/kafka:3.7 }
  jaeger:   { image: jaegertracing/all-in-one, ports: ["16686:16686"] }   # tracing UI
```

### Tracing across services (OpenTelemetry — must have)
```js
// tracing.js — loaded first in every Node service
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
new NodeSDK({ serviceName: 'order-service', instrumentations: [getNodeAutoInstrumentations()] }).start();
// HTTP, Express, pg, Kafka calls are traced automatically; one trace id across all services.
```

### How the frontend sees it
Next.js and RN apps call **one** gateway/BFF (`api.myapp.com`). They never know there are 6 services behind it.

---

## ⚫ Interview Questions + Answers

**Q1: What are microservices? What are their benefits and drawbacks?**
A1: An architecture of small, independently deployable services, each owning one business capability and its own data, communicating over the network. Benefits: independent deploys and scaling, fault isolation, team autonomy and ownership, and freedom to choose technology per service. Drawbacks: distributed-system complexity (network failures, latency), no cross-service ACID transactions, harder testing and debugging, heavy ops and observability requirements, and data duplication.

**Q2: How do microservices communicate? When do you choose sync vs async?**
A2: Synchronously via REST/gRPC when the caller needs an immediate answer to continue (validate a user, get a price, authorize a payment). Asynchronously via a message broker (Kafka, RabbitMQ, SQS) for side effects, fan-out and long workflows (order placed → notify, assign delivery, analytics). Async reduces coupling and cascading failures but brings eventual consistency. A good design minimizes long synchronous call chains.

**Q3: How do you handle a transaction that spans multiple services (e.g., order + payment + inventory)?**
A3: Use the Saga pattern: a sequence of local transactions, each publishing an event. If a step fails, run compensating actions (refund the payment, release the inventory). It's either orchestrated, with a central coordinator such as an order workflow or Temporal, or choreographed, with services reacting to each other's events. Use the transactional outbox so a DB write and its event publish are atomic, and make consumers idempotent. Avoid 2PC across services: it's blocking and fragile.

**Q4: How do you decide service boundaries?**
A4: Use Domain-Driven Design. Identify bounded contexts (ordering, payments, catalog, delivery) where the language and data model are cohesive. A service should be ownable by one team, change mostly independently, and own its data. Signals of wrong boundaries are chatty synchronous calls between two services, frequent coordinated deploys, and shared tables. Start coarse and split later, rather than starting with nano-services.

**Q5: What is a "distributed monolith" and how do you avoid it?**
A5: A system split into services that are still tightly coupled: a shared database, lockstep deploys, long synchronous call chains, shared libraries containing business logic. It has the costs of microservices with none of the benefits. Avoid it with a database per service, backward-compatible API contracts and versioning, async events for cross-domain workflows, consumer-driven contract tests, and clear team ownership.

---

## 🔷 Trade-offs
✅ Advantages:
- Independent deploy, scale and tech choices per service.
- Fault isolation (with timeouts/circuit breakers).
- Team autonomy and clear ownership; smaller codebases are easier to understand.

❌ Disadvantages:
- Network calls = latency + partial failures; harder debugging.
- Data consistency is eventual; sagas/outbox add complexity.
- High ops overhead: K8s, CI/CD per service, tracing, service discovery, security.
- Premature adoption slows small teams down.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Microservice | Small independent service for one capability | एक काम की छोटी स्वतंत्र service |
| Bounded Context | Clear business domain boundary | business क्षेत्र की सीमा |
| Database per service | Each service owns its data | हर service का अपना DB |
| Sync communication | Wait for response (REST/gRPC) | जवाब का इंतज़ार |
| Async communication | Events/messages via broker | events से बात |
| Saga | Distributed transaction with compensations | कई services का transaction |
| Outbox pattern | Save event in DB with data, publish later | event को DB में सेव करके भेजना |
| Distributed monolith | Coupled services (anti-pattern) | जुड़ी हुई services (ग़लत तरीका) |
| Distributed tracing | Following a request across services | services के पार request ट्रैक करना |

---

## ⚡ 3-Line Summary
**English:**
1. Microservices = independent services per business capability, each with own DB and deploy.
2. Benefits are team autonomy, independent scaling and fault isolation; cost is distributed complexity.
3. Use sync calls sparingly, events for side effects, sagas for transactions, tracing for debugging — and don't start with microservices.

**Hindi:**
1. Microservices = हर business काम की अलग service, अपना DB, अपना deploy।
2. फ़ायदा: टीम की आज़ादी, अलग स्केल, fault isolation; नुकसान: distributed complexity।
3. Sync कॉल कम, side effects के लिए events, transaction के लिए Saga, debugging के लिए tracing — और शुरुआत monolith से करो।

---

## ➡️ Next Topic Suggestion
**15. Vertical Scaling** — Whether monolith or microservices, traffic grows. Next: the first and simplest way to handle more load, a bigger machine, and its limits.
