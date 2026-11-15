---

# 218. Azure DDoS Protection
# AWS: AWS Shield (Standard / Advanced)
# Azure: Azure DDoS Protection (Network Protection / IP Protection)
# हिंदी में: DDoS हमलों से बचाव

---

## 🔵 Simple Definition (2 lines)
Azure DDoS Protection detects and mitigates volumetric, protocol and resource-layer-3/4 attacks on public IPs.
हिंदी: Azure DDoS Protection public IPs पर होने वाले DDoS हमलों को पहचानकर रोकता है।

---

## 🔴 Why it Exists (2 lines)
Floods can take your API offline and run up bills.
Adaptive tuning learns your normal traffic and mitigates anomalies automatically.

---

## 🟢 How it Works
```
Internet attack traffic -> Azure edge (platform infrastructure protection: always on, free)
   With DDoS Protection plan: adaptive tuning + telemetry + attack metrics + rapid response*
   -> clean traffic -> Public IP (LB / App Gateway / VM)
Tiers: Network Protection (VNet-wide plan), IP Protection (per public IP)
(*Rapid response/cost protection are Network Protection features; verify in current docs.)
L7 attacks: use WAF on App Gateway / Front Door.
```

---

## 💻 Code / Config Example
```bash
# Create plan and attach to a VNet (Network Protection)
az network ddos-protection create -g rg-demo -n ddos-plan

DDOS_ID=$(az network ddos-protection show -g rg-demo -n ddos-plan --query id -o tsv)
az network vnet update -g rg-demo -n vnet-prod \
  --ddos-protection true --ddos-protection-plan "$DDOS_ID"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Basic protection | Shield Standard (free) | Infrastructure protection (free) |
| Paid | Shield Advanced (subscription) | Network Protection / IP Protection |
| L7 | AWS WAF | WAF on App Gateway / Front Door |
| Pricing | High monthly fee (approximate — check current docs) | Monthly per plan/IP (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming DDoS plan stops HTTP application-layer floods.
✅ Correct: Combine with WAF and rate limiting.

❌ Mistake: Buying a paid plan for a hobby/small VPS app.
✅ Correct: Basic protection plus Cloudflare/WAF is often enough; evaluate cost.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] AWS equivalent? A1: AWS Shield.
Q2: [Medium] Is any protection free? A2: Yes, platform-level infrastructure protection applies to all Azure public IPs.
Q3: [Hard] Full-stack design? A3: Front Door + WAF at the edge, DDoS Protection on VNet public IPs, autoscaling, alerts on DDoS metrics.

---

## ✅ Quick Checklist
□ Public IPs inventoried
□ Alerts on under-DDoS metric
□ WAF for L7
□ DDoS response plan written

---

## ⚡ 1-Line Summary
Azure DDoS Protection is Shield for Azure public IPs | Azure DDoS Protection, Azure public IPs के लिए AWS Shield जैसा है।

## ➡️ Next: 219. Azure SQL Database

---
