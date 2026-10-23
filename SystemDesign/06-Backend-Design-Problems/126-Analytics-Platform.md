# 126. Analytics Platform (Event Analytics / Data Platform)
# हिंदी में: Analytics Platform — ऐप और सर्वर से आने वाले अरबों events (clicks, orders, page views) इकट्ठा करना, साफ़ करना, सस्ते में रखना, और dashboards/रिपोर्ट/real-time metrics में बदलना

---

## 🔵 Simple Definition (English)
Design an **analytics platform** that **collects events** from mobile apps, web and backend services (page views, clicks, searches, add-to-cart, orders, errors), **ingests** them at high volume, **validates and enriches** them, stores them cheaply in a **data lake** and queryable **warehouse/OLAP store**, and serves **dashboards, funnels, retention, A/B test results, real-time metrics and ML features**. Examples: Mixpanel/Amplitude/Google Analytics (product analytics), or an internal data platform (Kafka + S3 + Spark + BigQuery/ClickHouse/Snowflake).

## 🔵 सरल परिभाषा (Hindi)
Analytics platform ऐप, वेबसाइट और सर्वर के अरबों events (page view, click, search, cart, order) इकट्ठा करता है, जाँचता और जानकारी जोड़ता है, सस्ते data lake और तेज़ query वाले warehouse में रखता है, और उनसे dashboards, funnels, retention, A/B test नतीजे और real-time metrics बनाता है।

---

## 🔴 Problem it Solves
- Product and business teams need answers: "How many users ordered after seeing the Diwali banner?", "Where do users drop off in checkout?", "Is the new recommendation model better?"
- Production OLTP databases **can't** run heavy analytical queries over billions of rows (they'd slow down the app).
- Data is scattered across services, apps and third-party tools, with **inconsistent definitions** ("what's an active user?").
- Event volumes are huge (billions/day) and costs explode without **columnar storage, partitioning and tiering**.
- Some decisions need **real-time** data (fraud, live ops dashboards during IPL or a sale).

## 🔴 यह क्यों बना? (Hindi)
Business टीम को जवाब चाहिए — "Diwali banner देखकर कितनों ने ऑर्डर किया?", "checkout में लोग कहाँ छोड़ते हैं?", "नया model बेहतर है?"। Production DB पर अरबों rows की भारी queries नहीं चला सकते, डेटा बिखरा है, परिभाषाएँ अलग-अलग, और बिना सही storage के ख़र्च बहुत; कुछ फ़ैसलों (fraud, सेल dashboard) के लिए real-time डेटा।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional: client & server event collection SDKs, schema/tracking plan, ingestion API, validation,
  enrichment (geo, device, user traits), identity stitching (anonymous → logged-in), storage (raw +
  modeled), SQL access, dashboards, funnels/retention/cohorts, A/B experiment analysis, real-time metrics,
  data export to ML/BI, privacy (consent, deletion, PII handling)
Non-functional: ingest 1M events/s peak without data loss, real-time metrics within ~1 min,
  batch tables fresh within hours, queries over billions of rows in seconds, cost-efficient, GDPR/DPDP compliant
```

### 2. Estimation

```
DAU 50M × 200 events/day = 10B events/day ≈ 115k/s avg, peak 500k–1M/s
Event size ~1 KB JSON → 10 TB/day raw; compressed Parquet ~10× smaller → ~1 TB/day in the lake
Retention: raw 2 years in S3 ≈ 700 TB compressed; aggregates small
```

### 3. Architecture (Lambda/Kappa-style hybrid)

```
 📱 RN SDK  🌐 Web SDK  🖥 Backend services (server-side events: orders, payments)
     │ batched, compressed, retried (offline queue)
     ▼
 Collector API (stateless, autoscaled, behind CDN/LB) ── validate schema, add received_at, IP→geo, dedupe id
     ▼
 Kafka (raw-events, partitioned by user/device id; retention 3–7 days = replay buffer)
     ├─────────────────────────────┬───────────────────────────────┬────────────────────────┐
     ▼                             ▼                               ▼                        ▼
 Stream processing (Flink/      Lake loader (Kafka Connect /    Real-time OLAP ingest     Bad/invalid events
 Kafka Streams/Spark Streaming) Firehose) → S3 data lake        (ClickHouse / Druid /     → quarantine topic/DLQ
 - real-time metrics, alerts,     raw zone (Parquet, partitioned  Pinot) → live dashboards
   sessionization, fraud           by date/hour/event_type)
     │                             ▼
     │                       Batch ETL/ELT (Spark / dbt on warehouse): clean, dedupe, identity stitching,
     │                       sessions, facts & dimensions (star schema), metrics layer
     │                             ▼
     │                       Warehouse (BigQuery / Snowflake / Redshift) or lakehouse (Iceberg/Delta + Trino)
     │                             ▼
     └──────────────────────► BI & product analytics (Metabase/Looker/Superset), notebooks, ML feature store
 OLTP DBs ── CDC (Debezium) ──► Kafka ──► lake/warehouse (orders, users as dimension tables)
```

### 4. Event design (tracking plan)

```json
{
  "event_id": "b3a1…uuid",              // dedup
  "event_name": "checkout_started",     // snake_case, verb_object, from a governed catalog
  "event_version": 2,
  "timestamp": "2026-10-18T19:42:11.123Z",   // client time
  "received_at": "…",                   // server time (clock-skew correction)
  "anonymous_id": "dev_7f…", "user_id": "42",
  "session_id": "s_19a…",
  "platform": "android", "app_version": "5.12.0", "os": "14", "device": "Pixel 7",
  "context": { "city": "Mumbai", "network": "4g", "locale": "hi-IN", "utm_source": "insta" },
  "properties": { "cart_value": 450, "items": 3, "coupon": "DIWALI50" }
}
Rules: schema registry/validation; no PII in properties (or hashed); consistent naming; versioning;
       server-side events for money facts (orders/payments) — client events can be lost/blocked.
```

### 5. Storage design

```
Data lake (S3 + Parquet/ORC, table formats Iceberg/Delta/Hudi):
  cheap, durable, columnar, partitioned (dt=2026-10-18/hour=19/event_name=...), schema evolution
Warehouse / lakehouse: SQL for analysts, clustered by date/user; materialized aggregates
Real-time OLAP (ClickHouse/Druid/Pinot): sub-second aggregations on fresh data (last hours/days)
Modeling: raw → staging (cleaned) → marts (fact_orders, fact_events, dim_users, dim_restaurants)
          metrics layer defines "DAU", "conversion" ONCE (dbt metrics / semantic layer)
```

### 6. Key processing problems

```
Late & out-of-order events (offline phones send hours later) → event-time windows + watermarks;
   batch reprocessing of recent partitions
Duplicates (SDK retries) → dedupe by event_id (in stream state or batch DISTINCT)
Identity stitching: anonymous_id → user_id after login (identity graph) to build full funnels
Sessionization: group events by user with 30-min inactivity gap
Bot/fake traffic filtering
Backfills: replay from Kafka (short) or from raw lake (long) when logic changes
Exactly-once metrics for money: compute revenue from server-side order facts (CDC), not client events
```

### 7. Privacy & governance
```
Consent management (track only with consent where required), PII minimization & hashing, access controls
(column/row-level), data retention policies, right-to-erasure pipelines (delete user from lake via
table formats supporting deletes), audit logs; India DPDP Act 2023, GDPR for EU users
```

## 🟢 कैसे काम करता है? (Hindi)
1. ऐप/वेब SDK events को batch करके भेजते हैं (offline हो तो बाद में); collector API जाँचता है, सर्वर का समय और जगह जोड़ता है, Kafka में डालता है।
2. Kafka से तीन रास्ते: stream processing (real-time metrics, fraud), S3 data lake (Parquet, तारीख़ के हिसाब से), real-time OLAP (ClickHouse) dashboards के लिए।
3. Batch ETL (Spark/dbt) डेटा साफ़ करता है, duplicates हटाता है, anonymous → logged-in यूज़र जोड़ता है, sessions बनाता है, और warehouse में fact/dimension tables बनाता है।
4. देर से आए events (offline फ़ोन) के लिए event-time; पैसे वाले आँकड़े server-side order डेटा (CDC) से, client events से नहीं।
5. Tracking plan से events के नाम/ढाँचा तय, PII नहीं, consent और deletion नियम (DPDP/GDPR), "DAU" जैसी परिभाषा एक ही जगह।

---

## 🟡 Real World Example

**Uber** — built a massive data platform: Kafka (trillions of messages per day), Hadoop/HDFS, Apache Hudi (created at Uber for incremental lake updates), Presto/Trino, and Apache Pinot for real-time analytics in user-facing dashboards (e.g. Uber Eats restaurant manager).

**Netflix** — the Keystone pipeline (Kafka plus Flink) processes trillions of events per day into S3 data lakes using Iceberg (created at Netflix), queried with Spark, Trino and Druid.

**Swiggy / Zomato / Flipkart** — event pipelines on Kafka, lakes on S3 or HDFS, Spark ETL, warehouses or lakehouses (Snowflake, Databricks, BigQuery), and real-time dashboards for city ops during peaks. Swiggy has written about its in-house event tracking and data platform.

**Mixpanel / Amplitude / PostHog** — product analytics SaaS that offers funnels, retention and cohorts out of the box. PostHog is open source and self-hostable on ClickHouse.

## 🟡 Real Example Hindi में
Uber ने Kafka, Hudi (Uber ने बनाया), Presto और real-time के लिए Apache Pinot से विशाल data platform बनाया। Netflix का Keystone pipeline (Kafka + Flink) रोज़ खरबों events को Iceberg (Netflix ने बनाया) वाले S3 lake में डालता है।
Swiggy/Zomato/Flipkart Kafka + S3 + Spark + Snowflake/Databricks/BigQuery इस्तेमाल करते हैं; PostHog open-source analytics है जो ClickHouse पर चलता है।

---

## 🟠 My Stack Example

### React Native / web analytics SDK (batch + offline queue + retry)
```ts
const queue: AnalyticsEvent[] = JSON.parse(mmkv.getString('aq') ?? '[]');
export function track(event_name: string, properties: Record<string, unknown> = {}) {
  queue.push({ event_id: uuid.v4(), event_name, event_version: 1, timestamp: new Date().toISOString(),
               anonymous_id: deviceId, user_id: auth.userId ?? null, session_id: session.id(),
               platform: Platform.OS, app_version: appVersion, properties });
  mmkv.set('aq', JSON.stringify(queue.slice(-5000)));                    // persist (cap)
  if (queue.length >= 20) flush();
}
async function flush() {
  if (!queue.length || !(await NetInfo.fetch()).isConnected) return;
  const batch = queue.splice(0, 100);
  try {
    await fetch(`${COLLECTOR}/v1/batch`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ events: batch }) });
    mmkv.set('aq', JSON.stringify(queue));
  } catch { queue.unshift(...batch); }                                     // retry later with backoff
}
setInterval(flush, 30_000); AppState.addEventListener('change', (s) => s === 'background' && flush());
```

### Collector API (Node/Fastify) → Kafka
```js
app.post('/v1/batch', { bodyLimit: 1_000_000 }, async (req, reply) => {
  const now = new Date().toISOString();
  const geo = geoip.lookup(req.ip);
  const valid = [], invalid = [];
  for (const e of req.body.events ?? []) (validateEvent(e) ? valid : invalid).push({ ...e, received_at: now, ip_city: geo?.city });
  await producer.send({ topic: 'raw-events', messages: valid.map((e) => ({ key: e.user_id ?? e.anonymous_id, value: JSON.stringify(e) })) });
  if (invalid.length) await producer.send({ topic: 'invalid-events', messages: invalid.map((e) => ({ value: JSON.stringify(e) })) });
  reply.code(202).send({ accepted: valid.length });                        // ack fast
});
```

### Real-time OLAP: ClickHouse reading from Kafka
```sql
CREATE TABLE events_queue (event_id String, event_name String, timestamp DateTime64(3), user_id Nullable(String),
                           platform LowCardinality(String), properties String)
ENGINE = Kafka SETTINGS kafka_broker_list = 'kafka:9092', kafka_topic_list = 'raw-events',
                        kafka_group_name = 'ch-events', kafka_format = 'JSONEachRow';
CREATE TABLE events (event_id String, event_name LowCardinality(String), ts DateTime64(3), user_id Nullable(String),
                     platform LowCardinality(String), properties String)
ENGINE = ReplacingMergeTree PARTITION BY toYYYYMMDD(ts) ORDER BY (event_name, ts, event_id);   -- dedupe on merge
CREATE MATERIALIZED VIEW events_mv TO events AS SELECT event_id, event_name, timestamp AS ts, user_id, platform, properties FROM events_queue;

-- funnel: home_viewed → menu_viewed → checkout_started → order_placed within 1 hour
SELECT level, count() FROM (
  SELECT user_id, windowFunnel(3600)(ts, event_name = 'home_viewed', event_name = 'menu_viewed',
                                         event_name = 'checkout_started', event_name = 'order_placed') AS level
  FROM events WHERE ts >= now() - INTERVAL 1 DAY GROUP BY user_id) GROUP BY level ORDER BY level;
```

### Batch modeling with dbt (warehouse) — one definition of DAU
```sql
-- models/marts/fct_daily_active_users.sql
select date(ts) as day, count(distinct coalesce(user_id, anonymous_id)) as dau
from {{ ref('stg_events') }}
where event_name in ('app_opened', 'screen_viewed')
group by 1
```

### Revenue from server facts (CDC), not client events
```
Postgres orders ──Debezium──► Kafka ──► lake/warehouse fact_orders (status = DELIVERED) → revenue dashboards
Client "order_placed" events used only for funnel/attribution, never for money totals
```

### Python: experiment analysis (A/B)
```python
df = warehouse.query("SELECT variant, user_id, MAX(converted) c FROM exp_assignments JOIN conversions USING(user_id) WHERE exp='new_home_v2' GROUP BY 1,2")
summary = df.groupby("variant")["c"].agg(["mean", "count"])
# two-proportion z-test / Bayesian analysis → ship if significant and guardrail metrics OK
```

---

## ⚫ Interview Questions + Answers

**Q1: Design an analytics pipeline for billions of app events per day.**
A1: Client and server SDKs batch events (with offline queues and retries) to a stateless collector that validates schemas, enriches events (server timestamp, geo) and writes to Kafka partitioned by user or device. From Kafka: a lake loader writes compressed, partitioned Parquet or Iceberg tables to S3 (the raw zone); stream processors compute real-time metrics and alerts and feed a real-time OLAP store (ClickHouse, Druid, Pinot); batch ELT (Spark or dbt) cleans, dedupes, stitches identities, sessionizes and builds modeled fact and dimension tables in a warehouse or lakehouse for BI, funnels, experiments and ML. Invalid events go to a quarantine topic, and governance covers schemas, PII and retention.

**Q2: How do you handle late, duplicate and out-of-order events?**
A2: Assign each event a unique ID on the client and dedupe in stream state or during batch processing (ReplacingMergeTree, DISTINCT, MERGE). Process by event time, with watermarks and allowed lateness for streaming windows, and reprocess recent batch partitions when late data arrives (e.g. recompute the last 3 days nightly). Store both client and server timestamps to correct clock skew, and design metrics to tolerate small corrections.

**Q3: Data lake vs data warehouse vs real-time OLAP — why all three?**
A3: The data lake (object storage plus open formats) stores everything cheaply and durably and supports reprocessing, ML and schema evolution. The warehouse or lakehouse provides governed, modeled tables with fast SQL for analysts and BI over large history. Real-time OLAP gives sub-second aggregations on fresh data (minutes old) for live dashboards and user-facing analytics. Each optimizes a different cost, latency and flexibility trade-off. Modern lakehouses (Iceberg or Delta plus Trino or Spark) blur the lake–warehouse line.

**Q4: Why compute revenue from backend data instead of client events?**
A4: Client events can be lost (offline, app killed, ad blockers), duplicated (retries), spoofed, or have wrong timestamps, so they're unreliable for financial facts. Orders and payments are authoritative in OLTP databases, so ingest them via CDC into fact tables and use them for revenue, GMV and refunds. Client events remain valuable for behavioural analysis (funnels, engagement, attribution) where small inaccuracies are acceptable.

**Q5: How do you ensure privacy and compliance in an analytics platform?**
A5: Collect minimal data under a governed tracking plan, with no raw PII in event properties (hash or tokenize identifiers where needed). Respect consent (don't track or send without it in regulated regions), encrypt data, apply role-, column- and row-level access controls, set retention policies, and support user deletion requests with tooling that removes or anonymizes a user across the lake and warehouse (table formats with delete support help). Audit access and comply with laws such as India's DPDP Act and GDPR.

---

## 🔷 Trade-offs
✅ Kafka + lake + warehouse + OLAP: scalable, flexible, replayable — ❌ many systems, cost, data engineering effort.
✅ Buy (Mixpanel/Amplitude/PostHog Cloud): fast insights — ❌ cost at scale, less control, data residency concerns.
✅ Real-time metrics: faster decisions — ❌ approximations, complexity vs batch accuracy.
✅ Strict schemas: data quality — ❌ friction for product teams (needs tooling & governance).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event | A tracked user/system action | ट्रैक की गई घटना |
| Tracking plan | Catalog of events & properties | events की तय सूची |
| Collector | API ingesting events | events लेने वाली API |
| Data lake | Cheap raw storage (S3 + Parquet) | सस्ता कच्चा डेटा भंडार |
| Warehouse / lakehouse | Modeled SQL analytics store | विश्लेषण के लिए SQL भंडार |
| OLAP | Analytical query processing | विश्लेषण वाली queries |
| ETL / ELT | Transform pipelines | डेटा बदलने की प्रक्रिया |
| Identity stitching | Linking anonymous & logged-in ids | अनजान और लॉग-इन id जोड़ना |
| Sessionization | Grouping events into sessions | events को sessions में बाँटना |
| Funnel / cohort / retention | Product analytics views | product analytics के तरीके |

---

## ⚡ 3-Line Summary
**English:**
1. SDKs batch events → collector (validate/enrich) → Kafka → stream processing + S3 data lake (Parquet/Iceberg) + real-time OLAP.
2. Batch ELT cleans, dedupes, stitches identities, sessionizes and models facts/dimensions in a warehouse; metrics defined once.
3. Handle late/duplicate events via event ids + event time; revenue from CDC'd backend facts; enforce privacy, consent and retention.

**Hindi:**
1. SDK events → collector → Kafka → stream processing + S3 lake + real-time OLAP।
2. Batch ETL से साफ़, dedup, यूज़र जोड़ना, sessions, warehouse में fact/dimension tables; परिभाषाएँ एक जगह।
3. देर/duplicate events: event id + event time; पैसा backend डेटा से; privacy और consent का पालन।

---

## ➡️ Next Topic Suggestion
**🎉 Backend Design Problems complete!** Next: **F01. Frontend System Design Framework (RADIO)** in `07-Frontend-System-Design/`. You've designed backends; now learn how frontend system design interviews work and how to structure answers for web apps.
