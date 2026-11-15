# 116. SNS - Complete Guide
# AWS: Amazon SNS (Simple Notification Service)
# Azure: Service Bus Topics / Event Grid / Notification Hubs
# हिंदी में: एक message publish करो, कई subscribers (SQS, Lambda, email, HTTP) को एक साथ पहुँचे

---

## 🔵 Simple Definition
SNS is a pub/sub service: publishers send to a topic and SNS pushes a copy to every subscriber (SQS, Lambda, HTTP/S, email, SMS, mobile push).
SNS push करता है, SQS में consumer खुद उठाता है - यही बड़ा फ़र्क़ है।

---

## 🔴 Why it Exists
Sending one event to many services by calling each one couples the publisher to all of them. A topic removes that coupling.

---

## 🟢 How it Works
```
Publisher --Publish--> [ SNS Topic ] --push--> SQS queue (billing)
                                     --push--> Lambda (email)
                                     --push--> HTTPS endpoint (webhook)
                                     --push--> Email / SMS
Optional: filter policies per subscription; FIFO topics for ordered fan-out.
```

---

## 💻 Code / Config Example
```python
import boto3
sns = boto3.client("sns", region_name="ap-south-1")

topic_arn = sns.create_topic(Name="order-events")["TopicArn"]
sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint="dev@example.com")  # needs confirmation

sns.publish(
    TopicArn=topic_arn,
    Subject="Order placed",
    Message='{"orderId": 42}',
    MessageAttributes={"type": {"DataType": "String", "StringValue": "order.created"}},
)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Pub/sub topic | SNS | Service Bus Topics / Event Grid |
| Mobile/email/SMS | SNS | Notification Hubs / Communication Services |
| Delivery model | Push | Service Bus: pull; Event Grid: push |
| Pricing | Per million publishes + deliveries (approximate - check docs) | Per operation (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Subscribing HTTP endpoint but never confirming the subscription.
✅ Correct: Handle SubscriptionConfirmation message (visit SubscribeURL).

❌ Mistake: SNS directly to slow consumers without a queue.
✅ Correct: Put SQS between SNS and consumers for buffering/retries.

---

## ⚫ Interview Q&A
Q1: [Easy] SNS vs SQS?
A1: SNS is push pub/sub (one to many); SQS is a pull queue (one consumer group).
Q2: [Medium] Does SNS store messages?
A2: No durable queueing for slow consumers beyond delivery retries; use SQS for durability.
Q3: [Hard] How avoid every subscriber getting every message?
A3: Subscription filter policies on message attributes (or payload).

---

## ✅ Quick Checklist
□ Subscriptions confirmed
□ Filter policies where needed
□ DLQ on subscriptions

---

## ⚡ 1-Line Summary
SNS fans one message out to many subscribers | SNS एक message को कई subscribers तक भेजता है।

## ➡️ Next: 117. SNS Topics + Subscriptions
