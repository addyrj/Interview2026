# 176. Azure vs AWS — Overview
# AWS: Amazon Web Services (account > regions > services)
# Azure: Microsoft Azure (tenant > management groups > subscriptions > resource groups)
# हिंदी में: Azure और AWS की तुलना, एक नज़र में

---

## 🔵 Simple Definition
Both are hyperscale clouds with near-equivalent services; they differ mainly in naming, account hierarchy and identity model.
हिंदी: दोनों clouds में लगभग एक जैसी services हैं, फर्क नाम, account structure और identity में है।

---

## 🔴 Why it Exists
Many companies run multi-cloud or switch; knowing the mapping makes you productive on either.
Microsoft shops (AD, .NET, Office 365) often pick Azure; startups often pick AWS.

---

## 🟢 How it Works
```
AWS:   Organization -> OU -> Account -> Region -> resources (IAM per account)
Azure: Entra tenant -> Mgmt Group -> Subscription -> Resource Group -> resources (RBAC)
Key difference: Azure resources live in a Resource Group; AWS has no equivalent container
(tags / CloudFormation stacks are the nearest).
```

---

## 💻 Code / Config Example
```bash
# Same task on both: list compute
aws ec2 describe-instances --query "Reservations[].Instances[].InstanceId"
az vm list --query "[].name" -o tsv

# Same task: run a container for your Node.js / FastAPI stack
# AWS: ECS Fargate | Azure: Container Apps
az containerapp --help >/dev/null && echo "az CLI containerapp available"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| VM | EC2 | Virtual Machines |
| Object storage | S3 | Blob Storage |
| Containers | ECS/EKS/ECR | Container Apps/AKS/ACR |
| Serverless | Lambda | Functions |
| SQL DB | RDS | Azure SQL / Database for PostgreSQL |
| NoSQL | DynamoDB | Cosmos DB |
| Identity | IAM | Entra ID + RBAC |
| Monitoring | CloudWatch | Azure Monitor |
| IaC | CloudFormation/CDK | ARM/Bicep |
| CI/CD | CodePipeline | Azure Pipelines |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming a 1:1 feature match (e.g. Azure VNets span a region, AWS VPCs too, but subnets: AWS per AZ, Azure subnets span zones).
✅ Correct: Read each service's scope and limits.

❌ Mistake: Mixing up "account" with "subscription".
✅ Correct: AWS account ~ Azure subscription (billing + isolation boundary).

---

## ⚫ Interview Q&A
Q1: [Easy] AWS S3 equals which Azure service?
A1: Blob Storage.

Q2: [Medium] Why does Azure have Resource Groups?
A2: Lifecycle and RBAC container: deploy, tag, secure and delete related resources together.

Q3: [Hard] How would you choose between them?
A3: Existing licences/AD integration, region availability, service maturity for the workload, team skills, pricing and compliance; avoid lock-in with containers and Terraform.

---

## ✅ Quick Checklist
□ Know the service mapping
□ Know account vs subscription
□ Know IAM vs Entra ID + RBAC

---

## ⚡ 1-Line Summary
Same ideas, different names and hierarchy | विचार वही हैं, नाम और hierarchy अलग हैं।

## ➡️ Next: 177. Azure Account + Portal
