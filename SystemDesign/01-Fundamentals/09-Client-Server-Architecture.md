# 09. Client-Server Architecture
# हिंदी में: क्लाइंट-सर्वर आर्किटेक्चर — क्लाइंट (ऐप/ब्राउज़र) सेवा माँगता है और सर्वर उसे पूरा करता है

---

## 🔵 Simple Definition (English)
In **client-server architecture**, the **client** (browser, mobile app, another service) sends requests, and the **server** (a central machine/program) processes them, stores data, applies business rules, and returns responses. Clients are many and lightweight; servers are fewer, more powerful, and controlled by you.

## 🔵 सरल परिभाषा (Hindi)
क्लाइंट (ऐप या ब्राउज़र) माँगता है, सर्वर काम करके जवाब देता है।
डेटा और नियम (business logic) सर्वर पर सुरक्षित रहते हैं; क्लाइंट सिर्फ़ दिखाने और यूज़र से बात करने का काम करता है।

---

## 🔴 Problem it Solves
- **Before (mainframe / standalone apps):** either everything ran on one huge central computer with dumb terminals, or every PC had its own copy of the data. Sharing data between users was hard, and updates had to be installed on every machine.
- **Client-server gives:**
  - **One source of truth** — all users see the same orders, balances, messages.
  - **Security** — business rules and secrets (DB password, payment keys) stay on the server, not on devices users control.
  - **Central updates** — fix a bug on the server once; all clients benefit.
  - **Separation of concerns** — UI teams (React, RN) and backend teams (Node, FastAPI) work independently through an API contract.

## 🔴 यह क्यों बना? (Hindi)
पहले हर कंप्यूटर पर अपना अलग डेटा होता था — सबके साथ शेयर करना और अपडेट करना मुश्किल था।
क्लाइंट-सर्वर में डेटा एक जगह (सर्वर) रहता है, सब एक ही सच देखते हैं, नियम और पासवर्ड सुरक्षित रहते हैं, और बग एक जगह ठीक करने से सबका ठीक हो जाता है।

---

## 🟢 How it Works — Step by Step

### Basic model

```
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ Browser  │  │ RN App   │  │ Partner  │     ← CLIENTS (many)
  │ (Next.js)│  │ iOS/And. │  │ Service  │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │  request    │             │
       └─────────────┼─────────────┘
                     ▼
            ┌─────────────────┐
            │     SERVER      │                ← one logical server (many machines behind it)
            │ API + business  │
            │ logic           │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │    DATABASE     │
            └─────────────────┘
```

### Tiers

```
2-Tier:   Client ────────────► Database
          (old desktop apps talked to DB directly — insecure, DB creds on every PC ❌)

3-Tier:   Presentation ──► Application/Logic ──► Data          ← standard web app ✅
          (React/RN)       (Node/FastAPI)        (Postgres)

N-Tier:   Client ─► CDN ─► Load Balancer ─► API Gateway ─► Services ─► Cache ─► DB
                                                             └─► Queue ─► Workers
          ← modern production systems
```

### Thin vs Thick client

```
┌────────────────┬──────────────────────────────┬──────────────────────────────┐
│                │ Thin client                  │ Thick (fat) client           │
├────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Logic lives    │ Mostly on server             │ Lots on client               │
│ Example        │ Server-rendered HTML (PHP,   │ SPA (React), React Native    │
│                │ Next.js SSR), terminal       │ app with offline DB, games   │
│ Offline        │ No                           │ Yes (local storage, sync)    │
│ Server load    │ Higher                       │ Lower                        │
│ Updates        │ Instant (server deploy)      │ Need app update / bundle     │
│ Security       │ Better (logic hidden)        │ Client code can be inspected │
└────────────────┴──────────────────────────────┴──────────────────────────────┘
Golden rule: NEVER trust the client. Validate, authorize and compute prices on the server,
even if the client also validates for UX.
```

### Client-server vs Peer-to-peer

```
Client-Server                    Peer-to-Peer (P2P)
     S                            A ─── B
   / | \                          │ \ / │
  C  C  C                         │  X  │
                                  C ─── D
Central control, easy security    No central server; peers share directly
Server = bottleneck/SPOF          Scales with users, hard to control/secure
Most apps                         BitTorrent, blockchain, WebRTC media (after signaling)
```

### Communication patterns between client & server
```
Request/Response  → REST, GraphQL, gRPC        (most calls)
Server push       → WebSocket, SSE              (real-time)
Push notification → FCM/APNs                    (mobile, app in background)
Async             → client gets 202 + jobId, polls or gets notified (video upload processing)
```

## 🟢 कैसे काम करता है? (Hindi)
1. क्लाइंट (ब्राउज़र/ऐप) API पर request भेजता है।
2. सर्वर request जाँचता है (auth, validation), business logic चलाता है, DB से डेटा पढ़ता/लिखता है।
3. सर्वर जवाब भेजता है; क्लाइंट उसे स्क्रीन पर दिखाता है।
4. 3-tier में तीन परतें: UI (React/RN) → Logic (Node/FastAPI) → Data (Postgres)।
5. सबसे ज़रूरी नियम: क्लाइंट पर कभी भरोसा मत करो — कीमत, permission सब सर्वर पर जाँचो।

---

## 🟡 Real World Example

**Zomato — one backend, many clients**
```
Customer app (RN/Native) ─┐
Restaurant partner app ───┤
Delivery partner app ─────┼──► Zomato backend APIs ──► DBs, payment, maps
Web (zomato.com) ─────────┤
Internal admin dashboard ─┘
```
All five clients show different screens but share one source of truth: the order. When the restaurant marks the order "ready", the customer and delivery apps both see it.

**A real security bug ("never trust the client")**
- Several e-commerce apps have been exploited because the **price was sent from the client** in the checkout request. Attackers modified the request (`price: 1`) with a proxy tool and bought items for ₹1. Fix: the server always recalculates the price from product IDs.

## 🟡 Real Example Hindi में
Zomato के ग्राहक ऐप, रेस्टोरेंट ऐप, डिलीवरी ऐप और वेबसाइट — सब एक ही backend से बात करते हैं, इसलिए ऑर्डर का स्टेटस सबको एक जैसा दिखता है।
कुछ शॉपिंग ऐप्स में कीमत क्लाइंट से आती थी — हैकर ने request बदलकर ₹1 में सामान ख़रीद लिया। इसलिए कीमत हमेशा सर्वर पर तय करो।

---

## 🟠 My Stack Example

### Your typical 3-tier (and growing to N-tier) setup
```
[Next.js web on Vercel]   [React Native app]
          │                       │
          └──── HTTPS / JSON ─────┘
                     │
          [Nginx / AWS ALB]                          ← entry point, TLS
                     │
     [Node.js (Express/Nest) or FastAPI]             ← business logic, auth
          │                │              │
   [PostgreSQL]        [Redis]      [S3 for files]   ← data tier
```

### Never trust the client — server computes the price
```js
// ❌ BAD
app.post('/checkout', async (req, res) => {
  await chargeCard(req.user, req.body.totalAmount);   // client could send 1
});

// ✅ GOOD
app.post('/checkout', auth, async (req, res) => {
  const items = CheckoutSchema.parse(req.body).items;                // only ids + qty
  const products = await Product.findMany({ where: { id: { in: items.map(i => i.id) } } });
  const total = items.reduce((sum, i) => sum + products.find(p => p.id === i.id).price * i.qty, 0);
  const coupon = await validateCoupon(req.body.couponCode, req.user); // server-side check
  const order = await createOrder(req.user.id, items, total - coupon.discount);
  res.status(201).json(order);
});
```

### Share the contract between clients and server (monorepo)
```
apps/
  web/        (Next.js)
  mobile/     (React Native / Expo)
  api/        (Node.js)
packages/
  schemas/    ← zod schemas used by ALL: client-side form validation + server validation
  api-client/ ← typed fetch functions used by web + mobile
```
```ts
// packages/schemas/order.ts
export const CheckoutSchema = z.object({
  items: z.array(z.object({ id: z.string().uuid(), qty: z.number().int().min(1).max(20) })).min(1),
  couponCode: z.string().optional(),
});
```

### Async pattern for slow work (thin request, worker does the job)
```python
# FastAPI: return 202 immediately, process in background worker (Celery/RQ/ARQ)
@app.post("/reports", status_code=202)
async def create_report(body: ReportIn, user=Depends(current_user)):
    job = await queue.enqueue("generate_report", user.id, body.model_dump())
    return {"jobId": job.id, "statusUrl": f"/reports/jobs/{job.id}"}
```

---

## ⚫ Interview Questions + Answers

**Q1: What is client-server architecture and what are its main benefits?**
A1: Clients send requests; a server processes them and responds, owning the data and business rules. Benefits: a single source of truth, centralized security and access control, easy updates, independent scaling of server resources, and a clear separation between UI and backend through an API contract.

**Q2: Explain 2-tier vs 3-tier architecture. Why is 3-tier preferred?**
A2: In 2-tier, the client talks to the database directly, which means DB credentials on clients, business logic duplicated in clients, and poor scalability. 3-tier adds an application layer between UI and data, which centralizes logic, validation and security, hides the DB, allows caching, and lets each tier scale independently. Modern systems extend this to N-tier with CDN, LB, gateway, services, caches and queues.

**Q3: What does "never trust the client" mean? Give examples.**
A3: Anything from the client can be modified (dev tools, proxies like Burp, decompiled mobile apps). So the server must re-validate inputs, enforce authorization on every request (not just hide buttons in the UI), compute prices, discounts and balances, check ownership (`order.userId === req.user.id`, to prevent IDOR), and never rely on client-side flags like `isAdmin: true`. Secrets must never be shipped in the JS bundle or mobile app.

**Q4: Thin client vs thick client — when to pick which?**
A4: A thin client (server-rendered pages) gives faster first load, better SEO, a simpler client and instant updates, which suits content and e-commerce pages. A thick client (SPA, mobile apps) gives rich interactions, offline support and less server load, which suits dashboards, chat and editors. Modern apps are hybrids: Next.js SSR for first paint, then client-side interactivity. Mobile apps are thick but still keep critical logic on the server.

**Q5: How does client-server differ from peer-to-peer? When would you use P2P?**
A5: Client-server has a central authority, which makes it easy to secure, consistent and simple to reason about, but the server is a bottleneck and cost center. P2P peers communicate directly: it scales with users and is resilient, but is hard to secure, moderate and keep consistent. P2P suits file sharing (BitTorrent), blockchains and WebRTC video calls (media flows peer-to-peer, while a server still does signaling and TURN fallback).

---

## 🔷 Trade-offs
✅ Advantages:
- Centralized data, security, and updates.
- Clear separation: UI teams and backend teams evolve independently.
- Server can be scaled, monitored and backed up in one place.

❌ Disadvantages:
- Server is a potential bottleneck / single point of failure (needs LB, replicas).
- Clients depend on network; offline needs extra work.
- Server costs grow with users (vs P2P).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Client | Requests a service (app, browser) | सेवा माँगने वाला |
| Server | Provides the service, owns data | सेवा देने वाला |
| Tier | A layer of the architecture | आर्किटेक्चर की परत |
| Business logic | Rules of the application | ऐप के नियम |
| Thin client | Little logic on device | कम लॉजिक वाला क्लाइंट |
| Thick client | Lots of logic on device | ज़्यादा लॉजिक वाला क्लाइंट |
| P2P | Devices talk directly, no central server | सीधे आपस में जुड़े डिवाइस |
| IDOR | Accessing others' data by changing an ID | ID बदलकर दूसरे का डेटा देखना |

---

## ⚡ 3-Line Summary
**English:**
1. Clients request, servers process and own the data and rules; 3-tier = UI → logic → data.
2. Never trust the client: validate, authorize and calculate on the server.
3. Modern systems are N-tier (CDN, LB, gateway, services, cache, queue, DB) serving many client types.

**Hindi:**
1. क्लाइंट माँगता है, सर्वर काम करता है; 3-tier = UI → Logic → Data।
2. क्लाइंट पर भरोसा नहीं — सब जाँच सर्वर पर।
3. आज के सिस्टम N-tier हैं: CDN, LB, Gateway, Services, Cache, Queue, DB।

---

## ➡️ Next Topic Suggestion
**10. Request-Response Lifecycle** — Now follow ONE request through every layer of that architecture, from the tap on the phone to the DB and back, and see where time is spent and where things can fail.
