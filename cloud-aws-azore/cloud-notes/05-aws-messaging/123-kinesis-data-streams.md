# 123. Kinesis Data Streams
# AWS: Amazon Kinesis Data Streams (KDS)
# Azure: Event Hubs
# हिंदी में: शार्ड-आधारित, क्रमबद्ध और दोबारा पढ़ने योग्य रियल-टाइम स्ट्रीम

---

## 🔵 Simple Definition
KDS stores ordered records in shards; records with the same partition key go to the same shard. Consumers read and can replay within retention.
हिंदी: KDS में रिकॉर्ड शार्ड में क्रम से रखे जाते हैं और रिटेंशन के भीतर दोबारा पढ़े जा सकते हैं।

---

## 🔴 Why it Exists
Multiple consumers need the same ordered event data at low latency, with replay after bugs or new consumers.

---

## 🟢 How it Works
```
put_record(key=user-42) --hash--> Shard 1 [r1 r2 r3 ...] --> Consumer A (Lambda)
put_record(key=user-77) --hash--> Shard 2 [r1 r2 ...]     --> Consumer B (KCL)
Retention: 24h default, extendable (see current docs for max)
Modes: Provisioned (you set shards) | On-demand (auto scale)
Order is guaranteed per shard only.
```

---

## 💻 Code / Config Example
```python
# kds_demo.py - producer and consumer with boto3
import boto3, json
k = boto3.client("kinesis", region_name="ap-south-1")
k.create_stream(StreamName="orders", ShardCount=1)
k.get_waiter("stream_exists").wait(StreamName="orders")

k.put_record(StreamName="orders", PartitionKey="user-42",
             Data=json.dumps({"orderId": 1}).encode())

shard = k.describe_stream(StreamName="orders")["StreamDescription"]["Shards"][0]["ShardId"]
it = k.get_shard_iterator(StreamName="orders", ShardId=shard,
                          ShardIteratorType="TRIM_HORIZON")["ShardIterator"]
for r in k.get_records(ShardIterator=it, Limit=10)["Records"]:
    print(r["PartitionKey"], json.loads(r["Data"]))
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Kinesis Data Streams | Event Hubs |
| Unit of parallelism | Shard | Partition |
| Consumer tracking | KCL checkpoint (DynamoDB) | Consumer group + checkpoint (Blob) |
| Pricing | Per shard-hour/PUT or on-demand (approximate - check current docs) | Throughput/Processing units (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Expecting global ordering.
✅ Correct: Ordering is per shard; use the entity ID as partition key.

❌ Mistake: Many consumers sharing shared read throughput and getting throttled.
✅ Correct: Use enhanced fan-out for dedicated per-consumer throughput.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a shard?
A1: The unit of capacity and ordering in a stream.

Q2: [Medium] How does Lambda consume KDS?
A2: Event source mapping polls each shard, batches records, retries the batch on error (can block the shard) - use bisect-on-error, max retry and an on-failure destination.

Q3: [Hard] Hot shard problem?
A3: Skewed partition keys overload one shard (ProvisionedThroughputExceeded). Fix with better keys, key salting, or shard splitting/on-demand mode.

---

## ✅ Quick Checklist
□ Partition key chosen for even spread
□ Retention matches replay needs
□ Consumers idempotent

---

## ⚡ 1-Line Summary
KDS = ordered, replayable shard-based streams | KDS शार्ड-आधारित क्रमबद्ध और रीप्ले-योग्य स्ट्रीम है।

## ➡️ Next: Kinesis Firehose
