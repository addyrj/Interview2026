# 114. Notification System (Design)
# हिंदी में: Notification System — push, SMS, email, WhatsApp और in-app सूचनाएँ करोड़ों यूज़र्स तक भरोसे से, सही समय पर, उनकी पसंद के हिसाब से, बिना दोहराए भेजने वाली सेवा

---

## 🔵 Simple Definition (English)
A **notification system** is a platform service that other services call to deliver messages to users across **channels**: mobile push (**FCM/APNs**), **SMS**, **email**, **WhatsApp**, and **in-app/inbox**. It handles **templates and localization, user preferences and opt-outs, priorities (OTP vs marketing), rate limiting and quiet hours, retries and provider failover, deduplication, scheduling, delivery tracking and analytics**.

## 🔵 सरल परिभाषा (Hindi)
Notification system एक केंद्रीय सेवा है — बाक़ी services बस कहती हैं "user 42 को order delivered की सूचना भेजो", और यह सही channel (push, SMS, email, WhatsApp, in-app), सही भाषा, यूज़र की पसंद, priority (OTP पहले, marketing बाद में), retry और duplicate रोकने का ध्यान रखकर भेजती है।

---

## 🔴 Problem it Solves
Without a central system, every service integrates FCM, an SMS provider and email separately:
- Duplicated code and credentials, inconsistent templates, no global opt-out handling (legal issues: DND/TRAI, GDPR, CAN-SPAM).
- Users get **spammed** (5 notifications for one order) or receive them at 3 AM.
- **OTP SMS delayed** behind a 10M-message marketing campaign.
- No retries or failover when a provider is down; no delivery metrics.
- Traffic spikes (a campaign to 20M users) overwhelm providers and get you throttled or blocked.

## 🔴 यह क्यों बना? (Hindi)
हर service अलग से FCM/SMS/email जोड़े तो code दोहराया जाता है, opt-out/DND नियम टूटते हैं, एक order के 5 messages जाते हैं, रात 3 बजे सूचना आती है, और 1 करोड़ वाले marketing campaign के पीछे OTP अटक जाता है।
केंद्रीय notification system यह सब एक जगह, नियमों के साथ संभालता है।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional:
  - API/event: "send <template> to <user(s)> with <data>" for transactional & marketing
  - Channels: push (iOS/Android/web), SMS, email, WhatsApp, in-app inbox (+ real-time badge)
  - User preferences per category & channel, unsubscribe, quiet hours, language
  - Templates with variables & localization (English/Hindi/...), versioning
  - Priorities: critical (OTP, security) > transactional (order updates) > marketing
  - Scheduling (send at 7 PM local time), bulk campaigns (millions), dedup, delivery status & analytics
Non-functional:
  - OTP/security: p99 < 5–10 s end-to-end; transactional < 30 s; marketing: best effort
  - At-least-once delivery attempts with dedup (no double notifications)
  - Scale: 100M notifications/day, campaign bursts of 20M in an hour
  - Respect provider rate limits; HA; provider failover
```

### 2. Estimation

```
100M/day ≈ 1,150/s average; campaign bursts 20M/hour ≈ 5,500/s
Mix: push 70%, email 15%, SMS 8%, WhatsApp 5%, in-app 100% (stored)
SMS cost dominates budget → prefer push/WhatsApp; SMS mainly OTP
Storage: in-app inbox 100M/day × 500 B × 30 days ≈ 1.5 TB (Cassandra/DynamoDB, TTL)
```

### 3. Architecture

```
 Producers (order, auth, payments, marketing) ──► Notification API / events (Kafka "notify")
                                                        │
                                       ┌────────────────▼─────────────────┐
                                       │ NOTIFICATION SERVICE (orchestrator)│
                                       │ 1. validate, idempotency (dedupKey)│
                                       │ 2. load user prefs, devices, locale│
                                       │ 3. pick channels (rules/fallbacks) │
                                       │ 4. render template (lang, vars)    │
                                       │ 5. apply quiet hours / frequency   │
                                       │    caps / scheduling               │
                                       │ 6. enqueue per channel + priority  │
                                       └──┬───────┬───────┬───────┬────────┘
              priority queues per channel  ▼       ▼       ▼       ▼
                            [push-critical][push-normal][sms-otp][email][whatsapp][inbox]
                                   │           │          │         │        │       │
                                Push workers  ...     SMS workers  Email   WA      Inbox writer
                                   │                     │                          │
                         FCM / APNs / Web Push     SMS providers (A, B)     DB + WebSocket badge
                                   │                     │
                        delivery receipts / webhooks ──► Status tracker ──► analytics (ClickHouse)
                        invalid tokens ──► device registry cleanup
```

### 4. Data model

```
user_preferences(user_id, category['order_updates','offers','security'], channel, enabled, quiet_start, quiet_end, locale)
devices(id, user_id, platform['ios','android','web'], push_token, app_version, last_seen, active)
templates(id, channel, category, locale, version, subject, body)    -- "order_delivered_v3"
notifications(id, user_id, template_id, channel, dedup_key UNIQUE, status, provider, created_at, sent_at,
              delivered_at, opened_at, error)                       -- status log (or event stream)
inbox(user_id, notification_id, title, body, deep_link, read, created_at)   -- in-app feed (TTL 30–90 d)
```

### 5. Key design points

```
Priority isolation (bulkheads): separate queues + workers per priority & channel →
  a marketing blast never delays OTPs
Idempotency: producers send dedupKey (e.g. "order:9001:delivered") → unique constraint → no duplicates
Retries: transient provider errors → exponential backoff + jitter; permanent (invalid number/token) → stop
Failover: SMS provider A failing (error rate/latency) → circuit breaker → provider B
Rate limiting: per provider (their TPS), per user (frequency caps: max 3 marketing/day), per campaign
Fan-out for campaigns: segment query → batch user ids → stream through queues at controlled rate
Quiet hours & timezones: hold non-critical notifications until morning in user's timezone
Collapse/coalesce: "You have 5 new messages" instead of 5 pushes (FCM collapse_key, APNs thread-id)
Device token hygiene: remove tokens FCM marks as unregistered; one user → many devices
Tracking: sent → delivered (provider receipts) → opened/clicked (deep link with tracking id)
Compliance: unsubscribe links, DND/DLT (India SMS rules), consent records, sender IDs
```

### 6. Channel specifics (quick)

```
Push: FCM (Android + can route to APNs), APNs (iOS) — data vs notification payloads, priority high/normal,
      TTL, collapse keys; iOS needs permission; delivery is best-effort (device offline → queued by FCM)
SMS: costly; DLT-registered headers & templates in India; use for OTP/critical; delivery receipts via webhook
Email: SES/SendGrid; SPF/DKIM/DMARC for deliverability; bounce/complaint handling → suppression list
WhatsApp: Business API (Meta/BSPs like Gupshup/Twilio), pre-approved templates, opt-in required
In-app: stored inbox + real-time badge via WebSocket/SSE when online
```

## 🟢 कैसे काम करता है? (Hindi)
1. कोई service event भेजती है ("order:9001:delivered" dedup key के साथ); notification service यूज़र की पसंद, devices, भाषा देखती है।
2. Channel चुनती है (push पहले, न हो तो SMS), template भरती है (Hindi/English), quiet hours और सीमा (दिन में 3 marketing) लागू करती है।
3. हर channel और priority की अलग queue — OTP की queue कभी marketing के पीछे नहीं अटकती।
4. Workers FCM/APNs/SMS/email/WhatsApp को भेजते हैं; अस्थायी ग़लती पर retry, provider ख़राब तो दूसरा provider; ग़लत tokens हटाते हैं।
5. Delivered/opened की स्थिति ट्रैक होती है; in-app inbox DB में; भारत में SMS के DLT नियम और unsubscribe का पालन।

---

## 🟡 Real World Example

**Uber / Swiggy / Zomato** — order status changes trigger push notifications plus an in-app timeline. OTP and delivery-partner calls use SMS or voice providers with failover. Marketing pushes go through separate pipelines with frequency caps.

**LinkedIn (Air Traffic Controller)** — LinkedIn built a central system to decide **which** notifications to send, **when** and **how often**, reducing spam and improving engagement by aggregating and prioritizing.

**Netflix, Airbnb** — personalized, scheduled email and push pipelines processing hundreds of millions of messages, with experimentation and per-user send-time optimization.

**Indian banks / fintech** — transaction alerts by SMS are regulatory (RBI), so they use high-priority, dedicated SMS routes with multiple aggregators for reliability, separate from promotional routes.

## 🟡 Real Example Hindi में
Swiggy/Zomato में order का हर बदलाव push + in-app timeline बनाता है; OTP के लिए SMS कई providers के साथ; marketing अलग pipeline में, सीमा के साथ।
LinkedIn ने "Air Traffic Controller" बनाया — कौन-सी सूचना कब और कितनी बार भेजनी है, ताकि spam कम हो। बैंक लेन-देन के SMS RBI नियम के कारण अलग, तेज़ रास्ते से भेजते हैं।

---

## 🟠 My Stack Example

### Producer API (any service) — idempotent send request
```js
// order-service, after status change (via outbox ideally)
await notify.send({
  dedupKey: `order:${order.id}:delivered`,
  userId: order.userId,
  category: 'order_updates',
  template: 'order_delivered',
  data: { orderId: order.id, restaurant: order.restaurantName },
  priority: 'transactional',
  deepLink: `myapp://orders/${order.id}`,
});
```

### Notification service: orchestrate & enqueue (Node + BullMQ)
```js
const queues = {
  'push:critical': new Queue('push-critical', { connection }), 'push:normal': new Queue('push-normal', { connection }),
  'sms:otp': new Queue('sms-otp', { connection }), 'email:normal': new Queue('email', { connection }),
  'inbox': new Queue('inbox', { connection }),
};

export async function handleSend(req) {
  const inserted = await db.query(
    'INSERT INTO notifications(dedup_key, user_id, template_id, status) VALUES ($1,$2,$3,$4) ON CONFLICT (dedup_key) DO NOTHING RETURNING id',
    [req.dedupKey, req.userId, req.template, 'PENDING']);
  if (!inserted.rowCount) return { duplicate: true };                       // idempotent

  const prefs = await prefsFor(req.userId, req.category);
  const user = await userProfile(req.userId);                               // locale, timezone
  if (req.priority === 'marketing' && (inQuietHours(user) || await overFrequencyCap(req.userId))) {
    return scheduleLater(req, nextAllowedTime(user));
  }
  const channels = chooseChannels(req, prefs);                              // e.g. ['push','inbox'] fallback 'sms'
  for (const ch of channels) {
    const msg = await render(req.template, ch, user.locale, req.data);     // Hindi/English templates
    const q = queues[`${ch}:${req.priority === 'critical' ? 'critical' : 'normal'}`] ?? queues[ch];
    await q.add(ch, { notificationId: inserted.rows[0].id, userId: req.userId, msg, deepLink: req.deepLink },
                { attempts: 5, backoff: { type: 'exponential', delay: 2000 }, jobId: `${req.dedupKey}:${ch}` });
  }
}
```

### Push worker (FCM via firebase-admin) with token cleanup
```js
import { getMessaging } from 'firebase-admin/messaging';
new Worker('push-normal', async (job) => {
  const tokens = await activeDeviceTokens(job.data.userId);
  if (!tokens.length) return fallbackToSms(job.data);
  const res = await getMessaging().sendEachForMulticast({
    tokens,
    notification: { title: job.data.msg.title, body: job.data.msg.body },
    data: { deepLink: job.data.deepLink, nid: String(job.data.notificationId) },
    android: { priority: 'high', collapseKey: job.data.msg.collapseKey },
    apns: { payload: { aps: { 'thread-id': job.data.msg.threadId, sound: 'default' } } },
  });
  res.responses.forEach((r, i) => {
    if (!r.success && ['messaging/registration-token-not-registered', 'messaging/invalid-registration-token'].includes(r.error?.code))
      deactivateToken(tokens[i]);
  });
  await markSent(job.data.notificationId, 'fcm');
}, { connection, concurrency: 50, limiter: { max: 2000, duration: 1000 } });
```

### SMS worker with provider failover (circuit breakers)
```js
const providers = [breaker(msg91.send), breaker(twilio.send)];
new Worker('sms-otp', async (job) => {
  for (const p of providers) {
    if (p.opened) continue;
    try { return await p.fire(job.data.phone, job.data.msg.body); } catch {}
  }
  throw new Error('ALL_SMS_PROVIDERS_FAILED');                               // BullMQ retries with backoff
}, { connection, concurrency: 100 });
```

### FastAPI: delivery receipt webhook (provider → us)
```python
@app.post("/webhooks/sms/{provider}")
async def sms_receipt(provider: str, payload: dict):
    await db.execute("UPDATE notifications SET status=:s, delivered_at=now() WHERE provider_msg_id=:id",
                     {"s": map_status(provider, payload), "id": payload["message_id"]})
    return {"ok": True}
```

### React Native: register device token + handle taps
```ts
import messaging from '@react-native-firebase/messaging';
await messaging().requestPermission();
const token = await messaging().getToken();
await api.post('/devices', { platform: Platform.OS, pushToken: token, appVersion });
messaging().onTokenRefresh((t) => api.post('/devices', { platform: Platform.OS, pushToken: t }));
messaging().onNotificationOpenedApp((m) => { track('notif_open', m.data?.nid); navigateTo(m.data?.deepLink); });
```

---

## ⚫ Interview Questions + Answers

**Q1: Design a notification system for a large consumer app.**
A1: A central notification service exposes an API or event topic. It validates and deduplicates requests (dedup key), loads preferences, devices and locale, selects channels with fallback rules, renders localized templates, and applies quiet hours, frequency caps and scheduling. It then enqueues to per-channel, per-priority queues. Channel workers call providers (FCM, APNs, SMS, email, WhatsApp) with rate limits, retries with backoff, circuit-breaker failover between providers, and token cleanup. Delivery receipts and opens feed a status store and analytics. An in-app inbox is stored (with a TTL) and pushed live via WebSocket. Campaigns are fanned out in batches at controlled rates.

**Q2: How do you ensure OTP notifications aren't delayed by marketing campaigns?**
A2: Isolate by priority with bulkheads: separate queues, workers and even provider routes or accounts for critical messages (OTP, security alerts), with reserved capacity. Marketing goes through separate, rate-limited queues that are paused or slowed under load. Monitor per-priority latency SLOs (OTP p99 under 10 s) and alert on breaches.

**Q3: How do you avoid sending duplicate notifications?**
A3: Producers include a deterministic idempotency or dedup key (`order:9001:delivered`). The notification service records it under a unique constraint and ignores repeats. Queue job IDs are derived from the key plus channel, and workers check status before sending (at-least-once queues still redeliver). Use collapse keys or thread IDs on push to merge rapid updates on the device. Frequency caps add a further guard against spamming.

**Q4: How do you send a campaign to 20 million users without breaking things?**
A4: Precompute the segment (from a warehouse or DB) and stream user IDs in batches into a campaign queue. Throttle to provider and internal capacity, respecting per-user frequency caps, preferences, quiet hours and time zones (send at local 7 PM). Use separate workers so transactional traffic isn't affected. Monitor delivery and error rates with automatic pause on high failure, spread sends over time with jitter to avoid backend spikes from users opening the app, and track opens and clicks.

**Q5: Push notifications are "best effort". How do you make important notifications reliable?**
A5: Combine channels. Store the notification in the in-app inbox (the durable source of truth) and show it on next app open. Send push with high priority and an appropriate TTL. If there's no active device token or no delivery confirmation within a window, fall back to SMS or WhatsApp for critical messages. Track delivery receipts where available, keep device tokens fresh (refresh on app start, remove invalid ones), and use deep links with tracking IDs to confirm engagement.

---

## 🔷 Trade-offs
✅ Central service: consistent templates, prefs, compliance, retries, analytics; protects providers & users.
❌ Another critical platform service; complex rules engine; provider dependencies and costs (SMS).
✅ Async queues: scale & isolation — ❌ eventual delivery, need dedup & ordering care.
✅ Multi-provider failover: reliability — ❌ cost and integration effort.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Channel | Delivery medium (push, SMS, email) | सूचना भेजने का माध्यम |
| FCM / APNs | Google / Apple push services | Google / Apple push सेवा |
| Device token | Address of an app install for push | push के लिए device का पता |
| Template | Message format with variables | संदेश का ढाँचा |
| Dedup key | Idempotency key per notification | दोहराव रोकने वाली key |
| Priority queue | Separate queue per importance | ज़रूरत के हिसाब से अलग queue |
| Frequency cap | Max messages per user per period | एक यूज़र को अधिकतम संदेश |
| Quiet hours | No non-critical sends at night | रात में ग़ैर-ज़रूरी संदेश नहीं |
| Collapse key | Replace older push with newer | पुरानी push को नई से बदलना |
| DLT | India SMS registration framework | भारत का SMS पंजीकरण नियम |

---

## ⚡ 3-Line Summary
**English:**
1. Central notification service: API/events → dedup → preferences/devices/locale → channel selection → templates → per-channel priority queues → provider workers.
2. Isolate critical (OTP) from marketing, retry with backoff, fail over providers, rate-limit per provider & per user, honor quiet hours and opt-outs.
3. Track sent/delivered/opened, keep device tokens clean, store an in-app inbox as durable fallback, throttle campaigns.

**Hindi:**
1. केंद्रीय सेवा: event → dedup → पसंद/devices/भाषा → channel → template → हर channel की priority queue → providers।
2. OTP को marketing से अलग रखो, retry, provider failover, सीमाएँ, quiet hours और opt-out का पालन।
3. Delivered/opened ट्रैक करो, ख़राब tokens हटाओ, in-app inbox रखो, campaigns धीरे-धीरे भेजो।

---

## ➡️ Next Topic Suggestion
**115. Chat Application (WhatsApp)** — Notifications are one-way. Next: a real-time two-way messaging system with 1:1 and group chats, delivery/read receipts, presence, offline delivery, media, end-to-end encryption and massive scale.
