# 286. Compute Services Comparison
# AWS: EC2, Elastic Beanstalk, ECS/Fargate, Lambda
# Azure: Virtual Machines, App Service, Container Apps/ACI, Functions
# हिंदी में: कंप्यूट सर्विसेज की तुलना

---

## 🔵 Simple Definition
Both clouds offer a ladder from raw VMs to PaaS to containers to serverless; pick by how much control vs ops you want.
हिंदी: दोनों क्लाउड में VM से सर्वरलेस तक की सीढ़ी है, कंट्रोल बनाम ऑप्स देखकर चुनें।

---

## 🔴 Why it Exists
"Which service runs my Node.js/FastAPI app?" is the first design decision.
A mapping table avoids picking the wrong abstraction level.

---

## 🟢 How it Works
```
More control / more ops                          Less control / less ops
VM (EC2 / Azure VM) -> PaaS (Beanstalk / App Service)
  -> Containers (ECS-Fargate / Container Apps) -> Functions (Lambda / Azure Functions)
```

---

## 💻 Code / Config Example
```bash
# Same goal: run a container image publicly
# AWS (App Runner/Fargate need more setup; ECS CLI shown minimal)
aws ecs create-cluster --cluster-name demo

# Azure: one command with Container Apps
az containerapp up -n api -g rg-demo --image myacr.azurecr.io/api:1.0 --target-port 3000 --ingress external
```

---

## 📊 AWS vs Azure Quick Compare
| Need | AWS | Azure |
|------|-----|-------|
| Virtual machine | EC2 | Virtual Machines |
| Managed web app | Elastic Beanstalk / App Runner | App Service |
| Serverless containers | ECS Fargate | Container Apps / ACI |
| Kubernetes | EKS | AKS |
| Functions | Lambda | Azure Functions |
| Batch | AWS Batch | Azure Batch |

---

## ⚠️ Common Mistakes
❌ Mistake: Running a simple API on Kubernetes.
✅ Correct: Start with App Service/App Runner/Container Apps.

❌ Mistake: Lambda/Functions for long-running jobs.
✅ Correct: Use containers or batch for long work (functions have time limits - check docs).

---

## ⚫ Interview Q&A
Q1: [Easy] EC2 equivalent in Azure?
A1: Virtual Machines.

Q2: [Medium] Elastic Beanstalk equivalent?
A2: App Service.

Q3: [Hard] How choose between Functions and containers?
A3: Functions for event-driven, spiky, short tasks; containers for steady load, custom runtimes, long tasks or portability.

---

## ✅ Quick Checklist
□ Match workload to abstraction level
□ Consider cold starts and time limits
□ Consider team Kubernetes skills

---

## ⚡ 1-Line Summary
Same ladder on both clouds: VM, PaaS, containers, functions. | दोनों में एक ही सीढ़ी: VM, PaaS, कंटेनर, फंक्शन।

## ➡️ Next: 287. Database Services Comparison
