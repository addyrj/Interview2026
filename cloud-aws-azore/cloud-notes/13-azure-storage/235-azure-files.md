# 235. Azure Files
# AWS: Amazon EFS (NFS) / FSx for Windows (SMB)
# Azure: Azure Files
# हिंदी में: क्लाउड में मैनेज्ड नेटवर्क फ़ाइल शेयर (SMB/NFS)

---

## 🔵 Simple Definition (2 lines)
Azure Files provides managed file shares accessible via SMB or NFS that can be mounted on VMs, containers and on-prem machines.
हिंदी: कई सर्वर एक ही शेयर्ड फ़ोल्डर mount करके साथ में उपयोग कर सकते हैं।

---

## 🔴 Why it Exists (2 lines)
Legacy apps and shared configs need a POSIX/SMB filesystem, not object APIs.
Containers need persistent shared volumes.

---

## 🟢 How it Works
```
Storage Account -> File Share (quota)
   SMB 3.x (port 445)  -> Windows / Linux mount
   NFS 4.1 (premium)   -> Linux only
   Azure File Sync     -> cache share on on-prem Windows Server
Container Apps / AKS / Docker host mount the share as a volume
```

---

## 💻 Code / Config Example
```bash
az storage share-rm create --resource-group rg-app --storage-account myappstore \
  --name appdata --quota 100
# Mount on a Linux VPS/VM over SMB (port 445 must be open)
sudo mkdir -p /mnt/appdata
sudo mount -t cifs //myappstore.file.core.windows.net/appdata /mnt/appdata \
  -o username=myappstore,password="$STORAGE_KEY",serverino,nosharesock,actimeo=30,vers=3.1.1
```
```yaml
# docker-compose with a CIFS volume
services:
  api:
    image: myapp/api:latest
    volumes: [ "appdata:/data" ]
volumes:
  appdata:
    driver: local
    driver_opts:
      type: cifs
      device: //myappstore.file.core.windows.net/appdata
      o: "username=myappstore,password=${STORAGE_KEY},vers=3.1.1"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| NFS | EFS | Azure Files NFS (premium) |
| SMB | FSx for Windows | Azure Files SMB |
| Hybrid cache | Storage Gateway | Azure File Sync |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Port 445 blocked by ISP/firewall, so the mount hangs.
✅ Correct: Use VPN/ExpressRoute or private endpoint, or run inside Azure.

❌ Mistake: Putting a database data directory on Files.
✅ Correct: Use managed disks or a managed DB.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Protocols supported?
A1: SMB and NFS (NFS on premium shares).

Q2: [Medium] Files vs Blob?
A2: Files = filesystem semantics and shared mount; Blob = object API, cheaper and more scalable.

Q3: [Hard] Share across Container Apps replicas?
A3: Define an Azure Files storage mount on the environment and mount it in each app; watch file-locking and latency; consider Blob if no filesystem need.

---

## ✅ Quick Checklist
□ Protocol (SMB/NFS) matches OS
□ Private endpoint / secure transfer
□ Snapshots or backup enabled

---

## ⚡ 1-Line Summary
Azure Files = managed SMB/NFS shares, like EFS | Azure Files = मैनेज्ड SMB/NFS शेयर, EFS जैसा

## ➡️ Next: Azure Queue Storage

---
