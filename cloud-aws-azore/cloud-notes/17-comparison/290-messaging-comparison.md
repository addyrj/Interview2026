# 290. Messaging Comparison
# AWS: SQS, SNS, EventBridge, Kinesis, Amazon MQ
# Azure: Storage Queues / Service Bus, Event Grid, Event Hubs
# हिंदी में: मैसेजिंग सर्विसेज की तुलना

---

## 🔵 Simple Definition
Queues, pub/sub, event routing and streaming exist on both clouds under different names.
हिंदी: कतार, पब/सब, इवेंट रूटिंग और स्ट्रीमिंग दोनों क्लाउड में हैं, नाम अलग हैं।

---

## 🔴 Why it Exists
Decoupling services with async messages absorbs spikes and avoids cascading failures.

---

## 🟢 How it Works
```
Task queue   : SQS            <-> Service Bus queue / Storage Queue
Pub/Sub      : SNS            <-> Service Bus topic / Event Grid
Event routing: EventBridge    <-> Event Grid
Streaming    : Kinesis / MSK  <-> Event Hubs (Kafka-compatible endpoint)
```

---

## 💻 Code / Config Example
```javascript
// Send one message (Node.js)
// AWS: npm i @aws-sdk/client-sqs
const { SQSClient, SendMessageCommand } = require("@aws-sdk/client-sqs");
await new SQSClient({}).send(new SendMessageCommand({
  QueueUrl: process.env.QUEUE_URL, MessageBody: JSON.stringify({ orderId: 1 }) }));

// Azure: npm i @azure/service-bus @azure/identity
const { ServiceBusClient } = require("@azure/service-bus");
const { DefaultAzureCredential } = require("@azure/identity");
const sb = new ServiceBusClient("ns.servicebus.windows.net", new DefaultAzureCredential());
await sb.createSender("orders").sendMessages({ body: { orderId: 1 } });
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Queue | SQS (+ DLQ, FIFO) | Service Bus (DLQ, sessions) |
| Fan-out | SNS | Service Bus topics |
| Events | EventBridge | Event Grid |
| Stream | Kinesis | Event Hubs |
| Delivery | At-least-once (FIFO exactly-once processing) | At-least-once; Service Bus duplicate detection |

---

## ⚠️ Common Mistakes
❌ Mistake: No dead-letter queue or idempotent consumers.
✅ Correct: Configure DLQ and make handlers idempotent.

❌ Mistake: Using Event Grid as a work queue.
✅ Correct: Event Grid notifies; use Service Bus/SQS for work.

---

## ⚫ Interview Q&A
Q1: [Easy] SQS equivalent?
A1: Service Bus queues (or Storage Queues for simple needs).

Q2: [Medium] SNS equivalent?
A2: Service Bus topics/subscriptions, or Event Grid for event fan-out.

Q3: [Hard] Kinesis vs Event Hubs?
A3: Both partitioned streams; Event Hubs also offers a Kafka protocol endpoint and Capture to storage; ordering is per partition on both.

---

## ✅ Quick Checklist
□ DLQ configured
□ Idempotent consumers
□ Right tool: queue vs event vs stream

---

## ⚡ 1-Line Summary
SQS=Service Bus, SNS=Topics/Event Grid, Kinesis=Event Hubs. | SQS=Service Bus, SNS=Topics/Event Grid, Kinesis=Event Hubs।

## ➡️ Next: 291. Security Comparison
