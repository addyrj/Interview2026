# 126. Messaging Patterns (SQS vs SNS vs EventBridge vs Kinesis)
# AWS: SQS, SNS, EventBridge, Kinesis
# Azure: Service Bus Queue, Service Bus Topics / Event Grid, Event Hubs
# हिंदी में: कौन सा मैसेजिंग टूल कब चुनें

---

## 🔵 Simple Definition
Queue = one worker takes each message. Pub/Sub = many subscribers get a copy. Event bus = route by rules. Stream = ordered replayable log.
हिंदी: क्यू में हर मैसेज एक वर्कर लेता है, पब/सब में सबको कॉपी मिलती है, स्ट्रीम में रीप्ले हो सकता है।

---

## 🔴 Why it Exists
Choosing the wrong tool causes lost work, over-cost or tight coupling.

---

## 🟢 How it Works
```
SQS         : Producer -> [queue] -> ONE consumer (pull, retry, DLQ)
SNS         : Publisher -> topic -> MANY subscribers (push: SQS, Lambda, HTTP)
EventBridge : Event -> bus -> rules (filter/transform) -> targets
Kinesis     : Producer -> shards -> MANY readers, replay, order per shard

Fan-out pattern: SNS topic -> SQS queue per service (durable + decoupled)
```

---

## 💻 Code / Config Example
```python
# fanout_demo.py - SNS -> SQS fan-out (boto3; runs against moto)
import boto3, json
sns = boto3.client("sns", region_name="us-east-1")
sqs = boto3.client("sqs", region_name="us-east-1")
topic = sns.create_topic(Name="orders")["TopicArn"]
q = sqs.create_queue(QueueName="billing")["QueueUrl"]
qarn = sqs.get_queue_attributes(QueueUrl=q, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
sns.subscribe(TopicArn=topic, Protocol="sqs", Endpoint=qarn)
sns.publish(TopicArn=topic, Message=json.dumps({"orderId": 1}))
print(sqs.receive_message(QueueUrl=q)["Messages"][0]["Body"][:60])
```
In real AWS the queue policy must allow `sns.amazonaws.com` to send messages.

---

## 📊 AWS vs Azure Quick Compare
| Need | AWS | Azure |
|------|-----|-------|
| Work queue | SQS (Standard/FIFO) | Service Bus queue / Storage Queue |
| Pub/Sub fan-out | SNS | Service Bus topic |
| Event routing | EventBridge | Event Grid |
| Streaming | Kinesis / MSK | Event Hubs |

---

## ⚠️ Common Mistakes
❌ Mistake: SNS direct to a slow Lambda/HTTP with no buffer.
✅ Correct: SNS -> SQS -> consumer for durability and retries.

❌ Mistake: Using SQS when many services need the same data with replay.
✅ Correct: Use Kinesis/Kafka.

---

## ⚫ Interview Q&A
Q1: [Easy] SQS vs SNS?
A1: SQS is a pull queue (one consumer per message); SNS is push pub/sub.

Q2: [Medium] When EventBridge over SNS?
A2: Content-based filtering, schemas, SaaS/AWS events, scheduling, archive/replay.

Q3: [Hard] Design order flow for NestJS microservices.
A3: API publishes OrderCreated to SNS/EventBridge; per-service SQS queues with DLQs; idempotent consumers; Kinesis only if analytics needs replay/order.

---

## ✅ Quick Checklist
□ Need replay or order? -> stream
□ DLQ on every queue
□ Consumers idempotent

---

## ⚡ 1-Line Summary
Queue for work, topic for fan-out, bus for routing, stream for replay | काम के लिए क्यू, फैन-आउट के लिए SNS, रूटिंग के लिए EventBridge, रीप्ले के लिए Kinesis।

## ➡️ Next: AWS Security Overview
