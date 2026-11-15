# 71. DYNAMODB TABLES + KEYS
# AWS: DynamoDB tables, partition key, sort key
# Azure: Cosmos DB containers, partition key
# हिंदी में: DynamoDB टेबल और कीज़

---

## 🔵 Simple Definition (2 lines)
Every table needs a primary key: either a partition key alone, or a partition key plus a sort key (composite).
हिंदी: हर टेबल में प्राइमरी की ज़रूरी है: सिर्फ़ पार्टिशन की, या पार्टिशन की के साथ सॉर्ट की।

---

## 🔴 Why it Exists (2 lines)
The partition key is hashed to pick the physical partition, so it decides data spread and speed.
The sort key keeps related items together and sorted, enabling range queries.

---

## 🟢 How it Works
```
PK = userId (hash -> partition)      SK = orderId (sorted inside partition)
 u1 | 2026-001 | ...
 u1 | 2026-002 | ...    <- Query(PK=u1, SK begins_with "2026") = one fast read
 u2 | 2026-001 | ...
Key attribute types: String (S), Number (N), Binary (B) only
Same PK+SK = same item (put overwrites)
```

---

## 💻 Code / Config Example
```python
import boto3
ddb = boto3.client("dynamodb", region_name="ap-south-1")
ddb.create_table(
    TableName="Orders",
    AttributeDefinitions=[
        {"AttributeName": "userId", "AttributeType": "S"},
        {"AttributeName": "orderId", "AttributeType": "S"},
    ],
    KeySchema=[
        {"AttributeName": "userId", "KeyType": "HASH"},
        {"AttributeName": "orderId", "KeyType": "RANGE"},
    ],
    BillingMode="PAY_PER_REQUEST",
)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Unit | Table | Container |
| Distribution key | Partition key | Partition key (e.g. /userId) |
| Range key | Sort key | N/A (use id + queries); closest is hierarchical partition keys |
| Pricing | Per request / provisioned (approximate - check current docs) | RU/s (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: PK = status or date (few values, hot partition).
✅ Correct: PK = userId/orderId; put status in a GSI.

❌ Mistake: Trying to change the key later.
✅ Correct: Keys are immutable; plan first or migrate to a new table.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Partition key vs sort key?
A1: Partition key locates the partition; sort key orders items within it.

Q2: [Medium] Why is a hot partition bad?
A2: One key gets too much traffic and gets throttled although the table has spare capacity overall.

Q3: [Hard] Spread writes for a celebrity user with millions of events?
A3: Write sharding: append a suffix (userId#0..N) to the key and query all shards, or use a time-bucketed key.

---

## ✅ Quick Checklist
□ PK high-cardinality
□ SK supports range/begins_with queries
□ Key design reviewed against access patterns

---

## ⚡ 1-Line Summary
Partition key spreads data, sort key orders it; both are immutable. | पार्टिशन की डेटा बाँटती है, सॉर्ट की क्रम देती है; दोनों बाद में बदल नहीं सकते।

## ➡️ Next: DynamoDB Read/Write Capacity

---
