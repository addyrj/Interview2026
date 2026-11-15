# 189. Azure Policy
# AWS: AWS Config rules + SCPs
# Azure: Azure Policy
# हिंदी में: ऐसे नियम जो तय करते हैं कि कौन-से रिसोर्स बन सकते हैं और कैसे

---

## 🔵 Simple Definition
Azure Policy evaluates resources against rules (definitions) and can audit, deny, modify or auto-deploy.
Policy रिसोर्स को नियमों से जाँचती है और audit, deny या ठीक (modify) कर सकती है।

---

## 🔴 Why it Exists
RBAC says who can act; Policy says what is allowed (regions, SKUs, tags, HTTPS only).

---

## 🟢 How it Works
```
Policy definition (rule + effect)  -> grouped in Initiative
   -> Assignment at scope (MG/sub/RG) -> evaluated on create/update + periodically
Effects: Audit, Deny, Modify, Append, DeployIfNotExists, Disabled
Non-compliant existing resources -> Remediation task
```

---

## 💻 Code / Config Example
```json
{
  "properties": {
    "displayName": "Allowed locations",
    "mode": "Indexed",
    "parameters": {
      "listOfAllowed": { "type": "Array" }
    },
    "policyRule": {
      "if": {
        "not": { "field": "location", "in": "[parameters('listOfAllowed')]" }
      },
      "then": { "effect": "deny" }
    }
  }
}
```
```bash
az policy definition create --name allowed-locations \
  --rules policy-rule.json --params policy-params.json --mode Indexed
az policy assignment create --name allowed-loc \
  --policy allowed-locations --scope /subscriptions/<sub-id> \
  --params '{"listOfAllowed":{"value":["centralindia","southindia"]}}'
```
(Use a file with the `policyRule` content alone for `--rules`.)

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Preventive | SCP, IAM boundaries | Policy Deny |
| Detective | Config rules | Policy Audit |
| Auto-fix | Config remediation (SSM) | Modify / DeployIfNotExists |
| Pricing | Config charged per item | Policy free |

---

## ⚠️ Common Mistakes
❌ Mistake: Starting with Deny in prod.
✅ Correct: Start with Audit, review, then Deny.

❌ Mistake: Expecting Deny to fix existing resources.
✅ Correct: Run remediation; Deny affects only new/updated.

---

## ⚫ Interview Q&A
Q1: [Easy] Policy vs RBAC?
A1: Policy controls resource properties; RBAC controls user actions.

Q2: [Medium] What is an initiative?
A2: A group of policy definitions assigned together.

Q3: [Hard] Auto-enable diagnostic settings on every new App Service?
A3: A DeployIfNotExists policy with a managed identity that has needed roles, plus a remediation task for existing ones.

---

## ✅ Quick Checklist
□ Audit first, then Deny
□ Assigned at management group
□ Remediation scheduled

---

## ⚡ 1-Line Summary
Policy enforces guardrails on resource configuration. | Policy = रिसोर्स कॉन्फ़िगरेशन पर नियम लागू करने वाली गार्डरेल।

## ➡️ Next: Azure Blueprints
