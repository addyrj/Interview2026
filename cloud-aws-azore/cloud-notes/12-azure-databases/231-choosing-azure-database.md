# 231. Choosing Azure Database
# AWS: RDS / Aurora / DynamoDB / ElastiCache / Redshift
# Azure: Azure SQL / PostgreSQL / MySQL / Cosmos DB / Redis / Synapse
# हिंदी में: वर्कलोड देखकर सही डेटाबेस चुनने की गाइड

---

## 🔵 Simple Definition (2 lines)
Pick the database by data shape and access pattern: relational for transactions, NoSQL for scale and flexible schema, cache for speed, warehouse for analytics.
हिंदी: पहले सवाल पूछें कि डेटा कैसा है और कैसे पढ़ा जाएगा, फिर सर्विस चुनें।

---

## 🔴 Why it Exists (2 lines)
Wrong DB choice causes cost, latency or rewrite later.
A simple decision flow avoids over-engineering.

---

## 🟢 How it Works
```
Need ACID + joins?
  yes -> Postgres (default) / MySQL / Azure SQL (if .NET/SQL Server)
  no  -> Need global scale, flexible JSON, ms latency?
           yes -> Cosmos DB (NoSQL)
           no  -> Simple key-value on a budget? Table Storage / Postgres JSONB
Hot reads / sessions / rate limits?    -> Redis cache in front
Big analytical scans / BI?             -> Synapse / Fabric (+ ADLS)
Files, images, backups?                -> Blob Storage (not a DB)
Messaging/events?                      -> Service Bus / Event Hubs
```

---

## 💻 Code / Config Example
```yaml
# Typical Node.js/FastAPI stack decision (docker-compose style env for the app)
services:
  api:
    image: myapp/api:latest
    environment:
      DATABASE_URL: postgresql://user:pass@myapp-pg.postgres.database.azure.com:5432/appdb?sslmode=require  # system of record
      REDIS_URL: rediss://:key@myapp-redis.redis.cache.windows.net:6380                                      # cache/sessions
      BLOB_ACCOUNT_URL: https://myappstore.blob.core.windows.net                                             # uploads
      # Optional: COSMOS_ENDPOINT for globally distributed, high-write event data
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Relational | RDS / Aurora | Azure SQL / PostgreSQL / MySQL Flexible |
| NoSQL | DynamoDB | Cosmos DB |
| Cache | ElastiCache | Azure Cache for Redis |
| Warehouse | Redshift | Synapse |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Picking Cosmos DB for relational data with many joins.
✅ Correct: Use Postgres; add Cosmos for specific high-scale pieces.

❌ Mistake: Running analytics queries on the production OLTP database.
✅ Correct: Replicate to a read replica or warehouse.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Default choice for a CRUD app?
A1: Managed PostgreSQL (Flexible Server).

Q2: [Medium] When Cosmos over Postgres?
A2: Multi-region low latency, massive horizontal scale, schema-flexible docs, predictable key-based access.

Q3: [Hard] Design for an e-commerce platform.
A3: Postgres for orders/payments (ACID), Redis for cart/session/cache, Cosmos or Postgres JSONB for catalog if global reads matter, Blob for images with CDN, Synapse/Fabric for reporting.

---

## ✅ Quick Checklist
□ Access patterns written down first
□ One system of record per data type
□ Cache and analytics kept off the OLTP path

---

## ⚡ 1-Line Summary
Start with Postgres, add specialized stores when a need is proven | Postgres से शुरू करें, ज़रूरत साबित होने पर ही विशेष स्टोर जोड़ें

## ➡️ Next: Azure Blob Storage

---
