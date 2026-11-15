---

# 262. AZURE POLICY COMPLIANCE
# AWS: AWS Config rules + Service Control Policies (SCP)
# Azure: Azure Policy (compliance dashboard)
# हिंदी में: एज़्योर पॉलिसी कम्प्लायंस

---

## 🔵 Simple Definition (2 lines)
Azure Policy evaluates resources against rules (e.g. "only allowed regions", "tags required") and shows which are compliant; it can also deny or auto-fix.
हिंदी: Azure Policy नियम लगाती है कि कौन सा रिसोर्स कैसे बन सकता है, और नियम तोड़ने वाले रिसोर्स की लिस्ट दिखाती है।

---

## 🔴 Why it Exists (2 lines)
RBAC says who can act; it does not stop a permitted user creating a public storage account in the wrong region. Policy enforces guardrails.

---

## 🟢 How it Works
```
Policy definition (rule + effect)
   -> Assignment (scope: mgmt group / subscription / RG)
      -> Evaluated on create/update + periodic scan (~24h)
         effects: Deny | Audit | Append | Modify | DeployIfNotExists | Disabled
      -> Compliance state per resource (Compliant / Non-compliant)
```

---

## 💻 Code / Config Example
```json
{
  "mode": "Indexed",
  "policyRule": {
    "if": {
      "allOf": [
        { "field": "type", "equals": "Microsoft.Storage/storageAccounts" },
        { "field": "Microsoft.Storage/storageAccounts/allowBlobPublicAccess", "equals": true }
      ]
    },
    "then": { "effect": "deny" }
  }
}
```
```bash
az policy definition create --name deny-public-blob \
  --rules policy.json --mode Indexed --display-name "Deny public blob access"
az policy assignment create --name deny-public-blob \
  --policy deny-public-blob --scope "/subscriptions/<sub-id>"
# Compliance summary
az policy state summarize --subscription "<sub-id>"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Guardrail preventing actions | SCP (Organizations) | Policy effect `deny` |
| Compliance evaluation | AWS Config rules | Azure Policy compliance |
| Auto-remediation | Config remediation (SSM) | DeployIfNotExists / Modify + remediation task |
| Pricing | Config charges per item/rule; check docs | Policy evaluation itself is free (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assigning `deny` straight to production.
✅ Correct: Start with `audit`, review compliance, then switch to `deny`.

❌ Mistake: Expecting existing resources to be fixed automatically.
✅ Correct: Run a remediation task for DeployIfNotExists/Modify policies.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Policy vs RBAC?
A1: RBAC controls who can do actions; Policy controls what resource properties are allowed.

Q2: [Medium] What is an initiative?
A2: A group of policy definitions assigned together, e.g. a regulatory baseline.

Q3: [Hard] How do you enforce tags and inherit from resource group?
A3: Use a `Modify` policy with a managed identity (needs Contributor-type role) to add/inherit tags, and a remediation task for existing resources.

---

## ✅ Quick Checklist
□ Assign at management group where possible
□ Audit first, deny later
□ Review non-compliant list weekly

---

## ⚡ 1-Line Summary
Policy = guardrails and compliance report for resources | Policy = रिसोर्स बनाने के नियम और उनकी जाँच।

## ➡️ Next: Azure Advisor

---
