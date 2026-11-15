# 115. SQS Long Polling
# AWS: SQS long polling (WaitTimeSeconds)
# Azure: Service Bus receive with timeout (server-wait) / Queue Storage (no long poll)
# हिंदी में: queue खाली हो तो भी request कुछ सेकंड रुककर message का इंतज़ार करती है - कम खर्च, कम खाली calls

---

## 🔵 Simple Definition
With long polling, ReceiveMessage waits up to 20 seconds for a message to arrive instead of returning immediately empty (short polling).
Long polling = इंतज़ार करो, बार-बार मत पूछो।

---

## 🔴 Why it Exists
Short polling hammers SQS with empty responses, costing money and CPU, and may even miss messages on some servers (it samples a subset).

---

## 🟢 How it Works
```
Short poll (Wait=0): ask -> empty -> ask -> empty ... (many billed requests)
Long poll (Wait=20): ask -> held open until message arrives or 20s -> response
Enable: queue attribute ReceiveMessageWaitTimeSeconds (1-20) or per call WaitTimeSeconds.
```

---

## 💻 Code / Config Example
```javascript
// Node.js (AWS SDK v3) worker with long polling
import { SQSClient, ReceiveMessageCommand, DeleteMessageCommand } from "@aws-sdk/client-sqs";

const sqs = new SQSClient({ region: "ap-south-1" });
const QueueUrl = process.env.QUEUE_URL;

async function loop() {
  while (true) {
    const { Messages = [] } = await sqs.send(new ReceiveMessageCommand({
      QueueUrl,
      MaxNumberOfMessages: 10,
      WaitTimeSeconds: 20,          // long polling
    }));
    for (const m of Messages) {
      console.log("job", m.Body);
      await sqs.send(new DeleteMessageCommand({ QueueUrl, ReceiptHandle: m.ReceiptHandle }));
    }
  }
}
loop();
```
```bash
aws sqs set-queue-attributes --queue-url $QUEUE_URL --attributes ReceiveMessageWaitTimeSeconds=20
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Long polling | Yes, up to 20 s | Service Bus: receive wait; Queue Storage: poll with backoff |
| Push alternative | Lambda event source | Functions queue trigger |
| Pricing | Fewer empty requests = cheaper | Per operation |

---

## ⚠️ Common Mistakes
❌ Mistake: Short polling in a tight loop.
✅ Correct: WaitTimeSeconds=20 on queue or request.

❌ Mistake: HTTP client timeout shorter than 20 s.
✅ Correct: Client request timeout > wait time.

---

## ⚫ Interview Q&A
Q1: [Easy] Max long poll wait?
A1: 20 seconds.
Q2: [Medium] Benefit?
A2: Fewer empty responses, lower cost, lower latency.
Q3: [Hard] Short polling with few messages returns empty sometimes - why?
A3: Short polling queries a subset of servers; long polling queries all.

---

## ✅ Quick Checklist
□ Queue attribute set to 20
□ Client timeout > 20 s
□ Delete after processing

---

## ⚡ 1-Line Summary
Long polling waits for messages to cut cost and empty calls | Long polling इंतज़ार करके खर्च और खाली calls घटाता है।

## ➡️ Next: 116. SNS - Complete Guide
