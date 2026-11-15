---

# 260. Microsoft Entra ID (AAD)
# AWS: AWS IAM Identity Center + IAM (+ Amazon Cognito for app users)
# Azure: Microsoft Entra ID (formerly Azure Active Directory)
# हिंदी में: Entra ID = यूज़र, ऐप और सर्विस की पहचान (login) और अनुमति का केंद्र

---

## 🔵 Simple Definition (2 lines)
Entra ID is Microsoft's cloud identity provider: it authenticates users, apps and workloads and issues OAuth2/OIDC tokens.
Entra ID तय करता है कि कौन लॉगिन कर सकता है और उसे कौन सा टोकन मिलेगा।

---

## 🔴 Why it Exists (2 lines)
Per-app passwords are insecure and unmanageable.
Central identity gives SSO, MFA, conditional access and one place to revoke access.

---

## 🟢 How it Works
```
Tenant (directory)
 |- Users, Groups
 |- App registrations (your API/SPA)  -> client id, redirect URIs, scopes
 |- Enterprise apps (service principals)
 |- Managed identities (no secrets, for Azure resources)
Flow (OIDC auth code + PKCE): User -> Entra login (MFA) -> id_token/access_token (JWT) -> your API validates
Azure RBAC = who can do what on resources; Entra roles = who manages the directory
Conditional Access: require MFA / compliant device / location
```

---

## 💻 Code / Config Example
```javascript
// NestJS/Express API: validate Entra JWT. npm i jose
const { createRemoteJWKSet, jwtVerify } = require("jose");
const tenant = process.env.TENANT_ID;
const jwks = createRemoteJWKSet(new URL(`https://login.microsoftonline.com/${tenant}/discovery/v2.0/keys`));

async function verify(token) {
  const { payload } = await jwtVerify(token, jwks, {
    issuer: `https://login.microsoftonline.com/${tenant}/v2.0`,
    audience: process.env.API_CLIENT_ID,
  });
  return payload; // check payload.roles / payload.scp
}
module.exports = { verify };
```
```bash
# App registration + service principal
az ad app create --display-name my-api
az ad sp create-for-rbac --name gha-deploy --role Contributor \
  --scopes /subscriptions/<sub-id>/resourceGroups/rg-demo
# Prefer GitHub OIDC federated credentials over secrets
az ad app federated-credential create --id <app-object-id> --parameters '{
  "name":"gha-main","issuer":"https://token.actions.githubusercontent.com",
  "subject":"repo:myorg/myrepo:ref:refs/heads/main","audiences":["api://AzureADTokenExchange"]}'
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Workforce identity | IAM Identity Center | Entra ID |
| Customer identity | Cognito | Entra External ID (formerly Azure AD B2C) |
| Workload identity | IAM role | Managed Identity |
| Authorisation | IAM policies | Azure RBAC + Entra roles |
| Pricing | IAM free; Cognito per MAU | Free tier; P1/P2 paid features (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using client secrets for CI/CD and apps.
✅ Correct: Use Managed Identity and GitHub OIDC federated credentials.

❌ Mistake: Not validating `aud` and `iss` of the JWT.
✅ Correct: Verify signature, issuer, audience and expiry.

❌ Mistake: Giving Owner/Contributor at subscription scope.
✅ Correct: Least privilege at resource-group scope.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] AAD renamed to?
A1: Microsoft Entra ID.

Q2: [Medium] App registration vs service principal?
A2: Registration is the global app definition; the service principal is its instance in a tenant that receives permissions.

Q3: [Hard] Secure a Node API with Entra, no secrets?
A3: SPA uses auth code + PKCE; API validates JWT via JWKS; the API reaches Azure resources through a Managed Identity; CI deploys using federated OIDC credentials.

---

## ✅ Quick Checklist
□ MFA and Conditional Access enabled
□ Managed Identity / OIDC instead of secrets
□ JWT validated (iss, aud, exp, signature)

---

## ⚡ 1-Line Summary
Entra ID is Azure's identity layer for users, apps and workloads | Entra ID यूज़र, ऐप और वर्कलोड की पहचान और लॉगिन सँभालता है।

## ➡️ Next: 261. (next topic in the list)

---
