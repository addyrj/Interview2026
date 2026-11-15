# 196. App Service Deployment
# AWS: Elastic Beanstalk deploy / CodeDeploy
# Azure: App Service deployment (zip, GitHub Actions, slots, containers)
# हिंदी में: App Service पर कोड कैसे पहुँचाएँ - zip, GitHub Actions या container से

---

## 🔵 Simple Definition
Ways to publish: zip deploy, GitHub Actions, container image from ACR/Docker Hub, and slot swaps for zero downtime.
कोड भेजने के कई तरीके हैं; slot swap से बिना downtime release होता है।

---

## 🔴 Why it Exists
Repeatable, automated releases with rollback instead of FTP-style copying.

---

## 🟢 How it Works
```
git push -> GitHub Actions: build + test
   -> deploy to "staging" slot -> smoke test
   -> swap staging <-> production (warm-up, instant rollback by swapping back)
```
Slots require Standard tier or higher.

---

## 💻 Code / Config Example
```yaml
name: deploy-api
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci && npm run build && npm prune --omit=dev
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - uses: azure/webapps-deploy@v3
        with:
          app-name: orders-api-demo-123
          slot-name: staging
          package: .
      - run: az webapp deployment slot swap -g rg-web -n orders-api-demo-123 --slot staging --target-slot production
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Blue/green | Beanstalk swap / CodeDeploy | Slot swap |
| CI/CD | CodePipeline / GHA | Azure Pipelines / GHA |
| Containers | ECR + ECS/App Runner | ACR + Web App for Containers |

---

## ⚠️ Common Mistakes
❌ Mistake: Deploying straight to production slot.
✅ Correct: Deploy to staging, test, swap.

❌ Mistake: Slot-sticky settings forgotten (connection strings).
✅ Correct: Mark environment-specific settings as slot settings.

---

## ⚫ Interview Q&A
Q1: [Easy] How to roll back?
A1: Swap the slots again.

Q2: [Medium] Why OIDC login?
A2: No long-lived secret stored in GitHub.

Q3: [Hard] Database migrations with swaps?
A3: Use backward-compatible (expand/contract) migrations so both versions work during swap.

---

## ✅ Quick Checklist
□ Staging slot + health check
□ OIDC login
□ Slot settings flagged

---

## ⚡ 1-Line Summary
Deploy to a slot, verify, swap. | Slot में deploy करें, जाँचें, फिर swap करें।

## ➡️ Next: Azure Functions
