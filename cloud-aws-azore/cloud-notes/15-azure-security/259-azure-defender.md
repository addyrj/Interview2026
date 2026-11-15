---

# 259. Azure Defender
# AWS: Amazon GuardDuty (+ Inspector, Macie)
# Azure: Microsoft Defender for Cloud plans (formerly Azure Defender)
# हिंदी में: Defender = वर्कलोड (VM, कंटेनर, DB, स्टोरेज) पर खतरे पहचानने वाली सुरक्षा

---

## 🔵 Simple Definition (2 lines)
Defender plans add threat detection and protection to specific resource types such as servers, containers, databases and storage.
Defender हर रिसोर्स टाइप के लिए अलग सुरक्षा देता है और संदिग्ध गतिविधि पर अलर्ट करता है।

---

## 🔴 Why it Exists (2 lines)
Posture checks do not stop an active attack like brute force or malware upload.
Runtime protection detects and alerts on live threats.

---

## 🟢 How it Works
```
Defender for Cloud (enable per subscription)
  Plans: Servers | Containers (AKS/ACR) | App Service | Storage | SQL/Databases | Key Vault | DNS...
  Signals: agent / platform telemetry + Microsoft threat intelligence
  Output: Security alerts (MITRE-mapped) -> Defender portal / Sentinel / email / workflow automation
Examples: malware uploaded to Blob, SSH brute force on a VM, anomalous Key Vault access
```

---

## 💻 Code / Config Example
```bash
# See which plans are on
az security pricing list --query "[].{plan:name, tier:pricingTier}" -o table

# Turn on Servers (Plan 2) and Containers
az security pricing create -n VirtualMachines --tier Standard --subplan P2
az security pricing create -n Containers --tier Standard

# Email on high severity alerts
az security contact create -n default --emails secops@example.com \
  --alert-notifications on --alerts-admins on
```
Flags and plan names evolve; confirm with `az security pricing list`.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Threat detection | GuardDuty | Defender plans |
| Vuln scanning | Inspector | Defender for Servers / Containers |
| Sensitive data | Macie | Defender for Storage (malware/sensitive data scan) |
| Pricing | Per events/GB analysed (approximate - check current docs) | Per resource per month by plan (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Enabling every plan on dev subscriptions, spending needlessly.
✅ Correct: Enable by risk; protect production first.

❌ Mistake: Alerts going to a mailbox nobody reads.
✅ Correct: Route to Sentinel/ticketing with an on-call owner.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Defender vs Security Center?
A1: Security Center posture features and Azure Defender protection plans are unified as Defender for Cloud.

Q2: [Medium] Is it agent-based?
A2: Depends on plan: servers use Defender for Endpoint integration/agentless scanning; storage and Key Vault are agentless, platform-level.

Q3: [Hard] Respond to a Blob malware alert?
A3: Quarantine/delete blob, check uploader identity and SAS tokens, rotate keys, review logs, and add scan-on-upload to the pipeline.

---

## ✅ Quick Checklist
□ Plans enabled for prod resource types
□ Security contacts set
□ Alerts exported to SIEM

---

## ⚡ 1-Line Summary
Defender plans detect live threats on your workloads | Defender वर्कलोड पर चल रहे हमलों को पहचानकर अलर्ट देता है।

## ➡️ Next: 260. Microsoft Entra ID

---
