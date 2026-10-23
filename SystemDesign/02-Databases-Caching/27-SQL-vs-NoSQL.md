# 27. SQL vs NoSQL — When to Use
# हिंदी में: SQL या NoSQL — किस स्थिति में कौन-सा डेटाबेस चुनें, इसका फ़ैसला करने का तरीका

---

## 🔵 Simple Definition (English)
Choosing between SQL and NoSQL means matching the database to your **data shape, access patterns, consistency needs, and scale**.
- **SQL** → structured, related data needing transactions, integrity and flexible queries.
- **NoSQL** → huge scale, simple known access patterns, flexible schemas, or special models (graph, key-value, time-series).
In real systems you often use **both**.

## 🔵 सरल परिभाषा (Hindi)
SQL vs NoSQL का फ़ैसला चार चीज़ों पर होता है: डेटा का आकार, query कैसी होगी, consistency कितनी ज़रूरी है, और स्केल कितना है।
रिश्तों और पैसे वाला डेटा → SQL; बहुत बड़ा स्केल और सीधी key-based query → NoSQL। बड़े सिस्टम में दोनों साथ चलते हैं।

---

## 🔴 Problem it Solves
A wrong DB choice is one of the **most expensive mistakes** to fix later:
- Picking MongoDB for a payments ledger → hand-written transaction logic, inconsistent balances.
- Picking Postgres for 1M writes/sec of IoT telemetry → constant scaling pain.
- Picking Cassandra for an admin panel with ad-hoc filters → impossible queries.

Interviewers always ask *"Which database would you use and why?"* You need a **reasoned framework**, not a preference.

## 🔴 यह क्यों बना? (Hindi)
ग़लत DB चुनना बाद में ठीक करना बहुत महँगा पड़ता है — पेमेंट के लिए MongoDB या करोड़ों IoT writes के लिए अकेला Postgres, दोनों मुसीबत।
इंटरव्यू में हमेशा पूछा जाता है "कौन-सा DB और क्यों?" — इसलिए एक साफ़ सोचने का तरीका चाहिए।

---

## 🟢 How it Works — Step by Step

### Decision questions (ask in this order)

```
1. Do I need multi-row/multi-table ACID transactions? (money, inventory, bookings)
      YES → SQL (Postgres/MySQL)  — or distributed SQL if huge (Spanner, CockroachDB, Aurora)

2. Is the data highly relational with many joins / ad-hoc queries / reporting?
      YES → SQL

3. Are access patterns simple & known (get by id, latest N by partition) at HUGE scale
   (100k+ writes/s, TBs–PBs, multi-region always-on)?
      YES → NoSQL: DynamoDB / Cassandra / ScyllaDB

4. Is the schema very flexible / varies per record / nested documents read as a whole?
      YES → Document DB (MongoDB) — or Postgres JSONB if you also need SQL

5. Special shape?
      relationships/traversals → Graph (Neo4j)
      time-series metrics      → TimescaleDB / InfluxDB / ClickHouse
      full-text search         → Elasticsearch / OpenSearch
      vectors / embeddings     → pgvector / Pinecone
      cache / ephemeral        → Redis
      analytics (OLAP)         → ClickHouse / BigQuery / Redshift / Snowflake

6. Team & ops: what does the team know? Managed options? Cost?
```

### Side-by-side comparison

```
┌───────────────────┬──────────────────────────────┬───────────────────────────────┐
│                   │ SQL                          │ NoSQL                         │
├───────────────────┼──────────────────────────────┼───────────────────────────────┤
│ Data model        │ Tables, rows, relations      │ Docs, KV, wide-column, graph  │
│ Schema            │ Fixed (migrations)           │ Flexible / schema-on-read     │
│ Query             │ SQL, joins, ad-hoc           │ By key/partition, limited     │
│ Transactions      │ Full ACID                    │ Often single-item; limited    │
│ Consistency       │ Strong by default            │ Often eventual / tunable      │
│ Scaling           │ Vertical + read replicas;    │ Horizontal built-in           │
│                   │ sharding is hard             │                               │
│ Design approach   │ Model the DATA (normalize)   │ Model the QUERIES (denormalize)│
│ Write throughput  │ High (one primary)           │ Very high (distributed)       │
│ Best for          │ Orders, payments, users,     │ Feeds, chat, IoT, sessions,   │
│                   │ inventory, ERP, reporting    │ catalogs, logs, carts, caches │
└───────────────────┴──────────────────────────────┴───────────────────────────────┘
```

### Common myths

```
❌ "NoSQL is faster"        → For key lookups at huge scale, yes. A well-indexed Postgres
                             query is ~1 ms too. Joins/aggregations are often faster in SQL.
❌ "SQL can't scale"        → Instagram, Shopify, Zerodha, GitHub scale SQL massively
                             (replicas, partitioning, sharding, Vitess/Citus).
❌ "NoSQL = no schema"      → The schema just lives in your application code instead.
                             You still need validation and migrations of data shapes.
❌ "MongoDB has no transactions" → It has had multi-document ACID since v4.0.
```

### Example decisions for real systems

```
System                     Primary choice                 Why
───────────────────────    ─────────────────────────────  ────────────────────────────────────
E-commerce orders/payments Postgres                       ACID, relations, reporting
Product catalog            Postgres JSONB or MongoDB      varied attributes per category
Shopping cart              Redis / DynamoDB               simple key access, fast, TTL
Chat messages (WhatsApp)   Cassandra / ScyllaDB           huge append writes, by conversation
User sessions / OTP        Redis                          ephemeral, TTL, fast
News feed timeline         Redis + Cassandra              precomputed lists per user
Ride location updates      Redis (GEO) + Cassandra        high-frequency writes, geo queries
Social graph               Postgres (small) / Neo4j / TAO many-hop traversals
Search                     Elasticsearch (+ Postgres)     full-text, ranking, filters
Analytics dashboards       ClickHouse / BigQuery          columnar, aggregations over billions
Banking ledger             Postgres / Oracle              double-entry, strict consistency
IoT telemetry              TimescaleDB / Cassandra        time-series, high ingest
```

### Postgres can do a lot of "NoSQL" — start there
```
JSONB + GIN index   → document store
hstore / JSONB      → key-value
pg_trgm / tsvector  → basic full-text search
PostGIS             → geo queries
pgvector            → vector similarity (RAG)
TimescaleDB         → time-series
LISTEN/NOTIFY       → simple pub/sub
→ For most startups: ONE Postgres + Redis covers 90% of needs. Add specialized stores
  only when there's a measured need.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Transaction (पैसे, स्टॉक, बुकिंग) चाहिए? → SQL।
2. बहुत सारे रिश्ते, joins, रिपोर्ट? → SQL।
3. बहुत बड़ा स्केल और सीधी query (id से लाओ, latest 50)? → DynamoDB/Cassandra।
4. हर रिकॉर्ड का आकार अलग (product attributes)? → MongoDB या Postgres JSONB।
5. ख़ास ज़रूरत: search → Elasticsearch, cache → Redis, graph → Neo4j, analytics → ClickHouse। शुरुआत में Postgres + Redis ही काफ़ी है।

---

## 🟡 Real World Example

**Uber** — trips and payments in MySQL (via its Schemaless/Docstore layer). Real-time driver locations live in in-memory, geo-indexed stores. Analytics in Hadoop/Pinot. Every store is matched to its job.

**Flipkart** — orders and payments in MySQL; product catalog in a flexible document/KV store; search in a Solr/Elasticsearch-based system; caching in Redis/Aerospike.

**Netflix** — billing in MySQL/relational (ACID needed). Viewing history and personalization in Cassandra (huge scale, simple access). Netflix moved billing *off* Cassandra back to a relational DB because billing needs transactions. That's a great interview example.

**WhatsApp** — originally Mnesia (Erlang) for message routing, with messages deleted from servers after delivery. The design choice fits the access pattern: "store until delivered".

## 🟡 Real Example Hindi में
Netflix में viewing history Cassandra में है (बहुत बड़ा स्केल), पर billing को Cassandra से वापस SQL पर लाया गया क्योंकि पैसे के लिए transaction ज़रूरी है — इंटरव्यू में यह बढ़िया उदाहरण है।
Flipkart में ऑर्डर MySQL में, catalog लचीले document store में, search Elasticsearch में और cache Redis में।

---

## 🟠 My Stack Example

### Food delivery app — how you'd choose (say this in interviews)
```
PostgreSQL (RDS)
  users, addresses, restaurants, menu_items, orders, order_items, payments, refunds
  → relations + ACID (order + payment + coupon must be consistent)

Redis (ElastiCache)
  sessions, OTP (TTL), cart (hash per user), menu cache, rate limits,
  delivery partner live location (GEOADD / GEOSEARCH), BullMQ job queues

MongoDB (Atlas) — optional
  restaurant CMS content, banners/home-screen config, app event logs

Elasticsearch / OpenSearch
  "biryani near me" full-text + filters + geo + ranking (synced from Postgres via CDC/events)

S3
  images, invoices (PDF)
```

### Postgres JSONB instead of adding MongoDB
```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  price NUMERIC(10,2) NOT NULL,
  attrs JSONB NOT NULL DEFAULT '{}'         -- {"ram":"8GB","color":"black"} varies per category
);
CREATE INDEX idx_products_attrs ON products USING GIN (attrs);

SELECT id, name FROM products
WHERE category = 'phones' AND attrs @> '{"ram": "8GB"}' AND price < 20000;
```

### Redis geo for live driver locations
```js
await redis.geoAdd('drivers:mumbai', { longitude: 72.83, latitude: 19.07, member: 'driver:77' });
const nearby = await redis.geoSearch('drivers:mumbai',
  { longitude: userLng, latitude: userLat }, { radius: 3, unit: 'km' }, { SORT: 'ASC', COUNT: 10 });
```

### Keep stores in sync (don't dual-write blindly)
```
❌ app writes Postgres AND Elasticsearch → one fails → out of sync
✅ app writes Postgres → outbox/CDC (Debezium) → Kafka → indexer → Elasticsearch
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you decide between SQL and NoSQL for a new system?**
A1: Look at the requirements. If I need multi-entity ACID transactions, strong consistency, relational data with joins, or ad-hoc reporting, I choose SQL (usually Postgres). If access patterns are simple and known (key or partition lookups) at very high scale or write throughput, need multi-region always-on availability, or the schema varies widely, I choose an appropriate NoSQL store. I also consider the team's expertise, managed-service options and cost, and I often combine both: SQL as the source of truth and NoSQL for specific high-scale paths.

**Q2: Which database would you use for a chat application's messages? Why?**
A2: A wide-column store like Cassandra or ScyllaDB (or DynamoDB). Writes are append-heavy and enormous in volume, reads are "latest N messages in a conversation" (partition by `conversation_id` plus a time bucket, clustered by message ID), and it needs horizontal scaling and high availability. User accounts and group metadata could stay in Postgres, with Redis for presence and unread counters.

**Q3: Which database for a payment/wallet system? Why?**
A3: A relational database with ACID transactions (Postgres/MySQL), using a double-entry ledger table, constraints (balance ≥ 0), proper isolation or row locks to prevent double spending, idempotency keys, and an audit trail. Correctness beats scale here. When scale demands it, partition or shard by account, or use distributed SQL (Spanner, CockroachDB, Aurora) rather than an eventually consistent store.

**Q4: Can PostgreSQL replace MongoDB?**
A4: In many cases yes. JSONB with GIN indexes supports flexible documents and containment queries, and you keep SQL joins and transactions alongside relational tables. MongoDB still shines when the whole model is document-oriented with deep nesting, when you want built-in horizontal sharding, or when the team prefers its developer experience and Atlas features. For a typical startup, Postgres + JSONB avoids running two databases.

**Q5: What does "design for queries, not data" mean in NoSQL?**
A5: In SQL you normalize the data and rely on joins to answer any query. In NoSQL (Cassandra, DynamoDB) you first list the exact access patterns, then create tables or keys so each query hits one partition, duplicating data across multiple tables if needed (e.g. `messages_by_channel` and `messages_by_user`). Writes do more work (they update several copies) so reads are fast and predictable at scale.

---

## 🔷 Trade-offs
✅ SQL: correctness, flexibility of queries, mature tooling — ❌ harder to scale writes horizontally.
✅ NoSQL: scale, availability, speed for known patterns — ❌ limited queries, denormalization, weaker consistency.
✅ Polyglot (both): best tool per job — ❌ more systems to run, sync, secure and monitor.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Access pattern | How data is read/written | डेटा किस तरह पढ़ा-लिखा जाता है |
| Polyglot persistence | Multiple DB types in one system | कई DB एक साथ |
| Distributed SQL | SQL DB that scales horizontally | कई मशीनों पर फैला SQL DB |
| OLTP | Transactional workloads (orders) | रोज़ के लेन-देन वाला काम |
| OLAP | Analytical workloads (reports) | विश्लेषण/रिपोर्ट वाला काम |
| CDC | Change Data Capture (stream DB changes) | DB बदलावों की स्ट्रीम |
| JSONB | Postgres binary JSON type | Postgres का JSON |
| Denormalization | Duplicating data for fast reads | तेज़ पढ़ने के लिए डेटा दोहराना |

---

## ⚡ 3-Line Summary
**English:**
1. SQL for relational data, transactions, integrity and ad-hoc queries; NoSQL for massive scale with known, simple access patterns or special data shapes.
2. Decide by: transactions? joins? scale? schema variability? special model? team/ops?
3. Start with Postgres + Redis; add specialized stores (Cassandra, Elastic, ClickHouse) when a measured need appears.

**Hindi:**
1. रिश्ते, transaction, रिपोर्ट → SQL; बहुत बड़ा स्केल और सीधी query → NoSQL।
2. फ़ैसला: transaction? joins? स्केल? लचीला schema? ख़ास model? टीम?
3. शुरुआत Postgres + Redis से; ज़रूरत पड़ने पर ही Cassandra, Elasticsearch जोड़ो।

---

## ➡️ Next Topic Suggestion
**28. Database Indexes** — Whichever DB you choose, performance depends on indexes. Next: how B-tree indexes work, why they make queries 1000× faster, and what they cost on writes.
