# 300. Cloud-agnostic Architecture
# AWS: Runs open standards on EKS/RDS/S3 API
# Azure: Runs open standards on AKS/Flexible Server/Blob
# हिंदी में: क्लाउड-एग्नोस्टिक आर्किटेक्चर

---

## 🔵 Simple Definition
Design the app on portable building blocks (containers, Postgres, S3-style storage, OpenTelemetry) so the cloud can change with limited rework.
हिंदी: ऐप को पोर्टेबल ब्लॉक पर बनाना ताकि क्लाउड बदलना आसान रहे।

---

## 🔴 Why it Exists
Reduces lock-in and eases migration, at the price of not using every native feature.

---

## 🟢 How it Works
```
App (12-factor, config via env)
  -> Docker image            (runs anywhere)
  -> Postgres / Redis        (managed on any cloud, same wire protocol)
  -> Storage adapter         (S3 | Blob behind an interface)
  -> Queue adapter           (SQS | Service Bus | RabbitMQ)
  -> OpenTelemetry exporter  (any backend)
  -> Terraform / Helm        (deploy)
```

---

## 💻 Code / Config Example
```javascript
// storage.js - adapter interface; pick implementation by env
// AWS: npm i @aws-sdk/client-s3 ; Azure: npm i @azure/storage-blob @azure/identity
async function makeStorage() {
  if (process.env.CLOUD === "aws") {
    const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
    const s3 = new S3Client({});
    return { put: (key, body) => s3.send(new PutObjectCommand({ Bucket: process.env.BUCKET, Key: key, Body: body })) };
  }
  const { BlobServiceClient } = require("@azure/storage-blob");
  const { DefaultAzureCredential } = require("@azure/identity");
  const c = new BlobServiceClient(process.env.BLOB_URL, new DefaultAzureCredential())
    .getContainerClient(process.env.CONTAINER);
  return { put: (key, body) => c.getBlockBlobClient(key).upload(body, Buffer.byteLength(body)) };
}
module.exports = { makeStorage };
```

---

## 📊 AWS vs Azure Quick Compare
| Layer | AWS | Azure |
|-------|-----|-------|
| Run containers | EKS / ECS | AKS / Container Apps |
| Database | RDS PostgreSQL | Flexible Server PostgreSQL |
| Object storage | S3 | Blob (use adapter) |
| IaC | Terraform | Terraform |

---

## ⚠️ Common Mistakes
❌ Mistake: Wrapping everything in abstractions up front.
✅ Correct: Abstract only the hot spots (storage, queue, secrets); accept some lock-in.

❌ Mistake: Ignoring data gravity.
✅ Correct: Plan data export and egress cost for migration.

---

## ⚫ Interview Q&A
Q1: [Easy] What is cloud-agnostic?
A1: Design that avoids cloud-specific dependencies where practical.

Q2: [Medium] Which pieces are easiest to port?
A2: Containers, Postgres/MySQL, Redis, Kafka-compatible streams.

Q3: [Hard] Trade-off of agnostic design?
A3: Portability costs extra code and skips managed-service advantages (DynamoDB, Cosmos, Lambda triggers); decide per component with a lock-in vs speed analysis.

---

## ✅ Quick Checklist
□ 12-factor config
□ Adapters for storage/queue/secrets
□ IaC and CI portable

---

## ⚡ 1-Line Summary
Use portable standards and thin adapters; accept pragmatic lock-in. | पोर्टेबल स्टैंडर्ड और पतले एडाप्टर इस्तेमाल करें, व्यावहारिक लॉक-इन स्वीकारें।

## ➡️ Next: 301. Design 3-Tier App on AWS
