---

# 217. Service Endpoints
# AWS: VPC Gateway Endpoints (S3, DynamoDB)
# Azure: VNet Service Endpoints
# हिंदी में: Subnet से PaaS तक Azure backbone का सीधा रास्ता

---

## 🔵 Simple Definition (2 lines)
A service endpoint extends your subnet identity to an Azure service so it can allow only that subnet, over the backbone.
हिंदी: Service Endpoint subnet की पहचान Azure service तक पहुँचाता है ताकि service सिर्फ उसी subnet को allow करे।

---

## 🔴 Why it Exists (2 lines)
Lock down Storage/SQL to specific subnets without paying for private endpoints.
Traffic stays on Azure's network rather than the internet path.

---

## 🟢 How it Works
```
Subnet (Microsoft.Storage endpoint enabled)
   -> storage account public IP (unchanged) over Azure backbone
Storage firewall rule: allow VNet/subnet X, default action Deny
Not reachable from on-prem via the endpoint; service keeps public IP.
```

---

## 💻 Code / Config Example
```bash
# 1. Enable endpoint on subnet
az network vnet subnet update -g rg-demo --vnet-name vnet-prod -n app \
  --service-endpoints Microsoft.Storage

# 2. Deny by default, then allow the subnet
az storage account update -n mystorage123 -g rg-demo --default-action Deny
az storage account network-rule add -g rg-demo --account-name mystorage123 \
  --vnet-name vnet-prod --subnet app
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Gateway endpoint (S3, DynamoDB) | Service Endpoint |
| Cost | Free | Free |
| Private IP for service | No (route table prefix list) | No |
| Interface alternative | PrivateLink | Private Endpoint |

---

## ⚠️ Common Mistakes
❌ Mistake: Enabling the firewall rule before the endpoint on the subnet.
✅ Correct: Enable endpoint on the subnet first, then add the network rule.

❌ Mistake: Expecting on-prem access to work.
✅ Correct: Use Private Endpoint for on-prem or cross-region access.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a service endpoint? A1: A subnet-level feature to reach PaaS over the backbone and restrict access to the subnet.
Q2: [Medium] Does the service get a private IP? A2: No, it keeps its public IP.
Q3: [Hard] When prefer Private Endpoint? A3: When you need on-prem reachability, per-resource granularity, or to fully disable public access (exfiltration protection).

---

## ✅ Quick Checklist
□ Endpoint enabled on subnet
□ Service firewall default Deny
□ Subnet rule added
□ Consider Private Endpoint for sensitive data

---

## ⚡ 1-Line Summary
Service endpoints are free subnet-to-PaaS rules, no private IP | Service Endpoint मुफ़्त है, subnet से PaaS तक जाता है पर private IP नहीं देता।

## ➡️ Next: 218. Azure DDoS Protection

---
