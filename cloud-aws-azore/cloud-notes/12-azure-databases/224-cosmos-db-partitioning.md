# 224. Cosmos DB Partitioning
# AWS: DynamoDB partition key / sort key
# Azure: Cosmos DB logical and physical partitions (partition key)
# हिंदी में: डेटा को partition key के आधार पर बाँटना ताकि स्केल और स्पीड मिले

---

## 🔵 Simple Definition (2 lines)
Each item has a partition key value; items with the same value form a logical partition, which Cosmos places on physical partitions and splits automatically.
हिंदी: सही partition key चुनने से लोड बराबर बँटता है और queries सस्ती रहती हैं।

---

## 🔴 Why it Exists (2 lines)
One machine cannot hold unlimited data or throughput, so data is sharded by key.
A bad key creates hot partitions and 429 errors even when total RU/s is plentiful.

---

## 🟢 How it Works
```
item {id, userId=u42} --hash(userId)--> logical partition "u42"
Logical partition limit: ~20 GB, 10,000 RU/s (approximate - check docs)
Physical partitions hold many logical partitions; RU/s is split evenly among them.

Good key: high cardinality, even access, used in WHERE  -> /userId, /tenantId
Bad key : /country, /status, /date (hot, low cardinality)
Large tenants: hierarchical partition keys (/tenantId, /userId)
```

---

## 💻 Code / Config Example
```bash
az cosmosdb sql container create -a myapp-cosmos -g rg-app -d appdb -n events \
  --partition-key-path /tenantId --throughput 400
```
```javascript
// Always pass the partition key: single-partition query = cheap
const { resources } = await container.items.query(
  {
    query: "SELECT * FROM c WHERE c.tenantId = @t AND c.type = 'order'",
    parameters: [{ name: "@t", value: "acme" }],
  },
  { partitionKey: "acme" }   // avoids fan-out across partitions
).fetchAll();
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Key | Partition + sort key | Partition key (+ id unique within it) |
| Splitting | Automatic | Automatic (physical) |
| Hot key fix | Key design / write sharding | Key design / hierarchical keys |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Partition key = /status or /date.
✅ Correct: Use /userId or /tenantId, or a synthetic key (e.g. userId + month).

❌ Mistake: Expecting to change the key later.
✅ Correct: Key is immutable per container; migrate with the change feed or data migration tool.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a logical partition?
A1: All items sharing one partition key value.

Q2: [Medium] What makes a good key?
A2: High cardinality, even request distribution, and present in most query filters.

Q3: [Hard] One tenant is huge and throttles. Fix?
A3: Use hierarchical partition keys (tenantId, userId) or a synthetic key to spread the tenant, check metrics for the hot partition, and raise autoscale RU/s.

---

## ✅ Quick Checklist
□ Key matches the top queries
□ No logical partition near the ~20 GB limit
□ Normalized RU consumption per partition monitored

---

## ⚡ 1-Line Summary
Pick a high-cardinality key used in filters | ऊँची cardinality वाली और queries में आने वाली key चुनें

## ➡️ Next: Azure Database for PostgreSQL

---
