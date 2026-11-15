---

# 4. Public vs Private vs Hybrid Cloud
# AWS: Public cloud; Outposts / Direct Connect for hybrid
# Azure: Public cloud; Azure Arc / Azure Stack / ExpressRoute for hybrid
# हिंदी में: पब्लिक, प्राइवेट और हाइब्रिड क्लाउड के डिप्लॉयमेंट मॉडल

---

## 🔵 Simple Definition (2 lines)
Public cloud is shared provider infrastructure (AWS, Azure). Private cloud is dedicated to one organization. Hybrid links both (and multi-cloud uses several providers).
हिंदी: पब्लिक = प्रोवाइडर का साझा इंफ्रा, प्राइवेट = सिर्फ़ आपका, हाइब्रिड = दोनों का जोड़।

---

## 🔴 Why it Exists (2 lines)
Some data must stay on-prem for law, latency or existing investment, but you still want cloud elasticity.
Hybrid lets you move workloads gradually.

---

## 🟢 How it Works
```
 On-prem DC / Private cloud            Public cloud (AWS / Azure)
 +----------------------+   VPN or    +-----------------------+
 | legacy DB, ERP       |<--dedicated->| web tier, analytics  |
 +----------------------+   link      +-----------------------+
   Site-to-Site VPN (encrypted, over internet)
   Direct Connect / ExpressRoute (private circuit)
```

---

## 💻 Code / Config Example
```bash
# AWS: create the cloud-side pieces of a Site-to-Site VPN (ids are placeholders)
aws ec2 create-customer-gateway --type ipsec.1 \
  --public-ip 203.0.113.12 --bgp-asn 65000
aws ec2 create-vpn-gateway --type ipsec.1

# Azure: create a virtual network gateway for VPN (takes ~30-45 min)
az network vnet-gateway create --resource-group demo-rg --name hub-vpngw \
  --vnet hub-vnet --public-ip-address hub-vpngw-ip \
  --gateway-type Vpn --vpn-type RouteBased --sku VpnGw1
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Private circuit | Direct Connect | ExpressRoute |
| Encrypted tunnel | Site-to-Site VPN | VPN Gateway |
| On-prem hardware | Outposts | Azure Stack Hub / HCI |
| Unified management | Systems Manager hybrid | Azure Arc |

---

## ⚠️ Common Mistakes
❌ Mistake: Overlapping CIDR ranges between on-prem and VPC/VNet.
✅ Correct: Plan non-overlapping IP ranges before connecting.

❌ Mistake: Going multi-cloud "for safety" without a real need.
✅ Correct: Multi-cloud adds cost and skills burden; use only for clear reasons (compliance, M&A).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is hybrid cloud?
A1: Integrated use of on-prem/private and public cloud.

Q2: [Medium] VPN vs Direct Connect / ExpressRoute?
A2: VPN is quick and cheap over the internet; dedicated links give consistent latency and bandwidth but take time and cost more.

Q3: [Hard] Design hybrid access for an on-prem DB used by a cloud app.
A3: Private link (Direct Connect/ExpressRoute) with VPN as backup, non-overlapping CIDRs, DNS forwarding both ways, least-privilege security rules, monitoring on tunnel health.

---

## ✅ Quick Checklist
□ CIDRs do not overlap
□ Backup path for the link
□ Data classification decides what stays on-prem

---

## ⚡ 1-Line Summary
Public is shared, private is dedicated, hybrid connects both | पब्लिक साझा, प्राइवेट अपना, हाइब्रिड दोनों जुड़े।

## ➡️ Next: 5. Cloud Benefits

---
