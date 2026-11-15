# 182. Azure Active Directory (AAD)
# AWS: IAM + IAM Identity Center + Cognito (closest mix)
# Azure: Microsoft Entra ID (formerly Azure Active Directory)
# हिंदी में: Azure की पहचान (identity) सेवा, जो users, apps और login संभालती है

---

## 🔵 Simple Definition
Entra ID (renamed from Azure AD in 2023) is Microsoft's cloud identity service: users, groups, apps, SSO and MFA for a tenant.
यह यूज़र, ग्रुप, ऐप और लॉगिन (SSO/MFA) को मैनेज करने वाली पहचान सेवा है।

---

## 🔴 Why it Exists
Every login and API call needs a trusted identity. One central directory avoids separate passwords per app and enables MFA and conditional access.

---

## 🟢 How it Works
```
User/App --login--> Entra ID tenant --issues--> OAuth2/OIDC token (JWT)
                                                   |
                    Azure Resource Manager / your API validates the token
Objects: Users, Groups, App registrations, Service principals, Managed identities
```
- App registration = definition of your app; service principal = its instance in a tenant.
- Managed identity = service principal whose secret Azure manages (no credentials in code).

---

## 💻 Code / Config Example
```bash
# Create an app registration + service principal for GitHub Actions (CLI)
az ad app create --display-name gha-deploy
az ad sp create --id "<appId>"
# Federated credential (OIDC) so GitHub needs no stored secret
az ad app federated-credential create --id <appId> --parameters '{
  "name": "gha-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:myorg/myrepo:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'
```
```yaml
# GitHub Actions: login with OIDC (needs permissions: id-token: write)
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Workforce identity | IAM Identity Center | Entra ID |
| App users (customers) | Cognito | Entra External ID (B2C legacy) |
| Machine identity | IAM role | Managed identity / service principal |
| Pricing | IAM free | Free tier; P1/P2 paid (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Storing a client secret in repo or CI variables forever.
✅ Correct: Use managed identity or OIDC federated credentials.

❌ Mistake: Confusing Entra roles (directory) with Azure RBAC roles (resources).
✅ Correct: Entra roles manage the directory; RBAC roles manage Azure resources.

---

## ⚫ Interview Q&A
Q1: [Easy] Is Azure AD the same as Entra ID?
A1: Yes, it was renamed to Microsoft Entra ID.

Q2: [Medium] App registration vs service principal?
A2: Registration is the global app definition; the service principal is its local identity in a tenant that gets permissions.

Q3: [Hard] How do you let a FastAPI container on Azure read Key Vault without secrets?
A3: Enable a managed identity on the app, grant it a Key Vault role (Key Vault Secrets User), and use DefaultAzureCredential in code.

---

## ✅ Quick Checklist
□ MFA / conditional access on admins
□ Managed identity instead of secrets
□ Groups used for access, not individual users

---

## ⚡ 1-Line Summary
Entra ID is Azure's identity backbone for users, apps and tokens. | Entra ID = Azure की पहचान और लॉगिन की रीढ़।

## ➡️ Next: Azure RBAC
