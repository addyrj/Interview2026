---

# 208. Azure Firewall
# AWS: AWS Network Firewall
# Azure: Azure Firewall
# हिंदी में: पूरे network के लिए central managed firewall

---

## 🔵 Simple Definition (2 lines)
Azure Firewall is a managed, stateful, central firewall with FQDN filtering, NAT and threat intelligence.
हिंदी: Azure Firewall एक managed central firewall है जो FQDN, NAT और threat intelligence के साथ traffic रोकता है।

---

## 🔴 Why it Exists (2 lines)
NSGs filter by IP/port only; teams need domain-based egress control and central logging.
One firewall in a hub VNet inspects traffic for all spokes.

---

## 🟢 How it Works
```
Spoke VNets --UDR 0.0.0.0/0 next hop--> Azure Firewall (hub, AzureFirewallSubnet /26)
    rule order: DNAT rules -> Network rules -> Application rules
    -> Internet / on-prem      logs -> Log Analytics
SKUs: Basic, Standard, Premium (TLS inspection, IDPS)
```

---

## 💻 Code / Config Example
```bash
az extension add --name azure-firewall
az network vnet subnet create -g rg-demo --vnet-name vnet-hub \
  -n AzureFirewallSubnet --address-prefixes 10.0.0.0/26
az network public-ip create -g rg-demo -n fw-pip --sku Standard --allocation-method Static

az network firewall create -g rg-demo -n fw-hub -l centralindia
az network firewall ip-config create -g rg-demo -f fw-hub -n cfg \
  --public-ip-address fw-pip --vnet-name vnet-hub

# Allow only specific FQDNs outbound for app subnet
az network firewall application-rule create -g rg-demo -f fw-hub \
  -c allow-web --priority 200 --action Allow -n github \
  --source-addresses 10.0.2.0/24 --protocols Https=443 \
  --target-fqdns github.com registry.npmjs.org
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Network Firewall (Suricata rules) | Azure Firewall |
| FQDN filtering | Yes (domain lists) | Yes (application rules) |
| Deployment | Firewall endpoints in subnets | Dedicated AzureFirewallSubnet |
| Pricing | Hourly endpoint + per GB (approximate — check current docs) | Hourly deployment + per GB, by SKU (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Deploying Firewall for a single small VM app.
✅ Correct: It is costly; use NSG + NAT Gateway unless you need FQDN/central control.

❌ Mistake: Forgetting the UDR on spoke subnets.
✅ Correct: Add a 0.0.0.0/0 route to the firewall private IP, else traffic bypasses it.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Azure Firewall? A1: A managed stateful firewall service in Azure.
Q2: [Medium] Rule processing order? A2: DNAT, then network rules, then application rules.
Q3: [Hard] Hub-and-spoke egress design? A3: Firewall in hub, UDRs in spokes, peering with "use remote gateway/forwarded traffic" settings, and diagnostic logs to Log Analytics.

---

## ✅ Quick Checklist
□ AzureFirewallSubnet /26
□ UDR on spokes
□ Logs to Log Analytics
□ SKU matches need (cost aware)

---

## ⚡ 1-Line Summary
Azure Firewall is a central managed firewall with FQDN rules | Azure Firewall FQDN rules वाला central managed firewall है।

## ➡️ Next: 209. Azure Load Balancer

---
