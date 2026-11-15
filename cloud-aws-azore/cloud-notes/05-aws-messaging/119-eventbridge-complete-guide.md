# 119. EventBridge - Complete Guide
# AWS: Amazon EventBridge
# Azure: Azure Event Grid
# हिंदी में: events का central bus - AWS services और आपकी apps के events rules से सही target तक

---

## 🔵 Simple Definition
EventBridge is a serverless event bus: sources put JSON events on a bus, rules match them by pattern and route them to targets (Lambda, SQS, SNS, Step Functions, API destinations...).
Event आया, rule ने पहचाना, target चला।

---

## 🔴 Why it Exists
React to things like "EC2 stopped" or "order created" without polling, and connect SaaS/AWS/custom apps loosely with content-based routing.

---

## 🟢 How it Works
```
Sources: AWS services | your app (PutEvents) | SaaS partners | Scheduler
              |
        [ Event Bus ] default / custom / partner
              |  Rules: event pattern (JSON) or schedule
              v
 Targets: Lambda, SQS, SNS, Step Functions, ECS task, API destination...
 Extras: archive & replay, schema registry, retry + DLQ per target.
```

---

## 💻 Code / Config Example
```python
import boto3, json
events = boto3.client("events", region_name="ap-south-1")

events.create_event_bus(Name="shop")
resp = events.put_events(Entries=[{
    "Source": "shop.orders",
    "DetailType": "OrderCreated",
    "Detail": json.dumps({"orderId": 42, "amount": 999}),
    "EventBusName": "shop",
}])
print(resp["FailedEntryCount"])   # 0 on success
```
```javascript
// Node.js SDK v3
import { EventBridgeClient, PutEventsCommand } from "@aws-sdk/client-eventbridge";
const c = new EventBridgeClient({ region: "ap-south-1" });
await c.send(new PutEventsCommand({ Entries: [{
  Source: "shop.orders", DetailType: "OrderCreated",
  Detail: JSON.stringify({ orderId: 42 }), EventBusName: "shop" }] }));
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Event bus | EventBridge | Event Grid (custom topics / domains) |
| Routing | Rules with patterns | Subscriptions with filters |
| Schedules | EventBridge Scheduler / rules | Logic Apps / Functions timers |
| Pricing | Per million custom events (approximate - check docs) | Per operation (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Expecting ordering or exactly-once.
✅ Correct: At-least-once, unordered; make targets idempotent.

❌ Mistake: Using EventBridge for high-throughput streaming.
✅ Correct: Use Kinesis/Kafka for streams; EventBridge for routing events.

---

## ⚫ Interview Q&A
Q1: [Easy] What does EventBridge do?
A1: Routes events from sources to targets via rules.
Q2: [Medium] EventBridge vs SNS?
A2: EventBridge: rich content filtering, many AWS sources, archive/replay, schema; SNS: higher throughput fan-out and mobile/SMS/email.
Q3: [Hard] Failed target delivery?
A3: Retry policy (time/attempts) then optional SQS DLQ per target.

---

## ✅ Quick Checklist
□ Custom bus for app events
□ Target DLQ and retry policy
□ Idempotent targets

---

## ⚡ 1-Line Summary
EventBridge routes events to targets by pattern | EventBridge pattern देखकर events को सही target तक पहुँचाता है।

## ➡️ Next: 120. EventBridge Rules
