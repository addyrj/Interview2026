# 70. DYNAMODB - COMPLETE GUIDE
# AWS: Amazon DynamoDB
# Azure: Azure Cosmos DB (NoSQL API / Table API)
# हिंदी में: DynamoDB पूरी गाइड

---

## 🔵 Simple Definition (2 lines)
DynamoDB is a fully managed, serverless key-value and document database with single-digit millisecond latency at any scale.
हिंदी: DynamoDB पूरी तरह मैनेज्ड सर्वरलेस की-वैल्यू/डॉक्यूमेंट डेटाबेस है जो किसी भी स्केल पर तेज़ रहता है।

---

## 🔴 Why it Exists (2 lines)
Relational DBs struggle with massive, predictable-key access (sessions, carts, IoT) and need capacity planning.
DynamoDB partitions data automatically, with no servers, patching or joins.

---

## 🟢 How it Works
```
Table -> Items (max 400 KB each) -> Attributes (schemaless except the key)
Primary key = Partition key (hash)  [+ optional Sort key (range)]
Access patterns drive design: Query (by key) is fast, Scan reads everything (slow/costly)
Extras: GSI/LSI, Streams, TTL, DAX, Global Tables, PITR backups
Consistency: eventually consistent (default) or strongly consistent reads
```

---

## 💻 Code / Config Example
```python
# boto3 basic CRUD
import boto3
from boto3.dynamodb.conditions import Key

ddb = boto3.resource("dynamodb", region_name="ap-south-1")
t = ddb.Table("Orders")

t.put_item(Item={"userId": "u1", "orderId": "o-100", "total": 499})
print(t.get_item(Key={"userId": "u1", "orderId": "o-100"}).get("Item"))
print(t.query(KeyConditionExpression=Key("userId").eq("u1"))["Items"])
t.update_item(Key={"userId": "u1", "orderId": "o-100"},
              UpdateExpression="SET #s = :v",
              ExpressionAttributeNames={"#s": "status"},
              ExpressionAttributeValues={":v": "PAID"})
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | DynamoDB | Cosmos DB (NoSQL API) |
| Key | Partition + sort key | Partition key + id |
| Capacity | RCU/WCU or on-demand | RU/s (request units) or serverless |
| Pricing | Per request or provisioned (approximate - check current docs) | Per RU/s (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Designing tables like SQL and using Scan.
✅ Correct: Model for access patterns; use Query with keys and GSIs.

❌ Mistake: Low-cardinality partition key (hot partition).
✅ Correct: Choose a high-cardinality key that spreads traffic.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is DynamoDB?
A1: Serverless NoSQL key-value/document DB with millisecond latency.

Q2: [Medium] Query vs Scan?
A2: Query uses the key to read one partition's matching items; Scan reads the whole table and costs far more.

Q3: [Hard] How do you model orders with "orders by user" and "orders by status"?
A3: Table PK=userId, SK=orderId; add a GSI with PK=status, SK=createdAt for the second pattern.

---

## ✅ Quick Checklist
□ Access patterns listed before schema
□ High-cardinality partition key
□ TTL and PITR considered

---

## ⚡ 1-Line Summary
DynamoDB = serverless, key-driven NoSQL; design around access patterns. | DynamoDB = सर्वरलेस की-आधारित NoSQL; डिज़ाइन एक्सेस पैटर्न के हिसाब से करें।

## ➡️ Next: DynamoDB Tables + Keys

---
