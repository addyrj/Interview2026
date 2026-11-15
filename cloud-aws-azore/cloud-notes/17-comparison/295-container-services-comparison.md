# 295. Container Services Comparison
# AWS: ECR, ECS, Fargate, EKS, App Runner
# Azure: ACR, Container Apps, ACI, AKS, App Service for Containers
# हिंदी में: कंटेनर सर्विसेज की तुलना

---

## 🔵 Simple Definition
Both clouds offer a registry, simple serverless container platforms, and managed Kubernetes.
हिंदी: दोनों में रजिस्ट्री, सरल सर्वरलेस कंटेनर प्लेटफॉर्म और मैनेज्ड Kubernetes मिलते हैं।

---

## 🔴 Why it Exists
Docker images need a place to be stored and a runtime that handles scaling, networking and health.

---

## 🟢 How it Works
```
Dockerfile -> build -> registry (ECR | ACR)
 Simple : App Runner | Container Apps   (HTTP service, autoscale)
 Medium : ECS+Fargate | ACI / Container Apps jobs
 Full k8s: EKS | AKS
```

---

## 💻 Code / Config Example
```bash
# Push image
aws ecr create-repository --repository-name api
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-south-1.amazonaws.com
docker tag api:1 123456789012.dkr.ecr.ap-south-1.amazonaws.com/api:1 && docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/api:1

az acr create -n myacr -g rg-demo --sku Basic
az acr login -n myacr
docker tag api:1 myacr.azurecr.io/api:1 && docker push myacr.azurecr.io/api:1
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Registry | ECR | ACR |
| Simple container service | App Runner | Container Apps |
| Orchestrator (own) | ECS | N/A (AWS-only concept; closest: Container Apps) |
| Kubernetes | EKS | AKS |
| Run one container | Fargate task | ACI |

---

## ⚠️ Common Mistakes
❌ Mistake: Choosing Kubernetes for 1-2 services.
✅ Correct: Container Apps / App Runner / ECS Fargate first.

❌ Mistake: Running containers as root with no scan.
✅ Correct: Non-root user, image scanning, minimal base image.

---

## ⚫ Interview Q&A
Q1: [Easy] ECR equivalent?
A1: ACR.

Q2: [Medium] What is Fargate-like in Azure?
A2: Container Apps and ACI are serverless container hosts; AKS also supports virtual nodes.

Q3: [Hard] ECS vs EKS decision?
A3: ECS is simpler and AWS-native; EKS gives portable Kubernetes APIs, ecosystem tools (Helm, operators) but more ops complexity.

---

## ✅ Quick Checklist
□ Immutable tags
□ Non-root image
□ Health checks and autoscaling

---

## ⚡ 1-Line Summary
ECR=ACR, Fargate=Container Apps, EKS=AKS. | ECR=ACR, Fargate=Container Apps, EKS=AKS।

## ➡️ Next: 296. IAM vs AAD Comparison
