---

# 210. Azure Application Gateway
# AWS: Application Load Balancer (ALB) + AWS WAF
# Azure: Azure Application Gateway (+ WAF)
# हिंदी में: Layer-7 (HTTP/HTTPS) load balancer और WAF

---

## 🔵 Simple Definition (2 lines)
Application Gateway is a regional Layer-7 load balancer with URL/host routing, TLS termination and optional WAF.
हिंदी: Application Gateway HTTP/HTTPS के लिए Layer-7 load balancer है, जिसमें URL routing, TLS और WAF है।

---

## 🔴 Why it Exists (2 lines)
Web apps need path-based routing, SSL offload and protection from OWASP attacks, which L4 LBs cannot do.
One gateway fronts many backends (e.g. /api to NestJS, /ml to FastAPI).

---

## 🟢 How it Works
```
Client HTTPS -> Public frontend IP -> Listener (cert) -> Routing rule
   /api/*  -> backend pool: NestJS VMs/containers
   /ml/*   -> backend pool: FastAPI
   WAF policy inspects first; health probes pick healthy nodes
Needs its own dedicated subnet (e.g. /24 recommended)
```

---

## 💻 Code / Config Example
```bash
az network vnet subnet create -g rg-demo --vnet-name vnet-prod \
  -n appgw-subnet --address-prefixes 10.0.10.0/24
az network public-ip create -g rg-demo -n agw-pip --sku Standard

az network application-gateway create -g rg-demo -n agw-web \
  --sku Standard_v2 --capacity 2 \
  --vnet-name vnet-prod --subnet appgw-subnet \
  --public-ip-address agw-pip \
  --frontend-port 80 --http-settings-port 3000 --http-settings-protocol Http \
  --servers 10.0.2.4 10.0.2.5
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| L7 LB | ALB | Application Gateway v2 |
| WAF | AWS WAF (separate) | WAF on Application Gateway (WAF_v2) |
| Routing | Host/path rules | Host/path rules |
| Pricing | Hourly + LCU (approximate — check current docs) | Hourly + capacity units (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using v1 SKU or sharing the subnet with other resources.
✅ Correct: Use v2 in a dedicated subnet.

❌ Mistake: Probe path returns 404 so all backends are "unhealthy".
✅ Correct: Point a custom probe at a real `/health` endpoint.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Application Gateway vs Load Balancer? A1: App Gateway is L7 (HTTP aware), LB is L4.
Q2: [Medium] How do you route /api and /ml differently? A2: URL path map with separate backend pools and HTTP settings.
Q3: [Hard] Global multi-region web app? A3: Put Front Door in front for global routing, with an App Gateway (WAF) per region.

---

## ✅ Quick Checklist
□ v2 SKU, dedicated subnet
□ TLS cert from Key Vault
□ WAF in Prevention mode
□ Custom health probe

---

## ⚡ 1-Line Summary
App Gateway is Azure's ALB-like L7 balancer with WAF | App Gateway Azure का ALB जैसा L7 balancer है, WAF के साथ।

## ➡️ Next: 211. Azure Front Door (CDN + LB)

---
