---

# 84. Choosing Right AWS Database
# AWS: RDS / Aurora / DynamoDB / ElastiCache / Neptune / Redshift / Timestream / DocumentDB
# Azure: Azure SQL / PostgreSQL Flexible Server / Cosmos DB / Azure Cache for Redis / Synapse / ADX
# हिंदी में: सही AWS डेटाबेस कैसे चुनें

---

## 🔵 Simple Definition (2 lines)
Pick the database by access pattern, not by habit: relational, key-value, cache, graph, warehouse or time-series.
हिंदी: डेटाबेस अपने डेटा के एक्सेस पैटर्न के हिसाब से चुनें, आदत से नहीं।

---

## 🔴 Why it Exists (2 lines)
One database cannot be best at everything. Wrong choice means slow queries, huge bills or painful migrations later.

---

## 🟢 How it Works
```
Need transactions, JOINs, SQL?         -> RDS / Aurora (PostgreSQL, MySQL)
Single-digit ms at any scale, key access-> DynamoDB
Sub-ms cache / sessions / rate limits   -> ElastiCache (Redis/Valkey)
JSON documents, Mongo API               -> DocumentDB
Multi-hop relationships                 -> Neptune
Big analytics / BI                      -> Redshift
Timestamped metrics / IoT               -> Timestream
Full-text search                        -> OpenSearch
```

---

## 💻 Code / Config Example
```yaml
# Decision matrix kept in repo as architecture doc (docs/db-choice.yml)
workloads:
  - name: orders-api        # NestJS
    pattern: transactional, joins
    choice: Aurora PostgreSQL
  - name: user-sessions
    pattern: key lookup, TTL
    choice: ElastiCache Redis
  - name: product-catalog
    pattern: key-value, huge scale, predictable queries
    choice: DynamoDB
  - name: daily-sales-report
    pattern: aggregate billions of rows
    choice: Redshift
```

---

## 📊 AWS vs Azure Quick Compare
| Need | AWS | Azure |
|------|-----|-------|
| Relational | RDS / Aurora | Azure SQL / PostgreSQL Flexible Server |
| NoSQL key-value/doc | DynamoDB | Cosmos DB (NoSQL API) |
| Cache | ElastiCache | Azure Cache for Redis |
| Graph | Neptune | Cosmos DB Gremlin |
| Warehouse | Redshift | Synapse Analytics |
| Time series | Timestream | Azure Data Explorer |
| Pricing | Varies by service (approximate — check current docs) | Varies by service (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: DynamoDB for ad-hoc queries and reports.
✅ Correct: Design DynamoDB for known access patterns; export to Redshift/Athena for analytics.

❌ Mistake: Running analytics on the production RDS primary.
✅ Correct: Use read replica or warehouse.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] RDS or DynamoDB for a typical CRUD app with relations?
A1: RDS/Aurora, because you need JOINs and transactions.

Q2: [Medium] When is DynamoDB the better choice?
A2: Known key-based access patterns, massive scale, spiky traffic, serverless apps needing predictable low latency.

Q3: [Hard] Design storage for an e-commerce app.
A3: Aurora PostgreSQL for orders/payments, Redis for cart/session cache, DynamoDB for catalog or events at scale, OpenSearch for search, S3 + Redshift/Athena for analytics (polyglot persistence, with CDC to sync).

---

## ✅ Quick Checklist
□ List access patterns first
□ Consistency/transaction needs known
□ Expected scale, latency, and cost estimated

---

## ⚡ 1-Line Summary
Match the database to the access pattern | डेटाबेस को एक्सेस पैटर्न से मिलाकर चुनें।

## ➡️ Next: Lambda — Complete Guide

---
