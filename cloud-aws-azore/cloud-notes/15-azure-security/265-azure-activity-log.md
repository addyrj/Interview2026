---

# 265. AZURE ACTIVITY LOG
# AWS: AWS CloudTrail (management events)
# Azure: Azure Activity Log
# हिंदी में: एज़्योर एक्टिविटी लॉग

---

## 🔵 Simple Definition (2 lines)
The Activity Log is a subscription-level record of control-plane operations: who created, changed or deleted which resource, and when.
हिंदी: Activity Log बताता है कि किसने कौन सा रिसोर्स कब बनाया, बदला या डिलीट किया।

---

## 🔴 Why it Exists (2 lines)
"Who deleted the production database?" needs an audit trail. Activity Log gives it without any setup.

---

## 🟢 How it Works
```
ARM operation (portal/CLI/Terraform/pipeline)
   -> Azure Resource Manager records event (caller, operation, status, time)
   -> Activity Log (retained 90 days, free, queryable)
   -> Diagnostic setting -> Log Analytics / Storage / Event Hub (longer retention)
   -> Activity log alerts (e.g. on delete operations)
```

---

## 💻 Code / Config Example
```bash
# Last 7 days of operations in one resource group
az monitor activity-log list -g rg-prod --offset 7d \
  --query "[].{time:eventTimestamp, who:caller, op:operationName.value, status:status.value}" -o table

# Alert whenever a VM is deleted
az monitor activity-log alert create -g rg-ops -n alert-vm-delete \
  --scope /subscriptions/<sub-id> \
  --condition category=Administrative and operationName=Microsoft.Compute/virtualMachines/delete \
  --action-group ag-oncall
```
```
// KQL in Log Analytics (after exporting to a workspace)
AzureActivity
| where OperationNameValue endswith "DELETE" and ActivityStatusValue == "Success"
| project TimeGenerated, Caller, OperationNameValue, ResourceGroup
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Control-plane audit | CloudTrail event history (90 days) | Activity Log (90 days) |
| Long retention | Trail to S3 | Diagnostic setting to Log Analytics/Storage |
| Data-plane events | CloudTrail data events (paid) | Resource logs via Diagnostic Settings |
| Pricing | Management trail first copy free; check docs | Log itself free; export storage billed |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming the log keeps history forever.
✅ Correct: Export to Log Analytics or Storage for compliance retention.

❌ Mistake: Expecting it to show blob reads or SQL queries.
✅ Correct: Those are data-plane; enable resource logs via Diagnostic Settings.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] How long does Activity Log retain events?
A1: 90 days by default.

Q2: [Medium] Control plane vs data plane?
A2: Control plane = ARM operations (create VM); data plane = using the resource (read blob). Activity Log covers control plane.

Q3: [Hard] How do you build a tamper-resistant audit trail?
A3: Export to a storage account with immutable (WORM) policy and a separate Log Analytics workspace in a locked-down subscription, with RBAC and resource locks.

---

## ✅ Quick Checklist
□ Export to Log Analytics
□ Alerts on delete / role assignment changes
□ Retention meets compliance

---

## ⚡ 1-Line Summary
Activity Log = who did what to which resource | Activity Log = किसने क्या बदला, उसका रिकॉर्ड।

## ➡️ Next: Diagnostic Settings

---
