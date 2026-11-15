# 30. Route Tables
# AWS: VPC Route Tables
# Azure: Route Tables (User Defined Routes, UDR)
# हिंदी में: ट्रैफिक किस रास्ते जाएगा यह तय करने वाली सूची

---

## 🔵 Simple Definition
A route table is a set of rules (destination CIDR -> target) that decides where subnet traffic goes; the most specific match wins.
हिंदी: Route table नियमों की सूची है जो बताती है कि किसी IP रेंज का ट्रैफिक किस टारगेट (IGW, NAT, peering) पर जाएगा।

---

## 🔴 Why it Exists
Without routes, subnets cannot reach the internet, peers or on-prem. Routes define public vs private behaviour.

---

## 🟢 How it Works
```
Public RT:   10.0.0.0/16 -> local
             0.0.0.0/0   -> igw-xxx
Private RT:  10.0.0.0/16 -> local
             0.0.0.0/0   -> nat-xxx
             10.1.0.0/16 -> pcx-xxx
Longest-prefix match. Each subnet has exactly one RT (else the main RT).
```

---

## 💻 Code / Config Example
```bash
VPC_ID=vpc-0123456789abcdef0
RTB=$(aws ec2 create-route-table --vpc-id $VPC_ID --query RouteTable.RouteTableId --output text)

aws ec2 create-route --route-table-id $RTB --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-0123456789abcdef0
aws ec2 associate-route-table --route-table-id $RTB --subnet-id subnet-aaaa1111

aws ec2 describe-route-tables --route-table-ids $RTB \
  --query 'RouteTables[0].Routes' --output table
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Default routes | `local` + main RT | System routes (VNet, Internet) |
| Custom | Route tables per subnet | UDR route table per subnet |
| Force via firewall | Route to NAT/appliance ENI/TGW | UDR with next hop "Virtual appliance" |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving subnets on the main route table that has an IGW route.
✅ Correct: Keep main RT private; explicitly associate public subnets with a public RT.

❌ Mistake: Blackhole route after deleting a NAT/peering.
✅ Correct: Check route status `blackhole` and fix targets.

---

## ⚫ Interview Q&A
Q1: [Easy] What is the `local` route?
A1: Auto route for VPC CIDR so subnets inside the VPC talk; cannot be removed.

Q2: [Medium] Which route wins when several match?
A2: Longest prefix (most specific) match.

Q3: [Hard] Send all egress through an inspection firewall?
A3: Put firewall in a dedicated subnet, point private RTs to firewall endpoint/ENI (or Gateway Load Balancer), and return route from firewall subnet to the IGW/NAT; use edge routes for ingress.

---

## ✅ Quick Checklist
□ Public RT has IGW route only for public subnets
□ Private RT uses NAT
□ No blackhole routes

---

## ⚡ 1-Line Summary
Route tables map destination CIDRs to targets using longest-prefix match. | Route table destination CIDR को target से जोड़ती है और सबसे specific नियम जीतता है।

## ➡️ Next: Elastic IP
