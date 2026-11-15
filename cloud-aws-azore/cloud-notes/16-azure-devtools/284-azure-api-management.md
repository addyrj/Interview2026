# 284. Azure API Management
# AWS: Amazon API Gateway
# Azure: Azure API Management (APIM)
# हिंदी में: Azure API Management (API गेटवे)

---

## 🔵 Simple Definition
APIM is a gateway in front of your backends that adds auth, rate limits, caching, transformation, versioning and a developer portal.
हिंदी: APIM आपके बैकएंड के सामने गेटवे है जो ऑथ, रेट लिमिट, कैशिंग और वर्जनिंग देता है।

---

## 🔴 Why it Exists
Cross-cutting concerns (auth, throttling, logging) should not be rewritten in each service.
APIM centralizes them and publishes APIs consistently to consumers.

---

## 🟢 How it Works
```
Client --subscription key / JWT--> APIM gateway
   inbound policies : validate-jwt, rate-limit, rewrite
   backend          : NestJS / FastAPI on App Service, AKS, VPS
   outbound policies: set-header, cache, mask data
```

---

## 💻 Code / Config Example
```xml
<!-- APIM policy (applies to an API or operation) -->
<policies>
  <inbound>
    <base />
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
      <openid-config url="https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration" />
      <audiences><audience>api://my-api</audience></audiences>
    </validate-jwt>
    <rate-limit calls="100" renewal-period="60" />
    <set-backend-service base-url="https://my-api.azurewebsites.net" />
  </inbound>
  <backend><base /></backend>
  <outbound><base /></outbound>
  <on-error><base /></on-error>
</policies>
```
```bash
az apim create -n my-apim -g rg-demo -l centralindia \
  --publisher-email you@example.com --publisher-name Me --sku-name Consumption
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | API Gateway (REST/HTTP/WebSocket) | API Management |
| Policies | Usage plans, authorizers, mapping templates | XML policy engine |
| Dev portal | Limited | Built-in |
| Tiers | Pay per request | Consumption, Developer, Standard, Premium (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving the backend publicly reachable, bypassing APIM.
✅ Correct: Restrict the backend to APIM IPs, VNet or require a shared header/JWT.

❌ Mistake: Using subscription keys as the only auth.
✅ Correct: Combine with validate-jwt (OAuth2).

---

## ⚫ Interview Q&A
Q1: [Easy] Why use APIM?
A1: Central auth, throttling, caching, versioning for APIs.

Q2: [Medium] Subscription key vs JWT?
A2: Key identifies a consumer/product for quota; JWT proves user/app identity. Use both.

Q3: [Hard] How to expose a private backend through APIM?
A3: Deploy APIM in VNet (internal/external mode, Developer or Premium tier) or use private endpoints so the backend has no public access.

---

## ✅ Quick Checklist
□ validate-jwt in inbound
□ Rate limits per product
□ Backend locked to APIM

---

## ⚡ 1-Line Summary
APIM = managed API gateway with policies and a portal. | APIM = पॉलिसी और पोर्टल वाला मैनेज्ड API गेटवे।

## ➡️ Next: 285. Azure Application Insights for Node.js
