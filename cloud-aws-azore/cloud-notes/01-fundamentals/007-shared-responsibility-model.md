---

# 7. Shared Responsibility Model
# AWS: "Security OF the cloud vs security IN the cloud"
# Azure: Shared responsibility in the cloud (varies by IaaS/PaaS/SaaS)
# हिंदी में: सुरक्षा की ज़िम्मेदारी प्रोवाइडर और ग्राहक के बीच बँटी होती है

---

## 🔵 Simple Definition (2 lines)
The provider secures the underlying cloud (hardware, facilities, hypervisor). You secure what you put in it: data, identities, configs, apps.
हिंदी: क्लाउड का इंफ्रा प्रोवाइडर सुरक्षित करता है, आपका डेटा, यूज़र और सेटिंग्स आपकी ज़िम्मेदारी है।

---

## 🔴 Why it Exists (2 lines)
Many breaches come from customer misconfiguration (public buckets), not provider failures.
Clear boundaries stop teams assuming "AWS/Azure handles it".

---

## 🟢 How it Works
```
 Customer: data, IAM, app code, OS patches (on VMs),
           security groups/NSGs, encryption choices
 -------------------------------------------------
 Provider: physical DCs, hardware, network, hypervisor,
           managed-service software (RDS engine patching, etc.)

 EC2 / VM  -> you patch the guest OS
 RDS / SQL -> provider patches engine; you manage access + data
 S3 / Blob -> provider durability; you manage bucket policy + public access
```

---

## 💻 Code / Config Example
```bash
# Your side of the line: block public access on an S3 bucket
aws s3api put-public-access-block --bucket my-app-bucket \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Azure: disable anonymous blob access on a storage account
az storage account update --name mystorageacct --resource-group demo-rg \
  --allow-blob-public-access false
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Model name | Shared Responsibility Model | Shared responsibility model |
| Compliance reports | AWS Artifact | Service Trust Portal |
| Posture check | Trusted Advisor, Security Hub | Defender for Cloud |
| Pricing | Artifact free; others vary (check docs) | Basic posture free tier; Defender plans paid (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Thinking RDS/Azure SQL means no security work.
✅ Correct: You still own network rules, credentials, encryption settings and backups policy.

❌ Mistake: Leaving OS unpatched on EC2/VMs.
✅ Correct: Use patch automation (Systems Manager Patch Manager / Update Manager).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Who secures the physical data center?
A1: The provider.

Q2: [Medium] How does it differ for EC2 vs Lambda?
A2: On EC2 you patch the OS and runtime; on Lambda the provider manages OS/runtime, you own code, IAM and data.

Q3: [Hard] A public S3 bucket leaked data. Whose fault and how to prevent?
A3: Customer configuration. Prevent with account-level Block Public Access, least-privilege policies, Config/Security Hub rules and access reviews.

---

## ✅ Quick Checklist
□ I know my side for each service I use
□ Public access blocked by default
□ Patching and IAM reviews are scheduled

---

## ⚡ 1-Line Summary
Provider secures the cloud, you secure what is in it | प्रोवाइडर क्लाउड की, आप अपने डेटा और कॉन्फ़िग की सुरक्षा करते हैं।

## ➡️ Next: 8. High Availability Concepts

---
