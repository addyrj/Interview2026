---

# 206. Subnets in Azure
# AWS: VPC Subnets
# Azure: VNet Subnets
# हिंदी में: VNet का छोटा हिस्सा जहाँ resources रहते हैं

---

## 🔵 Simple Definition (2 lines)
A subnet is a slice of a VNet's IP range where you place VMs, AKS nodes or private endpoints.
हिंदी: Subnet VNet के IP range का एक हिस्सा है जिसमें आप resources रखते हैं।

---

## 🔴 Why it Exists (2 lines)
Splitting tiers (web/app/db) lets you apply different NSGs, route tables and delegations.
It also reserves space for services that need a dedicated subnet.

---

## 🟢 How it Works
```
VNet 10.0.0.0/16
 |-- web 10.0.1.0/24    NSG-web   -> internet via LB
 |-- app 10.0.2.0/24    NSG-app   -> only from web subnet
 |-- db  10.0.3.0/24    NSG-db    -> only from app subnet
 |-- AzureFirewallSubnet / GatewaySubnet / AzureBastionSubnet (reserved names)
Azure reserves 5 IPs per subnet (first 4 and last).
```

---

## 💻 Code / Config Example
```bash
# Subnet with NSG + service endpoint
az network vnet subnet create -g rg-demo --vnet-name vnet-prod -n db \
  --address-prefixes 10.0.3.0/24 \
  --network-security-group nsg-db \
  --service-endpoints Microsoft.Sql

# Delegate a subnet to Container Apps / App Service VNet integration
az network vnet subnet update -g rg-demo --vnet-name vnet-prod -n integration \
  --delegations Microsoft.Web/serverFarms
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| AZ scope | One AZ per subnet | Spans all AZs in region |
| Public/private | Route to IGW decides | No such label; public IP + NSG/route decides |
| Reserved IPs | 5 per subnet | 5 per subnet |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting everything in one subnet.
✅ Correct: Separate by tier and apply NSGs per subnet.

❌ Mistake: Naming the VPN subnet something custom.
✅ Correct: Use the required names `GatewaySubnet`, `AzureFirewallSubnet`, `AzureBastionSubnet`.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a subnet? A1: A range of IPs inside a VNet for placing resources.
Q2: [Medium] How many IPs does Azure reserve per subnet? A2: Five.
Q3: [Hard] What is subnet delegation? A3: Giving a service (e.g. Microsoft.Web/serverFarms) exclusive control to inject its resources into a subnet.

---

## ✅ Quick Checklist
□ Subnet sized for growth
□ NSG attached
□ Reserved names used correctly
□ Delegation set where required

---

## ⚡ 1-Line Summary
Subnets split a VNet into tiers with their own rules | Subnet VNet को tiers में बाँटता है, हर tier के अपने rules।

## ➡️ Next: 207. Network Security Groups (NSG)

---
