# 198. Azure Container Instances (ACI)
# AWS: ECS on Fargate (single task) / App Runner
# Azure: Azure Container Instances
# हिंदी में: बिना VM या cluster के सीधे container चलाने की सेवा

---

## 🔵 Simple Definition
Run a container (or small group) in seconds with per-second billing and no orchestrator.
ACI में सीधे Docker container चलता है; cluster या VM की ज़रूरत नहीं।

---

## 🔴 Why it Exists
Quick tasks, batch jobs, CI runners and demos do not need AKS or a VM.

---

## 🟢 How it Works
```
Docker image (ACR/Docker Hub) -> Container Group (shared network, volumes)
   -> public IP / DNS label or private VNet subnet
Billed per vCPU-second and GB-second while running
No built-in autoscale / load balancing / rolling updates
```

---

## 💻 Code / Config Example
```bash
az container create -g rg-aci -n aci-fastapi \
  --image myacr.azurecr.io/fastapi-app:1.0 \
  --registry-login-server myacr.azurecr.io \
  --registry-username <user> --registry-password <pwd> \
  --cpu 1 --memory 1.5 \
  --ports 8000 --dns-name-label fastapi-demo-123 \
  --environment-variables APP_ENV=prod \
  --secure-environment-variables DB_URL=<secret> \
  --restart-policy OnFailure
az container logs -g rg-aci -n aci-fastapi
az container delete -g rg-aci -n aci-fastapi --yes
```
Prefer managed identity pull from ACR over username/password.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Fargate task / App Runner | ACI |
| Orchestration | ECS | None (use AKS / Container Apps) |
| Billing | Per second vCPU/GB | Per second vCPU/GB |
| Better for services | ECS/App Runner | Azure Container Apps |

---

## ⚠️ Common Mistakes
❌ Mistake: Using ACI for production web services needing autoscale.
✅ Correct: Use Container Apps, App Service or AKS.

❌ Mistake: Plain env var for secrets.
✅ Correct: `--secure-environment-variables` or Key Vault.

---

## ⚫ Interview Q&A
Q1: [Easy] What is ACI?
A1: Serverless single-container hosting without VMs.

Q2: [Medium] Container group?
A2: Containers sharing lifecycle, network and volumes, like a Kubernetes pod.

Q3: [Hard] ACI vs Container Apps vs AKS?
A3: ACI is simplest for jobs; Container Apps adds autoscale/ingress/revisions; AKS gives full Kubernetes control with highest ops cost.

---

## ✅ Quick Checklist
□ Image from ACR with managed identity
□ Restart policy set
□ Deleted after job

---

## ⚡ 1-Line Summary
ACI = quick, per-second containers without orchestration. | ACI = बिना cluster के तुरंत container चलाना।

## ➡️ Next: Azure Kubernetes Service (AKS)
