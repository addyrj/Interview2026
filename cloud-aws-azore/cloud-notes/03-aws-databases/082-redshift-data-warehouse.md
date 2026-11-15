---

# 82. Redshift (Data Warehouse)
# AWS: Amazon Redshift
# Azure: Azure Synapse Analytics (dedicated SQL pool)
# हिंदी में: रेडशिफ्ट (डेटा वेयरहाउस)

---

## 🔵 Simple Definition (2 lines)
Redshift is a managed columnar data warehouse for OLAP: big analytical queries (SUM, GROUP BY) over billions of rows using SQL.
हिंदी: Redshift एक मैनेज्ड डेटा वेयरहाउस है जो बहुत बड़े डेटा पर रिपोर्टिंग और एनालिटिक्स क्वेरी चलाता है।

---

## 🔴 Why it Exists (2 lines)
Row-based OLTP databases (MySQL/Postgres) choke on huge aggregations and hurt production traffic. A warehouse stores data by column, in parallel, so analytics run fast without touching the app DB.

---

## 🟢 How it Works
```
App DB / S3 / Kinesis ──(COPY, ETL, zero-ETL)──> Redshift
                                                   |
   Leader node (parses SQL, plans)  ── Compute nodes (columnar, MPP, parallel)
                                                   |
                          BI tools (QuickSight, Metabase) via JDBC/ODBC/Data API
Redshift Serverless = same engine, billed by RPU-seconds, no cluster to manage
```

---

## 💻 Code / Config Example
```sql
-- Load CSV files from S3 into Redshift (IAM role must be attached to the cluster)
CREATE TABLE orders (
  order_id   BIGINT,
  user_id    BIGINT,
  amount     DECIMAL(10,2),
  created_at TIMESTAMP
)
DISTKEY(user_id) SORTKEY(created_at);

COPY orders
FROM 's3://my-bucket/orders/2026/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftCopyRole'
FORMAT AS CSV IGNOREHEADER 1;

SELECT date_trunc('day', created_at) AS day, SUM(amount)
FROM orders GROUP BY 1 ORDER BY 1;
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Redshift (provisioned / Serverless) | Synapse Analytics (dedicated SQL pool / serverless) |
| Storage | Columnar, RA3 managed storage | Columnar, distributed (hash/round-robin/replicated) |
| Data lake query | Redshift Spectrum (S3) | Synapse serverless SQL on ADLS |
| Pricing | Node-hour or RPU-second (approximate — check current docs) | DWU-hour or per-TB processed (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using Redshift for many small single-row INSERT/UPDATEs.
✅ Correct: Batch load with COPY from S3; keep OLTP in RDS/Aurora.

❌ Mistake: Ignoring distribution/sort keys.
✅ Correct: Choose DISTKEY for join column and SORTKEY for filter column (or use AUTO).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] OLTP vs OLAP?
A1: OLTP = many small transactions (RDS); OLAP = few huge analytical queries (Redshift).

Q2: [Medium] Why is columnar storage faster for analytics?
A2: A query reads only the needed columns, and similar values compress well, so far less I/O.

Q3: [Hard] How do you query S3 data without loading it?
A3: Redshift Spectrum with external schema and Glue Data Catalog; pay per data scanned, best with Parquet and partitioning.

---

## ✅ Quick Checklist
□ Bulk load via COPY, not row inserts
□ Distribution and sort keys chosen (or AUTO)
□ Cluster in private subnet, encrypted, IAM role for S3

---

## ⚡ 1-Line Summary
Redshift = columnar warehouse for big analytics | Redshift बड़े एनालिटिक्स के लिए कॉलम-आधारित वेयरहाउस है।

## ➡️ Next: Timestream (Time Series)

---
