# 112. SQS Standard vs FIFO
# AWS: SQS Standard queue vs SQS FIFO queue
# Azure: Queue Storage (standard-like) vs Service Bus with sessions (ordered)
# हिंदी में: Standard = तेज़ पर क्रम की गारंटी नहीं, FIFO = क्रम और duplicate से बचाव

---

## 🔵 Simple Definition
Standard queues give very high throughput with at-least-once delivery and best-effort ordering. FIFO queues guarantee order per message group and deduplicate within a 5-minute window.
Standard में तेज़ी, FIFO में क्रम (order)।

---

## 🔴 Why it Exists
Some workloads (emails) don't care about order; others (account ledger updates) must apply events in order exactly once.

---

## 🟢 How it Works
```
Standard: producers -> queue -> consumers (many parallel, order may vary, dupes possible)
FIFO:     name must end with .fifo
          MessageGroupId  = ordering lane (same group -> processed in order, one consumer at a time)
          MessageDeduplicationId (or content-based dedup) -> duplicates dropped for 5 min
```

---

## 💻 Code / Config Example
```python
import boto3
sqs = boto3.client("sqs", region_name="ap-south-1")

fifo = sqs.create_queue(
    QueueName="ledger.fifo",
    Attributes={"FifoQueue": "true", "ContentBasedDeduplication": "true"},
)["QueueUrl"]

# Same MessageGroupId (per account) keeps events for that account ordered
for i in range(3):
    sqs.send_message(
        QueueUrl=fifo,
        MessageBody=f"event-{i}",
        MessageGroupId="account-7",
    )

msgs = sqs.receive_message(QueueUrl=fifo, MaxNumberOfMessages=10)["Messages"]
print([m["Body"] for m in msgs])   # event-0, event-1, event-2
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Unordered high throughput | SQS Standard | Queue Storage |
| Ordered | SQS FIFO (message groups) | Service Bus sessions |
| Dedup | 5-minute window | Duplicate detection (configurable) |
| Throughput | FIFO has lower limits, high-throughput mode available (approximate - check docs) | Varies by tier |

---

## ⚠️ Common Mistakes
❌ Mistake: Using one MessageGroupId for everything on FIFO.
✅ Correct: Group per entity (user/account) so groups parallelise.

❌ Mistake: Choosing FIFO "just in case".
✅ Correct: Use Standard + idempotent consumers unless order is required.

---

## ⚫ Interview Q&A
Q1: [Easy] FIFO queue name rule?
A1: Must end with `.fifo`.
Q2: [Medium] What is MessageGroupId?
A2: Ordering key; messages in a group are delivered in order and one in-flight batch per group at a time.
Q3: [Hard] SNS to FIFO queues?
A3: Use SNS FIFO topics with SQS FIFO queues for ordered fan-out; standard topic cannot deliver to FIFO queue.

---

## ✅ Quick Checklist
□ Order really required?
□ Group ID design for parallelism
□ Dedup strategy chosen

---

## ⚡ 1-Line Summary
Standard = scale, FIFO = order + dedup | Standard में scale, FIFO में क्रम और dedup।

## ➡️ Next: 113. SQS Visibility Timeout
