# M09. API Design for Mobile (Payload, Versioning, Backward Compatibility)
# हिंदी में: Mobile के लिए API Design — ऐसे API बनाना जो फ़ोन के लिए हल्के और तेज़ हों (कम requests, छोटा payload), और जिनमें बदलाव करने पर भी सालों पुराने app versions न टूटें (versioning + backward compatibility + force update)

---

## 🔵 Simple Definition (English)
Mobile clients differ from web in one crucial way: **you can't update them instantly**. App-store releases take days, users update slowly, and **old versions stay in the wild for months or years**. A mobile API must therefore be:
- **Efficient**: screen-shaped responses (BFF/GraphQL), minimal fields, pagination, delta sync, compression, device-appropriate media URLs.
- **Resilient**: idempotent writes, consistent error codes, partial-failure tolerance.
- **Backward compatible**: only **additive changes** to existing contracts; clients act as **tolerant readers** (ignore unknown fields, handle unknown enum values); breaking changes go to **new versions** (`/v2`, header or date-based versions) with **deprecation** windows.
- **Version-aware**: clients send `X-App-Version`/platform, and the server can adapt responses, enable features, or require a **soft/force update** (`426 Upgrade Required` or remote config min version).
- **Evolvable without releases**: **remote config, feature flags and server-driven UI**, with safe fallbacks.

## 🔵 सरल परिभाषा (Hindi)
Mobile ऐप को तुरंत update नहीं कर सकते — store release में दिन लगते हैं, यूज़र देर से update करते हैं, पुराने versions सालों चलते हैं। इसलिए mobile API होनी चाहिए: हल्की (स्क्रीन जैसा जवाब, कम fields, pagination, delta sync, compression), मज़बूत (idempotent writes, साफ़ error codes), backward compatible (सिर्फ़ नई चीज़ें जोड़ो, client अनजान fields/enum को नज़रअंदाज़ करे, बड़े बदलाव नए version में), version जानने वाली (app version header, ज़रूरत पर force update), और बिना release बदलने लायक (remote config, flags, server-driven UI)।

---

## 🔴 Problem it Solves
Classic failures:
- A backend developer **renames `price` to `amount`**, and every app version older than today crashes or shows ₹0. You can't hotfix those apps.
- A new enum value `status: "OUT_FOR_DELIVERY_DRONE"` arrives, and old apps' `switch` statements crash.
- The home screen makes **8 calls** returning 300 KB of JSON for 20 cards: slow on 3G and costly on data packs.
- A **critical security fix** needs users off v3.x, but there's no mechanism to force an update.
- Each team adds fields ad hoc, payloads bloat and **contracts drift** between iOS, Android and web.
Good mobile API design keeps **apps fast and every shipped version working**.

## 🔴 यह क्यों बना? (Hindi)
आम ग़लतियाँ: backend में `price` का नाम `amount` किया — आज से पुराने सारे ऐप crash या ₹0 दिखाएँ, और उन्हें तुरंत ठीक नहीं कर सकते; नया enum मान आया तो पुराने ऐप का switch crash; home screen 8 calls में 300 KB JSON (3G पर धीमा, data महँगा); security fix के लिए v3.x हटाना है पर force update का तरीका नहीं; हर टीम अपने fields जोड़ती है, iOS/Android/web के contract बिखरते हैं।
अच्छा mobile API design = ऐप तेज़ और हर पुराना version भी चालू।

---

## 🟢 How it Works — Step by Step

### Payload design for phones

```
✅ Screen-shaped endpoints via BFF: GET /mobile/v1/home → everything the home screen needs (1 RTT)
✅ Only needed fields; avoid deep nested objects nobody renders; ids + small embedded summaries
✅ Cursor pagination (limit 20–50), "hasMore", stable ordering
✅ Delta sync for lists the app stores locally (since=cursor → changes + tombstones)
✅ Media: return URL templates or sized URLs (img: ".../42.jpg?w={w}") + width/height + blurhash
✅ Money as integer minor units + currency: { amount: 14999, currency: "INR" } (₹149.99) — no floats
✅ Timestamps ISO 8601 UTC ("2026-10-18T09:30:00Z"); client formats in local time zone
✅ Localized strings when server-driven (Accept-Language), or keys for client-side i18n
✅ Compression (gzip/brotli); consider protobuf for very chatty/real-time traffic
❌ Don't send server-internal fields (DB ids of other tables, debug info, PII not needed)
```

### Backward-compatibility rules (the "never break old apps" checklist)

```
SAFE (additive):                              BREAKING (needs new version):
+ add optional response fields                ✗ remove or rename a field
+ add new endpoints                           ✗ change a field's type/meaning/units (₹ → paise)
+ add optional request params w/ defaults     ✗ make an optional request field required
+ add enum values ONLY if clients handle      ✗ change error codes/status semantics
  unknown values (design for it from v1!)     ✗ change pagination/ordering semantics
+ add new widget types in SDUI (old apps      ✗ change auth flow without compat window
  skip unknown types)
Client side (tolerant reader): ignore unknown JSON fields, default missing ones, map unknown enums to
"UNKNOWN" with a generic UI, never crash on parse → log and degrade gracefully
```

### Versioning strategies

```
URL major version:   /mobile/v1/home, /mobile/v2/home     → simple, explicit, cache-friendly ⭐ common
Header version:      Accept: application/vnd.quickbite.v2+json   or  API-Version: 2026-10-01
Date-based (Stripe): account/client pinned to a version date; server transforms responses per version
App-version aware:   X-App-Version: 5.12.0, X-Platform: android → server tailors (e.g., only send new
                     widget to ≥ 5.10)
GraphQL: single evolving schema, @deprecated fields, never remove until usage ≈ 0 (field usage analytics)
Keep N previous versions alive; measure traffic per version; sunset with notice
```

### Update control: soft & force update

```
Remote config (fetched at startup, cached):
  { "minSupportedVersion": "5.0.0", "latestVersion": "5.14.0", "softUpdateBelow": "5.10.0" }
App start: if app < minSupported → blocking "Update required" screen (store link)
           else if app < softUpdateBelow → dismissible "New version available"
Server safety net: middleware returns 426 Upgrade Required for too-old versions on critical endpoints
Use force update rarely (security, legal, breaking backend migrations) — it hurts users on low storage
React Native: OTA updates (M17) can fix JS-only issues without the store, within store policy limits
```

### Server-driven UI (SDUI)

```
Server returns layout as typed components:
{ "screen": "home", "sections": [
   { "type": "BANNER_CAROUSEL", "id": "b1", "items": [...] },
   { "type": "CUISINE_GRID", "id": "c1", "items": [...] },
   { "type": "RESTAURANT_LIST", "id": "r1", "title": "Top picks", "items": [...], "action": { "type": "DEEPLINK", "url": "quickbite://collection/top" } } ] }
+ Change layout, ordering, A/B tests, festival themes without app releases
- Old apps must skip unknown section types; keep schemas versioned; limit logic in the payload
```

### Errors & idempotency

```
Consistent error envelope: { "error": { "code": "ITEM_UNAVAILABLE", "message": "…", "retryable": false,
                                        "details": {...}, "requestId": "req_…" } }
Client logic keys off stable "code", not message text; message is localized & user-displayable
All mutating endpoints accept Idempotency-Key (retries are normal on mobile)
Partial failure in aggregated responses: return what's available + "errors" per section (don't 500 the
whole home screen because "offers" timed out)
```

### Contract governance

```
OpenAPI/GraphQL schema as source of truth → codegen for Swift/Kotlin/TS clients
Contract tests (Pact / schema diff in CI) → block PRs that remove/rename fields used by live versions
Field-level usage telemetry per app version → know when it's safe to remove
```

## 🟢 कैसे काम करता है? (Hindi)
1. फ़ोन के लिए payload: BFF से एक call में पूरी screen, सिर्फ़ ज़रूरी fields, cursor pagination, delta sync, image के sized URL + width/height + blurhash, पैसा पूरे पैसे (paise) में integer + currency, समय UTC ISO में, compression।
2. Backward compatibility: सिर्फ़ जोड़ो (नए optional fields, नए endpoints); नाम बदलना/हटाना/type बदलना = नया version; client अनजान fields छोड़े, अनजान enum को "UNKNOWN" मानकर साधारण UI दिखाए, कभी crash नहीं।
3. Versioning: URL में `/v1`, `/v2` (सबसे आम) या header/date-based (Stripe); `X-App-Version` से सर्वर हर version के हिसाब से जवाब दे; हर version का traffic नापो और सूचना देकर बंद करो।
4. Update नियंत्रण: remote config में minSupported/softUpdate; बहुत पुराना ऐप → "Update ज़रूरी" screen, थोड़ा पुराना → "नया version" सुझाव; सर्वर से 426; force update कम से कम; JS-only fix के लिए OTA।
5. Server-driven UI से बिना release बदलाव (अनजान section पुराने ऐप छोड़ दें); errors का एक format (`code` पर logic), हर write पर Idempotency-Key, एक हिस्सा fail हो तो पूरी screen नहीं; OpenAPI codegen + contract tests।

---

## 🟡 Real World Example

**Stripe** — date-based API versioning. Each account is pinned to the version it integrated with, and the server applies compatibility transformations, so old integrations never break while the API evolves.

**Airbnb (Ghost Platform), Lyft, Swiggy/Zomato-style home feeds** — server-driven UI systems where the backend sends typed sections and the apps render them, enabling layout changes, experiments and festival campaigns without app releases. Unknown types are skipped by older apps.

**Facebook / Instagram GraphQL with persisted queries** — mobile apps ship pre-registered query IDs. The server knows exactly which fields each app version uses, so the schema can evolve and removal of unused fields is safe.

**Force-update in Indian fintech/UPI apps** — regulatory or security changes (new NPCI/RBI requirements, SDK updates) often require minimum versions, enforced with blocking update screens driven by remote config.

## 🟡 Real Example Hindi में
Stripe date-based versioning करता है — हर account उसी version पर पिन रहता है जिससे उसने जोड़ा था, सर्वर पुराने के लिए जवाब बदल देता है, इसलिए पुराने integrations कभी नहीं टूटते।
Airbnb, Lyft, Swiggy/Zomato जैसे home feeds server-driven UI से बिना release layout और festival campaigns बदलते हैं; भारतीय UPI/fintech ऐप RBI/NPCI नियम या security बदलाव पर remote config से minimum version लागू करते हैं।

---

## 🟠 My Stack Example

### BFF endpoint with version awareness, partial failure, sized media (Node/Express)
```js
app.get('/mobile/v1/home', auth, appVersion, async (req, res) => {
  const v = req.appVersion;                                         // from X-App-Version
  const sections = await Promise.allSettled([
    promo.banners(req.city), catalog.cuisines(req.city), catalog.topPicks(req.user.id, req.loc),
    semver.gte(v, '5.10.0') ? offers.flashDeals(req.city) : Promise.resolve(null),   // new widget only for new apps
  ]);
  const [banners, cuisines, picks, deals] = sections.map((s) => (s.status === 'fulfilled' ? s.value : null));
  res.set('Cache-Control', 'private, no-cache');
  res.json({
    sections: [
      banners && { type: 'BANNER_CAROUSEL', id: 'banners', items: banners.map((b) => ({ id: b.id, image: media(b.image), deeplink: b.link })) },
      cuisines && { type: 'CUISINE_GRID', id: 'cuisines', items: cuisines },
      deals && { type: 'FLASH_DEALS', id: 'deals', endsAt: deals.endsAt, items: deals.items },
      picks && { type: 'RESTAURANT_LIST', id: 'picks', title: t(req, 'home.topPicks'),
        items: picks.map((r) => ({ id: r.id, name: r.name, etaMin: r.eta, rating: r.rating,
          costForTwo: { amount: r.costForTwoPaise, currency: 'INR' }, image: media(r.image) })) },
    ].filter(Boolean),
    errors: sections.filter((s) => s.status === 'rejected').length ? ['PARTIAL'] : [],
  });
});
const media = (img) => ({ urlTemplate: `${CDN}/${img.key}?w={w}&fm=webp`, width: img.w, height: img.h, blurhash: img.blurhash });
```

### Tolerant reader on the client (zod with safe defaults & unknown handling)
```ts
import { z } from 'zod';
const Money = z.object({ amount: z.number().int(), currency: z.string().default('INR') });
const OrderStatus = z.enum(['PLACED', 'ACCEPTED', 'PICKED_UP', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED'])
  .or(z.string().transform(() => 'UNKNOWN' as const));                 // unknown future values don't crash
const Order = z.object({ id: z.string(), status: OrderStatus, total: Money, etaMin: z.number().optional() })
  .passthrough();                                                       // ignore extra fields
export const parseOrder = (json: unknown) => {
  const r = Order.safeParse(json);
  if (!r.success) { Sentry.captureMessage('order_parse_failed', { extra: { issues: r.error.issues } }); return null; }
  return r.data;
};
```
```tsx
// Server-driven sections: skip unknown types (old apps stay safe)
const registry: Record<string, React.ComponentType<any>> = { BANNER_CAROUSEL: BannerCarousel, CUISINE_GRID: CuisineGrid, RESTAURANT_LIST: RestaurantList, FLASH_DEALS: FlashDeals };
export const Home = ({ sections }: { sections: Section[] }) => (
  <FlashList data={sections.filter((s) => registry[s.type])} keyExtractor={(s) => s.id}
             renderItem={({ item }) => { const C = registry[item.type]; return <C {...item} />; }} />
);
```

### Force / soft update check at startup
```ts
export async function checkAppVersion() {
  const cfg = await remoteConfig.get();                        // cached last-known values if offline
  const current = Application.nativeApplicationVersion!;      // expo-application
  if (semverLt(current, cfg.minSupportedVersion)) return router.replace('/force-update');
  if (semverLt(current, cfg.softUpdateBelow) && !kv.getBoolean(`softUpdateDismissed:${cfg.latestVersion}`)) showSoftUpdateSheet(cfg);
}
```
```python
# FastAPI safety net for critical endpoints
@app.middleware("http")
async def min_version(request: Request, call_next):
    v = request.headers.get("x-app-version", "0.0.0")
    if request.url.path.startswith("/mobile/") and Version(v) < Version(settings.MIN_SUPPORTED):
        return JSONResponse(status_code=426, content={"error": {"code": "UPGRADE_REQUIRED", "message": "Please update the app"}})
    return await call_next(request)
```

### CI: block breaking schema changes
```yaml
- name: OpenAPI breaking-change check
  run: npx oasdiff breaking origin/main:openapi.yaml openapi.yaml --fail-on ERR
```

---

## ⚫ Interview Questions + Answers

**Q1: Why is backward compatibility more critical for mobile APIs than web APIs?**
A1: A web frontend is redeployed with the backend and users get the new code on refresh. Mobile apps are installed binaries updated through app stores with review delays, many users update slowly or never (auto-update off, low storage), and older versions persist for months or years. Any breaking API change instantly breaks all those installed versions, and you can't hotfix them. Mobile APIs must therefore evolve additively, version breaking changes, and offer force-update mechanisms.

**Q2: Which API changes are safe vs breaking?**
A2: Safe changes are additive: new optional response fields, new endpoints, new optional request parameters with defaults, and new enum values or widget types only if clients were built to handle unknowns. Breaking changes: removing or renaming fields, changing types, units or meaning, making optional inputs required, changing error codes or status semantics, altering pagination or ordering behaviour, and changing auth flows without a compatibility period. Breaking changes need a new version and a deprecation window, measured by per-version usage.

**Q3: How would you design the home screen API for a food delivery app?**
A3: A single BFF endpoint returning the screen as typed sections (banners, cuisines, offers, restaurant lists) with only the fields each card renders. Images come as size-templated CDN URLs with dimensions and blurhash, money as integer paise plus currency, and timestamps in UTC. Aggregation runs internally in parallel with timeouts and returns partial results when non-critical services fail. The endpoint is version-aware (new widget types only for supporting app versions), has cursor-paginated lists for "load more", and caching hints. Old apps skip unknown section types.

**Q4: How do you implement force update safely?**
A4: Keep `minSupportedVersion` and soft-update thresholds in remote config, fetched at startup with cached values for offline use. Below the minimum, block with an update screen linking to the store (Play in-app updates API on Android). Below the soft threshold, show a dismissible prompt. Add a server-side safety net that returns 426 on critical endpoints for unsupported versions, and make sure the update screen itself works offline. Use force update sparingly, communicate why, and monitor version adoption. For JS-only fixes in React Native, consider OTA updates instead.

**Q5: What is a tolerant reader and why does it matter?**
A5: A tolerant reader is a client that parses only what it needs and tolerates changes. It ignores unknown fields, provides defaults for missing optional fields, maps unknown enum values to a safe fallback, and logs rather than crashes on unexpected data. It lets the server evolve additively without breaking clients. It must be designed in from version 1, because you can't retrofit tolerance into apps already in users' hands.

---

## 🔷 Trade-offs
✅ BFF/screen-shaped APIs: fast mobile UX — ❌ more backend endpoints to maintain per client.
✅ URL versioning: explicit & simple — ❌ duplicated code across versions; maintain multiple.
✅ Server-driven UI: ship changes without releases — ❌ complex schema, less native flexibility, testing combos.
✅ Force update: removes old versions quickly — ❌ friction, user churn if overused.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Backward compatibility | Old clients keep working | पुराने ऐप भी चलें |
| Additive change | Only adding, never removing | सिर्फ़ जोड़ना |
| Breaking change | Change that breaks clients | ऐप तोड़ने वाला बदलाव |
| Tolerant reader | Client ignoring unknowns | अनजान चीज़ें छोड़ने वाला client |
| API versioning | Managing contract versions | API के versions |
| Deprecation | Marking for future removal | भविष्य में हटाने की सूचना |
| Force update | Block until app updated | update के बिना रोकना |
| Remote config | Server-controlled app settings | सर्वर से app settings |
| Server-driven UI | Server defines screen layout | सर्वर तय करे screen |
| Minor units | Money in paise/cents integers | पैसे integer में |

---

## ⚡ 3-Line Summary
**English:**
1. Mobile APIs must be lean (screen-shaped, minimal fields, pagination, delta sync, sized media, compression) and resilient (idempotency, error codes, partial results).
2. Never break shipped apps: additive changes only, tolerant readers, new versions for breaking changes, per-version usage tracking and deprecation.
3. Control evolution: app-version headers, remote config for soft/force update (+ 426 safety net), feature flags and server-driven UI with safe fallbacks.

**Hindi:**
1. Mobile API हल्की (स्क्रीन जैसी, कम fields, pagination, delta, compression) और मज़बूत (idempotency, error codes, आंशिक जवाब)।
2. पुराने ऐप कभी न टूटें: सिर्फ़ जोड़ो, tolerant reader, बड़े बदलाव नए version में, हर version का इस्तेमाल नापो।
3. App version header, remote config से soft/force update, flags और server-driven UI सुरक्षित fallback के साथ।

---

## ➡️ Next Topic Suggestion
**M10. Push Notifications (FCM + APNs)** — When the app is closed, push is the only way to reach the user. Next: how FCM and APNs work, token management, notification vs data messages, and designing a reliable push pipeline.
