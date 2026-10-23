# 63. API Versioning
# हिंदी में: API Versioning — API में बदलाव करते समय पुराने clients (ख़ासकर पुराने mobile ऐप) को तोड़े बिना नए version लाना

---

## 🔵 Simple Definition (English)
**API versioning** is the practice of managing changes to an API so **existing clients keep working** while new clients use new behaviour. You expose versions (e.g. `/api/v1/…`, `/api/v2/…`, or a version header), make **backward-compatible changes within a version**, introduce **breaking changes only in a new version**, and **deprecate** old versions with a timeline.

## 🔵 सरल परिभाषा (Hindi)
API versioning यानी API बदलते समय पुराने ऐप्स को चलते रहने देना — जैसे `/api/v1` और `/api/v2` दोनों साथ चलें।
छोटे, सुरक्षित बदलाव उसी version में; तोड़ने वाले बदलाव नए version में; और पुराने version को एक तय समय के बाद बंद करना।

---

## 🔴 Problem it Solves
Web frontends update instantly on deploy, but:
- **Mobile apps:** users run app versions from **months or years ago**. You can't force everyone to update. Renaming a field breaks their app → crashes → 1-star reviews.
- **Third-party integrations** (partners, public API users) upgrade on **their** schedule.
- **Microservices** are deployed independently; consumers lag behind providers.

Without versioning discipline, every API change risks **breaking production clients you don't control**.

## 🔴 यह क्यों बना? (Hindi)
Web ऐप deploy होते ही अपडेट हो जाता है, पर mobile ऐप के यूज़र महीनों पुराना version चलाते हैं — field का नाम बदला तो उनका ऐप crash।
Partners और दूसरी services भी अपने समय पर अपडेट करते हैं। Versioning के बिना हर बदलाव उन clients को तोड़ सकता है जिन पर आपका नियंत्रण नहीं है।

---

## 🟢 How it Works — Step by Step

### Breaking vs non-breaking changes (most important part)

```
✅ NON-BREAKING (safe within a version)          ❌ BREAKING (need new version)
- Add a new endpoint                              - Remove/rename a field or endpoint
- Add an OPTIONAL request field                   - Change a field's type (string → number)
- Add a new response field                        - Make an optional field required
- Add a new enum value* (if clients tolerate it)  - Change meaning/units (price paise → rupees)
- Relax validation (accept more)                  - Change error codes/format
- Improve performance                             - Change auth scheme
                                                  - Change default behaviour/sorting
                                                  - Tighten validation (reject previously valid)
* Clients must follow the "tolerant reader" rule: ignore unknown fields & handle unknown enums.
```

### Versioning strategies

```
┌──────────────────────────┬─────────────────────────────────┬──────────────────────────────────┐
│ Strategy                 │ Example                         │ Pros / Cons                      │
├──────────────────────────┼─────────────────────────────────┼──────────────────────────────────┤
│ URI path ⭐               │ /api/v1/orders                  │ ✅ explicit, easy to route/cache, │
│                          │                                 │ easy to test   ❌ "not pure REST" │
│ Query param              │ /api/orders?version=2           │ ✅ simple ❌ easy to forget, cache│
│ Custom header            │ API-Version: 2                  │ ✅ clean URLs ❌ hidden, harder   │
│                          │                                 │ to test in browser               │
│ Media type (content neg.)│ Accept: application/vnd.myapp.  │ ✅ REST-purist ❌ complex          │
│                          │ v2+json                         │                                  │
│ Date-based (Stripe)      │ Stripe-Version: 2024-06-20      │ ✅ fine-grained, account pinned   │
│                          │                                 │ ❌ needs transformation layers    │
└──────────────────────────┴─────────────────────────────────┴──────────────────────────────────┘
Most teams: URI major version (/v1, /v2) + additive changes within it.
```

### Stripe-style version transformation (how big APIs avoid N codebases)

```
Core code always produces the LATEST response shape.
Each old version has a small "transform" that converts latest → that version's shape.

Request with Stripe-Version 2023-01-01
   → handler builds latest response
   → apply transforms backwards: 2024-06 → 2024-01 → 2023-08 → 2023-01
   → return old shape
New accounts are pinned to the latest version at signup.
```

### Deprecation lifecycle

```
1. Announce: docs, changelog, email to API consumers / in-app message
2. Mark deprecated: response headers
     Deprecation: true    (or a date)
     Sunset: Wed, 01 Apr 2026 00:00:00 GMT
     Link: <https://docs.myapp.com/migrate-v2>; rel="deprecation"
3. Monitor usage of old version (metrics per version & client) → contact heavy users
4. Brownouts: temporarily disable old version for short periods to surface stragglers
5. Remove after sunset date
```

### Mobile-specific strategy ⭐

```
Every request sends:  X-App-Version: 4.12.0   X-Platform: android   X-Build: 41200
Server can:
  - keep old response shapes for old app versions (version-aware serializers)
  - feature-flag new behaviour only for app ≥ 4.10
  - return "426 Upgrade Required" / custom error for versions below minimum supported
App on launch: GET /app-config → { minSupportedVersion: "4.0.0", latestVersion: "4.12.0", forceUpdate: false }
   → if below min → blocking "Please update" screen (Topic M18)
Plan the API so old apps degrade gracefully: unknown enum → fallback UI, missing field → default.
```

### GraphQL & gRPC
```
GraphQL: typically "versionless" — add fields freely, mark old ones @deprecated(reason: "..."),
         track field usage, remove when unused.
gRPC/Protobuf: never reuse field numbers; add new fields; mark old `reserved`; new package (v2) for breaking.
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले समझो कौन-सा बदलाव तोड़ता है: field हटाना/नाम बदलना/type बदलना = breaking; नया optional field जोड़ना = सुरक्षित।
2. सुरक्षित बदलाव उसी version में करो; breaking बदलाव `/api/v2` में।
3. Clients "tolerant reader" हों — अनजान fields और enum values को नज़रअंदाज़ करें।
4. पुराने version को deprecate करो: `Deprecation`/`Sunset` headers, usage देखो, फिर तय तारीख़ को बंद।
5. Mobile: हर request में `X-App-Version` भेजो; बहुत पुराने version को "Update करो" स्क्रीन, और सर्वर पुराने ऐप के लिए पुराना response shape रख सकता है।

---

## 🟡 Real World Example

**Stripe** — date-based API versions, with every account pinned to the version it started with. Internally they keep one codebase plus "version change" modules that transform responses for older versions. That's how they support integrations written 10 years ago.

**Twitter API v1.1 → v2, Facebook Graph API (v18, v19…)** — Facebook releases a new Graph API version roughly every quarter, with each version supported for about 2 years. Apps must explicitly upgrade.

**Indian consumer apps (Swiggy, Zomato, PhonePe)** — send app version headers and run a **minimum supported version** config. When a critical API change or security fix lands, old versions get a **force update** screen. Backend serializers keep compatibility for the supported range.

**GitHub REST API** — moved to calendar-based versioning via an `X-GitHub-Api-Version: 2022-11-28` header.

## 🟡 Real Example Hindi में
Stripe हर अकाउंट को उसकी शुरुआत वाले version पर रखता है और पुराने version के लिए response बदलकर देता है — 10 साल पुराने integration भी चलते हैं।
Swiggy, PhonePe जैसे ऐप हर request में app version भेजते हैं; बहुत पुराना version हो तो "ज़रूरी अपडेट" स्क्रीन दिखती है।

---

## 🟠 My Stack Example

### Express — URI versioning with shared services
```js
import v1 from './routes/v1/index.js';
import v2 from './routes/v2/index.js';
app.use('/api/v1', deprecate({ sunset: '2026-04-01', link: 'https://docs.myapp.com/migrate-v2' }), v1);
app.use('/api/v2', v2);

function deprecate({ sunset, link }) {
  return (req, res, next) => {
    res.set('Deprecation', 'true');
    res.set('Sunset', new Date(sunset).toUTCString());
    res.set('Link', `<${link}>; rel="deprecation"`);
    metrics.apiVersionCalls.inc({ version: 'v1', client: req.get('X-App-Version') ?? 'unknown' });
    next();
  };
}

// v1 and v2 routes call the SAME service; only the response shape differs
// routes/v1/orders.js
r.get('/:id', async (req, res) => {
  const o = await orderService.get(req.params.id, req.user);
  res.json({ id: o.id, total: o.totalPaise / 100, status: o.status });            // v1: rupees float
});
// routes/v2/orders.js
r.get('/:id', async (req, res) => {
  const o = await orderService.get(req.params.id, req.user);
  res.json({ id: o.id, total: { amount: o.totalPaise, currency: 'INR' }, status: o.status, eta: o.eta }); // v2
});
```

### Minimum app version gate (mobile)
```js
import semver from 'semver';
const MIN_VERSION = { ios: '4.0.0', android: '4.0.0' };
app.use('/api', (req, res, next) => {
  const v = req.get('X-App-Version'), p = req.get('X-Platform');
  if (v && p && MIN_VERSION[p] && semver.lt(v, MIN_VERSION[p]))
    return res.status(426).json({ error: 'UPGRADE_REQUIRED', storeUrl: STORE_URLS[p] });
  next();
});
```

### FastAPI — versioned routers
```python
v1 = APIRouter(prefix="/api/v1"); v2 = APIRouter(prefix="/api/v2")

class OrderV1(BaseModel): id: int; total: float; status: str
class Money(BaseModel): amount: int; currency: str = "INR"
class OrderV2(BaseModel): id: int; total: Money; status: str; eta: datetime | None = None

@v1.get("/orders/{oid}", response_model=OrderV1, deprecated=True)     # shows as deprecated in /docs
async def get_v1(oid: int, user=Depends(current_user)):
    o = await svc.get(oid, user); return OrderV1(id=o.id, total=o.total_paise / 100, status=o.status)

@v2.get("/orders/{oid}", response_model=OrderV2)
async def get_v2(oid: int, user=Depends(current_user)):
    o = await svc.get(oid, user); return OrderV2(id=o.id, total=Money(amount=o.total_paise), status=o.status, eta=o.eta)

app.include_router(v1); app.include_router(v2)
```

### React Native client — tolerant reader + version headers
```ts
api.defaults.headers.common['X-App-Version'] = Application.nativeApplicationVersion!;
api.defaults.headers.common['X-Platform'] = Platform.OS;

// Tolerant: unknown status from a newer server → safe fallback UI
const STATUS_LABEL: Record<string, string> = { PLACED: 'Placed', PREPARING: 'Preparing', DELIVERED: 'Delivered' };
const label = STATUS_LABEL[order.status] ?? 'In progress';

// zod: .passthrough() / don't use .strict() on responses → extra fields don't crash parsing
const Order = z.object({ id: z.number(), status: z.string() }).passthrough();
```

### Contract safety in CI
```
- OpenAPI spec per version committed to repo
- CI diff check (oasdiff / openapi-diff) → fail PR if a breaking change hits an existing version
- Consumer-driven contract tests (Pact) between services
```

---

## ⚫ Interview Questions + Answers

**Q1: Why do APIs need versioning, especially for mobile?**
A1: Clients you don't control (installed mobile apps, partner integrations, other services) can't update in lockstep with your backend. Mobile users run old app versions for months. Breaking changes (renaming or removing fields, changing types or semantics) would crash them. Versioning lets you evolve the API while keeping existing clients working, then retire old versions in a controlled way.

**Q2: What changes are backward-compatible vs breaking?**
A2: Compatible: adding endpoints, adding optional request parameters, adding response fields, relaxing validation, and adding enum values (if clients are tolerant readers). Breaking: removing or renaming fields or endpoints, changing data types, formats or units, making optional inputs required, tightening validation, changing error formats or status codes, changing default behaviour or ordering, and changing auth. Breaking changes require a new version.

**Q3: URI versioning vs header versioning — which do you prefer?**
A3: URI major versioning (`/v1`, `/v2`) is explicit, easy to route at gateways and load balancers, cache-friendly, and easy to test with curl or a browser, which is why it's the common pragmatic choice. Header or media-type versioning keeps URLs stable and is more "RESTful", but it's less visible and harder to debug. Date-based header versions (Stripe, GitHub) allow fine-grained evolution with response transformations. Pick one and be consistent. Most changes should be additive anyway.

**Q4: How do you deprecate and remove an old API version safely?**
A4: Announce with a migration guide and timeline. Add `Deprecation` and `Sunset` headers plus a docs link. Instrument per-version and per-client usage, and contact the remaining heavy users. For mobile, raise the minimum supported app version and show update prompts, then force updates. Run brownouts (short planned disables) to flush out unknown dependents. Remove only after usage is near zero and the sunset date has passed, and keep the code paths isolated so removal is clean.

**Q5: How do you avoid maintaining several full copies of your API code for each version?**
A5: Keep a single domain or service layer, and version only the edges: per-version controllers or serializers (DTO mappers) that adapt the request and response shapes. Or, like Stripe, generate the latest shape and apply a chain of version-transform functions down to the requested version. Prefer additive changes so versions are rare, and enforce compatibility with OpenAPI diff checks and contract tests in CI.

---

## 🔷 Trade-offs
✅ Advantages:
- Safe evolution; old clients keep working; clear migration path; trust from partners.

❌ Disadvantages:
- Maintaining multiple versions costs time (tests, docs, code paths).
- Too many versions → complexity and security patching burden.
- Clients may never migrate without pressure (deprecation work needed).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| API versioning | Managing API changes over time | API बदलावों का प्रबंधन |
| Breaking change | Change that breaks existing clients | पुराने clients को तोड़ने वाला बदलाव |
| Backward compatible | Old clients still work | पुराने clients चलते रहें |
| Deprecation | Marking for future removal | भविष्य में हटाने की घोषणा |
| Sunset | Date when version is removed | बंद होने की तारीख़ |
| Tolerant reader | Client ignores unknown fields | अनजान fields नज़रअंदाज़ करने वाला |
| Force update | Block old app versions | पुराने ऐप को अपडेट के लिए मजबूर करना |
| Contract test | Verify API matches consumer expectations | API अनुबंध की जाँच |
| Brownout | Temporary planned disable | अस्थायी जानबूझकर बंद |

---

## ⚡ 3-Line Summary
**English:**
1. Version APIs so clients you don't control (mobile apps, partners) don't break; make additive changes within a version, breaking ones in a new version.
2. URI major versions are the pragmatic default; Stripe-style date versions + transformers for large public APIs.
3. Deprecate with headers, usage metrics and sunset dates; for mobile, send app version, use min-version force updates, and code clients as tolerant readers.

**Hindi:**
1. Versioning से पुराने mobile ऐप/partners नहीं टूटते; सुरक्षित बदलाव उसी version में, तोड़ने वाले नए version में।
2. `/v1`, `/v2` सबसे आसान; बड़े public API के लिए Stripe जैसा date version।
3. Deprecation headers, usage और sunset तारीख़; mobile पर app version भेजो, force update रखो, अनजान fields सहो।

---

## ➡️ Next Topic Suggestion
**64. Idempotency** — The last API fundamental: what happens when a mobile app on a flaky network retries "Pay ₹500"? Next: idempotency keys, safe retries, and preventing double charges and duplicate orders.
