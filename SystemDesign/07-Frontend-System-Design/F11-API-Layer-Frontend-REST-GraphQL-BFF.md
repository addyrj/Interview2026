# F11. API Layer for Frontend (REST vs GraphQL vs BFF)
# हिंदी में: Frontend का API Layer — UI और backend के बीच की परत: कौन-सा API style (REST, GraphQL, या UI के लिए ख़ास BFF), और client के अंदर API calls को एक जगह साफ़-सुथरे तरीके से (auth, retry, errors, types) कैसे रखें

---

## 🔵 Simple Definition (English)
The **frontend API layer** has two parts:
1. **Contract choice** (what the backend exposes to the UI):
   - **REST**: resource endpoints (`GET /restaurants/42/menu`), HTTP caching friendly, simple.
   - **GraphQL**: a single endpoint where the client asks for exactly the fields it needs, typed schema, one round trip for nested data.
   - **BFF (Backend-for-Frontend)**: a thin server per client type (web, mobile) that aggregates microservices and returns **screen-shaped** responses.
   - Also **tRPC/Server Actions** (TypeScript end-to-end, same repo), **gRPC-Web** (rare in browsers).
2. **Client-side API layer** (how the app calls it): one HTTP client module that handles base URL, auth headers and **token refresh**, timeouts, **retries with backoff**, error normalization, request IDs, **typed responses** (OpenAPI/GraphQL codegen) and cancellation. It is consumed by server-state hooks (F10).

## 🔵 सरल परिभाषा (Hindi)
Frontend API layer के दो हिस्से: (1) backend कैसा API देगा — REST (resource वाले URLs), GraphQL (client जितना माँगे उतना, एक request में), या BFF (web/mobile के लिए अलग छोटा सर्वर जो कई services से डेटा जोड़कर स्क्रीन के हिसाब से भेजे)।
(2) client के अंदर सारी API calls एक जगह — auth header, token refresh, timeout, retry, errors एक जैसे, TypeScript types — और फिर hooks इन्हें इस्तेमाल करें।

---

## 🔴 Problem it Solves
Without a deliberate API layer:
- **Over-fetching**: `/users/7` returns 60 fields when the card needs 3, wasting mobile data.
- **Under-fetching / waterfalls**: the home screen needs `/me`, `/banners`, `/restaurants`, `/offers` and `/cart`, so 5 round trips on 4G (~200–400 ms each).
- `fetch` calls scattered in components with **inconsistent auth, error handling and retries**.
- **Breaking changes** in backend fields crash old mobile app versions still in the wild.
- No types, so runtime `undefined` errors.

A good contract (REST, GraphQL or BFF chosen for the use case) plus a **single client API module** makes the UI faster, safer and easier to change.

## 🔴 यह क्यों बना? (Hindi)
बिना सोचे API layer के: ज़रूरत से ज़्यादा डेटा (60 fields जबकि 3 चाहिए), या कम डेटा जिसकी वजह से एक स्क्रीन के लिए 5 requests (4G पर हर एक 200–400 ms), components में बिखरे fetch जिनमें auth/error/retry अलग-अलग, backend field बदलने पर पुराने mobile app crash, और types नहीं।
सही contract (REST/GraphQL/BFF) + client में एक API module = तेज़, सुरक्षित, आसानी से बदलने लायक UI।

---

## 🟢 How it Works — Step by Step

### Contract options compared

```
┌─────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┐
│                 │ REST                     │ GraphQL                  │ BFF (REST/GraphQL)       │
├─────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ Shape           │ Server-defined resources │ Client picks fields      │ Screen-shaped, per client│
│ Round trips     │ Often many per screen    │ One query for nested data│ One per screen           │
│ HTTP caching    │ Easy (GET + CDN + ETag)  │ Harder (POST; use        │ Depends; can add caching │
│                 │                          │ persisted queries + GET) │                          │
│ Typing          │ OpenAPI → codegen        │ Schema → codegen (strong)│ Shared TS types/OpenAPI  │
│ Versioning      │ /v1, /v2 or headers      │ Evolve schema, deprecate │ Per-app releases         │
│ Over-fetch      │ Common                   │ Avoided                  │ Avoided (tailored)       │
│ Complexity      │ Low                      │ Server resolvers, N+1,   │ Extra service to own     │
│                 │                          │ query cost limits        │                          │
│ Best for        │ Public APIs, simple CRUD,│ Many clients, complex    │ Microservices backend +  │
│                 │ cacheable reads          │ nested UIs (social, e-   │ different web & mobile   │
│                 │                          │ commerce), fast iteration│ needs                    │
└─────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┘
```

### BFF aggregation for a mobile home screen

```
RN app ──GET /mobile/home──► Mobile BFF (Node/FastAPI)
                               ├─► user-svc      /me                    ┐
                               ├─► promo-svc     /banners?city=BLR      │ parallel
                               ├─► catalog-svc   /restaurants?near=...  │ (Promise.all, timeouts,
                               ├─► offers-svc    /offers                │  partial failure OK)
                               └─► cart-svc      /cart                  ┘
                             ◄── { user, banners, restaurants[20], offers, cartCount }  (trimmed fields,
                                  image URLs sized for device, feature flags applied)
1 round trip from phone (high latency) → N fast calls inside the data center (low latency)
```

### Client API module responsibilities

```
UI component → hook (useMenu) → api function (getMenu) → http client ──► network
                                                             │
          ┌──────────────────────────────────────────────────┘
          ▼
  - baseURL per env, timeout (e.g., 10 s)
  - Authorization header from secure store; refresh on 401 (single-flight: one refresh for many 401s)
  - Retry idempotent requests (GET, PUT, DELETE, POST with Idempotency-Key) on network/5xx with backoff+jitter
  - Normalize errors → { status, code, message, fieldErrors } for consistent UI handling
  - Request ID header (X-Request-Id) → trace in backend logs (Topic 102)
  - AbortSignal support (cancel on unmount / key change)
  - Typed responses + runtime validation at boundaries (zod) for critical data
  - App version header (X-App-Version) → backend can respond 426 "Upgrade required" (M18)
```

### Error contract (agree with backend)

```json
{ "error": { "code": "ITEM_OUT_OF_STOCK", "message": "Paneer Tikka is unavailable",
             "details": { "itemId": "it_42" }, "requestId": "req_9f2" } }
UI maps code → user-friendly text (i18n) and behaviour (retry? remove item? re-login?)
```

### Pagination, filtering, batching conventions

```
Cursor pagination for feeds: ?cursor=…&limit=20 → { items, nextCursor }      (Topic 39)
Sparse fieldsets (REST): ?fields=id,name,price ; expansions: ?include=author
Batch endpoints: POST /products:batchGet { ids: [...] } → avoid N requests
GraphQL: DataLoader on server batches N+1; persisted queries (hash → query) for caching & security
```

## 🟢 कैसे काम करता है? (Hindi)
1. REST: सरल, HTTP/CDN cache आसान, पर एक screen के लिए कई requests; GraphQL: client जितना माँगे उतना, एक query में nested डेटा, मज़बूत types — पर server पर N+1, cost limits, caching मुश्किल।
2. BFF: mobile/web के लिए अलग पतला सर्वर जो अंदर कई services को parallel call करके स्क्रीन जैसा जवाब देता है — फ़ोन से 1 request, data center के अंदर कई तेज़ requests।
3. Client में एक http module: base URL, timeout, auth header, 401 पर एक ही बार token refresh, retry (सिर्फ़ safe requests), errors एक format में, request ID, cancel।
4. Backend से error का तय format (`code`, `message`, `requestId`) — UI code के हिसाब से संदेश और कदम दिखाए।
5. Feed के लिए cursor pagination, ज़रूरी fields ही माँगो, कई ids के लिए batch endpoint; app version header से पुराने ऐप को "update करें" बताओ।

---

## 🟡 Real World Example

**Netflix** — runs device-specific API layers (originally a Groovy-scripted BFF per device, later GraphQL federation "Studio" and DGS) so TVs, phones and web each get tailored payloads from many microservices.

**Facebook / Instagram** — GraphQL was created at Facebook (2012) for the mobile News Feed, to fetch nested data in one round trip with exactly the needed fields, critical on mobile networks.

**Swiggy / Zomato-like apps** — home screens are commonly served by an aggregation layer ("widgets API") returning a list of typed widgets (banner carousel, restaurant list, offers). The mobile UI renders them generically, so the backend can rearrange the home screen without an app release (server-driven UI).

**Stripe** — the classic REST API: resource-oriented, versioned by date header, idempotency keys, expandable fields (`expand[]=customer`). The gold standard for public APIs.

## 🟡 Real Example Hindi में
Facebook ने 2012 में mobile News Feed के लिए GraphQL बनाया — एक request में nested डेटा, सिर्फ़ ज़रूरी fields। Netflix हर device (TV, फ़ोन, web) के लिए अलग API layer चलाता है।
Swiggy/Zomato जैसे ऐप का home screen अक्सर "widgets API" से आता है — backend तय करता है कौन-सा widget कहाँ, ऐप बस उन्हें दिखाता है (server-driven UI), बिना नए release के बदलाव। Stripe का REST API public APIs का आदर्श उदाहरण है।

---

## 🟠 My Stack Example

### Axios client with auth refresh (single-flight), retry, error normalization
```ts
// shared/http.ts — used by web (React/Next.js) and React Native
import axios, { AxiosError } from 'axios';
import { tokenStore } from './tokenStore';   // web: memory + httpOnly refresh cookie; RN: Keychain (F16/M16)

export const http = axios.create({ baseURL: process.env.NEXT_PUBLIC_API_URL, timeout: 10_000 });

http.interceptors.request.use((cfg) => {
  const token = tokenStore.getAccess();
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  cfg.headers['X-Request-Id'] = crypto.randomUUID();
  cfg.headers['X-App-Version'] = APP_VERSION;
  return cfg;
});

let refreshing: Promise<string> | null = null;           // single-flight refresh
http.interceptors.response.use(undefined, async (err: AxiosError) => {
  const cfg: any = err.config;
  if (err.response?.status === 401 && !cfg._retried) {
    cfg._retried = true;
    refreshing ??= tokenStore.refresh().finally(() => (refreshing = null));
    try { cfg.headers.Authorization = `Bearer ${await refreshing}`; return http(cfg); }
    catch { tokenStore.clear(); redirectToLogin(); }
  }
  const idempotent = ['get', 'put', 'delete'].includes(cfg?.method) || cfg?.headers?.['Idempotency-Key'];
  const retriable = !err.response || err.response.status >= 500 || err.response.status === 429;
  cfg._retryCount = (cfg._retryCount ?? 0) + 1;
  if (idempotent && retriable && cfg._retryCount <= 3) {
    const wait = Math.min(1000 * 2 ** cfg._retryCount, 8000) * (0.5 + Math.random() / 2);   // backoff + jitter
    await new Promise((r) => setTimeout(r, wait));
    return http(cfg);
  }
  throw toApiError(err);
});

export type ApiError = { status: number; code: string; message: string; requestId?: string };
function toApiError(err: AxiosError<any>): ApiError {
  const e = err.response?.data?.error;
  return { status: err.response?.status ?? 0, code: e?.code ?? (err.response ? 'UNKNOWN' : 'NETWORK'),
           message: e?.message ?? 'Something went wrong', requestId: e?.requestId };
}
```

### Typed endpoints from OpenAPI (FastAPI generates it for free)
```bash
# FastAPI serves /openapi.json → generate TS types for the frontend
npx openapi-typescript https://api.myapp.com/openapi.json -o src/shared/api-types.ts
```
```ts
import type { paths } from './api-types';
type Menu = paths['/restaurants/{id}/menu']['get']['responses']['200']['content']['application/json'];
export const getMenu = (id: string, signal?: AbortSignal) => http.get<Menu>(`/restaurants/${id}/menu`, { signal }).then((r) => r.data);
```

### Mobile BFF in Node (Express) — aggregate with timeouts + partial failure
```js
app.get('/mobile/home', auth, async (req, res) => {
  const city = req.query.city;
  const withTimeout = (p, ms, fallback) => Promise.race([p, new Promise((r) => setTimeout(() => r(fallback), ms))]).catch(() => fallback);
  const [user, banners, restaurants, offers, cart] = await Promise.all([
    withTimeout(userSvc.me(req.user.id), 300, null),
    withTimeout(promoSvc.banners(city), 300, []),                 // non-critical → fallback empty
    withTimeout(catalogSvc.nearby(req.query.lat, req.query.lng, 20), 800, []),
    withTimeout(offersSvc.forUser(req.user.id), 300, []),
    withTimeout(cartSvc.count(req.user.id), 300, 0),
  ]);
  res.set('Cache-Control', 'private, no-cache');
  res.json({
    widgets: [
      { type: 'BANNER_CAROUSEL', items: banners.map(b => ({ id: b.id, img: cdn(b.img, { w: 720 }), deeplink: b.link })) },
      { type: 'OFFERS_STRIP', items: offers },
      { type: 'RESTAURANT_LIST', title: 'Restaurants near you',
        items: restaurants.map(r => ({ id: r.id, name: r.name, eta: r.etaMin, rating: r.rating, img: cdn(r.img, { w: 360 }) })) },
    ],
    cartCount: cart, user: user && { name: user.firstName },
  });
});
```

### GraphQL alternative (Apollo Client, one query for the screen)
```ts
const HOME = gql`query Home($lat: Float!, $lng: Float!) {
  me { firstName }
  banners(city: BLR) { id imageUrl(width: 720) deeplink }
  nearbyRestaurants(lat: $lat, lng: $lng, first: 20) { edges { node { id name etaMin rating imageUrl(width: 360) } } pageInfo { endCursor hasNextPage } }
  cart { itemCount }
}`;
const { data, loading, error, fetchMore } = useQuery(HOME, { variables: { lat, lng } });
```

### Server-driven UI renderer (RN or web)
```tsx
const registry = { BANNER_CAROUSEL: BannerCarousel, OFFERS_STRIP: OffersStrip, RESTAURANT_LIST: RestaurantList };
export function Home({ widgets }: { widgets: Widget[] }) {
  return widgets.map((w, i) => { const C = registry[w.type]; return C ? <C key={i} {...w} /> : null; });   // unknown types ignored → old apps safe
}
```

---

## ⚫ Interview Questions + Answers

**Q1: REST vs GraphQL for a frontend — how do you choose?**
A1: REST suits simple, resource-oriented, cache-friendly APIs (CDN, ETag), public APIs and teams wanting minimal infrastructure. Its downsides are over-fetching, under-fetching and multiple round trips for complex screens. GraphQL suits complex nested UIs with many clients and rapid UI iteration: the client requests exactly what it needs in one round trip, with a strongly typed schema and codegen. The costs are server complexity (resolvers, N+1 with DataLoader, query cost limits, auth per field) and harder HTTP caching (persisted queries help). A BFF is a middle path: tailored REST endpoints per screen or client.

**Q2: What is a BFF and why use one?**
A2: A Backend-for-Frontend is a thin server owned by the frontend team for a specific client (web, iOS/Android, TV). It aggregates and transforms data from many microservices into screen-shaped responses, runs calls in parallel with timeouts and fallbacks, handles client-specific concerns (auth/session, image sizing, feature flags, versioning for old app versions) and hides internal service changes. It cuts round trips on high-latency mobile networks and lets each client evolve independently. The costs are another service to run and possible duplicated logic across BFFs.

**Q3: What should a client-side API layer handle?**
A3: A single configured HTTP client with base URL and timeouts, auth header injection and token refresh with single-flight on 401s, retries with exponential backoff and jitter for idempotent requests only, error normalization into a consistent shape, request IDs for tracing, cancellation via AbortSignal, typed request and response models (OpenAPI or GraphQL codegen, with runtime validation at critical boundaries), and app-version headers for compatibility. Components never call fetch directly; they use hooks built on this layer.

**Q4: How do you design APIs so old mobile app versions don't break?**
A4: Make additive, backward-compatible changes only: add optional fields, never remove or rename fields or change types in place. Version breaking changes (`/v2` or a GraphQL deprecation lifecycle) and keep old versions until usage drops. Clients should ignore unknown fields and widget types, and the server should provide defaults for missing request fields. Send an app version header so the server can tailor responses or require upgrades (426 or a force-update config). Use contract tests between client and server.

**Q5: How do you reduce the number of requests a screen makes?**
A5: Aggregate with a BFF or GraphQL so one request returns all screen data. Batch endpoints for many IDs. Include related resources (expand/include). Prefetch likely-next data (on hover or in-viewport) and cache aggressively on the client (React Query staleTime) and HTTP layer. Deduplicate identical requests. Use HTTP/2 multiplexing when multiple requests are unavoidable. Lazy-load below-the-fold widget data.

---

## 🔷 Trade-offs
✅ REST: simple, cacheable, universal — ❌ over/under-fetching, chatty screens.
✅ GraphQL: flexible, typed, one round trip — ❌ server complexity, caching, security (query depth/cost).
✅ BFF: tailored payloads, fewer round trips, hides microservices — ❌ extra service, duplication across BFFs.
✅ Centralized client API layer: consistency — ❌ must be designed carefully (retries only for idempotent).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Over-fetching | Getting more data than needed | ज़रूरत से ज़्यादा डेटा |
| Under-fetching | Needing extra requests | कम डेटा, और requests |
| BFF | Backend-for-Frontend | UI के लिए ख़ास सर्वर |
| Aggregation | Combining multiple services' data | कई services का डेटा जोड़ना |
| Interceptor | Hook on every request/response | हर request पर चलने वाला |
| Single-flight refresh | One refresh for many 401s | एक ही बार token refresh |
| Codegen | Generate types from schema | schema से types बनाना |
| Persisted query | Pre-registered GraphQL query hash | पहले से दर्ज query |
| Server-driven UI | Backend decides layout/widgets | backend तय करे UI |
| Backward compatible | Old clients keep working | पुराना ऐप भी चले |

---

## ⚡ 3-Line Summary
**English:**
1. Pick the contract per need: REST (simple, cacheable), GraphQL (flexible nested data), BFF (screen-shaped aggregation per client).
2. One client API module: auth + single-flight refresh, timeouts, safe retries with backoff, normalized errors, request IDs, types, cancellation.
3. Design for mobile: fewer round trips, trimmed payloads, additive changes, app-version awareness, server-driven widgets.

**Hindi:**
1. ज़रूरत के हिसाब से: REST (सरल, cache), GraphQL (nested डेटा), BFF (स्क्रीन जैसा जवाब)।
2. Client में एक API module: auth + एक बार refresh, timeout, safe retry, एक जैसे errors, request ID, types।
3. Mobile के लिए: कम requests, छोटा payload, सिर्फ़ जोड़ने वाले बदलाव, app version, server-driven widgets।

---

## ➡️ Next Topic Suggestion
**F12. Pagination, Infinite Scroll + Virtualization** — Feeds, menus and tables can have thousands of items. Next: how to load them page by page and render only what's visible so scrolling stays at 60 fps.
