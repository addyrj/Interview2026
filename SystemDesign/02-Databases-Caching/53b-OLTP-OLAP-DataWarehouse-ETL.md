# 53b. OLTP vs OLAP — Data Warehouse, Data Lake, ETL/ELT, Batch vs Streaming
# हिंदी में: OLTP बनाम OLAP — Application की DB (transactions) और Analytics की DB (reports) का फ़र्क; Data Warehouse, Data Lake, ETL/ELT, और Batch बनाम Streaming Processing क्या है और कब इस्तेमाल करें

---

## 🔵 Simple Definition (English)
- **OLTP** (Online Transaction Processing) — the database your app writes to every second: `INSERT order`, `UPDATE balance`, `SELECT user`. Optimised for fast, small, concurrent transactions.
- **OLAP** (Online Analytical Processing) — a database optimised for complex queries on large historical data: "total revenue by region for the last 3 years". Optimised for reads over millions of rows.
- **Data Warehouse** — a centralised, structured analytical store built for BI/reporting.
- **Data Lake** — a raw-data store (S3/GCS) that holds everything — structured, semi-structured, unstructured — at low cost.
- **ETL/ELT** — the pipeline that moves data from OLTP → Warehouse/Lake.

## 🔵 सरल परिभाषा (Hindi)
OLTP वो database है जिसमें आपका ऐप हर second में छोटे-छोटे transactions करता है (order बनाना, balance update करना)। OLAP वो database है जो बड़े, जटिल analytics queries के लिए बना है ("पिछले 3 साल में region-wise कुल revenue")। Data Warehouse structured analytics data का घर है; Data Lake सब raw data (JSON, logs, videos, CSV) सस्ते में रखता है; ETL/ELT वो pipeline है जो OLTP से data को Warehouse/Lake में ले जाती है।

---

## 🔴 Problem it Solves
Running analytics on your production OLTP DB causes:
```
Heavy analytics query
     ↓
Locks rows
     ↓
Slows down user-facing writes
     ↓
Latency spikes on your app
```
**Separate OLTP from OLAP** so analytics never touches your production DB.

## 🔴 यह क्यों बना? (Hindi)
Production DB पर analytics query चलाने से rows lock होती हैं, app slow हो जाता है। इसलिए OLAP और Data Warehouse अलग बनाए गए — analytics का load production पर न पड़े।

---

## 🟢 How it Works — Step by Step

### OLTP vs OLAP — Side by Side

```
           OLTP                         OLAP
     ─────────────────           ─────────────────
     MySQL / PostgreSQL           Redshift / BigQuery
     Your app DB                  Analytics / BI DB
     Many small transactions      Few complex queries
     INSERT / UPDATE / DELETE      SELECT aggregations
     Row-oriented storage          Column-oriented storage
     <10ms per query               Minutes for large scans
     Current data                  Historical data
     ACID transactions             Eventual consistency OK
     100s of concurrent users      10s of analysts
```

---

### Column-Oriented Storage (Why OLAP is fast for analytics)

OLTP (row-oriented):
```
Row 1: [order_id=1, user_id=100, amount=500, date=2026-01-01]
Row 2: [order_id=2, user_id=101, amount=300, date=2026-01-02]
```
To SUM amounts → scan all rows, read all columns even if only `amount` is needed.

OLAP (column-oriented):
```
order_id column: [1, 2, 3, 4, ...]
amount column:   [500, 300, 200, 800, ...]   ← stored together
date column:     [2026-01-01, 2026-01-02, ...]
```
`SUM(amount)` → reads only the `amount` column block → very fast for aggregations.

---

### Data Warehouse ⭐⭐⭐⭐⭐

A data warehouse stores **structured, cleaned, transformed** data optimised for analytics.

```
           OLTP DBs
          /    |    \
       MySQL  Mongo  Postgres
          \    |    /
           ETL/ELT
               ↓
        Data Warehouse
       (Redshift / BigQuery)
               ↓
        BI Tools / Dashboards
       (Grafana / QuickSight / Metabase)
```

**Key characteristics:**
- Schema-on-write (data is structured before loading)
- Optimised for complex JOIN + GROUP BY + aggregations
- Usually contains months/years of historical data
- Separate from production — no impact on app latency

**AWS example:**
```
RDS (MySQL/Postgres)
       ↓
AWS DMS (Database Migration Service) or Firehose
       ↓
Amazon Redshift
       ↓
Amazon QuickSight
```

---

### Data Lake ⭐⭐⭐⭐⭐

A data lake stores **raw, unprocessed** data at low cost. Anything goes in.

```
           Sources
          /   |   \
      App  IoT    Logs
      DB   data   JSON
          \  |   /
          S3 Data Lake
        (raw, cheap storage)
          /   |   \
       ETL  ML    Analytics
      jobs  training  Athena
```

**Key characteristics:**
- Schema-on-read (schema applied when querying, not when storing)
- Stores CSV, JSON, Parquet, images, videos, logs — anything
- Very cheap (S3 ~$0.023/GB/month)
- Needs transformation before it's usable for reports

**AWS example:**
```
App events → Kinesis Firehose → S3 (Data Lake)
                                    ↓
                              AWS Glue (catalog)
                                    ↓
                              Amazon Athena (SQL on S3)
```

---

### Data Lake vs Data Warehouse

```
           Data Lake                    Data Warehouse
        ─────────────               ──────────────────
        Raw everything               Structured, curated
        Schema-on-read               Schema-on-write
        S3 / GCS (cheap)             Redshift / BigQuery
        Petabytes                    Terabytes
        For ML, exploration          For BI, dashboards
        Engineers / Data Scientists  Analysts / Business
```

**Modern pattern — Data Lakehouse:**
```
Data Lake (S3) + warehouse-like query engine
(Delta Lake / Apache Iceberg / AWS Lake Formation)
→ best of both worlds
```

---

### ETL vs ELT ⭐⭐⭐⭐⭐

Both move data from source (OLTP) to destination (Warehouse/Lake).

**ETL — Extract, Transform, Load (traditional)**
```
Source DB
    ↓
Extract raw data
    ↓
Transform (clean, join, aggregate) ← happens OUTSIDE the warehouse
    ↓
Load clean data into Warehouse
```

**ELT — Extract, Load, Transform (modern)**
```
Source DB
    ↓
Extract raw data
    ↓
Load raw data into Warehouse/Lake first ← load immediately
    ↓
Transform inside the Warehouse ← using warehouse's compute
(dbt, Spark, SQL)
```

**Why ELT is more popular now:**
- Modern warehouses (BigQuery, Redshift, Snowflake) are powerful and cheap to compute on
- Load first = raw data always available for re-processing
- Transform at query time = flexible
- Tools like **dbt** make ELT easy

**ETL tools:** Apache Spark, Informatica, AWS Glue, Talend
**ELT tools:** dbt, Fivetran, Airbyte, Stitch

---

### Batch vs Streaming Processing ⭐⭐⭐⭐⭐

**Batch processing:** process a large chunk of data at scheduled intervals.

```
Every night at 2 AM:
   ↓
Read 10 million rows from OLTP
   ↓
Transform
   ↓
Load into Warehouse
   ↓
Reports updated by 3 AM
```

Good for: daily reports, monthly billing, ML retraining, non-real-time analytics.

**Streaming processing:** process data continuously, as it arrives.

```
IoT sensor sends temperature
   ↓
Kafka topic
   ↓
Flink / Kafka Streams (process in milliseconds)
   ↓
Alert if temp > 80°C
   ↓
Dashboard updated in real-time
```

Good for: fraud detection, live dashboards, real-time recommendations, IoT alerts.

**Batch vs Streaming:**

```
              Batch                    Streaming
         ───────────               ──────────────
         Periodic (hours/days)     Continuous (ms/sec)
         High throughput           Low latency
         Simpler                   Complex
         Historical analysis       Real-time decisions
         Apache Spark              Kafka Streams / Flink
         AWS Glue                  AWS Kinesis
         Lower cost                Higher ops cost
```

**Lambda Architecture (combining both):**
```
Data
 ├── Batch layer (Spark → Warehouse) → accurate, slow
 └── Speed layer (Kafka → Redis)     → fast, approximate
          ↓
     Serving layer (merge both)
```

---

## 🟢 कैसे काम करता है? (Hindi)
1. OLTP आपके ऐप की database है — छोटे-छोटे transactions, row-oriented, milliseconds में response।
2. OLAP analytics के लिए है — column-oriented storage, बड़ी queries, SUM/GROUP BY/JOIN पर optimised।
3. Data Warehouse में structured, cleaned data आता है जो BI tools को दिखाया जाता है।
4. Data Lake में raw सब कुछ (JSON, logs, CSV, images) सस्ते S3 में रखा जाता है।
5. ETL = पहले transform करो, फिर load करो; ELT = पहले raw load करो, फिर warehouse में transform करो (आज ELT ज़्यादा popular है — dbt जैसे tools से)।
6. Batch = रात को करोड़ों rows process; Streaming = हर event आते ही milliseconds में process (fraud detection, IoT alerts)।

---

## 🟡 Real World Example
- **Swiggy/Zomato:** OLTP (MySQL) stores orders in real-time. Every hour, orders are loaded to Redshift via ETL. Analysts query Redshift for "revenue by city by hour" without touching production DB.
- **Flipkart:** Data Lake on S3 stores raw click events, search logs, purchase events. Spark jobs run nightly to clean and aggregate data into Redshift for BI dashboards.
- **IoT Dashboard:** Temperature sensors push to Kafka → Kafka Streams processes in real-time → Redis stores last-known value → React dashboard shows live readings.

## 🟡 Real Example Hindi में
Swiggy का order OLTP (MySQL) में जाता है real-time में; हर घंटे वो data Redshift (OLAP warehouse) में जाता है — analysts production DB छूते ही नहीं। Flipkart raw click events S3 Data Lake में store करता है; nightly Spark jobs उसे clean करके Redshift में डालते हैं।

---

## 🟠 My Stack Example

### Simple ELT pipeline (Node.js + PostgreSQL + S3 + Athena):
```js
// Step 1: Extract from OLTP (PostgreSQL)
const orders = await db.query(`
  SELECT * FROM orders
  WHERE created_at >= NOW() - INTERVAL '1 hour'
`);

// Step 2: Load raw to S3 (Data Lake)
await s3.putObject({
  Bucket: 'my-data-lake',
  Key: `orders/year=2026/month=10/day=19/hour=14/batch.json`,
  Body: JSON.stringify(orders.rows)
});

// Step 3: Transform in Athena (ELT — transform in warehouse)
// Athena query to aggregate:
// SELECT region, SUM(amount) AS total FROM orders_raw
// WHERE year='2026' AND month='10' GROUP BY region
```

### Streaming with Kafka + FastAPI:
```python
from confluent_kafka import Consumer
import redis

r = redis.Redis.from_url(os.getenv("REDIS_URL"))

consumer = Consumer({'bootstrap.servers': 'kafka:9092',
                     'group.id': 'analytics-group'})
consumer.subscribe(['iot.temperature'])

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    data = json.loads(msg.value())
    # Real-time: update Redis for live dashboard
    r.hset(f"sensor:{data['device_id']}", 'temp', data['temperature'])
    # Alert if threshold exceeded
    if data['temperature'] > 80:
        await send_alert(data['device_id'])
```

---

## ⚫ Interview Questions + Answers

**Q1: Why can't I just run analytics on my production database?**
A1: Analytics queries (heavy JOINs, full-table scans, GROUP BY over millions of rows) lock rows and consume CPU/IO, which directly increases latency for your app's write operations. Separate OLAP systems (Redshift, BigQuery) are designed for this workload and don't affect your production DB.

**Q2: What is the difference between a Data Warehouse and a Data Lake?**
A2: A data warehouse stores structured, cleaned, schema-on-write data optimised for BI and SQL analytics. A data lake stores raw, unprocessed data (any format) at low cost on object storage like S3. Data lakes are good for ML and exploration; warehouses are better for dashboards and reporting. Modern systems often use a "lakehouse" combining both.

**Q3: ETL vs ELT — which is better?**
A3: ELT is generally preferred with modern cloud warehouses (BigQuery, Redshift, Snowflake) because their compute is cheap and powerful. Load raw data first, transform it with SQL (dbt) inside the warehouse. ETL makes sense when you need to clean or mask sensitive data before it touches the warehouse, or when the warehouse compute is expensive.

**Q4: When would you use streaming over batch?**
A4: Use streaming when latency matters — fraud detection (must decide in <100ms), IoT alerts, live dashboards, real-time recommendations. Use batch when you need to process large volumes cheaply and results can wait hours — nightly reports, ML model retraining, monthly billing.

**Q5: What is dbt?**
A5: dbt (data build tool) is an ELT transformation framework. You write SQL models; dbt runs them in order inside your warehouse, manages dependencies, tests data quality, and generates documentation. It's the most popular tool for the "T" step in ELT.

---

## 🔷 Trade-offs
✅ Separate OLTP/OLAP: production DB unaffected — ❌ adds pipeline complexity and data freshness lag.
✅ Data Lake: cheap, flexible, ML-ready — ❌ raw data is hard to query without transformation.
✅ Streaming: real-time decisions — ❌ higher ops cost, harder to reprocess historical data.
✅ Batch: simple, cheap, high throughput — ❌ data is always delayed (hours/days old).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OLTP | Transactional DB for app | ऐप की transaction database |
| OLAP | Analytical DB for reports | analytics/report की database |
| Data Warehouse | Structured analytical store | structured analytics का घर |
| Data Lake | Raw data store (S3) | raw data का सस्ता भंडार |
| ETL | Extract → Transform → Load | पहले transform, फिर load |
| ELT | Extract → Load → Transform | पहले load, फिर warehouse में transform |
| dbt | SQL transformation tool | ELT के लिए SQL framework |
| Batch | Periodic large-data processing | समय-समय पर bulk processing |
| Streaming | Continuous event processing | हर event आते ही processing |
| Lakehouse | Lake + Warehouse hybrid | दोनों का मिश्रण |

---

## ⚡ 3-Line Summary
**English:**
1. OLTP is your app's transactional DB (fast writes, row-oriented); OLAP is your analytics DB (slow complex queries, column-oriented) — never run analytics on OLTP.
2. Data Warehouse = structured, curated, schema-on-write (Redshift/BigQuery); Data Lake = raw everything, schema-on-read, cheap on S3 — modern systems use both (Lakehouse).
3. ETL transforms before loading (traditional); ELT loads raw first, transforms in warehouse (modern — use dbt); Streaming processes events in real-time (Kafka/Flink); Batch processes large chunks periodically.

**Hindi:**
1. OLTP = ऐप की transaction DB (तेज़ writes); OLAP = analytics DB (बड़ी queries) — production DB पर analytics कभी नहीं।
2. Data Warehouse = structured, clean (Redshift); Data Lake = raw सब कुछ, S3 पर सस्ता — आज दोनों साथ (Lakehouse)।
3. ETL = पहले transform; ELT = पहले load, फिर warehouse में transform (dbt); Streaming = real-time; Batch = scheduled bulk।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Data Warehouse vs Data Lake](https://www.youtube.com/results?search_query=data+warehouse+data+lake+ETL+bytebytego) | OLTP vs OLAP, Lambda architecture visuals |
| 📺 YouTube | [ByteByteGo — Batch vs Stream Processing](https://www.youtube.com/results?search_query=batch+vs+stream+processing+system+design+bytebytego) | Spark vs Kafka Streams, when to use each |
| 📝 Article | [dbt docs — What is ELT?](https://docs.getdbt.com/docs/introduction) | Modern ELT pattern: transform inside the warehouse |
| 📝 Article | [Confluent — Streaming vs Batch](https://www.confluent.io/learn/batch-vs-real-time-data-processing/) | Why streaming is replacing batch for modern data stacks |
| 🐙 GitHub | [dbt-labs/jaffle_shop](https://github.com/dbt-labs/jaffle_shop) | Sample dbt ELT project — see real SQL transform models |

---

## ➡️ Next Topic Suggestion
**52-Consistent-Hashing** — how data is distributed when sharding/partitioning at scale.
