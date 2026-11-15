# 118. SNS + SQS Fan-out Pattern
# AWS: SNS topic -> multiple SQS queues
# Azure: Service Bus topic with multiple subscriptions
# हिंदी में: एक event को कई queues में कॉपी करना, हर service अपनी रफ़्तार से प्रोसेस करे

---

## 🔵 Simple Definition
Publish once to an SNS topic; subscribe several SQS queues. Each queue gets its own copy, giving durable, independent processing per service.
एक event, कई स्वतंत्र queues - कोई service धीमी हो तो दूसरों पर असर नहीं।

---

## 🔴 Why it Exists
Plain SNS lacks buffering and retries per consumer; plain SQS can't copy to many consumers. Together they give both.

---

## 🟢 How it Works
```
Order API --Publish--> SNS order-events
                          |-> SQS billing-q   -> billing worker (+ DLQ)
                          |-> SQS shipping-q  -> shipping worker (+ DLQ)
                          '-> SQS analytics-q -> analytics worker
Each queue needs an access policy allowing the topic ARN to SendMessage.
```

---

## 💻 Code / Config Example
```python
import boto3, json
sns = boto3.client("sns", region_name="ap-south-1")
sqs = boto3.client("sqs", region_name="ap-south-1")

topic = sns.create_topic(Name="order-events")["TopicArn"]

def make_queue(name):
    url = sqs.create_queue(QueueName=name)["QueueUrl"]
    arn = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "sns.amazonaws.com"},
            "Action": "sqs:SendMessage",
            "Resource": arn,
            "Condition": {"ArnEquals": {"aws:SourceArn": topic}},
        }],
    }
    sqs.set_queue_attributes(QueueUrl=url, Attributes={"Policy": json.dumps(policy)})
    sns.subscribe(TopicArn=topic, Protocol="sqs", Endpoint=arn,
                  Attributes={"RawMessageDelivery": "true"})
    return url

queues = [make_queue(n) for n in ("billing-q", "shipping-q")]
sns.publish(TopicArn=topic, Message=json.dumps({"orderId": 42}))
for u in queues:
    print(sqs.receive_message(QueueUrl=u).get("Messages", [{}])[0].get("Body"))
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Fan-out | SNS + SQS | Service Bus topic + subscriptions (built-in) |
| Durable per consumer | SQS queue | Subscription |
| Extra setup | Queue access policy | None |
| Pricing | SNS + SQS requests | Service Bus tier |

---

## ⚠️ Common Mistakes
❌ Mistake: Missing queue policy -> messages silently not delivered.
✅ Correct: Allow sns.amazonaws.com with aws:SourceArn condition.

❌ Mistake: Not enabling raw delivery, then double-parsing.
✅ Correct: Raw delivery or unwrap the SNS envelope.

---

## ⚫ Interview Q&A
Q1: [Easy] Why SNS + SQS?
A1: Fan-out with durability and per-consumer retries.
Q2: [Medium] Adding a new consumer later?
A2: Create a queue and subscribe it; publisher unchanged.
Q3: [Hard] Ordered fan-out?
A3: SNS FIFO topic + SQS FIFO queues sharing MessageGroupId semantics.

---

## ✅ Quick Checklist
□ Queue policy for topic
□ DLQ per queue
□ Idempotent workers

---

## ⚡ 1-Line Summary
SNS fans out, SQS buffers each consumer | SNS बाँटता है, SQS हर consumer के लिए buffer रखता है।

## ➡️ Next: 119. EventBridge - Complete Guide
