# 07. REST API Design
# हिंदी में: REST API — रिसोर्स (जैसे users, orders) को साफ़ URL और HTTP methods से expose करने का मानक तरीका

---

## 🔵 Simple Definition (English)
**REST** (Representational State Transfer) is a style of designing APIs where everything is a **resource** (user, order, product) identified by a **URL**, and you act on it with standard **HTTP methods** (GET, POST, PUT, PATCH, DELETE). The server is **stateless**: every request carries all the information it needs.

## 🔵 सरल परिभाषा (Hindi)
REST में हर चीज़ एक "resource" है (users, orders), जिसका एक URL होता है, और उस पर काम HTTP methods से होता है — GET (पढ़ो), POST (बनाओ), PATCH (बदलो), DELETE (हटाओ)।
सर्वर कुछ याद नहीं रखता; हर request अपने आप में पूरा होता है।

---

## 🔴 Problem it Solves
Before REST, APIs were often **SOAP/RPC** style:
- One URL for everything (`POST /service`) with a big XML body saying `<getUserById>`.
- Every team invented its own naming: `/getUser`, `/fetchUserData`, `/user_get_v2`.
- Hard to cache, hard to learn, tightly coupled clients.

REST gives a **uniform, predictable** design:
- Anyone can guess `GET /users/42` and `DELETE /users/42`.
- Uses HTTP features that already exist: status codes, caching (`GET` + `ETag`), auth headers.
- Stateless → any server can handle any request → easy horizontal scaling.

## 🔴 यह क्यों बना? (Hindi)
पहले हर टीम अपने तरीके से API बनाती थी (`/getUser`, `/fetchUserData`) और SOAP में भारी XML भेजना पड़ता था — समझना और cache करना मुश्किल।
REST ने एक जैसा, अंदाज़ा लगाने लायक तरीका दिया जो HTTP की मौजूदा चीज़ों (methods, status codes, caching) का ही इस्तेमाल करता है।

---

## 🟢 How it Works — Step by Step

### The 6 REST constraints (know names for interview)

```
1. Client–Server       → UI and data storage are separated
2. Stateless           → no session on server between requests; send token every time
3. Cacheable           → responses say whether they can be cached (Cache-Control, ETag)
4. Uniform Interface   → resources + URLs + standard methods + representations (JSON)
5. Layered System      → client doesn't know if it's talking to CDN, LB, or app
6. Code on Demand      → (optional) server can send code (JS)
```

### Resource-oriented URLs

```
✅ GOOD (nouns, plural, hierarchy)        ❌ BAD (verbs, inconsistent)
GET    /users                              GET  /getAllUsers
GET    /users/42                           GET  /user?id=42&action=get
POST   /users                              POST /createUser
PATCH  /users/42                           POST /updateUser
DELETE /users/42                           GET  /deleteUser/42      ← GET must never change data!
GET    /users/42/orders                    GET  /getOrdersOfUser?uid=42
GET    /orders/9001/items

Rules:
- Nouns not verbs; plural collections (/orders)
- lowercase, hyphens: /delivery-partners (not /deliveryPartners)
- Nest max 2 levels: /users/42/orders   (not /users/42/orders/9/items/3/reviews)
- Actions that don't fit CRUD → sub-resource:  POST /orders/9001/cancel
                                                POST /payments/77/refunds
```

### Full CRUD mapping

```
┌──────────┬───────────────────┬──────────────────────────┬─────────────────┐
│ Method   │ URL               │ Meaning                  │ Success code    │
├──────────┼───────────────────┼──────────────────────────┼─────────────────┤
│ GET      │ /products         │ List (paginated)         │ 200             │
│ GET      │ /products/7       │ Get one                  │ 200 / 404       │
│ POST     │ /products         │ Create                   │ 201 + Location  │
│ PUT      │ /products/7       │ Replace whole object     │ 200 / 204       │
│ PATCH    │ /products/7       │ Update some fields       │ 200             │
│ DELETE   │ /products/7       │ Delete                   │ 204             │
└──────────┴───────────────────┴──────────────────────────┴─────────────────┘
```

### Filtering, sorting, pagination, field selection

```
GET /products?category=shoes&minPrice=500&maxPrice=2000     ← filtering
GET /products?sort=-createdAt,price                         ← sort desc createdAt, asc price
GET /products?limit=20&cursor=eyJpZCI6MTIzfQ                ← cursor pagination (Topic 39)
GET /products?page=3&limit=20                               ← offset pagination (simpler)
GET /products?fields=id,name,price                          ← return only needed fields (mobile!)
GET /products?include=brand,reviews                         ← embed related data
GET /products?q=nike+air                                    ← search
```

### Consistent response + error shape

```json
// List response
{
  "data": [{ "id": 7, "name": "Nike Air", "price": 4999 }],
  "pagination": { "nextCursor": "eyJpZCI6N30", "hasMore": true }
}

// Error response (same shape everywhere — RFC 7807 "problem details" style)
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Price must be positive",
    "details": [{ "field": "price", "issue": "must be > 0" }],
    "requestId": "req_8f2a1c"          // ← helps you find the log line
  }
}
```

### Versioning (Topic 63)

```
/api/v1/orders  → most common, explicit
Header: Accept: application/vnd.myapp.v2+json  → cleaner URLs, harder to test
Rule: never break v1 clients — especially MOBILE apps that users don't update.
```

### Richardson Maturity Model (bonus)

```
Level 0: one URL, POST everything (RPC/SOAP)
Level 1: resources (/users/42)
Level 2: + HTTP methods + status codes      ← most "REST" APIs are here (good enough)
Level 3: + HATEOAS (links in response telling what you can do next)
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले resources पहचानो — users, orders, products (संज्ञा/noun, क्रिया/verb नहीं)।
2. हर resource का साफ़ URL बनाओ: `/orders`, `/orders/42`, `/users/42/orders`।
3. काम के लिए सही method: GET पढ़ने, POST बनाने, PATCH बदलने, DELETE हटाने के लिए।
4. सही status code लौटाओ (201 बना, 404 नहीं मिला, 422 ग़लत डेटा) और error हमेशा एक जैसे format में।
5. लिस्ट में pagination, filter, sort दो; और API को version करो (`/api/v1`) ताकि पुराने मोबाइल ऐप न टूटें।

---

## 🟡 Real World Example

**Stripe API — the gold standard**
- `POST /v1/customers`, `GET /v1/charges/ch_123`, `POST /v1/refunds`.
- Consistent errors (`type`, `code`, `message`, `param`), cursor pagination (`starting_after`), `Idempotency-Key` header on POSTs, date-based versioning (`Stripe-Version: 2024-06-20`). Developers love it because it's predictable.

**GitHub REST API**
- `GET /repos/{owner}/{repo}/pulls/{number}` — clean hierarchy. Pagination via `Link` header. Rate-limit info in headers (`X-RateLimit-Remaining`).

**Zomato/Swiggy mobile apps**
- `GET /restaurants?lat=..&lng=..&cuisine=north-indian&sort=rating` for listing, `POST /cart/items`, `POST /orders`, `POST /orders/{id}/cancel`. Responses are trimmed for mobile (`fields=`) to save data on 3G/4G.

## 🟡 Real Example Hindi में
Stripe का API सबसे अच्छा उदाहरण माना जाता है — एक जैसे URL, एक जैसे error, cursor pagination और Idempotency-Key, इसलिए डेवलपर बिना docs पढ़े अंदाज़ा लगा लेते हैं।
Swiggy का ऐप `GET /restaurants?lat=..&cuisine=..` जैसी API से लिस्ट लाता है और मोबाइल डेटा बचाने के लिए सिर्फ़ ज़रूरी fields माँगता है।

---

## 🟠 My Stack Example

### Node.js (Express) — clean resource router
```js
// routes/products.js
import { Router } from 'express';
import { z } from 'zod';
const r = Router();

const ProductIn = z.object({ name: z.string().min(1), price: z.number().positive() });

r.get('/', async (req, res) => {
  const { limit = 20, cursor, category } = req.query;
  const rows = await db.query(
    `SELECT id, name, price FROM products
     WHERE ($1::text IS NULL OR category = $1) AND ($2::int IS NULL OR id > $2)
     ORDER BY id LIMIT $3`,
    [category ?? null, cursor ? decodeCursor(cursor) : null, Math.min(+limit, 100) + 1]
  );
  const hasMore = rows.length > limit;
  const data = rows.slice(0, limit);
  res.json({ data, pagination: { hasMore, nextCursor: hasMore ? encodeCursor(data.at(-1).id) : null } });
});

r.get('/:id', async (req, res) => {
  const p = await Product.findById(req.params.id);
  if (!p) return res.status(404).json({ error: { code: 'NOT_FOUND', message: 'Product not found' } });
  res.json({ data: p });
});

r.post('/', auth, requireRole('admin'), async (req, res) => {
  const body = ProductIn.parse(req.body);           // throws → error middleware → 422
  const p = await Product.create(body);
  res.status(201).location(`/api/v1/products/${p.id}`).json({ data: p });
});

r.patch('/:id', auth, requireRole('admin'), async (req, res) => {
  const body = ProductIn.partial().parse(req.body);
  res.json({ data: await Product.update(req.params.id, body) });
});

r.delete('/:id', auth, requireRole('admin'), async (req, res) => {
  await Product.delete(req.params.id);
  res.status(204).end();
});

app.use('/api/v1/products', r);

// One error handler → same error shape everywhere
app.use((err, req, res, next) => {
  if (err instanceof z.ZodError)
    return res.status(422).json({ error: { code: 'VALIDATION_FAILED', details: err.issues, requestId: req.id } });
  logger.error({ err, requestId: req.id });
  res.status(500).json({ error: { code: 'INTERNAL', message: 'Something went wrong', requestId: req.id } });
});
```

### FastAPI — same API, auto OpenAPI docs at /docs
```python
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, PositiveFloat

router = APIRouter(prefix="/api/v1/products", tags=["products"])

class ProductIn(BaseModel):
    name: str
    price: PositiveFloat

@router.get("")
async def list_products(limit: int = Query(20, le=100), cursor: int | None = None, category: str | None = None):
    rows = await repo.list(limit=limit + 1, after_id=cursor, category=category)
    has_more = len(rows) > limit
    return {"data": rows[:limit], "pagination": {"hasMore": has_more, "nextCursor": rows[limit-1].id if has_more else None}}

@router.get("/{product_id}")
async def get_product(product_id: int):
    p = await repo.get(product_id)
    if not p:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    return {"data": p}

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductIn, user=Depends(require_admin)):
    return {"data": await repo.create(body)}
```

### Next.js / React Native client — one typed API layer
```ts
// api/products.ts — shared idea for web & mobile
export const getProducts = (params: { cursor?: string; category?: string }) =>
  http.get<{ data: Product[]; pagination: Page }>('/api/v1/products', { params });

// React Query infinite list (works in Next.js & React Native)
const q = useInfiniteQuery({
  queryKey: ['products', category],
  queryFn: ({ pageParam }) => getProducts({ cursor: pageParam, category }),
  getNextPageParam: (last) => last.pagination.nextCursor ?? undefined,
  initialPageParam: undefined,
});
```

### Checklist you can say in an interview
```
✓ Nouns, plural, ≤2 levels nesting      ✓ Correct methods + status codes
✓ Validation → 422 with field details   ✓ Same error shape + requestId
✓ Pagination (cursor for feeds)         ✓ Filtering / sorting / fields
✓ Versioning /api/v1                    ✓ Auth (Bearer token) + RBAC
✓ Rate limiting (429 + Retry-After)     ✓ Idempotency-Key on POST payments/orders
✓ Caching headers on GET (ETag)         ✓ OpenAPI/Swagger docs
✓ HTTPS only, gzip, request timeouts    ✓ Never return passwords/internal fields
```

---

## ⚫ Interview Questions + Answers

**Q1: What makes an API RESTful?**
A1: Resources are identified by URLs, manipulated through a uniform interface of standard HTTP methods, and passed around as representations (usually JSON). The interaction is stateless (every request carries auth and context), responses are cacheable where appropriate, and the system can be layered (CDN, LB, gateway). Most practical "REST" APIs reach Richardson level 2: resources plus proper methods and status codes.

**Q2: PUT vs PATCH vs POST?**
A2: POST creates a new resource (or triggers an action) and is not idempotent. PUT replaces the entire resource at a known URL and is idempotent: sending the same body twice gives the same result. PATCH partially updates specific fields. It's idempotent if it sets values (`{"name":"x"}`), but not if it's an operation like "increment by 1".

**Q3: How would you design an endpoint for an action that isn't CRUD, like cancelling an order?**
A3: Model the action as a sub-resource or state change. Either `POST /orders/{id}/cancel` (a clear, common action endpoint) or `PATCH /orders/{id}` with `{"status": "CANCELLED"}` plus validation of the allowed state transitions. Return 409 Conflict if the order is already delivered. Avoid `GET /cancelOrder?id=…`, because GET must be safe: crawlers and prefetchers can trigger it.

**Q4: How do you handle pagination for a large, frequently-changing list like a feed?**
A4: Use cursor (keyset) pagination: `?limit=20&cursor=<opaque encoded last id/timestamp>`, querying `WHERE (created_at, id) < (:ts, :id) ORDER BY created_at DESC, id DESC LIMIT 21`. It stays fast with an index regardless of depth, and doesn't skip or duplicate items when new rows are inserted, unlike `OFFSET`, which gets slower and shifts results. Return `nextCursor` and `hasMore`.

**Q5: How do you evolve a REST API without breaking existing mobile clients?**
A5: Make only additive, backward-compatible changes within a version: add optional fields, never rename or remove fields or change their types. Clients must ignore unknown fields. Breaking changes go into `/v2`, while v1 keeps running with deprecation headers (`Sunset`, `Deprecation`) and a migration window. Track client versions via headers (`X-App-Version`) and use a force-update screen for very old app versions. Contract tests help, using the OpenAPI spec.

---

## 🔷 Trade-offs
✅ Advantages:
- Simple, predictable, uses HTTP natively (caching, status codes, tooling).
- Stateless → scales horizontally; cacheable at CDN/browser.
- Universal: every language, Postman, curl, OpenAPI docs + code generation.

❌ Disadvantages:
- **Over-fetching** (getting fields you don't need) and **under-fetching** (N calls for one screen) — hurts mobile. → GraphQL / BFF solve this.
- No built-in real-time (need WebSocket/SSE).
- Loosely specified — teams argue about naming/conventions; needs a style guide.
- Chatty for complex screens → many round trips.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Resource | A thing exposed by API (user, order) | API में मौजूद चीज़ |
| Endpoint | URL + method (GET /orders) | API का पता |
| Stateless | Each request self-contained | हर request अपने में पूरा |
| Payload | Request/response body | भेजा गया डेटा |
| Pagination | Returning data in pages | डेटा को पन्नों में देना |
| Over-fetching | Getting more data than needed | ज़रूरत से ज़्यादा डेटा |
| Under-fetching | Needing many calls for one screen | एक स्क्रीन के लिए कई कॉल |
| OpenAPI / Swagger | Machine-readable API spec | API का लिखित ढाँचा |
| HATEOAS | Response contains links to next actions | जवाब में आगे के लिंक |

---

## ⚡ 3-Line Summary
**English:**
1. REST = resources (nouns) at URLs + standard HTTP methods + status codes + stateless requests.
2. Good APIs have consistent naming, errors, pagination, filtering, versioning, and validation.
3. Weakness: over/under-fetching and no real-time — solved by GraphQL/BFF and WebSockets.

**Hindi:**
1. REST = URL पर resource + HTTP method + status code, और सर्वर stateless।
2. अच्छी API में एक जैसा naming, error format, pagination, versioning होता है।
3. कमी: ज़्यादा/कम डेटा और real-time नहीं — इसके लिए GraphQL, BFF, WebSocket।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Hussein Nasser — REST API explained](https://www.youtube.com/results?search_query=REST+API+design+hussein+nasser) | HTTP internals, status codes, idempotency in depth |
| 📺 YouTube | [ByteByteGo — API Design](https://www.youtube.com/results?search_query=API+design+best+practices+bytebytego) | API versioning, pagination, rate limiting visually |
| 📝 Article | [restfulapi.net](https://restfulapi.net/) | Best free REST reference — constraints, status codes, naming |
| 📝 Article | [Stripe API Docs (industry standard)](https://stripe.com/docs/api) | Read Stripe's API — best real-world REST design example |
| 🐙 GitHub | [system-design-primer — API design](https://github.com/donnemartin/system-design-primer#representational-state-transfer-rest) | REST vs RPC, trade-offs with examples |

---

## ➡️ Next Topic Suggestion
**07a. GraphQL** — REST's biggest pain is over-fetching and many round trips per screen. Next: how GraphQL lets the client ask for exactly what it needs in one request, and when it's better or worse than REST.
