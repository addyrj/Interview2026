---

# 244. Service Bus Queues + Topics
# AWS: SQS queue / SNS topic (+ SNS filter policies)
# Azure: Service Bus Queue / Topic + Subscription (rules and filters)
# हिंदी में: Queue = एक रिसीवर को मैसेज, Topic = सभी subscribers को कॉपी

---

## 🔵 Simple Definition (2 lines)
A queue gives each message to exactly one consumer; a topic copies each message to every subscription, optionally filtered.
Queue में एक मैसेज एक ही consumer लेता है, Topic में हर subscription को अपनी कॉपी मिलती है।

---

## 🔴 Why it Exists (2 lines)
Work distribution (jobs) and event fan-out (notify many systems) are different needs.
Queues scale workers; topics decouple many independent subscribers.

---

## 🟢 How it Works
```
Order API --> Topic "order-events"
                |-- Sub "billing"    (rule: type = 'paid')      -> billing worker
                |-- Sub "email"      (rule: all)                -> email worker
                |-- Sub "analytics"  (SQL filter: amount > 1000) -> analytics worker
Job API --> Queue "resize-image" -> worker1 | worker2 | worker3 (competing)
```

---

## 💻 Code / Config Example
```bash
# Azure CLI (az servicebus) - namespace, queue, topic, subscription, rule
az servicebus namespace create -g rg-demo -n sb-demo-ns -l centralindia --sku Standard
az servicebus queue create -g rg-demo --namespace-name sb-demo-ns -n resize-image \
  --max-delivery-count 5 --enable-dead-lettering-on-message-expiration true
az servicebus topic create -g rg-demo --namespace-name sb-demo-ns -n order-events
az servicebus topic subscription create -g rg-demo --namespace-name sb-demo-ns \
  --topic-name order-events -n billing
# Replace default rule with SQL filter
az servicebus topic subscription rule create -g rg-demo --namespace-name sb-demo-ns \
  --topic-name order-events --subscription-name billing -n paid-only \
  --filter-sql-expression "type = 'paid'"
```
```python
# FastAPI/worker side: pip install azure-servicebus
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os
with ServiceBusClient.from_connection_string(os.environ["SB_CONN"]) as c:
    with c.get_topic_sender("order-events") as s:
        s.send_messages(ServiceBusMessage('{"id":1}', application_properties={"type": "paid"}))
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Point-to-point | SQS | Queue |
| Fan-out | SNS -> multiple SQS | Topic + subscriptions (one service) |
| Filtering | SNS filter policy (JSON) | SQL / correlation filters |
| Pricing | Per request (approximate - check current docs) | Per tier (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Several services reading the same queue expecting each to get every message.
✅ Correct: Use a topic with one subscription per service.

❌ Mistake: Leaving the default `1=1` rule and adding a filter rule (both match).
✅ Correct: Remove the default rule when you add a specific one.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] When use a topic over a queue?
A1: When multiple independent consumers need the same message.

Q2: [Medium] How is filtering done?
A2: Subscription rules: SQL filters on properties, correlation filters, or boolean true/false filters; applied by the broker.

Q3: [Hard] Cost implications of many subscriptions?
A3: Each subscription holds its own copy and operations, so ingress once but egress/ops multiply; use filters so subscribers get only what they need.

---

## ✅ Quick Checklist
□ Queue for jobs, topic for events
□ Default rule removed where filters used
□ Max delivery count and TTL set

---

## ⚡ 1-Line Summary
Queues load-balance work; topics fan out events | Queue काम बाँटती है, Topic इवेंट सबको भेजता है।

## ➡️ Next: 245. Service Bus vs SQS

---
