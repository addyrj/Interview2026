---

# 243. Azure Service Bus
# AWS: Amazon SQS + SNS (and Amazon MQ)
# Azure: Azure Service Bus
# हिंदी में: Service Bus = भरोसेमंद enterprise मैसेज ब्रोकर (queue + topic)

---

## 🔵 Simple Definition (2 lines)
Service Bus is a fully managed message broker for reliable, ordered, transactional messaging between services.
Service Bus सर्विसेज़ के बीच मैसेज सुरक्षित भेजता है, भले ही रिसीवर थोड़ी देर के लिए डाउन हो।

---

## 🔴 Why it Exists (2 lines)
Direct HTTP calls fail when the receiver is slow or down, and you lose data.
A broker decouples sender and receiver, buffers load and retries.

---

## 🟢 How it Works
```
Producer --send--> [ Namespace ]
                    |- Queue  -> one consumer (competing consumers)
                    |- Topic  -> Subscription A (filter) -> consumer A
                               -> Subscription B          -> consumer B
Consumer: receive (peek-lock) -> process -> complete()
          failure -> abandon / lock expires -> retry -> after MaxDeliveryCount -> Dead-letter queue
Tiers: Basic, Standard, Premium (Premium = dedicated, bigger messages, VNet/private endpoints)
```

---

## 💻 Code / Config Example
```javascript
// npm i @azure/service-bus   (Node.js 18+)
const { ServiceBusClient } = require("@azure/service-bus");
const conn = process.env.SERVICEBUS_CONNECTION_STRING; // prefer Managed Identity in prod

async function main() {
  const client = new ServiceBusClient(conn);
  const sender = client.createSender("orders");
  await sender.sendMessages({ body: { orderId: 42 }, messageId: "order-42" });
  await sender.close();

  const receiver = client.createReceiver("orders"); // default peekLock
  const msgs = await receiver.receiveMessages(1, { maxWaitTimeInMs: 5000 });
  for (const m of msgs) {
    console.log("got", m.body);
    await receiver.completeMessage(m); // ack
  }
  await receiver.close();
  await client.close();
}
main().catch(console.error);
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Queue | SQS | Service Bus Queue |
| Pub/Sub | SNS | Service Bus Topic/Subscription |
| Ordering | FIFO queue | Sessions |
| Dead-letter | DLQ via redrive policy | Built-in DLQ sub-queue |
| Pricing | Per request (approximate - check current docs) | Per tier + operations (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using receiveAndDelete mode for important messages.
✅ Correct: Use peek-lock and call complete only after successful processing.

❌ Mistake: Ignoring the dead-letter queue.
✅ Correct: Monitor DLQ length and alert on it.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Queue vs Topic?
A1: Queue delivers each message to one consumer; topic fans out to every subscription.

Q2: [Medium] What is peek-lock?
A2: Message is locked, not deleted; deleted only on complete. If lock expires it becomes available again.

Q3: [Hard] How do you get strict ordering and exactly-once-like behaviour?
A3: Enable sessions for ordered groups and duplicate detection (by MessageId within a time window); make consumers idempotent.

---

## ✅ Quick Checklist
□ Peek-lock mode with explicit complete
□ DLQ monitored, MaxDeliveryCount tuned
□ Managed Identity instead of connection strings

---

## ⚡ 1-Line Summary
Service Bus is Azure's reliable queue plus pub/sub broker | Service Bus Azure का भरोसेमंद queue और pub/sub ब्रोकर है।

## ➡️ Next: 244. Service Bus Queues + Topics

---
