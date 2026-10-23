# M10. Push Notifications (FCM + APNs)
# हिंदी में: Push Notifications — ऐप बंद होने पर भी सर्वर से फ़ोन तक सूचना पहुँचाना: Android पर Google का FCM, iPhone पर Apple का APNs; device token, permission, notification बनाम data message, और भरोसेमंद push pipeline

---

## 🔵 Simple Definition (English)
A **push notification** is a message sent from your server **through the OS vendor's push service** to a user's device, even when your app is **backgrounded or killed**:
- **APNs (Apple Push Notification service)** for iOS, iPadOS and macOS.
- **FCM (Firebase Cloud Messaging)** for Android (and it can also relay to APNs for iOS).
How it works:
1. The app asks permission (iOS always; Android 13+ needs `POST_NOTIFICATIONS`).
2. The OS gives the app a **device token** (FCM registration token / APNs device token).
3. The app sends the token to **your backend**, which stores it per user and device.
4. To notify, your backend calls the FCM/APNs API with the token and a payload.
5. The OS delivers it and shows it (alert, sound, badge) or wakes the app (data/background push).
Payload types:
- **Notification/alert** messages, displayed by the OS automatically.
- **Data/background** messages (`content-available`), handled by app code. These are throttled and not guaranteed, especially on iOS.
In React Native: `@react-native-firebase/messaging`, `expo-notifications` (with the Expo push service or direct FCM/APNs), and **Notifee** for rich local display.

## 🔵 सरल परिभाषा (Hindi)
Push notification = आपके सर्वर से Apple (APNs) या Google (FCM) की push service के ज़रिए फ़ोन तक संदेश — ऐप background में हो या बंद, फिर भी।
तरीका: ऐप permission माँगे (iOS हमेशा, Android 13+ भी) → OS एक device token दे → ऐप वो token आपके backend को भेजे (user + device के साथ save) → भेजना हो तो backend FCM/APNs API को token + payload दे → OS दिखाए या ऐप को जगाए। Notification message OS ख़ुद दिखाता है; data/background message ऐप का code संभालता है (iOS पर सीमित, पक्का नहीं)।

---

## 🔴 Problem it Solves
Apps can't keep a socket open in the background (battery, OS limits, M04), but users need to know **now**:
- "Your order is out for delivery 🛵", "Driver arrived", "OTP for login", "Payment received ₹500", "New message from Mom", "India need 12 runs in 6 balls!".
Polling from every phone would drain batteries and overload servers. Instead, **the OS keeps one shared, battery-efficient connection to Apple/Google** for all apps, and your server just hands messages to that system.
Push is also a key **re-engagement** channel (offers, reminders), which makes **relevance, frequency control and opt-outs** important. Spammy push causes users to disable notifications or uninstall.

## 🔴 यह क्यों बना? (Hindi)
Background में ऐप socket खुला नहीं रख सकता (battery, OS की पाबंदी), पर यूज़र को अभी पता चलना चाहिए — "order निकल चुका 🛵", "driver पहुँच गया", "OTP", "₹500 मिले", "माँ का message", "6 गेंद में 12 रन!"।
हर फ़ोन से polling = battery ख़त्म और सर्वर पर भार; इसलिए OS Apple/Google से एक साझा, battery-बचाऊ कनेक्शन रखता है और आपका सर्वर बस संदेश उसे दे देता है। Push यूज़र को वापस लाने का बड़ा ज़रिया भी है — इसलिए सही समय, सीमित संख्या और opt-out ज़रूरी, वरना यूज़र notifications बंद या ऐप हटा देते हैं।

---

## 🟢 How it Works — Step by Step

### End-to-end flow

```
 ┌──────── Device ────────┐                      ┌──────── Your backend ────────┐
 │ 1. request permission  │                      │                               │
 │ 2. OS → device token   │──3. POST /devices───►│ devices table:                │
 │    (FCM/APNs)          │   {token, platform,  │ user_id, device_id, token,    │
 │                        │    appVersion, locale│ platform, locale, last_seen   │
 └──────────▲─────────────┘   , tz}              └──────────────┬────────────────┘
            │                                                   │ 4. event: order.out_for_delivery
            │ 6. OS displays / wakes app                        ▼
            │                                  Notification service (Topic 114):
 ┌──────────┴──────────┐   5. send (HTTP/2)   preferences, quiet hours, dedupe, rate limit,
 │  APNs / FCM         │◄─────────────────────templating + i18n, priority, collapse key
 │ (one persistent,    │                       → queue (Kafka/SQS) → push workers
 │  OS-level conn)     │──► responses: success / invalid token (410/UNREGISTERED) → delete token
 └─────────────────────┘
```

### Payload types & behaviour

```
┌──────────────────────┬──────────────────────────────────────────┬─────────────────────────────────┐
│ Type                 │ Behaviour                                │ Use for                         │
├──────────────────────┼──────────────────────────────────────────┼─────────────────────────────────┤
│ Alert / notification │ OS shows title/body/sound/badge even if  │ User-visible updates (order,    │
│ message              │ app killed; tap → opens app (deep link)  │ messages, OTP, offers)          │
│ Data message (FCM)   │ Delivered to app code (onMessage /       │ Silent sync, custom rendering   │
│                      │ background handler); Android: high       │ (Notifee), call invites         │
│                      │ priority only for user-visible results   │                                 │
│ Background push (iOS │ content-available:1, apns-priority 5,    │ Opportunistic refresh — NOT     │
│ "silent")            │ throttled by iOS, not delivered if app   │ guaranteed                      │
│                      │ force-quit                               │                                 │
│ VoIP push (iOS)      │ PushKit, must report a CallKit call      │ Incoming calls (WhatsApp, Zoom) │
│ Live Activities      │ Updates lock-screen widget via APNs      │ Delivery/ride ETA, live score   │
│ (iOS 16.1+)          │                                          │                                 │
└──────────────────────┴──────────────────────────────────────────┴─────────────────────────────────┘
Rich notifications: images (iOS Notification Service Extension with mutable-content:1; Android BigPicture),
action buttons ("Reply", "Track"), grouping (thread-id / Android group), collapse keys (replace older
"ETA 12 min" with "ETA 8 min"), TTL (don't deliver stale OTPs after 5 min)
```

### Permissions & channels

```
iOS: requestAuthorization (alert, sound, badge); "provisional" = quiet delivery without prompt
Android 13+: runtime POST_NOTIFICATIONS permission; Android 8+: notification CHANNELS
  (orders: high importance; promotions: default; chat: high + custom sound) → users can mute per channel
Best practice: ask at a meaningful moment ("Get live updates on your order?") not at first launch
→ much higher opt-in; explain value with a pre-permission screen
```

### Token management (where bugs hide)

```
- Tokens change (reinstall, restore, token refresh, OS updates) → listen for onTokenRefresh, re-register
- Register on every app start (cheap upsert with last_seen) → keeps token fresh
- Multiple devices per user → send to all active devices (or most recent for OTP)
- Logout → unregister token from that user (avoid notifying the next user on a shared phone!)
- Remove invalid tokens on APNs 410 / FCM UNREGISTERED responses; prune tokens unseen for ~60–90 days
```

### Reliability & delivery semantics

```
Push is BEST-EFFORT: can be delayed (Doze, low power, network), collapsed, or dropped (device off > TTL)
→ never put the only copy of important data in a push; the app must fetch state on open
→ OTP: also SMS fallback; payments: in-app status + SMS/email
Track funnel: sent → accepted by FCM/APNs → delivered (FCM delivery data / client receipt ping) → opened
Throughput: FCM/APNs handle huge volumes but enforce rate limits; spread mass campaigns, use topics or
batched sends (FCM HTTP v1 per-message; topic messaging for broadcast)
```

### Security & privacy

```
- Server credentials: APNs auth key (.p8, token-based JWT) and FCM service account → secrets manager
- Don't include sensitive data in plaintext payloads (they may show on the lock screen)
  → generic text ("You have a new message") or encrypt payload & decrypt in a Notification Service
     Extension (WhatsApp-style E2E)
- Respect user preferences, quiet hours (no promos at 2 AM IST), frequency caps; DND for marketing (TRAI
  rules apply to SMS/calls; app push is governed by store policies + user consent)
```

## 🟢 कैसे काम करता है? (Hindi)
1. ऐप permission माँगता है (iOS हमेशा; Android 13+ में भी) → OS device token देता है → ऐप `POST /devices` से token, platform, version, भाषा backend को भेजता है।
2. Event आने पर (order निकला) notification service पसंद, quiet hours, duplicate, सीमा, भाषा देखकर queue में डालती है → workers FCM/APNs को HTTP/2 से भेजते हैं → OS फ़ोन पर दिखाता है; token ग़लत (410/UNREGISTERED) तो DB से हटाओ।
3. Notification message OS ख़ुद दिखाता है (ऐप बंद हो तब भी); data message ऐप का code संभालता है; iOS silent push सीमित और पक्का नहीं; calls के लिए VoIP push + CallKit; iOS Live Activities से lock screen पर ETA।
4. Permission सही समय पर माँगो ("order की live updates चाहिए?"), Android channels (orders, offers, chat) बनाओ; token हर start पर update, logout पर हटाओ, पुराने tokens साफ़ करो।
5. Push पक्का नहीं — ज़रूरी डेटा सिर्फ़ push में मत रखो, ऐप खुलने पर state लाओ, OTP के लिए SMS backup; lock screen पर निजी जानकारी नहीं (या encrypt); रात 2 बजे promo नहीं, frequency cap।

---

## 🟡 Real World Example

**WhatsApp** — message pushes carry encrypted content. On iOS a Notification Service Extension decrypts and shows a preview, so the plaintext never passes through Apple or Google. VoIP pushes with CallKit ring incoming calls even when the app is killed.

**Swiggy / Zomato / Uber** — transactional pushes for every order or trip state (collapse keys replace older ETAs), plus iOS Live Activities and Android ongoing notifications showing live delivery progress on the lock screen. Zomato is famously known in India for witty, culturally topical push copy, which shows push as a brand channel.

**JioCinema / Hotstar / Dream11 during IPL and World Cup** — huge broadcast spikes ("Toss: India won!") to tens of millions of devices within seconds, using topic or segmented sends, pre-warmed workers and staggered delivery to avoid overloading their own backends when everyone opens the app.

**Banks & UPI apps** — use push for transaction alerts alongside mandatory SMS. OTP autofill often uses the SMS Retriever API, with push as a supplement.

## 🟡 Real Example Hindi में
WhatsApp के push में content encrypted होता है — iOS पर Notification Service Extension फ़ोन पर ही decrypt करके preview दिखाता है; VoIP push + CallKit से ऐप बंद होने पर भी call बजती है।
Swiggy/Zomato/Uber हर order/trip स्थिति पर push भेजते हैं (collapse key पुराना ETA बदल देती है) और lock screen पर live progress; Zomato अपने मज़ेदार push संदेशों के लिए मशहूर; IPL/World Cup में JioCinema/Hotstar/Dream11 सेकंडों में करोड़ों devices को push भेजते हैं।

---

## 🟠 My Stack Example

### React Native (Expo): permission at the right moment + register token
```ts
// src/platform/push.ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

export async function setupAndroidChannels() {
  if (Platform.OS !== 'android') return;
  await Notifications.setNotificationChannelAsync('orders', { name: 'Order updates', importance: Notifications.AndroidImportance.HIGH, sound: 'default' });
  await Notifications.setNotificationChannelAsync('offers', { name: 'Offers & deals', importance: Notifications.AndroidImportance.DEFAULT });
  await Notifications.setNotificationChannelAsync('chat', { name: 'Messages', importance: Notifications.AndroidImportance.HIGH });
}

export async function enablePush(userId: string) {           // call after user places first order, with pre-prompt
  if (!Device.isDevice) return null;
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') return null;
  const token = (await Notifications.getDevicePushTokenAsync()).data;     // raw FCM/APNs token (or getExpoPushTokenAsync)
  await http.post('/devices', { token, platform: Platform.OS, appVersion, locale: i18n.language, tz: Intl.DateTimeFormat().resolvedOptions().timeZone });
  return token;
}

// Handle taps → deep link (M11)
Notifications.addNotificationResponseReceivedListener((resp) => {
  const url = resp.notification.request.content.data?.url as string | undefined;
  if (url) router.push(url);                                  // e.g., /order/123/track
});
// Foreground display behaviour
Notifications.setNotificationHandler({ handleNotification: async () => ({ shouldShowBanner: true, shouldShowList: true, shouldPlaySound: true, shouldSetBadge: false }) });
```

### Backend: devices table + token upsert (Postgres)
```sql
CREATE TABLE devices (
  id BIGSERIAL PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES users(id),
  token TEXT NOT NULL UNIQUE, platform TEXT NOT NULL, app_version TEXT, locale TEXT, tz TEXT,
  last_seen TIMESTAMPTZ NOT NULL DEFAULT now(), disabled_at TIMESTAMPTZ);
CREATE INDEX idx_devices_user ON devices(user_id) WHERE disabled_at IS NULL;
-- upsert: INSERT ... ON CONFLICT (token) DO UPDATE SET user_id=EXCLUDED.user_id, last_seen=now(), disabled_at=NULL;
```

### Sending via FCM HTTP v1 (Node, firebase-admin) — Android + iOS
```js
import admin from 'firebase-admin';
admin.initializeApp({ credential: admin.credential.applicationDefault() });   // service account from secrets

export async function sendOrderUpdate(userId, order) {
  const devices = await db.query('SELECT token, locale FROM devices WHERE user_id=$1 AND disabled_at IS NULL', [userId]);
  const results = await Promise.allSettled(devices.rows.map((d) => admin.messaging().send({
    token: d.token,
    notification: { title: t(d.locale, 'order.outTitle'), body: t(d.locale, 'order.outBody', { eta: order.etaMin }) },
    data: { url: `/order/${order.id}/track`, orderId: order.id, type: 'ORDER_STATUS' },        // strings only
    android: { priority: 'high', collapseKey: `order-${order.id}`, ttl: 30 * 60 * 1000, notification: { channelId: 'orders' } },
    apns: { headers: { 'apns-priority': '10', 'apns-collapse-id': `order-${order.id}`, 'apns-push-type': 'alert' },
            payload: { aps: { sound: 'default', 'thread-id': `order-${order.id}`, 'mutable-content': 1 } } },
  })));
  await Promise.all(results.map((r, i) => {                    // prune dead tokens
    const code = r.status === 'rejected' && r.reason?.errorInfo?.code;
    return code === 'messaging/registration-token-not-registered' || code === 'messaging/invalid-registration-token'
      ? db.query('UPDATE devices SET disabled_at=now() WHERE token=$1', [devices.rows[i].token]) : null;
  }));
}
```

### Notification service guardrails (FastAPI worker sketch)
```python
async def should_send(user_id: int, kind: str, now_ist: datetime) -> bool:
    prefs = await get_prefs(user_id)                          # per-category opt-ins
    if not prefs.get(kind, True): return False
    if kind == "promo" and (now_ist.hour >= 22 or now_ist.hour < 8): return False      # quiet hours
    key = f"push:cap:{user_id}:{kind}:{now_ist:%Y%m%d}"
    count = await redis.incr(key); await redis.expire(key, 86400)
    return kind != "promo" or count <= 3                      # max 3 promos/day
# Dedupe: SET NX push:dedupe:{event_id} EX 3600 before sending (events can be redelivered)
```

### Logout: detach token
```ts
export async function onLogout() {
  const token = (await Notifications.getDevicePushTokenAsync()).data;
  await http.delete('/devices', { data: { token } }).catch(() => {});   // so next user on this phone doesn't get old user's pushes
}
```

---

## ⚫ Interview Questions + Answers

**Q1: How do push notifications work end to end?**
A1: The app requests permission and registers with the platform push service (APNs, or FCM which also covers iOS via APNs), receiving a device token. The app sends the token, with user, device, platform, locale and app version, to the backend, which stores it. When an event occurs, the backend's notification service applies preferences, rate limits and templating, then calls the FCM or APNs API with the token and payload. The vendor delivers the message over the OS's persistent connection, and the OS displays it or wakes the app. The backend handles responses, removing invalid tokens.

**Q2: Notification message vs data message — what's the difference?**
A2: A notification (alert) message contains display fields that the OS renders automatically when the app is backgrounded or killed, which makes it reliable for user-visible alerts. A data message carries key-value data delivered to app code for custom handling (sync, custom UI via Notifee, call invites). On Android, high-priority data messages can wake the app but should lead to user-visible notifications. On iOS, background (silent) pushes are throttled, low priority and not delivered to force-quit apps, so don't depend on them for critical flows. Many apps send both: a notification block plus data for deep linking.

**Q3: How do you manage device tokens correctly?**
A3: Upsert the token on every app start and on token-refresh callbacks, with last-seen timestamps. Support multiple devices per user. Detach the token on logout so another user on the same device doesn't receive pushes. Delete or disable tokens on invalid-token responses (APNs 410, FCM UNREGISTERED). Prune stale tokens unseen for months. Store platform, app version and locale for targeting and formatting. Keep vendor credentials (APNs .p8 key, FCM service account) in a secrets manager.

**Q4: Design order-status notifications for a food delivery app.**
A4: Order service events (accepted, picked up, out for delivery, delivered) go to Kafka. A notification service consumes them, dedupes by event ID, checks user preferences, picks channels (push plus in-app, SMS for critical cases), localizes templates and enqueues sends. Push workers call FCM and APNs with high priority, a collapse key per order (latest ETA replaces older ones), a short TTL and a deep link to the tracking screen. They track sent, delivered and opened, and prune bad tokens. iOS Live Activities and Android ongoing notifications show progress. The app always fetches the latest state on open, since push is best-effort.

**Q5: Why shouldn't push be your only delivery mechanism for important information?**
A5: Push delivery is best-effort: messages can be delayed by Doze or low-power modes, dropped when the device is offline beyond the TTL, collapsed, blocked by revoked permissions or muted channels, or never shown if the token is stale. Critical information (OTP, payment status, order state) must also be available in the app (fetched on open or via sync) and via fallback channels like SMS or email where required. Push should notify, not be the system of record.

---

## 🔷 Trade-offs
✅ Battery-efficient reach when app is closed — ❌ best-effort delivery, vendor dependency.
✅ Rich, actionable notifications boost engagement — ❌ notification fatigue → opt-outs/uninstalls.
✅ Data/silent pushes for freshness — ❌ throttled/unreliable on iOS.
✅ Expo push service: simple unified API — ❌ extra hop/dependency vs direct FCM/APNs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| APNs | Apple push service | Apple की push सेवा |
| FCM | Firebase Cloud Messaging | Google की push सेवा |
| Device token | Address of app install for push | push का पता |
| Notification message | OS-displayed alert | OS से दिखने वाली सूचना |
| Data message | Payload handled by app | ऐप द्वारा संभाला डेटा |
| Silent push | Background wake, no UI | बिना दिखे जगाना |
| Notification channel | Android category with settings | Android की श्रेणी |
| Collapse key | Replace older notification | पुरानी सूचना बदलना |
| TTL | Time-to-live for delivery | कब तक भेजनी है |
| Notification Service Extension | iOS pre-display modifier | iOS में दिखाने से पहले बदलना |

---

## ⚡ 3-Line Summary
**English:**
1. Push = app gets token from APNs/FCM → backend stores it → backend sends via vendor API → OS delivers even if app is killed.
2. Use alert messages for user-visible info, data/silent for opportunistic work; channels, collapse keys, TTL, rich media and deep links; ask permission at a meaningful moment.
3. Manage tokens (refresh, multi-device, logout detach, prune invalid), enforce preferences/quiet hours/caps, protect sensitive content, and never rely on push as the only source of truth.

**Hindi:**
1. Push = APNs/FCM से token → backend में save → vendor API से भेजो → ऐप बंद हो तब भी पहुँचे।
2. दिखने वाली बातों के लिए alert, बाक़ी के लिए data/silent; channels, collapse key, TTL, deep links; permission सही समय पर।
3. Tokens संभालो (refresh, कई devices, logout पर हटाओ), पसंद/quiet hours/सीमा मानो, निजी जानकारी छुपाओ, push को एकमात्र स्रोत मत बनाओ।

---

## ➡️ Next Topic Suggestion
**M11. Deep Linking + Universal Links** — Tapping a notification, a shared link or a QR code should open the right screen in the app. Next: URL schemes, Universal Links, Android App Links, deferred deep links, and routing safely.
