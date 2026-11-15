---

# 1. What is Cloud Computing
# AWS: Amazon Web Services (whole platform)
# Azure: Microsoft Azure (whole platform)
# हिंदी में: क्लाउड कंप्यूटिंग = इंटरनेट पर किराये के सर्वर, स्टोरेज और सर्विसेज़

---

## 🔵 Simple Definition (2 lines)
Cloud computing means renting compute, storage, network and managed services over the internet, on demand, and paying only for what you use.
हिंदी: अपना हार्डवेयर खरीदने की जगह इंटरनेट से ज़रूरत के हिसाब से सर्वर किराये पर लेना और सिर्फ़ इस्तेमाल का पैसा देना।

---

## 🔴 Why it Exists (2 lines)
Buying servers takes weeks, needs big upfront money, and is wasted when traffic is low or too small when traffic spikes.
Cloud gives servers in minutes through an API, so a small team can ship a global product.

---

## 🟢 How it Works
```
 You (Console / CLI / API / Terraform)
            |
            v
   +---------------------+
   |  Cloud provider API |  <- auth, billing, quotas
   +---------------------+
            |
   Virtualized pool of hardware (many data centers)
   [Compute] [Storage] [Network] [Managed DB] ...
            |
   You get: VM / bucket / DB in minutes -> metered per second/hour/GB
```
Five NIST traits: on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service.

---

## 💻 Code / Config Example
```bash
# Launch one small VM from the CLI (needs configured credentials).
# AWS (CLI v2): AMI id is region-specific -- replace it.
aws ec2 run-instances --image-id ami-0123456789abcdef0 \
  --instance-type t3.micro --count 1 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=demo}]'

# Azure (az CLI): create group, then VM
az group create --name demo-rg --location centralindia
az vm create --resource-group demo-rg --name demo-vm \
  --image Ubuntu2204 --size Standard_B1s --generate-ssh-keys
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Virtual machine | EC2 | Virtual Machines |
| Object storage | S3 | Blob Storage |
| Management unit | Account | Subscription + Resource Group |
| Pricing | Pay-as-you-go, free tier (terms change, check docs) | Pay-as-you-go, free account credit (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Treating cloud as "someone else's server" and leaving resources running forever.
✅ Correct: Tag resources, set budgets/alerts, and delete or schedule-stop unused ones.

❌ Mistake: Lifting a VPS setup 1:1 and ignoring managed services.
✅ Correct: Use managed DB/queue/storage where it saves operations work.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is cloud computing?
A1: On-demand delivery of IT resources over the internet with pay-as-you-go pricing.

Q2: [Medium] What are its key characteristics?
A2: Self-service, broad network access, pooled resources, rapid elasticity, metered usage.

Q3: [Hard] When might cloud NOT be the right choice?
A3: Steady, predictable heavy load (reserved hardware can be cheaper), strict data-residency/latency needs, or heavy egress traffic where bandwidth costs dominate.

---

## ✅ Quick Checklist
□ I can name the 5 NIST traits
□ I know the console / CLI / IaC ways to create resources
□ I set a budget alert on every new account

---

## ⚡ 1-Line Summary
Cloud = rent infrastructure on demand, pay per use | क्लाउड = ज़रूरत पर किराये का इंफ्रा, जितना इस्तेमाल उतना भुगतान।

## ➡️ Next: 2. Cloud vs On-Premise vs VPS

---
