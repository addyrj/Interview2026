---

# 245. Service Bus vs SQS
# AWS: Amazon SQS (Standard / FIFO)
# Azure: Azure Service Bus (also Storage Queues for simple needs)
# हिंदी में: SQS सरल और बेहद scalable है, Service Bus में ज़्यादा enterprise फीचर हैं

---

## 🔵 Simple Definition (2 lines)
SQS is a simple pull-based queue; Service Bus is a richer broker with topics, sessions, transactions and scheduled delivery.
SQS सिर्फ़ queue है, जबकि Service Bus में topic, session और transaction भी मिलते हैं।

---

## 🔴 Why it Exists (2 lines)
Teams moving between clouds must pick the right messaging service and map semantics correctly.
Wrong choice means missing ordering, filtering or retries.

---

## 🟢 How it Works
```
SQS:         send -> receive (visibility timeout) -> delete ; failures -> redrive to DLQ
Service Bus: send -> receive (lock duration)       -> complete; failures -> auto DLQ after MaxDeliveryCount
Visibility timeout  ~  lock duration
maxReceiveCount     ~  MaxDeliveryCount
FIFO MessageGroupId ~  Session ID
```

---

## 💻 Code / Config Example
```javascript
// Same "process then ack" flow in both SDKs
// AWS SDK v3: npm i @aws-sdk/client-sqs
const { SQSClient, ReceiveMessageCommand, DeleteMessageCommand } = require("@aws-sdk/client-sqs");
const sqs = new SQSClient({ region: "ap-south-1" });
async function awsPoll(url) {
  const r = await sqs.send(new ReceiveMessageCommand({ QueueUrl: url, WaitTimeSeconds: 20, MaxNumberOfMessages: 5 }));
  for (const m of r.Messages ?? []) {
    console.log(m.Body);
    await sqs.send(new DeleteMessageCommand({ QueueUrl: url, ReceiptHandle: m.ReceiptHandle })); // ack
  }
}
// Azure: npm i @azure/service-bus
const { ServiceBusClient } = require("@azure/service-bus");
async function azPoll(conn, queue) {
  const rx = new ServiceBusClient(conn).createReceiver(queue);
  for (const m of await rx.receiveMessages(5, { maxWaitTimeInMs: 5000 })) {
    console.log(m.body);
    await rx.completeMessage(m); // ack
  }
}
module.exports = { awsPoll, azPoll };
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS SQS | Azure Service Bus |
|---------|---------|-------------------|
| Pub/Sub | Needs SNS | Built-in topics |
| Ordering | FIFO queue | Sessions |
| Message size | Up to 256 KiB (approximate - check current docs) | 256 KB Standard, larger on Premium (approximate - check current docs) |
| Delay/scheduling | Delay seconds | Scheduled enqueue time |
| Transactions | No | Yes |
| Protocol | HTTPS API | AMQP 1.0 and others |
| Pricing | Per request | Per tier + ops (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming Service Bus queue and SQS behave identically on long polling.
✅ Correct: Service Bus uses AMQP connections; SQS uses long polling requests.

❌ Mistake: Setting visibility/lock shorter than processing time.
✅ Correct: Make it longer than worst-case processing, or renew the lock.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which is simpler and cheaper for a plain queue?
A1: SQS (or Azure Storage Queues on Azure) for basic needs.

Q2: [Medium] Which needs SNS added to match Service Bus topics?
A2: SQS; SNS + SQS gives fan-out that Service Bus topics provide natively.

Q3: [Hard] Migrating SQS FIFO to Service Bus - what maps?
A3: MessageGroupId -> SessionId, deduplication ID -> MessageId with duplicate detection, visibility timeout -> lock duration, redrive -> MaxDeliveryCount DLQ.

---

## ✅ Quick Checklist
□ Mapped timeouts and retry counts
□ Idempotent consumers (both are at-least-once)
□ DLQ alarms in CloudWatch / Azure Monitor

---

## ⚡ 1-Line Summary
SQS is simple and scalable; Service Bus adds topics, sessions, transactions | SQS सरल है, Service Bus ज़्यादा सुविधाओं वाला है।

## ➡️ Next: 246. Azure Event Hubs

---
