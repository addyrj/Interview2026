# 76. DYNAMODB DAX (CACHE)
# AWS: DynamoDB Accelerator (DAX)
# Azure: Cosmos DB integrated cache (dedicated gateway)
# हिंदी में: DAX यानी DynamoDB का इन-मेमोरी कैश

---

## 🔵 Simple Definition (2 lines)
DAX is a managed, DynamoDB-compatible in-memory cache cluster that cuts read latency from milliseconds to microseconds.
हिंदी: DAX DynamoDB के आगे लगा मैनेज्ड इन-मेमोरी कैश है जो रीड को माइक्रोसेकंड में ले आता है।

---

## 🔴 Why it Exists (2 lines)
Read-heavy hot keys (leaderboards, catalog) cost RCUs and still take milliseconds.
DAX serves repeated reads from memory with almost no code changes.

---

## 🟢 How it Works
```
App --DAX client--> DAX cluster (VPC, node cache) --miss--> DynamoDB
 Item cache  : GetItem/BatchGetItem results
 Query cache : Query/Scan results
 Write-through: writes go via DAX to DynamoDB and update the cache
 Cache TTL default about 5 min (configurable). Eventually consistent reads only;
 strongly consistent reads bypass the cache.
```

---

## 💻 Code / Config Example
```bash
# Create a 3-node DAX cluster (AWS CLI v2) - needs an IAM role + subnet group first
aws dax create-subnet-group --subnet-group-name app-dax-subnets \
  --subnet-ids subnet-aaa111 subnet-bbb222

aws dax create-cluster \
  --cluster-name app-dax \
  --node-type dax.t3.small \
  --replication-factor 3 \
  --iam-role-arn arn:aws:iam::123456789012:role/DAXServiceRole \
  --subnet-group app-dax-subnets
```
```javascript
// Node.js: swap the DynamoDB client for the DAX client (amazon-dax-client)
// const AmazonDaxClient = require("amazon-dax-client");
// const dax = new AmazonDaxClient({ endpoints: [process.env.DAX_ENDPOINT], region: "ap-south-1" });
// const doc = new AWS.DynamoDB.DocumentClient({ service: dax });
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Cache | DAX cluster | Cosmos DB integrated cache via dedicated gateway |
| Latency | Microseconds | Low single-digit ms for cached point reads |
| Code change | Use DAX SDK client | Use gateway connection mode |
| Pricing | Hourly per node (approximate - check current docs) | Dedicated gateway nodes hourly (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using DAX for write-heavy or strongly consistent needs.
✅ Correct: DAX shines on read-heavy, eventually consistent access.

❌ Mistake: Using DAX where ElastiCache or app-level cache is enough.
✅ Correct: DAX is DynamoDB-only; use Redis for other data or computed results.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is DAX?
A1: A DynamoDB-specific in-memory cache.

Q2: [Medium] DAX vs ElastiCache Redis?
A2: DAX is drop-in, API-compatible with DynamoDB and caches automatically; Redis is general-purpose and you manage cache logic.

Q3: [Hard] Stale data concerns with DAX?
A3: Item cache TTL controls staleness; writes through DAX update the cache but writes directly to DynamoDB do not, so route all writes via DAX or use short TTLs.

---

## ✅ Quick Checklist
□ Workload read-heavy and repeat reads
□ Cluster has 3+ nodes across AZs
□ All writes go through DAX

---

## ⚡ 1-Line Summary
DAX = microsecond read cache for DynamoDB, almost no code changes. | DAX = DynamoDB के लिए माइक्रोसेकंड रीड कैश, कोड में लगभग कोई बदलाव नहीं।

## ➡️ Next: ElastiCache - Redis + Memcached

---
