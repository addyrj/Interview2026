# 121. EventBridge + Lambda
# AWS: Amazon EventBridge + AWS Lambda
# Azure: Event Grid + Azure Functions
# हिंदी में: इवेंट आने पर नियम (rule) के हिसाब से अपने-आप Lambda चलाना

---

## 🔵 Simple Definition
EventBridge is a serverless event bus. Rules match events by pattern or schedule and route them to targets such as Lambda.
हिंदी: EventBridge एक इवेंट बस है जो नियम के हिसाब से इवेंट को Lambda जैसे टारगेट तक पहुँचाती है।

---

## 🔴 Why it Exists
Services should react to events without polling or tight coupling. Cron jobs, AWS service events and SaaS events all need one routing layer.

---

## 🟢 How it Works
```
Producer (your API / AWS service / cron schedule)
        |  PutEvents
        v
  [ Event Bus ] --rule: pattern match--> Lambda (target)
        |      \--rule: schedule -------> SQS / Step Functions
        v
   (no match = event dropped)
```

---

## 💻 Code / Config Example
```python
# put_event.py - publish a custom event (boto3)
import boto3, json
eb = boto3.client("events", region_name="ap-south-1")
resp = eb.put_events(Entries=[{
    "Source": "myapp.orders",
    "DetailType": "OrderCreated",
    "Detail": json.dumps({"orderId": "42", "amount": 999}),
    "EventBusName": "default",
}])
print(resp["FailedEntryCount"])  # 0 = success
```
```json
{
  "source": ["myapp.orders"],
  "detail-type": ["OrderCreated"],
  "detail": { "amount": [{ "numeric": [">", 500] }] }
}
```
The JSON above is the rule's event pattern. The Lambda target also needs a resource permission (`lambda:InvokeFunction` for `events.amazonaws.com`).

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Event router | EventBridge bus + rules | Event Grid topics + subscriptions |
| Compute target | Lambda | Azure Functions |
| Schedule | EventBridge Scheduler / rule cron | Timer trigger (Functions) |
| Pricing | Per million events (approximate - check current docs) | Per million operations (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Rule created but Lambda never fires because no invoke permission was granted.
✅ Correct: Add a Lambda resource policy for `events.amazonaws.com` (Terraform/CDK do this via `aws_lambda_permission`).

❌ Mistake: Assuming exactly-once delivery.
✅ Correct: Delivery is at-least-once; make the Lambda idempotent and attach a DLQ.

---

## ⚫ Interview Q&A
Q1: [Easy] What is EventBridge?
A1: A serverless event bus that routes events from producers to targets using rules.

Q2: [Medium] EventBridge vs SNS?
A2: EventBridge has content-based filtering, schema registry, SaaS sources and scheduling; SNS is simpler, higher throughput fan-out push.

Q3: [Hard] How do you handle failed Lambda invocations from a rule?
A3: Configure a retry policy (max age, attempts) and a DLQ (SQS) on the target; Lambda async errors can also use on-failure destinations. Make handlers idempotent.

---

## ✅ Quick Checklist
□ Event pattern tested with the console/`test-event-pattern`
□ Lambda permission for events.amazonaws.com
□ DLQ + idempotent handler

---

## ⚡ 1-Line Summary
EventBridge routes events by rule to Lambda | EventBridge नियम के आधार पर इवेंट को Lambda तक भेजती है।

## ➡️ Next: Kinesis - Data Streaming
