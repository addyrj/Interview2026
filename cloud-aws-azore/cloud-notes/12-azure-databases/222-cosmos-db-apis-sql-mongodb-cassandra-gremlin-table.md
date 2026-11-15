# 222. Cosmos DB APIs (SQL, MongoDB, Cassandra, Gremlin, Table)
# AWS: DynamoDB, DocumentDB, Keyspaces, Neptune (one service per model)
# Azure: Cosmos DB API for NoSQL, MongoDB, Cassandra, Gremlin, Table
# हिंदी में: एक ही Cosmos इंजन पर अलग-अलग डेटा मॉडल के API

---

## 🔵 Simple Definition (2 lines)
Cosmos DB exposes one storage engine through several wire-compatible APIs: NoSQL (native), MongoDB, Cassandra, Gremlin (graph) and Table.
हिंदी: API चुनना मतलब यह तय करना कि आपका ऐप किस भाषा/ड्राइवर से Cosmos से बात करेगा; API बाद में बदली नहीं जा सकती।

---

## 🔴 Why it Exists (2 lines)
Teams already using Mongo, Cassandra or Table Storage can migrate with minimal code change.
New projects get the most features on the native NoSQL API.

---

## 🟢 How it Works
```
Account is created with ONE API (cannot change later)

 NoSQL API   -> JSON docs, SQL-like queries (native, most features)
 MongoDB API -> Mongo drivers (mongoose, pymongo) via connection string
 Cassandra   -> CQL, cassandra drivers
 Gremlin     -> graph (vertices/edges), TinkerPop
 Table       -> key/value, Azure Tables SDK compatible
 (PostgreSQL -> distributed Postgres, Citus-based, separate offering)
```

---

## 💻 Code / Config Example
```bash
# Create accounts for specific APIs
az cosmosdb create -n app-nosql  -g rg-app                       # NoSQL (default)
az cosmosdb create -n app-mongo  -g rg-app --kind MongoDB --server-version 7.0
az cosmosdb create -n app-table  -g rg-app --capabilities EnableTable
az cosmosdb create -n app-cassa  -g rg-app --capabilities EnableCassandra
az cosmosdb create -n app-gremlin -g rg-app --capabilities EnableGremlin
```
```python
# FastAPI/pymongo: same code as MongoDB, only the connection string changes
from pymongo import MongoClient
import os
client = MongoClient(os.environ["COSMOS_MONGO_URI"])  # mongodb://acct:key@acct.mongo.cosmos.azure.com:10255/?ssl=true...
db = client["appdb"]
db.orders.insert_one({"userId": "u42", "total": 499})
print(db.orders.find_one({"userId": "u42"}))
```
```sql
-- NoSQL API query
SELECT c.id, c.total FROM c WHERE c.userId = "u42" AND c.total > 100
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Key-value / doc | DynamoDB | NoSQL / Table API |
| Mongo-compatible | DocumentDB | Cosmos DB for MongoDB (RU or vCore) |
| Cassandra | Keyspaces | Cosmos Cassandra API |
| Graph | Neptune | Gremlin API |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Choosing the Mongo API for a brand-new app and expecting 100% MongoDB feature parity.
✅ Correct: Check compatibility docs; pick native NoSQL for new work, Mongo API for migrations.

❌ Mistake: Assuming you can switch API later.
✅ Correct: API is fixed per account; migrate data to a new account.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which API is the native one?
A1: API for NoSQL (formerly Core/SQL).

Q2: [Medium] When pick the MongoDB API?
A2: Migrating an existing Mongo/NestJS-mongoose app with minimal change and wanting Azure-managed global distribution.

Q3: [Hard] Mongo RU vs vCore model?
A3: RU-based is serverless-style, elastic and billed by RU; vCore is a dedicated-cluster model with more native Mongo behavior and predictable pricing. Choose based on feature compatibility and workload shape.

---

## ✅ Quick Checklist
□ API decided before account creation
□ Driver/version compatibility checked
□ Features you need (transactions, aggregation) verified

---

## ⚡ 1-Line Summary
One Cosmos engine, many APIs; NoSQL is native | एक Cosmos इंजन, कई API; NoSQL नेटिव है

## ➡️ Next: Cosmos DB Consistency Levels

---
