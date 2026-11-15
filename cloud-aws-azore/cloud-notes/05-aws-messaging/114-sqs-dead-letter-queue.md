# 114. SQS Dead Letter Queue
# AWS: SQS DLQ (RedrivePolicy)
# Azure: Service Bus dead-letter sub-queue
# हिंदी में: बार-बार fail होने वाले message को अलग queue में डालना ताकि बाक़ी काम न रुके

---

## 🔵 Simple Definition
A DLQ is a normal SQS queue that receives messages that exceeded maxReceiveCount on the source queue.
Poison message अलग queue में, जाँच बाद में।

---

## 🔴 Why it Exists
A malformed message that always crashes the worker would loop forever and burn compute. DLQ isolates it for debugging.

---

## 🟢 How it Works
```
Source queue --receive--> fail (not deleted) --> receiveCount++
receiveCount > maxReceiveCount (e.g. 3)  --> moved to DLQ
Alarm on DLQ ApproximateNumberOfMessagesVisible > 0
Fix bug -> "redrive" messages back (console StartMessageMoveTask / API)
FIFO source needs FIFO DLQ; standard needs standard DLQ.
```

---

## 💻 Code / Config Example
```python
import boto3, json
sqs = boto3.client("sqs", region_name="ap-south-1")

dlq_url = sqs.create_queue(QueueName="orders-dlq",
                           Attributes={"MessageRetentionPeriod": "1209600"})["QueueUrl"]  # 14 days
dlq_arn = sqs.get_queue_attributes(QueueUrl=dlq_url,
                                   AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]

sqs.create_queue(
    QueueName="orders",
    Attributes={
        "RedrivePolicy": json.dumps({"deadLetterTargetArn": dlq_arn, "maxReceiveCount": "3"})
    },
)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| DLQ | Separate queue via RedrivePolicy | Automatic sub-queue ($DeadLetterQueue) |
| Max attempts | maxReceiveCount | MaxDeliveryCount |
| Re-drive | StartMessageMoveTask / console | Resubmit via code/tools |
| Pricing | Normal SQS pricing | Included with Service Bus |

---

## ⚠️ Common Mistakes
❌ Mistake: DLQ retention shorter than source -> messages expire before inspection.
✅ Correct: Set DLQ retention to max (14 days).

❌ Mistake: maxReceiveCount = 1 -> transient errors go to DLQ.
✅ Correct: 3-5 with backoff.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a DLQ?
A1: Queue for messages that failed processing too many times.
Q2: [Medium] How do you monitor?
A2: CloudWatch alarm on DLQ visible messages.
Q3: [Hard] Lambda + SQS DLQ gotcha?
A3: Configure the DLQ on the SQS queue (not on the Lambda), and keep source visibility timeout >= function timeout.

---

## ✅ Quick Checklist
□ DLQ attached with sensible maxReceiveCount
□ Alarm on DLQ
□ Redrive runbook

---

## ⚡ 1-Line Summary
DLQ quarantines poison messages | DLQ ख़राब messages को अलग रखता है।

## ➡️ Next: 115. SQS Long Polling
