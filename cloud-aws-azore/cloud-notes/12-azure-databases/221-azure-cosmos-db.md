# 221. Azure Cosmos DB (Multi-model NoSQL)
# AWS: DynamoDB (closest; also DocumentDB/Keyspaces for specific APIs)
# Azure: Azure Cosmos DB
# हिंदी में: ग्लोबली डिस्ट्रीब्यूटेड, मैनेज्ड NoSQL डेटाबेस जो कई APIs सपोर्ट करता है

---

## 🔵 Simple Definition (2 lines)
Cosmos DB is a fully managed, globally distributed NoSQL database with single-digit-millisecond reads/writes, automatic indexing and multi-region replication.
हिंदी: Cosmos DB एक मैनेज्ड NoSQL डेटाबेस है जिसे आप कई रीजन में replicate करके तेज़ और हमेशा उपलब्ध रख सकते हैं।

---

## 🔴 Why it Exists (2 lines)
Apps with users worldwide need low latency and high availability without hand-running sharding and replication.
Cosmos handles scaling (RU/s), indexing, and failover for you; you pay for throughput + storage.

---

## 🟢 How it Works
```
App (Node/FastAPI) --SDK--> Account (endpoint + key/AAD)
                              |
                       Database -> Container (partition key /userId)
                              |
          Logical partitions -> Physical partitions (auto-split)
                              |
        Replicas in Region A (write) + Region B, C (read / multi-write)

Every operation costs Request Units (RU). Provisioned RU/s or Serverless.
```

---

## 💻 Code / Config Example
```bash
# Azure CLI (az cosmosdb) - create account, DB, container
az cosmosdb create -n myapp-cosmos -g rg-app \
  --default-consistency-level Session \
  --locations regionName=centralindia failoverPriority=0 isZoneRedundant=False
az cosmosdb sql database create -a myapp-cosmos -g rg-app -n appdb
az cosmosdb sql container create -a myapp-cosmos -g rg-app -d appdb \
  -n orders --partition-key-path /userId --throughput 400
```
```javascript
// Node.js (@azure/cosmos v4)
const { CosmosClient } = require("@azure/cosmos");
const client = new CosmosClient(process.env.COSMOS_CONN_STRING);
const container = client.database("appdb").container("orders");

async function main() {
  await container.items.upsert({ id: "o1", userId: "u42", total: 499 });
  const { resource } = await container.item("o1", "u42").read(); // id + partition key = cheapest read (~1 RU for 1KB)
  console.log(resource);
}
main();
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | DynamoDB | Cosmos DB |
| Capacity unit | RCU/WCU (or on-demand) | RU/s (provisioned, autoscale, serverless) |
| Global replication | Global Tables | Built-in multi-region, multi-write option |
| Consistency | Eventual / strong (per read) | 5 tunable levels |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Cross-partition queries everywhere, and a low-cardinality partition key.
✅ Correct: Choose a high-cardinality key that appears in your most common filters.

❌ Mistake: Using the primary key in the frontend.
✅ Correct: Keep keys in Key Vault or use Entra ID (RBAC) with managed identity.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a Request Unit?
A1: A normalized cost of an operation (CPU, IO, memory). A point read of a 1 KB item is about 1 RU.

Q2: [Medium] Provisioned vs serverless?
A2: Provisioned/autoscale suits steady traffic with SLAs; serverless suits spiky or dev workloads, billed per RU consumed.

Q3: [Hard] You get 429 errors. What do you do?
A3: 429 = RU limit exceeded. Check for a hot partition, raise RU/s or enable autoscale, fix the partition key, add retry with backoff (SDK does by default), and tune the indexing policy to cut write RU.

---

## ✅ Quick Checklist
□ Partition key chosen from the access pattern
□ Consistency level set (default Session)
□ Managed identity / Key Vault instead of raw keys

---

## ⚡ 1-Line Summary
Cosmos DB = global, low-latency NoSQL billed in RU/s | Cosmos DB = ग्लोबल, तेज़ NoSQL जो RU/s के हिसाब से बिल होता है

## ➡️ Next: Cosmos DB APIs (SQL, MongoDB, Cassandra, Gremlin, Table)

---
