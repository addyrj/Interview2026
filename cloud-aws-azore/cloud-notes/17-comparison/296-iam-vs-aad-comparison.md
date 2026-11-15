# 296. IAM vs AAD Comparison
# AWS: IAM (users, roles, policies), IAM Identity Center, Cognito
# Azure: Microsoft Entra ID (formerly Azure AD) + Azure RBAC, External ID/B2C
# हिंदी में: IAM बनाम Azure AD (Entra ID)

---

## 🔵 Simple Definition
AWS IAM is account-scoped authorization with JSON policies; Entra ID is a tenant-wide identity directory, and Azure RBAC assigns roles on scopes.
हिंदी: AWS IAM अकाउंट-स्तर की अनुमति है, Entra ID पूरे टेनेंट की पहचान डायरेक्टरी है और RBAC रोल देता है।

---

## 🔴 Why it Exists
Every API call must answer who is calling and what are they allowed to do.

---

## 🟢 How it Works
```
AWS  : Principal (user/role) + Policy (JSON allow/deny) -> Resource
Azure: Principal (user/group/SP/managed identity in Entra tenant)
       + Role definition + Scope (mgmt group > subscription > RG > resource)
```

---

## 💻 Code / Config Example
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": "arn:aws:s3:::my-app-uploads/*"
  }]
}
```
```bash
# Azure equivalent: give an identity read access to blobs at storage scope
az role assignment create --assignee <principal-id> \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<sub>/resourceGroups/rg-demo/providers/Microsoft.Storage/storageAccounts/myappuploads123
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Directory | Per account (Identity Center for SSO) | Entra tenant (shared by subscriptions) |
| Permissions | JSON policies (allow/deny) | RBAC roles at scope (+ deny assignments) |
| Workload identity | IAM role | Managed identity / service principal |
| Customer auth | Cognito | Entra External ID / B2C |
| Cross-account | AssumeRole | Cross-tenant/Lighthouse, guest users |

---

## ⚠️ Common Mistakes
❌ Mistake: Mixing Entra directory roles with Azure RBAC roles.
✅ Correct: Directory roles manage Entra; RBAC manages Azure resources.

❌ Mistake: `Action: "*"` / Owner for apps.
✅ Correct: Narrow actions and scopes.

---

## ⚫ Interview Q&A
Q1: [Easy] What was Azure AD renamed to?
A1: Microsoft Entra ID.

Q2: [Medium] IAM role equivalent?
A2: Managed identity plus an RBAC role assignment.

Q3: [Hard] Policy evaluation difference?
A3: AWS: explicit deny wins, otherwise needs an allow (plus SCP/boundary limits). Azure RBAC is additive allow at inherited scopes, with deny assignments and Azure Policy as guardrails.

---

## ✅ Quick Checklist
□ MFA for humans
□ Managed identities for apps
□ Least-privilege scope

---

## ⚡ 1-Line Summary
IAM policies vs Entra identity + RBAC on scopes. | IAM पॉलिसी बनाम Entra पहचान + स्कोप पर RBAC।

## ➡️ Next: 297. Cost Model Comparison
