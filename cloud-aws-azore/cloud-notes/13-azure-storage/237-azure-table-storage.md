# 237. Azure Table Storage
# AWS: DynamoDB (simple key-value usage)
# Azure: Azure Table Storage (Cosmos DB Table API for premium)
# हिंदी में: बहुत सस्ता NoSQL key-value / wide-column स्टोर

---

## 🔵 Simple Definition (2 lines)
Table Storage is a schemaless NoSQL store where each entity is addressed by PartitionKey + RowKey.
हिंदी: साधारण डेटा (logs, user profiles) को बहुत कम कीमत में key से स्टोर करने की जगह।

---

## 🔴 Why it Exists (2 lines)
Not every app needs Cosmos DB's global features or a relational DB.
Table Storage is cheap and scales for key-based lookups.

---

## 🟢 How it Works
```
Storage Account -> Table "events"
  Entity = { PartitionKey, RowKey, ...any properties }
  Point lookup (PK+RowKey) = fastest
  Query within one PartitionKey = efficient
  Full-table scan = slow
No joins, no secondary indexes. Upgrade path: Cosmos DB Table API.
```

---

## 💻 Code / Config Example
```javascript
// Node.js: @azure/data-tables
const { TableClient } = require("@azure/data-tables");

async function demo(connStr) {
  const table = TableClient.fromConnectionString(connStr, "events");
  await table.createTable();

  await table.createEntity({ partitionKey: "user42", rowKey: "evt-001", type: "login", ip: "1.2.3.4" });
  const e = await table.getEntity("user42", "evt-001");
  console.log(e.type);

  for await (const ent of table.listEntities({ queryOptions: { filter: "PartitionKey eq 'user42'" } })) {
    console.log(ent.rowKey);
  }
}
module.exports = { demo };
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | DynamoDB | Table Storage / Cosmos Table API |
| Key | Partition + sort key | PartitionKey + RowKey |
| Secondary indexes | GSI/LSI | None (duplicate data instead) |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Filtering on non-key properties across the whole table.
✅ Correct: Design keys so queries hit PartitionKey (and RowKey).

❌ Mistake: Putting all rows in one partition.
✅ Correct: Spread by user/tenant/date to avoid hot partitions.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What identifies an entity?
A1: PartitionKey + RowKey.

Q2: [Medium] Table Storage vs Cosmos Table API?
A2: Cosmos adds global distribution, secondary indexes, guaranteed latency SLAs at higher cost.

Q3: [Hard] Need sort by time and lookup by user?
A3: Use RowKey as a reverse-timestamp for newest-first within a user partition; denormalize for other access patterns.

---

## ✅ Quick Checklist
□ Keys fit the query
□ Entity size/property limits checked in docs
□ Migration path considered

---

## ⚡ 1-Line Summary
Table Storage = cheap key-value NoSQL | Table Storage = सस्ता key-value NoSQL

## ➡️ Next: Azure Data Lake Storage

---
