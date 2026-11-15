# 283. Azure Static Web Apps
# AWS: AWS Amplify Hosting / S3 + CloudFront
# Azure: Azure Static Web Apps (SWA)
# हिंदी में: Azure Static Web Apps की बुनियाद

---

## 🔵 Simple Definition
SWA is a service for static front ends (React, Vue, Angular) plus optional serverless API (Azure Functions), with auth and routing rules built in.
हिंदी: SWA स्टैटिक फ्रंटएंड और वैकल्पिक सर्वरलेस API को ऑथ और रूटिंग के साथ होस्ट करता है।

---

## 🔴 Why it Exists
Frontend teams need HTTPS, CDN, auth, and API routing without managing servers.
SWA provides all of it from one config file.

---

## 🟢 How it Works
```
Browser -> SWA edge/CDN -> static files
                |-> /api/*    -> managed Functions or linked backend
                |-> /.auth/*  -> built-in login (GitHub, Entra ID)
                |-> routes in staticwebapp.config.json (roles, rewrites, headers)
```

---

## 💻 Code / Config Example
```json
// staticwebapp.config.json
{
  "routes": [
    { "route": "/admin/*", "allowedRoles": ["administrator"] },
    { "route": "/login", "redirect": "/.auth/login/github" }
  ],
  "responseOverrides": {
    "401": { "redirect": "/login", "statusCode": 302 }
  },
  "navigationFallback": { "rewrite": "/index.html" },
  "globalHeaders": { "X-Content-Type-Options": "nosniff" }
}
```
```bash
az staticwebapp create -n my-spa -g rg-demo \
  --source https://github.com/ORG/REPO --branch main \
  --app-location "/" --output-location "build" --login-with-github
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Amplify Hosting | Static Web Apps |
| Built-in auth | Cognito (separate) | /.auth providers |
| API | Lambda / API Gateway | Functions (managed or linked) |
| Pricing | Usage based | Free and Standard plans (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using SWA for server-rendered apps that need long-running servers.
✅ Correct: Use App Service or Container Apps for full backends.

❌ Mistake: Trusting client-side role checks only.
✅ Correct: Enforce roles in routes and validate again in the API.

---

## ⚫ Interview Q&A
Q1: [Easy] What is SWA good for?
A1: SPAs and static sites with CDN, HTTPS and CI/CD.

Q2: [Medium] How does auth work?
A2: Built-in `/.auth` endpoints with providers like GitHub and Entra ID; roles feed route rules.

Q3: [Hard] Managed Functions vs linked backend?
A3: Managed Functions are simple but limited; linking an App Service/Container App gives full runtime control, VNet integration and your own scaling.

---

## ✅ Quick Checklist
□ Config file committed
□ Custom domain + SSL
□ Roles enforced on API too

---

## ⚡ 1-Line Summary
SWA = static hosting + auth + API routing in one service. | SWA = होस्टिंग, ऑथ और API रूटिंग एक ही सर्विस में।

## ➡️ Next: 284. Azure API Management
