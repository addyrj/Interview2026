# 282. Deploy React to Static Web Apps
# AWS: S3 + CloudFront (or AWS Amplify Hosting)
# Azure: Azure Static Web Apps
# हिंदी में: React ऐप को Static Web Apps पर डिप्लॉय करना

---

## 🔵 Simple Definition
Build the React app and let Azure Static Web Apps host it on a global CDN, with a GitHub Actions workflow auto-generated for CI/CD.
हिंदी: React का build Static Web Apps पर होस्ट होता है और हर push पर GitHub Actions से अपने-आप डिप्लॉय होता है।

---

## 🔴 Why it Exists
Hosting a SPA otherwise needs a storage bucket, CDN, HTTPS and a pipeline wired by hand.
SWA bundles hosting, SSL, preview URLs per pull request and deployment in one resource.

---

## 🟢 How it Works
```
git push / PR -> GitHub Actions (Azure/static-web-apps-deploy)
                    |  npm ci && npm run build  (Oryx)
                    v
              dist/ or build/ -> SWA global CDN -> HTTPS custom domain
PR opened  -> temporary preview environment URL
```

---

## 💻 Code / Config Example
```yaml
# .github/workflows/swa.yml
name: Deploy React to SWA
on:
  push: { branches: [main] }
  pull_request: { types: [opened, synchronize, reopened, closed], branches: [main] }
jobs:
  deploy:
    if: github.event_name == 'push' || github.event.action != 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: upload
          app_location: "/"            # React root
          output_location: "build"     # CRA = build, Vite = dist
  close:
    if: github.event_name == 'pull_request' && github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          action: close
```
```json
// staticwebapp.config.json - SPA fallback for React Router
{ "navigationFallback": { "rewrite": "/index.html", "exclude": ["/assets/*", "*.{css,js,png}"] } }
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | S3 + CloudFront / Amplify | Static Web Apps |
| PR previews | Amplify only | Built in |
| SPA routing | CloudFront error page to index.html | navigationFallback |
| Pricing | Pay per use | Free + Standard plan (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Wrong `output_location` (build vs dist) gives a blank site.
✅ Correct: Match your bundler's output folder.

❌ Mistake: 404 on page refresh for client routes.
✅ Correct: Add `navigationFallback` in `staticwebapp.config.json`.

---

## ⚫ Interview Q&A
Q1: [Easy] Where does the deployment token come from?
A1: The SWA resource; stored as a GitHub secret.

Q2: [Medium] How do you point React to a backend API?
A2: Linked backend (App Service/Functions/Container Apps) under `/api`, or set an absolute API URL via build-time env vars.

Q3: [Hard] How do you handle environment-specific config for a build?
A3: Vite/CRA env vars are baked in at build time, so inject them as `env:` in the workflow per branch; never put secrets in them.

---

## ✅ Quick Checklist
□ output_location correct
□ SPA fallback configured
□ No secrets in frontend env

---

## ⚡ 1-Line Summary
SWA = CDN-hosted React with built-in CI/CD and PR previews. | SWA = React के लिए CDN होस्टिंग, बिल्ट-इन CI/CD के साथ।

## ➡️ Next: 283. Azure Static Web Apps
