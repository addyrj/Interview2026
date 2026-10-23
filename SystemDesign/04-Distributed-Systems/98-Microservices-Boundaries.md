# 98. Microservices Boundaries
# हिंदी में: Microservice Boundaries — सिस्टम को services में कहाँ से और कैसे बाँटना है, यह तय करना; business domains (bounded contexts) के हिसाब से, न कि tech layers के हिसाब से

---

## 🔵 Simple Definition (English)
**Service boundaries** define **what each microservice owns**: which business capability, which data, which APIs and events. Good boundaries follow **business domains** (Domain-Driven Design **bounded contexts**: Ordering, Payments, Catalog, Delivery, Identity) so each service is **highly cohesive inside** and **loosely coupled outside**, can be **owned by one team**, and can **change and deploy independently**.

## 🔵 सरल परिभाषा (Hindi)
Service boundary तय करती है कि हर microservice किस business काम और किस डेटा की मालिक है — जैसे Ordering, Payments, Catalog, Delivery।
अच्छी boundary में service अंदर से एकजुट और बाहर से अलग होती है, एक टीम उसकी मालिक होती है, और वो बाक़ियों से अलग बदल और deploy हो सकती है।

---

## 🔴 Problem it Solves
Wrong boundaries are the #1 reason microservice migrations fail:
- **Too fine-grained ("nano-services"):** `user-email-service`, `user-address-service`… every request hops through 8 services, and every feature touches 5 repos.
- **Split by technical layer:** "API service", "business logic service", "DB service" → every change crosses all layers.
- **Shared database** between services → hidden coupling, lockstep deploys (a distributed monolith).
- **Chatty synchronous calls** between two services that are really one domain → latency, cascading failures, distributed transactions everywhere.

Good boundaries minimize **cross-service transactions and chatter**, and match **team ownership** (Conway's Law).

## 🔴 यह क्यों बना? (Hindi)
ग़लत boundaries की वजह से ज़्यादातर microservice प्रोजेक्ट फ़ेल होते हैं — बहुत छोटी services (हर request 8 services से गुज़रे), tech layers के हिसाब से बँटवारा, साझा database (distributed monolith), और दो services के बीच लगातार कॉल्स।
अच्छी boundaries से services के बीच transactions और बातचीत कम होती है और हर service एक टीम की ज़िम्मेदारी बनती है।

---

## 🟢 How it Works — Step by Step

### Domain-Driven Design basics

```
Domain            → the business problem space (online food delivery)
Subdomains        → Core (competitive advantage): Dispatch/Delivery matching, Pricing
                    Supporting: Restaurant onboarding, Menu management
                    Generic: Identity/Auth, Notifications, Payments (often buy/integrate)
Bounded context   → boundary within which a model and its terms have ONE consistent meaning
Ubiquitous language → the shared vocabulary inside a context ("Order", "Rider", "Slot")

Same word, different meaning per context (classic signal of a boundary):
  "Order" in Ordering       → items, price, status for the CUSTOMER
  "Order" in Restaurant     → kitchen ticket: items to cook, prep time
  "Order" in Delivery       → pickup & drop task: locations, rider, ETA
  "Order" in Accounting     → invoice, taxes, commissions, payouts
→ 4 contexts, each with its own model of "order", linked by orderId and events
```

### Example decomposition: food delivery

```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ Identity   │  │ Catalog    │  │ Ordering   │  │ Payments   │  │ Delivery   │
│ users,auth │  │ restaurants│  │ cart,order │  │ charges,   │  │ riders,    │
│ profiles   │  │ menus,     │  │ lifecycle  │  │ refunds,   │  │ dispatch,  │
│            │  │ pricing?   │  │            │  │ ledger     │  │ tracking   │
└────────────┘  └────────────┘  └────────────┘  └────────────┘  └────────────┘
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Promotions │  │ Notification│ │ Search/    │   ← read-optimized (CQRS, fed by events)
│ coupons    │  │ push/SMS   │  │ Discovery  │
└────────────┘  └────────────┘  └────────────┘
Each: own database, own team(s), communicates via APIs + events.
```

### Heuristics for a good boundary

```
✓ Business capability: maps to a thing the business does (take payments, dispatch riders)
✓ Data ownership: one service is the source of truth for its entities; others keep copies via events
✓ Transactional boundary: things that must change ATOMICALLY together stay in ONE service
     (order + order items + order status history) → avoid distributed transactions
✓ Team ownership: one team can own it end-to-end ("two-pizza team"); Conway's Law
✓ Independent change: most features touch ONE service
✓ Different scaling/reliability/compliance needs → separate (payments PCI scope, search scaling)
✓ Low chattiness: if A calls B synchronously for most requests, they may belong together

Red flags (wrong boundary):
✗ Two services always deployed together
✗ Shared tables / one service reading another's DB
✗ A business change requires coordinated changes in 3+ services
✗ Long synchronous call chains (A→B→C→D) for one request
✗ "Entity services" (UserService, ProductService as CRUD wrappers) with logic scattered elsewhere
```

### How to find boundaries in practice

```
1. Event Storming workshop: put domain events on a timeline (OrderPlaced, PaymentCaptured,
   RiderAssigned, OrderDelivered); group by who cares → contexts emerge
2. Look for language changes and separate data lifecycles
3. Start COARSE (modular monolith with modules = future services); extract when needed
4. Extract the module that most needs independence first (different scale/team/release cadence)
5. Strangler Fig: route new traffic for that capability to the new service; migrate gradually
```

### Integration between contexts
```
Sync (REST/gRPC) for queries needing immediate answers; Async events for state changes
Anti-corruption layer (ACL): translate another context's (or legacy system's) model into yours,
   so their changes don't leak into your domain
Published language: versioned, documented API/event contracts
```

### Size: "micro" isn't about lines of code
```
A service should be as small as possible but no smaller than one cohesive capability.
Uber's DOMA lesson: thousands of tiny services → regroup into domains with gateways.
Many successful companies run 10–50 well-bounded services, not 1,000.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Business को domains में बाँटो: Identity, Catalog, Ordering, Payments, Delivery, Promotions, Notifications।
2. एक ही शब्द ("Order") का हर context में अलग मतलब हो — ग्राहक के लिए, किचन के लिए, rider के लिए — यही boundary का संकेत है।
3. जो चीज़ें एक साथ atomic बदलनी हैं, वो एक ही service में रहें; हर service अपने डेटा की मालिक हो, बाक़ी events से copy रखें।
4. बुरे संकेत: हमेशा साथ deploy, साझा टेबल, एक feature के लिए 3+ services बदलना, लंबी sync call chain।
5. Event Storming से boundaries खोजो, पहले modular monolith बनाओ, फिर ज़रूरत के हिसाब से एक-एक module (Strangler Fig) अलग करो।

---

## 🟡 Real World Example

**Amazon "two-pizza teams"** — services are aligned to teams small enough to be fed by two pizzas, each owning a business capability end to end ("you build it, you run it"). That's Conway's Law used deliberately.

**Uber DOMA (2020)** — after growing to ~2,200 microservices, Uber grouped them into ~70 domains with clear gateways and layers. That reduced complexity and cross-team coupling and made boundaries explicit.

**Segment** — consolidated 140+ fine-grained destination services back into a monolith because the boundaries were too granular and maintenance overwhelmed the team.

**Swiggy / Zomato** — commonly decompose around ordering, catalog and menu, pricing and offers, payments, delivery dispatch, search and discovery, and customer support, each owned by separate teams with separate data stores.

**Shopify** — chose a modular monolith with enforced component boundaries instead of microservices, getting most of the ownership benefits without network costs.

## 🟡 Real Example Hindi में
Amazon की "two-pizza टीमें" — हर टीम एक business काम की पूरी मालिक। Uber 2,200 services तक गया, फिर उन्हें ~70 domains में समूहित किया (DOMA)।
Segment ने बहुत छोटी 140+ services को वापस monolith बनाया। Shopify ने microservices की जगह modular monolith चुना।

---

## 🟠 My Stack Example

### Start as a modular monolith with context folders (NestJS / Node)
```
src/contexts/
  identity/      (users, auth, profiles)          public: identity.api.ts, events: UserRegistered
  catalog/       (restaurants, menus)              public: catalog.api.ts, events: MenuUpdated
  ordering/      (cart, orders, status)            public: ordering.api.ts, events: OrderPlaced, OrderStatusChanged
  payments/      (charges, refunds, ledger)        public: payments.api.ts, events: PaymentCaptured
  delivery/      (riders, dispatch, tracking)      public: delivery.api.ts, events: RiderAssigned
  notifications/ (listens to events only)
Rules (lint-enforced): no imports into another context's internals; each context owns its tables
(schema per context: ordering.orders, payments.charges); cross-context reads via public API/events.
```

### Each context owns its data (Postgres schemas → later separate DBs)
```sql
CREATE SCHEMA ordering;  CREATE SCHEMA payments;  CREATE SCHEMA catalog;
CREATE TABLE ordering.orders (id BIGSERIAL PRIMARY KEY, user_id BIGINT, restaurant_id BIGINT, status TEXT, total_paise BIGINT);
CREATE TABLE payments.charges (id BIGSERIAL PRIMARY KEY, order_id BIGINT, amount_paise BIGINT, status TEXT);
-- ❌ no foreign key from payments.charges to ordering.orders across contexts (future service split)
-- ✅ store order_id as a reference; validate via API/event
-- DB roles: ordering_app can't SELECT payments.* → enforces the boundary today
```

### Anti-corruption layer (Delivery context consumes Ordering's event in its own model)
```ts
// delivery/acl/ordering-translator.ts
export function toDeliveryTask(evt: OrderPlacedV1): DeliveryTask {
  return {
    taskId: `task-${evt.data.orderId}`,
    pickup: { restaurantId: evt.data.restaurantId, location: evt.data.restaurantLocation },
    drop: { location: evt.data.deliveryAddress.location, contactMasked: maskPhone(evt.data.phone) },
    readyBy: estimateReadyTime(evt.data.items),
  };          // Delivery's model doesn't know about prices, coupons, or menu items
}
```

### Extracting a service later (Strangler Fig)
```
1. Payments module already isolated (own schema, public API, events)
2. Deploy payments-service (FastAPI) with its own DB; replicate payments schema data
3. Gateway/BFF routes /api/v1/payments/* to the new service (feature flag, % rollout)
4. Monolith calls payments via HTTP client instead of in-process API (same interface)
5. Remove payments code from monolith once traffic is 100% migrated
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you decide microservice boundaries?**
A1: Use Domain-Driven Design. Identify business capabilities and bounded contexts, the areas where a model and its vocabulary are consistent (Ordering, Payments, Catalog, Delivery). Each service owns its context's data and invariants, so anything that must change atomically lives in one service. Align services with team ownership, keep most changes local to one service, separate parts with different scaling or compliance needs, and minimize synchronous chatter between services. Event Storming is a practical way to discover the contexts.

**Q2: What is a bounded context?**
A2: A DDD concept: an explicit boundary within which a particular domain model and its ubiquitous language apply consistently. The same real-world concept can have different models in different contexts. An "Order" means a customer purchase in Ordering, a kitchen ticket in Restaurant and a delivery task in Delivery. Contexts integrate through well-defined contracts (APIs and events) and translation layers. They're natural candidates for service boundaries.

**Q3: What are signs that your microservice boundaries are wrong?**
A3: Services that must deploy together; shared databases or one service reading another's tables; features that routinely require coordinated changes across several services; long synchronous call chains per request; frequent distributed transactions or sagas for simple operations; very chatty service pairs; anemic "entity services" with logic spread elsewhere; and teams constantly blocked on other teams. The fix is to merge, re-split by capability, or move data ownership.

**Q4: Should you start a new product with microservices?**
A4: Usually not. Early on the domain isn't well understood, and wrong boundaries are costly to change. Start with a well-structured modular monolith whose modules follow bounded contexts with enforced boundaries (separate schemas, public interfaces, events), then extract services when there's a concrete need: team scaling, independent deployment, different scaling or reliability profiles, or isolation for compliance. Use the Strangler Fig pattern for extraction.

**Q5: What is an anti-corruption layer?**
A5: A translation layer at the boundary between your context and another context or legacy system. It converts their models, terminology and APIs into your own domain model, so changes or quirks on their side don't leak into your code. It's typically implemented as adapters or translators when consuming another service's API or events, or when wrapping a legacy system during migration.

---

## 🔷 Trade-offs
✅ Good boundaries: independent teams & deploys, local changes, fewer distributed transactions, clear ownership.
❌ Too fine: latency, chatty calls, distributed-transaction pain, ops overhead.
❌ Too coarse: monolith-like coupling inside a "service", team contention.
→ Start coarse, refine with evidence.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service boundary | What a service owns | service की सीमा |
| DDD | Domain-Driven Design | business domain पर आधारित design |
| Bounded context | Boundary of a consistent model | एक मॉडल की सीमा |
| Ubiquitous language | Shared domain vocabulary | साझा business शब्दावली |
| Core / Supporting / Generic subdomain | Strategic classification | domain का वर्गीकरण |
| Conway's Law | Systems mirror org structure | सिस्टम टीम ढाँचे जैसा बनता है |
| Event Storming | Workshop to discover domains | domains खोजने की कार्यशाला |
| Anti-corruption layer | Translator between models | मॉडलों के बीच अनुवादक |
| Strangler Fig | Gradual extraction pattern | धीरे-धीरे अलग करने का तरीका |
| Distributed monolith | Coupled services anti-pattern | जुड़ी हुई services |

---

## ⚡ 3-Line Summary
**English:**
1. Draw service boundaries around business capabilities / bounded contexts, not technical layers or entities.
2. A service owns its data and invariants; keep atomic changes inside one service; align with one team; minimize sync chatter.
3. Discover via Event Storming, start with a modular monolith, extract with Strangler Fig; watch for distributed-monolith red flags.

**Hindi:**
1. Boundaries business काम / bounded context के हिसाब से, tech layers या टेबल के हिसाब से नहीं।
2. Service अपने डेटा की मालिक; atomic बदलाव एक service में; एक टीम; sync कॉल्स कम।
3. Event Storming से खोजो, पहले modular monolith, फिर Strangler Fig से अलग करो।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Microservices explained](https://www.youtube.com/results?search_query=microservices+boundaries+design+bytebytego) | Domain decomposition, service sizing, anti-patterns |
| 📺 YouTube | [Tech Dummies — Microservices vs Monolith](https://www.youtube.com/results?search_query=microservices+vs+monolith+tech+dummies) | When to use each, migration path |
| 📝 Article | [Martin Fowler — Microservices](https://martinfowler.com/articles/microservices.html) | The original microservices definition paper |
| 📝 Article | [microservices.io — Decomposition patterns](https://microservices.io/patterns/decomposition/) | Decompose by subdomain, by capability — Chris Richardson |
| 🐙 GitHub | [ByteByteGoHq/system-design-101 — Microservices](https://github.com/ByteByteGoHq/system-design-101) | Visual diagrams of microservice communication and data patterns |

---

## ➡️ Next Topic Suggestion
**99. Database Per Service** — The most important consequence of good boundaries: each service owns its own database. Next: why, how services share data without sharing databases, and how to handle queries across services.
