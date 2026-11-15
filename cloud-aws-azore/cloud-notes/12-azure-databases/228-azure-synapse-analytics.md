# 228. Azure Synapse Analytics
# AWS: Amazon Redshift (+ Athena, EMR/Glue for Spark)
# Azure: Azure Synapse Analytics (Microsoft Fabric is the newer unified platform)
# हिंदी में: बड़े डेटा पर analytics के लिए data warehouse + Spark

---

## 🔵 Simple Definition (2 lines)
Synapse combines a data warehouse (dedicated SQL pool), a serverless SQL query engine over the data lake, and Spark pools in one workspace.
हिंदी: बहुत बड़े डेटा पर रिपोर्टिंग और analytics के लिए एक जगह में SQL और Spark।

---

## 🔴 Why it Exists (2 lines)
OLTP databases are not built for scanning billions of rows for reports.
Synapse separates storage from compute and queries lake files directly.

---

## 🟢 How it Works
```
Sources -> Data Factory/Synapse Pipelines -> Data Lake (ADLS Gen2, Parquet)
                                               |
        Serverless SQL pool  (pay per TB scanned, query files)
        Dedicated SQL pool   (MPP warehouse, DWUs, pause/resume)
        Spark pool           (notebooks, PySpark)
                                               |
                                   Power BI / apps
```

---

## 💻 Code / Config Example
```sql
-- Serverless SQL pool: query Parquet in the lake without loading it
SELECT TOP 10 customer_id, SUM(amount) AS total
FROM OPENROWSET(
    BULK 'https://myapplake.dfs.core.windows.net/curated/orders/*.parquet',
    FORMAT = 'PARQUET'
) AS orders
GROUP BY customer_id
ORDER BY total DESC;
```
```bash
# Pause a dedicated pool when idle to stop compute billing
az synapse sql pool pause --name dwpool --workspace-name myapp-syn --resource-group rg-data
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Warehouse | Redshift | Dedicated SQL pool |
| Query lake | Athena / Redshift Spectrum | Serverless SQL pool |
| Spark | EMR / Glue | Spark pools |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving a dedicated pool running 24/7 for occasional reports.
✅ Correct: Pause it, or use serverless for ad-hoc queries.

❌ Mistake: Many small CSV files in the lake.
✅ Correct: Use partitioned, columnar Parquet with sensible file sizes.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Serverless vs dedicated SQL pool?
A1: Serverless bills per data scanned for ad-hoc lake queries; dedicated is a provisioned MPP warehouse billed for compute.

Q2: [Medium] Why distribution columns?
A2: Dedicated pools spread rows across 60 distributions; a good hash key reduces data movement in joins.

Q3: [Hard] Design a reporting pipeline for app data.
A3: Copy OLTP data via Data Factory into ADLS (Parquet, partitioned by date), transform with Spark/SQL, serve curated tables to Power BI, and orchestrate and monitor on a schedule.

---

## ✅ Quick Checklist
□ Lake in Parquet, partitioned
□ Pools paused when idle
□ Evaluate Fabric for new builds

---

## ⚡ 1-Line Summary
Synapse = warehouse + lake SQL + Spark | Synapse = वेयरहाउस + लेक SQL + Spark

## ➡️ Next: Azure Data Factory

---
