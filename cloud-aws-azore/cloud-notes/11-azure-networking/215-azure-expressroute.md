---

# 215. Azure ExpressRoute
# AWS: AWS Direct Connect
# Azure: Azure ExpressRoute
# हिंदी में: on-prem से Azure तक private dedicated लाइन

---

## 🔵 Simple Definition (2 lines)
ExpressRoute is a private, dedicated connection from your network to Azure through a connectivity provider, bypassing the public internet.
हिंदी: ExpressRoute provider के ज़रिए on-prem से Azure तक private dedicated connection है, internet के बिना।

---

## 🔴 Why it Exists (2 lines)
Large data transfers and regulated workloads need predictable latency, bandwidth and no internet exposure.
VPNs over the internet can vary in performance.

---

## 🟢 How it Works
```
On-prem --- provider / colocation (MSEE routers) ---> Azure
   Circuit (service key, bandwidth, peering location)
     |-- Private peering   -> VNets via ExpressRoute Gateway
     |-- Microsoft peering -> Microsoft 365 / public Azure services
BGP exchanges routes; two redundant links per circuit.
```

---

## 💻 Code / Config Example
```bash
# Circuit (provider and location values must match a real provider/location)
az network express-route create -g rg-demo -n er-circuit -l centralindia \
  --bandwidth 200 --provider "Equinix" --peering-location "Chennai" \
  --sku-tier Standard --sku-family MeteredData

az network express-route show -g rg-demo -n er-circuit --query serviceKey -o tsv
# give service key to provider; after provisioned, link a gateway to the VNet:
az network vnet-gateway create -g rg-demo -n er-gw --vnet vnet-prod \
  --public-ip-addresses er-gw-pip --gateway-type ExpressRoute --sku Standard
```
Provider and location names above are examples; verify with `az network express-route list-service-providers`.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Direct Connect | ExpressRoute |
| Encryption | Not default (add VPN/MACsec) | Not default (add IPsec VPN / MACsec on Direct) |
| Models | Dedicated / hosted | Provider / ExpressRoute Direct |
| Pricing | Port-hour + data out (approximate — check current docs) | Circuit fee + data plan (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming ExpressRoute traffic is encrypted.
✅ Correct: It is private, not encrypted by default; add IPsec VPN or MACsec if required.

❌ Mistake: Single circuit with no backup.
✅ Correct: Add a second circuit/location or a VPN failover.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is ExpressRoute? A1: Private dedicated link to Azure, like Direct Connect.
Q2: [Medium] ExpressRoute vs VPN? A2: Private, higher bandwidth, steadier latency vs cheap, quick, internet-based.
Q3: [Hard] How to design resilient hybrid? A3: Two circuits in different peering locations, zone-redundant gateway, VPN as backup via BGP.

---

## ✅ Quick Checklist
□ Redundant circuits
□ BGP configured
□ Encryption need decided
□ VPN backup path

---

## ⚡ 1-Line Summary
ExpressRoute is a private dedicated Azure line (Direct Connect) | ExpressRoute Azure तक private dedicated लाइन है, Direct Connect जैसी।

## ➡️ Next: 216. Private Endpoints

---
