# 177. Azure Account + Portal
# AWS: AWS account + Management Console
# Azure: Azure account (Entra tenant + subscription) + Azure Portal
# हिंदी में: Azure account बनाना और Portal इस्तेमाल करना

---

## 🔵 Simple Definition
An Azure account is a Microsoft identity linked to a subscription; you manage resources in portal.azure.com, Cloud Shell, or the `az` CLI.
हिंदी: Azure account एक Microsoft login है जिससे subscription जुड़ी होती है, और आप Portal या az CLI से काम करते हैं।

---

## 🔴 Why it Exists
You need an identity (tenant) and a billing container (subscription) before creating anything.
The free account offers a trial credit and some always-free services (terms change: check current docs).

---

## 🟢 How it Works
```
Sign up (email + phone + card) -> Entra tenant created
 -> Free trial subscription
 -> Portal / Cloud Shell / az CLI -> Azure Resource Manager (ARM) API
Every tool calls the same ARM API
```

---

## 💻 Code / Config Example
```bash
# install: brew install azure-cli
az login                              # browser login
az account list -o table              # subscriptions
az account set --subscription "<name-or-id>"
az account show --query "{sub:name, tenant:tenantId}" -o json

# service principal for CI (prefer OIDC federated credentials, see 162 equivalent)
az ad sp create-for-rbac --name gha-deploy --role Contributor \
  --scopes /subscriptions/<sub-id>/resourceGroups/rg-demo
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Console | Management Console | Azure Portal |
| Browser shell | CloudShell | Cloud Shell |
| CLI | `aws` | `az` |
| Root user | Root account email | Account owner / Global Administrator |
| Free tier | 12-month and always-free (approximate — check current docs) | Trial credit + free services (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Daily work as Owner/Global Admin without MFA.
✅ Correct: Enable MFA, use least-privilege RBAC roles.

❌ Mistake: Forgetting to set a budget; trial credit expires into pay-as-you-go.
✅ Correct: Create a Cost Management budget alert immediately.

---

## ⚫ Interview Q&A
Q1: [Easy] What is Cloud Shell?
A1: Browser-based shell with az CLI and PowerShell, preauthenticated.

Q2: [Medium] Tenant vs subscription?
A2: Tenant = identity directory (Entra ID); subscription = billing/resource scope trusting one tenant.

Q3: [Hard] How do CI pipelines authenticate securely?
A3: Federated credential (OIDC) on an app registration with a scoped RBAC role, avoiding client secrets.

---

## ✅ Quick Checklist
□ MFA on
□ Budget alert set
□ `az login` works and subscription selected

---

## ⚡ 1-Line Summary
Account gives tenant + subscription, managed via Portal or az | Account से tenant और subscription मिलते हैं, जिन्हें Portal या az से चलाते हैं।

## ➡️ Next: 178. Azure Regions + AZs
