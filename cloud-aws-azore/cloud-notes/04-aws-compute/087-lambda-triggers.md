---

# 87. Lambda Triggers
# AWS: Lambda event sources (S3, SQS, SNS, EventBridge, API Gateway, DynamoDB Streams)
# Azure: Azure Functions triggers and bindings
# हिंदी में: लैम्ब्डा ट्रिगर्स

---

## 🔵 Simple Definition (2 lines)
A trigger is the event source that invokes your Lambda: an upload, a queue message, an HTTP call or a schedule.
हिंदी: ट्रिगर वह इवेंट है जो आपके Lambda को चलाता है, जैसे फ़ाइल अपलोड, queue मैसेज या शेड्यूल।

---

## 🔴 Why it Exists (2 lines)
Instead of polling or running a server, let events push work to the code. This makes systems loosely coupled and cheap.

---

## 🟢 How it Works
```
Push (async/sync invoke):  S3, SNS, EventBridge, API Gateway, ALB
Poll  (event source mapping): SQS, Kinesis, DynamoDB Streams, Kafka
   Lambda service polls the source and invokes your function with a batch.

Sync   -> caller waits (API GW)
Async  -> Lambda queues it, retries twice on error, optional DLQ / destination
SQS    -> batch; failed batch returns to queue (use partial batch response)
```

---

## 💻 Code / Config Example
```yaml
# AWS SAM template.yaml: SQS + schedule triggers
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  Queue:
    Type: AWS::SQS::Queue
    Properties: { VisibilityTimeout: 60 }
  Worker:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: nodejs20.x
      Handler: index.handler
      Timeout: 30
      Events:
        FromQueue:
          Type: SQS
          Properties:
            Queue: !GetAtt Queue.Arn
            BatchSize: 10
            FunctionResponseTypes: [ReportBatchItemFailures]
        Nightly:
          Type: Schedule
          Properties: { Schedule: 'cron(0 2 * * ? *)' }
```
```javascript
// index.mjs : SQS handler with partial batch failure
export const handler = async (event) => {
  const failures = [];
  for (const r of event.Records ?? []) {
    try { JSON.parse(r.body); /* process */ }
    catch { failures.push({ itemIdentifier: r.messageId }); }
  }
  return { batchItemFailures: failures };
};
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Queue | SQS event source mapping | Queue/Service Bus trigger |
| Storage | S3 event notification | Blob trigger / Event Grid |
| Schedule | EventBridge Scheduler/rules | Timer trigger (NCRONTAB) |
| Pricing | Pay per invocation (approximate — check current docs) | Same model (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: SQS visibility timeout shorter than function timeout.
✅ Correct: Set visibility timeout to at least 6x the function timeout (AWS guidance).

❌ Mistake: Assuming exactly-once processing.
✅ Correct: Make handlers idempotent; delivery is at-least-once.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Name 3 Lambda triggers.
A1: API Gateway, S3, SQS (also EventBridge, SNS, DynamoDB Streams).

Q2: [Medium] Sync vs async invocation?
A2: Sync returns the result to the caller; async queues the event and Lambda retries (default 2 retries) with optional DLQ/destinations.

Q3: [Hard] How to avoid one bad SQS message failing the whole batch?
A3: Enable ReportBatchItemFailures and return the failed messageIds; add a DLQ with maxReceiveCount on the queue.

---

## ✅ Quick Checklist
□ Idempotent handler
□ DLQ configured
□ Visibility timeout and batch size set

---

## ⚡ 1-Line Summary
Triggers connect events to Lambda | ट्रिगर इवेंट को Lambda से जोड़ते हैं।

## ➡️ Next: Lambda Layers

---
