# 111. SQS - Complete Guide
# AWS: Amazon SQS (Simple Queue Service)
# Azure: Azure Queue Storage / Service Bus Queues
# हिंदी में: दो services के बीच message रखने की queue - producer भेजता है, consumer बाद में उठाता है

---

## 🔵 Simple Definition
SQS is a fully managed message queue that decouples producers from consumers; messages are stored until a consumer receives and deletes them.
Queue में message सुरक्षित रहता है, consumer अपनी रफ़्तार से प्रोसेस करता है।

---

## 🔴 Why it Exists
Synchronous calls fail when a downstream service is slow or down. A queue buffers spikes and enables retries.

---

## 🟢 How it Works
```
API (producer) --SendMessage--> [ SQS queue ] <--ReceiveMessage-- Worker (consumer)
                                     |                              |
                       message hidden (visibility timeout)   process -> DeleteMessage
Not deleted in time -> becomes visible again -> retried (-> DLQ after maxReceiveCount)
Retention 1 min..14 days (default 4 days); max message size 256 KiB (check current docs).
```

---

## 💻 Code / Config Example
```python
# Python boto3 - send, receive, delete
import boto3
sqs = boto3.client("sqs", region_name="ap-south-1")
url = sqs.create_queue(QueueName="orders")["QueueUrl"]

sqs.send_message(QueueUrl=url, MessageBody='{"orderId": 42}')

resp = sqs.receive_message(QueueUrl=url, MaxNumberOfMessages=10, WaitTimeSeconds=10)
for m in resp.get("Messages", []):
    print("processing", m["Body"])
    sqs.delete_message(QueueUrl=url, ReceiptHandle=m["ReceiptHandle"])  # ack
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Simple queue | SQS | Queue Storage |
| Rich messaging (ordering, sessions, topics) | SQS FIFO + SNS | Service Bus |
| DLQ | Redrive policy | Built-in on Service Bus |
| Pricing | Per request (first 1M/month free tier, approximate - check docs) | Per operation (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Not deleting messages after processing -> duplicates.
✅ Correct: Delete after success; make consumers idempotent (standard queues are at-least-once).

❌ Mistake: No DLQ, so poison messages loop.
✅ Correct: Attach a DLQ with maxReceiveCount.

---

## ⚫ Interview Q&A
Q1: [Easy] Why use SQS?
A1: Decouple and buffer between services.
Q2: [Medium] Is delivery exactly once?
A2: Standard: at-least-once, possibly out of order; FIFO supports exactly-once processing semantics within dedup window.
Q3: [Hard] Scale workers with queue?
A3: Autoscale on ApproximateNumberOfMessagesVisible per worker (backlog per instance) via CloudWatch.

---

## ✅ Quick Checklist
□ Long polling on
□ DLQ configured
□ Idempotent consumers

---

## ⚡ 1-Line Summary
SQS buffers and decouples work between services | SQS services के बीच काम को buffer और अलग करता है।

## ➡️ Next: 112. SQS Standard vs FIFO
