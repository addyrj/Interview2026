# 31. Elastic IP
# AWS: Elastic IP (EIP)
# Azure: Public IP Address (Static SKU)
# हिंदी में: स्थायी पब्लिक IP जो बदलता नहीं

---

## 🔵 Simple Definition
An Elastic IP is a static public IPv4 address you own in your account and can re-map between instances or NAT gateways.
हिंदी: Elastic IP एक स्थायी public IPv4 है जिसे आप एक इंस्टेंस से दूसरे पर जल्दी से लगा सकते हैं।

---

## 🔴 Why it Exists
Normal public IPs change on stop/start. Whitelisting by partners, DNS records and NAT need a fixed address.

---

## 🟢 How it Works
```
allocate-address  -> eipalloc-xxx (yours until released)
associate-address -> instance / ENI / NAT GW
Failover: re-associate EIP to a standby instance, same IP.
```
Since Feb 2024 AWS charges for all public IPv4 addresses, in use or idle (approximate, check current docs).

---

## 💻 Code / Config Example
```bash
ALLOC=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)
aws ec2 associate-address --instance-id i-0123456789abcdef0 --allocation-id $ALLOC

aws ec2 describe-addresses --allocation-ids $ALLOC

# Cleanup (avoid idle charges)
aws ec2 disassociate-address --association-id eipassoc-xxxx
aws ec2 release-address --allocation-id $ALLOC
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Static IP | Elastic IP | Public IP, Standard SKU, Static |
| Remap | Re-associate anytime | Re-associate to NIC |
| Pricing | Charged hourly for public IPv4 (approximate, check current docs) | Standard static IP billed hourly (approximate, check current docs) |
| Better option | ALB + DNS name | Load Balancer/App Gateway + DNS |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving unattached EIPs allocated.
✅ Correct: Release unused EIPs.

❌ Mistake: Hard-coding EIP for a scalable app.
✅ Correct: Use ALB + Route 53 name; EIP only for NAT, bastion or whitelisting.

---

## ⚫ Interview Q&A
Q1: [Easy] Why Elastic IP over auto-assigned public IP?
A1: It persists across stop/start and can be remapped.

Q2: [Medium] Default EIP limit?
A2: Soft limit of 5 per Region (approximate, can be raised via Service Quotas; check docs).

Q3: [Hard] How to give a partner a fixed IP for outbound calls from an autoscaled private fleet?
A3: Route egress through a NAT Gateway with an EIP; partner whitelists that EIP (one per AZ).

---

## ✅ Quick Checklist
□ EIP only where static IP truly needed
□ No unattached EIPs
□ DNS/ALB used for app entry

---

## ⚡ 1-Line Summary
Elastic IP is a remappable static public IPv4 owned by your account. | Elastic IP आपके अकाउंट का स्थायी public IPv4 है जिसे दूसरे रिसोर्स पर लगाया जा सकता है।

## ➡️ Next: EC2 — Complete Guide
