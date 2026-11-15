---

# 212. Azure DNS
# AWS: Amazon Route 53
# Azure: Azure DNS (+ Private DNS zones, Traffic Manager)
# हिंदी में: Domain के नाम को IP में बदलने की सेवा

---

## 🔵 Simple Definition (2 lines)
Azure DNS hosts your DNS zones (public and private) on Azure's anycast name servers.
हिंदी: Azure DNS आपके domain के DNS records को Azure के name servers पर host करता है।

---

## 🔴 Why it Exists (2 lines)
You need reliable name resolution managed with the same RBAC, IaC and tooling as other Azure resources.
Private zones give internal names (e.g. db.internal) inside VNets.

---

## 🟢 How it Works
```
Registrar NS records -> Azure DNS name servers (ns1-xx.azure-dns.com ...)
Public zone  example.com:  A, AAAA, CNAME, MX, TXT, alias records
Private zone internal.local: linked to VNet(s) -> auto-resolve VM/PE names
Alias record -> points at Azure resource (Front Door, public IP) with no dangling risk
```
Note: Azure DNS is not a domain registrar; it has no built-in latency/geo routing (use Traffic Manager).

---

## 💻 Code / Config Example
```bash
az network dns zone create -g rg-demo -n example.com

az network dns record-set a add-record -g rg-demo -z example.com \
  -n api -a 20.40.60.80

az network dns record-set cname set-record -g rg-demo -z example.com \
  -n www -c example.azurefd.net

# Private zone linked to a VNet
az network private-dns zone create -g rg-demo -n internal.local
az network private-dns link vnet create -g rg-demo -z internal.local \
  -n link-prod -v vnet-prod -e false
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Route 53 | Azure DNS |
| Registrar | Yes | No (use external registrar / App Service domains) |
| Routing policies | Latency, geo, weighted, failover | Via Traffic Manager / Front Door |
| Pricing | Per zone + per million queries (approximate — check current docs) | Per zone + per million queries (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Creating the zone but not updating NS at the registrar.
✅ Correct: Copy the 4 Azure NS values to the registrar.

❌ Mistake: CNAME at the zone apex.
✅ Correct: Use an alias A record at the apex.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Azure DNS? A1: Hosting for DNS zones on Azure, like Route 53 zones.
Q2: [Medium] What are alias records? A2: Records that reference an Azure resource directly and update with it.
Q3: [Hard] How does private DNS work with private endpoints? A3: A `privatelink.*` private zone is linked to the VNet so the service FQDN resolves to the private IP.

---

## ✅ Quick Checklist
□ NS delegated at registrar
□ Low TTL before migrations
□ Private zones linked to VNets
□ RBAC/locks on zones

---

## ⚡ 1-Line Summary
Azure DNS hosts public/private zones (Route 53 without registrar) | Azure DNS public/private zones host करता है, Route 53 जैसा पर registrar के बिना।

## ➡️ Next: 213. VNet Peering

---
