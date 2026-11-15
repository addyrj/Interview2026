---

# 3. IaaS vs PaaS vs SaaS
# AWS: EC2 (IaaS), Elastic Beanstalk (PaaS), WorkMail/Amazon Chime-type apps (SaaS)
# Azure: Virtual Machines (IaaS), App Service (PaaS), Microsoft 365 (SaaS)
# हिंदी में: सर्विस मॉडल: कितना आप संभालते हैं और कितना प्रोवाइडर

---

## 🔵 Simple Definition (2 lines)
IaaS gives raw infrastructure (VMs, disks, networks), PaaS gives a ready runtime where you deploy code, SaaS gives a finished app you just use.
हिंदी: IaaS में सर्वर आप संभालते हैं, PaaS में सिर्फ़ कोड, और SaaS में सिर्फ़ इस्तेमाल।

---

## 🔴 Why it Exists (2 lines)
Not every team wants to patch OSes or build runtimes.
Different layers of abstraction let you trade control for less operations work.

---

## 🟢 How it Works
```
Layer            On-prem  IaaS   PaaS   SaaS
Application        you    you    you    provider
Runtime/Data       you    you    you*   provider
OS                 you    you    prov   provider
Virtualization     you    prov   prov   provider
Hardware/Network   you    prov   prov   provider
(* you still own your data and config)

Examples: EC2 | Beanstalk, App Service, Cloud Run | Gmail, Office 365
```

---

## 💻 Code / Config Example
```bash
# PaaS: deploy a Node.js app to Azure App Service from local folder
az webapp up --name my-node-api-12345 --resource-group demo-rg \
  --runtime "NODE:20-lts" --sku B1

# IaaS: you must set up Node yourself on the VM
ssh ubuntu@<vm-ip> 'sudo apt-get update && sudo apt-get install -y nodejs npm'

# AWS PaaS: Elastic Beanstalk via EB CLI (pip install awsebcli)
eb init my-node-api --platform node.js --region ap-south-1
eb create prod-env
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| IaaS | EC2 | Virtual Machines |
| PaaS web apps | Elastic Beanstalk / App Runner | App Service |
| Serverless functions | Lambda (FaaS) | Azure Functions |
| SaaS example | WorkDocs/Amazon Connect | Microsoft 365, Dynamics 365 |

---

## ⚠️ Common Mistakes
❌ Mistake: Choosing IaaS by default, then spending weeks on patching.
✅ Correct: Start with PaaS/containers; drop to IaaS only if you need OS-level control.

❌ Mistake: Assuming SaaS means you have no security duties.
✅ Correct: You still own identities, access settings and data classification.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Give one example of each model.
A1: EC2/Azure VM (IaaS), Elastic Beanstalk/App Service (PaaS), Microsoft 365 (SaaS).

Q2: [Medium] Is Lambda PaaS or something else?
A2: It is FaaS, a serverless flavor of PaaS where you supply only functions and pay per invocation.

Q3: [Hard] How does the shared responsibility change across these?
A3: The provider's share grows from hardware (IaaS) to OS/runtime (PaaS) to the whole app (SaaS); customer always keeps data, identity and configuration.

---

## ✅ Quick Checklist
□ I can draw the responsibility stack
□ I pick the highest abstraction that meets requirements
□ I know FaaS and CaaS as in-between models

---

## ⚡ 1-Line Summary
Higher abstraction = less control but less ops | ऊपर का लेयर = कम कंट्रोल, कम मेहनत।

## ➡️ Next: 4. Public vs Private vs Hybrid Cloud

---
