# 25. Internet Gateway
# AWS: Internet Gateway (IGW)
# Azure: No separate resource (system default route + Public IP)
# हिंदी में: VPC का इंटरनेट का दरवाज़ा

---

## 🔵 Simple Definition
An Internet Gateway is a horizontally scaled, managed VPC component that allows two-way internet traffic for resources with public IPs.
हिंदी: Internet Gateway VPC को इंटरनेट से जोड़ने वाला मैनेज्ड दरवाज़ा है, यह दोनों तरफ का ट्रैफिक चलने देता है।

---

## 🔴 Why it Exists
A VPC has no internet path by default. IGW provides it and also does 1:1 NAT between private and public IPv4 addresses.

---

## 🟢 How it Works
```
Internet <-> IGW <-> route table (0.0.0.0/0 -> igw-xxx)
                        |
                 public subnet: EC2 (private IP 10.0.1.5 <-> public IP)
One IGW per VPC. Free; you pay only data transfer.
```

---

## 💻 Code / Config Example
```bash
VPC_ID=vpc-0123456789abcdef0
RTB_ID=rtb-0123456789abcdef0   # public route table

IGW=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW --vpc-id $VPC_ID
aws ec2 create-route --route-table-id $RTB_ID \
  --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Internet path | IGW attached to VPC + route | System route to Internet; need Public IP on NIC/LB |
| Outbound only | NAT Gateway / egress-only IGW (IPv6) | NAT Gateway |
| Pricing | IGW free; data transfer out charged | Public IP and egress charged (approximate, check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: IGW attached but instance still unreachable.
✅ Correct: Check all four: route to IGW, public/Elastic IP, Security Group, NACL.

❌ Mistake: Expecting IGW to give private subnets outbound access.
✅ Correct: Private instances need a NAT Gateway (IGW needs a public IP on the instance).

---

## ⚫ Interview Q&A
Q1: [Easy] How many IGWs per VPC?
A1: One.

Q2: [Medium] Does IGW cost money or limit bandwidth?
A2: No cost and no bandwidth bottleneck; it is managed and redundant. Data transfer out is billed.

Q3: [Hard] Instance in public subnet has public IP but cannot reach internet. Debug?
A3: Verify route table associated with that subnet has 0.0.0.0/0 -> IGW, IGW is attached, SG outbound and NACL (ephemeral ports both ways) allow, OS firewall is open.

---

## ✅ Quick Checklist
□ IGW attached to VPC
□ Public route table has 0.0.0.0/0 -> IGW
□ Instance has public/Elastic IP

---

## ⚡ 1-Line Summary
IGW gives a VPC two-way internet access via routes and public IPs. | IGW रूट और public IP के ज़रिए VPC को दोनों तरफ का इंटरनेट देता है।

## ➡️ Next: NAT Gateway
