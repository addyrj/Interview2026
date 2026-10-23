# 86. Dead Letter Queue (DLQ)
# हिंदी में: Dead Letter Queue — वो अलग queue जहाँ बार-बार फ़ेल होने वाले messages रख दिए जाते हैं, ताकि वो मुख्य queue को रोकें नहीं और बाद में जाँचकर दोबारा भेजे जा सकें

---

## 🔵 Simple Definition (English)
A **Dead Letter Queue (DLQ)** is a separate queue where messages are moved after they **fail processing a maximum number of times** (or expire, or are rejected as invalid). It isolates **poison messages** so they don't block or slow the main queue, preserves them for **investigation**, and allows **replaying (redriving)** them after the issue is fixed.

## 🔵 सरल परिभाषा (Hindi)
DLQ एक अलग queue है जहाँ वो messages भेजे जाते हैं जो कई बार कोशिश के बाद भी फ़ेल होते रहें (या ग़लत हों/पुराने हो जाएँ)।
इससे ख़राब (poison) message मुख्य queue को जाम नहीं करता, बाद में जाँच हो सकती है, और bug ठीक होने पर उन्हें दोबारा चला सकते हैं।

---

## 🔴 Problem it Solves
Some messages **will never succeed** as-is:
- Malformed JSON, missing fields, schema mismatch from an old producer.
- Data that violates business rules (an order for a deleted restaurant).
- A bug in the consumer for a specific edge case.
- A downstream permanently rejecting the request (invalid phone number).

Without a DLQ:
- The message is **retried forever**, wasting resources and spamming logs.
- In ordered queues/partitions it **blocks everything behind it** (head-of-line blocking).
- Or it's **dropped silently**, and data is lost (a customer never gets their refund).

A DLQ gives **bounded retries + safe parking + visibility + recovery**.

## 🔴 यह क्यों बना? (Hindi)
कुछ messages कभी सफल नहीं होंगे — ग़लत JSON, ग़ायब fields, consumer में bug, या downstream का स्थायी इनकार।
बिना DLQ के ऐसा message हमेशा retry होता रहेगा, क्रम वाली queue में पीछे वाले सब अटक जाएँगे, या चुपचाप गिर जाएगा (refund कभी नहीं मिलेगा)। DLQ सीमित retry, सुरक्षित जगह, निगरानी और recovery देता है।

---

## 🟢 How it Works — Step by Step

```
                 ┌──────────── retry with backoff (attempt 1..N) ─────────┐
                 ▼                                                        │
Producer ──► [ main queue ] ──► Consumer ── success ──► ACK/delete ✅      │
                                   │                                      │
                                   └── failure ──── attempts < N ─────────┘
                                   │
                                   └── attempts == N (or invalid/expired) ──► [ DLQ ] 🅿️
                                                                               │
                                              alert 🔔  ◄──────────────────────┤
                                              inspect 🔍 (payload, error, attempts, trace id)
                                              fix bug / data 🛠
                                              redrive ↩️  ──► main queue (or discard with audit)
```

### What goes to the DLQ
```
- Exceeded max retries (maxReceiveCount / attempts)
- Validation/parsing failures (permanent → send straight to DLQ, don't retry 5 times)
- Expired messages (TTL) — if you still want to inspect them
- Messages rejected by consumer (RabbitMQ nack requeue=false → DLX)
```

### Classify errors: transient vs permanent
```
Transient (retry with backoff): timeouts, 503, DB deadlock, rate limit
Permanent (DLQ immediately):    schema invalid, 400 from downstream, business rule violation,
                                 unknown event type
→ saves time and avoids hammering downstreams with hopeless retries
```

### What to store with a dead message (make it debuggable)
```
original payload + headers, error message & stack, attempt count, first/last failure time,
consumer name/version, trace id / correlation id, source queue/topic/partition/offset
```

### DLQ by system
```
AWS SQS      → redrive policy (maxReceiveCount) → DLQ; console/API "start DLQ redrive"
SNS          → per-subscription DLQ for undeliverable messages
Lambda       → on-failure destination / DLQ for async invocations
RabbitMQ     → dead-letter exchange (x-dead-letter-exchange) on reject/expire/overflow
Kafka        → no built-in: consumer publishes failed record to "<topic>.DLT" (dead letter topic)
               often with retry topics: orders.retry.1m → orders.retry.10m → orders.DLT
BullMQ       → failed jobs set (removeOnFail: false) + UI (Bull Board) to retry
Celery       → failed task tracking; custom DLQ queue
```

### Operating DLQs (what interviewers want)
```
1. ALERT when DLQ depth > 0 (or rate > threshold) — a DLQ nobody watches = silent data loss
2. Dashboards: DLQ size, age of oldest, top error types
3. Runbook: inspect → fix → redrive (rate-limited!) → verify
4. Redrive must be SAFE: consumers idempotent; consider ordering implications
5. Retention: DLQ retention ≥ main queue (SQS max 14 days) — or archive to S3
6. Don't use DLQ as a "trash can" — every message is a bug or data issue to resolve
```

### Kafka retry-topic pattern (non-blocking retries)
```
order-events ──fail──► order-events.retry.5s ──fail──► order-events.retry.1m ──fail──► order-events.DLT
                 (consumer of each retry topic waits until message timestamp + delay)
Main partition keeps flowing (no head-of-line blocking).
⚠️ Breaks strict per-key ordering for retried messages — OK for many use cases, not for all.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Consumer फ़ेल हुआ → backoff के साथ retry; N बार फ़ेल होने पर message DLQ में।
2. स्थायी ग़लती (ग़लत format, 400, business नियम टूटा) हो तो सीधे DLQ — बेकार retry नहीं।
3. DLQ message के साथ error, कितनी कोशिश, समय, trace id भी सेव करो ताकि जाँच आसान हो।
4. DLQ में कुछ भी आए तो alert; bug ठीक करो, फिर धीरे-धीरे redrive (वापस मुख्य queue में) — consumer idempotent होना चाहिए।
5. Kafka में DLQ अपने आप नहीं होता — retry topics और `.DLT` topic बनाते हैं।

---

## 🟡 Real World Example

**Payment webhooks at fintechs** — when processing a `payment.captured` event fails (order not found due to a race, or a schema change), the event goes to a DLQ with alerting. On-call fixes the issue and redrives the events, so customers aren't left "paid but not confirmed".

**Uber's Kafka consumer platform** — Uber built "reliable reprocessing" with retry topics and dead letter queues, so a few bad messages don't block real-time pipelines, while every failure stays recoverable.

**AWS DLQ redrive (2021+)** — AWS added one-click DLQ redrive for SQS because teams constantly needed to replay messages after deploying fixes.

**E-commerce catalog ingestion** — sellers upload millions of product rows. Invalid rows go to a DLQ, which feeds an error report shown back to the seller ("row 1,203: price missing").

## 🟡 Real Example Hindi में
Fintech में `payment.captured` event प्रोसेस न हो पाए तो DLQ में जाता है और alert आता है; bug ठीक करके redrive — ताकि ग्राहक "पैसे कटे पर ऑर्डर नहीं" में न फँसे।
Uber ने retry topics + DLQ बनाए ताकि कुछ ख़राब messages real-time pipeline न रोकें। Seller की ग़लत product rows DLQ से error report बनकर seller को वापस दिखती हैं।

---

## 🟠 My Stack Example

### BullMQ — retries + "dead" handling + alert
```js
new Worker('payments-webhooks', async (job) => {
  const evt = job.data;
  const parsed = WebhookSchema.safeParse(evt);
  if (!parsed.success) throw new UnrecoverableError('INVALID_PAYLOAD');   // no retries → failed immediately
  await processPaymentEvent(parsed.data);                                   // idempotent
}, { connection, concurrency: 10 });

await queue.add('evt', payload, { attempts: 6, backoff: { type: 'exponential', delay: 5000 }, removeOnFail: false });

const events = new QueueEvents('payments-webhooks', { connection });
events.on('failed', async ({ jobId, failedReason }) => {
  const job = await queue.getJob(jobId);
  if (job && job.attemptsMade >= (job.opts.attempts ?? 1)) {
    await deadLetters.add('dead', { original: job.data, reason: failedReason, attempts: job.attemptsMade, failedAt: Date.now() });
    await alert(`DLQ: payments-webhooks job ${jobId}: ${failedReason}`);
  }
});
// Bull Board UI → inspect & retry failed jobs after a fix
```

### Kafka (kafkajs) — dead letter topic
```js
await consumer.run({ eachMessage: async ({ topic, partition, message }) => {
  try {
    await handle(JSON.parse(message.value));
  } catch (err) {
    const permanent = err instanceof ValidationError;
    const attempts = Number(message.headers?.attempts ?? 0) + 1;
    const target = permanent || attempts >= 5 ? `${topic}.DLT` : `${topic}.retry`;
    await producer.send({ topic: target, messages: [{
      key: message.key, value: message.value,
      headers: { ...message.headers, attempts: String(attempts), error: String(err.message).slice(0, 500),
                 'original-topic': topic, 'original-partition': String(partition), 'original-offset': message.offset },
    }]});
  }
  // offset commits after either success or forwarding → main partition never blocks
}});
```

### SQS DLQ + CloudWatch alarm
```hcl
resource "aws_cloudwatch_metric_alarm" "dlq_not_empty" {
  alarm_name          = "notification-dlq-not-empty"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  dimensions          = { QueueName = aws_sqs_queue.notif_dlq.name }
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  alarm_actions       = [aws_sns_topic.oncall.arn]
}
```
```bash
# after fixing the bug: redrive DLQ → source queue (rate-limited)
aws sqs start-message-move-task --source-arn <dlq-arn> --max-number-of-messages-per-second 50
```

### Python (Celery) — permanent vs transient
```python
@celery.task(bind=True, max_retries=5, acks_late=True)
def process_refund(self, payload):
    try:
        data = RefundIn.model_validate(payload)
    except ValidationError as e:
        dead_letter.delay(payload, str(e)); return            # permanent → DLQ immediately
    try:
        gateway.refund(data.payment_id, idempotency_key=data.refund_id)
    except (Timeout, ServiceUnavailable) as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 5)   # transient → retry
    except Exception as e:
        if self.request.retries >= self.max_retries: dead_letter.delay(payload, repr(e))
        raise
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a dead letter queue and why is it important?**
A1: A separate queue where messages go after exceeding retry limits or failing validation, or after expiring. It prevents poison messages from being retried forever, from blocking ordered queues or partitions, and from being silently dropped. It preserves failed messages for debugging, and enables replay once the issue is fixed, which turns hidden failures into visible, recoverable work.

**Q2: What's a poison message?**
A2: A message that consistently fails processing regardless of retries, due to malformed data, a schema mismatch, a business rule violation or a consumer bug triggered by that specific input. Without a DLQ it can loop endlessly, consume resources, and in ordered systems block all messages behind it.

**Q3: How should you handle retries before sending to a DLQ?**
A3: Classify errors. Transient errors (timeouts, 503, throttling, deadlocks) get limited retries with exponential backoff and jitter, possibly via delayed retry queues or topics to avoid blocking. Permanent errors (validation, 4xx, unknown types) go straight to the DLQ. Keep max attempts and total retry duration bounded, record the attempt count and error details, and keep processing idempotent so retries are safe.

**Q4: How do you operate DLQs in production?**
A4: Alert on any DLQ messages (or rising rates) with ownership per queue, and keep dashboards for depth, oldest age and error categories. Store rich context (payload, error, attempts, trace ID, consumer version). Have runbooks: inspect, fix code or data, then redrive at a controlled rate to idempotent consumers and verify. Set retention to cover investigation time, and archive to S3 if needed. Never treat the DLQ as a trash bin.

**Q5: Kafka doesn't have a built-in DLQ. How do you implement one?**
A5: In the consumer, catch processing failures and publish the record (with headers for error, attempts and original topic, partition and offset) to a dead letter topic (`topic.DLT`), then commit the offset so the partition continues. For transient errors, use tiered retry topics with increasing delays (`topic.retry.1m`, `topic.retry.10m`) before the DLT. Spring Kafka, Uber's framework and Confluent connectors offer this. Note that it can reorder retried messages relative to others with the same key.

---

## 🔷 Trade-offs
✅ Advantages:
- Isolates bad messages, keeps pipelines flowing, prevents silent loss, enables replay & debugging.

❌ Disadvantages:
- Needs monitoring, ownership and runbooks (or it becomes a black hole).
- Redrive can cause duplicates/order issues → idempotency required.
- Retry topics add complexity and can break per-key ordering.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DLQ | Queue for failed messages | फ़ेल messages की queue |
| Poison message | Always-failing message | हमेशा फ़ेल होने वाला message |
| maxReceiveCount | Attempts before DLQ | DLQ से पहले की कोशिशें |
| Redrive | Move DLQ messages back | DLQ से वापस भेजना |
| Transient error | Temporary failure | अस्थायी ग़लती |
| Permanent error | Will never succeed | स्थायी ग़लती |
| Retry topic | Delayed retry stream (Kafka) | देर से retry की topic |
| Dead letter topic | Kafka DLQ topic | Kafka की DLQ |
| Head-of-line blocking | One message blocks the rest | एक message से सब अटकना |

---

## ⚡ 3-Line Summary
**English:**
1. A DLQ holds messages that failed max retries or are invalid, so they don't block or vanish.
2. Retry transient errors with backoff; send permanent ones straight to DLQ; store rich error context.
3. Alert on DLQ > 0, inspect, fix, redrive safely (rate-limited, idempotent); Kafka uses retry topics + DLT.

**Hindi:**
1. DLQ में वो messages जाते हैं जो बार-बार फ़ेल हों या ग़लत हों — ताकि वो queue न रोकें और खोएँ नहीं।
2. अस्थायी ग़लती पर retry, स्थायी पर सीधे DLQ; पूरी error जानकारी सेव करो।
3. DLQ > 0 पर alert, जाँच, ठीक करो, सावधानी से redrive; Kafka में retry topics + DLT।

---

## ➡️ Next Topic Suggestion
**87. Event-Driven Architecture** — Queues, Kafka, SNS and DLQs are the building blocks. Next: the architecture style itself, with services communicating through events, event types, choreography, schema contracts and pitfalls.
