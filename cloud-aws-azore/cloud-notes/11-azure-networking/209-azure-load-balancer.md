---

# 209. Azure Load Balancer
# AWS: Network Load Balancer (NLB) / Gateway Load Balancer
# Azure: Azure Load Balancer
# हिंदी में: Layer-4 (TCP/UDP) traffic बाँटने वाला

---

## 🔵 Simple Definition (2 lines)
Azure Load Balancer distributes TCP/UDP traffic (Layer 4) across healthy VMs or instances in a backend pool.
हिंदी: Azure Load Balancer TCP/UDP traffic को backend VMs में बराबर बाँटता है।

---

## 🔴 Why it Exists (2 lines)
One VM is a single point of failure and a capacity limit.
The LB spreads load and removes unhealthy nodes using health probes.

---

## 🟢 How it Works
```
Client -> Frontend IP (public or internal)
        -> LB rule (port 80 -> 3000) + health probe
        -> Backend pool: VM1, VM2, VM3 (or VMSS)
Hash-based 5-tuple distribution; no TLS termination, no URL routing.
SKUs: Basic (retired), Standard (zone-redundant, secure by default - needs NSG)
```

---

## 💻 Code / Config Example
```bash
az network public-ip create -g rg-demo -n lb-pip --sku Standard
az network lb create -g rg-demo -n lb-web --sku Standard \
  --public-ip-address lb-pip --frontend-ip-name fe --backend-pool-name be

az network lb probe create -g rg-demo --lb-name lb-web -n http-probe \
  --protocol Http --port 3000 --path /health

az network lb rule create -g rg-demo --lb-name lb-web -n http-rule \
  --protocol Tcp --frontend-port 80 --backend-port 3000 \
  --frontend-ip-name fe --backend-pool-name be --probe-name http-probe
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| L4 LB | NLB | Azure Load Balancer |
| L7 LB | ALB | Application Gateway |
| Scope | Regional | Regional (Cross-region LB tier available) |
| Pricing | Hourly + LCU (approximate — check current docs) | Rules-based + data processed (Standard) (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Expecting URL/host routing or TLS offload.
✅ Correct: Use Application Gateway/Front Door for L7.

❌ Mistake: Standard LB with no NSG, traffic dropped.
✅ Correct: Standard SKU is closed by default; allow ports in the NSG.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which OSI layer does Azure LB work at? A1: Layer 4.
Q2: [Medium] Public vs internal LB? A2: Public has a public frontend IP; internal uses a private IP inside a VNet for tier-to-tier traffic.
Q3: [Hard] How do you get zone resilience? A3: Standard SKU with zone-redundant frontend and backends spread across zones.

---

## ✅ Quick Checklist
□ Standard SKU
□ Health probe on /health
□ NSG allows traffic
□ Backends across zones

---

## ⚡ 1-Line Summary
Azure LB is a fast Layer-4 balancer (like NLB) | Azure LB तेज़ Layer-4 load balancer है, NLB जैसा।

## ➡️ Next: 210. Azure Application Gateway

---
