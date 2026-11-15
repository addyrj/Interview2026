---

# 247. Event Hubs vs Kinesis
# AWS: Amazon Kinesis Data Streams
# Azure: Azure Event Hubs
# हिंदी में: दोनों स्ट्रीमिंग सर्विस हैं, scaling और Kafka सपोर्ट में अंतर है

---

## 🔵 Simple Definition (2 lines)
Both ingest ordered, replayable event streams; Kinesis scales with shards, Event Hubs with partitions and throughput/processing units.
दोनों बड़ी इवेंट स्ट्रीम सँभालते हैं, बस scaling का तरीका और सपोर्टेड प्रोटोकॉल अलग हैं।

---

## 🔴 Why it Exists (2 lines)
Choosing between them (or migrating) needs a clear term mapping and limits awareness.
Mismatch leads to throttling or wrong partitioning.

---

## 🟢 How it Works
```
Kinesis:    Stream -> Shards (1 MB/s in, 2 MB/s out each*)  -> KCL / Lambda / Firehose
Event Hubs: Namespace -> Event Hub -> Partitions -> Consumer groups -> Functions / Stream Analytics / Capture
Shard         ~ Partition
Partition key ~ Partition key
Sequence no.  ~ Offset
KCL checkpoint (DynamoDB) ~ EventProcessor checkpoint (Blob)
* approximate - check current docs
```

---

## 💻 Code / Config Example
```python
# Producer side in Python: boto3 vs azure-eventhub
# pip install boto3 azure-eventhub
import json, os

def send_kinesis(stream="clicks"):
    import boto3
    k = boto3.client("kinesis", region_name="ap-south-1")
    k.put_record(StreamName=stream, Data=json.dumps({"page": "/home"}).encode(), PartitionKey="user1")

def send_eventhub(name="clicks"):
    from azure.eventhub import EventHubProducerClient, EventData
    p = EventHubProducerClient.from_connection_string(os.environ["EH_CONN"], eventhub_name=name)
    with p:
        batch = p.create_batch(partition_key="user1")
        batch.add(EventData(json.dumps({"page": "/home"})))
        p.send_batch(batch)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | Kinesis | Event Hubs |
|---------|---------|------------|
| Scale unit | Shard (or on-demand mode) | Partition + TU/PU/CU |
| Retention | 24h default, extended up to 365 days (approximate - check current docs) | 1 day Standard, longer on higher tiers (approximate - check current docs) |
| Kafka API | No (use MSK) | Yes, built-in endpoint |
| Auto-archive | Firehose | Capture |
| Pricing | Shard-hour + PUT units (approximate - check current docs) | Throughput unit-hour + ingress (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Hot partition from a poor key (e.g., constant key).
✅ Correct: Use a high-cardinality partition key.

❌ Mistake: No checkpointing so a restart reprocesses everything.
✅ Correct: Checkpoint to DynamoDB (KCL) or Blob (Event Hubs processor).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Shard equals what in Event Hubs?
A1: Partition.

Q2: [Medium] Which fits an existing Kafka app?
A2: Event Hubs (Kafka endpoint) or MSK; Kinesis needs code changes.

Q3: [Hard] How do you scale consumers?
A3: Max parallel consumers per group is the partition/shard count; add partitions/shards before adding consumers.

---

## ✅ Quick Checklist
□ Partition key avoids hotspots
□ Checkpointing enabled
□ Throttling metrics alarmed

---

## ⚡ 1-Line Summary
Kinesis and Event Hubs are equivalent streams: shard=partition | दोनों समान स्ट्रीम हैं, shard और partition एक जैसे हैं।

## ➡️ Next: 248. Azure Event Grid

---
