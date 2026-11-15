# 74. DYNAMODB GSI + LSI
# AWS: Global Secondary Index / Local Secondary Index
# Azure: Cosmos DB automatic indexing (no explicit secondary-index objects)
# हिंदी में: DynamoDB सेकेंडरी इंडेक्स

---

## 🔵 Simple Definition (2 lines)
Indexes let you query by attributes other than the table key: a GSI has its own partition and sort key; an LSI shares the table's partition key with a different sort key.
हिंदी: इंडेक्स से आप टेबल की के अलावा दूसरे एट्रिब्यूट से क्वेरी कर सकते हैं।

---

## 🔴 Why it Exists (2 lines)
Query needs a key, and one table key supports only one access pattern.
Indexes add more patterns without a Scan.

---

## 🟢 How it Works
```
            GSI                          LSI
Keys        any PK + optional SK         same PK, different SK
Create      anytime                      only at table creation
Consistency eventually consistent only   eventual or strong
Capacity    own RCU/WCU (provisioned)    shares table capacity
Limits      default 20 per table         max 5 per table, 10 GB per partition key
Writes to table are copied to indexes (extra write cost, async for GSI)
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
        {"AttributeName": "status", "AttributeType": "S"},
        {"AttributeName": "createdAt", "AttributeType": "S"},
    ],
    KeySchema=[{"AttributeName": "userId", "KeyType": "HASH"},
               {"AttributeName": "orderId", "KeyType": "RANGE"}],
    GlobalSecondaryIndexes=[{
        "IndexName": "status-createdAt-index",
        "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"},
                      {"AttributeName": "createdAt", "KeyType": "RANGE"}],
        "Projection": {"ProjectionType": "ALL"},
    }],
    BillingMode="PAY_PER_REQUEST",
)
# Query: ddb.query(TableName="Orders", IndexName="status-createdAt-index", ...)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Secondary access | GSI / LSI (explicit) | Automatic indexing of all properties (tunable policy) |
| Extra cost | Index storage + writes | Index adds RU on writes |
| Cross-partition | GSI re-partitions data | Cross-partition queries supported |
| Pricing | Approximate - check current docs | Approximate - check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Planning an LSI after the table exists.
✅ Correct: LSIs can only be defined at creation; use a GSI later.

❌ Mistake: Projecting ALL attributes into every GSI.
✅ Correct: Project only needed attributes to cut storage and write cost.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] GSI or LSI, which can be added later?
A1: GSI.

Q2: [Medium] Can you do a strongly consistent read on a GSI?
A2: No, GSIs are eventually consistent.

Q3: [Hard] Your GSI throttles table writes. Why?
A3: If the GSI lacks write capacity (or has a hot key), back-pressure throttles base-table writes; give it enough capacity and a well-distributed key.

---

## ✅ Quick Checklist
□ Each access pattern has a key or index
□ Projection minimal
□ GSI capacity matches table writes

---

## ⚡ 1-Line Summary
GSI = new keys anytime; LSI = same partition, new sort key, creation-time only. | GSI = कभी भी नई कीज़; LSI = वही पार्टिशन, नई सॉर्ट की, सिर्फ़ टेबल बनाते समय।

## ➡️ Next: DynamoDB Streams

---
