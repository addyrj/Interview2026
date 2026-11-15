# 26. NAT Gateway
# AWS: NAT Gateway
# Azure: Azure NAT Gateway
# हिंदी में: प्राइवेट सबनेट को सिर्फ बाहर जाने का इंटरनेट रास्ता

---

## 🔵 Simple Definition
A NAT Gateway lets resources in private subnets start outbound connections to the internet while blocking inbound connections from it.
हिंदी: NAT Gateway private सबनेट के सर्वर को इंटरनेट पर बाहर जाने देता है, पर बाहर से अंदर आने नहीं देता।

---

## 🔴 Why it Exists
Private servers still need npm/pip installs, OS updates and third-party API calls, but must not be publicly reachable.

---

## 🟢 How it Works
```
Private EC2 (10.0.11.5)
   | route 0.0.0.0/0 -> nat-xxx
   v
NAT GW (in PUBLIC subnet, has Elastic IP)
   | route 0.0.0.0/0 -> igw
   v
Internet   (replies return via NAT; unsolicited inbound dropped)
```

---

## 💻 Code / Config Example
```bash
PUB_SUBNET=subnet-aaaa1111      # must be a public subnet
PRIV_RTB=rtb-bbbb2222           # private route table

EIP=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)
NAT=$(aws ec2 create-nat-gateway --subnet-id $PUB_SUBNET --allocation-id $EIP \
  --query NatGateway.NatGatewayId --output text)
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT

aws ec2 create-route --route-table-id $PRIV_RTB \
  --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | NAT Gateway (zonal) | NAT Gateway (attached to subnet) |
| Billing | Hourly + per-GB processed (approximate, check current docs) | Hourly + per-GB (approximate, check current docs) |
| Cheaper DIY | NAT instance on EC2 | VM with IP forwarding |
| Avoid NAT for AWS APIs | VPC Gateway endpoints (S3, DynamoDB) | Service/Private endpoints |

---

## ⚠️ Common Mistakes
❌ Mistake: Creating NAT in a private subnet.
✅ Correct: NAT must be in a public subnet with an Elastic IP.

❌ Mistake: One NAT for all AZs; AZ-down breaks everyone, and cross-AZ traffic costs more.
✅ Correct: One NAT per AZ for production; single NAT only for dev.

---

## ⚫ Interview Q&A
Q1: [Easy] Why NAT Gateway?
A1: Outbound-only internet for private subnets.

Q2: [Medium] NAT Gateway vs NAT instance?
A2: Gateway is managed, scales automatically, no patching; instance is cheaper for tiny loads but you manage HA, size, source/dest check.

Q3: [Hard] NAT bill is huge. What do you do?
A3: Find top talkers (VPC Flow Logs), add S3/DynamoDB gateway endpoints (free) and interface endpoints for ECR/Secrets, keep traffic same-AZ, cache dependencies.

---

## ✅ Quick Checklist
□ NAT in public subnet with Elastic IP
□ Private route table points to NAT
□ One per AZ in prod, endpoints for S3

---

## ⚡ 1-Line Summary
NAT Gateway gives private subnets outbound-only internet. | NAT Gateway private सबनेट को सिर्फ बाहर जाने वाला इंटरनेट देता है।

## ➡️ Next: Security Groups
