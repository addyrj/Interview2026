---

# 201. Azure Container Registry (ACR)
# AWS: Amazon ECR (Elastic Container Registry)
# Azure: Azure Container Registry (ACR)
# हिंदी में: Docker images रखने की private अलमारी

---

## 🔵 Simple Definition (2 lines)
ACR is a managed private registry that stores and serves your Docker/OCI images and Helm charts.
हिंदी: ACR आपकी Docker images को private और सुरक्षित तरीके से रखने वाली managed registry है।

---

## 🔴 Why it Exists (2 lines)
Docker Hub is public and rate-limited; production needs a private, geo-close, access-controlled image store.
ACR integrates with Entra ID, AKS, App Service and Container Apps, so no passwords are copied around.

---

## 🟢 How it Works
```
Dev/GitHub Actions --docker push--> ACR (myreg.azurecr.io)
                                      |  (image scan, tasks, geo-replication on Premium)
AKS / Container Apps / App Service <--docker pull (managed identity, AcrPull role)
```

---

## 💻 Code / Config Example
```bash
# Create registry (name must be globally unique, 5-50 alphanumeric)
az group create -n rg-demo -l centralindia
az acr create -n myapiacr123 -g rg-demo --sku Basic

# Login + push a NestJS/FastAPI image
az acr login -n myapiacr123
docker build -t myapiacr123.azurecr.io/api:1.0.0 .
docker push myapiacr123.azurecr.io/api:1.0.0

# Build in the cloud (no local Docker needed)
az acr build -r myapiacr123 -t api:1.0.1 .

# Let AKS pull images without secrets
az aks update -n my-aks -g rg-demo --attach-acr myapiacr123
```
```yaml
# GitHub Actions: push to ACR
- uses: azure/docker-login@v2
  with:
    login-server: myapiacr123.azurecr.io
    username: ${{ secrets.ACR_USER }}
    password: ${{ secrets.ACR_PASS }}
- run: |
    docker build -t myapiacr123.azurecr.io/api:${{ github.sha }} .
    docker push myapiacr123.azurecr.io/api:${{ github.sha }}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | ECR | ACR |
| Tiers | Private/Public repos | Basic, Standard, Premium |
| Geo-replication | Cross-region replication rules | Premium geo-replication |
| Auth | IAM + `aws ecr get-login-password` | Entra ID / managed identity / `az acr login` |
| Pricing | Per GB storage + data transfer (approximate — check current docs) | Daily fee per tier + storage (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Enabling the admin user and sharing its password in CI.
✅ Correct: Use a service principal/managed identity with `AcrPull` / `AcrPush` roles.

❌ Mistake: Always deploying `:latest`.
✅ Correct: Tag with the git SHA or semver; keep tags immutable by convention.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is ACR? A1: Azure's managed private Docker/OCI registry, the equivalent of ECR.
Q2: [Medium] How does AKS pull from ACR securely? A2: AKS kubelet managed identity gets the `AcrPull` role (`--attach-acr`), so no image-pull secrets are needed.
Q3: [Hard] How do you serve images fast to multi-region clusters? A3: Premium SKU geo-replication gives one registry name with regional replicas; add private endpoints to keep pulls off the public internet.

---

## ✅ Quick Checklist
□ Admin user disabled
□ Images tagged by SHA/semver
□ AcrPull role given to runtime identity
□ Retention/purge policy for old images

---

## ⚡ 1-Line Summary
ACR is Azure's private image store (like ECR) | ACR Azure की private image store है, जैसे AWS में ECR।

## ➡️ Next: 202. Azure Batch

---
