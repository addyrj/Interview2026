# 231. Microservices with Node.js
# हिंदी में: Node.js के साथ Microservices

---

## 🔵 Simple Definition (English)
Microservices architecture splits a large application into small, independently deployable services, each owning a specific business capability (orders, payments, inventory) and communicating over the network (HTTP, gRPC, message queues). Node.js is popular for microservices because it's lightweight, starts fast, and handles I/O-heavy inter-service communication efficiently.

## 🔵 सरल परिभाषा (Hindi)
Microservices architecture एक बड़े application को small, independently deployable services में बांटती है, हर एक specific business capability (orders, payments, inventory) को own करती है और network (HTTP, gRPC, message queues) पर communicate करती है। Node.js microservices के लिए popular है क्योंकि यह lightweight है, fast start होता है, और I/O-heavy inter-service communication efficiently handle करता है।

---

## 🔴 Problem it Solves
A monolithic app (everything in one codebase/process) becomes hard to scale, deploy, and maintain as it grows: one team's bug can break the whole app, one slow feature blocks deployment of everything else, and scaling means scaling the ENTIRE app even if only one part needs it (e.g., scaling the whole monolith for a busy "search" feature wastes resources on unrelated code). Microservices solve this by letting each service scale, deploy, and fail independently — a crash in the "recommendation service" doesn't take down "checkout."

## 🔴 यह क्यों बना? (Hindi)
Monolithic app (सब कुछ एक codebase/process में) बढ़ने के साथ scale, deploy, maintain करना मुश्किल हो जाता है: एक team का bug पूरे app को तोड़ सकता है, एक slow feature बाकी सबकी deployment block कर देता है, और scaling का मतलब पूरे app को scale करना है भले ही सिर्फ एक हिस्से को जरूरत हो (जैसे busy "search" feature के लिए पूरा monolith scale करना resources waste करता है)। Microservices हर service को independently scale, deploy, fail होने देकर यह solve करते हैं — "recommendation service" crash होने से "checkout" down नहीं होता।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify bounded contexts/business capabilities (Order Service, Payment Service, Inventory Service, Notification Service).
Step 2 → Each becomes its own Node.js app with its own codebase, database (or schema), and deployment pipeline.
Step 3 → Services communicate via well-defined contracts — synchronous (REST/gRPC) for request-response, or asynchronous (message queues/events) for decoupled workflows.
Step 4 → An API Gateway sits in front, routing external client requests to the right internal service.
Step 5 → Each service is deployed, scaled, and monitored independently (its own Docker container/Kubernetes deployment).
Step 6 → Cross-cutting concerns (auth, logging, tracing) are handled via shared libraries or sidecars, not duplicated business logic.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Bounded contexts/business capabilities identify करो (Order Service, Payment Service, Inventory Service, Notification Service)।
Step 2 → हर एक अपना Node.js app बनता है अपने codebase, database (या schema), और deployment pipeline के साथ।
Step 3 → Services well-defined contracts से communicate करती हैं — synchronous (REST/gRPC) request-response के लिए, या asynchronous (message queues/events) decoupled workflows के लिए।
Step 4 → एक API Gateway आगे रहता है, external client requests को सही internal service पर route करता है।
Step 5 → हर service independently deploy, scale, monitor होती है (अपना Docker container/Kubernetes deployment)।
Step 6 → Cross-cutting concerns (auth, logging, tracing) shared libraries या sidecars से handle होते हैं, business logic duplicate नहीं होता।

---

## 🟡 Real World Example
**Zomato's architecture:** Instead of one giant app, Zomato runs separate services — a Restaurant Discovery service, an Order Management service, a Delivery Tracking service, a Payments service, and a Notifications service — each in Node.js (or polyglot). When Delivery Tracking needs to scale heavily during dinner rush, it scales independently without touching Payments. If Notifications service has a bug and crashes, users can still place orders — just notifications are delayed, not the whole app going down.

## 🟡 Real Example Hindi mein
**Zomato का architecture:** एक giant app के बजाय, Zomato अलग-अलग services चलाता है — Restaurant Discovery, Order Management, Delivery Tracking, Payments, और Notifications — हर एक Node.js (या polyglot) में। Dinner rush में Delivery Tracking को heavily scale करना पड़े तो वो independently scale होती है, Payments को छुए बिना। अगर Notifications service में bug आकर crash हो जाए, तो users फिर भी order place कर सकते हैं — सिर्फ notifications delay होते हैं, पूरा app down नहीं होता।

---

## 💻 Code Example — Basic

```javascript
// order-service.js — a minimal standalone microservice
// Run: node order-service.js
// Owns ONLY order-related logic and its own in-memory "DB" (replace with real DB)

const express = require('express');
const app = express();
app.use(express.json());

const orders = [];   // in real life: this service's own database

// This service's ONLY job: manage orders. It does NOT know about payments internals.
app.post('/orders', (req, res) => {
  const order = { id: orders.length + 1, items: req.body.items, status: 'CREATED' };
  orders.push(order);
  res.status(201).json(order);
});

app.get('/orders/:id', (req, res) => {
  const order = orders.find(o => o.id === Number(req.params.id));
  if (!order) return res.status(404).json({ error: 'Order not found' });
  res.json(order);
});

app.listen(4001, () => console.log('Order Service running on port 4001'));
```

## 💻 Code Example — Advanced

```javascript
// order-service-with-payment-call.js
// Shows a service calling ANOTHER microservice over HTTP (synchronous inter-service call)

const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

const PAYMENT_SERVICE_URL = process.env.PAYMENT_SERVICE_URL || 'http://localhost:4002';
const orders = new Map();

app.post('/orders', async (req, res) => {
  const orderId = `order_${Date.now()}`;
  const order = { id: orderId, items: req.body.items, amount: req.body.amount, status: 'PENDING' };
  orders.set(orderId, order);

  try {
    // Call Payment Service — network boundary, must handle failure/timeout
    const paymentRes = await axios.post(
      `${PAYMENT_SERVICE_URL}/payments`,
      { orderId, amount: order.amount },
      { timeout: 5000 }   // never call another service without a timeout
    );

    order.status = paymentRes.data.success ? 'PAID' : 'PAYMENT_FAILED';
  } catch (err) {
    // Network failure, timeout, or Payment Service down — handle gracefully
    console.error('Payment Service call failed:', err.message);
    order.status = 'PAYMENT_PENDING';   // will be retried async via a queue, not blocked here
  }

  orders.set(orderId, order);
  res.status(201).json(order);
});

app.get('/orders/:id', (req, res) => {
  const order = orders.get(req.params.id);
  if (!order) return res.status(404).json({ error: 'Order not found' });
  res.json(order);
});

app.listen(4001, () => console.log('Order Service (with Payment integration) on 4001'));
```

---

## 🟠 Express.js Integration

```javascript
// api-gateway.js — a lightweight API Gateway routing to microservices
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

// External clients only talk to THIS gateway — never directly to internal services
app.use('/api/orders', createProxyMiddleware({
  target: 'http://order-service:4001',
  changeOrigin: true,
  pathRewrite: { '^/api/orders': '/orders' },
}));

app.use('/api/payments', createProxyMiddleware({
  target: 'http://payment-service:4002',
  changeOrigin: true,
  pathRewrite: { '^/api/payments': '/payments' },
}));

app.use('/api/inventory', createProxyMiddleware({
  target: 'http://inventory-service:4003',
  changeOrigin: true,
  pathRewrite: { '^/api/inventory': '/inventory' },
}));

app.listen(8080, () => console.log('API Gateway listening on 8080'));
// Clients call gateway:8080/api/orders — gateway internally routes to order-service:4001
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sharing a single database across multiple "microservices"
✅ Correct: Each service owns its own data; cross-service data access goes through APIs/events, not shared tables

```javascript
// Wrong — Order Service directly queries Payment Service's DB tables
const payment = await db.query('SELECT * FROM payments_table WHERE order_id = ?', [orderId]);

// Right — Order Service calls Payment Service's API
const payment = await axios.get(`${PAYMENT_SERVICE_URL}/payments/by-order/${orderId}`);
```

❌ Mistake 2: Synchronous call chains with no timeout/circuit breaker
✅ Correct: Always set timeouts and consider async messaging for non-critical-path operations

```javascript
// Wrong
await axios.post(url, data);   // no timeout — can hang forever if target is down

// Right
await axios.post(url, data, { timeout: 3000 });   // fail fast, handle gracefully
```

---

## 🧠 Tricky Interview Question

```javascript
// Order Service calls Payment Service, which calls Fraud-Check Service,
// which calls a third-party API. Each hop has a 5s timeout.
// What's the WORST-case total time the client waits for a response?
```
Answer: In naive synchronous chaining, worst case is roughly the SUM of all hop timeouts (5s + 5s + 5s = 15s) if each layer waits for the one below it to time out before failing. This "cascading timeout" problem is a classic microservices pitfall — it's why real systems use circuit breakers (fail fast once a dependency is known to be down), aggressive but sane per-hop timeouts, and async/event-driven patterns for anything not strictly required in the critical path, so the client isn't stuck waiting on deep synchronous chains.

---

## ⚫ Interview Questions + Answers

Q1: What are the main benefits of microservices over a monolith?
A1: Independent deployment (ship one service without redeploying everything), independent scaling (scale only the bottleneck service), fault isolation (one service crashing doesn't take down others if designed well), technology flexibility (each service can use different languages/DBs if needed), and smaller codebases per team (easier to understand and onboard). The trade-off is added operational complexity: network calls, distributed data consistency, and more infrastructure to manage.

Q2: Why is Node.js a good fit for many microservices?
A2: Node.js has fast startup time (good for scaling up/down quickly and for serverless-style deployments), low memory footprint per instance, and excellent handling of I/O-bound workloads (which most microservices are — they mostly wait on network calls to DBs/other services, not heavy CPU computation). Its huge npm ecosystem also makes it quick to build HTTP/gRPC servers, message queue consumers, etc.

Q3: How should data be managed across microservices — shared DB or separate DBs?
A3: Best practice: each microservice owns its own database/schema (database-per-service pattern), and other services access its data only through its API or via events, never direct DB access. Shared databases create tight coupling (schema changes in one service break others) and defeat the purpose of independent deployability. Cross-service data needs — e.g., showing order + payment info together — are handled via API composition, data duplication (eventual consistency via events), or a dedicated read-model/BFF layer.

Q4: What's the difference between synchronous and asynchronous communication between microservices, and when would you use each?
A4: Synchronous (REST/gRPC) = caller waits for an immediate response; good for request-response flows where the client needs data right away (e.g., "get order details"). Asynchronous (message queues like RabbitMQ/Kafka) = caller fires an event/message and continues, with the consumer processing it independently; good for workflows that don't need an immediate result (e.g., "send a notification after order placed," "update analytics"). Overusing synchronous calls creates tight coupling and cascading failures; overusing async can make debugging and consistency harder — a real system uses a mix.

Q5: What is an API Gateway and why is it important in microservices?
A5: An API Gateway is a single entry point that external clients talk to; it routes requests to the appropriate internal microservice, and commonly handles cross-cutting concerns like authentication, rate limiting, request logging, and response aggregation. It hides internal service topology from clients (clients don't need to know service hostnames/ports), simplifies client-side code (one base URL), and provides a central place to enforce policies without duplicating them in every service.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The team/organization is large enough that independent deployment per team adds real value
- Different parts of the system have very different scaling needs
- Fault isolation between business domains is critical (e.g., payments shouldn't go down because of a bug in recommendations)

❌ Avoid when:
- The team is small and a monolith is simpler to develop, test, and deploy (microservices add real operational overhead)
- The product/domain boundaries aren't well understood yet (premature microservices lead to the wrong splits and painful refactors — "distributed monolith")
- You don't yet have the DevOps maturity (CI/CD, monitoring, service discovery) to operate many independent services reliably

---

## 📊 Visual Diagram
```
                     ┌─────────────────┐
      Client   ────▶ │   API Gateway    │
                     └────────┬─────────┘
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Order Svc    │◀──▶│ Payment Svc  │    │ Inventory Svc│
   │ (own DB)     │    │ (own DB)     │    │ (own DB)     │
   └──────┬───────┘    └─────────────┘    └─────────────┘
          │  (async event)
          ▼
   ┌─────────────┐
   │ Message Queue│  ──▶  Notification Svc, Analytics Svc, etc.
   └─────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Microservice | Independently deployable business-capability service | Independently deployable business service |
| Bounded context | A clear boundary around a business domain | Business domain के around clear boundary |
| API Gateway | Single entry point routing to services | Services तक route करने वाला single entry point |
| Database-per-service | Each service owns its own data store | हर service अपना data store own करे |
| Distributed monolith | Microservices that are too tightly coupled | बहुत tightly coupled microservices |

---

## ⚡ 3-Line Summary
**English:**
1. Microservices split an app into independently deployable services, each owning a business capability and its own data.
2. Node.js suits microservices well due to fast startup, low memory, and strong I/O-bound performance.
3. Key risks are shared databases, synchronous call chains without timeouts, and premature splitting without clear bounded contexts.

**Hindi:**
1. Microservices app को independently deployable services में बांटते हैं, हर एक अपनी business capability और data own करता है।
2. Node.js fast startup, low memory, और strong I/O-bound performance की वजह से microservices के लिए सही है।
3. Main risks: shared databases, timeout-less synchronous call chains, और clear bounded contexts के बिना premature splitting।

---

## ➡️ Next Topic
**232. Service Communication (REST/gRPC)** — Detailed comparison of synchronous communication protocols between microservices.
