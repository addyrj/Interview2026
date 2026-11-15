# 125. MSK - Managed Kafka
# AWS: Amazon MSK (Managed Streaming for Apache Kafka)
# Azure: Event Hubs for Kafka (or HDInsight Kafka / Confluent on Azure)
# हिंदी में: AWS द्वारा संभाला गया Apache Kafka क्लस्टर

---

## 🔵 Simple Definition
MSK runs Apache Kafka brokers for you across AZs; you use normal Kafka clients and APIs.
हिंदी: MSK में Kafka ब्रोकर AWS चलाता है, आप सामान्य Kafka क्लाइंट इस्तेमाल करते हैं।

---

## 🔴 Why it Exists
Self-hosting Kafka (ZooKeeper/KRaft, patching, replication, storage) is heavy ops. Teams with Kafka code want it managed.

---

## 🟢 How it Works
```
App (Kafka client) --TLS/IAM/SASL--> Brokers in 3 AZs (inside your VPC)
   topic "orders" partitions 0..N, replication factor 3
   Consumer groups track offsets
Types: Provisioned | Serverless
```

---

## 💻 Code / Config Example
```javascript
// producer.js - Node.js with kafkajs (plain TLS example; MSK IAM auth needs a different SASL mechanism)
const { Kafka } = require("kafkajs");
const kafka = new Kafka({
  clientId: "orders-api",
  brokers: process.env.MSK_BROKERS.split(","), // b-1.xxx:9094,...
  ssl: true,
});
async function main() {
  const producer = kafka.producer({ idempotent: true });
  await producer.connect();
  await producer.send({
    topic: "orders",
    messages: [{ key: "user-42", value: JSON.stringify({ orderId: 1 }) }],
  });
  await producer.disconnect();
}
main().catch(console.error);
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | MSK / MSK Serverless | Event Hubs Kafka endpoint, HDInsight |
| Native Kafka | Yes (real Kafka) | Kafka-protocol compatible (not real Kafka brokers on Event Hubs) |
| Network | In your VPC | Private endpoints |
| Pricing | Broker-hour + storage (approximate - check current docs) | Throughput units (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Running MSK for a tiny workload.
✅ Correct: It has a fixed broker cost; use SQS/Kinesis/EventBridge for small needs.

❌ Mistake: Clients cannot connect (public internet).
✅ Correct: Brokers are in a VPC; run clients in the VPC or use security groups/VPN.

---

## ⚫ Interview Q&A
Q1: [Easy] What is MSK?
A1: Managed Apache Kafka on AWS.

Q2: [Medium] MSK vs Kinesis?
A2: MSK = Kafka API/ecosystem, tuning control; Kinesis = simpler AWS-native, less ops.

Q3: [Hard] How do you avoid data loss?
A3: Replication factor 3, min.insync.replicas=2, producer acks=all and idempotence, multi-AZ brokers, monitor under-replicated partitions.

---

## ✅ Quick Checklist
□ Multi-AZ, RF 3
□ Auth (TLS/IAM/SASL) enabled
□ Consumer lag alarm

---

## ⚡ 1-Line Summary
MSK = Kafka without broker ops | MSK में Kafka का ब्रोकर-संचालन AWS संभालता है।

## ➡️ Next: Messaging Patterns
