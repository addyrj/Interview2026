---

# 205. Azure Virtual Network (VNet)
# AWS: Amazon VPC
# Azure: Azure Virtual Network (VNet)
# हिंदी में: Azure में आपका private network

---

## 🔵 Simple Definition (2 lines)
A VNet is your isolated private network in Azure with its own IP address space, split into subnets.
हिंदी: VNet Azure में आपका अपना private network है जिसका IP range आप तय करते हैं।

---

## 🔴 Why it Exists (2 lines)
Resources need private IPs, controlled traffic and isolation from other tenants and the internet.
A VNet lets VMs, AKS, databases and on-prem talk securely.

---

## 🟢 How it Works
```
Subscription -> Resource Group -> VNet 10.0.0.0/16  (regional)
   |-- subnet web 10.0.1.0/24  [NSG]
   |-- subnet app 10.0.2.0/24  [NSG]
   |-- subnet db  10.0.3.0/24  [NSG]
Outbound internet works by default; inbound needs a public IP/LB/Gateway.
Connect: peering, VPN Gateway, ExpressRoute.
```

---

## 💻 Code / Config Example
```bash
az network vnet create -g rg-demo -n vnet-prod -l centralindia \
  --address-prefixes 10.0.0.0/16 \
  --subnet-name web --subnet-prefixes 10.0.1.0/24

az network vnet subnet create -g rg-demo --vnet-name vnet-prod \
  -n app --address-prefixes 10.0.2.0/24
```
```bicep
resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: 'vnet-prod'
  location: 'centralindia'
  properties: {
    addressSpace: { addressPrefixes: ['10.0.0.0/16'] }
    subnets: [
      { name: 'web', properties: { addressPrefix: '10.0.1.0/24' } }
      { name: 'app', properties: { addressPrefix: '10.0.2.0/24' } }
    ]
  }
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | VPC | VNet |
| Scope | Region, subnets are per-AZ | Region, subnets span all AZs |
| Default outbound | Needs IGW/NAT | Default outbound access (being phased out; use NAT Gateway) |
| Pricing | VPC free; NAT/data transfer paid | VNet free; peering, gateways, data transfer paid (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Overlapping address spaces across VNets/on-prem.
✅ Correct: Plan non-overlapping CIDRs up front; peering and VPN need it.

❌ Mistake: Choosing a tiny range (/24) for the whole VNet.
✅ Correct: Start with /16 and carve subnets; resizing later is painful.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a VNet? A1: Azure's private, isolated network, like an AWS VPC.
Q2: [Medium] Are VNets global? A2: No, regional; connect regions via global VNet peering.
Q3: [Hard] How do you design a hub-and-spoke? A3: Hub VNet holds Firewall/VPN/DNS; spoke VNets peer to hub with UDRs sending traffic through the firewall.

---

## ✅ Quick Checklist
□ Non-overlapping CIDRs
□ One subnet per tier
□ NSG on each subnet
□ NAT Gateway for outbound

---

## ⚡ 1-Line Summary
VNet is Azure's private network (VPC equivalent) | VNet Azure का private network है, AWS के VPC जैसा।

## ➡️ Next: 206. Subnets in Azure

---
