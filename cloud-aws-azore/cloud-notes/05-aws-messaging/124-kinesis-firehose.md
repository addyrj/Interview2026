# 124. Kinesis Firehose
# AWS: Amazon Data Firehose (formerly Kinesis Data Firehose)
# Azure: Event Hubs Capture / Stream Analytics output
# हिंदी में: स्ट्रीम का डेटा बिना कोड के S3/Redshift/OpenSearch में पहुँचाने वाली मैनेज्ड सेवा

---

## 🔵 Simple Definition
Firehose buffers streaming data and delivers it to destinations like S3, Redshift, OpenSearch or HTTP endpoints, with optional Lambda transform.
हिंदी: Firehose स्ट्रीम डेटा को बफर करके S3 जैसी जगहों पर अपने-आप पहुँचाता है।

---

## 🔴 Why it Exists
Writing and scaling your own consumers just to land logs in S3 is repetitive work.

---

## 🟢 How it Works
```
Producers / KDS / CloudWatch Logs
        |
   [ Firehose ] buffer by size OR time (near real time, not real time)
        | (optional) Lambda transform, format convert (Parquet), compress
        v
   S3 / Redshift / OpenSearch / Splunk / HTTP
   Failed records -> S3 error prefix
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation - Firehose to S3 (IAM role and bucket assumed to exist)
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  BucketArn: {Type: String}
  RoleArn: {Type: String}
Resources:
  LogDelivery:
    Type: AWS::KinesisFirehose::DeliveryStream
    Properties:
      DeliveryStreamName: app-logs
      DeliveryStreamType: DirectPut
      ExtendedS3DestinationConfiguration:
        BucketARN: !Ref BucketArn
        RoleARN: !Ref RoleArn
        Prefix: "logs/dt=!{timestamp:yyyy-MM-dd}/"
        ErrorOutputPrefix: "errors/!{firehose:error-output-type}/"
        BufferingHints: {IntervalInSeconds: 300, SizeInMBs: 64}
        CompressionFormat: GZIP
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Data Firehose | Event Hubs Capture (to Blob/ADLS) |
| Transform | Lambda, Parquet conversion | Stream Analytics / Functions |
| Latency | Buffered (seconds to minutes) | Capture window based |
| Pricing | Per GB ingested (approximate - check current docs) | Capture add-on (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Expecting sub-second delivery.
✅ Correct: Firehose is near real time; use KDS + consumer for true real time.

❌ Mistake: Tiny files in S3 from small buffers.
✅ Correct: Raise buffer size/interval, partition prefixes sensibly.

---

## ⚫ Interview Q&A
Q1: [Easy] What does Firehose do?
A1: Loads streaming data into stores like S3 with no consumer code.

Q2: [Medium] Firehose vs KDS?
A2: Firehose: managed delivery, no replay, no shards. KDS: custom consumers, replay, ordering.

Q3: [Hard] How to query logs delivered by Firehose cheaply?
A3: Convert to Parquet, partition by date, query with Athena; keep a failed-record prefix and alarm on delivery errors.

---

## ✅ Quick Checklist
□ Buffer hints set
□ Error output prefix configured
□ Compression/format chosen

---

## ⚡ 1-Line Summary
Firehose = no-code stream delivery to storage | Firehose स्ट्रीम को बिना कोड स्टोरेज में पहुँचाता है।

## ➡️ Next: MSK - Managed Kafka
