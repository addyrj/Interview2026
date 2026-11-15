---

# 214. Azure VPN Gateway
# AWS: AWS Site-to-Site VPN / Client VPN (Virtual Private Gateway)
# Azure: Azure VPN Gateway
# हिंदी में: Internet पर encrypted tunnel से on-prem को Azure से जोड़ना

---

## 🔵 Simple Definition (2 lines)
VPN Gateway sends encrypted IPsec/IKE traffic between a VNet and on-prem sites (S2S) or individual users (P2S).
हिंदी: VPN Gateway internet पर encrypted tunnel बनाकर VNet को on-prem या users से जोड़ता है।

---

## 🔴 Why it Exists (2 lines)
Companies need secure hybrid connectivity quickly and cheaply without a dedicated circuit.
It also gives developers private access to VNet resources.

---

## 🟢 How it Works
```
On-prem router/firewall <== IPsec tunnel (internet) ==> Azure VPN Gateway (GatewaySubnet)
        Local Network Gateway (on-prem IP + prefixes)  +  Connection (shared key)
Types: Site-to-Site, Point-to-Site (OpenVPN/IKEv2), VNet-to-VNet
Gateway deployment can take ~30-45 minutes.
```

---

## 💻 Code / Config Example
```bash
az network vnet subnet create -g rg-demo --vnet-name vnet-prod \
  -n GatewaySubnet --address-prefixes 10.0.255.0/27
az network public-ip create -g rg-demo -n vpngw-pip --sku Standard --allocation-method Static

az network vnet-gateway create -g rg-demo -n vpngw --vnet vnet-prod \
  --public-ip-addresses vpngw-pip --gateway-type Vpn --vpn-type RouteBased \
  --sku VpnGw1 --no-wait

az network local-gateway create -g rg-demo -n onprem-lgw \
  --gateway-ip-address 203.0.113.20 --local-address-prefixes 192.168.0.0/24

az network vpn-connection create -g rg-demo -n s2s-conn \
  --vnet-gateway1 vpngw --local-gateway2 onprem-lgw --shared-key 'REPLACE_WITH_SECRET'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Site-to-Site | Site-to-Site VPN | VPN Gateway S2S |
| User VPN | Client VPN | Point-to-Site |
| Throughput | Per tunnel limits | Depends on SKU (approximate — check current docs) |
| Pricing | Per connection-hour + data | Hourly by SKU + egress (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using a PolicyBased VPN type for modern needs.
✅ Correct: Use RouteBased; it supports P2S and multiple connections.

❌ Mistake: Putting a custom NSG on GatewaySubnet.
✅ Correct: Do not attach NSGs to GatewaySubnet; it can break the gateway.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is VPN Gateway? A1: Managed gateway for IPsec VPNs to Azure.
Q2: [Medium] VPN vs ExpressRoute? A2: VPN runs over the public internet encrypted; ExpressRoute is a private dedicated circuit.
Q3: [Hard] How to get HA? A3: Active-active gateway with zone-redundant SKUs (AZ), two on-prem devices and BGP.

---

## ✅ Quick Checklist
□ GatewaySubnet /27 or larger
□ RouteBased type
□ Strong shared key in Key Vault
□ BGP / active-active for HA

---

## ⚡ 1-Line Summary
VPN Gateway = encrypted tunnel to Azure over internet | VPN Gateway internet पर encrypted tunnel से Azure जोड़ता है।

## ➡️ Next: 215. Azure ExpressRoute

---
