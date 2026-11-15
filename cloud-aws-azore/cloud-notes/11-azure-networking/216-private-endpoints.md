---

# 216. Private Endpoints
# AWS: AWS PrivateLink / VPC Interface Endpoints
# Azure: Azure Private Endpoint (Private Link)
# हिंदी में: PaaS service को VNet के private IP पर लाना

---

## 🔵 Simple Definition (2 lines)
A Private Endpoint is a NIC with a private IP in your subnet that maps to an Azure PaaS service (Storage, SQL, Key Vault...).
हिंदी: Private Endpoint आपके subnet में private IP वाला NIC है जो किसी PaaS service से जुड़ता है।

---

## 🔴 Why it Exists (2 lines)
PaaS services have public endpoints; compliance often demands no public exposure.
Private Endpoint keeps traffic on the Microsoft backbone and lets you disable public access.

---

## 🟢 How it Works
```
App VM/AKS (10.0.2.5) -> mystorage.blob.core.windows.net
   Private DNS zone privatelink.blob.core.windows.net (linked to VNet)
   -> resolves to 10.0.3.4 (Private Endpoint NIC) -> Storage account (Private Link)
Public network access can then be Disabled on the service.
```

---

## 💻 Code / Config Example
```bash
STORAGE_ID=$(az storage account show -n mystorage123 -g rg-demo --query id -o tsv)

az network vnet subnet update -g rg-demo --vnet-name vnet-prod -n pe-subnet \
  --private-endpoint-network-policies Disabled

az network private-endpoint create -g rg-demo -n pe-blob \
  --vnet-name vnet-prod --subnet pe-subnet \
  --private-connection-resource-id "$STORAGE_ID" \
  --group-id blob --connection-name conn-blob

# DNS so the normal hostname resolves privately
az network private-dns zone create -g rg-demo -n privatelink.blob.core.windows.net
az network private-dns link vnet create -g rg-demo -z privatelink.blob.core.windows.net \
  -n link1 -v vnet-prod -e false
az network private-endpoint dns-zone-group create -g rg-demo --endpoint-name pe-blob \
  -n zg --private-dns-zone privatelink.blob.core.windows.net --zone-name blob
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | PrivateLink interface endpoint | Private Endpoint |
| S3 special case | Gateway endpoint (free) | Service endpoint (free) or Private Endpoint |
| DNS | Private DNS on endpoint | privatelink.* private DNS zone |
| Pricing | Per endpoint-hour + GB (approximate — check current docs) | Per endpoint-hour + GB (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Creating the endpoint but no private DNS zone, so the name still resolves to the public IP.
✅ Correct: Link the correct `privatelink.*` zone to every VNet that needs it.

❌ Mistake: Leaving public network access enabled.
✅ Correct: Disable it after validating private access.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a Private Endpoint? A1: A private IP in your VNet for a PaaS resource.
Q2: [Medium] Private vs Service Endpoint? A2: Private Endpoint gives a private IP per resource and is reachable from on-prem; Service Endpoint keeps the public IP but restricts access to your subnet.
Q3: [Hard] On-prem DNS resolution? A3: Forward the privatelink zone to Azure DNS Private Resolver or a DNS forwarder in the VNet (168.63.129.16 is only reachable inside Azure).

---

## ✅ Quick Checklist
□ Correct group-id
□ Private DNS zone linked
□ Public access disabled
□ NSG/route rules reviewed

---

## ⚡ 1-Line Summary
Private Endpoint brings a PaaS service onto a private IP (PrivateLink) | Private Endpoint PaaS service को आपके VNet के private IP पर लाता है।

## ➡️ Next: 217. Service Endpoints

---
