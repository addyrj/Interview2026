# F07. Browser Caching (Cache-Control, ETag)
# हिंदी में: Browser Caching — ब्राउज़र (और CDN) files की कॉपी अपने पास रखते हैं ताकि दोबारा डाउनलोड न करना पड़े; Cache-Control बताता है कितनी देर रखो, ETag से पूछते हैं "क्या file बदली?"

---

## 🔵 Simple Definition (English)
**HTTP caching** lets browsers, CDNs and proxies store responses and reuse them, either **without contacting the server** (fresh cache) or by asking cheaply whether the copy is still valid (**revalidation**).
- **`Cache-Control`** response header controls caching: `max-age`, `s-maxage`, `no-cache`, `no-store`, `public`, `private`, `immutable`, `stale-while-revalidate`, `must-revalidate`.
- **Validators**: `ETag` (a fingerprint of the content) and `Last-Modified`. The browser revalidates with `If-None-Match` / `If-Modified-Since`, and the server replies **`304 Not Modified`** (no body) if unchanged.
- Caches involved: **memory cache**, **disk (HTTP) cache**, **service worker cache** (F08), **CDN/shared caches**.

## 🔵 सरल परिभाषा (Hindi)
HTTP caching में ब्राउज़र और CDN जवाबों की कॉपी रखते हैं — ताज़ा हो तो सर्वर से पूछे बिना इस्तेमाल, पुरानी हो तो सस्ते में पूछते हैं "बदली क्या?"।
`Cache-Control` तय करता है कितनी देर और कौन रखे (max-age, no-cache, no-store, private, immutable); `ETag` file की पहचान है — न बदली हो तो सर्वर `304 Not Modified` भेजता है, body नहीं।

---

## 🔴 Problem it Solves
Without caching:
- Every page view re-downloads the same JS, CSS, fonts, logos: slow on mobile networks and expensive in bandwidth (Jio/Airtel data, CDN bills).
- Servers handle far more requests than necessary.
- Repeat visits are as slow as the first visit.

Wrong caching is also dangerous:
- **Stale app after deploy** (HTML cached too long references old JS).
- **Private data leaked** via shared caches (a CDN caching `/api/me` for everyone).
- Users seeing **old prices**.
So you need the right policy per resource type.

## 🔴 यह क्यों बना? (Hindi)
बिना caching के हर बार वही JS, CSS, fonts दोबारा डाउनलोड — धीमा, mobile data और CDN का ख़र्च, सर्वर पर बेवजह भार।
ग़लत caching भी ख़तरनाक: deploy के बाद पुराना ऐप दिखना, CDN पर किसी की निजी जानकारी cache होकर दूसरों को दिखना, पुरानी कीमतें। इसलिए हर तरह की file के लिए सही नियम।

---

## 🟢 How it Works — Step by Step

### The decision flow in the browser

```
Need /app.3f9a1c.js
   │
   ▼
Is it in cache?  ── no ──► fetch from network (CDN/origin) ──► store per Cache-Control
   │ yes
   ▼
Is it FRESH? (age < max-age)  ── yes ──► use it, NO network request  ⚡ (from memory/disk cache)
   │ no (stale)
   ▼
Has validator (ETag / Last-Modified)?
   │ yes → conditional request: If-None-Match: "abc123"
   │         server: unchanged → 304 Not Modified (headers only, tiny) → reuse cached body, refresh age
   │                 changed   → 200 OK + new body + new ETag
   │ no  → full fetch
stale-while-revalidate=N: within N sec after stale, serve stale immediately + revalidate in background
```

### Cache-Control directives cheat sheet

```
max-age=N             fresh for N seconds (browser + shared caches)
s-maxage=N            fresh for N seconds in SHARED caches (CDN) — overrides max-age there
public                any cache may store (even with Authorization, if allowed)
private               only the user's browser may store (no CDN) → personalized responses
no-cache              may store, but MUST revalidate before every use (not "don't cache"!)
no-store              never store anywhere → sensitive data (banking, OTP pages, PII APIs)
immutable             content never changes at this URL → skip revalidation even on reload
must-revalidate       once stale, must revalidate (don't serve stale on errors)
stale-while-revalidate=N   serve stale while refreshing in background
stale-if-error=N      serve stale if origin errors (resilience)
Vary: Accept-Encoding, Accept-Language   → cache separate variants per header value
```

### Recommended policy per resource (the interview answer)

```
┌──────────────────────────────────┬──────────────────────────────────────────────────────────┐
│ Resource                         │ Cache-Control                                            │
├──────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ Hashed static assets             │ public, max-age=31536000, immutable                      │
│ (app.3f9a1c.js, styles.ab12.css, │ → cache 1 year; new deploy = new filename (cache busting)│
│  fonts, versioned images)        │                                                          │
│ HTML documents (index.html,      │ no-cache  (or max-age=0, must-revalidate) + ETag         │
│  SSR pages)                      │ → always check, 304 if unchanged; or short s-maxage at   │
│                                  │   CDN + stale-while-revalidate for public pages          │
│ Public API (product catalog,     │ public, max-age=60, s-maxage=300, stale-while-revalidate │
│  restaurant list)                │ =600 + ETag                                              │
│ Personalized API (/me, /cart)    │ private, no-cache (or max-age=0) + ETag                  │
│ Sensitive (payments, PII, OTP)   │ no-store                                                 │
│ User-uploaded images (S3+CDN)    │ public, max-age=31536000, immutable (unique key per      │
│                                  │ upload; new upload = new URL)                            │
└──────────────────────────────────┴──────────────────────────────────────────────────────────┘
```

### ETag in practice

```
1st:  GET /api/restaurants/42        → 200, ETag: "v7-9f8e", Cache-Control: private, no-cache
2nd:  GET /api/restaurants/42
      If-None-Match: "v7-9f8e"       → 304 Not Modified (0 bytes body) → saves bandwidth & JSON parse
Strong ETag "abc" (byte-identical) vs weak W/"abc" (semantically same)
Behind multiple servers: ETag must be consistent across instances (hash of content/version, not inode)
ETag also used for optimistic concurrency: If-Match on PUT → 412 if someone else changed it
```

### Cache busting & CDN invalidation

```
Cache busting: put a content hash/version in the URL → new URL on change → no invalidation needed
CDN invalidation (CloudFront create-invalidation /index.html) → for non-hashed URLs only; slow-ish, costs
Never long-cache non-hashed URLs (e.g., /logo.png max-age=1y → can't update it)
```

### Other browser caches
```
Memory cache (current tab session) · Disk/HTTP cache (above rules) · Service Worker Cache API (F08, you
control it in JS) · bfcache (back/forward cache: whole page snapshot — avoid unload handlers,
Cache-Control: no-store on the page blocks it) · Client data caches (React Query, Apollo — F10)
```

## 🟢 कैसे काम करता है? (Hindi)
1. ब्राउज़र देखता है — cache में है? ताज़ा (max-age के अंदर) है तो network पर गए बिना इस्तेमाल।
2. पुरानी हो तो `If-None-Match: ETag` भेजता है; न बदली हो तो सर्वर 304 भेजता है (बिना body), बदली हो तो 200 + नई file।
3. Hash वाली JS/CSS/fonts: एक साल + immutable; HTML: no-cache (हर बार पूछो) ताकि नया deploy तुरंत दिखे।
4. निजी API: `private` (CDN पर नहीं); payment/OTP जैसा संवेदनशील: `no-store`; public catalog: छोटा max-age + CDN पर s-maxage + stale-while-revalidate।
5. बदलने वाली file का URL बदलो (hash) — CDN invalidation की ज़रूरत नहीं; `no-cache` का मतलब "हर बार पूछो" है, "cache मत करो" नहीं।

---

## 🟡 Real World Example

**Every major SPA/Next.js deploy (Vercel, Netlify, CloudFront)** — `/_next/static/*` assets are served with `public, max-age=31536000, immutable` and HTML with revalidation. Only changed chunks are downloaded after a deploy.

**GitHub / Facebook** — personalized API responses use `private` with ETags. Static assets sit on CDNs with hashed filenames and year-long caching.

**Swiggy/Zomato-style apps** — restaurant images and menus are on a CDN with long cache (new image = new URL). Restaurant availability and ETAs aren't cached publicly (or only for seconds). Cart and payment responses use `no-store`.

**Banking sites (SBI, HDFC netbanking)** — use `no-store` on authenticated pages so the back button or shared computers don't reveal account data from cache.

## 🟡 Real Example Hindi में
Next.js/Vercel पर `_next/static` की files एक साल immutable cache होती हैं और HTML हर बार revalidate — deploy के बाद सिर्फ़ बदली files आती हैं।
Swiggy/Zomato जैसे ऐप में restaurant की images CDN पर लंबे समय cache (नई image = नया URL), पर availability/ETA का cache नहीं; बैंकिंग साइटें login वाले pages पर `no-store` लगाती हैं ताकि shared computer पर back दबाने से डेटा न दिखे।

---

## 🟠 My Stack Example

### Nginx — per-resource caching
```nginx
server {
  # Hashed build assets (Vite/Next export): cache forever
  location ~* \.(?:js|css|woff2|svg|png|webp|avif)$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
    try_files $uri =404;
  }
  # HTML: always revalidate (ETag on by default for static files in nginx)
  location / {
    add_header Cache-Control "no-cache";
    try_files $uri /index.html;
  }
  # API proxied to Node/FastAPI — let the app set headers
  location /api/ { proxy_pass http://app; }
}
```

### Node/Express — ETag + correct headers per route
```js
app.set('etag', 'strong');                                   // Express computes ETag for res.send/json

app.get('/api/restaurants/:id', async (req, res) => {        // public catalog
  const r = await getRestaurant(req.params.id);
  res.set('Cache-Control', 'public, max-age=60, s-maxage=300, stale-while-revalidate=600');
  res.json(r);                                               // 304 handled automatically if If-None-Match matches
});

app.get('/api/me/cart', auth, async (req, res) => {          // personalized
  res.set('Cache-Control', 'private, no-cache');
  res.json(await getCart(req.user.id));
});

app.post('/api/payments', auth, async (req, res) => {        // sensitive
  res.set('Cache-Control', 'no-store');
  res.json(await createPayment(req.user.id, req.body));
});
```

### FastAPI — manual ETag with version
```python
from fastapi import Request, Response
import hashlib, json

@app.get("/api/menu/{rid}")
async def menu(rid: int, request: Request):
    data = await get_menu(rid)                                    # includes data["version"]
    etag = '"' + hashlib.sha1(f'{rid}-{data["version"]}'.encode()).hexdigest() + '"'
    headers = {"ETag": etag, "Cache-Control": "public, max-age=30, s-maxage=120, stale-while-revalidate=300"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(content=json.dumps(data), media_type="application/json", headers=headers)
```

### Next.js — headers config + route caching
```js
// next.config.js
module.exports = {
  async headers() {
    return [
      { source: '/images/:path*', headers: [{ key: 'Cache-Control', value: 'public, max-age=86400, stale-while-revalidate=604800' }] },
      { source: '/account/:path*', headers: [{ key: 'Cache-Control', value: 'private, no-store' }] },
    ];
  },
};
```

### S3 + CloudFront upload with cache headers (GitHub Actions deploy)
```bash
aws s3 sync dist/assets s3://myapp-web/assets --cache-control "public,max-age=31536000,immutable"
aws s3 cp dist/index.html s3://myapp-web/index.html --cache-control "no-cache"
aws cloudfront create-invalidation --distribution-id $CF_ID --paths "/index.html"   # only non-hashed file
```

### React Native note
```
RN's fetch uses the OS HTTP cache (NSURLCache / OkHttp) — respects Cache-Control/ETag on responses.
Images: expo-image / FastImage have their own memory+disk cache (Topic M12).
For data, prefer an explicit client cache (React Query + MMKV persistence — Topic M05/M06).
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between `no-cache` and `no-store`?**
A1: `no-cache` allows caches to store the response but requires revalidation with the origin (using ETag or Last-Modified) before every reuse, which often yields a cheap 304. `no-store` forbids storing the response anywhere, so it must be fetched fully every time. Use `no-cache` for HTML and personalized data that changes, and `no-store` for sensitive data like banking, payments or PII.

**Q2: How would you cache a React/Next.js app's assets and HTML?**
A2: Hashed static assets (JS chunks, CSS, fonts, versioned images) get `public, max-age=31536000, immutable`, because a new build produces new filenames. The HTML gets `no-cache` (revalidate with ETag) or a short CDN `s-maxage` with `stale-while-revalidate` for public pages, so users get new deploys immediately. Personalized pages and APIs get `private`. Keep old hashed assets available after deploys to avoid chunk-load errors.

**Q3: How do ETags work?**
A3: The server sends an `ETag` header, an opaque identifier for that version of the resource (often a hash or version). When the cached copy goes stale, the browser sends `If-None-Match` with that ETag. If the resource is unchanged, the server responds `304 Not Modified` with no body, saving bandwidth and parsing, and the cached copy is reused. Otherwise it returns 200 with the new body and ETag. ETags must be consistent across servers. They're also used with `If-Match` for optimistic concurrency on updates.

**Q4: What is `stale-while-revalidate` and when is it useful?**
A4: It allows a cache to serve a stale response immediately for a window after expiry while fetching a fresh one in the background, so the next request gets updated data. It gives users instant responses with eventual freshness. It's ideal for public catalog data, CDN-served HTML for content pages, avatars, and configs where a few seconds or minutes of staleness is acceptable. React Query and SWR apply the same idea on the client.

**Q5: What caching mistakes can cause bugs or security issues?**
A5: Long-caching non-hashed URLs (users stuck on old JS or HTML). Caching HTML too long after deploys. Caching personalized or authenticated responses as `public` on a CDN, which leaks data to other users. Forgetting `Vary` for content negotiation (wrong language or encoding served). Inconsistent ETags across servers (no 304s). Using `no-store` everywhere (slow, no bfcache). Not invalidating CDN entries for changed non-hashed resources.

---

## 🔷 Trade-offs
✅ Long cache + hashing: fastest repeat loads, minimal bandwidth — ❌ requires build pipeline hashing.
✅ Revalidation (ETag): always correct, cheap 304s — ❌ still a round trip (latency on mobile).
✅ stale-while-revalidate: instant + fresh-ish — ❌ users may briefly see old data.
✅ no-store: safest for sensitive data — ❌ slowest, disables bfcache.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache-Control | Header controlling caching | caching का नियम |
| max-age | Freshness lifetime (seconds) | कितनी देर ताज़ा |
| s-maxage | Freshness for shared caches (CDN) | CDN के लिए समय |
| no-cache | Store but revalidate always | रखो पर हर बार पूछो |
| no-store | Never store | कभी मत रखो |
| private / public | Browser-only / any cache | सिर्फ़ ब्राउज़र / कोई भी |
| immutable | Never changes at this URL | कभी नहीं बदलेगा |
| ETag | Content version identifier | content की पहचान |
| 304 Not Modified | Unchanged, reuse cache | नहीं बदला |
| Cache busting | New URL on content change | बदलने पर नया URL |

---

## ⚡ 3-Line Summary
**English:**
1. Fresh cache = no request; stale cache = revalidate with ETag/Last-Modified → 304 if unchanged.
2. Hashed assets: 1 year immutable; HTML: no-cache; personalized: private; sensitive: no-store; public APIs: short max-age + s-maxage + SWR.
3. Change URLs instead of invalidating, never cache private data publicly, and keep old assets after deploys.

**Hindi:**
1. ताज़ा cache = कोई request नहीं; पुराना = ETag से पूछो → न बदला तो 304।
2. Hash वाली files 1 साल; HTML no-cache; निजी private; संवेदनशील no-store; public API छोटा max-age + SWR।
3. बदलाव पर URL बदलो, निजी डेटा CDN पर cache मत करो, deploy के बाद पुरानी files रखो।

---

## ➡️ Next Topic Suggestion
**F08. Service Workers + PWA + Offline** — HTTP caching is controlled by headers. Service workers let you program the cache yourself: offline pages, app-shell caching, background sync and installable PWAs. Next: how service workers work.
