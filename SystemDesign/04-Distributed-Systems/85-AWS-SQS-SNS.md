# 85. AWS SQS + SNS
# हिंदी में: SQS — AWS की पूरी तरह managed message queue (काम बाँटने के लिए); SNS — AWS की pub/sub सेवा (एक message कई जगह भेजने के लिए); दोनों मिलकर fan-out बनाते हैं

---

## 🔵 Simple Definition (English)
- **Amazon SQS (Simple Queue Service):** a fully managed **message queue**. Producers send messages; consumers **poll**, process and **delete** them. No servers to manage, practically unlimited scale. Two types: **Standard** (at-least-once, best-effort order, nearly unlimited throughput) and **FIFO** (exactly-once processing within a deduplication window, strict order per message group).
- **Amazon SNS (Simple Notification Service):** a managed **pub/sub** service. Publishers send to a **topic**; SNS **pushes** copies to all **subscribers**: SQS queues, Lambda, HTTP endpoints, email, SMS, mobile push.
- **SNS → SQS fan-out:** publish once, and each service gets its own durable queue.

## 🔵 सरल परिभाषा (Hindi)
SQS AWS की managed queue है — message डालो, worker उठाकर काम करे और delete करे; कोई सर्वर नहीं संभालना। Standard (बहुत तेज़, कभी-कभी duplicate) और FIFO (क्रम पक्का)।
SNS pub/sub है — एक topic पर message डालो, वो सारे subscribers (SQS queues, Lambda, SMS, email, push) को पहुँच जाता है। SNS + SQS = fan-out।

---

## 🔴 Problem it Solves
Running RabbitMQ or Kafka yourself means clusters, upgrades, disk alarms, replication and on-call. Many teams just need:
- **Reliable background jobs** (emails, invoices, image processing) → SQS.
- **One event, many independent consumers** (order placed → notify, analytics, loyalty) → SNS + SQS.
- **Serverless pipelines** (S3 upload → process → notify) → SQS/SNS + Lambda.
- **Mobile push / SMS** at scale → SNS.

SQS/SNS give **zero-ops, highly available (multi-AZ), pay-per-use** messaging.

## 🔴 यह क्यों बना? (Hindi)
RabbitMQ/Kafka ख़ुद चलाना मतलब clusters, upgrades, disk alarms, on-call। ज़्यादातर टीमों को बस भरोसेमंद background jobs और "एक event, कई consumers" चाहिए।
SQS/SNS बिना सर्वर संभाले, कई AZ में सुरक्षित, इस्तेमाल के हिसाब से पैसे वाली messaging देते हैं।

---

## 🟢 How it Works — Step by Step

### SQS lifecycle

```
Producer ── SendMessage ──► [ SQS queue ]  (stored redundantly across AZs, retained 4 days default, up to 14)
                                 │
Consumer ── ReceiveMessage (long poll up to 20s, batch up to 10) ──► gets message + ReceiptHandle
                                 │   message becomes INVISIBLE for VisibilityTimeout (e.g. 60s)
            process ✓ → DeleteMessage(ReceiptHandle)  → gone
            crash ✗   → visibility timeout expires → message VISIBLE again → redelivered
            fails N times (maxReceiveCount) → moved to DEAD-LETTER QUEUE
```

### Standard vs FIFO

```
┌──────────────────────┬───────────────────────────────┬────────────────────────────────────┐
│                      │ Standard                      │ FIFO                               │
├──────────────────────┼───────────────────────────────┼────────────────────────────────────┤
│ Delivery             │ At-least-once (dups possible) │ Exactly-once processing (5-min     │
│                      │                               │ dedup window via dedup ID)         │
│ Ordering             │ Best-effort                   │ Strict within MessageGroupId       │
│ Throughput           │ Nearly unlimited              │ 300 msg/s per API action (3,000    │
│                      │                               │ with batching; higher in high-     │
│                      │                               │ throughput mode)                   │
│ Name                 │ any                           │ must end with .fifo                │
│ Use                  │ jobs, emails, image processing│ order state changes per order,     │
│                      │                               │ financial events per account       │
└──────────────────────┴───────────────────────────────┴────────────────────────────────────┘
FIFO trick: MessageGroupId = orderId → ordered per order, parallel across orders.
```

### SNS → SQS fan-out (the classic pattern)

```
                              ┌──► SQS: notification-queue ──► Notification worker
Order Svc ── Publish ──► SNS ─┼──► SQS: analytics-queue    ──► Analytics Lambda
            "order.placed"    ├──► SQS: loyalty-queue      ──► Loyalty worker
            topic             └──► Lambda (direct)          ──► Slack alert for big orders
Each consumer: own queue → own pace, own retries, own DLQ; one failing consumer doesn't affect others.
Subscription FILTER POLICIES: loyalty-queue only receives messages where attribute total > 1000.
(Also: EventBridge — event bus with richer routing rules, schema registry, SaaS integrations.)
```

### Lambda integration
```
SQS → Lambda event source mapping: Lambda polls for you, batches (up to 10,000), scales concurrency,
deletes on success; partial batch failure reporting → only failed messages retried.
SNS → Lambda: push invocation (async, with retries + on-failure destination/DLQ).
```

### Important settings
```
VisibilityTimeout   > max processing time (≈ 6× avg for Lambda)  — else duplicate processing
ReceiveMessageWaitTimeSeconds = 20 → long polling (fewer empty receives, cheaper)
MessageRetentionPeriod: 4 days default (1 min – 14 days)
DelaySeconds (0–900s) per queue/message → delayed jobs (≤ 15 min)
Max message size 256 KB → larger payloads: store in S3, send pointer ("claim check" pattern)
Redrive policy: maxReceiveCount=5 → DLQ; DLQ redrive back to source after fixing bug
Encryption (SSE-SQS/KMS), access via IAM policies, VPC endpoints
```

### SQS vs SNS vs Kafka vs EventBridge
```
SQS         → queue (pull), one consumer group per queue, jobs
SNS         → pub/sub (push), fan-out to many endpoints, no retention
SNS+SQS     → durable fan-out
EventBridge → event bus with content-based routing rules, archives/replay, SaaS/AWS events
Kinesis/MSK → streaming with retention & replay, ordered shards/partitions, high throughput analytics
```

## 🟢 कैसे काम करता है? (Hindi)
1. Producer SQS में message भेजता है; consumer long-polling से उठाता है — message कुछ समय (visibility timeout) के लिए छिप जाता है।
2. काम पूरा → DeleteMessage; crash हुआ → timeout के बाद message फिर दिखेगा; कई बार फ़ेल → DLQ।
3. Standard = तेज़, duplicate संभव; FIFO = क्रम पक्का (MessageGroupId जैसे orderId के हिसाब से)।
4. SNS topic पर publish → सारे subscribers (हर service की अपनी SQS queue, Lambda, SMS, push) को copy।
5. Visibility timeout प्रोसेसिंग समय से ज़्यादा रखो, 256 KB से बड़ा डेटा S3 में रखकर सिर्फ़ pointer भेजो, consumers idempotent रखो।

---

## 🟡 Real World Example

**Amazon.com** — SQS was one of the first AWS services (2004/2006), born from Amazon's need to decouple retail services. Order pipelines still rely on queues and fan-out.

**Netflix, Airbnb, Lyft** — use SNS/SQS for decoupled event delivery between microservices and for job processing alongside Kafka.

**Indian startups on AWS (Swiggy, Meesho, Dunzo-era startups)** — common pattern: S3 upload → SQS → worker (image resize, catalog processing); order events → SNS → several SQS queues; OTP SMS via SNS (or dedicated SMS providers) with DLT-registered templates in India.

**Serverless apps** — API Gateway → Lambda writes to SQS → Lambda consumers is a popular no-server architecture that handles spiky traffic cheaply.

## 🟡 Real Example Hindi में
SQS AWS की सबसे पुरानी सेवाओं में से है — Amazon की अपनी services को अलग रखने के लिए बनी। भारतीय startups में आम pattern: S3 upload → SQS → worker (image resize); order event → SNS → कई SQS queues।
Serverless ऐप्स में API Gateway → Lambda → SQS → Lambda — बिना सर्वर के अचानक ट्रैफ़िक सस्ते में संभल जाता है।

---

## 🟠 My Stack Example

### Fan-out setup (Terraform-ish)
```hcl
resource "aws_sns_topic" "order_events" { name = "order-events" }

resource "aws_sqs_queue" "notif_dlq" { name = "notification-dlq" }
resource "aws_sqs_queue" "notif" {
  name = "notification-queue"
  visibility_timeout_seconds = 60
  receive_wait_time_seconds  = 20
  redrive_policy = jsonencode({ deadLetterTargetArn = aws_sqs_queue.notif_dlq.arn, maxReceiveCount = 5 })
}
resource "aws_sns_topic_subscription" "notif" {
  topic_arn = aws_sns_topic.order_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.notif.arn
  raw_message_delivery = true
  filter_policy = jsonencode({ eventType = ["OrderPlaced", "OrderDelivered"] })
}
# + aws_sqs_queue_policy allowing sns.amazonaws.com to SendMessage from this topic
```

### Publish (Node.js SDK v3)
```js
import { SNSClient, PublishCommand } from '@aws-sdk/client-sns';
const sns = new SNSClient({ region: 'ap-south-1' });

await sns.send(new PublishCommand({
  TopicArn: process.env.ORDER_EVENTS_TOPIC,
  Message: JSON.stringify({ eventId, orderId, userId, total }),
  MessageAttributes: { eventType: { DataType: 'String', StringValue: 'OrderPlaced' } },   // for filter policies
}));
// For strict reliability publish via outbox relay (Topic 68)
```

### Consumer as Lambda with partial batch failures (TypeScript)
```ts
import type { SQSHandler } from 'aws-lambda';
export const handler: SQSHandler = async (event) => {
  const batchItemFailures: { itemIdentifier: string }[] = [];
  for (const record of event.Records) {
    try {
      const evt = JSON.parse(record.body);
      await processIdempotently(evt);                // dedup on evt.eventId (DynamoDB conditional put)
    } catch {
      batchItemFailures.push({ itemIdentifier: record.messageId });   // only these are retried
    }
  }
  return { batchItemFailures };
};
// event source mapping: batchSize 10, functionResponseTypes: ["ReportBatchItemFailures"]
```

### FIFO queue for ordered per-order events (Python boto3)
```python
sqs.send_message(
    QueueUrl=ORDER_STATE_FIFO_URL,
    MessageBody=json.dumps({"orderId": oid, "status": "OUT_FOR_DELIVERY"}),
    MessageGroupId=str(oid),                       # order per order
    MessageDeduplicationId=f"{oid}:OUT_FOR_DELIVERY",   # exactly-once within 5 min
)
```

### Claim-check for big payloads
```js
const key = `payloads/${eventId}.json`;
await s3.send(new PutObjectCommand({ Bucket: B, Key: key, Body: JSON.stringify(bigReport) }));
await sqs.send(new SendMessageCommand({ QueueUrl: Q, MessageBody: JSON.stringify({ s3Key: key }) }));
```

### Mobile push via SNS (or FCM directly)
```
SNS Platform Applications (FCM for Android, APNs for iOS) → endpoint per device token
→ publish to endpoint or to a topic of endpoints
(Many teams call FCM/APNs directly or use Expo Push / OneSignal; see Topic M10)
```

### Local dev
```yaml
localstack:
  image: localstack/localstack
  ports: ["4566:4566"]
  environment: { SERVICES: "sqs,sns,s3" }
# SDK endpoint: http://localhost:4566
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between SQS and SNS?**
A1: SQS is a pull-based message queue: messages are stored until a consumer receives and deletes them, which suits work distribution, buffering and retries. SNS is push-based pub/sub: a message published to a topic is immediately pushed to all subscribers (SQS, Lambda, HTTP, email, SMS, mobile push) with no long-term storage. Combined (SNS → multiple SQS queues), you get durable fan-out where each consumer processes at its own pace.

**Q2: SQS Standard vs FIFO — when to use each?**
A2: Standard: nearly unlimited throughput, at-least-once delivery (occasional duplicates) and best-effort ordering. Good for most background jobs with idempotent consumers. FIFO: strict ordering within a message group and exactly-once processing via deduplication IDs (5-minute window), with lower throughput limits. Use it when the order of operations per entity matters (order state transitions, account ledger events), with MessageGroupId set to the entity ID for parallelism across entities.

**Q3: What is the visibility timeout and what goes wrong if it's too short?**
A3: After a consumer receives a message, SQS hides it from other consumers for the visibility timeout. If the consumer deletes it in time, it's done. If not (crash or slowness), it reappears and is redelivered. If the timeout is shorter than processing time, another consumer receives the same message while the first is still working, causing duplicate processing. Set it above the maximum processing time (or extend it with ChangeMessageVisibility), and keep consumers idempotent.

**Q4: How do you implement fan-out of an "order placed" event to several services on AWS?**
A4: Publish to an SNS topic (ideally via an outbox relay for reliability). Subscribe one SQS queue per consuming service, with raw message delivery and filter policies so each receives only relevant event types. Each queue has its own DLQ and redrive policy, and consumers (ECS workers or Lambda with partial batch responses) process idempotently. Alternatively, use EventBridge rules for richer content-based routing and archive/replay.

**Q5: How do you handle messages larger than 256 KB?**
A5: Use the claim-check pattern: store the payload in S3 (or a DB) and send a small message with a reference (S3 key or ID). Consumers fetch the payload, and lifecycle rules clean up S3. The Amazon SQS Extended Client Library automates this for Java and Python. Also consider sending only IDs and letting consumers fetch fresh data.

---

## 🔷 Trade-offs
✅ Advantages:
- Fully managed, highly available, scales automatically, pay-per-use, deep AWS/Lambda integration.
- SNS+SQS gives simple durable fan-out with filtering.

❌ Disadvantages:
- AWS lock-in; limited features vs RabbitMQ (routing) or Kafka (retention/replay, ordering at scale).
- Standard queues duplicate/reorder; FIFO throughput limits; 256 KB message limit; max 15-min delay.
- Polling costs/latency (mitigated by long polling).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SQS | AWS managed queue | AWS की queue सेवा |
| SNS | AWS managed pub/sub | AWS की pub/sub सेवा |
| Fan-out | One message to many consumers | एक message कई जगह |
| Visibility timeout | Message hidden while processing | प्रोसेसिंग के समय छिपा |
| Long polling | Wait up to 20s for messages | messages का इंतज़ार करके लेना |
| FIFO queue | Ordered, deduplicated queue | क्रम वाली queue |
| MessageGroupId | Ordering scope in FIFO | क्रम का समूह |
| Redrive policy | Rule to move to DLQ | DLQ में भेजने का नियम |
| Filter policy | SNS subscription message filter | SNS का filter |
| Claim check | Store payload elsewhere, send reference | बड़ा डेटा S3 में, pointer भेजो |

---

## ⚡ 3-Line Summary
**English:**
1. SQS = managed pull queue (Standard: at-least-once, unlimited; FIFO: ordered per group, deduped); SNS = managed push pub/sub.
2. SNS → per-service SQS queues = durable fan-out with filters, DLQs, independent scaling; Lambda integrates natively.
3. Tune visibility timeout, use long polling, idempotent consumers, claim-check for >256 KB.

**Hindi:**
1. SQS = managed queue (Standard तेज़, FIFO क्रम वाली); SNS = managed pub/sub।
2. SNS → हर service की SQS queue = भरोसेमंद fan-out; Lambda के साथ आसानी से।
3. Visibility timeout सही रखो, long polling, idempotent consumers, बड़े डेटा के लिए S3 pointer।

---

## ➡️ Next Topic Suggestion
**86. Dead Letter Queue (DLQ)** — Every queue needs a place for messages that keep failing. Next: DLQ design, poison messages, alerting, inspection and safe redrive.
