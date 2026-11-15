---

# 252. Messaging Pattern Comparison (Azure vs AWS)
# AWS: SQS, SNS, EventBridge, Kinesis, Amazon MQ, AppSync
# Azure: Storage Queues, Service Bus, Event Grid, Event Hubs, SignalR/Web PubSub
# हिंदी में: कौन सा काम किस मैसेजिंग सर्विस से करना है, इसकी गाइड

---

## 🔵 Simple Definition (2 lines)
Pick the messaging service by pattern: job queue, pub/sub, event notification, stream, or real-time push.
पैटर्न देखकर सर्विस चुनें: काम की queue, fan-out, इवेंट, स्ट्रीम या रियल-टाइम।

---

## 🔴 Why it Exists (2 lines)
Using a stream for jobs or a queue for analytics causes pain.
A decision table prevents wrong-tool designs.

---

## 🟢 How it Works
```
Need                         AWS               Azure
---------------------------  ----------------  ---------------------------
Simple job queue             SQS               Storage Queue / Service Bus Queue
Fan-out pub/sub (reliable)   SNS + SQS         Service Bus Topic
Event routing / reactions    EventBridge       Event Grid
High-volume stream, replay   Kinesis / MSK     Event Hubs
Ordered, transactional       SQS FIFO          Service Bus sessions
Realtime to browser          API GW WebSocket  SignalR / Web PubSub
Mobile push                  SNS Mobile        Notification Hubs
Managed RabbitMQ/ActiveMQ    Amazon MQ         (run on AKS/VM; Service Bus AMQP)
```

---

## 💻 Code / Config Example
```javascript
// Tiny decision helper you can paste into a design doc / ADR tool
function pick({ replay, fanout, order, realtime, volume }) {
  if (realtime) return { aws: "API GW WebSocket", azure: "SignalR/Web PubSub" };
  if (replay || volume === "high") return { aws: "Kinesis/MSK", azure: "Event Hubs" };
  if (fanout && order) return { aws: "SNS FIFO + SQS FIFO", azure: "Service Bus Topic + sessions" };
  if (fanout) return { aws: "SNS+SQS or EventBridge", azure: "Service Bus Topic or Event Grid" };
  return { aws: "SQS", azure: "Service Bus Queue / Storage Queue" };
}
console.log(pick({ fanout: true }));
console.log(pick({ replay: true, volume: "high" }));
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Queue | SQS | Service Bus / Storage Queue |
| Pub/Sub | SNS | Service Bus Topics |
| Event bus | EventBridge | Event Grid |
| Stream | Kinesis, MSK | Event Hubs |
| Pricing model | Mostly per request (approximate - check current docs) | Tier/unit-based plus ops (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using Event Grid for jobs that must not be lost or need ordering.
✅ Correct: Use Service Bus / SQS.

❌ Mistake: Using Service Bus to ingest millions of telemetry events.
✅ Correct: Use Event Hubs / Kinesis.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Command vs event?
A1: A command asks someone to do work (queue); an event states a fact happened (event grid/bridge).

Q2: [Medium] Why SNS + SQS together?
A2: SNS fans out; each SQS queue buffers and gives retries per consumer. Service Bus topic subscriptions do both in one.

Q3: [Hard] Design order processing on Azure.
A3: API -> Service Bus topic "orders"; subscriptions for billing/inventory with DLQ; Event Grid for blob/infra events; Event Hubs for clickstream analytics; SignalR to push status to UI.

---

## ✅ Quick Checklist
□ Pattern identified before service
□ Idempotent consumers everywhere (at-least-once)
□ DLQ + alarms on each path

---

## ⚡ 1-Line Summary
Match the service to the pattern: queue, topic, event, stream, realtime | पैटर्न के हिसाब से सही मैसेजिंग सर्विस चुनें।

## ➡️ Next: 253. Azure Security Center

---
