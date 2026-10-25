# 289. Build Notification Service
# हिंदी में: Notification Service कैसे बनायें

---

## 🔵 Simple Definition (English)
A **notification service** is a backend system that sends alerts to users through multiple channels — email, SMS, push notification, in-app — triggered by events like "order placed" or "payment failed". It decouples the "what happened" from "how the user is told", usually via a queue so the main request stays fast.

## 🔵 सरल परिभाषा (Hindi)
**Notification service** एक backend system है जो users को अलग-अलग channels (email, SMS, push, in-app) पर alert भेजता है — जैसे "order placed" या "payment failed" event पर। यह "क्या हुआ" और "user को कैसे बताया जाए" को अलग करता है, आमतौर पर queue के through, ताकि main request fast रहे।

---

## 🔴 Problem it Solves
Without a dedicated service, every feature (orders, payments, chat) would directly call email/SMS APIs inline — making requests slow, duplicating retry logic, and making it impossible to let users control preferences (e.g., "don't SMS me, only push"). A notification service centralizes templates, channel selection, retries, rate-limiting and user preferences in ONE place.

## 🔴 यह क्यों बना? (Hindi)
Dedicated service के बिना हर feature (orders, payments, chat) को email/SMS API सीधे call करना पड़ता — request slow होती, retry logic बार-बार लिखना पड़ता, और user preferences ("सिर्फ push चाहिए, SMS नहीं") control करना मुश्किल होता। Notification service templates, channel selection, retries, rate-limiting, preferences — सब एक जगह centralize करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Business event occurs (order placed) → app publishes a "notification request" to a queue (Redis/BullMQ, RabbitMQ, Kafka) instead of calling providers directly.
Step 2 → Notification worker consumes the queue job, loads user's channel preferences + template.
Step 3 → Worker renders template (fills in variables like name, order id) per channel.
Step 4 → Worker calls the right provider adapter (email via Nodemailer/SES, SMS via Twilio, push via FCM).
Step 5 → On failure, job retries with backoff; on exhausted retries it's moved to a dead-letter queue and logged.
Step 6 → Delivery status stored (sent/failed) for audit and analytics.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Business event होता है (order placed) → app सीधे provider call नहीं करता, बल्कि queue (Redis/BullMQ, RabbitMQ, Kafka) में "notification request" publish करता है।
Step 2 → Worker queue से job उठाता है, user की channel preferences + template load करता है।
Step 3 → हर channel के लिए template render होता है (name, order id जैसी variables fill होती हैं)।
Step 4 → Worker सही provider adapter call करता है (email = Nodemailer/SES, SMS = Twilio, push = FCM)।
Step 5 → Failure पर retry backoff के साथ होता है; retries खत्म होने पर job dead-letter queue में जाता है और log होता है।
Step 6 → Delivery status (sent/failed) audit और analytics के लिए store होता है।

---

## 🟡 Real World Example
**Swiggy** sends: order confirmation (push + SMS), delivery partner assigned (push), order delivered (push + email receipt). Internally, the order service never calls Twilio or FCM directly — it just emits `order.placed` to a queue. A separate `notification-service` microservice owns all provider integrations, user preferences ("muted promotional SMS"), and retry/rate-limit logic, so order service stays decoupled and fast.

## 🟡 Real Example Hindi mein
**Swiggy**: order confirm (push + SMS), delivery partner assign (push), order delivered (push + email receipt) भेजता है। Order service कभी Twilio/FCM को directly call नहीं करता — सिर्फ `order.placed` event queue में डालता है। एक अलग `notification-service` सभी provider integrations, user preferences, retry/rate-limit संभालता है, जिससे order service fast और decoupled रहता है।

---

## 💻 Code Example — Basic

```javascript
// notification-basic.js
// Minimal in-memory notification dispatcher (no external deps, runs with `node notification-basic.js`)

const EventEmitter = require('events');

// Central event bus — business logic emits events here
const bus = new EventEmitter();

// Simple "channel" functions — in real life these call Nodemailer/Twilio/FCM
function sendEmail(to, subject, body) {
  console.log(`[EMAIL] to=${to} subject="${subject}" body="${body}"`);
}

function sendSms(to, body) {
  console.log(`[SMS] to=${to} body="${body}"`);
}

function sendPush(userId, title, body) {
  console.log(`[PUSH] user=${userId} title="${title}" body="${body}"`);
}

// User preferences — which channels each user allows
const preferences = {
  u1: { email: true, sms: false, push: true },
};

// Notification "template" — turns event data into messages per channel
function renderTemplate(eventName, data) {
  if (eventName === 'order.placed') {
    return {
      subject: `Order #${data.orderId} confirmed`,
      body: `Hi ${data.name}, your order #${data.orderId} has been placed!`,
    };
  }
  return { subject: 'Notification', body: 'You have a new update.' };
}

// The notification dispatcher — listens to business events
bus.on('order.placed', (data) => {
  const prefs = preferences[data.userId] || { email: true, sms: true, push: true };
  const { subject, body } = renderTemplate('order.placed', data);

  if (prefs.email) sendEmail(data.email, subject, body);
  if (prefs.sms) sendSms(data.phone, body);
  if (prefs.push) sendPush(data.userId, subject, body);
});

// Simulate the order service emitting an event (it never calls providers directly!)
bus.emit('order.placed', {
  userId: 'u1',
  name: 'Rahul',
  orderId: 'ORD123',
  email: 'rahul@example.com',
  phone: '+919999999999',
});
```

## 💻 Code Example — Advanced

```javascript
// notification-advanced.js
// Production-style notification service using BullMQ (Redis-backed queue) with retries.
// npm i bullmq ioredis
const { Queue, Worker } = require('bullmq');

const connection = { host: '127.0.0.1', port: 6379 };

// Queue that business services push jobs to
const notificationQueue = new Queue('notifications', { connection });

// Provider adapters — pluggable, each throws on failure so BullMQ can retry
const providers = {
  async email({ to, subject, body }) {
    // Simulate flaky network — 20% failure to demonstrate retries
    if (Math.random() < 0.2) throw new Error('SMTP timeout');
    console.log(`[EMAIL SENT] ${to} - ${subject}`);
  },
  async sms({ to, body }) {
    if (Math.random() < 0.2) throw new Error('Twilio 5xx');
    console.log(`[SMS SENT] ${to} - ${body}`);
  },
  async push({ userId, title, body }) {
    console.log(`[PUSH SENT] ${userId} - ${title}`);
  },
};

// Helper for business services (order-service, payment-service) to call
async function notify(channel, payload) {
  // 'notify' job name, payload includes channel + data
  // attempts: retry up to 3 times with exponential backoff
  await notificationQueue.add('notify', { channel, payload }, {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 },
    removeOnComplete: 1000,   // keep queue clean
    removeOnFail: false,      // keep failed jobs for debugging / dead-letter inspection
  });
}

// Worker process — runs separately in production (own process/container)
const worker = new Worker('notifications', async (job) => {
  const { channel, payload } = job.data;
  const send = providers[channel];
  if (!send) throw new Error(`Unknown channel: ${channel}`);
  await send(payload);
  return { status: 'sent', channel };
}, { connection, concurrency: 5 });

worker.on('completed', (job) => console.log(`Job ${job.id} delivered`));
worker.on('failed', (job, err) => {
  console.error(`Job ${job.id} failed (attempt ${job.attemptsMade}): ${err.message}`);
  // On final failure: log to DB, alert on-call, or move to dead-letter table
});

// Example usage — order service calls this after placing an order
async function main() {
  await notify('email', { to: 'rahul@example.com', subject: 'Order Confirmed', body: 'Thanks for ordering!' });
  await notify('sms', { to: '+919999999999', body: 'Your order ORD123 is confirmed.' });
  await notify('push', { userId: 'u1', title: 'Order Confirmed', body: 'ORD123 placed' });
}

main().catch(console.error);

module.exports = { notify, notificationQueue };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express endpoint that triggers notifications via the queue (non-blocking)
const express = require('express');
const { notify } = require('./notification-advanced');

const app = express();
app.use(express.json());

app.post('/orders', async (req, res) => {
  const { userId, name, email, phone } = req.body;
  const orderId = 'ORD' + Date.now();

  // 1. Save order to DB (fast, critical path)
  // await db.orders.create({ orderId, userId, ... });

  // 2. Fire-and-forget notification — DO NOT await the delivery, only the enqueue
  await notify('email', { to: email, subject: `Order ${orderId} confirmed`, body: `Hi ${name}!` });
  await notify('sms', { to: phone, body: `Order ${orderId} confirmed` });

  // 3. Respond immediately — user doesn't wait for SMS/email to actually send
  res.status(201).json({ orderId, status: 'placed' });
});

app.listen(3000, () => console.log('Order API on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling email/SMS providers synchronously inside the request handler
✅ Correct: Enqueue a job and respond immediately; let a worker handle delivery asynchronously

```javascript
// Wrong — request waits for slow 3rd-party API, can time out
app.post('/orders', async (req, res) => {
  await sendEmailViaSES(req.body.email); // blocks response on external API
  res.json({ ok: true });
});

// Right — enqueue and respond fast
app.post('/orders', async (req, res) => {
  await notificationQueue.add('notify', { channel: 'email', payload: req.body });
  res.json({ ok: true });
});
```

❌ Mistake 2: No retry/backoff — one provider hiccup means notification is lost forever
✅ Correct: Use queue-level retries with exponential backoff and a dead-letter path

```javascript
// Wrong
try { await sendSms(data); } catch (e) { console.log('failed, oh well'); }

// Right
await queue.add('sms', data, { attempts: 5, backoff: { type: 'exponential', delay: 1000 } });
```

---

## 🧠 Tricky Interview Question

```javascript
const { EventEmitter } = require('events');
const bus = new EventEmitter();

bus.on('notify', async (data) => {
  throw new Error('boom'); // thrown inside an async listener
});

bus.emit('notify', {});
console.log('after emit');
```
Answer: `"after emit"` prints, then the process crashes with an **unhandled promise rejection** (or `uncaughtException` depending on Node version/flags). `EventEmitter.emit` is synchronous and does NOT await async listeners — it just calls them and moves on. Since the listener is `async`, the thrown error becomes a rejected Promise that nobody `.catch()`es, which Node treats as an unhandled rejection. This is why production notification workers never throw inside raw EventEmitter listeners directly — they wrap handlers in try/catch or use a queue library (BullMQ) that properly awaits and catches job processor errors.

---

## ⚫ Interview Questions + Answers

Q1: Why use a queue instead of calling providers directly from the request?
A1: Queues decouple the fast "business write" path from slow third-party API calls, enable automatic retries with backoff, provide back-pressure control (don't overload Twilio/SES), and let you scale notification workers independently from the API servers.

Q2: How do you handle a user who wants to turn off SMS but keep email?
A2: Store per-user, per-channel preferences in a DB table (userId, channel, enabled). The notification worker checks preferences before sending each channel, skipping disabled ones. Also respect legal opt-outs (e.g., TRAI DND regulations in India) by checking a separate consent flag.

Q3: How do you prevent duplicate notifications if a job is retried?
A3: Use idempotency keys — before sending, check (and set) a "notification_sent:{jobId}" flag in Redis with a TTL. If already sent, skip. Also design provider calls to be idempotent where the provider supports a client-generated message ID.

Q4: How would you template multi-language notifications?
A4: Store templates keyed by `(templateName, locale)` in DB or files, resolve locale from user profile, and use a templating engine (Handlebars/EJS) to interpolate variables. Fallback to a default locale ('en') if a translation is missing.

Q5: How do you monitor notification delivery health?
A5: Track metrics per channel/provider: sent count, failure count, latency, bounce/delivery webhooks from provider (SES bounce, Twilio delivery status callback). Alert when failure rate crosses a threshold; store delivery logs for audit/support queries.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple features need to notify users across channels
- You need retries, rate limiting, templates, and preference management centrally
- Notification volume is high enough that async processing matters

❌ Avoid when:
- It's a tiny app with one notification type — a direct function call is simpler
- You have zero tolerance for any delay (truly synchronous confirmation screens), though even then the actual send should still be async

---

## 📊 Visual Diagram
```
 Order Service          Queue (Redis/BullMQ)        Notification Worker
 ┌──────────────┐        ┌─────────────────┐        ┌───────────────────┐
 │ order placed │──push──▶  notify job      │──pull──▶ load prefs+template│
 └──────────────┘        └─────────────────┘        │ pick channel(s)    │
                                                      │ call provider API │
                                                      └─────────┬─────────┘
                                                                │
                                      ┌─────────────────────────┼─────────────────────┐
                                      ▼                         ▼                     ▼
                                  Email (SES)               SMS (Twilio)         Push (FCM)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Channel | Delivery medium (email/SMS/push) | भेजने का माध्यम |
| Queue | Buffer between producer and worker | Producer-worker के बीच buffer |
| Backoff | Increasing delay between retries | Retry के बीच बढ़ता delay |
| Dead-letter queue | Place for permanently failed jobs | हमेशा के लिए fail jobs की जगह |
| Idempotency | Same operation repeated = same result | बार-बार करने पर same result |
| Template | Reusable message format with variables | Variables वाला reusable format |

---

## ⚡ 3-Line Summary
English: A notification service decouples "event happened" from "how user is told" using a queue + worker + provider adapters. It centralizes templates, preferences, retries, and delivery tracking. Build it async-first so business APIs stay fast and notifications remain reliable even when a provider is slow or down.
Hindi: Notification service queue + worker + provider adapters से "event" और "user को बताना" अलग करता है। Templates, preferences, retries, delivery tracking सब centralize होता है। हमेशा async design रखो ताकि APIs fast रहें और provider down होने पर भी notifications reliable रहें।

---

## ➡️ Next Topic
**290. Build URL Shortener API** — hashing/encoding strategies, collision handling, and redirect performance.
