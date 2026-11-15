# 229. Azure Data Factory
# AWS: AWS Glue (ETL) + Step Functions / Data Pipeline (legacy)
# Azure: Azure Data Factory (ADF)
# हिंदी में: डेटा को एक जगह से दूसरी जगह ले जाने और बदलने का ऑर्केस्ट्रेशन सर्विस

---

## 🔵 Simple Definition (2 lines)
Data Factory is a managed ETL/ELT orchestrator: pipelines made of activities (copy, data flow, notebook, stored procedure) run on triggers.
हिंदी: ADF से आप बिना सर्वर चलाए डेटा pipelines शेड्यूल और मॉनिटर कर सकते हैं।

---

## 🔴 Why it Exists (2 lines)
Moving data between databases, APIs and storage with cron scripts is fragile and unmonitored.
ADF has 90+ connectors, retries, alerts and a visual designer.

---

## 🟢 How it Works
```
Trigger (schedule / tumbling window / event)
   -> Pipeline
        -> Activity: Copy (source dataset -> sink dataset)
        -> Activity: Data Flow / Databricks / Stored Proc
   Linked Service = connection (Postgres, Blob, ...)
   Dataset        = shape/location of data
   Integration Runtime = compute (Azure, or self-hosted for on-prem/VPS)
```

---

## 💻 Code / Config Example
```json
{
  "name": "CopyOrdersToLake",
  "properties": {
    "activities": [
      {
        "name": "CopyOrders",
        "type": "Copy",
        "inputs":  [ { "referenceName": "PgOrders", "type": "DatasetReference" } ],
        "outputs": [ { "referenceName": "LakeOrdersParquet", "type": "DatasetReference" } ],
        "typeProperties": {
          "source": { "type": "AzurePostgreSqlSource", "query": "SELECT * FROM orders WHERE updated_at >= now() - interval '1 day'" },
          "sink":   { "type": "ParquetSink" }
        },
        "policy": { "retry": 2, "timeout": "0.01:00:00" }
      }
    ]
  }
}
```
```bash
# Needs: az extension add --name datafactory
az datafactory pipeline create-run --factory-name myapp-adf --resource-group rg-data --name CopyOrdersToLake
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| ETL service | Glue (Spark/Python) | Data Factory (low-code + Data Flows) |
| Orchestration | Step Functions / MWAA | ADF pipelines / triggers |
| On-prem access | Glue connections / DMS | Self-hosted Integration Runtime |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Full table copy every run.
✅ Correct: Incremental load with a watermark column.

❌ Mistake: Secrets hard-coded in linked services.
✅ Correct: Reference Key Vault and use managed identity.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a linked service?
A1: A connection definition to a data store or compute.

Q2: [Medium] What is an Integration Runtime?
A2: The compute that executes activities; self-hosted IR reaches private networks.

Q3: [Hard] How do you do CI/CD for ADF?
A3: Author in a Git-backed factory, publish generates ARM templates, deploy via GitHub Actions/Azure Pipelines with environment parameter overrides.

---

## ✅ Quick Checklist
□ Incremental loads with watermark
□ Alerts on failed runs
□ Git integration and Key Vault

---

## ⚡ 1-Line Summary
ADF orchestrates ETL pipelines at scale | ADF बड़े पैमाने पर ETL pipelines चलाता है

## ➡️ Next: Azure HDInsight

---
