# 287. Database Services Comparison
# AWS: RDS, Aurora, DynamoDB, ElastiCache, Redshift
# Azure: Azure SQL / Database for PostgreSQL & MySQL, Cosmos DB, Azure Cache for Redis, Synapse
# हिंदी में: डेटाबेस सर्विसेज की तुलना

---

## 🔵 Simple Definition
Both clouds provide managed relational, NoSQL, cache and warehouse databases with backups, patching and replicas.
हिंदी: दोनों क्लाउड में मैनेज्ड रिलेशनल, NoSQL, कैश और वेयरहाउस डेटाबेस मिलते हैं।

---

## 🔴 Why it Exists
Self-managing Postgres/MySQL on a VM means you own backups, failover and patches.
Managed services trade some control for reliability.

---

## 🟢 How it Works
```
Relational : RDS / Aurora      <->  Azure DB for PostgreSQL/MySQL, Azure SQL
NoSQL      : DynamoDB          <->  Cosmos DB (NoSQL API / Table API)
Cache      : ElastiCache       <->  Azure Cache for Redis
Warehouse  : Redshift          <->  Synapse / Fabric
```

---

## 💻 Code / Config Example
```bash
# Managed PostgreSQL, same intent
aws rds create-db-instance --db-instance-identifier pg1 --engine postgres \
  --db-instance-class db.t3.micro --allocated-storage 20 \
  --master-username app --manage-master-user-password

az postgres flexible-server create -g rg-demo -n pg1-demo \
  --admin-user app --admin-password "$PGPASS" --tier Burstable --sku-name Standard_B1ms
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Postgres/MySQL | RDS / Aurora | Flexible Server |
| Key-value/document | DynamoDB | Cosmos DB |
| Global distribution | DynamoDB Global Tables, Aurora Global | Cosmos DB multi-region writes |
| Pricing | Instance-hours + storage; DynamoDB on-demand/provisioned | Similar; Cosmos uses RU/s (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Public database endpoint with weak rules.
✅ Correct: Private networking (VPC/VNet), security groups/NSGs, TLS.

❌ Mistake: Choosing NoSQL without known access patterns.
✅ Correct: Default to Postgres; use DynamoDB/Cosmos for scale-driven key access.

---

## ⚫ Interview Q&A
Q1: [Easy] DynamoDB equivalent in Azure?
A1: Cosmos DB.

Q2: [Medium] How is Cosmos billed vs DynamoDB?
A2: Cosmos uses Request Units per second (provisioned/serverless/autoscale); DynamoDB uses read/write capacity units or on-demand requests.

Q3: [Hard] How design multi-region DB failover?
A3: Cross-region replicas (Aurora Global / Postgres read replicas, Cosmos multi-region), health-based DNS (Route 53 / Traffic Manager), tested RPO/RTO.

---

## ✅ Quick Checklist
□ Private access only
□ Automated backups tested
□ Right engine for access pattern

---

## ⚡ 1-Line Summary
RDS=Azure DB, DynamoDB=Cosmos DB, ElastiCache=Azure Redis. | RDS=Azure DB, DynamoDB=Cosmos DB, ElastiCache=Azure Redis।

## ➡️ Next: 288. Storage Services Comparison
