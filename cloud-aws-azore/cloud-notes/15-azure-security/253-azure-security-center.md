---

# 253. Azure Security Center
# AWS: AWS Security Hub (+ Inspector, Config)
# Azure: Microsoft Defender for Cloud (formerly Azure Security Center)
# हिंदी में: Security Center = आपके क्लाउड की सुरक्षा स्थिति जाँचने और सुधारने का डैशबोर्ड

---

## 🔵 Simple Definition (2 lines)
Security Center (now Microsoft Defender for Cloud) scans your resources, scores your security posture and recommends fixes.
यह बताता है कि आपके क्लाउड में कौन सी सेटिंग असुरक्षित है और उसे कैसे ठीक करें।

---

## 🔴 Why it Exists (2 lines)
Misconfigurations (public storage, open ports) cause most breaches.
Continuous posture checks catch them before attackers do.

---

## 🟢 How it Works
```
Subscriptions/resources -> Defender for Cloud
   |- CSPM (free tier): Secure Score + recommendations (benchmark policies)
   |- CWP (paid Defender plans): threat detection for servers, containers, storage, SQL...
   \- Regulatory compliance dashboard (CIS, PCI, ISO...)
Alerts/recommendations -> Azure Monitor / Sentinel / email / Logic Apps
```
Name note: Security Center and Azure Defender were merged into "Microsoft Defender for Cloud".

---

## 💻 Code / Config Example
```bash
# List recommendations (assessments) and secure score
az security assessment list --query "[?status.code=='Unhealthy'].{name:displayName}" -o table
az security secure-scores list -o table

# Enable a paid Defender plan (example: Storage)
az security pricing create -n StorageAccounts --tier Standard
# Free tier back
az security pricing create -n StorageAccounts --tier Free

# AWS comparison
# aws securityhub enable-security-hub
# aws securityhub get-findings --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}]}'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Posture score | Security Hub | Defender for Cloud Secure Score |
| Vulnerability scan | Inspector | Defender for Servers (Qualys/MDVM) |
| Config rules | AWS Config | Azure Policy |
| Pricing | Per check/finding (approximate - check current docs) | Free CSPM basics, paid plans per resource (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Enabling it and never acting on recommendations.
✅ Correct: Assign owners, fix high-severity items first, track Secure Score.

❌ Mistake: Using the old name only in scripts/docs.
✅ Correct: Search by "Defender for Cloud"; CLI group remains `az security`.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does it give you?
A1: Security posture assessment, recommendations and threat protection.

Q2: [Medium] CSPM vs CWP?
A2: CSPM finds misconfigurations (posture); CWP detects threats on workloads (paid plans).

Q3: [Hard] Enforce, not just detect?
A3: Pair with Azure Policy (deny / deployIfNotExists) and IaC checks in CI so bad configs never deploy.

---

## ✅ Quick Checklist
□ Defender for Cloud enabled on all subscriptions
□ Critical recommendations assigned
□ Alerts exported to Sentinel/Monitor

---

## ⚡ 1-Line Summary
Defender for Cloud scores and fixes your security posture | Defender for Cloud आपकी सुरक्षा स्थिति जाँचकर सुधार बताता है।

## ➡️ Next: 254. Azure Key Vault

---
