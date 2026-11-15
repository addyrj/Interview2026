# 24. Subnets (Public + Private)
# AWS: VPC Subnets
# Azure: VNet Subnets
# हिंदी में: VPC को छोटे हिस्सों में बांटना, पब्लिक या प्राइवेट

---

## 🔵 Simple Definition
A subnet is a slice of the VPC CIDR placed in one AZ. It is "public" if its route table sends 0.0.0.0/0 to an Internet Gateway, otherwise "private".
हिंदी: Subnet VPC का एक हिस्सा है; जिसका रूट Internet Gateway की ओर हो वह public, बाकी private।

---

## 🔴 Why it Exists
You must separate internet-facing parts (ALB) from sensitive parts (DB, workers) and place them across AZs for availability.

---

## 🟢 How it Works
```
VPC 10.0.0.0/16
 AZ-a: public 10.0.1.0/24 (ALB, NAT)   private 10.0.11.0/24 (API, DB)
 AZ-b: public 10.0.2.0/24              private 10.0.12.0/24
"Public" = route to IGW (+ public IP). Nothing else makes it public.
AWS reserves 5 IPs per subnet (first 4 and last 1).
```

---

## 💻 Code / Config Example
```bash
VPC_ID=vpc-0123456789abcdef0   # replace

PUB=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --availability-zone ap-south-1a --query Subnet.SubnetId --output text)
PRIV=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.11.0/24 \
  --availability-zone ap-south-1a --query Subnet.SubnetId --output text)

# Auto-assign public IPv4 for instances launched in the public subnet
aws ec2 modify-subnet-attribute --subnet-id $PUB --map-public-ip-on-launch
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Scope | Single AZ | Entire region |
| Public/private | Decided by route to IGW | Decided by public IP + NSG; default outbound access being retired for new subnets (check docs) |
| Reserved IPs | 5 per subnet | 5 per subnet |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting the DB in a public subnet "to connect easily".
✅ Correct: Private subnet; access via bastion/SSM or VPN.

❌ Mistake: Subnets too small (/28) and run out of IPs (EKS/ENIs use many).
✅ Correct: Use /24 or larger for app tiers.

---

## ⚫ Interview Q&A
Q1: [Easy] What makes a subnet public?
A1: Its route table has 0.0.0.0/0 -> Internet Gateway (and instances have public IPs).

Q2: [Medium] Why does AWS reserve 5 IPs?
A2: Network address, VPC router, DNS, future use, and broadcast (unsupported but reserved).

Q3: [Hard] How do private instances reach the internet for updates?
A3: Route 0.0.0.0/0 to a NAT Gateway in a public subnet (one per AZ for HA), or use VPC endpoints for AWS services to avoid NAT cost.

---

## ✅ Quick Checklist
□ 2+ AZs, each with public and private subnet
□ Correct route table association
□ DB only in private subnets

---

## ⚡ 1-Line Summary
Subnet is an AZ-bound slice of the VPC; the IGW route makes it public. | Subnet एक AZ में VPC का हिस्सा है; IGW का रूट उसे public बनाता है।

## ➡️ Next: Internet Gateway
