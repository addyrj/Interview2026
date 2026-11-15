---

# 97. API Gateway Auth
# AWS: IAM auth, Cognito, JWT, Lambda authorizers, API keys
# Azure: APIM validate-jwt policy, Entra ID (Azure AD), subscription keys
# हिंदी में: API गेटवे ऑथेंटिकेशन

---

## 🔵 Simple Definition (2 lines)
API Gateway can check who is calling before your backend runs: using IAM signatures, JWT tokens, Cognito or a custom Lambda authorizer.
हिंदी: API Gateway आपके बैकएंड से पहले ही जाँच लेता है कि कॉल करने वाला कौन है।

---

## 🔴 Why it Exists (2 lines)
Unauthenticated endpoints get abused. Central auth means backends stay simple and every route is protected consistently.

---

## 🟢 How it Works
```
IAM            : caller signs request (SigV4); service-to-service
Cognito / JWT  : Authorization: Bearer <JWT>; gateway validates issuer+audience+signature
Lambda authorizer: your code validates token/headers -> returns allow/deny policy (cached by TTL)
API keys       : REST only; identify clients + usage plans, NOT real security
Mutual TLS     : client certs (custom domain)
```

---

## 💻 Code / Config Example
```yaml
# HTTP API with JWT authorizer (works with Cognito, Auth0, Entra ID) : CloudFormation
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Api:
    Type: AWS::ApiGatewayV2::Api
    Properties: { Name: secure-api, ProtocolType: HTTP }
  Auth:
    Type: AWS::ApiGatewayV2::Authorizer
    Properties:
      ApiId: !Ref Api
      AuthorizerType: JWT
      Name: jwt
      IdentitySource: ["$request.header.Authorization"]
      JwtConfiguration:
        Issuer: https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_EXAMPLE
        Audience: [my-app-client-id]
```
```javascript
// Lambda authorizer (HTTP API, simple response format 2.0)
export const handler = async (event) => {
  const token = event.headers?.authorization ?? "";
  // replace with real verification (e.g. jose + JWKS)
  return { isAuthorized: token === "Bearer demo-token", context: { userId: "u1" } };
};
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| JWT validation | JWT authorizer (HTTP API) | `validate-jwt` policy |
| Identity provider | Cognito | Entra ID / B2C (External ID) |
| Custom logic | Lambda authorizer | Policy expressions / Functions |
| Keys | API keys + usage plans | Subscription keys |
| Pricing | Authorizers free; Lambda authorizer costs invokes (approximate — check current docs) | Included in tier (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Treating API keys as authentication.
✅ Correct: Keys are for metering; use JWT/IAM for identity.

❌ Mistake: Authorizer cache too long, so revoked tokens still work.
✅ Correct: Short TTL (e.g. 60-300 s) or disable caching for sensitive routes.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Name API Gateway auth options.
A1: IAM, Cognito/JWT authorizer, Lambda authorizer, API keys (REST), mTLS.

Q2: [Medium] JWT authorizer vs Lambda authorizer?
A2: JWT: built-in, no code, validates standard claims. Lambda: custom logic (DB lookups, legacy tokens) at extra latency and cost.

Q3: [Hard] Implement multi-tenant authorization.
A3: JWT carries tenant claim; authorizer or backend checks scopes/tenant per route; pass tenantId in context; enforce data isolation in the backend (never trust the client).

---

## ✅ Quick Checklist
□ Every route has an authorizer
□ Issuer and audience validated
□ Authorizer cache TTL reviewed

---

## ⚡ 1-Line Summary
Authenticate at the gateway with JWT/IAM/Lambda authorizers | Gateway पर ही JWT/IAM/Lambda से auth करें।

## ➡️ Next: ECS — Elastic Container Service

---
