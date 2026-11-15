---

# 213. VNet Peering
# AWS: VPC Peering / Transit Gateway
# Azure: VNet Peering (Global VNet Peering)
# हिंदी में: दो VNets को private तरीके से जोड़ना

---

## 🔵 Simple Definition (2 lines)
VNet peering links two VNets so resources communicate over Microsoft's private backbone with private IPs.
हिंदी: VNet peering दो VNets को Microsoft के private backbone से जोड़ती है, private IPs पर।

---

## 🔴 Why it Exists (2 lines)
Separate VNets (per env, team or region) still need low-latency private communication.
Peering avoids gateways and public internet.

---

## 🟢 How it Works
```
VNet-A 10.0.0.0/16 <==== peering (both directions required) ====> VNet-B 10.1.0.0/16
Same region: VNet peering | Different regions: Global VNet peering
Not transitive: A<->B and B<->C does NOT give A<->C (use hub firewall/NVA or Virtual WAN)
Address spaces must not overlap.
```

---

## 💻 Code / Config Example
```bash
VNET_A_ID=$(az network vnet show -g rg-a -n vnet-a --query id -o tsv)
VNET_B_ID=$(az network vnet show -g rg-b -n vnet-b --query id -o tsv)

# Peering must be created in BOTH directions
az network vnet peering create -g rg-a -n a-to-b --vnet-name vnet-a \
  --remote-vnet "$VNET_B_ID" --allow-vnet-access
az network vnet peering create -g rg-b -n b-to-a --vnet-name vnet-b \
  --remote-vnet "$VNET_A_ID" --allow-vnet-access
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | VPC Peering, Transit Gateway | VNet Peering, Virtual WAN |
| Transitive | No (TGW yes) | No (use hub/Virtual WAN) |
| Cross-region | Inter-region peering | Global VNet peering |
| Pricing | Data transfer charges | Ingress/egress per GB (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Creating peering in one direction only (status stays Initiated).
✅ Correct: Create both sides; status becomes Connected.

❌ Mistake: Overlapping CIDRs.
✅ Correct: Plan unique ranges before deploying.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is VNet peering? A1: Private connectivity between two VNets.
Q2: [Medium] Is it transitive? A2: No; route via a hub firewall/NVA or use Virtual WAN.
Q3: [Hard] How do spokes use the hub's VPN gateway? A3: Enable "allow gateway transit" on the hub side and "use remote gateways" on spokes.

---

## ✅ Quick Checklist
□ Non-overlapping CIDRs
□ Both directions created
□ Gateway transit settings correct
□ NSGs allow peered traffic

---

## ⚡ 1-Line Summary
Peering privately links VNets, non-transitive | Peering VNets को private जोड़ता है, पर transitive नहीं है।

## ➡️ Next: 214. Azure VPN Gateway

---
