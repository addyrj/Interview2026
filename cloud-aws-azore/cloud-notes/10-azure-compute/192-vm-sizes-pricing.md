# 192. VM Sizes + Pricing
# AWS: EC2 instance types + pricing models
# Azure: VM series/sizes + pricing options
# हिंदी में: सही VM साइज़ चुनना और सस्ते भुगतान विकल्प समझना

---

## 🔵 Simple Definition
A size = vCPU + RAM + disk/network limits, grouped in families (B burstable, D general, E memory, F compute, N GPU).
Size में vCPU, RAM और नेटवर्क सीमाएँ होती हैं; काम के हिसाब से family चुनें।

---

## 🔴 Why it Exists
Over-sizing wastes money; under-sizing hurts performance.

---

## 🟢 How it Works
```
Name: Standard_D4s_v5  = family D, 4 vCPU, s = premium storage capable, v5 = generation
Families: B (burst, dev/test) | D (general) | E (memory) | F (CPU) | N (GPU)
Pricing options:
  Pay-as-you-go -> Reservation (1/3 yr) / Savings Plan -> Spot (evictable, cheap)
  + Azure Hybrid Benefit for Windows/SQL licenses
```
Prices vary by region and change - approximate, check the pricing calculator.

---

## 💻 Code / Config Example
```bash
# List sizes available in a region
az vm list-sizes -l centralindia --query "[?numberOfCores<=4].{n:name,cpu:numberOfCores,mem:memoryInMB}" -o table
# Check availability/restrictions of a SKU
az vm list-skus -l centralindia --size Standard_B --resource-type virtualMachines -o table
# Spot VM (cheap, can be evicted)
az vm create -g rg-vm -n vm-batch --image Ubuntu2204 --size Standard_D2s_v5 \
  --priority Spot --max-price -1 --eviction-policy Deallocate --generate-ssh-keys
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Burstable | t3/t4g | B-series |
| Commitment | Savings Plans / RIs | Reservations / Savings Plans |
| Spot | Spot Instances | Spot VMs |
| ARM chips | Graviton | Cobalt / Ampere (Dpsv5 etc.) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using B-series for sustained high CPU.
✅ Correct: Burst credits run out; use D-series.

❌ Mistake: Spot for stateful databases.
✅ Correct: Spot for batch/CI runners that tolerate eviction.

---

## ⚫ Interview Q&A
Q1: [Easy] Which family for dev/test?
A1: B-series, cheapest for low average CPU.

Q2: [Medium] Reservation vs Savings Plan?
A2: Reservation locks a specific size/region for more discount; Savings Plan commits to hourly spend with more flexibility.

Q3: [Hard] Cut costs for a steady API plus nightly jobs?
A3: Reservation for the baseline, Spot for nightly jobs, right-size via Advisor metrics, auto-shutdown non-prod.

---

## ✅ Quick Checklist
□ Metrics checked before sizing
□ Region quota verified
□ Commitment only for steady load

---

## ⚡ 1-Line Summary
Pick the family by workload and pay less with commitments or Spot. | Workload के हिसाब से family चुनें, Reservation/Spot से बचत करें।

## ➡️ Next: VM Scale Sets
