---

# 248. Azure Event Grid
# AWS: Amazon EventBridge
# Azure: Azure Event Grid
# हिंदी में: Event Grid = "कुछ हुआ" वाले इवेंट को सही handler तक पहुँचाने वाला राउटर

---

## 🔵 Simple Definition (2 lines)
Event Grid is a serverless event router: sources publish events, subscriptions filter and push them to handlers.
Event Grid इवेंट को सोर्स से हैंडलर (Function, Webhook, Queue) तक push करके पहुँचाता है।

---

## 🔴 Why it Exists (2 lines)
Polling for changes wastes resources.
Reactive push events (blob created, resource changed) trigger work instantly.

---

## 🟢 How it Works
```
Source (Blob created / Resource Group / Custom topic)
   -> Event Grid Topic
        -> Event Subscription (filter: subject prefix, event type, advanced)
             -> Handler: Azure Function | Webhook | Service Bus | Event Hubs | Storage Queue
Delivery: push, at-least-once, retry with backoff, dead-letter to Blob
```

---

## 💻 Code / Config Example
```bash
# Trigger a webhook/Function when a blob is created
az eventgrid system-topic create -g rg-demo -n st-blobs -l centralindia \
  --topic-type microsoft.storage.storageaccounts \
  --source $(az storage account show -n mystorageacct123 -g rg-demo --query id -o tsv)

az eventgrid system-topic event-subscription create -g rg-demo \
  --system-topic-name st-blobs -n on-upload \
  --endpoint https://myapi.example.com/webhooks/blob \
  --included-event-types Microsoft.Storage.BlobCreated \
  --subject-begins-with /blobServices/default/containers/uploads/
```
```javascript
// Express webhook: must answer the validation handshake
app.post("/webhooks/blob", express.json(), (req, res) => {
  for (const e of req.body) {
    if (e.eventType === "Microsoft.EventGrid.SubscriptionValidationEvent")
      return res.json({ validationResponse: e.data.validationCode });
    console.log("event", e.eventType, e.subject);
  }
  res.sendStatus(200);
});
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | EventBridge | Event Grid |
| Native events | AWS service events on default bus | System topics |
| Custom events | Custom event bus | Custom topics / domains |
| Filtering | Event patterns (JSON) | Subject / type / advanced filters |
| Pricing | Per million events (approximate - check current docs) | Per million operations (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Webhook does not answer the validation handshake, so subscription fails.
✅ Correct: Return `validationResponse` (or use CloudEvents handshake).

❌ Mistake: Treating Event Grid as ordered/streaming.
✅ Correct: No ordering guarantee; use Event Hubs for streams.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Push or pull?
A1: Push to handlers (Event Grid also supports pull delivery for namespaces; basic topics push).

Q2: [Medium] Event Grid vs Service Bus?
A2: Event Grid = lightweight notifications of facts; Service Bus = commands/work with strong delivery features.

Q3: [Hard] Handling failures?
A3: Retry policy (max attempts, TTL), then dead-letter to Blob; handlers must be idempotent.

---

## ✅ Quick Checklist
□ Filters narrow events by subject/type
□ Dead-letter destination configured
□ Handler idempotent and validated

---

## ⚡ 1-Line Summary
Event Grid routes "something happened" events to handlers | Event Grid इवेंट्स को सही handler तक रूट करता है।

## ➡️ Next: 249. Event Grid vs EventBridge

---
