# 38. Launch Template
# AWS: EC2 Launch Template (replaces Launch Configuration)
# Azure: VMSS model / VM image + ARM/Bicep template
# हिंदी में: इंस्टेंस कैसे बनेगा इसका सेव किया हुआ नक्शा

---

## 🔵 Simple Definition
A Launch Template stores launch parameters (AMI, type, SG, IAM profile, user data, tags) and supports multiple versions.
हिंदी: Launch Template में इंस्टेंस बनाने की सारी सेटिंग सेव रहती हैं और इसके कई वर्ज़न बन सकते हैं।

---

## 🔴 Why it Exists
ASGs and fleets need a repeatable recipe. Launch Configurations were immutable and are deprecated; templates are versioned and support newer features.

---

## 🟢 How it Works
```
Launch Template lt-xxx
  v1 (AMI-old)  v2 (AMI-new)  v3 ...   Default / $Latest
ASG -> uses lt-xxx:$Default (or $Latest) 
New AMI -> create-launch-template-version -> instance refresh
```

---

## 💻 Code / Config Example
```bash
cat > lt.json <<'EOF'
{
  "ImageId": "resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64",
  "InstanceType": "t3.small",
  "SecurityGroupIds": ["sg-aaaa1111"],
  "IamInstanceProfile": {"Name": "api-profile"},
  "MetadataOptions": {"HttpTokens": "required"},
  "TagSpecifications": [
    {"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": "api"}]}
  ]
}
EOF
python3 -c "import json;json.load(open('lt.json'))" && echo json ok

aws ec2 create-launch-template --launch-template-name api-lt \
  --launch-template-data file://lt.json

# New version from the old one with a different type
aws ec2 create-launch-template-version --launch-template-name api-lt \
  --source-version 1 --launch-template-data '{"InstanceType":"t3.medium"}'
aws ec2 modify-launch-template --launch-template-name api-lt --default-version 2
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Recipe | Launch Template | Scale set model / Bicep |
| Versioning | Built in | Via template/gallery versions |
| Mixed spot/on-demand | Supported via ASG mixed instances | Flexible orchestration, Spot priority mix |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Using legacy Launch Configurations.
✅ Correct: Use Launch Templates (AWS no longer adds new features to Launch Configurations).

❌ Mistake: ASG points to `$Latest` in prod and a bad edit auto-rolls out.
✅ Correct: Point to an explicit/`$Default` version, promote after testing.

---

## ⚫ Interview Q&A
Q1: [Easy] What goes in a Launch Template?
A1: AMI, instance type, key, SGs, IAM profile, user data, block devices, tags.

Q2: [Medium] How to roll out a new AMI?
A2: New template version, set default, `start-instance-refresh` on the ASG with min healthy percentage.

Q3: [Hard] Mixed On-Demand and Spot?
A3: ASG MixedInstancesPolicy with template overrides for several types, on-demand base capacity, capacity-optimized Spot allocation.

---

## ✅ Quick Checklist
□ Versioned, IMDSv2 required
□ IAM profile attached
□ Explicit version used by ASG

---

## ⚡ 1-Line Summary
Launch Template is a versioned instance recipe used by ASGs. | Launch Template इंस्टेंस की वर्ज़न वाली रेसिपी है जिसे ASG इस्तेमाल करता है।

## ➡️ Next: Auto Scaling Group
