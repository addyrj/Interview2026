# 288. Storage Services Comparison
# AWS: S3, EBS, EFS, Glacier
# Azure: Blob Storage, Managed Disks, Azure Files, Archive tier
# हिंदी में: स्टोरेज सर्विसेज की तुलना

---

## 🔵 Simple Definition
Object, block and file storage exist on both clouds with tiers from hot to archive.
हिंदी: दोनों में ऑब्जेक्ट, ब्लॉक और फाइल स्टोरेज हैं, हॉट से आर्काइव तक टियर के साथ।

---

## 🔴 Why it Exists
Different data needs different access speed and cost: uploads, VM disks, shared files, backups.

---

## 🟢 How it Works
```
Object : S3            <-> Blob Storage (container/blob)
Block  : EBS           <-> Managed Disks
File   : EFS (NFS)     <-> Azure Files (SMB/NFS)
Cold   : S3 Glacier    <-> Blob Archive tier
```

---

## 💻 Code / Config Example
```bash
# Create bucket/container and upload
aws s3 mb s3://my-app-uploads
aws s3 cp ./logo.png s3://my-app-uploads/

az storage account create -n myappuploads123 -g rg-demo --sku Standard_LRS
az storage container create --account-name myappuploads123 -n uploads --auth-mode login
az storage blob upload --account-name myappuploads123 -c uploads -f logo.png -n logo.png --auth-mode login
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Object namespace | Bucket | Storage account + container |
| Temp access | Presigned URL | SAS token |
| Redundancy | Standard (multi-AZ), CRR | LRS, ZRS, GRS |
| Lifecycle | Lifecycle rules | Lifecycle management policy |

---

## ⚠️ Common Mistakes
❌ Mistake: Public buckets/containers by default.
✅ Correct: Block public access; serve via CDN or presigned URL/SAS.

❌ Mistake: Long-lived SAS keys or account keys in code.
✅ Correct: Managed identity or short-lived, scoped SAS.

---

## ⚫ Interview Q&A
Q1: [Easy] S3 equivalent?
A1: Blob Storage.

Q2: [Medium] Presigned URL equivalent?
A2: SAS token (ideally user delegation SAS).

Q3: [Hard] Cut cost of old logs?
A3: Lifecycle rules: move to infrequent/cool, then Glacier/Archive, then delete; account for retrieval fees and minimum retention.

---

## ✅ Quick Checklist
□ Public access blocked
□ Lifecycle policy set
□ Encryption + versioning on

---

## ⚡ 1-Line Summary
S3=Blob, EBS=Managed Disks, EFS=Azure Files. | S3=Blob, EBS=Managed Disks, EFS=Azure Files।

## ➡️ Next: 289. Networking Comparison
