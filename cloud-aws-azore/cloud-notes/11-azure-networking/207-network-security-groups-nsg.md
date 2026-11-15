---

# 207. Network Security Groups (NSG)
# AWS: Security Groups + Network ACLs
# Azure: Network Security Group (NSG)
# हिंदी में: Subnet/NIC का traffic filter (firewall rules)

---

## 🔵 Simple Definition (2 lines)
An NSG is a list of allow/deny rules (5-tuple) filtering inbound and outbound traffic to subnets or NICs.
हिंदी: NSG allow/deny rules की सूची है जो subnet या NIC पर आने-जाने वाले traffic को filter करती है।

---

## 🔴 Why it Exists (2 lines)
Without filtering any reachable VM port is exposed; you need least-privilege network access.
NSGs give stateful rule-based control at L3/L4 for free.

---

## 🟢 How it Works
```
Packet -> rules evaluated by priority (100 .. 4096, lowest number first)
   first match wins -> Allow / Deny
Default rules (65000+): allow VNet-to-VNet, allow LB probes, deny all other inbound,
                        allow all outbound
Stateful: return traffic is allowed automatically.
```

---

## 💻 Code / Config Example
```bash
az network nsg create -g rg-demo -n nsg-web

# Allow HTTPS from internet
az network nsg rule create -g rg-demo --nsg-name nsg-web -n allow-https \
  --priority 100 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes Internet --destination-port-ranges 443

# Allow SSH only from office IP (documentation range used here)
az network nsg rule create -g rg-demo --nsg-name nsg-web -n allow-ssh-office \
  --priority 110 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes 203.0.113.10/32 --destination-port-ranges 22

# Attach to subnet
az network vnet subnet update -g rg-demo --vnet-name vnet-prod -n web \
  --network-security-group nsg-web
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Security Group (stateful) + NACL (stateless) | NSG (stateful) |
| Attach to | ENI / instance | Subnet and/or NIC |
| Deny rules | NACL only | Yes, in NSG |
| Group by role | Reference other SGs | Application Security Groups (ASG) |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Allowing `*` source on port 22/3389.
✅ Correct: Restrict to specific IPs or use Azure Bastion / JIT access.

❌ Mistake: Confusing priority order.
✅ Correct: Lower number = evaluated first; leave gaps (100, 110, 120).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is an NSG? A1: A stateful allow/deny rule set for network traffic.
Q2: [Medium] Subnet NSG and NIC NSG both exist, which applies? A2: Both; inbound hits subnet NSG then NIC NSG, outbound the reverse; both must allow.
Q3: [Hard] NSG vs Azure Firewall? A3: NSG is free L3/L4 filtering per subnet/NIC; Firewall is a central L3-L7 service with FQDN filtering, threat intel and logging.

---

## ✅ Quick Checklist
□ Default deny posture
□ No Any-source admin ports
□ ASGs used for tiers
□ NSG flow logs enabled

---

## ⚡ 1-Line Summary
NSG is Azure's free stateful subnet/NIC firewall | NSG Azure का मुफ़्त stateful firewall है जो subnet/NIC पर लगता है।

## ➡️ Next: 208. Azure Firewall

---
