---

# 2. Cloud vs On-Premise vs VPS
# AWS: EC2 / Lightsail (VPS-like) vs Outposts (on-prem)
# Azure: Virtual Machines vs Azure Stack HCI / Arc (on-prem)
# हिंदी में: क्लाउड बनाम अपना डेटा सेंटर बनाम सस्ता VPS

---

## 🔵 Simple Definition (2 lines)
On-premise = you own and run hardware in your building. VPS = a fixed virtual server rented from a host (DigitalOcean, Hetzner). Cloud = a huge API-driven platform with elastic servers plus hundreds of managed services.
हिंदी: On-prem में हार्डवेयर आपका, VPS में एक फ़िक्स्ड किराये का सर्वर, और क्लाउड में ज़रूरत के हिसाब से घटने-बढ़ने वाली सर्विसेज़।

---

## 🔴 Why it Exists (2 lines)
Teams need to pick the right trade-off between control, cost and operational effort.
A VPS is cheap for one app; cloud wins when you need autoscaling, managed DBs, IAM and multi-region.

---

## 🟢 How it Works
```
            Control   Effort   Elasticity   Cost shape
On-prem      high     highest  low          big CapEx
VPS          medium   medium   low (resize) small flat monthly
Cloud        shared   lowest*  high         usage-based OpEx
(*if you use managed services)

Your stack: Docker app on 1 VPS  -->  ECS/App Service + RDS + S3
```

---

## 💻 Code / Config Example
```bash
# Same Docker app, two homes.
# VPS: ssh in and run it yourself
ssh deploy@my-vps "docker run -d --restart=always -p 80:3000 myapp:1.0"

# AWS: managed container service (cluster/service must already exist)
aws ecs update-service --cluster prod --service api --force-new-deployment

# Azure: Web App for Containers
az webapp config container set --resource-group demo-rg --name my-api \
  --container-image-name myacr.azurecr.io/myapp:1.0
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| VPS-like simple server | Lightsail | VM (B-series) |
| On-prem extension | Outposts | Azure Arc / Stack HCI |
| Autoscaling | Auto Scaling Groups | VM Scale Sets |
| Pricing | Per-second billing for EC2 Linux (check docs) | Per-second billing for most VMs (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Moving a steady 1-server app to cloud and paying 3x a VPS.
✅ Correct: Compare total cost incl. egress, managed DB and ops time before moving.

❌ Mistake: Ignoring backups on a VPS because "it is a server".
✅ Correct: Snapshots plus off-site backups; the host does not back up for you by default.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Difference between VPS and cloud VM?
A1: VPS is usually a fixed plan with simple pricing; cloud VMs are part of an API platform with autoscaling, IAM, networking and managed add-ons.

Q2: [Medium] When keep on-premise?
A2: Regulatory/data-sovereignty needs, ultra-low latency to local equipment, or already-paid hardware with steady load.

Q3: [Hard] How do you migrate a VPS Docker app with minimal downtime?
A3: Containerize, build cloud infra with IaC, replicate DB, deploy in parallel, lower DNS TTL, cut over with weighted DNS, keep VPS as rollback.

---

## ✅ Quick Checklist
□ Compared monthly cost including bandwidth
□ Know my RTO/RPO needs
□ Have IaC so the setup is repeatable

---

## ⚡ 1-Line Summary
VPS is cheap and simple, cloud is elastic and managed, on-prem is full control | VPS सस्ता, क्लाउड लचीला, On-prem पूरा कंट्रोल।

## ➡️ Next: 3. IaaS vs PaaS vs SaaS

---
