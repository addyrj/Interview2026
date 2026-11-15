# 193. VM Scale Sets
# AWS: EC2 Auto Scaling Groups
# Azure: Virtual Machine Scale Sets (VMSS)
# हिंदी में: एक जैसी VMs का समूह जो लोड के हिसाब से अपने-आप घटता-बढ़ता है

---

## 🔵 Simple Definition
VMSS manages a group of identical VMs with autoscale rules and a load balancer.
VMSS एक जैसी VMs का ग्रुप है जो लोड के अनुसार अपने-आप बढ़ता-घटता है।

---

## 🔴 Why it Exists
Manual VM counts cannot follow traffic; you need self-healing, even spread and scale.

---

## 🟢 How it Works
```
Image/model -> VMSS (instances 2..10) across zones
Autoscale: metric (CPU > 70% for 5 min) -> +1 ; (CPU < 30%) -> -1
Load Balancer / App Gateway -> health probe -> only healthy instances
Orchestration: Flexible (recommended) or Uniform
```

---

## 💻 Code / Config Example
```bash
az vmss create -g rg-vm -n vmss-api \
  --image Ubuntu2204 --vm-sku Standard_B2s \
  --instance-count 2 --zones 1 2 3 \
  --upgrade-policy-mode Automatic \
  --admin-username azureuser --generate-ssh-keys \
  --lb-sku Standard

az monitor autoscale create -g rg-vm --resource vmss-api \
  --resource-type Microsoft.Compute/virtualMachineScaleSets \
  --name as-api --min-count 2 --max-count 6 --count 2
az monitor autoscale rule create -g rg-vm --autoscale-name as-api \
  --condition "Percentage CPU > 70 avg 5m" --scale out 1
az monitor autoscale rule create -g rg-vm --autoscale-name as-api \
  --condition "Percentage CPU < 30 avg 5m" --scale in 1
```
(Check `az vmss create -h` for orchestration-mode flags in your CLI version.)

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Auto Scaling Group | VMSS |
| Scaling policy | Target tracking / step | Autoscale rules / schedule |
| Template | Launch Template | Model + image |
| Pricing | Pay for instances only | Pay for instances only |

---

## ⚠️ Common Mistakes
❌ Mistake: Scale in rule too aggressive, causing flapping.
✅ Correct: Wider thresholds and cooldown.

❌ Mistake: Storing state/sessions on instances.
✅ Correct: Externalize to Redis/DB/Blob.

---

## ⚫ Interview Q&A
Q1: [Easy] Why VMSS?
A1: Automatic scaling and self-healing of identical VMs.

Q2: [Medium] Flexible vs Uniform?
A2: Flexible allows mixing VM types and standalone-like VMs and is the recommended mode; Uniform requires identical instances.

Q3: [Hard] Zero-downtime rollout?
A3: Rolling upgrades with health probes/app health extension and max-surge; or bake new images and swap.

---

## ✅ Quick Checklist
□ Min 2 instances across zones
□ Health probe configured
□ Stateless app

---

## ⚡ 1-Line Summary
VMSS = Auto Scaling Group for Azure VMs. | VMSS = Azure VMs का Auto Scaling Group।

## ➡️ Next: Azure App Service
