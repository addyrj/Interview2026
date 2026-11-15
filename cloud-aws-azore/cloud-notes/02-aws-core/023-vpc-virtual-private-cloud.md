# 23. VPC — Virtual Private Cloud
# AWS: Amazon VPC
# Azure: Virtual Network (VNet)
# हिंदी में: क्लाउड में आपका अपना प्राइवेट नेटवर्क

---

## 🔵 Simple Definition
A VPC is your logically isolated virtual network in a Region where you define IP range (CIDR), subnets, routing and firewalls.
हिंदी: VPC क्लाउड में आपका अपना अलग और प्राइवेट नेटवर्क है जिसके IP, सबनेट और रूटिंग आप तय करते हैं।

---

## 🔴 Why it Exists
Without isolation, resources would share a flat public network. VPC lets you keep DBs private, expose only the load balancer, and control all traffic.

---

## 🟢 How it Works
```
Region ap-south-1
 VPC 10.0.0.0/16  (spans all AZs)
  ├── Public subnet  10.0.1.0/24 (AZ-a) -> route 0.0.0.0/0 -> IGW
  ├── Private subnet 10.0.11.0/24 (AZ-a) -> route 0.0.0.0/0 -> NAT
  └── Security Groups / NACLs filter traffic
Every account gets a default VPC (172.31.0.0/16) per region.
```

---

## 💻 Code / Config Example
```bash
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=app-vpc}]' \
  --query 'Vpc.VpcId' --output text)

# Needed so instances get DNS names
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames

aws ec2 describe-vpcs --vpc-ids "$VPC_ID"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Network | VPC (regional) | VNet (regional) |
| Subnet scope | One AZ | Whole region (can span zones) |
| Default network | Default VPC | None by default |
| Firewall | Security Group, NACL | NSG |
| Pricing | VPC free; NAT, endpoints, transfer paid | VNet free; NAT GW, peering transfer paid |

---

## ⚠️ Common Mistakes
❌ Mistake: Overlapping CIDRs (e.g. everything is 10.0.0.0/16), which blocks peering later.
✅ Correct: Plan non-overlapping CIDR ranges per environment/account.

❌ Mistake: Using the default VPC for production.
✅ Correct: Create a dedicated VPC with private subnets for data tier.

---

## ⚫ Interview Q&A
Q1: [Easy] What is the allowed VPC CIDR size?
A1: From /16 (largest) to /28 (smallest) for IPv4.

Q2: [Medium] Is a VPC zonal or regional? Subnet?
A2: VPC is regional; each subnet lives in exactly one AZ.

Q3: [Hard] How do you connect many VPCs and on-prem at scale?
A3: Peering is non-transitive and gets messy (n*(n-1)/2); use Transit Gateway hub-and-spoke, plus VPN/Direct Connect. Azure equivalent is Virtual WAN / hub VNet.

---

## ✅ Quick Checklist
□ CIDR planned, no overlap
□ Public + private subnets in 2+ AZs
□ DNS hostnames enabled where needed

---

## ⚡ 1-Line Summary
VPC is your isolated regional network with subnets, routes and firewalls. | VPC क्लाउड में आपका प्राइवेट नेटवर्क है जिसमें सबनेट, रूट और फ़ायरवॉल होते हैं।

## ➡️ Next: Subnets (Public + Private)
