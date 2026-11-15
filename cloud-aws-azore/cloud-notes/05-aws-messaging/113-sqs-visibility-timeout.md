# 113. SQS Visibility Timeout
# AWS: SQS VisibilityTimeout
# Azure: Service Bus lock duration / Queue Storage visibility timeout
# हिंदी में: message उठाने के बाद कुछ समय तक दूसरों से छुपा रहता है ताकि दो workers एक ही काम न करें

---

## 🔵 Simple Definition
After a consumer receives a message, SQS hides it for the visibility timeout (default 30 s, max 12 h). If not deleted in time, it reappears for another consumer.
Timeout = "इतने समय में काम पूरा करो वरना message फिर दिखेगा"।

---

## 🔴 Why it Exists
SQS can't know if a worker crashed. Hiding then re-exposing gives safe retries without double processing at the same time.

---

## 🟢 How it Works
```
t=0   Worker A receives msg  -> hidden for T seconds
t<T   A finishes -> DeleteMessage  -> gone  (success)
t=T   A not done  -> msg visible again -> Worker B gets it (duplicate work!)
Fix: set T > max processing time, or extend with ChangeMessageVisibility heartbeat.
```

---

## 💻 Code / Config Example
```python
import boto3
sqs = boto3.client("sqs", region_name="ap-south-1")
url = sqs.create_queue(
    QueueName="jobs",
    Attributes={"VisibilityTimeout": "60"},   # queue default
)["QueueUrl"]
sqs.send_message(QueueUrl=url, MessageBody="big-job")

m = sqs.receive_message(QueueUrl=url, VisibilityTimeout=120)["Messages"][0]  # per-receive override

# long job: extend while still working
sqs.change_message_visibility(
    QueueUrl=url, ReceiptHandle=m["ReceiptHandle"], VisibilityTimeout=300
)
sqs.delete_message(QueueUrl=url, ReceiptHandle=m["ReceiptHandle"])
```
Lambda event source rule of thumb: queue visibility timeout at least 6x the function timeout (per AWS guidance).

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Hide-while-processing | Visibility timeout | Service Bus lock duration (peek-lock) |
| Extend | ChangeMessageVisibility | RenewLock |
| Default / max | 30 s / 12 h | Lock default 1 min (check docs) |
| Pricing | No extra cost | No extra cost |

---

## ⚠️ Common Mistakes
❌ Mistake: Default 30 s for a 2-minute job -> duplicate processing.
✅ Correct: Timeout > worst-case runtime, or heartbeat extend.

❌ Mistake: Huge timeout (12 h) so failed messages wait forever to retry.
✅ Correct: Reasonable value plus extension.

---

## ⚫ Interview Q&A
Q1: [Easy] What happens after the timeout?
A1: The message becomes visible again.
Q2: [Medium] How to handle variable job durations?
A2: ChangeMessageVisibility heartbeat.
Q3: [Hard] Why still duplicates with correct timeout?
A3: Standard queues are at-least-once; design idempotent handlers (dedupe key in DB).

---

## ✅ Quick Checklist
□ Timeout > processing time
□ Delete only after success
□ Idempotency key

---

## ⚡ 1-Line Summary
Visibility timeout hides in-flight messages until deleted or expired | Visibility timeout in-process message को छुपाता है जब तक delete या expire न हो।

## ➡️ Next: 114. SQS Dead Letter Queue
