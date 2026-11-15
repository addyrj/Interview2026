---

# 263. AZURE ADVISOR
# AWS: AWS Trusted Advisor (+ Compute Optimizer)
# Azure: Azure Advisor
# हिंदी में: एज़्योर एडवाइज़र

---

## 🔵 Simple Definition (2 lines)
Azure Advisor analyses your resources and gives free recommendations across Cost, Security, Reliability, Operational Excellence and Performance.
हिंदी: Advisor आपके रिसोर्स देखकर बताता है कि खर्च कैसे घटाएँ और सुरक्षा/भरोसा कैसे बढ़ाएँ।

---

## 🔴 Why it Exists (2 lines)
Teams over-provision and miss best practices. Advisor surfaces idle VMs, missing backups, and unsafe configs automatically.

---

## 🟢 How it Works
```
Telemetry of your resources
   -> Advisor rules engine
      -> Recommendations grouped by 5 pillars
         (Cost | Security | Reliability | Operational Excellence | Performance)
      -> Act, postpone, or dismiss; optional alerts
```

---

## 💻 Code / Config Example
```bash
# List all cost recommendations
az advisor recommendation list --category Cost -o table

# Refresh recommendations
az advisor recommendation list --refresh

# Configure low-CPU threshold for VM right-size suggestions
az advisor configuration update --low-cpu-threshold 20
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Trusted Advisor | Advisor |
| Categories | Cost, Performance, Security, Fault tolerance, Service limits | Cost, Security, Reliability, Operational Excellence, Performance |
| Free tier | Core checks free; full checks need Business/Enterprise support | Advisor is free |
| Alerts | EventBridge | Advisor alerts / Activity Log |

---

## ⚠️ Common Mistakes
❌ Mistake: Ignoring recommendations for months.
✅ Correct: Review monthly and assign owners; postpone with a reason.

❌ Mistake: Right-sizing a VM by CPU alone.
✅ Correct: Check memory, burst patterns, and peak traffic first.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Azure Advisor?
A1: A free personalised recommendation engine across five pillars.

Q2: [Medium] How does it relate to Well-Architected Framework?
A2: Its pillars map to WAF pillars; Advisor Score quantifies adoption of recommendations.

Q3: [Hard] How would you automate acting on recommendations?
A3: Export via the Advisor API/CLI or Resource Graph, open work items in Azure Boards, and use Advisor alerts to notify owners; apply changes through IaC, not portal clicks.

---

## ✅ Quick Checklist
□ Check Advisor Score monthly
□ Delete idle/unattached disks and IPs
□ Enable alerts for high-impact items

---

## ⚡ 1-Line Summary
Advisor = free best-practice and savings suggestions | Advisor = मुफ्त सलाहकार जो बचत और सुरक्षा सुझाता है।

## ➡️ Next: Azure Service Health

---
