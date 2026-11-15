# 194. Azure App Service
# AWS: Elastic Beanstalk (closest) / App Runner
# Azure: Azure App Service (Web Apps)
# हिंदी में: बिना सर्वर संभाले वेब ऐप/API होस्ट करने की managed सेवा

---

## 🔵 Simple Definition
A managed PaaS to host web apps, APIs and containers (Node, Python, .NET, Java) with TLS, scaling and deployment slots.
App Service में आप कोड या container डालते हैं; OS, patching और scaling Azure संभालता है।

---

## 🔴 Why it Exists
Teams want to ship an API without managing VMs, load balancers and patching.

---

## 🟢 How it Works
```
Code zip / GitHub Actions / Docker image
      |
App Service Plan (the compute: size + instance count)
      |-- Web App 1 (NestJS)     https://app-orders.azurewebsites.net
      |-- Web App 2 (FastAPI container)
Features: custom domain + managed cert, slots, autoscale, VNet integration
```

---

## 💻 Code / Config Example
```bash
az group create -n rg-web -l centralindia
az appservice plan create -g rg-web -n plan-web --is-linux --sku B1
az webapp create -g rg-web -p plan-web -n orders-api-demo-123 \
  --runtime "NODE:20-lts"
az webapp config appsettings set -g rg-web -n orders-api-demo-123 \
  --settings NODE_ENV=production PORT=8080
az webapp config set -g rg-web -n orders-api-demo-123 \
  --startup-file "node dist/main.js"
az webapp log tail -g rg-web -n orders-api-demo-123
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Elastic Beanstalk / App Runner | App Service |
| Containers | App Runner / ECS | Web App for Containers |
| Staging | Beanstalk swap URL (blue/green) | Deployment slots |
| Pricing | Underlying resources | Per plan instance (approximate - check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: App listens on a hard-coded port.
✅ Correct: Read `process.env.PORT` (or WEBSITES_PORT for containers).

❌ Mistake: Relying on local disk for uploads.
✅ Correct: Use Blob Storage; instances can move.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a Web App?
A1: A hosted app running in a plan's compute.

Q2: [Medium] What are slots?
A2: Live staging instances of an app; swap for zero-downtime releases and rollback.

Q3: [Hard] App Service vs AKS vs Functions for a NestJS API?
A3: App Service for simple always-on APIs with low ops; AKS for many microservices and custom orchestration; Functions for event-driven, bursty work.

---

## ✅ Quick Checklist
□ HTTPS only on
□ Secrets from Key Vault references
□ Health check path configured

---

## ⚡ 1-Line Summary
App Service = managed hosting for web apps and APIs. | App Service = वेब ऐप/API के लिए managed होस्टिंग।

## ➡️ Next: App Service Plans
