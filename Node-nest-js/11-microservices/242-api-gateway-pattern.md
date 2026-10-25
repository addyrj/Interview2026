# 242. API Gateway Pattern
# हिंदी में: API Gateway Pattern

---

## 🔵 Simple Definition (English)
An API Gateway is a single entry point that sits between external clients and internal microservices. It routes requests to the appropriate backend service, and commonly handles cross-cutting concerns like authentication, rate limiting, request/response transformation, and aggregation — so individual microservices don't each have to reimplement these.

## 🔵 सरल परिभाषा (Hindi)
API Gateway एक single entry point है जो external clients और internal microservices के बीच रहता है। यह requests को सही backend service पर route करता है, और commonly cross-cutting concerns जैसे authentication, rate limiting, request/response transformation, और aggregation handle करता है — ताकि individual microservices को यह सब अलग-अलग implement न करना पड़े।

---

## 🔴 Problem it Solves
Without a gateway, clients must know about and directly call each microservice individually — exposing internal architecture, forcing clients to make multiple round trips for a single screen's data, and requiring every single service to independently implement auth, rate limiting, logging, and CORS handling (massive duplication). The API Gateway solves this by centralizing these concerns in one place, presenting clients with a simple, unified API surface while hiding the internal complexity and service topology.

## 🔴 यह क्यों बना? (Hindi)
Gateway के बिना, clients को हर microservice को individually directly call करना और उसके बारे में जानना पड़ता है — internal architecture expose होता है, एक screen के data के लिए clients को multiple round trips करने पड़ते हैं, और हर service को independently auth, rate limiting, logging, CORS handling implement करना पड़ता है (massive duplication)। API Gateway इन concerns को एक जगह centralize करके यह solve करता है, clients को एक simple, unified API surface देता है जबकि internal complexity और service topology को hide करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → All external client requests go to the Gateway's single public URL, never directly to internal services.
Step 2 → The Gateway performs cross-cutting checks first: authentication (validate JWT), rate limiting, request logging.
Step 3 → Based on the request path/method, the Gateway routes (proxies) the request to the correct internal microservice.
Step 4 → For some endpoints, the Gateway may call MULTIPLE internal services and aggregate their responses into one combined response (API composition / Backend-for-Frontend pattern).
Step 5 → The Gateway can also transform requests/responses — e.g., converting REST to gRPC for internal calls, or reshaping a response for a specific client type (mobile vs web).
Step 6 → If an internal service is slow/down, the Gateway can apply circuit breaking/timeouts/fallbacks before the failure reaches the client.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → सभी external client requests Gateway के single public URL पर जाती हैं, कभी directly internal services पर नहीं।
Step 2 → Gateway पहले cross-cutting checks करता है: authentication (JWT validate करना), rate limiting, request logging।
Step 3 → Request path/method के आधार पर, Gateway request को सही internal microservice पर route (proxy) करता है।
Step 4 → कुछ endpoints के लिए, Gateway MULTIPLE internal services को call करके उनके responses को एक combined response में aggregate कर सकता है (API composition / Backend-for-Frontend pattern)।
Step 5 → Gateway requests/responses को transform भी कर सकता है — जैसे internal calls के लिए REST को gRPC में convert करना, या किसी specific client type (mobile vs web) के लिए response reshape करना।
Step 6 → अगर कोई internal service slow/down हो, Gateway client तक failure पहुंचने से पहले circuit breaking/timeouts/fallbacks apply कर सकता है।

---

## 🟡 Real World Example
**Swiggy's mobile app home screen:** Loading the home screen needs data from the Restaurant service, Offers service, User Preferences service, and Delivery-time Estimation service. Instead of the mobile app making 4 separate network calls (slow on mobile networks), it calls ONE Gateway endpoint (`GET /home`), and the Gateway internally fans out to all 4 services in parallel, aggregates the results, and returns a single combined JSON response — dramatically reducing mobile round trips and simplifying client code.

## 🟡 Real Example Hindi mein
**Swiggy के mobile app का home screen:** Home screen load करने के लिए Restaurant service, Offers service, User Preferences service, और Delivery-time Estimation service से data चाहिए। Mobile app को 4 अलग network calls करने के बजाय (mobile networks पर slow), वो सिर्फ एक Gateway endpoint (`GET /home`) call करता है, और Gateway internally उन सभी 4 services को parallel में call करके results aggregate करके एक single combined JSON response return करता है — mobile round trips को dramatically कम करता है और client code को simplify करता है।

---

## 💻 Code Example — Basic

```javascript
// api-gateway-basic.js — simple routing gateway using http-proxy-middleware
// Run: node api-gateway-basic.js (requires npm i express http-proxy-middleware)

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// Route requests based on URL path prefix to the appropriate internal service
app.use('/api/orders', createProxyMiddleware({
  target: 'http://localhost:4001',       // Order Service
  changeOrigin: true,
  pathRewrite: { '^/api/orders': '' },
}));

app.use('/api/payments', createProxyMiddleware({
  target: 'http://localhost:4002',       // Payment Service
  changeOrigin: true,
  pathRewrite: { '^/api/payments': '' },
}));

app.listen(8080, () => console.log('API Gateway listening on 8080'));
// Client calls gateway:8080/api/orders/5 → internally proxied to order-service:4001/5
```

## 💻 Code Example — Advanced

```javascript
// api-gateway-advanced.js — auth, rate limiting, and response aggregation (BFF pattern)
const express = require('express');
const axios = require('axios');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');

const app = express();
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';

// ─── CROSS-CUTTING CONCERN 1: Rate limiting applied ONCE for all routes ──────
app.use(rateLimit({ windowMs: 60 * 1000, max: 100 }));   // 100 requests/min per IP

// ─── CROSS-CUTTING CONCERN 2: Centralized authentication ────────────────────
function requireAuth(req, res, next) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Unauthorized' });
  }
}

const services = {
  restaurant: 'http://localhost:4010',
  offers: 'http://localhost:4011',
  preferences: 'http://localhost:4012',
};

// ─── API COMPOSITION: one gateway endpoint aggregates multiple services ──────
app.get('/api/home', requireAuth, async (req, res) => {
  try {
    // Fan out to multiple internal services IN PARALLEL — much faster than sequential calls
    const [restaurants, offers, preferences] = await Promise.all([
      axios.get(`${services.restaurant}/nearby`, { params: { userId: req.user.userId }, timeout: 3000 }),
      axios.get(`${services.offers}/active`, { timeout: 3000 }),
      axios.get(`${services.preferences}/${req.user.userId}`, { timeout: 3000 }),
    ]);

    // Combine into a single response tailored for the mobile home screen
    res.json({
      restaurants: restaurants.data,
      offers: offers.data,
      preferences: preferences.data,
    });
  } catch (err) {
    console.error('Home aggregation failed:', err.message);
    res.status(502).json({ error: 'Failed to load home screen data' });
  }
});

app.listen(8080, () => console.log('Advanced API Gateway on 8080'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const morgan = require('morgan');

const app = express();

// Centralized logging for ALL downstream services, in one place
app.use(morgan('combined'));

// Centralized CORS handling — individual services don't need their own CORS config
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  next();
});

app.use('/api/users', createProxyMiddleware({ target: 'http://user-service:4020', changeOrigin: true }));
app.use('/api/orders', createProxyMiddleware({ target: 'http://order-service:4021', changeOrigin: true }));

app.listen(8080, () => console.log('Express-based API Gateway on 8080'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting business logic inside the Gateway
✅ Correct: Keep the Gateway focused on routing + cross-cutting concerns; business logic belongs in the services

```javascript
// Wrong — gateway calculating order totals, applying discounts, etc.
app.post('/api/orders', (req, res) => { const total = calculateDiscount(req.body); /* ... */ });

// Right — gateway just routes; Order Service owns business logic
app.use('/api/orders', createProxyMiddleware({ target: 'http://order-service:4001' }));
```

❌ Mistake 2: Making the Gateway a single point of failure with no redundancy
✅ Correct: Run multiple Gateway instances behind a load balancer, just like any other service

```javascript
// Wrong: one Gateway instance — if it crashes, the ENTIRE system becomes unreachable
// Right: run N Gateway instances behind a load balancer, stateless, health-checked like any service
```

---

## 🧠 Tricky Interview Question

```javascript
// Gateway's /api/home endpoint calls 3 downstream services in parallel with Promise.all.
// One service times out after 3s. What happens to the OTHER two successful calls' data?
```
Answer: With `Promise.all`, if ANY of the promises rejects (e.g., the timed-out axios call throws), the WHOLE `Promise.all` immediately rejects — even though the other two calls may have succeeded, their results are discarded in the `catch` block, and the client gets a full failure (502) instead of partial data. To return partial/degraded results, you'd use `Promise.allSettled` instead, checking each result's status individually and returning whatever succeeded (perhaps with placeholders for the failed service) rather than failing the entire aggregated response.

---

## ⚫ Interview Questions + Answers

Q1: What are the main responsibilities of an API Gateway?
A1: Routing requests to the correct backend service, authentication/authorization enforcement, rate limiting/throttling, request/response logging and monitoring, SSL termination, CORS handling, and sometimes response aggregation (composing data from multiple services into one response) or protocol translation (REST at the edge, gRPC internally). It centralizes these cross-cutting concerns so individual microservices don't each reimplement them.

Q2: What is the Backend-for-Frontend (BFF) pattern, and how does it relate to API Gateways?
A2: BFF is a specialized variant of the Gateway pattern where you build a SEPARATE gateway/aggregation layer tailored to each type of client (e.g., one BFF for the mobile app, another for the web app), since different clients often need different shapes/amounts of data. A generic API Gateway serves all clients uniformly; a BFF customizes the aggregation and response shape per client type, trading some duplication for a better fit to each client's specific needs.

Q3: Why shouldn't business logic live in the API Gateway?
A3: Putting business logic in the Gateway re-couples it to specific services' domain rules, defeating the purpose of microservices' independent evolution — a change to order-pricing logic would require redeploying the shared Gateway instead of just the Order Service. It also makes the Gateway a bottleneck for ALL business logic changes across the whole system, increasing risk and blast radius of bugs. The Gateway should stay a thin routing/cross-cutting layer; actual domain logic belongs in the owning microservice.

Q4: How does an API Gateway improve mobile client performance specifically?
A4: Mobile networks have higher latency and are less reliable than typical server-to-server links. If a mobile client had to make 4-5 separate calls directly to different microservices for one screen, each round trip adds latency and failure risk. An API Gateway (or BFF) can make those 4-5 calls server-side (low-latency internal network) in parallel and return ONE aggregated response, so the mobile client only pays for ONE round trip over its slower connection.

Q5: What are the risks of making the API Gateway a single point of failure, and how do you mitigate them?
A5: If there's only one Gateway instance, its failure takes down access to the ENTIRE system even if all backend services are healthy. Mitigations: run multiple stateless Gateway instances behind a load balancer (just like any horizontally-scaled service), implement health checks so unhealthy instances are removed from rotation, add circuit breakers/timeouts for calls to backend services so one slow dependency doesn't hang the whole Gateway, and avoid putting any unique, non-replicated state in the Gateway itself.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have multiple microservices and want a single, consistent entry point for clients
- Cross-cutting concerns (auth, rate limiting, logging) would otherwise be duplicated across every service
- Clients (especially mobile) benefit from aggregated responses instead of multiple round trips

❌ Avoid when:
- You have a single monolithic service — there's nothing to "gateway" to yet
- The added network hop and operational complexity isn't justified for a very small number of simple services

---

## 📊 Visual Diagram
```
                        ┌───────────────────┐
     Client (Mobile)──▶│    API Gateway      │
                        │ (auth, rate-limit,  │
                        │  logging, routing)  │
                        └─────────┬──────────┘
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
   Restaurant Service        Offers Service          Preferences Service
   (internal network, fast, no direct client exposure)

Gateway aggregates all 3 responses into ONE response for the client.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| API Gateway | Single entry point routing to services | Services तक route करने वाला single entry point |
| API composition | Combining multiple service responses into one | कई service responses को एक में combine करना |
| BFF | Backend-for-Frontend, client-specific gateway | Client-specific gateway |
| Cross-cutting concern | Shared functionality needed by many services | बहुत services को चाहिए होने वाला shared functionality |
| Proxy routing | Forwarding requests to the right backend | Requests को सही backend पर forward करना |

---

## ⚡ 3-Line Summary
**English:**
1. An API Gateway is the single entry point for clients, routing requests to internal microservices.
2. It centralizes cross-cutting concerns (auth, rate limiting, logging) and can aggregate multiple service calls into one response.
3. Keep business logic out of the Gateway, and run multiple Gateway instances to avoid a single point of failure.

**Hindi:**
1. API Gateway clients के लिए single entry point है, requests को internal microservices पर route करता है।
2. यह cross-cutting concerns (auth, rate limiting, logging) centralize करता है और कई service calls को एक response में aggregate कर सकता है।
3. Business logic को Gateway से बाहर रखो, और single point of failure से बचने के लिए multiple Gateway instances चलाओ।

---

## ➡️ Next Topic
**243. Circuit Breaker in Node** — Protecting the Gateway and services from cascading failures when a dependency is down.
