# 29. VPC Peering
# AWS: VPC Peering Connection
# Azure: VNet Peering
# हिंदी में: दो VPC को आपस में प्राइवेट तरीके से जोड़ना

---

## 🔵 Simple Definition
VPC Peering is a private, one-to-one network link between two VPCs (same or different account/region) using private IPs.
हिंदी: VPC Peering दो VPC के बीच प्राइवेट IP से सीधा कनेक्शन है, इंटरनेट की ज़रूरत नहीं।

---

## 🔴 Why it Exists
Separate VPCs (prod, shared-services, data) need to talk privately without the public internet or VPN.

---

## 🟢 How it Works
```
VPC-A 10.0.0.0/16 <== pcx-123 ==> VPC-B 10.1.0.0/16
1) Requester sends request   2) Accepter accepts
3) BOTH sides add routes:  A: 10.1.0.0/16 -> pcx-123 ; B: 10.0.0.0/16 -> pcx-123
4) SGs/NACLs allow traffic
Non-transitive: A<->B and B<->C does NOT give A<->C. CIDRs must not overlap.
```

---

## 💻 Code / Config Example
```bash
PCX=$(aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-aaaa1111 --peer-vpc-id vpc-bbbb2222 \
  --query VpcPeeringConnection.VpcPeeringConnectionId --output text)
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $PCX

aws ec2 create-route --route-table-id rtb-aaaa1111 \
  --destination-cidr-block 10.1.0.0/16 --vpc-peering-connection-id $PCX
aws ec2 create-route --route-table-id rtb-bbbb2222 \
  --destination-cidr-block 10.0.0.0/16 --vpc-peering-connection-id $PCX
```
Cross-account/region: add `--peer-owner-id` / `--peer-region`.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | VPC Peering | VNet Peering (global peering for cross-region) |
| Transitive | No (use Transit Gateway) | No by default (hub with gateway transit / Virtual WAN) |
| Routes | Manual route entries | Automatic once peered |
| Pricing | No hourly fee; data transfer charged (approximate, check current docs) | Ingress/egress charged (approximate, check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Peering overlapping CIDRs.
✅ Correct: Plan unique CIDRs first; overlap cannot be peered.

❌ Mistake: Created peering but forgot routes or SG rules.
✅ Correct: Add routes in both route tables and SG rules for the peer CIDR.

---

## ⚫ Interview Q&A
Q1: [Easy] Is peering transitive?
A1: No.

Q2: [Medium] Peering vs Transit Gateway?
A2: Peering: simple, cheap, 1:1, no hub. TGW: hub-and-spoke, transitive routing, supports VPN/DX, hourly + per-GB attachment cost.

Q3: [Hard] 10 VPCs need full connectivity. Approach?
A3: Full mesh needs 45 peerings and route upkeep; use Transit Gateway with route tables per environment for segmentation.

---

## ✅ Quick Checklist
□ CIDRs do not overlap
□ Routes added on both sides
□ SG/NACL allow peer CIDR

---

## ⚡ 1-Line Summary
Peering privately links two VPCs 1:1, non-transitive, routes needed. | Peering दो VPC को प्राइवेट रूप से जोड़ता है, यह transitive नहीं है और रूट जोड़ने पड़ते हैं।

## ➡️ Next: Route Tables
