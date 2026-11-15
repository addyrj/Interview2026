# 191. Azure Virtual Machines
# AWS: EC2
# Azure: Azure Virtual Machines
# हिंदी में: Azure में किराए का वर्चुअल सर्वर जिस पर आप पूरा कंट्रोल रखते हैं

---

## 🔵 Simple Definition
IaaS virtual machines: you pick an image, size, disk and network, and manage the OS and software yourself.
VM में आप OS से लेकर ऐप तक खुद संभालते हैं; Azure हार्डवेयर संभालता है।

---

## 🔴 Why it Exists
Workloads that need full OS control, custom software, or lift-and-shift of VPS-style apps (Docker on a Linux box).

---

## 🟢 How it Works
```
Image (Ubuntu 22.04) + Size (Standard_B2s) + OS disk (+data disks)
   + NIC -> VNet/Subnet (+ NSG, public IP) + SSH key
Availability: Availability Zone / Availability Set / Scale Set
Billing: running = compute charged; Deallocated = no compute charge (disks/IP still billed)
```

---

## 💻 Code / Config Example
```bash
az group create -n rg-vm -l centralindia
az vm create -g rg-vm -n vm-api-01 \
  --image Ubuntu2204 --size Standard_B2s \
  --admin-username azureuser --generate-ssh-keys \
  --public-ip-sku Standard
az vm open-port -g rg-vm -n vm-api-01 --port 80
# Install Docker via cloud-init is better; quick run:
az vm run-command invoke -g rg-vm -n vm-api-01 \
  --command-id RunShellScript --scripts "curl -fsSL https://get.docker.com | sh"
az vm deallocate -g rg-vm -n vm-api-01   # stop billing for compute
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | EC2 | Virtual Machines |
| Access | Key pair / SSM | SSH key / Bastion / Run Command |
| Firewall | Security Group | NSG |
| Pricing | Per second (Linux) | Per second; Reserved/Spot discounts (approximate - check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Stopping from inside the OS and expecting no charge.
✅ Correct: Deallocate via Azure.

❌ Mistake: Opening SSH 22 to `*`.
✅ Correct: Restrict source IP, or use Bastion / JIT access.

---

## ⚫ Interview Q&A
Q1: [Easy] Stopped vs deallocated?
A1: Stopped keeps the allocation and billing; deallocated releases compute and stops compute charges.

Q2: [Medium] Availability Zone vs Set?
A2: Zones span datacenters in a region; sets spread across fault/update domains within one datacenter.

Q3: [Hard] Deploy a Node.js app on VMs with high availability?
A3: Two+ VMs across zones behind a Standard Load Balancer or Application Gateway, health probes, a VMSS, managed DB, and GitHub Actions deploying via SSH or images.

---

## ✅ Quick Checklist
□ SSH keys, no passwords
□ NSG restricted
□ Auto-shutdown/deallocate for dev

---

## ⚡ 1-Line Summary
Azure VM = EC2-style IaaS server. | Azure VM = EC2 जैसा पूरा-नियंत्रण वाला सर्वर।

## ➡️ Next: VM Sizes + Pricing
