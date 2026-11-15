# 316. Deploy to Azure App Service
# AWS: Elastic Beanstalk (closest PaaS) / App Runner
# Azure: App Service (Linux, Node 20) + GitHub Actions OIDC
# हिंदी में: बिना सर्वर संभाले Node.js ऐप को Azure App Service पर डिप्लॉय करना

---

## 🔵 Simple Definition
App Service is managed web hosting: you push code or a container, Azure handles OS, scaling, TLS and patching.
हिंदी: कोड पुश करो, OS, TLS और स्केलिंग Azure संभालता है।

## 🔴 Why it Exists
Fastest path to production for standard web apps without Kubernetes or VM management.

## 🟢 How it Works
```
git push main -> GitHub Actions -> azure/login (OIDC, no secret)
   -> azure/webapps-deploy (zip package) -> App Service plan (B1, Linux)
Staging slot -> warm up -> swap (zero downtime; needs Standard tier+)
Health check path /health removes unhealthy instances from rotation
```

## 💻 Code / Config Example
`main.bicep`: Linux plan (B1), web app with `NODE|20-lts`, HTTPS only, TLS 1.2, health check, system identity. `deploy.yml`: build + OIDC login + webapps-deploy@v3 (copy to `.github/workflows/`).
Not deployed or linted - Azure CLI and Actions runner not available here. Create the federated credential on the Entra app first.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| PaaS web hosting | Elastic Beanstalk / App Runner | App Service |
| Blue/green | EB swap URLs / CodeDeploy | Deployment slots + swap |
| CI auth | GitHub OIDC to IAM role | azure/login OIDC federated credential |
| Pricing | by plan SKU, per hour (approximate - check current docs) | same |

## 💰 Cost / HA / Security
- Cost: plan is billed even if idle; many apps can share one plan. Free/Shared tiers have no Always On.
- HA: 2+ instances in plan, health check, zone redundancy on Premium; slots for safe release.
- Security: httpsOnly, ftps disabled, managed identity to Key Vault, no publish profile secrets (use OIDC).

## ⚠️ Common Mistakes
❌ Using publish-profile secret in CI.
✅ OIDC federated credential.

❌ App listens on hard-coded port.
✅ Read `process.env.PORT`.

## ⚫ Interview Q&A
Q1 [Easy]: What is an App Service plan?
A1: The compute (VM size, instance count) that one or more web apps share; it determines price and features.

Q2 [Medium]: How do you deploy with zero downtime?
A2: Deploy to a staging slot, warm it up, then swap slots; roll back by swapping again.

Q3 [Hard]: App is slow only after deploy; what do you check?
A3: Cold start / Always On off, slot warm-up, health check config, instance count, App Insights for dependency latency, memory limits of the plan.

## ✅ Quick Checklist
□ Always On + health check
□ OIDC login in CI
□ Slots for production

## ⚡ 1-Line Summary
App Service = managed hosting; OIDC pipeline + slot swap = safe deploys. | App Service = मैनेज्ड होस्टिंग; OIDC + स्लॉट स्वैप = सुरक्षित डिप्लॉय।

## ➡️ Next: 317. Setup Azure CosmosDB
