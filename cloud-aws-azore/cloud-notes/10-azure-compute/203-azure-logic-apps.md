---

# 203. Azure Logic Apps
# AWS: AWS Step Functions (+ EventBridge/AppFlow for integrations)
# Azure: Azure Logic Apps
# हिंदी में: बिना ज़्यादा code के workflow automation

---

## 🔵 Simple Definition (2 lines)
Logic Apps is a low-code workflow service that connects triggers and actions across 1000+ connectors.
हिंदी: Logic Apps एक low-code workflow सेवा है जो अलग-अलग apps/services को trigger और action से जोड़ती है।

---

## 🔴 Why it Exists (2 lines)
Gluing SaaS, email, queues and databases with custom code is slow and hard to maintain.
Logic Apps gives ready connectors, retries and run history out of the box.

---

## 🟢 How it Works
```
Trigger (HTTP request / Blob created / Service Bus msg / schedule)
   -> Action 1 (Condition) -> Action 2 (call API) -> Action 3 (send email/Teams)
Each run is logged with inputs/outputs; failed actions can retry.
Plans: Consumption (multi-tenant, per action) | Standard (single-tenant, built on Functions runtime)
```

---

## 💻 Code / Config Example
```json
{
  "definition": {
    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
    "contentVersion": "1.0.0.0",
    "triggers": {
      "manual": {
        "type": "Request",
        "kind": "Http",
        "inputs": { "schema": { "type": "object", "properties": { "orderId": { "type": "string" } } } }
      }
    },
    "actions": {
      "CallApi": {
        "type": "Http",
        "inputs": { "method": "GET", "uri": "https://api.example.com/orders/@{triggerBody()?['orderId']}" },
        "runAfter": {}
      },
      "Respond": {
        "type": "Response",
        "inputs": { "statusCode": 200, "body": "@body('CallApi')" },
        "runAfter": { "CallApi": ["Succeeded"] }
      }
    },
    "outputs": {}
  }
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Step Functions (state machines) | Logic Apps (workflows) |
| Style | JSON ASL, code-first | Visual designer + JSON |
| Connectors | SDK integrations, AppFlow | 1000+ managed connectors |
| Pricing | Per state transition (approximate — check current docs) | Per action execution (Consumption) or fixed (Standard) (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting heavy business logic in dozens of designer actions.
✅ Correct: Call a Function/API for logic; keep Logic Apps as orchestration.

❌ Mistake: Using Consumption plan for very high-volume polling.
✅ Correct: Prefer Standard plan or event-based triggers to control cost.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Logic Apps? A1: Low-code workflow automation with triggers, actions and connectors.
Q2: [Medium] Logic Apps vs Functions? A2: Logic Apps is declarative orchestration; Functions is code for custom logic. They are often combined.
Q3: [Hard] Consumption vs Standard? A3: Consumption is serverless multi-tenant, billed per action; Standard is single-tenant with VNet support, stateful/stateless workflows and predictable pricing.

---

## ✅ Quick Checklist
□ Use managed identity for connectors
□ Retry policy configured
□ Run history alerts set up
□ Workflow definition kept in Git (Bicep/ARM)

---

## ⚡ 1-Line Summary
Logic Apps is Azure's low-code workflow engine | Logic Apps Azure का low-code workflow engine है।

## ➡️ Next: 204. Azure Spring Apps

---
