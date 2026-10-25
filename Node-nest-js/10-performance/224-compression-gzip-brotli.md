# 224. Compression (gzip/brotli)
# हिंदी में: Compression — Response Size घटा कर Network Transfer तेज़ करना

---

## 🔵 Simple Definition (English)
**HTTP compression** shrinks the response body (JSON, HTML, CSS, JS) before sending it over the network, and the browser/client decompresses it automatically. **gzip** is the widely-supported standard; **brotli** is newer and typically compresses 15-25% smaller than gzip for text content. Both can reduce a JSON API response by 70-90% in size, directly cutting network transfer time.

## 🔵 सरल परिभाषा (Hindi)
**HTTP compression** response body (JSON, HTML, CSS, JS) को network पर भेजने से पहले छोटा कर देती है, और browser/client automatically उसे decompress कर लेता है। **gzip** widely-supported standard है; **brotli** नया है और text content के लिए आम तौर पर gzip से 15-25% ज़्यादा छोटा compress करता है। दोनों एक JSON API response को size में 70-90% तक घटा सकते हैं, network transfer time directly कम होता है।

---

## 🔴 Problem it Solves
A 500KB uncompressed JSON API response takes meaningfully longer to transfer over the network than a 50KB compressed version — especially impactful for mobile users on slower connections, or for APIs serving users across geographic distances with higher latency. Without compression, every byte travels uncompressed, wasting bandwidth and adding real, measurable milliseconds-to-seconds to response times, particularly for text-heavy payloads (JSON, HTML) which compress extremely well due to repetitive structure (field names, whitespace, repeated tokens).

## 🔴 यह क्यों बना? (Hindi)
एक 500KB uncompressed JSON API response network पर transfer होने में compressed 50KB version से काफी ज़्यादा समय लेता है — especially mobile users के लिए slower connections पर, या geographic distance में ज़्यादा latency वाले users के लिए। Compression के बिना, हर byte uncompressed travel करता है, bandwidth waste होता है और response times में real, measurable milliseconds-to-seconds add होते हैं, especially text-heavy payloads (JSON, HTML) के लिए जो repetitive structure (field names, whitespace, repeated tokens) की वजह से बहुत अच्छे compress होते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends a request with an `Accept-Encoding: gzip, br` header, indicating which compression formats it can decompress
Step 2 → Server (via middleware like `compression` in Express) checks this header and compresses the response body accordingly before sending
Step 3 → Server sets `Content-Encoding: gzip` (or `br`) in the response headers so the client knows how to decompress it
Step 4 → Client automatically decompresses the body (browsers/HTTP clients handle this transparently — app code never sees compressed bytes)
Step 5 → Compression is usually skipped for already-compressed formats (images, videos, already-gzipped files) since compressing them again wastes CPU for negligible/negative size benefit
Step 6 → Tune the compression level (1-9 for gzip) — higher levels compress smaller but use more CPU; level 6 is a common balanced default

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client `Accept-Encoding: gzip, br` header के साथ request भेजता है, बताता है कि कौन से compression formats decompress कर सकता है
Step 2 → Server (Express में `compression` middleware से) इस header को check करता है और response body को उसके अनुसार compress करता है भेजने से पहले
Step 3 → Server response headers में `Content-Encoding: gzip` (या `br`) set करता है ताकि client को पता चले कैसे decompress करना है
Step 4 → Client automatically body decompress करता है (browsers/HTTP clients transparently handle करते हैं — app code को कभी compressed bytes नहीं दिखते)
Step 5 → Already-compressed formats (images, videos, already-gzipped files) के लिए compression skip कर दी जाती है क्योंकि दोबारा compress करना CPU waste है negligible/negative benefit के लिए
Step 6 → Compression level (gzip के लिए 1-9) tune करो — higher levels छोटा compress करते हैं पर ज़्यादा CPU use करते हैं; level 6 एक common balanced default है

---

## 🟡 Real World Example
**Flipkart's product-listing API** returns JSON responses averaging 400KB for a page of 50 products with full details (images URLs, specs, reviews summary, pricing tiers). Enabling gzip compression at level 6 reduced the average response size to ~45KB (89% reduction) — for users on 3G/4G connections in tier-2/3 Indian cities, this cut the time-to-first-render on the product listing page significantly, since the network transfer itself was often the biggest bottleneck, bigger than server processing time. Switching to brotli for clients that support it (`Accept-Encoding: br`) shaved off another ~8KB on average.

## 🟡 Real Example Hindi mein
**Flipkart का product-listing API** 50 products के पूरे details (images URLs, specs, reviews summary, pricing tiers) के साथ average 400KB JSON responses return करता था। Level 6 पर gzip compression enable करने से average response size ~45KB (89% reduction) हो गई — tier-2/3 Indian cities में 3G/4G connections वाले users के लिए, इसने product listing page का time-to-first-render काफी कम किया, क्योंकि network transfer अक्सर server processing time से बड़ा bottleneck था।

---

## 💻 Code Example — Basic

```javascript
// compression-basic.js — enabling gzip compression in Express with one line
const express = require('express');
const compression = require('compression'); // npm install compression
const app = express();

// This single middleware line compresses ALL eligible responses automatically
app.use(compression());

app.get('/products', (req, res) => {
  // Simulate a large JSON response (typical product listing payload)
  const products = Array.from({ length: 200 }, (_, i) => ({
    id: i,
    name: `Product ${i}`,
    description: 'A great product with amazing features and specifications. '.repeat(10),
    price: 999 + i,
    tags: ['electronics', 'bestseller', 'free-shipping'],
  }));
  res.json(products);
  // Express's compression middleware automatically detects the client's
  // Accept-Encoding header and compresses this response, setting
  // Content-Encoding: gzip in the response headers
});

app.listen(3000);

// Verify compression is working:
// curl -H "Accept-Encoding: gzip" -v http://localhost:3000/products | wc -c
// vs
// curl -v http://localhost:3000/products | wc -c   (uncompressed, larger)
```

```javascript
// manual-gzip.js — understanding what the middleware does under the hood
const zlib = require('zlib');
const http = require('http');

const server = http.createServer((req, res) => {
  const jsonData = JSON.stringify({ message: 'x'.repeat(100000) }); // large payload
  const acceptEncoding = req.headers['accept-encoding'] || '';

  if (acceptEncoding.includes('gzip')) {
    // Manually compress the response body with zlib's gzip
    zlib.gzip(jsonData, (err, compressed) => {
      res.setHeader('Content-Encoding', 'gzip'); // tell client how to decompress
      res.setHeader('Content-Type', 'application/json');
      res.end(compressed); // send the SMALLER compressed buffer
    });
  } else {
    // Client doesn't support gzip — send uncompressed
    res.setHeader('Content-Type', 'application/json');
    res.end(jsonData);
  }
});

server.listen(3001);
```

## 💻 Code Example — Advanced

```javascript
// production-compression-config.js — tuning compression for a real API
const express = require('express');
const compression = require('compression');
const app = express();

app.use(compression({
  // Compression level: 1 (fastest, less compression) to 9 (slowest, best compression)
  level: 6, // balanced default — good compression without excessive CPU cost

  // Only compress responses larger than this threshold (bytes) —
  // compressing tiny responses wastes CPU for negligible network benefit
  threshold: 1024, // don't bother compressing responses under 1KB

  // Custom filter: skip compression for already-compressed content types
  filter: (req, res) => {
    const contentType = res.getHeader('Content-Type') || '';
    if (contentType.includes('image/') || contentType.includes('video/')) {
      return false; // images/videos are already compressed — don't re-compress
    }
    return compression.filter(req, res); // use default filter for everything else
  },
}));

// ─── BROTLI SUPPORT (Node 11.7+, via zlib built-in) ───────────────────────
// Modern Express apps can use a library like 'shrink-ray-current' or
// implement manual brotli negotiation for even better compression than gzip
const zlib = require('zlib');

app.get('/large-data', (req, res) => {
  const data = JSON.stringify({ results: new Array(5000).fill({ x: 'sample data' }) });
  const acceptEncoding = req.headers['accept-encoding'] || '';

  if (acceptEncoding.includes('br')) {
    // Brotli typically compresses 15-25% smaller than gzip for text/JSON
    zlib.brotliCompress(data, {
      params: {
        [zlib.constants.BROTLI_PARAM_QUALITY]: 4, // 0-11, balance speed vs ratio
      }
    }, (err, compressed) => {
      res.setHeader('Content-Encoding', 'br');
      res.setHeader('Content-Type', 'application/json');
      res.end(compressed);
    });
  } else if (acceptEncoding.includes('gzip')) {
    zlib.gzip(data, (err, compressed) => {
      res.setHeader('Content-Encoding', 'gzip');
      res.setHeader('Content-Type', 'application/json');
      res.end(compressed);
    });
  } else {
    res.setHeader('Content-Type', 'application/json');
    res.end(data);
  }
});

// ─── MEASURING COMPRESSION RATIO ──────────────────────────────────────────
function measureCompressionRatio(originalData) {
  const original = Buffer.byteLength(originalData);
  const gzipped = zlib.gzipSync(originalData).length;
  const brotli = zlib.brotliCompressSync(originalData).length;

  console.log({
    originalKB: (original / 1024).toFixed(1),
    gzipKB: (gzipped / 1024).toFixed(1),
    gzipSavings: `${(100 - (gzipped / original) * 100).toFixed(1)}%`,
    brotliKB: (brotli / 1024).toFixed(1),
    brotliSavings: `${(100 - (brotli / original) * 100).toFixed(1)}%`,
  });
}
```

---

## 🟠 Express.js Integration

```javascript
// app.js — production-ready setup combining compression with CDN/proxy best practices
const express = require('express');
const compression = require('compression');
const app = express();

// 1. Compression middleware should come EARLY — before route handlers
app.use(compression({ level: 6, threshold: 1024 }));

// 2. For static assets, often better to pre-compress at BUILD time and
// serve the .gz file directly, avoiding runtime compression CPU cost
app.use(express.static('public', {
  // Many reverse proxies (nginx) or CDNs handle static file compression
  // more efficiently than Node's runtime compression — offload when possible
}));

// 3. Note: if behind a reverse proxy (nginx, CDN) that ALREADY compresses
// responses, double-compressing in Express is wasted CPU — pick ONE layer
// to do compression, usually the edge/proxy layer for static content and
// app-level compression for dynamic API responses it doesn't touch

app.get('/api/orders', async (req, res) => {
  const orders = await getOrders(); // large JSON payload
  res.json(orders); // automatically compressed by the middleware above
});

app.listen(3000);

// nginx.conf equivalent (if compression is offloaded to the reverse proxy):
// gzip on;
// gzip_types application/json text/css application/javascript;
// gzip_comp_level 6;
// gzip_min_length 1024;
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Compressing already-compressed binary content (images, videos, zip files)
```javascript
// WRONG: trying to gzip a JPEG wastes CPU — JPEGs are already compressed,
// gzip typically makes them SLIGHTLY LARGER or provides near-zero benefit
app.use(compression()); // without a filter, might attempt to compress everything

// CORRECT: use the filter option to skip already-compressed media types
app.use(compression({
  filter: (req, res) => {
    const type = res.getHeader('Content-Type') || '';
    if (/image|video|zip|gzip/.test(type)) return false;
    return compression.filter(req, res);
  }
}));
```

❌ Mistake 2: Using maximum compression level (9) everywhere without considering CPU cost
```javascript
// WRONG: level 9 squeezes out marginally smaller output but uses
// significantly more CPU per request — under high traffic, this CPU
// cost can become a bigger bottleneck than the bandwidth it saves
app.use(compression({ level: 9 }));

// CORRECT: level 6 is the standard balanced default — test level 4-6
// for high-traffic APIs where CPU matters more than squeezing out the
// last few % of size reduction
app.use(compression({ level: 6 }));
```

---

## 🧠 Tricky Interview Question

**Q: Your API response size dropped from 400KB to 45KB after enabling gzip, but overall P99 latency got slightly WORSE under very high concurrent load. What happened?**
Answer: Compression trades **network transfer time** for **CPU time** — the server now spends extra CPU cycles compressing every response before sending it. Under VERY HIGH concurrent load where CPU is already the bottleneck (many simultaneous requests competing for the same CPU cores), adding compression work to every request can increase CPU contention and INCREASE latency, even though each individual response is now smaller over the wire. This is especially likely if using a high compression level (8-9) or if the server is already CPU-bound from other work. Fixes: lower the compression level (e.g., to 4-6), offload compression to a reverse proxy/CDN layer with more spare capacity, or ensure the app is horizontally scaled (more instances/cores) rather than relying on a single bottlenecked instance to both serve AND compress at peak load.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between gzip and brotli?
A1: Both are HTTP content compression algorithms. gzip (based on DEFLATE) is older, universally supported by virtually all clients. Brotli (developed by Google) generally achieves 15-25% better compression ratios for text content (JSON, HTML, CSS, JS) at similar or better speed, but has slightly less universal client support (though all modern browsers support it). Many production setups serve brotli when the client's `Accept-Encoding` header indicates support, falling back to gzip otherwise.

Q2: Why shouldn't you compress every response regardless of size or type?
A2: Compressing very small responses (a few hundred bytes) adds CPU overhead for negligible network savings — the compression header/metadata overhead can even make tiny payloads LARGER after "compression." Compressing already-compressed binary formats (JPEG, PNG, MP4, ZIP) wastes CPU for zero or even negative benefit since those formats have little remaining redundancy to exploit. Good practice: set a size `threshold` (skip tiny responses) and `filter` out binary media types.

Q3: How does the `Accept-Encoding` / `Content-Encoding` negotiation work?
A3: The CLIENT sends `Accept-Encoding: gzip, br` (or similar) listing formats it can decompress, in priority order. The SERVER picks a format it supports from that list, compresses the response, and sets `Content-Encoding: gzip` (or `br`) in the response so the client knows which decompression algorithm to apply. If the client doesn't send `Accept-Encoding` at all, or the server doesn't support any listed format, the response is sent uncompressed.

Q4: Where is the "best" layer to perform compression — application code, reverse proxy, or CDN?
A4: For static assets (JS/CSS bundles, HTML), pre-compressing at BUILD time or letting a reverse proxy (nginx) / CDN handle it is usually most efficient — they're often more optimized for this and can cache the compressed result, avoiding re-compression per request. For DYNAMIC API responses (JSON that changes per request/user), application-level compression (Express's `compression` middleware) is necessary since there's nothing to pre-compute/cache. Avoid double-compressing the same response at multiple layers — pick one layer per content type.

Q5: What's the tradeoff of a higher compression level, and how would you choose one for a high-traffic API?
A5: Higher levels (7-9) achieve smaller output size but take more CPU time and longer to compress — for high-traffic APIs where many requests are compressed per second, this CPU cost multiplies across the fleet and can become a bottleneck itself. Lower-to-mid levels (4-6) offer a good balance: meaningfully smaller payloads with much less CPU overhead than max level. The right choice depends on measuring actual CPU usage and response size under realistic load — benchmark multiple levels with your real payload shapes before deciding.

---

## 🔷 When to Use + When Not to Use
✅ Use compression when:
- Serving text-based responses (JSON, HTML, CSS, JS) over 1KB in size
- Users are on bandwidth-constrained connections (mobile, international, tier-2/3 markets)
- Network transfer time is a meaningful part of overall response latency

❌ Avoid/skip compression when:
- Content is already compressed (images, videos, pre-gzipped files) — re-compressing wastes CPU
- Response is very small (under ~1KB) — overhead may exceed the benefit
- The server is already CPU-bound at peak load and adding compression work would worsen latency more than it saves in transfer time

---

## 📊 Visual Diagram
```
COMPRESSION NEGOTIATION FLOW:
────────────────────────────────────────────────
  Client Request:
    GET /products
    Accept-Encoding: gzip, br, deflate
         │
         ▼
  Server checks header, picks best supported format (e.g., br)
         │
         ▼
  Compresses response body: 400KB → ~37KB (brotli)
         │
         ▼
  Server Response:
    Content-Encoding: br
    Content-Length: 37000
    [compressed bytes]
         │
         ▼
  Client automatically decompresses → gets back full 400KB JSON

SIZE COMPARISON (typical JSON API payload):
  Uncompressed:  ████████████████████████████████████████  400 KB
  Gzip (L6):     ████                                        45 KB  (89% smaller)
  Brotli (Q4):   ███                                         37 KB  (91% smaller)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| gzip | Widely-supported compression algorithm | Widely-supported compression algorithm |
| brotli | Newer, often smaller compression algorithm | नया, अक्सर छोटा compression algorithm |
| Accept-Encoding | Client header listing supported formats | Client का supported formats header |
| Content-Encoding | Response header stating compression used | Response में बताया गया compression format |
| Compression level | Tradeoff dial between speed and size | Speed और size के बीच tradeoff |
| Threshold | Minimum size before compression kicks in | Compression शुरू होने की minimum size |

---

## ⚡ 3-Line Summary
English:
1. HTTP compression (gzip/brotli) shrinks text-based responses by 70-90%, directly reducing network transfer time, especially impactful for users on slower connections.
2. Use Express's `compression` middleware with a sensible `threshold` and `filter` to skip tiny or already-compressed (image/video) responses.
3. Compression trades network time for CPU time — tune the level (usually 4-6) based on measured CPU impact under real traffic, and avoid double-compressing at multiple layers (proxy + app).

Hindi:
1. HTTP compression (gzip/brotli) text-based responses को 70-90% तक छोटा करता है, network transfer time directly कम होता है, खासकर slower connections वाले users के लिए।
2. Express के `compression` middleware को sensible `threshold` और `filter` के साथ use करो ताकि छोटे या already-compressed (image/video) responses skip हो जाएं।
3. Compression network time को CPU time से trade करता है — level को (आम तौर पर 4-6) real traffic में measured CPU impact के आधार पर tune करो, और कई layers (proxy + app) में double-compress करने से बचो।

---

## ➡️ Next Topic
**225. HTTP/2 in Node.js** — multiplexing, header compression, और server push से multiple requests को ज़्यादा efficiently handle करना।
