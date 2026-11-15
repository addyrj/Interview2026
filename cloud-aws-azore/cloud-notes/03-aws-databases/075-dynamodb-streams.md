# 75. DYNAMODB STREAMS
# AWS: DynamoDB Streams (+ Lambda trigger)
# Azure: Cosmos DB Change Feed
# हिंदी में: DynamoDB स्ट्रीम्स यानी बदलावों की लाइव फ़ीड

---

## 🔵 Simple Definition (2 lines)
A stream is an ordered, time-limited log (24 hours) of item-level changes (insert, modify, remove) on a table.
हिंदी: स्ट्रीम टेबल में हुए हर बदलाव का क्रमबद्ध लॉग है जो 24 घंटे तक रहता है।

---

## 🔴 Why it Exists (2 lines)
You often must react to data changes: send an email, update search, sync to analytics.
Streams let you do it without polling or dual-writes.

---

## 🟢 How it Works
```
App --> DynamoDB table --> Stream (shards, ordered per item key)
                              |
                         Lambda (event source mapping, batches)
View types: KEYS_ONLY | NEW_IMAGE | OLD_IMAGE | NEW_AND_OLD_IMAGES
Retention 24 h. At-least-once -> make handlers idempotent.
```

---

## 💻 Code / Config Example
```python
# Lambda handler for a DynamoDB stream
import json

def handler(event, context):
    for rec in event["Records"]:
        kind = rec["eventName"]          # INSERT | MODIFY | REMOVE
        new = rec["dynamodb"].get("NewImage")
        print(kind, json.dumps(new))
        # idempotent work: e.g. send "order received" email keyed by orderId
    return {"batchItemFailures": []}
```
```bash
# Enable stream on a table (AWS CLI v2)
aws dynamodb update-table --table-name Orders \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Change log | DynamoDB Streams | Cosmos DB Change Feed |
| Retention | 24 hours | Persistent (as long as the data exists; no deletes shown) |
| Consumer | Lambda / KCL | Azure Functions trigger / Change Feed Processor |
| Pricing | Read requests billed; Lambda reads free-ish (approximate - check current docs) | Uses RU for reads (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Non-idempotent handler, so retries create duplicates.
✅ Correct: Use the item key or event ID as an idempotency key.

❌ Mistake: Poison record blocks the shard.
✅ Correct: Use bisect-on-error, max retry age and an on-failure DLQ.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] How long are stream records kept?
A1: 24 hours.

Q2: [Medium] Ordering guarantee?
A2: Ordered per item (partition key); not globally across the table.

Q3: [Hard] Keep OpenSearch in sync with DynamoDB.
A3: Stream with NEW_IMAGE to Lambda, upsert/delete in OpenSearch idempotently with the item key, DLQ for failures, and a backfill job for initial data.

---

## ✅ Quick Checklist
□ View type chosen
□ Handler idempotent
□ DLQ and alarm on iterator age

---

## ⚡ 1-Line Summary
Streams = 24-hour ordered change log that triggers Lambda. | स्ट्रीम्स = 24 घंटे का क्रमबद्ध चेंज लॉग जो Lambda को ट्रिगर करता है।

## ➡️ Next: DynamoDB DAX (Cache)

---
