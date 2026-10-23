# 13. Monolith Architecture
# हिंदी में: Monolith — पूरा ऐप (users, orders, payments, notifications) एक ही codebase और एक ही deploy में

---

## 🔵 Simple Definition (English)
A **monolith** is an application where all features — auth, users, products, orders, payments, notifications — live in **one codebase**, are built into **one deployable unit**, run as **one process**, and usually share **one database**.

## 🔵 सरल परिभाषा (Hindi)
Monolith में पूरा ऐप एक ही प्रोजेक्ट में होता है, एक साथ deploy होता है, और आम तौर पर एक ही database इस्तेमाल करता है।
जैसे एक बड़ी दुकान जहाँ सब कुछ एक ही छत के नीचे मिलता है।

---

## 🔴 Problem it Solves
A monolith is the **default, simplest way** to build software. It's not "old and bad"; it solves real problems for most teams:
- **Speed to market:** one repo, one deploy, one DB → a small team ships features fast.
- **Simple development:** function calls instead of network calls; one debugger; easy local setup.
- **Strong consistency:** one DB transaction can update orders + inventory + payments together (ACID).
- **Low ops cost:** one server/container, one CI pipeline, one log stream.

The problems start **later**, when the codebase and team grow large → that's when microservices are considered (next topic).

## 🔴 यह क्यों बना? (Hindi)
Monolith सॉफ़्टवेयर बनाने का सबसे सीधा तरीका है — एक repo, एक deploy, एक DB, इसलिए छोटी टीम बहुत तेज़ काम कर सकती है।
एक ही transaction में कई टेबल अपडेट हो जाती हैं, debugging आसान है, ख़र्च कम है। दिक़्क़तें तब आती हैं जब ऐप और टीम बहुत बड़ी हो जाती है।

---

## 🟢 How it Works — Step by Step

### Structure

```
              ┌──────────────────────────────────────────┐
 Clients ───► │           ONE APPLICATION (Node.js)      │
              │  ┌────────┐ ┌────────┐ ┌──────────┐      │
              │  │  Auth  │ │ Users  │ │ Products │      │
              │  └────────┘ └────────┘ └──────────┘      │
              │  ┌────────┐ ┌────────┐ ┌──────────┐      │
              │  │ Orders │ │Payments│ │ Notific. │      │
              │  └────────┘ └────────┘ └──────────┘      │
              │   (modules call each other via functions) │
              └────────────────────┬─────────────────────┘
                                   ▼
                        ┌────────────────────┐
                        │  ONE PostgreSQL DB │
                        └────────────────────┘
```

### Scaling a monolith (it CAN scale!)

```
                     ┌──► Monolith copy 1 ─┐
 Load Balancer ──────┼──► Monolith copy 2 ─┼──► Postgres primary ──► read replicas
                     └──► Monolith copy 3 ─┘         + Redis cache
                                    │
                              background workers (same codebase, different entrypoint)

Horizontal scaling works fine IF the app is stateless (sessions in Redis/JWT).
Shopify, GitHub, Stack Overflow, Basecamp all run huge MONOLITHS at scale.
```

### Types of monoliths

```
1. Big Ball of Mud     ❌  everything imports everything, no boundaries
2. Layered monolith    ⚠️  controllers / services / repositories — but by tech layer
3. MODULAR MONOLITH    ✅  split by business domain (orders, payments, users),
                          each module has its own folder, public interface,
                          and own tables; modules talk only through interfaces/events.
                          → easiest path to microservices later
```

### When the monolith starts to hurt

```
Symptom                                          Why
────────────────────────────────────────────     ────────────────────────────────
Deploy takes 40 min, everyone waits             one big build/test suite
One bug in "reports" crashes checkout           shared process, no isolation
Can't scale only the hot part (search)          must scale the whole app
50 devs, constant merge conflicts               one codebase, unclear ownership
Stuck on old framework/language version         upgrade = whole app
Slow startup, huge memory                       everything loaded
```

## 🟢 कैसे काम करता है? (Hindi)
1. सारे features (auth, orders, payments) एक ही ऐप में अलग-अलग modules/folders की तरह होते हैं।
2. Modules आपस में सीधे function call से बात करते हैं — network की ज़रूरत नहीं।
3. एक ही database, इसलिए एक transaction में सब कुछ सुरक्षित तरीके से अपडेट होता है।
4. स्केल करने के लिए पूरे ऐप की कई copies Load Balancer के पीछे चलाते हैं।
5. सबसे अच्छा तरीका "Modular Monolith" है — हर business domain का अलग module, साफ़ सीमाओं के साथ।

---

## 🟡 Real World Example

**Shopify** — one of the largest Ruby on Rails monoliths in the world (millions of lines). Instead of breaking it into microservices, they turned it into a **modular monolith** ("components" with enforced boundaries using a tool called Packwerk). It handles Black Friday traffic of millions of requests per minute.

**Amazon Prime Video (2023)** — their video-quality monitoring tool was built on microservices plus serverless (Step Functions, Lambda). Moving it to a **monolith reduced infrastructure cost by 90%**, because data no longer had to be passed between services over the network and S3.

**Stack Overflow** — serves billions of page views per month with a .NET monolith on a handful of servers, heavily optimized and cached.

**Most Indian startups (early Swiggy, Zomato, Razorpay)** — started as monoliths and split into services only after hitting scale and team-size limits.

## 🟡 Real Example Hindi में
Shopify दुनिया के सबसे बड़े monolith में से एक है — उन्होंने microservices की जगह उसे "modular monolith" बनाया, और Black Friday का भारी ट्रैफ़िक संभालता है।
Amazon Prime Video ने एक टूल को microservices से monolith में बदला और ख़र्च 90% कम हो गया। Swiggy, Zomato भी monolith से ही शुरू हुए थे।

---

## 🟠 My Stack Example

### Modular monolith in Node.js / NestJS (recommended starting point)
```
src/
  modules/
    auth/
      auth.controller.ts
      auth.service.ts
      index.ts            ← public API of the module (only this is imported by others)
    users/
    catalog/
    orders/
      orders.controller.ts
      orders.service.ts
      orders.repository.ts   ← owns tables: orders, order_items
      events.ts              ← emits "order.placed"
      index.ts
    payments/
    notifications/
      listeners.ts           ← listens to "order.placed"
  shared/                    ← logger, db client, config, errors
  main.ts                    ← HTTP entrypoint
  worker.ts                  ← background jobs entrypoint (same codebase)
```

```ts
// orders.service.ts — talk to other modules via their public interface or events
import { PaymentsApi } from '../payments';          // ✅ module's index.ts
// import { PaymentRepo } from '../payments/payments.repository'; ❌ reaching into internals

export class OrdersService {
  constructor(private repo: OrdersRepo, private payments: PaymentsApi, private bus: EventBus) {}

  async place(userId: string, input: PlaceOrderInput) {
    const order = await this.repo.transaction(async (tx) => {
      const o = await this.repo.create(tx, userId, input);
      await this.payments.reserve(tx, o.id, o.total);   // same DB transaction → consistent
      return o;
    });
    this.bus.emit('order.placed', { orderId: order.id }); // notifications listens (loose coupling)
    return order;
  }
}
```

Enforce boundaries automatically:
```js
// .eslintrc — forbid deep imports into other modules
"no-restricted-imports": ["error", { "patterns": ["../*/!(index)", "**/modules/*/*.repository"] }]
```
(Or use `dependency-cruiser` / Nx module boundaries.)

### FastAPI modular monolith
```
app/
  orders/   (router.py, service.py, models.py, schemas.py)
  payments/
  users/
  main.py   → app.include_router(orders.router, prefix="/api/v1/orders") ...
```

### Deploy: one Docker image, two roles
```yaml
services:
  api:
    image: myapp:1.4.2
    command: node dist/main.js
    deploy: { replicas: 3 }
  worker:
    image: myapp:1.4.2           # SAME image
    command: node dist/worker.js # different entrypoint (queues, cron)
  db:    { image: postgres:16 }
  redis: { image: redis:7 }
```

### Monolith + Next.js + React Native
```
Next.js (web) ─┐
               ├──► ONE Node/FastAPI monolith API ──► Postgres + Redis + S3
RN app ────────┘
```
For a team of 2–15 devs, this is usually the **right** architecture.

---

## ⚫ Interview Questions + Answers

**Q1: What is a monolith? What are its pros and cons?**
A1: A single deployable application containing all business features, usually with one shared database. Pros: simple development, testing, debugging and deployment; fast in-process calls; ACID transactions across features; low infrastructure and ops cost; fast iteration for small teams. Cons: as it grows, builds and deploys get slow; one bug can take everything down; you can't scale or choose a different technology for individual parts; and large teams step on each other.

**Q2: Can a monolith scale? How?**
A2: Yes. Run many stateless instances behind a load balancer (horizontal scaling), keep sessions in Redis or JWT, add caching (Redis, CDN), read replicas and good indexing for the DB, and move heavy work to background workers from the same codebase. Shopify, GitHub and Stack Overflow serve huge traffic with monoliths. The limits usually come from team and organization scaling, not technical scaling.

**Q3: What is a modular monolith and why is it often recommended?**
A3: A monolith split internally by business domains (orders, payments, users). Each module has a clear public interface, owns its data/tables, and communicates via interfaces or in-process events, with boundaries enforced by lint or tooling. You get most of the organizational benefits of microservices (ownership, decoupling) without distributed-systems complexity. Modules can later be extracted into services if needed.

**Q4: When would you move from a monolith to microservices?**
A4: When there are clear signals: many teams blocked by a shared deploy pipeline; parts with very different scaling needs (search, media processing); failure isolation required for critical paths (payments); different tech needs (an ML service in Python); and a codebase too big to understand. Even then, extract incrementally with the Strangler Fig pattern, starting with the most independent, high-value domain, never a big-bang rewrite.

**Q5: You're starting a new startup product. Monolith or microservices?**
A5: Almost always a well-structured modular monolith. Requirements change rapidly, so domain boundaries aren't known yet, and wrong service boundaries are very expensive to fix. A small team can't afford the operational overhead (service discovery, distributed tracing, eventual consistency, many pipelines). Keep it stateless and modular so it can scale horizontally and split later. "Monolith first" (Martin Fowler).

---

## 🔷 Trade-offs
✅ Advantages:
- Simple to build, test, debug, deploy; one repo, one pipeline.
- In-process calls (fast), single DB transactions (consistent).
- Cheap to run; ideal for small/medium teams and new products.

❌ Disadvantages:
- Large codebase → slow builds, tight coupling if not modular.
- No fault isolation — a memory leak in one module kills all.
- Scale everything together; one tech stack; big-team coordination pain.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Monolith | Single deployable app with all features | एक ही ऐप में सब कुछ |
| Modular monolith | Monolith split by business modules | modules में बँटा monolith |
| Deployable unit | Thing you build and release | एक साथ release होने वाली इकाई |
| Coupling | How much parts depend on each other | आपस में जुड़ाव |
| Big ball of mud | Messy code with no structure | बिना ढाँचे का उलझा कोड |
| Strangler Fig | Gradually replace parts of old system | धीरे-धीरे पुराना सिस्टम बदलना |
| Fault isolation | Failure in one part doesn't affect others | एक की ख़राबी दूसरे पर असर न डाले |

---

## ⚡ 3-Line Summary
**English:**
1. Monolith = one codebase, one deploy, usually one DB — simplest and fastest way to start.
2. It scales horizontally fine; the real limits are team size, deploy speed and fault isolation.
3. Build a modular monolith with clear domain boundaries so you can extract services later.

**Hindi:**
1. Monolith = एक codebase, एक deploy, एक DB — शुरुआत का सबसे आसान तरीका।
2. यह स्केल हो सकता है; असली दिक़्क़त बड़ी टीम, धीमा deploy और fault isolation है।
3. Modular monolith बनाओ, ताकि ज़रूरत पड़ने पर बाद में services अलग कर सको।

---

## ➡️ Next Topic Suggestion
**14. Microservices Architecture** — When the monolith's pains become real, teams split it. Next: what microservices are, how they communicate, what they cost you (network, consistency, ops), and how companies like Swiggy and Netflix use them.
