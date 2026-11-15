# 117. SNS Topics + Subscriptions
# AWS: SNS topics, subscriptions, filter policies
# Azure: Service Bus topics + subscriptions with filters (rules)
# हिंदी में: Topic = चैनल, Subscription = उस चैनल को सुनने वाला, Filter = सिर्फ़ ज़रूरी message

---

## 🔵 Simple Definition
A topic is a named channel; each subscription binds an endpoint and protocol to it. Filter policies let a subscription receive only matching messages.
हर subscriber को सिर्फ़ अपने काम के message मिलें, यह filter policy तय करती है।

---

## 🔴 Why it Exists
Different consumers care about different events (e.g. billing wants `order.paid`, shipping wants `order.packed`) without separate topics for each.

---

## 🟢 How it Works
```
Publish(type=order.paid)  --> Topic order-events
   Sub A (billing SQS)  filter {"type":["order.paid"]}      -> receives
   Sub B (shipping SQS) filter {"type":["order.packed"]}    -> skipped
   Sub C (audit SQS)    no filter                           -> receives all
Raw message delivery: send payload without SNS JSON envelope (SQS/HTTP).
```

---

## 💻 Code / Config Example
```python
import boto3, json
sns = boto3.client("sns", region_name="ap-south-1")
sqs = boto3.client("sqs", region_name="ap-south-1")

topic = sns.create_topic(Name="order-events")["TopicArn"]
q = sqs.create_queue(QueueName="billing")["QueueUrl"]
q_arn = sqs.get_queue_attributes(QueueUrl=q, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]

sns.subscribe(
    TopicArn=topic, Protocol="sqs", Endpoint=q_arn,
    Attributes={
        "FilterPolicy": json.dumps({"type": ["order.paid"]}),
        "RawMessageDelivery": "true",
    },
)
sns.publish(TopicArn=topic, Message="paid-42",
            MessageAttributes={"type": {"DataType": "String", "StringValue": "order.paid"}})
sns.publish(TopicArn=topic, Message="packed-42",
            MessageAttributes={"type": {"DataType": "String", "StringValue": "order.packed"}})
```
In real AWS the queue also needs a policy allowing `sns.amazonaws.com` to SendMessage (see note 118).

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Topic | SNS topic | Service Bus topic |
| Subscription filter | FilterPolicy (attributes/body) | SQL/correlation rules |
| Protocols | SQS, Lambda, HTTP(S), email, SMS, Firehose, push | Queues-like subscriptions, Functions via triggers |
| Pricing | Pay per publish + delivery | Tier-based |

---

## ⚠️ Common Mistakes
❌ Mistake: Filter on an attribute publisher forgets to set -> nothing delivered.
✅ Correct: Always publish with MessageAttributes (or use payload-based filtering).

❌ Mistake: Wrapped JSON envelope parsed as raw body.
✅ Correct: Enable RawMessageDelivery or unwrap `Message`.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a subscription?
A1: Binding of an endpoint to a topic.
Q2: [Medium] Filter policy scope?
A2: MessageAttributes by default; can be set to MessageBody scope.
Q3: [Hard] Delivery failures?
A3: SNS retries per protocol policy; configure a subscription redrive policy (SQS DLQ) to capture failures.

---

## ✅ Quick Checklist
□ Filter policy per subscription
□ Raw message delivery decided
□ Subscription DLQ

---

## ⚡ 1-Line Summary
Topic broadcasts, filters route per subscriber | Topic बाँटता है, filter हर subscriber का हिस्सा चुनता है।

## ➡️ Next: 118. SNS + SQS Fan-out Pattern
