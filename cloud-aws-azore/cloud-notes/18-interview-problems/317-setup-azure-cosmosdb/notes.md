# 317. Setup Azure CosmosDB
# AWS: DynamoDB (closest equivalent)
# Azure: Cosmos DB for NoSQL (serverless or provisioned RU/s)
# हिंदी में: Cosmos DB में डेटाबेस, कंटेनर और पार्टीशन की सेट-अप करना और Node.js से जोड़ना

---

## 🔵 Simple Definition
Cosmos DB is Azure's globally distributed NoSQL database; you pick a partition key and pay in Request Units (RUs).
हिंदी: ग्लोबल NoSQL डेटाबेस; पार्टीशन की चुनो, RU में भुगतान करो।

## 🔴 Why it Exists
Low-latency, elastic JSON storage with turnkey multi-region replication and tunable consistency.

## 🟢 How it Works
```
Account (region(s), consistency) -> Database -> Container (partition key /customerId)
Each operation costs RUs (point read ~1 RU for 1 KB - approximate, check docs)
Logical partitions hashed to physical partitions; hot key = throttling (HTTP 429)
Modes: Serverless (pay per RU used) | Provisioned (manual/autoscale RU/s)
```

## 💻 Code / Config Example
`main.bicep`: serverless account, Session consistency, `shop` database, `orders` container with `/customerId` partition key. `app.js`: create, point read, in-partition query using `@azure/cosmos` (syntax-checked with `node --check`; not run - no emulator/account available).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS DynamoDB | Azure Cosmos DB |
|---------|--------------|-----------------|
| Unit | RCU/WCU or on-demand | RU/s or serverless |
| Partitioning | partition key (+ sort key) | partition key (hierarchical keys possible) |
| Global | Global Tables | built-in multi-region |
| Consistency | eventual / strong | 5 levels (Session default) |
| Pricing | approximate - check current docs | approximate - check current docs |

## 💰 Cost / HA / Security
- Cost: serverless for spiky/dev; provisioned autoscale for steady load. Cross-partition queries burn RUs.
- HA: add regions + automatic failover; zone redundancy for prod.
- Security: disable key auth and use Entra ID RBAC + managed identity; private endpoint; keys never in code.

## ⚠️ Common Mistakes
❌ Low-cardinality partition key (e.g. country).
✅ High-cardinality key that spreads load and appears in most queries.

❌ `SELECT *` cross-partition scans everywhere.
✅ Include partition key in queries; use point reads.

## ⚫ Interview Q&A
Q1 [Easy]: What is a Request Unit?
A1: A normalized cost of an operation (CPU, IO, memory); capacity and billing are in RUs.

Q2 [Medium]: How to choose a partition key?
A2: High cardinality, even distribution of storage and requests, present in common query filters.

Q3 [Hard]: Getting 429s although total RU/s is not exhausted?
A3: A hot logical/physical partition exceeds its share; fix the key design, add synthetic/hierarchical keys, and retry with backoff.

## ✅ Quick Checklist
□ Partition key designed from access patterns
□ Consistency level chosen
□ Keyless (RBAC) auth planned

## ⚡ 1-Line Summary
Cosmos DB = partitioned, RU-priced global NoSQL; key design decides cost. | Cosmos DB = पार्टीशन वाला, RU-आधारित ग्लोबल NoSQL; की डिज़ाइन से खर्च तय।

## ➡️ Next: 318. Write Azure Pipeline
