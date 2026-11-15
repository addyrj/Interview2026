# 34. EC2 AMI
# AWS: Amazon Machine Image (AMI)
# Azure: VM Image / Azure Compute Gallery image
# हिंदी में: सर्वर की तैयार फ़ोटोकॉपी (OS + सॉफ्टवेयर)

---

## 🔵 Simple Definition
An AMI is a template containing the OS, software and root-volume snapshot used to launch identical EC2 instances.
हिंदी: AMI एक टेम्पलेट है जिसमें OS और सॉफ्टवेयर पहले से होते हैं, उससे एक जैसे कई सर्वर बनते हैं।

---

## 🔴 Why it Exists
Installing everything on each new server is slow and inconsistent. A golden AMI gives fast, identical boots (important for Auto Scaling).

---

## 🟢 How it Works
```
Running instance -> create-image -> EBS snapshot(s) + AMI metadata
AMI (regional) -> launch N instances
Copy to other Region: copy-image ; share: launch permissions to account IDs
Sources: AWS (Amazon Linux), Marketplace, community, your own
```

---

## 💻 Code / Config Example
```bash
# Bake an AMI from a configured instance (--no-reboot is faster but less consistent)
AMI=$(aws ec2 create-image --instance-id i-0123456789abcdef0 \
  --name "api-$(date +%Y%m%d-%H%M)" --query ImageId --output text)
aws ec2 wait image-available --image-ids $AMI

# Latest Amazon Linux 2023 via public SSM parameter
aws ssm get-parameter \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query Parameter.Value --output text

# Copy to another region
aws ec2 copy-image --source-image-id $AMI --source-region ap-south-1 \
  --region ap-southeast-1 --name api-copy

# Cleanup
aws ec2 deregister-image --image-id $AMI   # then delete its snapshots
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Image | AMI (regional) | Managed image / Compute Gallery (replicable) |
| Builder tool | EC2 Image Builder, Packer | Azure Image Builder, Packer |
| Share | Launch permissions | Gallery sharing/RBAC |
| Pricing | Snapshot storage cost only | Storage cost of image |

---

## ⚠️ Common Mistakes
❌ Mistake: Using a stale hard-coded AMI ID.
✅ Correct: Resolve latest via SSM parameter; rebuild golden AMIs regularly with patches.

❌ Mistake: Deregistering AMI and leaving snapshots.
✅ Correct: Delete associated snapshots too.

---

## ⚫ Interview Q&A
Q1: [Easy] Is an AMI regional?
A1: Yes; copy it to use in another Region.

Q2: [Medium] Golden AMI vs user data bootstrap?
A2: Golden AMI: fast boot, consistent, but needs rebuild pipeline. User data: flexible but slower and may fail on external downloads. Often combine both.

Q3: [Hard] Build an AMI pipeline?
A3: GitHub Actions runs Packer (or EC2 Image Builder), tests, tags AMI with git SHA, updates Launch Template version, triggers ASG instance refresh; old AMIs pruned by lifecycle policy.

---

## ✅ Quick Checklist
□ AMI IDs resolved dynamically
□ Images tagged with version/SHA
□ Old AMIs + snapshots cleaned

---

## ⚡ 1-Line Summary
AMI is a reusable server template for fast, identical launches. | AMI सर्वर का दोहराने योग्य टेम्पलेट है जिससे तेज़ और एक जैसे लॉन्च होते हैं।

## ➡️ Next: EC2 Key Pairs
