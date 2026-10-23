# 99. Database Per Service
# हिंदी में: Database Per Service — हर microservice का अपना अलग database, जिसे सिर्फ़ वही service सीधे छू सकती है; बाक़ी services API या events से डेटा लेती हैं

---

## 🔵 Simple Definition (English)
In the **database-per-service** pattern, each microservice has **exclusive ownership** of its data store (its own DB, schema, or tables with access restricted to it). Other services **never read or write it directly**. They use the owner's **API** or consume its **events** (keeping local copies if needed). Each service can pick the **best database for its job** (Postgres for orders, Redis for sessions, Elasticsearch for search, Cassandra for messages): **polyglot persistence**.

## 🔵 सरल परिभाषा (Hindi)
हर microservice का अपना database होता है, जिसे सिर्फ़ वही सीधे पढ़/लिख सकती है। दूसरी services को डेटा चाहिए तो उस service की API या events से लेती हैं।
इससे services सच में अलग रहती हैं, और हर service अपने काम के लिए सबसे सही DB चुन सकती है।

---

## 🔴 Problem it Solves
A **shared database** across microservices destroys their independence:
- **Hidden coupling:** Order service reads `payments` tables directly. When Payments renames a column, Orders breaks in production.
- **Lockstep deploys:** schema migrations need coordination across teams → a **distributed monolith**.
- **No clear ownership:** who validates the data? Who can change a table?
- **Scaling/performance interference:** one service's heavy queries slow down all others; one DB = SPOF and scaling bottleneck.
- **One technology for everything**, even when another store fits better.

Database per service gives **loose coupling, autonomy, independent scaling and the right tool per job**.

## 🔴 यह क्यों बना? (Hindi)
सबका एक साझा DB हो तो छिपा हुआ जुड़ाव: Payments ने column बदला और Orders टूट गया; migrations के लिए सब टीमों को साथ deploy करना पड़ता है; कौन डेटा का मालिक है पता नहीं; एक service की भारी query सबको धीमा करती है।
हर service का अपना DB → सच्ची आज़ादी, अलग स्केलिंग और हर काम के लिए सही DB।

---

## 🟢 How it Works — Step by Step

### Ownership

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Order Svc    │    │ Payment Svc  │    │ Catalog Svc  │    │ Search Svc   │
│      │       │    │      │       │    │      │       │    │      │       │
│  [Postgres]  │    │  [Postgres]  │    │  [MongoDB]   │    │[Elasticsearch]│
│  orders      │    │  charges     │    │  menus       │    │ (read model) │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────▲───────┘
       │ API / events      │                   │ MenuUpdated events │
       └───────────────────┴───────────────────┴────────────────────┘
❌ Order Svc → SELECT * FROM payments.charges     (forbidden)
✅ Order Svc → GET payment-svc/charges?orderId=…  or consume PaymentCaptured event
```

### Levels of isolation (cost vs strictness)
```
1. Private tables per service in a shared DB server (enforced by DB users/roles/grants)   ← cheapest
2. Schema per service on a shared server (separate schema + role per service)
3. Database instance per service (separate RDS instance/cluster)                          ← strongest
Pragmatic start: 1 or 2 (cheap), move heavy/critical services to 3 as they grow.
The RULE matters more than the physical setup: only the owner accesses its data.
```

### How to get data you don't own

```
1. API composition (synchronous query)
   Order page needs restaurant name + payment status:
   BFF calls order-svc + catalog-svc + payment-svc in parallel → merges
   ✅ always fresh   ❌ latency, availability depends on all

2. Data replication via events (local read copy) ⭐
   Order svc subscribes to RestaurantUpdated → keeps orders_restaurant_cache(id, name, logo)
   ✅ fast local reads, resilient   ❌ eventually consistent, duplicated data

3. CQRS read models (Topic 71)
   Dedicated query service builds denormalized views from many services' events
   (e.g. admin "order 360°" view in Elasticsearch)

4. Analytics: CDC from every DB → data lake/warehouse (BigQuery/Snowflake/ClickHouse) for joins
   across services (never join across service DBs in production paths)
```

### Consistency across services
```
No cross-service ACID transactions → Saga + outbox + idempotent consumers (Topics 68–70)
No cross-service foreign keys → store reference IDs; validate via API or events; handle "dangling"
references (e.g. deleted restaurant) gracefully
```

### Challenges
```
- Queries spanning services (joins) → API composition / read models / warehouse
- Data duplication & sync lag
- Distributed transactions → sagas
- Operational overhead: more DBs to back up, monitor, patch (managed DBs help)
- Reporting/BI needs a central warehouse
- Migration from a shared DB: identify ownership, add APIs, cut direct access gradually
```

### Polyglot persistence examples
```
Ordering → PostgreSQL (ACID, relations)
Payments ledger → PostgreSQL / strongly consistent DB
Catalog → MongoDB or Postgres JSONB (flexible attributes)
Sessions/carts → Redis
Chat messages → Cassandra/ScyllaDB
Search → Elasticsearch/OpenSearch
Analytics → ClickHouse/BigQuery
Rider locations → Redis GEO + Cassandra history
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर service अपने DB (या कम से कम अपने schema/tables) की अकेली मालिक; बाक़ी को सीधी पहुँच नहीं (DB roles से लागू करो)।
2. दूसरी service का डेटा चाहिए तो: API से पूछो (ताज़ा, पर धीमा), या events से अपनी local copy रखो (तेज़, थोड़ा पुराना)।
3. कई services का मिला-जुला view चाहिए तो CQRS read model; रिपोर्ट/analytics के लिए CDC से warehouse।
4. Services के बीच ACID transaction और foreign keys नहीं — Saga, outbox और reference IDs।
5. शुरुआत में एक DB सर्वर पर अलग schemas (सस्ता), बड़ी services को बाद में अलग DB instance।

---

## 🟡 Real World Example

**Amazon** — a 2002 mandate (the famous "Bezos API memo") required teams to expose data and functionality only through service interfaces, with no direct database access between teams. That set the foundation for AWS and Amazon's service architecture.

**Netflix** — each service owns its data (Cassandra, EVCache, MySQL, Elasticsearch) and shares through APIs and events, with a data platform (Kafka and data lake) for cross-service analytics.

**Uber / Swiggy-scale companies** — use polyglot stores per domain (MySQL/Postgres for trips or orders, Redis for real-time state, Cassandra for high-volume logs, Elasticsearch for search), synced via Kafka and CDC.

**The shared-DB trap** — many companies' first "microservices" were just multiple apps reading one database. A single migration or slow query on the shared DB caused company-wide outages, which pushed them to enforce per-service ownership.

## 🟡 Real Example Hindi में
2002 में Amazon के "Bezos API memo" ने कहा — टीमें डेटा सिर्फ़ service API से साझा करेंगी, एक-दूसरे के DB सीधे नहीं छुएँगी; यहीं से AWS की नींव पड़ी।
Netflix और Uber में हर service का अपना DB है (Cassandra, MySQL, Redis), और डेटा Kafka/CDC से साझा होता है। कई कंपनियों में साझा DB की एक ग़लत migration से पूरी कंपनी का सिस्टम गिरा।

---

## 🟠 My Stack Example

### Stage 1: shared Postgres server, separate schemas + roles (cheap, enforced)
```sql
CREATE SCHEMA ordering;  CREATE SCHEMA payments;
CREATE ROLE ordering_svc LOGIN PASSWORD '...';
CREATE ROLE payments_svc LOGIN PASSWORD '...';
GRANT USAGE, CREATE ON SCHEMA ordering TO ordering_svc;
GRANT USAGE, CREATE ON SCHEMA payments TO payments_svc;
REVOKE ALL ON SCHEMA payments FROM ordering_svc;     -- ordering can't touch payments data
ALTER ROLE ordering_svc SET search_path = ordering;
```

### docker-compose for local dev (stage 3 style: DB per service)
```yaml
services:
  order-service:   { build: ./order,   environment: { DATABASE_URL: postgres://u:p@order-db/orders } }
  payment-service: { build: ./payment, environment: { DATABASE_URL: postgres://u:p@payment-db/payments } }
  catalog-service: { build: ./catalog, environment: { MONGO_URL: mongodb://catalog-db/catalog } }
  order-db:   { image: postgres:16 }
  payment-db: { image: postgres:16 }
  catalog-db: { image: mongo:7 }
```

### Local read copy via events (Order service keeps restaurant names)
```js
// order-service consumer
onEvent('catalog.restaurant.updated.v1', async (evt) => {
  await db.query(`INSERT INTO restaurant_refs(id, name, logo_url, updated_at) VALUES ($1,$2,$3,$4)
                  ON CONFLICT (id) DO UPDATE SET name=$2, logo_url=$3, updated_at=$4
                  WHERE restaurant_refs.updated_at < $4`,                // ignore stale/out-of-order events
                 [evt.data.id, evt.data.name, evt.data.logoUrl, evt.time]);
});
// "My orders" now joins locally: orders JOIN restaurant_refs — no call to catalog-svc
```

### API composition in a BFF (fresh data, parallel)
```js
app.get('/mobile/v1/orders/:id', authenticate, async (req, res) => {
  const order = await orderSvc.get(req.params.id, req.user.id);
  const [restaurant, payment, tracking] = await Promise.allSettled([
    catalogSvc.restaurant(order.restaurantId),
    paymentSvc.byOrder(order.id),
    deliverySvc.tracking(order.id),
  ]);
  res.json({
    ...order,
    restaurant: restaurant.status === 'fulfilled' ? restaurant.value : { id: order.restaurantId },
    paymentStatus: payment.status === 'fulfilled' ? payment.value.status : 'UNKNOWN',
    tracking: tracking.status === 'fulfilled' ? tracking.value : null,
  });
});
```

### Cross-service analytics (never join production DBs)
```
Each service DB ──Debezium CDC──► Kafka ──► S3/ClickHouse/BigQuery
SQL joins across orders, payments, catalog happen in the warehouse for BI dashboards
```

### FastAPI service with its own DB
```python
# payment-service/app/db.py — the ONLY code allowed to use PAYMENTS_DATABASE_URL
engine = create_async_engine(os.environ["PAYMENTS_DATABASE_URL"], pool_size=10)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the database-per-service pattern and why use it?**
A1: Each microservice exclusively owns its data store, and others access that data only via its API or events. It ensures loose coupling (schema changes stay internal), independent deployment and scaling, clear data ownership and validation, fault isolation (one DB's problems don't take down everything), and the freedom to choose the best database per service (polyglot persistence). A shared database creates a distributed monolith.

**Q2: How do you query data that spans multiple services?**
A2: API composition: an aggregator (BFF or gateway) calls the owning services in parallel and merges the results, which gives fresh data but adds latency and failure points. Event-driven replication: services keep local read copies of the data they need from others' events, which is fast but eventually consistent. CQRS read models: a query service builds denormalized views from many services' events. For analytics and reporting, CDC into a data warehouse where cross-service joins are allowed. Never join across service databases directly in production code.

**Q3: How do you maintain consistency without cross-service transactions?**
A3: Use sagas (local transactions plus compensations) orchestrated or choreographed via events. Publish events with the transactional outbox, make consumers idempotent, and design for eventual consistency in the UX. Use reference IDs instead of foreign keys and handle missing references gracefully. Run reconciliation jobs for critical data like payments. Keep data that must be updated atomically inside one service's boundary.

**Q4: Do you need a separate database server for every service?**
A4: Not necessarily. The key rule is exclusive ownership and no direct cross-service access. Cost-effective options are private tables or schemas per service on a shared database server, enforced with separate DB roles and grants. Move to dedicated instances when a service needs independent scaling, different technology, stricter isolation (compliance, like payments under PCI), or to avoid noisy-neighbour effects. Managed databases reduce the operational burden.

**Q5: How would you migrate from a shared database to database-per-service?**
A5: First assign ownership of each table to one service and document it. Find all cross-service reads and writes (query logs). Add APIs or events on the owning service and switch consumers to them, building local read copies where needed. Restrict access with DB roles so new violations can't appear. Move the owned tables to a separate schema or DB using replication or CDC with a short cutover. Do it one service at a time (Strangler Fig), and keep a warehouse fed by CDC for reporting that used to rely on cross-table joins.

---

## 🔷 Trade-offs
✅ Advantages:
- True service autonomy, independent schema evolution & scaling, fault isolation, best-fit databases.

❌ Disadvantages:
- No cross-service joins/ACID; data duplication and eventual consistency.
- More databases to operate and pay for; reporting needs a warehouse.
- Requires discipline (APIs, events, sagas, ownership rules).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Database per service | Each service owns its DB | हर service का अपना DB |
| Data ownership | One service is source of truth | डेटा की मालिक service |
| Polyglot persistence | Different DB types per need | ज़रूरत के हिसाब से अलग DB |
| API composition | Combining data from several APIs | कई APIs का डेटा जोड़ना |
| Local read copy | Replicated data via events | events से रखी copy |
| Reference ID | Foreign ID without FK constraint | बिना FK का संदर्भ id |
| Shared database anti-pattern | Many services one DB | सबका एक DB (ग़लत तरीका) |
| CDC | Stream DB changes | DB बदलावों की धारा |
| Data warehouse | Central analytics store | विश्लेषण का केंद्रीय भंडार |

---

## ⚡ 3-Line Summary
**English:**
1. Each service exclusively owns its data; others use its API or events — no shared tables, no cross-service joins.
2. Get foreign data via API composition, event-fed local copies, CQRS read models, or a CDC-fed warehouse for analytics.
3. Consistency via sagas + outbox + idempotency; start with schema-per-service on shared servers, isolate further as needed.

**Hindi:**
1. हर service अपने डेटा की अकेली मालिक; बाक़ी API या events से लेते हैं — साझा टेबल नहीं।
2. दूसरों का डेटा: API composition, events से local copy, CQRS read model, या analytics के लिए warehouse।
3. Consistency: Saga + Outbox + idempotency; पहले अलग schemas, फिर ज़रूरत पर अलग DB।

---

## ➡️ Next Topic Suggestion
**🎉 Distributed Systems complete!** Next: **100. Observability — Logs** in `05-Observability-Infra/`. With dozens of services, databases and queues, you need to see what's happening. Start with structured logging, correlation IDs, and centralized log search.
