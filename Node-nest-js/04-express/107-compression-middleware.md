# 107. Compression Middleware
# हिंदी में: Compression Middleware — Response को Gzip/Brotli से छोटा करना

---

## 🔵 Simple Definition (English)
**Compression middleware** (the `compression` npm package) compresses HTTP response bodies using gzip/brotli/deflate before sending them to the client. Smaller payload over the wire = faster page loads, lower bandwidth cost, especially for JSON APIs and HTML/CSS/JS assets.

## 🔵 सरल परिभाषा (Hindi)
**Compression middleware** (`compression` npm package) HTTP response body को client को भेजने से पहले gzip/brotli/deflate से compress कर देता है। Wire पर छोटा payload जाता है = तेज़ page load, कम bandwidth cost — खासकर JSON APIs और HTML/CSS/JS assets के लिए।

---

## 🔴 Problem it Solves
Without compression, a 500KB JSON response (e.g., Flipkart product listing with 200 items) travels over the network as-is — 500KB. On 3G/4G mobile networks in India, this adds visible latency. Text-based content (JSON, HTML, CSS, JS) compresses extremely well with gzip — often 70-90% size reduction. Without this middleware, every API response, every static asset is sent uncompressed, wasting bandwidth and slowing down mobile users who are the majority of traffic for apps like Swiggy/Zomato.

## 🔴 यह क्यों बना? (Hindi)
Compression के बिना, एक 500KB JSON response (जैसे Flipkart का 200 items वाला product listing) network पर as-is जाता है — पूरा 500KB। India में 3G/4G mobile networks पर ये noticeable latency add करता है। Text-based content (JSON, HTML, CSS, JS) gzip से बहुत अच्छे से compress होता है — अक्सर 70-90% size कम हो जाता है। इस middleware के बिना हर API response, हर static asset uncompressed भेजा जाता है, bandwidth waste होती है और mobile users (जो Swiggy/Zomato जैसे apps के majority traffic हैं) के लिए app slow हो जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends request with `Accept-Encoding: gzip, deflate, br` header (browsers do this automatically).
Step 2 → `compression()` middleware intercepts the outgoing response before it's written to the socket.
Step 3 → It checks `Accept-Encoding` header and picks the best supported algorithm (prefers brotli `br` if supported, else gzip).
Step 4 → Response body is piped through a compression stream (zlib) and `Content-Encoding: gzip` header is set.
Step 5 → Browser receives compressed bytes, automatically decompresses using the `Content-Encoding` header, renders normally — fully transparent to frontend code.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client request में `Accept-Encoding: gzip, deflate, br` header भेजता है (browser automatically करता है)।
Step 2 → `compression()` middleware outgoing response को socket पर write होने से पहले intercept करता है।
Step 3 → ये `Accept-Encoding` header check करके best algorithm choose करता है (brotli `br` preferred, फिर gzip)।
Step 4 → Response body zlib compression stream से गुज़रता है और `Content-Encoding: gzip` header set होता है।
Step 5 → Browser compressed bytes receive करके `Content-Encoding` header के आधार पर automatically decompress करता है — frontend code को कुछ पता नहीं चलता।

---

## 🟡 Real World Example
**Flipkart product-listing API:** `/api/products?category=electronics` returns 200 products as JSON — raw size ~480KB. With `compression()` middleware applied, gzip reduces it to ~45KB (about 90% reduction because JSON has repetitive keys like `"price"`, `"title"`, `"inStock"`). On a mobile 4G connection, this cuts response time from ~1.2s to ~150ms. Flipkart's CDN/reverse-proxy (Nginx/Varnish) may also compress, but having it at the app layer as well guards direct API calls that bypass the CDN (internal microservice calls, mobile app hitting the origin directly).

## 🟡 Real Example Hindi mein
**Flipkart product-listing API:** `/api/products?category=electronics` 200 products JSON में return करता है — raw size ~480KB। `compression()` middleware लगाने पर gzip इसे ~45KB तक घटा देता है (करीब 90% reduction क्योंकि JSON में `"price"`, `"title"`, `"inStock"` जैसी repetitive keys होती हैं)। Mobile 4G connection पर ये response time ~1.2s से ~150ms तक घटा देता है। Flipkart का CDN/reverse-proxy (Nginx/Varnish) भी compress करता है, लेकिन app layer पर भी compression रखने से direct API calls (internal microservices, origin को directly hit करने वाला mobile app) भी protected रहती हैं।

---

## 💻 Code Example — Basic

```javascript
// compression-basic.js
const http = require('http');
const zlib = require('zlib'); // built-in Node.js compression module

// Create a plain HTTP server (no Express) to show raw mechanics
const server = http.createServer((req, res) => {
  const bigJson = JSON.stringify({ items: new Array(1000).fill({ name: 'item', price: 100 }) });

  // Check what the client supports
  const acceptEncoding = req.headers['accept-encoding'] || '';

  if (acceptEncoding.includes('gzip')) {
    // Set header telling browser the body is gzip-compressed
    res.setHeader('Content-Encoding', 'gzip');
    res.setHeader('Content-Type', 'application/json');

    // Create gzip stream and pipe the data through it
    const gzip = zlib.createGzip();
    gzip.pipe(res); // compressed bytes go to response
    gzip.end(bigJson); // write original data into gzip stream
  } else {
    // Fallback: send uncompressed if client doesn't support gzip
    res.setHeader('Content-Type', 'application/json');
    res.end(bigJson);
  }
});

server.listen(3000, () => console.log('Server running on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// compression-advanced.js
const express = require('express');
const compression = require('compression'); // npm install compression
const zlib = require('zlib');

const app = express();

// Production-ready compression config
app.use(
  compression({
    level: 6, // compression level 0-9 (6 is default balance of speed vs ratio)
    threshold: 1024, // only compress responses bigger than 1KB (small responses not worth it)
    filter: (req, res) => {
      // Custom filter: skip compression for already-compressed content (images, videos)
      const contentType = res.getHeader('Content-Type') || '';
      if (/image|video|audio/.test(contentType)) return false; // already compressed formats
      // Use the default filter logic as fallback (checks Content-Type for text-based types)
      return compression.filter(req, res);
    },
    brotli: {
      params: {
        [zlib.constants.BROTLI_PARAM_QUALITY]: 4, // brotli quality (0-11), lower = faster
      },
    },
  })
);

app.use(express.json());

// Simulate a large product listing endpoint
app.get('/api/products', (req, res) => {
  const products = Array.from({ length: 500 }, (_, i) => ({
    id: i,
    name: `Product ${i}`,
    description: 'A great product with many features and detailed specifications included here.',
    price: Math.floor(Math.random() * 10000),
  }));
  res.json({ products }); // compression middleware automatically compresses this
});

// Static assets also get compressed (CSS/JS files)
app.use(express.static('public')); // compression applies before static middleware sends files

app.listen(3000, () => {
  console.log('Server running — compression active for responses > 1KB');
});
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const compression = require('compression');
const app = express();

// Apply compression as early as possible in the middleware stack
// (so it wraps res.write/res.end before any route handler runs)
app.use(compression());

app.use(express.json());
app.use(express.static('public')); // static files also compressed

app.get('/api/orders', async (req, res) => {
  const orders = await Order.find().limit(100); // Mongoose query
  res.json(orders); // automatically gzip-compressed if client supports it
});

app.listen(4000, () => console.log('API server with compression running'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Compressing already-compressed content (images, videos, zip files)
✅ Correct: Use `filter` option to skip binary/already-compressed MIME types — compressing a JPEG wastes CPU and can even increase size slightly.

```javascript
// Wrong — compresses everything blindly, wasting CPU on images
app.use(compression());
app.get('/image.jpg', (req, res) => res.sendFile('image.jpg')); // CPU wasted re-compressing JPEG

// Right — filter out binary formats
app.use(compression({
  filter: (req, res) => !/image|video/.test(res.getHeader('Content-Type') || ''),
}));
```

❌ Mistake 2: Setting compression level too high (9) on a high-traffic API
✅ Correct: Level 9 gives marginally better compression ratio but can be 2-4x slower than level 6, hurting CPU-bound throughput under load — level 6 is the sweet spot for most APIs.

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const compression = require('compression');
const app = express();

app.get('/small', (req, res) => res.json({ ok: true })); // tiny response, no compression middleware yet
app.use(compression({ threshold: 0 }));
app.get('/big', (req, res) => res.json({ data: 'x'.repeat(5000) }));

app.listen(3000);
```
What is the `Content-Encoding` header for `/small` vs `/big`?

Answer: `/small` has **no `Content-Encoding` header** (not `gzip`, plain) because the route is registered BEFORE `app.use(compression())` — Express middleware runs in registration order, so `/small`'s handler executes and sends the response before the compression middleware is even attached to that request's response object. `/big` gets `Content-Encoding: gzip` because it's registered after compression middleware was applied, so the response-wrapping happens first. This demonstrates that middleware order in Express matters — compression (and most middleware) should be registered near the top of the stack, before route handlers.

---

## ⚫ Interview Questions + Answers

Q1: Why does compression() need to be registered early in the middleware stack?
A1: Express middleware executes in the order it's registered via `app.use()`/route handlers. `compression()` works by monkey-patching `res.write` and `res.end` to pipe data through a zlib stream before it reaches the socket. If a route handler runs and calls `res.end()` before `compression()` wraps it, the response is already sent uncompressed. So it must be registered before any routes that should be compressed.

Q2: What's the difference between gzip, deflate, and brotli?
A2: All are compression algorithms. **Deflate** is the raw DEFLATE algorithm (older, less used directly). **Gzip** wraps DEFLATE with a header/checksum — most widely supported, good balance of speed/ratio. **Brotli (`br`)** is newer (by Google), achieves 15-25% better compression ratio than gzip for text content but is slower to compress (though faster to decompress) — ideal for static assets that are compressed once and served many times (pre-compress at build time), less ideal for dynamic responses compressed on every request unless using a low quality setting.

Q3: Should you compress responses on every request, or precompute compressed static assets?
A3: For **dynamic API responses** (JSON that changes per-request), compress on-the-fly with middleware — there's no way to precompute. For **static assets** (bundled CSS/JS, images that don't change), precompute `.gz`/`.br` files at build time and serve them directly (e.g., Nginx `gzip_static` or serving `.br` files with correct headers) — this avoids repeated CPU cost of compressing the same file on every request.

Q4: Does compression help with already-encrypted/binary data like images or videos?
A4: No — JPEG, PNG, MP4, and ZIP files are already compressed/entropy-dense; running gzip/brotli on them yields negligible or even negative savings (adds overhead) while wasting CPU. The `compression` middleware's default filter already excludes most binary content-types, but it's good practice to explicitly filter them out.

Q5: What is the `threshold` option and why does it matter for performance?
A5: `threshold` sets a minimum response size (bytes) below which compression is skipped (default 1024 bytes / 1KB). Compressing tiny responses (e.g., `{"ok":true}`) wastes CPU cycles for negligible network savings since the compression overhead (gzip header bytes, CPU time) can exceed the saved bytes. Setting a sensible threshold avoids this inefficiency on high-traffic small-payload endpoints.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Serving JSON APIs with medium/large payloads (product lists, search results, reports)
- Serving text-based static assets (HTML, CSS, JS) not already compressed by a CDN
- Bandwidth cost or mobile network latency matters (majority Indian mobile traffic)

❌ Avoid when:
- A reverse proxy/CDN (Nginx, CloudFront, Varnish) already compresses responses — doing it twice at app level is redundant CPU cost (though can still help for direct origin hits)
- Serving already-compressed binary content (images, videos, PDFs, zip files)
- Extremely CPU-constrained environments where every millisecond of compute matters more than bandwidth (rare, but possible for very high-throughput low-latency services)

---

## 📊 Visual Diagram
```
WITHOUT COMPRESSION:
  Server ──[ 480 KB JSON ]──────────────────▶ Client   (slow on 3G/4G)

WITH COMPRESSION MIDDLEWARE:
  Server ──gzip()──[ 45 KB gzip ]────────────▶ Client
                                                 │
                                        auto-decompress
                                        (Content-Encoding: gzip)
                                                 ▼
                                          Original 480 KB JSON

MIDDLEWARE ORDER MATTERS:
  app.use(compression())  ◀── MUST be before routes
  app.use(express.json())
  app.get('/api/products', handler)  ◀── response gets compressed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compression | Reducing response size before sending | Response size कम करना |
| gzip | Common compression algorithm | सामान्य compression algorithm |
| brotli | Newer, better-ratio compression algorithm | नया, बेहतर ratio वाला algorithm |
| Content-Encoding | Header telling client how body is encoded | Body encoding बताने वाला header |
| Accept-Encoding | Client header listing supported algorithms | Client के supported algorithms |
| Threshold | Minimum size to trigger compression | Compression के लिए minimum size |
| zlib | Node.js built-in compression module | Node का built-in compression module |

---

## ⚡ 3-Line Summary
English:
1. Compression middleware (`compression` npm package) gzip/brotli-compresses HTTP responses, cutting payload size by 70-90% for text/JSON content.
2. Register it early in the middleware stack (before routes) since it wraps `res.write`/`res.end`; use a `threshold` and `filter` to skip tiny or already-compressed responses.
3. Essential for JSON APIs and mobile-heavy traffic (Flipkart, Swiggy) where bandwidth and latency directly affect user experience.

Hindi:
1. Compression middleware (`compression` npm package) HTTP responses को gzip/brotli से compress करता है, text/JSON content का size 70-90% तक कम हो जाता है।
2. इसे middleware stack में शुरुआत में (routes से पहले) register करो क्योंकि ये `res.write`/`res.end` को wrap करता है; tiny या already-compressed responses को skip करने के लिए `threshold` और `filter` use करो।
3. JSON APIs और mobile-heavy traffic (Flipkart, Swiggy) के लिए ज़रूरी है जहाँ bandwidth और latency directly user experience को affect करते हैं।

---

## ➡️ Next Topic
**108. Morgan — Request Logger** — HTTP request logging for debugging and monitoring in Express apps।
