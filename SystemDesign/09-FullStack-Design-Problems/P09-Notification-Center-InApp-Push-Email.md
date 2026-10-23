# P09. Notification Center (In-app + Push + Email) (End-to-End Design)
# हिंदी में: Notification Center — एक ही platform जो हर तरह की सूचना (order update, like, offer, OTP) सही यूज़र तक सही channel पर (ऐप के अंदर inbox, push, email, SMS, WhatsApp) सही समय पर पहुँचाए — पसंद, सीमा, भाषा और "पढ़ लिया" हर device पर एक जैसा

---

## 🔵 Simple Definition (English)
A **notification center** is the end-to-end system that turns events ("order shipped", "Asha liked your photo", "Payment failed", "50% off today") into **messages on the right channels**, and shows users an **in-app inbox** (bell icon with unread badge) synced across web and mobile:
- **Producers**: product services emit events (order-service, social-service, marketing campaigns).
- **Notification service**:
  - templating and **i18n**, user **preferences** and **consent**
  - **channel routing** (in-app, push, email, SMS, WhatsApp), **priority** and **frequency caps**
  - **quiet hours**, dedupe, **aggregation/digests** ("Asha and 5 others liked…"), scheduling
- **Channel workers**: FCM/APNs (push), SES/SendGrid (email), SMS gateways (DLT templates in India), WhatsApp Business API, plus the **in-app inbox store**.
- **Delivery tracking**: sent → delivered → opened → clicked, plus bounces, unsubscribes and invalid tokens.
- **Clients**: web (Next.js bell dropdown) and mobile (inbox screen, badge, push taps with deep links), with **real-time updates** (WebSocket/SSE) and **read state synced across devices**.
Backend detail: **Topic 114 (Notification System)**. This file covers the full product including clients and the inbox.

## 🔵 सरल परिभाषा (Hindi)
Notification center = events ("order भेजा गया", "Asha ने फ़ोटो like की", "भुगतान fail", "आज 50% off") को सही channels पर संदेश में बदलना और ऐप के अंदर inbox (घंटी पर unread गिनती) दिखाना जो web और mobile पर एक जैसा रहे।
हिस्से: producers (services events भेजें) → notification service (template + भाषा, यूज़र की पसंद/सहमति, channel चुनना, priority, सीमा, quiet hours, duplicate हटाना, "Asha और 5 लोगों ने…" जैसा जोड़ना, scheduling) → channel workers (push, email, SMS — भारत में DLT, WhatsApp, in-app inbox) → tracking (भेजा, पहुँचा, खोला, click) → clients (real-time अपडेट और हर device पर पढ़ने की स्थिति एक जैसी)।

---

## 🔴 Problem it Solves
Without a central platform, every team sends notifications its own way:
- **Spam and fatigue**: marketing, social and transactional messages all fire at once (5 pushes in 10 minutes), so users disable notifications or uninstall.
- **Inconsistent preferences**: a user turns off offers, but one team ignores it (legal risk under India's DPDP Act and TRAI rules for SMS/calls).
- **Missed critical messages**: OTPs or payment failures stuck behind marketing in the same queue.
- **Duplicates**: retried events send the same email twice.
- **Out-of-sync read state**: notifications read on the phone still show unread on the web.
- **No visibility** into delivery and engagement, and no way to A/B test copy.
A unified system gives **reliability for critical messages, respect for user attention, consistent UX across devices, and measurability**.

## 🔴 यह क्यों बना? (Hindi)
बिना केंद्रीय platform हर टीम अपने तरीके से भेजती है: marketing, social और transactional सब एक साथ (10 मिनट में 5 push) → यूज़र notifications बंद या ऐप हटा दे; यूज़र ने offers बंद किए पर कोई टीम न माने (DPDP/TRAI का क़ानूनी जोखिम); OTP या payment fail marketing की कतार में अटके; retry से वही email दो बार; फ़ोन पर पढ़ा पर web पर अभी भी unread; delivery और engagement का पता नहीं।
एक platform = ज़रूरी संदेशों की भरोसेमंद delivery, यूज़र के ध्यान की इज़्ज़त, हर device पर एक जैसा अनुभव और नापने की क्षमता।

---

## 🟢 How it Works — Step by Step

### 1. Requirements

```
Producers send events, not channel-specific messages: {type: "ORDER_SHIPPED", userId, data, idempotencyKey}
Channels: in-app inbox, push (FCM/APNs/Web Push), email, SMS, WhatsApp
Per-user preferences per CATEGORY × CHANNEL (transactional, social, offers, reminders); legal opt-outs
Priority: critical (OTP, payment, security) > transactional (order updates) > social > marketing
Frequency caps & quiet hours (per user timezone), digests/aggregation, scheduling (send at 7 pm local)
In-app inbox: list, unread badge, mark read/all read, delete, real-time, synced across devices, 90-day retention
Tracking: sent/delivered/opened/clicked, bounces, unsubscribes; A/B testing of templates
Scale (assume): 500M notifications/day, spikes (sale start, cricket) 50k+/s
Latency: OTP/critical < 5 s end-to-end; transactional < 30 s; marketing scheduled/batched
```

### 2. Architecture

```
Producers (order, payment, social, marketing campaign tool)
   │ events (Kafka topics by priority: notif.critical, notif.transactional, notif.bulk)
   ▼
┌──────────────────────── Notification Service ─────────────────────────────┐
│ 1. Ingest & DEDUPE (idempotencyKey → Redis SETNX, TTL)                    │
│ 2. Resolve recipient: user profile, devices, email, phone, locale, tz     │
│ 3. Preferences & consent check (category × channel), legal suppressions   │
│ 4. Policy: priority, frequency caps, quiet hours, aggregation window,     │
│    channel selection & fallback (push → SMS for critical if not delivered)│
│ 5. Render templates (i18n, personalization, A/B variant)                  │
│ 6. Enqueue per channel (separate queues & rate limits per provider)       │
└──────────────────────────────────────────────────────────────────────────┘
   │             │              │              │               │
   ▼             ▼              ▼              ▼               ▼
 In-app        Push          Email           SMS          WhatsApp
 inbox store  (FCM/APNs/   (SES/SendGrid)  (gateway, DLT   (BSP API,
 (Cassandra/  Web Push)                     templates)     approved templates)
 Postgres) + WS fan-out
   │
 Delivery events (provider callbacks, opens/clicks) → tracking store → analytics & ops dashboards
```

### 3. In-app inbox data model

```
notifications (user_id, notif_id, created_at, category, type, title, body, deep_link, image,
               group_key, actor_ids[], read_at, deleted, expires_at)
   partition by user_id, cluster by created_at DESC → "latest 50 for user" is one partition read
unread_counter (user_id → count) in Redis (fast badge) + periodically reconciled with DB
Aggregation: group_key = "post:123:likes" → upsert existing notification within window:
   "Asha liked your photo" → "Asha and 5 others liked your photo" (actor_ids, count, updated_at bumped)
```

### 4. Client experience (web & mobile)

```
Bell icon + badge: GET /notifications/unread-count on load; real-time increments via WS/SSE
Inbox: GET /notifications?cursor= (paginated, grouped by Today/Earlier), virtualized list
Open notification → mark read (optimistic), deep link to target (M11/F routes)
Mark all read → server sets read_at for all ≤ now, counter = 0 → broadcast to user's other devices
Cross-device sync: read events published on user channel → web & mobile update badge instantly
Push tap: opens deep link + marks the corresponding inbox item read (same notif_id in push data)
App icon badge (iOS) = unread count sent in push payload (badge), Android shows dot/number via launcher
Empty, loading, error states; accessible list (role=list, aria-live for new items)
```

### 5. Policies that protect user attention

```
Frequency caps: e.g., ≤ 3 marketing pushes/day, ≤ 1 per 2 hours; social pushes collapsed per post
Quiet hours: 10 pm – 8 am user local time → marketing held until morning (critical bypasses)
Aggregation windows: likes/comments batched for 5–15 min before push
Channel fallback: critical OTP via SMS if push not delivered in N s; payment failure: push + email
Smart routing: if user is ACTIVE in app (WS connected) → in-app toast instead of push (avoid double)
Global kill switch & campaign throttling (sale start → stagger 10M sends over minutes)
```

### 6. India-specific channels

```
SMS: TRAI DLT — sender IDs (headers) and message templates must be pre-registered; variables only in
     approved slots; promotional vs transactional categories; time-of-day restrictions for promos
WhatsApp Business: pre-approved templates for business-initiated messages (order updates, OTP),
     24-hour customer-service window rules; opt-in required
Email: SPF/DKIM/DMARC, unsubscribe links (one-click), bounce handling
```

## 🟢 कैसे काम करता है? (Hindi)
1. Services channel नहीं, event भेजती हैं (`ORDER_SHIPPED`, userId, data, idempotencyKey) → Kafka में priority के हिसाब से topics (critical, transactional, bulk) ताकि OTP marketing के पीछे न अटके।
2. Notification service: duplicate हटाओ → यूज़र के devices/email/phone/भाषा/timezone → पसंद और सहमति जाँचो → सीमा, quiet hours, जोड़ने का समय, channel चुनो (critical पर push न पहुँचे तो SMS) → भाषा के हिसाब से template → हर channel की अलग कतार।
3. In-app inbox: यूज़र के partition में ताज़ा पहले, unread गिनती Redis में; "Asha और 5 लोगों ने like किया" के लिए group_key से एक ही notification update।
4. Client: घंटी पर गिनती, WS/SSE से real-time; inbox paginated + virtualized; खोलते ही read (optimistic) और deep link; "सब पढ़ा" और read events सारे devices पर तुरंत; push tap पर वही notif_id read; iOS badge push से।
5. ध्यान की रक्षा: दिन में 3 से ज़्यादा marketing push नहीं, रात 10–सुबह 8 बजे promo रोको, likes 5–15 मिनट जोड़कर, ऐप खुला है तो push की जगह in-app toast; भारत में SMS के लिए TRAI DLT templates, WhatsApp के approved templates, email में SPF/DKIM और unsubscribe।

---

## 🟡 Real World Example

**LinkedIn "Air Traffic Controller" (ATC)** — LinkedIn built a centralized system that decides which notifications and emails to send, through which channel and when, applying frequency limits and relevance so members aren't overwhelmed. It's a reference design for attention-aware notification platforms.

**Facebook / Instagram** — aggregate social notifications ("X and 12 others liked your post"), sync read state across devices, and personalize which notifications become pushes versus in-app only.

**Swiggy / Zomato / Flipkart** — transactional order updates go to push and the in-app tracker (plus SMS for critical steps), offers are governed by preferences and quiet hours, and big-sale campaigns are throttled to avoid crushing their own backends when millions open the app at once.

**Indian banks & UPI apps** — mandatory transaction alerts via SMS (regulatory), plus push and email. They use DLT-registered templates, and OTP delivery latency is closely monitored with multiple SMS gateways for redundancy.

## 🟡 Real Example Hindi में
LinkedIn ने "Air Traffic Controller" बनाया जो तय करता है कौन-सा notification/email, किस channel से और कब भेजना है — सीमा और relevance के साथ ताकि members परेशान न हों।
Facebook/Instagram "X और 12 लोगों ने like किया" जैसा जोड़ते और हर device पर read sync करते हैं; Swiggy/Zomato/Flipkart order updates push + in-app (ज़रूरी पर SMS), offers पसंद और quiet hours से, बड़ी sale के campaigns धीरे-धीरे; बैंक और UPI ऐप ज़रूरी SMS alerts DLT templates से, OTP के लिए कई SMS gateways।

---

## 🟠 My Stack Example

### Producer contract (any service)
```ts
await kafka.send({ topic: 'notif.transactional', messages: [{ key: String(userId), value: JSON.stringify({
  type: 'ORDER_SHIPPED', userId, category: 'transactional',
  data: { orderId: 'ord_123', eta: '2026-10-20', items: 3 },
  idempotencyKey: `ORDER_SHIPPED:ord_123`, deepLink: '/orders/ord_123',
}) }] });
```

### Notification service pipeline (Node consumer)
```js
consumer.run({ eachMessage: async ({ message }) => {
  const evt = JSON.parse(message.value);
  if (!(await redis.set(`notif:dedupe:${evt.idempotencyKey}`, 1, 'NX', 'EX', 86400))) return;   // dedupe

  const user = await profiles.get(evt.userId);                     // locale, tz, devices, email, phone, consent
  const prefs = await preferences.get(evt.userId);                 // { offers: {push:false,email:true}, ... }
  const channels = route(evt, user, prefs);                        // e.g. ['inapp','push'] ; critical → ['push','sms']
  const tmpl = await templates.render(evt.type, user.locale, evt.data, await abVariant(evt.type, user.id));

  for (const ch of channels) {
    if (!(await withinCaps(user, evt.category, ch))) continue;      // frequency caps
    if (isQuietHours(user.tz) && evt.category === 'offers') { await scheduler.at(nextMorning(user.tz), { evt, ch }); continue; }
    await queues[ch].add({ userId: user.id, tmpl, evt }, { priority: PRIORITY[evt.category] });
  }
}});

function route(evt, user, prefs) {
  const base = { critical: ['push', 'sms'], transactional: ['inapp', 'push'], social: ['inapp', 'push'], offers: ['inapp', 'push', 'email'] }[evt.category];
  return base.filter((ch) => evt.category === 'critical' || prefs[evt.category]?.[ch] !== false)
             .filter((ch) => !(ch === 'push' && realtime.isOnline(user.id) && evt.category !== 'critical'));   // active in app → in-app toast only
}
```

### In-app inbox worker with aggregation (Postgres)
```sql
CREATE TABLE notifications (
  user_id BIGINT, id UUID DEFAULT gen_random_uuid(), created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now(),
  category TEXT, type TEXT, title TEXT, body TEXT, deep_link TEXT, image TEXT,
  group_key TEXT, actor_ids BIGINT[] DEFAULT '{}', actor_count INT DEFAULT 0, read_at TIMESTAMPTZ, expires_at TIMESTAMPTZ,
  PRIMARY KEY (user_id, id));
CREATE INDEX ON notifications (user_id, updated_at DESC);
CREATE UNIQUE INDEX ON notifications (user_id, group_key) WHERE read_at IS NULL AND group_key IS NOT NULL;   -- one open group
```
```js
async function writeInbox(userId, n) {
  const row = await db.one(`
    INSERT INTO notifications (user_id, category, type, title, body, deep_link, group_key, actor_ids, actor_count, expires_at)
    VALUES ($1,$2,$3,$4,$5,$6,$7, ARRAY[$8]::bigint[], 1, now() + interval '90 days')
    ON CONFLICT (user_id, group_key) WHERE read_at IS NULL AND group_key IS NOT NULL
    DO UPDATE SET actor_ids = array_append(notifications.actor_ids, $8), actor_count = notifications.actor_count + 1,
                  title = $4, updated_at = now()
    RETURNING *, (xmax = 0) AS inserted`, [userId, n.category, n.type, n.title, n.body, n.deepLink, n.groupKey, n.actorId]);
  if (row.inserted) await redis.incr(`unread:${userId}`);
  await realtime.publish(`user:${userId}`, { t: 'notif.upsert', notif: row });       // web + mobile update live
}
```

### Inbox API: list, unread count, mark read (synced across devices)
```js
app.get('/notifications', auth, async (req, res) => {
  const { cursor } = req.query;
  const rows = await db.any(`SELECT * FROM notifications WHERE user_id=$1 AND ($2::timestamptz IS NULL OR updated_at < $2)
                             AND (expires_at IS NULL OR expires_at > now()) ORDER BY updated_at DESC LIMIT 30`, [req.user.id, cursor ?? null]);
  res.json({ items: rows, nextCursor: rows.at(-1)?.updated_at ?? null });
});
app.get('/notifications/unread-count', auth, async (req, res) => res.json({ count: Number(await redis.get(`unread:${req.user.id}`) ?? 0) }));
app.post('/notifications/read', auth, async (req, res) => {
  const { ids, all } = req.body;
  const updated = all
    ? await db.result(`UPDATE notifications SET read_at=now() WHERE user_id=$1 AND read_at IS NULL`, [req.user.id])
    : await db.result(`UPDATE notifications SET read_at=now() WHERE user_id=$1 AND id = ANY($2) AND read_at IS NULL`, [req.user.id, ids]);
  const count = all ? 0 : Math.max(0, (await redis.decrby(`unread:${req.user.id}`, updated.rowCount)));
  if (all) await redis.set(`unread:${req.user.id}`, 0);
  await realtime.publish(`user:${req.user.id}`, { t: 'notif.read', ids, all, count });  // other devices sync
  res.json({ count });
});
```

### Web bell (Next.js client) with real-time badge
```tsx
'use client';
export function NotificationBell() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ['notif', 'count'], queryFn: () => http.get('/notifications/unread-count').then((r) => r.data.count) });
  useEffect(() => realtime.subscribe('me', (e) => {
    if (e.t === 'notif.upsert') { qc.invalidateQueries({ queryKey: ['notif', 'list'] }); if (!e.notif.read_at) qc.setQueryData(['notif', 'count'], (c: number = 0) => c + (e.notif.actor_count === 1 ? 1 : 0)); }
    if (e.t === 'notif.read') qc.setQueryData(['notif', 'count'], e.count);
  }), []);
  return <button aria-label={`Notifications, ${data ?? 0} unread`}><BellIcon aria-hidden />{data ? <span className="badge">{data > 99 ? '99+' : data}</span> : null}</button>;
}
```

### Mobile: push tap → deep link + mark read; badge sync
```ts
Notifications.addNotificationResponseReceivedListener(async (r) => {
  const { notifId, url } = r.notification.request.content.data as { notifId?: string; url?: string };
  if (notifId) http.post('/notifications/read', { ids: [notifId] }).catch(() => {});
  if (url) router.push(url);
});
realtime.subscribe('me', (e) => e.t === 'notif.read' && Notifications.setBadgeCountAsync(e.count));
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you design a notification system that sends across push, email, SMS and in-app?**
A1: Producers publish semantic events with idempotency keys to priority-separated queues. A central notification service dedupes, resolves the recipient's profile, devices and locale, checks category-by-channel preferences and legal consent, applies policies (priority, frequency caps, quiet hours, aggregation, channel selection and fallback), renders localized templates (with A/B variants) and enqueues per-channel jobs. Channel workers integrate with providers (FCM/APNs, SES, SMS gateways with DLT templates, the WhatsApp BSP) with per-provider rate limits, retries and dead-letter queues. The in-app inbox is stored per user with real-time fan-out, and delivery and engagement events flow back for tracking and analytics.

**Q2: How do you prevent notification fatigue?**
A2: Use category-level preferences with easy opt-outs, frequency caps per user, category and channel, quiet hours in the user's timezone, aggregation and digests for social events, and suppression of pushes when the user is actively in the app (show an in-app toast instead). Rank and filter by relevance (only notify for high-predicted-value events), stagger campaigns, and monitor opt-out and uninstall rates as guardrail metrics. LinkedIn's ATC is a reference: a central decision-maker over all notifications.

**Q3: How do you keep unread counts and read state consistent across web and mobile?**
A3: The server is the source of truth: notifications have `read_at`, and a fast unread counter in Redis is updated transactionally with inserts and read operations and reconciled periodically with the database. Clients show optimistic updates. When a notification is read on any device (including via a push tap carrying the notification ID), the server publishes a read event on the user's real-time channel, so other connected devices update their lists and badges. Disconnected devices refetch the count on foreground, and iOS badges are set from the server count in push payloads.

**Q4: How do you guarantee OTPs and critical alerts arrive quickly?**
A4: Isolate them on a dedicated high-priority queue and workers with reserved capacity so marketing spikes can't delay them. Bypass quiet hours and caps, use the fastest channel with fallback (push, then SMS within seconds if not delivered, or SMS-first for OTP), and use multiple SMS gateways with health-based routing and DLT-approved templates. Set short TTLs so stale OTPs aren't delivered late, monitor end-to-end latency and delivery rates per provider with alerts, and make sends idempotent to avoid duplicate OTPs.

**Q5: How would you aggregate "X and 5 others liked your post"?**
A5: Assign a group key per target and action (`post:123:likes`). When a like event arrives, upsert the user's open (unread) notification with that group key, appending the actor and incrementing the count and timestamp instead of creating a new row. The title is re-rendered ("Asha and 5 others…"). Hold pushes for an aggregation window (minutes) so the user gets one push summarizing several likes, and close the group when the user reads it, so new likes start a new notification.

---

## 🔷 Trade-offs
✅ Central platform: consistent policies & analytics — ❌ becomes critical shared dependency (needs high availability, isolation per priority).
✅ Aggregation windows: less spam — ❌ slight delay for social notifications.
✅ Multi-channel fallback: reliability — ❌ cost (SMS) and duplicate-feel if not coordinated.
✅ In-app instead of push when active: less noise — ❌ requires accurate presence.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| In-app inbox | Notification list inside app | ऐप के अंदर सूचना सूची |
| Channel | Delivery medium (push/email/SMS) | पहुँचाने का माध्यम |
| Preference center | User's notification settings | सूचना की पसंद |
| Frequency cap | Max notifications per period | समय में अधिकतम सूचनाएँ |
| Quiet hours | No-send time window | न भेजने का समय |
| Aggregation / digest | Combine related notifications | मिलाकर एक सूचना |
| Channel fallback | Try another channel if failed | दूसरा माध्यम |
| DLT | India SMS template registry | SMS template पंजीकरण |
| Unread counter | Badge count of unread | न पढ़ी की गिनती |
| Delivery tracking | Sent/delivered/opened stats | पहुँच की जानकारी |

---

## ⚡ 3-Line Summary
**English:**
1. Producers emit idempotent semantic events into priority queues; a central service dedupes, checks preferences/consent, applies caps/quiet hours/aggregation, renders i18n templates and routes to channels with fallback.
2. In-app inbox per user (grouped notifications, Redis unread counter) with real-time fan-out and cross-device read sync; push taps deep link and mark read.
3. Protect attention (LinkedIn ATC-style policies), isolate critical OTP paths with multi-provider SMS, comply with DLT/WhatsApp/email rules, and track delivery & engagement.

**Hindi:**
1. Producers priority कतारों में events भेजें; केंद्रीय service duplicate हटाए, पसंद जाँचे, सीमा/quiet hours/जोड़ना लागू करे, भाषा के template बनाकर channel चुने।
2. हर यूज़र का in-app inbox (grouped, Redis गिनती), real-time और हर device पर read sync; push tap से deep link + read।
3. यूज़र के ध्यान की रक्षा, OTP का अलग तेज़ रास्ता और कई SMS gateways, DLT/WhatsApp/email नियम, delivery tracking।

---

## ➡️ Next Topic Suggestion
**P10. Real-Time Admin / Analytics Dashboard** — The last full-stack problem: ops teams watch orders, payments and riders live. Next: streaming ingestion, real-time OLAP, efficient queries, and a fast dashboard frontend with charts, filters and huge tables.
