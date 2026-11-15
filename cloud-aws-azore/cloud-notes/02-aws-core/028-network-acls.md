# 28. Network ACLs
# AWS: Network ACL (NACL)
# Azure: NSG on subnet (closest; NSG also does what SG does)
# हिंदी में: सबनेट के स्तर का स्टेटलेस फ़ायरवॉल

---

## 🔵 Simple Definition
A Network ACL is a stateless firewall at the subnet boundary with numbered allow and deny rules evaluated in order.
हिंदी: NACL सबनेट पर लगा स्टेटलेस फ़ायरवॉल है जिसमें नंबर वाले allow/deny नियम क्रम से चेक होते हैं।

---

## 🔴 Why it Exists
A second layer of defense: block specific IPs/CIDRs for a whole subnet, which SGs cannot do.

---

## 🟢 How it Works
```
Packet -> subnet boundary -> NACL (lowest rule number first, first match wins)
       -> Security Group -> instance
Stateless: return traffic needs its own rule (ephemeral ports 1024-65535).
Default NACL allows all; a custom NACL denies all until you add rules.
Final rule "*" = deny.
```

---

## 💻 Code / Config Example
```bash
VPC_ID=vpc-0123456789abcdef0
SUBNET_ID=subnet-aaaa1111

NACL=$(aws ec2 create-network-acl --vpc-id $VPC_ID --query NetworkAcl.NetworkAclId --output text)

# Block a bad IP (low number = evaluated first)
aws ec2 create-network-acl-entry --network-acl-id $NACL --ingress --rule-number 90 \
  --protocol -1 --rule-action deny --cidr-block 198.51.100.7/32
# Allow HTTPS in
aws ec2 create-network-acl-entry --network-acl-id $NACL --ingress --rule-number 100 \
  --protocol tcp --port-range From=443,To=443 --rule-action allow --cidr-block 0.0.0.0/0
# Allow ephemeral return traffic out
aws ec2 create-network-acl-entry --network-acl-id $NACL --egress --rule-number 100 \
  --protocol tcp --port-range From=1024,To=65535 --rule-action allow --cidr-block 0.0.0.0/0

aws ec2 describe-network-acls --network-acl-ids $NACL --query 'NetworkAcls[0].Entries'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | NACL | SG | Azure NSG |
|---------|------|----|-----------|
| Level | Subnet | ENI | Subnet or NIC |
| State | Stateless | Stateful | Stateful |
| Rules | Allow + Deny, ordered | Allow only | Allow + Deny, priority |
| Pricing | Free | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Allowing inbound 443 but forgetting outbound ephemeral ports.
✅ Correct: Add return-traffic rules both directions.

❌ Mistake: Using NACLs for everything.
✅ Correct: Keep default NACL, use SGs for app rules, NACL only for explicit IP blocks.

---

## ⚫ Interview Q&A
Q1: [Easy] SG vs NACL?
A1: SG: instance level, stateful, allow-only. NACL: subnet level, stateless, allow + deny.

Q2: [Medium] How are NACL rules evaluated?
A2: By ascending rule number; first match wins; implicit deny at end.

Q3: [Hard] Site works from some clients but connections hang. NACL issue?
A3: Likely missing ephemeral port range in the return direction (client OS ports vary, e.g. Linux 32768-60999, Windows 49152-65535); allow 1024-65535.

---

## ✅ Quick Checklist
□ Ephemeral ports allowed both ways
□ Deny rules numbered lower than allows
□ Default NACL left open unless needed

---

## ⚡ 1-Line Summary
NACL is a stateless, ordered, subnet-level firewall with allow and deny. | NACL सबनेट-स्तर का स्टेटलेस, क्रमबद्ध फ़ायरवॉल है जिसमें allow और deny दोनों होते हैं।

## ➡️ Next: VPC Peering
