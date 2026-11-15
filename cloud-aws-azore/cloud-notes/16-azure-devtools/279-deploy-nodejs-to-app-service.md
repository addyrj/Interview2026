---

# 279. DEPLOY NODE.JS TO APP SERVICE
# AWS: Elastic Beanstalk / App Runner
# Azure: Azure App Service (Linux)
# हिंदी में: Node.js को App Service पर डिप्लॉय करना

---

## 🔵 Simple Definition (2 lines)
App Service is a managed PaaS for web apps: you upload code (zip/GitHub Actions) and Azure runs Node, handles TLS, scaling and patches.
हिंदी: App Service में कोड अपलोड करो, सर्वर, TLS और स्केलिंग Azure संभालता है।

---

## 🔴 Why it Exists (2 lines)
Running Node on a VPS means managing OS, nginx, certs and restarts. PaaS removes that toil.

---

## 🟢 How it Works
```
Resource group
  └─ App Service Plan (Linux, SKU = CPU/RAM/price)
       └─ Web App (runtime NODE|20-lts)
Deploy: zip deploy / GitHub Actions / Pipelines  -> Oryx build (npm install)
Start:  `npm start` (or custom startup command), listens on process.env.PORT
Settings -> env vars | Managed identity -> Key Vault | Deployment slots
```

---

## 💻 Code / Config Example
```bash
az group create -n rg-prod -l centralindia
az appservice plan create -g rg-prod -n plan-api --is-linux --sku B1
az webapp create -g rg-prod -p plan-api -n api-prod-unique123 --runtime "NODE:20-lts"

az webapp config appsettings set -g rg-prod -n api-prod-unique123 \
  --settings NODE_ENV=production SCM_DO_BUILD_DURING_DEPLOYMENT=true

# zip deploy from local
zip -r app.zip . -x "node_modules/*" ".git/*"
az webapp deploy -g rg-prod -n api-prod-unique123 --src-path app.zip --type zip
az webapp log tail -g rg-prod -n api-prod-unique123
```
```javascript
// server.js : must bind to the platform port
const http = require("http");
const port = process.env.PORT || 3000;
http.createServer((_, res) => res.end("ok")).listen(port);
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Elastic Beanstalk / App Runner | App Service |
| Zero-downtime | Blue/green env swap | Deployment slots swap |
| Containers | App Runner / ECS | Web App for Containers |
| Pricing | Underlying EC2/usage | Per plan SKU hour (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Hardcoding port 3000.
✅ Correct: Use `process.env.PORT`.

❌ Mistake: Deploying node_modules, or no build step.
✅ Correct: Let Oryx build (`SCM_DO_BUILD_DURING_DEPLOYMENT=true`) or build in CI.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] App Service Plan?
A1: The compute (VM size/instances) shared by apps in it; billed per plan.

Q2: [Medium] Deployment slots?
A2: Staging environments you warm up then swap to production for zero downtime and rollback.

Q3: [Hard] App is slow after scale-out and returns 502 on start?
A3: Check app listens on PORT, startup time vs warmup limits, Always On, health check path, and logs in Log stream/Kudu.

---

## ✅ Quick Checklist
□ HTTPS only, TLS 1.2
□ Slot for staging
□ Managed identity, no secrets in settings

---

## ⚡ 1-Line Summary
App Service = managed hosting for Node apps | App Service = Node ऐप के लिए मैनेज्ड होस्टिंग।

## ➡️ Next: Deploy FastAPI to App Service

---
