---

# 249. Event Grid vs EventBridge
# AWS: Amazon EventBridge
# Azure: Azure Event Grid
# हिंदी में: दोनों इवेंट राउटर हैं, फ़र्क़ फीचर्स और schema में है

---

## 🔵 Simple Definition (2 lines)
Both route events from sources to targets by rules; EventBridge uses buses and rules, Event Grid uses topics and subscriptions.
नाम अलग हैं पर काम वही: इवेंट को filter करके सही target तक भेजना।

---

## 🔴 Why it Exists (2 lines)
Multi-cloud teams must translate terms and event shapes.
Knowing the mapping avoids rewriting event logic blindly.

---

## 🟢 How it Works
```
EventBridge: Event bus -> Rule (event pattern) -> Targets (Lambda, SQS, Step Functions...)
Event Grid : Topic -> Event subscription (filter) -> Handlers (Function, Service Bus, webhook...)
Bus ~ Topic/Domain      Rule ~ Event subscription     Target ~ Handler
Schema registry ~ CloudEvents / Event Grid schema
Scheduled rules ~ (no native cron; use Logic Apps / Functions timer)
```

---

## 💻 Code / Config Example
```bash
# AWS: rule matching S3 object created -> Lambda
aws events put-rule --name on-upload --event-pattern '{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {"bucket": {"name": ["my-bucket"]}}
}'
aws events put-targets --rule on-upload --targets "Id"="1","Arn"="arn:aws:lambda:ap-south-1:123456789012:function:handler"

# Azure: equivalent subscription (see 248)
az eventgrid system-topic event-subscription create -g rg-demo --system-topic-name st-blobs \
  -n on-upload --endpoint-type azurefunction \
  --endpoint /subscriptions/<sub-id>/resourceGroups/rg-demo/providers/Microsoft.Web/sites/myfunc/functions/handler \
  --included-event-types Microsoft.Storage.BlobCreated
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | EventBridge | Event Grid |
|---------|-------------|------------|
| Cron/scheduling | EventBridge Scheduler / rules | Not native |
| Filtering | Rich content-based patterns | Subject, type, advanced filters |
| SaaS partners | Partner event sources | Partner topics |
| Archive/replay | Built-in archive and replay | Limited (dead-letter, no general replay) |
| Pricing | Per million events (approximate - check current docs) | Per million operations (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Porting EventBridge cron rules to Event Grid directly.
✅ Correct: Use Functions timer trigger or Logic Apps recurrence.

❌ Mistake: Expecting identical event JSON.
✅ Correct: Adopt CloudEvents or map fields explicitly.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which service is EventBridge's Azure peer?
A1: Event Grid.

Q2: [Medium] Replay of past events?
A2: EventBridge archive/replay exists; Event Grid has no equivalent general replay.

Q3: [Hard] Design cross-cloud eventing?
A3: Use CloudEvents format, an HTTPS webhook bridge or queue between clouds, and idempotent handlers with retries.

---

## ✅ Quick Checklist
□ Mapped bus/rule/target to topic/subscription/handler
□ Scheduling re-implemented
□ Event schema normalised (CloudEvents)

---

## ⚡ 1-Line Summary
EventBridge and Event Grid both route events; mapping is bus=topic, rule=subscription | दोनों इवेंट रूट करते हैं, बस शब्द और फीचर अलग हैं।

## ➡️ Next: 250. Azure Notification Hubs

---
