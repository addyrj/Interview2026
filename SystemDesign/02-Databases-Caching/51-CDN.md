# 51. CDN — Content Delivery Network
# हिंदी में: CDN — दुनिया भर में फैले सर्वरों का जाल, जो आपकी फ़ाइलें (images, JS, videos) यूज़र के सबसे पास वाले सर्वर से देता है

---

## 🔵 Simple Definition (English)
A **CDN** is a globally distributed network of **edge servers (PoPs — Points of Presence)** that **cache and serve content close to users**. Instead of every user fetching images/JS/videos from your origin server in Mumbai, users get them from the nearest edge (Delhi, Chennai, Singapore, London). The result: lower latency, less origin load, and protection against traffic spikes and DDoS.
Examples: **CloudFront, Cloudflare, Akamai, Fastly**, Google Cloud CDN, Bunny.

## 🔵 सरल परिभाषा (Hindi)
CDN दुनिया भर में फैले सर्वरों (edge) का नेटवर्क है जो आपकी फ़ाइलों की copy रखता है और यूज़र को सबसे पास वाले सर्वर से देता है।
इससे वेबसाइट तेज़ होती है, आपके मुख्य सर्वर (origin) पर बोझ कम होता है, और DDoS हमले से बचाव मिलता है।

---

## 🔴 Problem it Solves
- **Distance = latency:** a user in Delhi fetching from a US server: ~250 ms per round trip; a page with 80 assets takes seconds.
- **Origin overload:** your one server can't push 10 Gbps of images/video to millions of users.
- **Bandwidth cost:** origin egress is expensive; CDN egress is cheaper and offloads it.
- **Spikes & attacks:** viral content or DDoS would crush the origin.
- **Global users:** you can't put servers in 300 cities yourself.

CDN = **"cache at the edge of the internet."**

## 🔴 यह क्यों बना? (Hindi)
दूरी = देरी; दिल्ली के यूज़र को अमेरिका से 80 फ़ाइलें लाने में सेकंड लग जाते हैं। एक सर्वर लाखों यूज़र्स को images/video नहीं भेज सकता, और bandwidth महँगी है।
CDN दुनिया भर के शहरों में copies रखकर यह सब हल करता है — internet के किनारे पर cache।

---

## 🟢 How it Works — Step by Step

```
                  ┌──────────── Origin (S3 / Nginx / Next.js in ap-south-1) ────────────┐
                  │                                                                     │
           cache miss: fetch once                                                 cache miss
                  │                                                                     │
   ┌──────────────┴─────┐      ┌────────────────────┐      ┌─────────────────────┐      │
   │ Edge PoP: Mumbai   │      │ Edge PoP: Delhi    │      │ Edge PoP: Singapore │──────┘
   │ (cached copy)      │      │ (cached copy)      │      │ (cached copy)       │
   └────────▲───────────┘      └─────────▲──────────┘      └──────────▲──────────┘
            │ 5 ms                        │ 8 ms                        │ 30 ms
       Mumbai users                  Delhi users                  SE Asia users
```

```
Step 1 → DNS: cdn.myapp.com → CDN's DNS returns the IP of the NEAREST/healthiest edge
         (GeoDNS or Anycast: same IP announced from many locations, BGP routes to closest)
Step 2 → User → edge: TLS terminated at the edge (fast handshake, nearby)
Step 3 → Edge checks its cache using the CACHE KEY (host + path + selected query/headers)
Step 4 → HIT: return immediately (ms)
         MISS: edge (or a regional "shield" tier) fetches from ORIGIN, stores per Cache-Control, returns
Step 5 → Next users near that edge get HITs
```

### Tiered caching / origin shield

```
User → Edge (300 PoPs) → Regional/Shield cache (few) → Origin
Without shield: 300 edges miss → 300 requests to origin
With shield:    300 edges miss → 1 request to origin (shield collapses them)
```

### What to serve via CDN

```
✅ Static assets: JS, CSS, fonts, icons — hashed filenames, cache 1 year (immutable)
✅ Images & media: product photos, avatars, thumbnails (often with on-the-fly resize/WebP)
✅ Video: HLS/DASH segments (.m3u8, .ts/.m4s) — the #1 CDN use by bytes
✅ Downloads: app bundles, PDFs, OTA updates (Expo updates via CDN)
✅ Public HTML / SSG / ISR pages (Next.js), public API GET responses (menus, catalogs)
⚠️ Dynamic, personalized pages — only with care (no cache, or cache by cookie segments)
❌ Never: authenticated/user-specific responses without "private"/no-store
```

### Cache key & headers control everything

```
Cache key default: scheme + host + path (+ maybe query string)
  /img/p7.jpg?w=400&fm=webp → include w & fm in key (else all sizes collide!)
  Ignore tracking params (utm_*) → better hit ratio
  Vary: Accept-Encoding (gzip/br)   ← OK
  Vary: Cookie                       ← kills hit ratio (each user unique) ❌

Origin response headers:
  Cache-Control: public, max-age=31536000, immutable      → hashed static
  Cache-Control: public, s-maxage=300, stale-while-revalidate=60  → CDN 5 min, browser default
  Cache-Control: private, no-store                         → never cache at CDN
  Surrogate-Key / Cache-Tag                                → purge by tag
```

### Invalidation / purge

```
1. Versioned URLs (best): app.3f9a1c.js, logo.png?v=42 → new deploy = new URL, no purge needed
2. Purge by path:        /restaurants/42/menu   (CloudFront: create-invalidation)
3. Purge by tag:         restaurant-42 (Fastly/Cloudflare)
4. Short TTL + SWR for semi-dynamic data
```

### Beyond caching — modern CDN features
```
- DDoS protection & WAF (block SQLi/XSS/bots), rate limiting, bot management
- TLS termination + HTTP/2, HTTP/3, TLS 1.3 at edge
- Compression (brotli), image optimization (resize, WebP/AVIF)
- Edge compute: Cloudflare Workers, Lambda@Edge, CloudFront Functions, Vercel Edge
  (auth checks, A/B routing, redirects, geolocation headers, personalization)
- Signed URLs / signed cookies → private content (paid videos) served from CDN securely
- Origin failover (secondary origin)
```

## 🟢 कैसे काम करता है? (Hindi)
1. यूज़र `cdn.myapp.com` खोलता है → DNS/Anycast उसे सबसे पास वाले edge सर्वर पर भेजता है।
2. Edge अपने cache में फ़ाइल देखता है — मिली (HIT) तो तुरंत; नहीं मिली (MISS) तो origin से एक बार लाकर रख लेता है।
3. कितनी देर रखना है, यह origin के `Cache-Control` header से तय होता है।
4. JS/CSS के नाम में hash रखो (app.3f9a.js) — नया deploy = नया नाम, purge की ज़रूरत नहीं।
5. CDN DDoS से बचाव, WAF, images का resize, signed URLs और edge पर छोटा code (Workers) भी चलाता है।

---

## 🟡 Real World Example

**Netflix Open Connect** — Netflix built its own CDN. It places cache appliances **inside ISPs** (Jio, Airtel, ACT in India), pre-loaded at night with popular shows. Over 95% of Netflix traffic is served from these boxes, never crossing the internet backbone.

**Hotstar / JioCinema IPL** — tens of Tbps at peak, served by multiple CDNs (Akamai, CloudFront and others) with live HLS segments cached at the edge. A multi-CDN setup gives redundancy if one CDN struggles.

**Flipkart / Myntra product images** — served via CDN with on-the-fly resizing (different widths for phone vs desktop, WebP), which cuts page weight massively.

**Cloudflare outage (July 2019)** — a bad WAF regex caused CPU exhaustion on all edges and took down many sites for ~30 minutes. Lesson: the CDN is itself a critical dependency; some companies keep multi-CDN fallbacks.

## 🟡 Real Example Hindi में
Netflix ने अपना CDN बनाया — Jio/Airtel के डेटा सेंटर के अंदर boxes रखे, जिनमें रात को popular शो पहले से भर दिए जाते हैं; 95% ट्रैफ़िक वहीं से जाता है।
Hotstar का IPL कई CDNs से चलता है, ताकि एक CDN में दिक़्क़त हो तो दूसरा संभाल ले। Flipkart की images CDN पर अपने आप छोटी और WebP बनती हैं।

---

## 🟠 My Stack Example

### Typical setup
```
Next.js web        → Vercel Edge Network (built-in CDN) or CloudFront in front of your Node server
Static/user uploads → S3 bucket (private) → CloudFront (Origin Access Control) → cdn.myapp.com
API                → api.myapp.com (CloudFront/Cloudflare optional for public GETs + WAF)
RN app             → images from cdn.myapp.com, OTA updates (EAS Update) served via CDN
```

### Express: set the right headers (CDN obeys them)
```js
// public, cacheable menu (CDN 5 min, browser 30 s, serve stale while revalidating)
app.get('/api/v1/restaurants/:id/menu', async (req, res) => {
  res.set('Cache-Control', 'public, max-age=30, s-maxage=300, stale-while-revalidate=60');
  res.json(await getMenu(req.params.id));
});
// personal data — never at CDN
app.get('/api/v1/me', auth, (req, res) => { res.set('Cache-Control', 'private, no-store'); res.json(req.user); });
// static build assets with hashed names
app.use('/static', express.static('dist/static', { maxAge: '1y', immutable: true }));
```

### Next.js
```js
// next.config.js — images through optimizer/CDN
module.exports = {
  images: { remotePatterns: [{ protocol: 'https', hostname: 'cdn.myapp.com' }], formats: ['image/avif', 'image/webp'] },
  assetPrefix: process.env.CDN_URL,           // serve /_next/static from CDN when self-hosting
};
// _next/static/* files are hashed → Cache-Control: public, max-age=31536000, immutable (automatic)
```

### CloudFront invalidation after deploy (CI — GitHub Actions)
```yaml
- name: Upload & invalidate
  run: |
    aws s3 sync ./out s3://myapp-web --delete --cache-control "public,max-age=31536000,immutable" --exclude "*.html"
    aws s3 sync ./out s3://myapp-web --exclude "*" --include "*.html" --cache-control "public,max-age=0,must-revalidate"
    aws cloudfront create-invalidation --distribution-id $CF_ID --paths "/index.html" "/*.html"
```

### Private content: signed URLs (paid course videos, invoices)
```js
import { getSignedUrl } from '@aws-sdk/cloudfront-signer';
const url = getSignedUrl({
  url: `https://cdn.myapp.com/videos/${courseId}/master.m3u8`,
  keyPairId: process.env.CF_KEY_PAIR_ID,
  privateKey: process.env.CF_PRIVATE_KEY,
  dateLessThan: new Date(Date.now() + 60 * 60 * 1000).toISOString(),   // 1 hour
});
```

### Image resizing at the edge (pattern)
```
https://cdn.myapp.com/img/products/7.jpg?w=400&fm=webp
CloudFront → (cache key includes w, fm) → miss → Lambda/Image service resizes from S3 original → cached
(or use Cloudinary / imgix / Cloudflare Images / Next.js Image)
```

### React Native
```tsx
<Image source={{ uri: `https://cdn.myapp.com/img/${id}.jpg?w=${PixelRatio.getPixelSizeForLayoutSize(120)}&fm=webp` }} />
// request exactly the pixel size needed → smaller download, better CDN hit ratio with fixed size buckets
```

### Measure
```bash
curl -sI https://cdn.myapp.com/img/p7.jpg | grep -iE "x-cache|age|cache-control|cf-cache-status"
# X-Cache: Hit from cloudfront   |  CF-Cache-Status: HIT   |  Age: 123 (seconds in cache)
```
Track the CDN **cache hit ratio** (aim for 90%+ for static assets) in the CloudFront or Cloudflare dashboard.

---

## ⚫ Interview Questions + Answers

**Q1: What is a CDN and how does it work?**
A1: A geographically distributed network of edge caches. DNS (GeoDNS) or anycast routes each user to a nearby edge, which serves cached content directly. On a miss, it fetches from the origin, often via a shield tier, and caches the response according to Cache-Control. This reduces latency (shorter distance, TLS terminated nearby), offloads origin bandwidth and CPU, absorbs traffic spikes, and adds DDoS and WAF protection.

**Q2: What content should and shouldn't be cached on a CDN?**
A2: Cache static assets (with hashed filenames and long immutable TTLs), images, video segments, downloads, public HTML/SSG pages, and public, non-personalized API GETs with short TTLs. Don't publicly cache authenticated or personalized responses, sensitive data, or responses varying by cookies. Mark them `private, no-store`, or use edge logic that segments carefully. Misconfigurations here cause data leaks.

**Q3: How do you invalidate content on a CDN?**
A3: The best way is to avoid invalidation by using versioned or hashed URLs: a new deploy references new filenames, and old ones expire naturally. For content at fixed URLs, purge by path or wildcard, or by tag or surrogate key (Fastly, Cloudflare), triggered from the CMS or backend on change. Use short `s-maxage` with `stale-while-revalidate` for semi-dynamic content. Keep HTML entry points (index.html) short-lived so they pick up new asset versions.

**Q4: How does a CDN improve performance for dynamic, uncacheable APIs?**
A4: Even without caching, the edge terminates TCP and TLS close to the user, which saves round trips, and keeps persistent, optimized connections to the origin over the provider's backbone. It supports HTTP/2 and HTTP/3 and compression, and can route to the nearest healthy origin region. Edge functions can also handle auth checks, redirects or simple logic without reaching the origin, and WAF and rate limits protect the origin.

**Q5: How would you serve paid video content securely via a CDN?**
A5: Keep the origin private (S3 with Origin Access Control). Serve HLS/DASH through the CDN using signed URLs or signed cookies with short expiry, scoped to the user's entitled content and optionally IP- or geo-restricted. For stronger protection, encrypt segments (AES-128 HLS keys served from an authenticated key server, or DRM like Widevine/FairPlay). Monitor for link sharing, and rotate signing keys.

---

## 🔷 Trade-offs
✅ Advantages:
- Big latency reduction worldwide; massive origin offload; cheaper bandwidth.
- Spike absorption, DDoS/WAF protection, HTTP/3, image optimization, edge compute.

❌ Disadvantages:
- Stale content and invalidation complexity; misconfig can leak private data.
- Cost at very high volumes; vendor dependency (CDN outages affect you).
- Debugging is harder (which edge? cached or not?).
- Limited benefit for highly personalized/uncacheable content (only connection benefits).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CDN | Network of edge caches | दुनिया भर के cache सर्वर |
| Edge / PoP | CDN location near users | यूज़र के पास का सर्वर |
| Origin | Your real server/bucket | आपका असली सर्वर |
| Cache key | What identifies a cached object | cache पहचानने की key |
| Origin shield | Extra cache layer before origin | origin से पहले की परत |
| Anycast | Same IP from many locations | एक IP, कई जगह |
| Purge / Invalidation | Remove content from CDN | CDN से हटाना |
| Signed URL | Time-limited secure link | समय-सीमित सुरक्षित लिंक |
| Edge function | Code running at CDN edge | edge पर चलने वाला code |

---

## ⚡ 3-Line Summary
**English:**
1. A CDN caches content at edge servers near users → lower latency, less origin load, DDoS protection.
2. Control it with Cache-Control headers and cache keys; use hashed URLs to avoid purges; never cache private data publicly.
3. Use it for static assets, images, video, public pages/APIs; signed URLs for private content.

**Hindi:**
1. CDN यूज़र के पास edge पर content रखता है → तेज़, origin पर कम बोझ, DDoS से बचाव।
2. Cache-Control header और cache key से नियंत्रण; hashed URLs से purge की ज़रूरत नहीं; निजी डेटा public cache में कभी नहीं।
3. Static, images, video, public pages के लिए; निजी content के लिए signed URLs।

---

## ➡️ Next Topic Suggestion
**51a. Object Storage (AWS S3)** — CDNs need an origin for files. Next: object storage, how S3 stores billions of files with 11 nines of durability, presigned uploads from mobile, storage classes, and lifecycle policies.
