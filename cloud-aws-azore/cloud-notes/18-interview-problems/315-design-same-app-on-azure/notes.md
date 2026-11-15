# 315. Design Same App on Azure
# AWS: ALB + ECS Fargate + RDS + ECR + CloudWatch (the 301/307 design)
# Azure: Container Apps + PostgreSQL Flexible Server + ACR + Log Analytics
# हिंदी में: वही 3-टियर ऐप Azure पर - सर्विस बदलती हैं, आर्किटेक्चर वही रहता है

---

## 🔵 Simple Definition
Map each AWS building block to its Azure equivalent and rebuild the same architecture with Bicep.
हिंदी: हर AWS सर्विस का Azure मैपिंग करके वही आर्किटेक्चर बनाओ।

## 🔴 Why it Exists
Interviews and migrations test whether you understand the pattern, not only one vendor's names.

## 🟢 How it Works
```
Internet -> Container Apps ingress (built-in HTTPS, L7)   [ALB + Fargate]
              -> API replicas (HTTP autoscale 1..5)
              -> PostgreSQL Flexible Server               [RDS]
Image: ACR, pulled by managed identity (AcrPull)           [ECR + task role]
Logs: Log Analytics workspace                              [CloudWatch Logs]
Secrets: Container Apps secret (-> Key Vault ref in prod)  [Secrets Manager]
```

## 💻 Code / Config Example
`main.bicep` (this folder): Log Analytics, ACR (Basic), PostgreSQL Flexible Server (Burstable B1ms, v15), Container Apps environment + app with HTTP scaling and probe, AcrPull role assignment for the app identity.
Not deployed - Azure CLI not installed. The first deploy uses a placeholder hello-world image (it listens on port 80, so set targetPort/probe to match or push your image first). DB firewall/VNet rules are not included - add private access before real use.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Container runtime | ECS Fargate | Container Apps |
| Load balancer | ALB | built-in ingress / Front Door / App Gateway |
| Database | RDS PostgreSQL | PostgreSQL Flexible Server |
| Registry | ECR | ACR |
| IaC | Terraform/CFN | Bicep/ARM (Terraform also works) |
| Pricing | per vCPU/GB-second (approximate - check current docs) | similar consumption model |

## 💰 Cost / HA / Security
- Cost: Container Apps can scale to zero (minReplicas 0) for dev; Burstable DB for non-prod.
- HA: set minReplicas >= 2 and zone-redundant environment/DB (General Purpose tier) for prod.
- Security: managed identity for ACR, secrets in Key Vault, private endpoint/VNet for DB, no admin user on ACR.

## ⚠️ Common Mistakes
❌ Leaving DB publicly reachable with a password in a template param file.
✅ Private access + Key Vault reference, pass secrets securely.

❌ Assuming the same quotas/regions as AWS.
✅ Check Azure region and quota availability first.

## ⚫ Interview Q&A
Q1 [Easy]: ECS Fargate equivalent on Azure?
A1: Azure Container Apps (or ACI / AKS for more control).

Q2 [Medium]: How does the app authenticate to ACR without passwords?
A2: System/user-assigned managed identity with the AcrPull role, similar to an ECS task execution role.

Q3 [Hard]: Container Apps vs AKS vs App Service?
A3: App Service: simplest PaaS web apps. Container Apps: serverless containers, KEDA scaling, microservices. AKS: full Kubernetes control and ops burden.

## ✅ Quick Checklist
□ Service mapping table done
□ Managed identity instead of keys
□ Logs/alerts wired to Log Analytics

## ⚡ 1-Line Summary
Same 3-tier pattern, Azure names: Container Apps + PostgreSQL Flexible + ACR. | वही पैटर्न, Azure नाम: Container Apps + PostgreSQL + ACR।

## ➡️ Next: 316. Deploy to Azure App Service
