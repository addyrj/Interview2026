---

# 246. Azure Event Hubs (= Kafka compatible)
# AWS: Amazon Kinesis Data Streams / Amazon MSK (managed Kafka)
# Azure: Azure Event Hubs (Kafka endpoint on Standard tier and above)
# हिंदी में: Event Hubs = लाखों इवेंट/सेकंड के लिए streaming प्लेटफ़ॉर्म, Kafka से compatible

---

## 🔵 Simple Definition (2 lines)
Event Hubs is a managed streaming service that ingests huge event volumes and lets many consumers read them in order per partition.
Event Hubs logs, clickstream और IoT जैसे ज़्यादा डेटा को स्ट्रीम में लेकर कई consumers को पढ़ने देता है।

---

## 🔴 Why it Exists (2 lines)
Queues delete messages once consumed; analytics needs replayable high-throughput logs.
Event Hubs keeps events for a retention period so consumers can re-read.

---

## 🟢 How it Works
```
Producers -> Event Hub (partitions P0..Pn, retention days)
               |-- Consumer Group "analytics" (offset per partition)
               |-- Consumer Group "alerts"
               \-- Capture -> Blob/ADLS (Avro) automatically
Kafka mapping: Namespace=cluster, Event Hub=topic, Partition=partition, Consumer group=group
Kafka clients connect to <ns>.servicebus.windows.net:9093 (SASL_SSL, user "$ConnectionString")
```

---

## 💻 Code / Config Example
```javascript
// npm i kafkajs  - use existing Kafka code against Event Hubs
const { Kafka } = require("kafkajs");
const kafka = new Kafka({
  clientId: "api",
  brokers: [`${process.env.EH_NAMESPACE}.servicebus.windows.net:9093`],
  ssl: true,
  sasl: { mechanism: "plain", username: "$ConnectionString", password: process.env.EH_CONNECTION_STRING },
});
async function run() {
  const p = kafka.producer();
  await p.connect();
  await p.send({ topic: "clicks", messages: [{ key: "user1", value: JSON.stringify({ page: "/home" }) }] });
  await p.disconnect();
}
run().catch(console.error);
```
```bash
az eventhubs namespace create -g rg-demo -n eh-demo-ns -l centralindia --sku Standard
az eventhubs eventhub create -g rg-demo --namespace-name eh-demo-ns -n clicks --partition-count 4
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Native stream | Kinesis Data Streams | Event Hubs |
| Kafka | MSK (real Kafka brokers) | Kafka protocol endpoint on Event Hubs |
| Scale unit | Shards / on-demand | Partitions + throughput/processing units |
| Archive | Firehose to S3 | Capture to Blob/ADLS |
| Pricing | Per shard/hour or on-demand (approximate - check current docs) | Per TU/PU + ingress (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Choosing too few partitions; count is hard to change on lower tiers.
✅ Correct: Plan for peak parallelism up front.

❌ Mistake: Using Event Hubs as a work queue with per-message ack.
✅ Correct: Use Service Bus for jobs; Event Hubs for streams.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a consumer group?
A1: An independent view/offset set over the stream so multiple apps read the same data.

Q2: [Medium] Does Event Hubs run Kafka?
A2: No, it exposes a Kafka-protocol-compatible endpoint; it is not Apache Kafka itself and some features differ.

Q3: [Hard] How do you guarantee ordering?
A3: Order is per partition only; use a partition key so related events land in the same partition.

---

## ✅ Quick Checklist
□ Partition count sized for peak consumers
□ Retention and Capture configured
□ Separate consumer group per application

---

## ⚡ 1-Line Summary
Event Hubs is Azure's high-throughput event stream with a Kafka endpoint | Event Hubs बड़े पैमाने की इवेंट स्ट्रीम है जिसमें Kafka सपोर्ट है।

## ➡️ Next: 247. Event Hubs vs Kinesis

---
