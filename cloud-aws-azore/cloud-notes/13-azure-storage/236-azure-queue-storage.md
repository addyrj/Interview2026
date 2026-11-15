# 236. Azure Queue Storage
# AWS: Amazon SQS
# Azure: Azure Queue Storage (Service Bus for advanced messaging)
# हिंदी में: सरल और सस्ती मैसेज क्यू बैकग्राउंड जॉब्स के लिए

---

## 🔵 Simple Definition (2 lines)
Queue Storage is a simple, cheap queue inside a storage account for decoupling producers and workers (messages up to 64 KB).
हिंदी: एक हिस्सा मैसेज डालता है, दूसरा बाद में उसे प्रोसेस करता है।

---

## 🔴 Why it Exists (2 lines)
Slow work (emails, thumbnails) should not block an HTTP request.
A queue gives buffering and retries for background workers.

---

## 🟢 How it Works
```
API --sendMessage--> [ Queue ] --receiveMessages (hidden for visibilityTimeout)--> Worker
                                  Worker processes -> deleteMessage
                                  If not deleted before timeout -> reappears (dequeueCount++)
Message max ~64 KB, TTL up to 7 days by default (approximate - check docs)
No FIFO / dead-letter built in: use Service Bus for those.
```

---

## 💻 Code / Config Example
```javascript
// Node.js: @azure/storage-queue
const { QueueServiceClient } = require("@azure/storage-queue");

async function demo(connStr) {
  const queue = QueueServiceClient.fromConnectionString(connStr).getQueueClient("emails");
  await queue.createIfNotExists();

  await queue.sendMessage(Buffer.from(JSON.stringify({ to: "a@b.com" })).toString("base64"));

  const res = await queue.receiveMessages({ numberOfMessages: 5, visibilityTimeout: 30 });
  for (const m of res.receivedMessageItems) {
    const job = JSON.parse(Buffer.from(m.messageText, "base64").toString());
    console.log("processing", job, "attempt", m.dequeueCount);
    await queue.deleteMessage(m.messageId, m.popReceipt);   // delete only on success
  }
}
module.exports = { demo };
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Simple queue | SQS Standard | Queue Storage |
| FIFO / DLQ | SQS FIFO, DLQ | Service Bus (sessions, DLQ) |
| Max message | 1 MiB (256 KiB older) - check docs | ~64 KB |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Not making consumers idempotent.
✅ Correct: Expect at-least-once delivery; use dedupe keys.

❌ Mistake: No poison-message handling.
✅ Correct: Check dequeueCount and move to a "poison" queue after N tries.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is visibility timeout?
A1: Time a received message is hidden from other consumers.

Q2: [Medium] Queue Storage vs Service Bus?
A2: Queue Storage is simple and cheap; Service Bus adds FIFO sessions, DLQ, topics, transactions.

Q3: [Hard] Worker crashes mid-job?
A3: Message reappears after timeout and is retried; idempotent handling and dequeueCount limits prevent duplicates and infinite loops.

---

## ✅ Quick Checklist
□ Idempotent consumers
□ Poison queue strategy
□ Base64 encoding consistent with consumers

---

## ⚡ 1-Line Summary
Queue Storage = cheap SQS-like queue | Queue Storage = सस्ती SQS जैसी क्यू

## ➡️ Next: Azure Table Storage

---
