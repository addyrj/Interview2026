# 32. EC2 — Complete Guide
# AWS: Amazon EC2
# Azure: Azure Virtual Machines
# हिंदी में: क्लाउड में किराये का वर्चुअल सर्वर

---

## 🔵 Simple Definition
EC2 gives resizable virtual servers on demand; you choose OS (AMI), CPU/RAM (instance type), storage (EBS) and network.
हिंदी: EC2 क्लाउड में मांग पर मिलने वाला वर्चुअल सर्वर है, OS, साइज़, स्टोरेज और नेटवर्क आप चुनते हैं।

---

## 🔴 Why it Exists
No hardware buying or waiting. Pay per second/hour, scale up or down, run any stack (Node.js, FastAPI, Docker).

---

## 🟢 How it Works
```
AMI + Instance type + Subnet + SG + Key pair/SSM + IAM role + User data
        -> RunInstances -> pending -> running -> stopping/stopped -> terminated
Billing: running = compute + EBS; stopped = EBS only; terminated = nothing.
Purchasing: On-Demand | Reserved/Savings Plans | Spot (can be reclaimed) 
```

---

## 💻 Code / Config Example
```bash
# Launch a t3.micro with Docker via user data (IMDSv2 required)
cat > userdata.sh <<'EOF'
#!/bin/bash
dnf install -y docker
systemctl enable --now docker
EOF

aws ec2 run-instances \
  --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --instance-type t3.micro \
  --subnet-id subnet-aaaa1111 --security-group-ids sg-aaaa1111 \
  --iam-instance-profile Name=ec2-ssm-profile \
  --metadata-options HttpTokens=required \
  --user-data file://userdata.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=api-1}]'

aws ec2 describe-instances --filters Name=tag:Name,Values=api-1 \
  --query 'Reservations[].Instances[].[InstanceId,State.Name,PublicIpAddress]' --output table
aws ec2 stop-instances --instance-ids i-0123456789abcdef0
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | EC2 | Virtual Machines |
| Image | AMI | Image / Marketplace image |
| Disk | EBS | Managed Disks |
| Cheap interruptible | Spot | Spot VMs |
| Run commands | SSM Run Command | Run Command / Custom Script Extension |
| Pricing | Per-second (Linux, min 60s); approximate, check current docs | Per-second billing for most VMs; check docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Stopped instance assumed free.
✅ Correct: EBS volumes and Elastic IPs still cost.

❌ Mistake: Storing data on instance store or root disk with delete-on-termination.
✅ Correct: Use separate EBS/S3/RDS; snapshot regularly.

---

## ⚫ Interview Q&A
Q1: [Easy] Stop vs terminate?
A1: Stop keeps EBS and can restart; terminate deletes instance (root volume deleted by default).

Q2: [Medium] On-Demand vs Reserved vs Spot?
A2: On-Demand flexible; Reserved/Savings Plans discount for 1-3 year commitment; Spot is deep discount but 2-minute interruption notice.

Q3: [Hard] Host a Node.js API on EC2 with HA?
A3: ALB across 2 AZs -> ASG from Launch Template (Docker image from ECR) in private subnets, SG chain, IAM role (no keys), SSM access, CloudWatch agent, rolling instance refresh from GitHub Actions.

---

## ✅ Quick Checklist
□ IAM role attached, IMDSv2 on
□ SSH closed, SSM used
□ Backups (AMI/EBS snapshots)

---

## ⚡ 1-Line Summary
EC2 is pay-as-you-go virtual servers; design for replacement, not repair. | EC2 pay-as-you-go वर्चुअल सर्वर है; इसे ठीक करने के बजाय बदलने के हिसाब से डिज़ाइन करें।

## ➡️ Next: EC2 Instance Types
