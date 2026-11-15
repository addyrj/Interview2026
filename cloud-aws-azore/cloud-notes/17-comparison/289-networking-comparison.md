# 289. Networking Comparison
# AWS: VPC, Security Groups, NACL, ALB/NLB, Route 53, CloudFront
# Azure: VNet, NSG, Load Balancer/App Gateway, Azure DNS/Traffic Manager, Front Door
# हिंदी में: नेटवर्किंग की तुलना

---

## 🔵 Simple Definition
Both provide private networks, subnet-level firewalls, load balancers, DNS and CDN, with different naming and scope.
हिंदी: दोनों में प्राइवेट नेटवर्क, फायरवॉल, लोड बैलेंसर, DNS और CDN हैं, बस नाम और स्कोप अलग हैं।

---

## 🔴 Why it Exists
Traffic isolation and routing are the base of secure apps; engineers moving clouds must map concepts fast.

---

## 🟢 How it Works
```
Internet -> CDN (CloudFront / Front Door) -> L7 LB (ALB / App Gateway)
         -> subnets in VPC / VNet -> app (private) -> DB (private)
Firewall: Security Group (stateful, per ENI) / NSG (stateful, per subnet or NIC)
```

---

## 💻 Code / Config Example
```bash
# Allow HTTPS in
aws ec2 authorize-security-group-ingress --group-id sg-0123 --protocol tcp --port 443 --cidr 0.0.0.0/0

az network nsg rule create -g rg-demo --nsg-name web-nsg -n allow-https \
  --priority 100 --access Allow --protocol Tcp --direction Inbound \
  --destination-port-ranges 443 --source-address-prefixes Internet
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Private network | VPC (regional) | VNet (regional) |
| Subnets | Tied to one AZ | Span zones in the region |
| L4 LB | NLB | Azure Load Balancer |
| L7 LB | ALB | Application Gateway |
| DNS | Route 53 | Azure DNS + Traffic Manager |
| Peering | VPC peering / Transit Gateway | VNet peering / Virtual WAN |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming Azure subnets are per-AZ like AWS.
✅ Correct: Azure subnets span zones; place resources in zones individually.

❌ Mistake: Opening 0.0.0.0/0 to SSH.
✅ Correct: Bastion / VPN, specific CIDRs.

---

## ⚫ Interview Q&A
Q1: [Easy] VPC equivalent?
A1: Virtual Network (VNet).

Q2: [Medium] SG vs NSG?
A2: Both stateful allow/deny rules; SGs are allow-only attached to resources; NSGs have priorities with allow and deny, attached to subnets or NICs.

Q3: [Hard] Connect on-prem to cloud?
A3: Site-to-site VPN or dedicated link (Direct Connect / ExpressRoute) with redundancy and routing (BGP).

---

## ✅ Quick Checklist
□ Private subnets for app and DB
□ Least-privilege rules
□ CIDRs do not overlap for peering

---

## ⚡ 1-Line Summary
VPC=VNet, SG=NSG, ALB=App Gateway, Route 53=Azure DNS. | VPC=VNet, SG=NSG, ALB=App Gateway, Route 53=Azure DNS।

## ➡️ Next: 290. Messaging Comparison
