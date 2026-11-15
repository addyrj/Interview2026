---

# 15. AWS vs Azure vs GCP Overview
# AWS: Amazon Web Services
# Azure: Microsoft Azure (GCP = Google Cloud for comparison)
# हिंदी में: तीनों बड़े क्लाउड की सर्विसेज़ का आमने-सामने मिलान

---

## 🔵 Simple Definition (2 lines)
AWS, Azure and GCP are the three largest public clouds with mostly equivalent services under different names.
हिंदी: तीनों में लगभग एक जैसी सर्विसेज़ हैं, बस नाम और डिज़ाइन में फ़र्क़ है।

---

## 🔴 Why it Exists (2 lines)
Interviews and migrations need you to map concepts across providers.
Knowing equivalents avoids vendor lock-in confusion.

---

## 🟢 How it Works
```
Concept          AWS            Azure              GCP
Account scope    Account / Org  Subscription / MG  Project / Org
Network          VPC            VNet               VPC
VM               EC2            Virtual Machines   Compute Engine
Containers       ECS / EKS      ACI,Container Apps/AKS  Cloud Run / GKE
Serverless fn    Lambda         Functions          Cloud Functions
Object storage   S3             Blob Storage       Cloud Storage
SQL managed      RDS / Aurora   Azure SQL / PG Flex Cloud SQL / AlloyDB
NoSQL            DynamoDB       Cosmos DB          Firestore / Bigtable
Queue / pubsub   SQS / SNS      Service Bus / Event Grid  Pub/Sub
Identity         IAM            Entra ID + RBAC    Cloud IAM
IaC native       CloudFormation Bicep / ARM        Deployment Manager
```

---

## 💻 Code / Config Example
```bash
# Same task, three CLIs: create an object storage container
aws s3 mb s3://my-unique-bucket-12345 --region ap-south-1

az storage container create --name mycontainer \
  --account-name mystorageacct --auth-mode login

gcloud storage buckets create gs://my-unique-bucket-12345 --location=asia-south1
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Strength | Widest service catalog, maturity | Microsoft/enterprise integration (Entra, .NET, M365) |
| Hierarchy | Org > OU > Account | Tenant > Mgmt Group > Subscription > RG |
| IaC | CloudFormation, CDK | Bicep, ARM |
| Pricing | Per-second compute, many discount types (check docs) | Similar; Hybrid Benefit for Windows/SQL licenses (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming service names map 1:1 in behavior (e.g., IAM models differ).
✅ Correct: Learn semantic differences: AWS policies vs Azure RBAC role assignments at scopes.

❌ Mistake: Choosing a provider on brand alone.
✅ Correct: Choose by existing skills, ecosystem, required services, region presence and cost.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Azure equivalent of S3?
A1: Blob Storage.

Q2: [Medium] AWS Account vs Azure Subscription?
A2: Both are billing/isolation boundaries; Azure adds Resource Groups for lifecycle grouping inside a subscription.

Q3: [Hard] How avoid lock-in?
A3: Containers, open standards (Postgres, Kubernetes, OpenTelemetry), Terraform, abstraction at edges; accept some lock-in where managed services give big value.

---

## ✅ Quick Checklist
□ Can map 10 core services across providers
□ Know hierarchy: account/subscription/project
□ Know IaC options per cloud

---

## ⚡ 1-Line Summary
Same ideas, different names: map concepts, not just labels | आइडिया वही, नाम अलग: नाम नहीं, कॉन्सेप्ट मैप करो।

## ➡️ Next: 16. AWS Account Setup + IAM Root

---
