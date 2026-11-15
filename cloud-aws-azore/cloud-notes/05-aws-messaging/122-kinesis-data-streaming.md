# 122. Kinesis - Data Streaming
# AWS: Amazon Kinesis (Data Streams, Firehose, Data Analytics/Managed Flink)
# Azure: Event Hubs (+ Stream Analytics)
# हिंदी में: लगातार आने वाले डेटा (क्लिक, लॉग, IoT) को रियल-टाइम में लेना और प्रोसेस करना

---

## 🔵 Simple Definition
Kinesis is the AWS family for ingesting and processing continuous streams of data in real time.
हिंदी: Kinesis AWS की सेवाओं का समूह है जो लगातार बहते डेटा को रियल-टाइम में संभालता है।

---

## 🔴 Why it Exists
Batch jobs are too slow for clickstreams, logs and telemetry. You need ordered, replayable, multi-consumer streams.

---

## 🟢 How it Works
```
Producers --> Kinesis Data Streams (shards) --> Consumers (Lambda, KCL app, Flink)
                      |
                      +--> Firehose --> S3 / Redshift / OpenSearch (no code)
Family:
  Data Streams  = custom real-time processing, replay
  Firehose      = managed delivery to storage (near real time)
  Managed Flink = SQL/Java stream analytics
```

---

## 💻 Code / Config Example
```bash
# Create a stream and send one record (AWS CLI v2)
aws kinesis create-stream --stream-name clicks --shard-count 1
aws kinesis put-record --stream-name clicks \
  --partition-key user-42 --data "$(echo -n '{"page":"/home"}' | base64)"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Stream ingest | Kinesis Data Streams | Event Hubs |
| Managed delivery | Firehose | Event Hubs Capture / Stream Analytics |
| Kafka compatible | MSK (separate) | Event Hubs Kafka endpoint |
| Pricing | Shard-hour or on-demand + data (approximate - check current docs) | Throughput units / PUs (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using SQS for ordered, replayable analytics streams.
✅ Correct: Use Kinesis/Kafka when you need replay and multiple independent consumers.

❌ Mistake: One hot partition key.
✅ Correct: Choose a high-cardinality partition key.

---

## ⚫ Interview Q&A
Q1: [Easy] What is Kinesis used for?
A1: Real-time ingestion and processing of streaming data.

Q2: [Medium] Kinesis Data Streams vs Firehose?
A2: Streams = you write consumers, retention and replay; Firehose = fully managed delivery to S3/Redshift/OpenSearch with buffering.

Q3: [Hard] Kinesis vs Kafka (MSK)?
A3: Kinesis is fully managed with simpler ops and shard model; MSK gives Kafka ecosystem/API compatibility and more tuning but more operational responsibility.

---

## ✅ Quick Checklist
□ Right member of the family chosen
□ Partition key distributes load
□ Consumers handle retries/duplicates

---

## ⚡ 1-Line Summary
Kinesis = real-time data streams on AWS | Kinesis AWS में रियल-टाइम डेटा स्ट्रीम की सेवा है।

## ➡️ Next: Kinesis Data Streams
