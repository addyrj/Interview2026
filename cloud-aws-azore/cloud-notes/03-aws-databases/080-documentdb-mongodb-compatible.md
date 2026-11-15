# 80. DOCUMENTDB (MONGODB COMPATIBLE)
# AWS: Amazon DocumentDB (with MongoDB compatibility)
# Azure: Azure Cosmos DB for MongoDB (vCore / RU)
# हिंदी में: DocumentDB यानी MongoDB-जैसा मैनेज्ड डेटाबेस

---

## 🔵 Simple Definition (2 lines)
DocumentDB is a managed document database that implements the MongoDB API on an Aurora-style distributed storage layer; it is not MongoDB itself.
हिंदी: DocumentDB MongoDB API देने वाला मैनेज्ड डॉक्यूमेंट डेटाबेस है; यह असली MongoDB नहीं है।

---

## 🔴 Why it Exists (2 lines)
Teams with Mongo-based apps (Node.js + Mongoose) want managed HA, backups and scaling inside AWS.
It offers familiar drivers with 6-copy storage and up to 15 replicas.

---

## 🟢 How it Works
```
App (mongoose) --TLS--> cluster endpoint (writer)
                         reader endpoint (replicas, up to 15)
Shared storage volume: 6 copies / 3 AZs, auto-grows
Compatible with MongoDB APIs of selected versions (check docs for the list);
some operators/features are unsupported -> test your queries
```

---

## 💻 Code / Config Example
```javascript
// Node.js (mongoose) connecting to DocumentDB with TLS
const mongoose = require("mongoose");
// Download the Amazon RDS/DocumentDB CA bundle (global-bundle.pem) first.
const uri = `mongodb://${process.env.DB_USER}:${encodeURIComponent(process.env.DB_PASS)}` +
  `@${process.env.DOCDB_HOST}:27017/app` +
  `?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false`;
mongoose.connect(uri).then(() => console.log("connected"));
```
```bash
# Create a cluster (AWS CLI v2)
aws docdb create-db-cluster --db-cluster-identifier app-docdb \
  --engine docdb --master-username appadmin --manage-master-user-password
aws docdb create-db-instance --db-instance-identifier app-docdb-1 \
  --db-instance-class db.t4g.medium --engine docdb --db-cluster-identifier app-docdb
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | DocumentDB | Cosmos DB for MongoDB |
| Model | Instance-based cluster | vCore (instance) or RU-based |
| Compatibility | MongoDB API subset | MongoDB API subset |
| Pricing | Instance-hours + storage + IO (approximate - check current docs) | vCore or RU/s (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming 100% MongoDB compatibility.
✅ Correct: Run your test suite against DocumentDB; check unsupported operators.

❌ Mistake: Using `retryWrites=true`.
✅ Correct: Historically unsupported; set `retryWrites=false` unless docs for your version say otherwise.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Is DocumentDB MongoDB?
A1: No, it is an AWS-built database compatible with the MongoDB API.

Q2: [Medium] How do you connect securely?
A2: TLS with the CA bundle, in a private subnet, SG allowing 27017 from the app only.

Q3: [Hard] Mongo Atlas vs DocumentDB?
A3: Atlas is real MongoDB with full features and multi-cloud; DocumentDB is cheaper to integrate with AWS (IAM, VPC) but has feature gaps and AWS lock-in.

---

## ✅ Quick Checklist
□ Query compatibility tested
□ TLS and CA bundle configured
□ Reader endpoint used for reads

---

## ⚡ 1-Line Summary
DocumentDB = managed, MongoDB-API-compatible database on AWS (not real MongoDB). | DocumentDB = AWS पर मैनेज्ड, MongoDB-API कम्पैटिबल डेटाबेस (असली MongoDB नहीं)।

## ➡️ Next: Next section topic

---
