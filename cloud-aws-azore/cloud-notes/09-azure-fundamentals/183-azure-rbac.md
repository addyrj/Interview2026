# 183. Azure RBAC
# AWS: IAM policies + roles
# Azure: Azure role-based access control (RBAC)
# हिंदी में: कौन, किस रिसोर्स पर, कौन-सा काम कर सकता है - यह तय करने की व्यवस्था

---

## 🔵 Simple Definition
RBAC grants a security principal a role at a scope. Assignment = who + role + scope.
RBAC में "कौन + कौन-सा रोल + किस स्कोप पर" तय होता है।

---

## 🔴 Why it Exists
Least privilege: devs should deploy to dev but not delete prod databases. Roles bundle permissions so you do not grant them one by one.

---

## 🟢 How it Works
```
Principal (user/group/SP/managed identity)
   + Role definition (Actions / NotActions / DataActions)
   + Scope (management group > subscription > resource group > resource)
   = Role assignment (inherited downward, additive)
```
Built-ins: Owner, Contributor (no access assignment), Reader, User Access Administrator. Data-plane roles such as "Storage Blob Data Reader" are separate from management roles.

---

## 💻 Code / Config Example
```bash
# Contributor on one resource group for a CI service principal
az role assignment create \
  --assignee <sp-or-group-object-id> \
  --role "Contributor" \
  --resource-group rg-myapp-prod

# List assignments
az role assignment list --resource-group rg-myapp-prod -o table
```
```json
{
  "Name": "VM Operator",
  "IsCustom": true,
  "Description": "Start/stop/restart VMs",
  "Actions": [
    "Microsoft.Compute/virtualMachines/read",
    "Microsoft.Compute/virtualMachines/start/action",
    "Microsoft.Compute/virtualMachines/restart/action",
    "Microsoft.Compute/virtualMachines/deallocate/action"
  ],
  "NotActions": [],
  "AssignableScopes": ["/subscriptions/<subscription-id>"]
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Model | JSON policies on identities/resources | Role assignment at a scope |
| Explicit deny | Yes (policy Deny) | Deny assignments (mostly system-managed); use Policy |
| Inheritance | Via Organizations SCP ceiling | Scope hierarchy, additive |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Giving Owner at subscription scope to CI.
✅ Correct: Contributor at resource-group scope, or a custom role.

❌ Mistake: Assigning to individual users.
✅ Correct: Assign to groups.

---

## ⚫ Interview Q&A
Q1: [Easy] Contributor vs Owner?
A1: Owner can also assign roles; Contributor manages resources but cannot grant access.

Q2: [Medium] Control plane vs data plane?
A2: Control plane (Actions) manages resources; data plane (DataActions) accesses content like blobs or secrets.

Q3: [Hard] A user has Reader at subscription and Contributor at one RG. Result?
A3: Permissions are additive: Contributor in that RG, Reader elsewhere. No deny unless a deny assignment exists.

---

## ✅ Quick Checklist
□ Groups, not users
□ Narrowest scope possible
□ Review assignments periodically (Access Reviews)

---

## ⚡ 1-Line Summary
RBAC = principal + role + scope, additive and inherited. | RBAC = कौन + रोल + स्कोप, नीचे तक लागू।

## ➡️ Next: Azure CLI + PowerShell
