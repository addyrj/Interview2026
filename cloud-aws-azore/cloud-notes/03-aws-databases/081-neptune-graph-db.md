---

# 81. Neptune (Graph DB)
# AWS: Amazon Neptune
# Azure: Azure Cosmos DB for Apache Gremlin (closest equivalent)
# हिंदी में: नेप्च्यून (ग्राफ डेटाबेस)

---

## 🔵 Simple Definition (2 lines)
Neptune is a managed graph database. It stores nodes (things) and edges (relationships) and queries them with Gremlin, openCypher or SPARQL.
हिंदी: Neptune एक मैनेज्ड ग्राफ डेटाबेस है जो नोड्स और उनके आपसी रिश्तों (edges) को तेज़ी से खोजता है।

---

## 🔴 Why it Exists (2 lines)
SQL JOINs get slow for "friends of friends of friends" style queries. A graph DB follows relationships directly, so deep traversals stay fast (fraud rings, recommendations, social graphs).

---

## 🟢 How it Works
```
App (Node.js/FastAPI, inside VPC)
   |  Gremlin (wss://:8182/gremlin) / openCypher (https://:8182/openCypher)
   v
Neptune Cluster
  ├─ 1 Writer instance
  ├─ up to 15 Read replicas
  └─ Shared storage volume (6 copies across 3 AZs, auto-grows)
(Neptune is VPC-only: no public endpoint)
```

---

## 💻 Code / Config Example
```python
# FastAPI/Python: openCypher over HTTPS (Neptune endpoint is reachable only inside the VPC)
# With IAM auth enabled you must SigV4-sign requests; shown here without signing for brevity.
import requests

ENDPOINT = "https://my-cluster.cluster-xxxx.ap-south-1.neptune.amazonaws.com:8182/openCypher"
query = """
MATCH (u:User {id: $uid})-[:FOLLOWS]->(f)-[:FOLLOWS]->(fof)
WHERE fof.id <> $uid
RETURN DISTINCT fof.id LIMIT 10
"""
r = requests.post(ENDPOINT, data={"query": query, "parameters": '{"uid": "u1"}'}, timeout=10)
print(r.json())
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Neptune | Cosmos DB for Gremlin |
| Query languages | Gremlin, openCypher, SPARQL | Gremlin only |
| Model | Instance-based cluster (also Neptune Serverless) | RU/s provisioned or serverless |
| Network | VPC only | Public or Private Endpoint |
| Pricing | Per instance-hour + storage + I/O (approximate — check current docs) | Per RU/s + storage (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using a graph DB for plain CRUD/orders data.
✅ Correct: Keep OLTP in PostgreSQL/DynamoDB; use Neptune only when relationships are the query.

❌ Mistake: Trying to reach Neptune from your laptop/public internet.
✅ Correct: Use a bastion, VPN, or run the app in the same VPC.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] When do you choose a graph DB?
A1: When queries are relationship-heavy and multi-hop (recommendations, fraud, social, knowledge graphs).

Q2: [Medium] Gremlin vs openCypher vs SPARQL?
A2: Gremlin = property-graph traversal language; openCypher = declarative SQL-like for property graphs; SPARQL = for RDF triple stores.

Q3: [Hard] How do you scale Neptune reads and make it HA?
A3: Add read replicas (up to 15) behind the reader endpoint; storage is replicated across 3 AZs and a replica gets promoted on writer failure. Writes scale only vertically (or use Serverless capacity).

---

## ✅ Quick Checklist
□ Is the workload really multi-hop relationships?
□ App runs inside the VPC / security group allows port 8182
□ IAM DB auth + encryption at rest enabled

---

## ⚡ 1-Line Summary
Neptune = managed graph DB for relationship-heavy queries | Neptune रिश्तों वाली क्वेरी के लिए मैनेज्ड ग्राफ DB है।

## ➡️ Next: Redshift (Data Warehouse)

---
