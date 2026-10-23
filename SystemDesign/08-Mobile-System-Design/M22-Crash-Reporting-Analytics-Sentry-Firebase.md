# M22. Crash Reporting + Analytics (Sentry, Firebase)
# हिंदी में: Crash Reporting + Analytics — असली यूज़र्स के फ़ोन पर ऐप कहाँ crash या अटक (ANR) रहा है उसकी पूरी जानकारी पाना, और यूज़र ऐप में क्या करते हैं (events, funnels, retention) यह नापना — निजता का ध्यान रखते हुए

---

## 🔵 Simple Definition (English)
Two kinds of field telemetry every mobile app needs:
1. **Crash & stability reporting**: capture and group failures in production.
   - **JS exceptions** (React Native), **native crashes** (iOS signals/NSException, Android Java/Kotlin/NDK), **ANRs** (Android "App Not Responding", main thread blocked ≥ 5 s), **iOS hangs/watchdog kills**, **OOM terminations**.
   - Reports are **symbolicated** (JS source maps, iOS dSYMs, Android R8/ProGuard mappings and NDK symbols) and come with **breadcrumbs** and context (device, OS, app version/build, OTA update ID, user ID hash, screen).
   - Tools: **Sentry**, **Firebase Crashlytics**, Bugsnag, Embrace. Key metrics: **crash-free users/sessions**, **ANR rate**, by version, device and OS.
2. **Product analytics**: record **events** ("restaurant_viewed", "cart_item_added", "order_placed") with properties to understand behaviour.
   - Analyses: **funnels, retention cohorts, feature adoption, A/B test results, attribution**.
   - Tools: **Firebase Analytics/GA4**, Amplitude, Mixpanel, **CleverTap** and **MoEngage** (popular in India), and CDPs like Segment/**RudderStack**, or an in-house pipeline (Kafka → ClickHouse/BigQuery).
Both must be **batched, offline-tolerant, privacy-safe (consent, no PII, DPDP Act / ATT)** and must not slow the app.

## 🔵 सरल परिभाषा (Hindi)
हर mobile ऐप को दो तरह की field जानकारी चाहिए: (1) Crash/stability — JS errors, native crashes, Android ANR (main thread 5 सेकंड से ज़्यादा अटका), iOS hangs, memory से बंद होना; source maps/dSYM/R8 mapping से असली line, breadcrumbs (crash से पहले क्या हुआ) और context (device, OS, version, OTA update); मुख्य नाप crash-free users/sessions और ANR rate — Sentry, Crashlytics।
(2) Product analytics — events ("cart_item_added", "order_placed") से funnels, retention, feature इस्तेमाल, A/B नतीजे — Firebase/GA4, Amplitude, Mixpanel, CleverTap, MoEngage। दोनों batch में, offline में भी, निजता के साथ (सहमति, PII नहीं, DPDP Act/ATT)।

---

## 🔴 Problem it Solves
- You can't attach a debugger to millions of phones. Without crash reporting, you learn about crashes from **1-star reviews** ("app crashes on payment!!") with no stack trace, device or version info.
- **ANRs and crashes hurt store ranking**: Google Play's bad-behaviour thresholds are a user-perceived crash rate above ~1.09% and ANR rate above ~0.47%.
- **Minified/bytecode stack traces** are unreadable without symbolication.
- Product teams make **blind decisions** without analytics: where do users drop off between cart and payment? Did the new checkout increase orders in Tier-2 cities? What's D7 retention for users acquired via a referral campaign?
- Badly built analytics **leaks PII**, **drains battery** (one request per event), **loses events offline**, or produces **inconsistent event names** nobody trusts.

## 🔴 यह क्यों बना? (Hindi)
लाखों फ़ोन पर debugger नहीं लगा सकते — crash reporting के बिना crash का पता 1-star reviews से चलता है ("payment पर crash!!"), बिना stack trace, device या version के। ANR और crashes Play Store ranking गिराते हैं (crash ~1.09%, ANR ~0.47% की सीमा); minified stack trace बिना symbolication के पढ़ा नहीं जाता।
Analytics के बिना product फ़ैसले अंधेरे में: cart से payment के बीच यूज़र कहाँ छोड़ते हैं? नया checkout Tier-2 शहरों में orders बढ़ाया? ख़राब analytics PII लीक करे, battery खाए, offline events खो दे, या events के नाम ऐसे कि कोई भरोसा न करे।

---

## 🟢 How it Works — Step by Step

### Crash reporting pipeline

```
On device:
  JS: ErrorUtils global handler / Sentry RN integration → capture exception + JS stack
  Native: signal/exception handlers (iOS: PLCrashReporter-style; Android: UncaughtExceptionHandler, NDK)
          → write report to disk immediately (process is dying) → send on NEXT launch
  ANR: Android watchdog (main thread blocked) → ANR report; iOS: hang detection (main thread > 2 s)
  OOM: no crash callback → inferred on next launch (app died in foreground without crash/clean exit)
  Context attached: release, build, updateId (OTA), device model, OS, memory, battery, network,
                    screen/route, user id (hashed), feature flags, breadcrumbs (last ~100 events:
                    navigation, taps, HTTP calls with status, console warnings)
Server side (Sentry/Crashlytics):
  symbolicate using uploaded artifacts per release:
     JS: Hermes bytecode → source maps (composed packager + Hermes maps)
     iOS: dSYM files      Android: R8/ProGuard mapping.txt + NDK .so symbols
  → group by fingerprint (stack frames) → issues → alert on new/regressed issues per release
  → release health dashboards: crash-free users %, crash-free sessions %, ANR rate, adoption
```

### What "good" looks like

```
Crash-free users ≥ 99.5% (good), ≥ 99.9% (excellent) | ANR rate < 0.47% (Play threshold) | startup p90 budget
Triage loop: new issue alert → owner (CODEOWNERS / screen ownership) → severity by users affected & flow
(checkout > profile) → fix (OTA if JS) → verify crash-free recovers on next update/release
```

### Product analytics: event design

```
Naming: object_action in snake_case → restaurant_viewed, dish_added_to_cart, coupon_applied,
        checkout_started, payment_failed, order_placed, order_delivered
Properties: { restaurant_id, dish_id, price_paise, city, source: "search|home|deeplink", position, experiment_variant }
Identity: anonymous_id (device install) → user_id after login (alias/merge); never phone/email as properties
Super properties: app_version, platform, os_version, locale, network_type, session_id
Tracking plan: a typed schema (TS types / JSON schema) reviewed like an API → consistent across iOS/Android/web
Avoid: free-text event names, PII (phone, address, names), high-cardinality junk properties
```

### Client SDK behaviour (efficiency & reliability)

```
- Buffer in memory + persist (MMKV/SQLite) → flush every 30 s / 20 events / on background (M08)
- Offline: keep queue (cap size, e.g., 1,000 events), send when online; events carry client timestamp + id
- Dedupe by event id on server; tolerate clock skew (server receive time too)
- Sampling for high-volume low-value events (scroll, impressions) → aggregate client-side (e.g., impressions batch)
- Respect consent: no tracking until consent where required; kill switch via remote config
```

### Analyses you should mention

```
Funnels: home → restaurant_viewed → dish_added_to_cart → checkout_started → payment_success (drop-off per step,
         segmented by city tier, device, app version, network)
Retention: D1/D7/D30 cohorts by acquisition channel
Feature adoption & A/B tests: exposure + metric events (F22)
Performance analytics: screen load time, API latency by network type
Attribution: install source (Play Install Referrer, SKAdNetwork/AdAttributionKit on iOS)
```

### Privacy & compliance

```
India DPDP Act 2023: consent, purpose limitation, data minimization, user rights (access/erasure)
iOS App Tracking Transparency: IDFA only with permission; App Store privacy "nutrition labels"
Google Play Data safety form: declare what you collect & why
Scrub PII in crash reports (beforeSend), mask screenshots/replays, hash user ids, set retention periods,
support "delete my data" across analytics vendors
```

## 🟢 कैसे काम करता है? (Hindi)
1. Device पर: JS errors global handler से, native crashes signal/exception handlers से (रिपोर्ट तुरंत disk पर, अगली बार खुलने पर भेजी जाती है), Android ANR watchdog से, iOS hangs, और OOM का अंदाज़ा अगले launch पर; साथ में version, build, OTA updateId, device, OS, screen, breadcrumbs।
2. सर्वर पर symbolication: Hermes source maps, iOS dSYM, Android R8 mapping (हर release पर CI से upload); stack से group होकर issues बनते हैं; नई/वापस आई issue पर alert; dashboards में crash-free users %, ANR rate।
3. लक्ष्य: crash-free users ≥ 99.5% (बेहतरीन 99.9%), ANR < 0.47%; triage — owner तय, ज़रूरी flow (checkout) पहले, JS fix OTA से।
4. Analytics events: `object_action` नाम (dish_added_to_cart), properties (id, price_paise, city, source), anonymous id → login के बाद user id, typed tracking plan; phone/पता/नाम जैसी PII कभी नहीं।
5. SDK: buffer + persist, हर 30 सेकंड/20 events/background पर batch, offline queue, event id से dedupe, ज़्यादा volume वाले events का sampling; निजता — DPDP सहमति, iOS ATT, Play Data safety, crash reports में PII साफ़, "मेरा डेटा मिटाओ" का समर्थन।

---

## 🟡 Real World Example

**Firebase Crashlytics** — the most widely used free crash reporter on Android and iOS (Fabric was acquired by Google in 2017), with real-time crash alerts, velocity alerts and integration with Play vitals. Many Indian apps use it alongside Firebase Analytics and Remote Config.

**Sentry** — popular with React Native teams for symbolicated JS and native stack traces, release health (crash-free sessions per release or OTA update), breadcrumbs and performance tracing. Companies like Discord have described using Sentry for client error monitoring.

**CleverTap and MoEngage (Indian companies)** — customer engagement and analytics platforms (funnels, cohorts, segmentation, push and in-app campaigns) used by many Indian consumer apps across food delivery, fintech, OTT and e-commerce. **RudderStack** (Indian-founded) is an open-source CDP that routes events to warehouses and tools.

**Play Console Android vitals** — Google surfaces user-perceived crash and ANR rates. Exceeding bad-behaviour thresholds can reduce an app's visibility on Play, so stability is a growth metric, not just an engineering one.

## 🟡 Real Example Hindi में
Firebase Crashlytics Android/iOS पर सबसे ज़्यादा इस्तेमाल होने वाला मुफ़्त crash reporter है (2017 में Google ने Fabric ख़रीदा); Sentry RN टीमों में लोकप्रिय — symbolicated stack traces, हर release/OTA update का crash-free %।
CleverTap और MoEngage (भारतीय कंपनियाँ) कई भारतीय ऐप्स के funnels, cohorts और push campaigns चलाते हैं; RudderStack (भारतीय संस्थापकों का) open-source CDP है; Play Console में crash/ANR सीमा पार होने पर ऐप का दिखना कम हो सकता है — stability भी growth metric है।

---

## 🟠 My Stack Example

### Sentry for React Native (Expo): crashes, ANRs, release health, PII scrubbing
```ts
// src/shared/sentry.ts
import * as Sentry from '@sentry/react-native';
import * as Updates from 'expo-updates';
import * as Application from 'expo-application';

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,                      // DSN is public by design
  release: `in.quickbite.app@${Application.nativeApplicationVersion}+${Application.nativeBuildVersion}`,
  dist: Updates.updateId ?? 'embedded',                         // separate OTA updates within a binary
  environment: process.env.EXPO_PUBLIC_APP_ENV,
  tracesSampleRate: 0.1,
  enableAutoSessionTracking: true,                               // crash-free sessions/users
  enableAppHangTracking: true, appHangTimeoutInterval: 2,        // iOS hangs
  enableNativeFramesTracking: true,                              // slow/frozen frames
  beforeSend(event) {
    if (event.user) event.user = { id: event.user.id };          // drop email/phone/ip
    event.breadcrumbs = event.breadcrumbs?.map((b) => (b.category === 'http' ? { ...b, data: { ...b.data, url: stripQuery(b.data?.url) } } : b));
    return event;
  },
});
Sentry.setTag('updateId', Updates.updateId ?? 'embedded');
export const setUserForTelemetry = (userId: string) => Sentry.setUser({ id: hash(userId) });
```
```json
// app.json — Sentry Expo plugin uploads source maps & native debug files during EAS Build
{ "expo": { "plugins": [["@sentry/react-native/expo", { "organization": "quickbite", "project": "mobile" }]] } }
```

### Breadcrumbs for critical flows
```ts
Sentry.addBreadcrumb({ category: 'checkout', message: 'payment_initiated', data: { method: 'UPI', amountPaise: 24900 }, level: 'info' });
try { await payments.initiate(order); }
catch (e) { Sentry.captureException(e, { tags: { flow: 'checkout', step: 'payment_initiate' } }); throw e; }
```

### Typed analytics tracking plan + batched sender
```ts
// packages/analytics/events.ts — one schema for iOS, Android, web
export type Events = {
  restaurant_viewed: { restaurant_id: string; source: 'home' | 'search' | 'deeplink'; position?: number };
  dish_added_to_cart: { restaurant_id: string; dish_id: string; price_paise: number; qty: number };
  checkout_started: { cart_value_paise: number; items: number };
  payment_failed: { method: 'UPI' | 'CARD' | 'COD'; reason_code: string };
  order_placed: { order_id: string; value_paise: number; coupon?: string };
};
export function track<E extends keyof Events>(name: E, props: Events[E]) {
  enqueue({ id: uuid(), name, props, ts: Date.now(), ctx: superProps() });   // batched + persisted (M08)
}
// usage — compile-time checked; no PII fields exist in the schema
track('dish_added_to_cart', { restaurant_id: 'r42', dish_id: 'd9', price_paise: 24900, qty: 1 });
```

### Event ingestion → warehouse (FastAPI → Kafka → ClickHouse)
```python
@app.post("/events/batch", status_code=202)
async def ingest(events: list[dict], request: Request):
    now = datetime.utcnow().isoformat()
    for e in events[:500]:
        if e.get("name") not in ALLOWED_EVENTS: continue                   # schema governance
        e["received_at"] = now; e["ip_country"] = geo_country(request.client.host)   # no raw IP stored
        await kafka.send("app-events", key=e["id"].encode(), value=json.dumps(e).encode())
```
```sql
-- Funnel: viewed → added → checkout → placed (last 7 days, by city tier)
SELECT city_tier,
  uniqIf(user_id, name='restaurant_viewed') AS viewed,
  uniqIf(user_id, name='dish_added_to_cart') AS added,
  uniqIf(user_id, name='checkout_started') AS checkout,
  uniqIf(user_id, name='order_placed') AS placed
FROM events WHERE ts > now() - INTERVAL 7 DAY GROUP BY city_tier;
```

### Consent gate
```ts
const consent = kv.getString('consent.analytics');          // 'granted' | 'denied' | undefined
export const analyticsEnabled = () => consent === 'granted' && remoteConfig.bool('analytics_enabled');
// iOS ATT (only if you use IDFA for cross-app tracking/ads attribution):
// import { requestTrackingPermissionsAsync } from 'expo-tracking-transparency';
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you set up crash reporting for a React Native app?**
A1: Integrate an SDK (Sentry or Crashlytics) that captures JS exceptions, native crashes, ANRs and hangs, persists reports immediately and uploads them on the next launch. Tag every event with release, build, OTA update ID, environment, device and OS, plus hashed user IDs and breadcrumbs. Upload symbolication artifacts per build in CI (Hermes source maps, iOS dSYMs, Android R8 mappings and NDK symbols). Scrub PII in `beforeSend`. Track release health (crash-free users and sessions, ANR rate), alert on new or regressed issues, route them to owners and gate rollouts on these metrics.

**Q2: What's an ANR and how do you reduce it?**
A2: An ANR (Application Not Responding) occurs on Android when the main thread is blocked long enough that the app can't respond to input (about 5 s for input dispatch) or a broadcast receiver or service doesn't finish in time. Causes include disk or network I/O on the main thread, heavy synchronous native work, lock contention, slow SDK initialization at startup and huge layouts. Reduce them by moving I/O and heavy work to background threads, lazy-initializing SDKs, avoiding synchronous main-thread storage on large data, profiling with StrictMode and Perfetto, and monitoring ANR clusters in Play vitals and your crash tool.

**Q3: How do you design product analytics events?**
A3: Define a tracking plan as a typed schema shared across platforms, with consistent `object_action` event names, well-defined properties (IDs, amounts in minor units, source, position, experiment variant) and global context (app version, platform, locale, network). Use an anonymous ID merged with the user ID after login. Never include PII. Govern changes like API changes (reviews, versioning) and validate events server-side against the schema. Batch, persist and dedupe events, and design dashboards for funnels, retention and experiment analysis.

**Q4: How do you avoid analytics hurting performance or battery?**
A4: Buffer events in memory, persist them to fast storage, and flush in batches on time or size thresholds and when backgrounded rather than per event. Compress payloads and piggyback on existing network activity where possible. Sample or aggregate high-frequency events like impressions and scrolls. Initialize SDKs lazily after the first screen, limit the number of third-party SDKs, and cap offline queue sizes. Provide a remote kill switch for misbehaving SDKs.

**Q5: What privacy obligations apply to mobile telemetry?**
A5: Collect only what you need for stated purposes, obtain consent where required (DPDP Act in India, GDPR in the EU), and respect platform rules (iOS App Tracking Transparency for IDFA and cross-app tracking, App Store privacy labels, Play Data safety declarations). Exclude PII from events and crash reports, hash identifiers, mask session replays, set retention limits and support user deletion requests across vendors. Disclose third-party SDKs and their data use, and allow opt-out where applicable.

---

## 🔷 Trade-offs
✅ Rich crash context & breadcrumbs: fast debugging — ❌ privacy risk if not scrubbed; SDK overhead.
✅ Many analytics SDKs: marketing flexibility — ❌ app size, startup cost, data leakage risk → prefer one CDP routing server-side.
✅ In-house pipeline (Kafka → ClickHouse): control & cost at scale — ❌ build/maintain effort.
✅ Sampling: lower cost — ❌ less precision for rare events (never sample crashes/payments).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Crash-free users | % users without a crash | बिना crash वाले यूज़र % |
| ANR | Android App Not Responding | ऐप जवाब नहीं दे रहा |
| Symbolication | Map addresses to source lines | असली code line निकालना |
| dSYM | iOS debug symbols file | iOS debug symbols |
| R8/ProGuard mapping | Android obfuscation map | Android नाम-नक़्शा |
| Breadcrumbs | Events leading to an error | error से पहले के कदम |
| Release health | Stability per release | हर release की सेहत |
| Tracking plan | Defined event schema | events की तय सूची |
| Funnel | Step-by-step conversion analysis | क़दम-दर-क़दम conversion |
| Cohort retention | Return rate by user group | समूह के लौटने की दर |

---

## ⚡ 3-Line Summary
**English:**
1. Capture JS/native crashes, ANRs, hangs, OOMs with context + breadcrumbs; upload source maps/dSYMs/mappings per release; watch crash-free & ANR rates per version/OTA.
2. Analytics: typed tracking plan (object_action events, minor-unit amounts, no PII), anonymous→user identity, batched/persisted/deduped delivery, funnels/retention/experiments.
3. Keep it light and lawful: lazy SDK init, batching, sampling non-critical events, consent (DPDP/ATT), PII scrubbing, retention limits, deletion support.

**Hindi:**
1. JS/native crashes, ANR, hangs को context + breadcrumbs के साथ पकड़ो; हर release पर source maps/dSYM upload; crash-free और ANR rate देखो।
2. Analytics: typed events (object_action, paise में राशि, PII नहीं), batch + persist + dedupe, funnels और retention।
3. हल्का और क़ानूनी: SDK देर से init, batching, sampling, सहमति (DPDP/ATT), PII साफ़, डेटा मिटाने का समर्थन।

---

## ➡️ Next Topic Suggestion
**🎉 Mobile System Design complete!** Next: **P01. WhatsApp — mobile app + web + backend** in `09-FullStack-Design-Problems/`. Now combine everything (backend, web and mobile) into full end-to-end designs, starting with WhatsApp.
