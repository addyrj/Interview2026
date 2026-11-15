# 27. Security Groups
# AWS: Security Groups (SG)
# Azure: Network Security Group (NSG)
# हिंदी में: इंस्टेंस के स्तर का स्टेटफुल फ़ायरवॉल

---

## 🔵 Simple Definition
A Security Group is a stateful virtual firewall attached to network interfaces (EC2, RDS, ALB); it only has allow rules.
हिंदी: Security Group एक स्टेटफुल फ़ायरवॉल है जो सिर्फ allow नियम रखता है और इंस्टेंस से जुड़ा होता है।

---

## 🔴 Why it Exists
Least-privilege network access: only the ALB talks to the app, only the app talks to the DB.

---

## 🟢 How it Works
```
Internet -> [ALB SG: 443 from 0.0.0.0/0]
              -> [App SG: 3000 from ALB SG]
                   -> [DB SG: 5432 from App SG]
Stateful: reply to an allowed request is auto-allowed.
Default: all inbound denied, all outbound allowed. Rules evaluated together (no order).
```

---

## 💻 Code / Config Example
```bash
VPC_ID=vpc-0123456789abcdef0
ALB_SG=$(aws ec2 create-security-group --group-name alb-sg --description alb \
  --vpc-id $VPC_ID --query GroupId --output text)
APP_SG=$(aws ec2 create-security-group --group-name app-sg --description app \
  --vpc-id $VPC_ID --query GroupId --output text)

aws ec2 authorize-security-group-ingress --group-id $ALB_SG \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# Reference another SG instead of an IP range
aws ec2 authorize-security-group-ingress --group-id $APP_SG \
  --protocol tcp --port 3000 --source-group $ALB_SG

# SSH only from your IP
aws ec2 authorize-security-group-ingress --group-id $APP_SG \
  --protocol tcp --port 22 --cidr 203.0.113.10/32
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS SG | Azure NSG |
|---------|--------|-----------|
| Rules | Allow only | Allow and Deny, with priority |
| State | Stateful | Stateful |
| Attach to | ENI / instance | Subnet or NIC |
| Reference groups | SG ids | Application Security Groups |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: `0.0.0.0/0` on port 22 or 5432.
✅ Correct: Restrict to your IP/SG, or use SSM Session Manager (no open port).

❌ Mistake: Expecting a "deny" rule.
✅ Correct: SGs cannot deny; use NACLs to block an IP.

---

## ⚫ Interview Q&A
Q1: [Easy] Stateful meaning?
A1: Return traffic for allowed connections is automatically allowed, no explicit rule.

Q2: [Medium] Can you attach multiple SGs to one instance?
A2: Yes; rules are a union (default quota is limited, approximate, check current docs).

Q3: [Hard] Design SGs for 3-tier app.
A3: ALB SG allows 443 from internet; app SG allows app port only from ALB SG; DB SG allows DB port only from app SG; no inbound SSH, use SSM.

---

## ✅ Quick Checklist
□ SG-to-SG references, not wide CIDRs
□ No 0.0.0.0/0 on admin/DB ports
□ Outbound reviewed for sensitive tiers

---

## ⚡ 1-Line Summary
Security Groups are stateful allow-only firewalls attached to ENIs. | Security Group ENI से जुड़ा स्टेटफुल, सिर्फ-allow वाला फ़ायरवॉल है।

## ➡️ Next: Network ACLs
