# 230. Azure HDInsight
# AWS: Amazon EMR
# Azure: Azure HDInsight
# हिंदी में: Hadoop, Spark, Kafka जैसे open-source big data क्लस्टर का मैनेज्ड सर्विस

---

## 🔵 Simple Definition (2 lines)
HDInsight runs managed open-source analytics clusters (Spark, Hadoop, HBase, Kafka, Hive) on Azure.
हिंदी: बिना खुद क्लस्टर बनाए बड़े डेटा पर Spark/Hadoop jobs चलाने की सुविधा।

---

## 🔴 Why it Exists (2 lines)
Existing Hadoop/Spark workloads need the same open-source stack in the cloud.
Newer builds often prefer Synapse, Databricks or Fabric; HDInsight mainly serves lift-and-shift.

---

## 🟢 How it Works
```
Head nodes + Worker nodes (+ ZooKeeper)
        |
 Storage: ADLS Gen2 / Blob (decoupled from the cluster)
        |
 Job: spark-submit / Livy / Jupyter -> results back to storage
Delete the cluster after the job; data stays in storage (cost saving).
```

---

## 💻 Code / Config Example
```python
# PySpark job: daily revenue from Parquet in ADLS Gen2
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("daily-revenue").getOrCreate()
df = spark.read.parquet("abfss://curated@myapplake.dfs.core.windows.net/orders/")
out = (df.groupBy(F.to_date("created_at").alias("day"))
         .agg(F.sum("amount").alias("revenue")))
out.write.mode("overwrite").parquet("abfss://curated@myapplake.dfs.core.windows.net/daily_revenue/")
```
```bash
# Creating a cluster has many required flags; verify with: az hdinsight create --help
az hdinsight list -g rg-data -o table
az hdinsight delete -g rg-data -n myapp-spark --yes   # stop paying when job finishes
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | EMR (also EMR Serverless) | HDInsight |
| Storage | S3 | ADLS Gen2 / Blob |
| Alternatives | Glue | Synapse Spark, Databricks, Fabric |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Keeping the cluster running 24/7 and storing data on cluster HDFS.
✅ Correct: Keep data in ADLS/Blob and create or delete clusters per job.

❌ Mistake: Choosing HDInsight for new greenfield analytics by default.
✅ Correct: Compare Synapse/Fabric/Databricks first.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What can HDInsight run?
A1: Spark, Hadoop, Hive, HBase, Kafka and more.

Q2: [Medium] Why decouple storage and compute?
A2: Clusters become disposable and cheap; data persists.

Q3: [Hard] Migrate on-prem Hadoop to Azure?
A3: Copy data to ADLS (DistCp/ADF), rewrite HDFS paths to abfss://, run Hive/Spark on HDInsight or move to Synapse/Databricks, validate and tune.

---

## ✅ Quick Checklist
□ Data in ADLS, not cluster disks
□ Auto-delete clusters after jobs
□ Alternatives evaluated

---

## ⚡ 1-Line Summary
HDInsight = managed Hadoop/Spark clusters, EMR equivalent | HDInsight = मैनेज्ड Hadoop/Spark क्लस्टर, EMR जैसा

## ➡️ Next: Choosing Azure Database

---
