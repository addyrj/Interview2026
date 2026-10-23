# M01. Mobile System Design Framework
# हिंदी में: Mobile System Design Framework — mobile app (iOS/Android/React Native) के design इंटरव्यू का ढाँचा: ज़रूरतें, app की परतें, फ़ोन पर डेटा कैसे रखें, API कैसी हो, और offline, battery, performance, release जैसी mobile की ख़ास बातें

---

## 🔵 Simple Definition (English)
A **mobile system design** interview asks you to design the **client app** (and its contract with the backend) for a product like WhatsApp, Instagram, Uber, Swiggy or a banking app, on **iOS and Android** (often with **React Native**).
Mobile adds constraints that web doesn't have:
- **App lifecycle**: background, suspended, killed by the OS
- **Unreliable networks**: offline, 2G/3G, switching Wi-Fi ↔ mobile data
- **Limited battery, memory and storage**, plus device fragmentation (₹7,000 Android to iPhone Pro)
- **Push notifications, deep links, permissions** (location, camera, contacts)
- **Slow, gated releases** (app-store review) and **many old versions in the wild**, so APIs must stay backward compatible
A good structure: **Requirements → High-level architecture (app layers + platform services) → Data & storage → API & sync contract → Deep dives (offline/sync, performance, battery, security, releases, observability)**.

## 🔵 सरल परिभाषा (Hindi)
Mobile system design इंटरव्यू में WhatsApp, Uber, Swiggy जैसे ऐप का फ़ोन वाला हिस्सा (और backend से उसका contract) डिज़ाइन करना होता है — iOS/Android, अक्सर React Native पर।
Mobile की ख़ास मुश्किलें: OS ऐप को background में रोक या बंद कर देता है, नेटवर्क टूटता/धीमा, battery-memory-storage सीमित, सस्ते से महँगे तक कई तरह के फ़ोन, push/deep links/permissions, app store review से धीमी release और पुराने versions सालों चलते रहते हैं। ढाँचा: ज़रूरतें → app की परतें → डेटा/storage → API और sync → गहराई (offline, performance, battery, security, release)।

---

## 🔴 Problem it Solves
Candidates often answer mobile rounds like backend rounds (drawing Kafka and databases) or like web rounds, and miss what makes mobile hard:
- What happens when the user is **offline** or the app is **killed mid-upload**?
- How do you show the first screen in **< 2 s on a low-end phone**?
- How do you avoid **draining battery** with location or sockets?
- How do you ship a fix when **30% of users never update**?
- Where do you store **tokens securely**?
A mobile-specific framework shows you think like someone who has shipped apps to millions of real devices.

## 🔴 यह क्यों बना? (Hindi)
लोग mobile round को backend (Kafka, DB) या web की तरह जवाब देते हैं और असली mobile सवाल छोड़ देते हैं: offline हो या upload के बीच ऐप बंद हो जाए तो? सस्ते फ़ोन पर 2 सेकंड में पहली screen कैसे? location/socket से battery कैसे न ख़त्म हो? 30% यूज़र update ही न करें तो fix कैसे पहुँचे? token सुरक्षित कहाँ रखें?
Mobile का अलग ढाँचा दिखाता है कि आपने असली devices पर लाखों यूज़र्स के लिए ऐप बनाए हैं।

---

## 🟢 How it Works — Step by Step

### Time plan (45–60 min)

```
1. Requirements & constraints ...... 5–8 min
2. High-level app architecture ..... 8–10 min (layers + platform services diagram)
3. Data model & local storage ...... 5–8 min
4. API / sync contract ............. 5–8 min
5. Deep dives ...................... 15–20 min (pick 2–4: offline sync, media, real-time, perf, battery, security, release)
6. Trade-offs, monitoring, wrap-up . 2–3 min
```

### 1. Requirements: mobile-specific questions

```
Functional: core flows (e.g., chat: 1:1, groups, media, receipts), which screens, notifications, deep links
Platforms: iOS + Android? Min OS (iOS 15+, Android 8+)? Tablets? React Native or native?
Offline: read offline? write offline (queue)? how stale is OK?
Real-time: live updates while open? when backgrounded → push
Device features: camera, location (foreground/background), contacts, biometrics, Bluetooth
Constraints: low-end devices (2–3 GB RAM), 3G, data cost, battery, app size (< 50 MB download?)
Non-functional: cold start < 2 s, 60 fps scrolling, crash-free ≥ 99.8%, a11y, i18n (Hindi, Tamil)
Security/compliance: payments, PII, RBI/DPDP rules, jailbreak/root policy
Release: how often, OTA allowed?, support old versions for how long, force update
```

### 2. High-level app architecture

```
┌───────────────────────────────────── Mobile App ─────────────────────────────────────┐
│ UI layer: screens + components (RN), navigation (React Navigation / Expo Router)      │
│      ▲ state/hooks (React Query for server state, Zustand for UI/session state)        │
│ Domain/use-cases: sendMessage(), placeOrder(), startTrip()  (pure logic, testable)    │
│      ▲                                                                                 │
│ Data layer — Repository pattern (single source of truth = LOCAL DB)                    │
│   ├─ Local storage: SQLite/WatermelonDB/op-sqlite (entities), MMKV (KV/prefs),         │
│   │                 Keychain/Keystore (tokens), file system (media cache)              │
│   ├─ Remote: API client (REST/GraphQL via BFF), WebSocket/MQTT realtime               │
│   └─ Sync engine: outbox queue, retry/backoff, delta pull, conflict resolution         │
│ Platform services: push (FCM/APNs), background tasks, location, camera/media,          │
│   deep links, biometrics, permissions, network state (NetInfo), app lifecycle          │
│ Cross-cutting: auth/session, feature flags & remote config, analytics, crash/perf      │
│   monitoring (Sentry/Crashlytics), i18n, theming/design system, OTA updates           │
└────────────────────────────────────────────────────────────────────────────────────────┘
          │ HTTPS (BFF/API Gateway)   │ WSS/MQTT    │ FCM/APNs      │ CDN (images/video)
          ▼                           ▼             ▼               ▼
                                   Backend (covered in 06-Backend-Design-Problems)
```

### 3. Data & storage decisions

```
What lives locally, how much, for how long: last 50 chats × 100 messages, menu cache 1 day
Entities + indexes in SQLite (query offline, sort, search); KV prefs in MMKV; secrets in Keychain
Media: disk cache with LRU eviction (e.g., 500 MB cap), thumbnails vs full-size
Schema migrations for local DB across app versions (!!)
Encryption at rest for sensitive data (SQLCipher / OS file protection)
```

### 4. API & sync contract (mobile-friendly)

```
- Screen-shaped responses via BFF (fewer round trips on high-latency networks)
- Cursor pagination + delta sync: GET /sync?since=<token> → changes + tombstones + newToken
- Idempotency keys for all writes (retries are normal on mobile)
- Payload diet: only needed fields, compressed (gzip/brotli), image URLs sized for device
- Versioning: additive changes; X-App-Version header; min-supported version → force/soft update
- Real-time: WebSocket while foreground, push notifications when background/killed
```

### 5. Deep-dive menu

```
Offline-first & sync (M06/M07)       Performance: startup, lists, images, memory (M03, M12–M14)
Networking on flaky links (M08)      Push & deep links (M10/M11)
Media upload/download (M21)          Location & maps, battery (M20)
Security & auth (M15/M16)            Releases: OTA, force update, CI/CD (M17–M19)
Observability: crashes, ANRs, analytics (M22)
```

### Mobile vs web: quick contrast

```
Web: refresh fixes most things; deploy = instant for all users; tabs; SEO; browser sandbox
Mobile: app can be killed anytime; release = days + users on old versions for years; push & background
        limits (iOS strict); app size & store policies; device permissions; offline expected
```

## 🟢 कैसे काम करता है? (Hindi)
1. ज़रूरतें पूछो: कौन-से flows, iOS/Android/min version, offline पढ़ना/लिखना, background में क्या (push), camera/location, सस्ते फ़ोन और 3G, cold start < 2 s, crash-free %, release और force update नीति।
2. परतें बनाओ: UI + navigation → state/hooks → domain logic → repository (असली सच्चाई local DB में) → local storage + API client + sync engine; साथ में platform services (push, location, background, deep links) और cross-cutting (auth, flags, crash reporting, OTA)।
3. Storage तय करो: entities SQLite में, छोटी settings MMKV में, tokens Keychain में, media disk cache (LRU सीमा); ऐप versions के बीच local DB migration मत भूलो।
4. API mobile के लिए: BFF से स्क्रीन जैसा जवाब, cursor + delta sync, हर write पर idempotency key, छोटा payload, app version header और force update, foreground में WebSocket और background में push।
5. 2–4 गहराइयाँ चुनो (offline sync, performance, battery, security, release) और trade-offs बताओ।

---

## 🟡 Real World Example

**WhatsApp** — the local database is the source of truth for chats (works offline). It uses a persistent connection while in the foreground and push notifications when backgrounded, with message queues and retries on flaky 2G. It's famously lean on low-end Android phones.

**Uber / Ola driver apps** — background location with battery-aware sampling, offline trip state, resilience to network drops mid-trip, and force updates for safety-critical changes.

**Swiggy / Zomato** — server-driven home screens (no app release needed), image-heavy lists optimized for low-end devices, real-time order tracking (sockets plus push), and city-wise feature rollouts via remote config.

**Mobile interview loops (Meta, Uber, Airbnb, Flipkart, CRED)** — include "mobile system design" rounds (design Instagram feed client, offline-first notes, image loader library, chat client) evaluated on exactly these mobile concerns.

## 🟡 Real Example Hindi में
WhatsApp में local DB ही असली सच्चाई — offline भी chats दिखती हैं; foreground में खुला कनेक्शन, background में push; 2G पर retry; सस्ते Android पर भी हल्का।
Uber/Ola driver ऐप battery का ध्यान रखते हुए background location भेजता है और नेटवर्क टूटने पर भी trip की स्थिति बचाकर रखता है; Swiggy/Zomato का home screen सर्वर तय करता है (बिना release बदलाव) और शहर-दर-शहर features remote config से खुलते हैं।

---

## 🟠 My Stack Example

### Folder structure for an Expo / React Native app
```
app/                         ← Expo Router screens (file-based routes, deep-link friendly)
  (tabs)/home.tsx, orders.tsx, account.tsx
  restaurant/[id].tsx, order/[id]/track.tsx
src/
  features/orders/
    api.ts                   ← typed API calls (BFF)
    repository.ts            ← reads local DB, syncs with API (single source of truth)
    hooks.ts                 ← useOrders(), usePlaceOrder() (React Query + DB observers)
    components/
  data/
    db/schema.ts, migrations.ts   ← SQLite (op-sqlite / expo-sqlite) or WatermelonDB
    kv.ts                         ← MMKV (prefs, feature flags cache)
    secure.ts                     ← expo-secure-store (tokens)
    sync/outbox.ts                ← queued writes with idempotency keys
  platform/
    push.ts, deeplinks.ts, location.ts, background.ts, netinfo.ts
  shared/
    http.ts (auth refresh, retry), realtime.ts, analytics.ts, sentry.ts, i18n/, ui/ (design system)
```

### Repository: local DB is the source of truth, network refreshes it
```ts
// src/features/orders/repository.ts
export const ordersRepo = {
  observeActive: () => db.orders.query(Q.where('status', Q.notIn(['DELIVERED', 'CANCELLED']))).observe(), // UI subscribes
  async refresh() {
    const since = kv.getString('orders.syncToken');
    const { changes, deleted, syncToken } = await api.get('/mobile/orders/sync', { params: { since } }).then(r => r.data);
    await db.write(async () => { await upsertOrders(changes); await deleteOrders(deleted); });
    kv.set('orders.syncToken', syncToken);
  },
  async placeOrder(cart: Cart) {
    const clientId = uuid();
    await db.write(() => db.orders.create({ clientId, status: 'PENDING_SYNC', ...fromCart(cart) }));  // optimistic, offline-safe
    await outbox.enqueue({ type: 'PLACE_ORDER', clientId, body: cart, idempotencyKey: clientId });   // sync engine sends
  },
};
```

### App lifecycle hooks that matter
```ts
AppState.addEventListener('change', (state) => {
  if (state === 'active') { ordersRepo.refresh(); realtime.connect(); outbox.flush(); }
  if (state === 'background') { realtime.close(); analytics.flush(); }
});
NetInfo.addEventListener((s) => { if (s.isConnected) outbox.flush(); });
```

### API contract snippet (BFF) with version awareness
```js
app.use((req, res, next) => {
  const v = req.get('X-App-Version') ?? '0.0.0';
  if (semver.lt(v, config.minSupportedVersion)) return res.status(426).json({ error: { code: 'UPGRADE_REQUIRED', storeUrl: storeUrlFor(req) } });
  req.appVersion = v; next();
});
```

---

## ⚫ Interview Questions + Answers

**Q1: How is mobile system design different from web frontend design?**
A1: Mobile apps run under OS lifecycle control (backgrounded, suspended, killed), so state must be persisted and work resumed. Networks are unreliable, which makes offline-first storage, retries and sync central. Devices vary widely in CPU, memory and storage, and battery use matters. Push notifications, background execution limits, permissions and deep links are first-class concerns. Releases go through app-store review and old versions persist for years, so APIs must be backward compatible, with force-update and OTA strategies. Web can refresh and deploy instantly; mobile can't.

**Q2: What does a typical mobile app architecture look like?**
A2: Layers: a UI layer (screens, components, navigation) bound to state via hooks or view models; a domain layer with use-cases; and a data layer using the repository pattern, coordinating local persistence (SQLite or WatermelonDB for entities, MMKV for key-value, Keychain/Keystore for secrets, a file cache for media) with remote sources (REST/GraphQL via a BFF, WebSocket) through a sync engine (outbox, retries, delta pull, conflicts). Platform services cover push, background tasks, location, media, deep links and permissions. Cross-cutting concerns include auth, flags and remote config, analytics, crash reporting, i18n and OTA updates.

**Q3: What requirements would you clarify for a mobile chat app?**
A3: Supported platforms and minimum OS versions, 1:1 vs group sizes, media types and size limits, offline read and send (queueing), delivery and read receipts, notification behaviour (foreground, background, killed), end-to-end encryption, multi-device sync, history retention and local storage limits, target devices and networks (low-end Android, 2G/3G), performance targets (cold start, scroll fps), battery constraints for keeping connections, and release cadence with backward compatibility.

**Q4: Why make the local database the source of truth?**
A4: The UI reads from local storage, which is always available, fast and consistent, while the network asynchronously syncs it. That gives instant screens (no spinners on reopen), offline support, a single place for optimistic writes (marked pending and queued), simpler UI logic (observe the DB) and resilience when the app is killed mid-operation, since the queue persists. The costs are sync complexity (delta sync, conflicts, schema migrations) and storage management.

**Q5: How do you handle users on old app versions?**
A5: Design APIs to be backward compatible: additive changes only, tolerant readers that ignore unknown fields and widget types, server-side defaults, and versioned endpoints for breaking changes. Send the app version with requests so the backend can adapt responses. Use remote config for minimum and recommended versions to drive force or soft update prompts. Use OTA updates for JS-only fixes in React Native. Keep feature flags with safe defaults. Track version adoption and sunset old versions deliberately.

---

## 🔷 Trade-offs
✅ Offline-first (local source of truth): instant, resilient UX — ❌ sync & migration complexity.
✅ React Native: one codebase, OTA, web skills — ❌ native modules for some features, perf tuning.
✅ Server-driven UI: change screens without release — ❌ less flexibility per screen, testing complexity.
✅ Strict backward compatibility: no broken old apps — ❌ API cruft, longer support windows.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| App lifecycle | Foreground/background/killed states | ऐप की अवस्थाएँ |
| Repository pattern | Data access abstraction | डेटा लाने की परत |
| Source of truth | Authoritative data store | असली डेटा का स्रोत |
| Sync engine | Syncs local and server data | local और server मिलाने वाला |
| Outbox | Queue of pending writes | भेजने के लिए कतार |
| Delta sync | Fetch only changes | सिर्फ़ बदलाव लाना |
| Push notification | Server-to-device message via OS | OS से आने वाली सूचना |
| Force update | Require newer app version | ज़बरदस्ती update |
| OTA update | Update JS without store release | बिना store के update |
| Device fragmentation | Many device types/OS versions | कई तरह के फ़ोन |

---

## ⚡ 3-Line Summary
**English:**
1. Mobile design = requirements (offline, background, devices, releases) → app layers + platform services → local storage → API/sync contract → deep dives.
2. Make the local DB the source of truth with a sync engine (outbox, delta pull, idempotency); use sockets in foreground and push in background.
3. Design for flaky networks, low-end devices, battery, security, and old app versions (backward-compatible APIs, force update, OTA).

**Hindi:**
1. Mobile design = ज़रूरतें (offline, background, devices, release) → परतें + platform services → local storage → API/sync → गहराई।
2. Local DB असली सच्चाई + sync engine (outbox, delta, idempotency); foreground में socket, background में push।
3. टूटता नेटवर्क, सस्ते फ़ोन, battery, security और पुराने versions (backward compatible API, force update, OTA) के लिए डिज़ाइन।

---

## ➡️ Next Topic Suggestion
**M02. How React Native Works (Bridge vs New Architecture — JSI, Fabric, TurboModules)** — Before optimizing a React Native app, understand what's under the hood: threads, the old bridge, and the New Architecture that replaced it.
