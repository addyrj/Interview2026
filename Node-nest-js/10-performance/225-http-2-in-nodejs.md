# 225. HTTP/2 in Node.js
# हिंदी में: HTTP/2 — Multiplexing से Multiple Requests को Efficiently Handle करना

---

## 🔵 Simple Definition (English)
**HTTP/2** is a major revision of the HTTP protocol that allows **multiplexing** (many requests/responses over a SINGLE TCP connection simultaneously, no head-of-line blocking per-request), **header compression** (HPACK, reducing repetitive header overhead), and **server push**. Node.js has a built-in `http2` core module for building HTTP/2 servers directly, without needing Express's HTTP/1.1-only assumptions in some setups (though Express can run over HTTP/2 via compatibility layers too).

## 🔵 सरल परिभाषा (Hindi)
**HTTP/2** HTTP protocol का एक बड़ा revision है जो **multiplexing** (एक SINGLE TCP connection पर एक साथ कई requests/responses, per-request head-of-line blocking नहीं), **header compression** (HPACK, repetitive header overhead कम करना), और **server push** allow करता है। Node.js में built-in `http2` core module है directly HTTP/2 servers बनाने के लिए।

---

## 🔴 Problem it Solves
HTTP/1.1 requires either opening multiple TCP connections (browsers cap this at ~6 per domain) or serializing requests over one connection, both limiting how many resources a page can fetch in parallel — and each connection has its own TCP handshake + TLS negotiation overhead. HTTP/1.1 also re-sends full headers (cookies, user-agent, etc.) on EVERY request, even though they're often identical across requests. HTTP/2 solves both: one connection carries many concurrent streams (no connection-count limit problem), and HPACK compresses repeated headers, cutting overhead especially noticeable on pages/APIs making many small requests.

## 🔴 यह क्यों बना? (Hindi)
HTTP/1.1 को या तो कई TCP connections खोलने पड़ते हैं (browsers ~6 per domain तक limit करते हैं) या एक connection पर requests serialize करने पड़ते हैं, दोनों limit करते हैं कि एक page कितने resources parallel में fetch कर सकता है — और हर connection का अपना TCP handshake + TLS negotiation overhead होता है। HTTP/1.1 हर request पर पूरे headers (cookies, user-agent, etc.) फिर भेजता है, भले ही वो अक्सर identical हों। HTTP/2 दोनों solve करता है: एक connection पर कई concurrent streams चलते हैं, और HPACK repeated headers compress करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Client and server negotiate HTTP/2 during the TLS handshake (via ALPN — Application-Layer Protocol Negotiation); HTTP/2 over plaintext (`h2c`) exists but is rarely used in browsers
Step 2 → A single TCP+TLS connection is established once (one handshake cost, not per-request)
Step 3 → Multiple requests become independent **streams** multiplexed over that one connection — stream 1's response can arrive interleaved with stream 2's, with no need to wait in line
Step 4 → Headers are compressed with **HPACK**, which maintains a shared compression context so repeated header fields (cookies, auth tokens) aren't retransmitted in full every time
Step 5 → Optionally, the server can **push** resources it knows the client will need (e.g., push a CSS file when HTML is requested) before the client even asks — though server push is now less commonly used due to caching complexities and is being phased out of some implementations in favor of preload hints
Step 6 → Node.js apps use the built-in `http2` module for native servers, or run behind HTTP/2-terminating reverse proxies (nginx, CDN) with HTTP/1.1 internally for simplicity

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client और server TLS handshake के दौरान HTTP/2 negotiate करते हैं (ALPN से); plaintext HTTP/2 (`h2c`) exist करता है पर browsers में rarely use होता है
Step 2 → एक single TCP+TLS connection एक बार बनता है (handshake cost per-request नहीं)
Step 3 → Multiple requests independent **streams** बन जाते हैं जो उस एक connection पर multiplex होते हैं — stream 1 का response stream 2 के साथ interleaved आ सकता है, line में wait करने की ज़रूरत नहीं
Step 4 → Headers **HPACK** से compress होते हैं, जो shared compression context maintain करता है ताकि repeated header fields (cookies, auth tokens) हर बार पूरे न भेजे जाएं
Step 5 → Optionally, server resources **push** कर सकता है जो client को चाहिए होंगे, client के पूछे बिना
Step 6 → Node.js apps built-in `http2` module से native servers बनाते हैं, या HTTP/2-terminating reverse proxies (nginx, CDN) के पीछे चलते हैं internally HTTP/1.1 के साथ simplicity के लिए

---

## 🟡 Real World Example
**Myntra's product page** loads dozens of resources per page view: the main HTML, several JS bundles, CSS files, and dozens of product thumbnail images — all from the same domain. Under HTTP/1.1, browsers were limited to ~6 parallel connections per domain, so most of these 40+ requests had to queue and wait. After migrating their CDN/edge layer to HTTP/2, all 40+ requests multiplex over a SINGLE connection with no artificial 6-connection cap, meaningfully improving page load time, especially for users on higher-latency mobile networks where each additional connection's handshake cost was previously multiplied by the number of connections needed.

## 🟡 Real Example Hindi mein
**Myntra का product page** हर page view पर दर्जनों resources load करता है: main HTML, कई JS bundles, CSS files, और दर्जनों product thumbnail images — सब same domain से। HTTP/1.1 में, browsers ~6 parallel connections per domain तक limited थे, तो 40+ requests में से ज़्यादातर को queue में wait करना पड़ता था। CDN/edge layer को HTTP/2 में migrate करने के बाद, सभी 40+ requests एक SINGLE connection पर multiplex होते हैं, page load time काफी improve हुआ।

---

## 💻 Code Example — Basic

```javascript
// http2-basic-server.js — a native HTTP/2 server using Node's built-in module
// HTTP/2 generally REQUIRES TLS in browsers, so we need certificates
// (for local testing, generate self-signed certs with openssl)
const http2 = require('http2');
const fs = require('fs');

const server = http2.createSecureServer({
  key: fs.readFileSync('./localhost-key.pem'),
  cert: fs.readFileSync('./localhost-cert.pem'),
});

server.on('stream', (stream, headers) => {
  // Each `stream` here represents one multiplexed HTTP/2 request/response
  const path = headers[':path'];

  if (path === '/') {
    stream.respond({
      ':status': 200,
      'content-type': 'text/html',
    });
    stream.end('<h1>Hello over HTTP/2!</h1>');
  } else {
    stream.respond({ ':status': 404 });
    stream.end('Not found');
  }
});

server.on('error', (err) => console.error('Server error:', err));
server.listen(3000, () => console.log('HTTP/2 server running on https://localhost:3000'));

// Test with: curl --http2 -k https://localhost:3000/
// (-k skips cert validation for self-signed certs in local testing)
```

```javascript
// http2-multiple-streams.js — demonstrating multiplexing with multiple parallel requests
const http2 = require('http2');
const fs = require('fs');

const server = http2.createSecureServer({
  key: fs.readFileSync('./localhost-key.pem'),
  cert: fs.readFileSync('./localhost-cert.pem'),
});

server.on('stream', (stream, headers) => {
  const path = headers[':path'];
  // Simulate different response times for different "resources"
  const delay = path === '/slow-resource' ? 500 : 10;

  setTimeout(() => {
    stream.respond({ ':status': 200, 'content-type': 'application/json' });
    stream.end(JSON.stringify({ path, servedAt: Date.now() }));
  }, delay);
  // Even though /slow-resource takes 500ms, OTHER concurrent streams on the
  // SAME connection are NOT blocked waiting for it — true multiplexing
});

server.listen(3000);
```

## 💻 Code Example — Advanced

```javascript
// express-http2-compat.js — running Express.js over HTTP/2 via a compatibility layer
// Express itself is built around the HTTP/1.x `req`/`res` API, but 'spdy' or
// manual adaptation lets it run under HTTP/2 transparently
const spdy = require('spdy'); // npm install spdy — supports HTTP/2 with Express-style API
const express = require('express');
const fs = require('fs');

const app = express();

app.get('/api/products', (req, res) => {
  res.json({ products: ['item1', 'item2'] });
});

app.get('/api/users', (req, res) => {
  res.json({ users: ['user1', 'user2'] });
});

const server = spdy.createServer({
  key: fs.readFileSync('./localhost-key.pem'),
  cert: fs.readFileSync('./localhost-cert.pem'),
}, app);

server.listen(3000, () => console.log('Express app running over HTTP/2 on :3000'));

// ─── PRODUCTION PATTERN: terminate HTTP/2 at a reverse proxy/CDN ─────────
// Most production Node.js apps DON'T implement HTTP/2 directly — instead:
//   Browser <--HTTP/2--> CDN/nginx/ALB <--HTTP/1.1--> Node.js app (Express)
// The proxy/CDN handles the HTTP/2 complexity (multiplexing, HPACK) with
// clients, while talking simple HTTP/1.1 to the backend Node app — this is
// simpler to operate and lets you use plain Express without http2/spdy

// nginx.conf relevant snippet:
// server {
//   listen 443 ssl http2;    # HTTP/2 enabled for client-facing connections
//   location / {
//     proxy_pass http://localhost:3000;  # plain HTTP/1.1 to the Node app
//   }
// }

// ─── CHECKING NEGOTIATED PROTOCOL IN CODE ─────────────────────────────────
server.on('stream', (stream, headers) => {
  console.log('Request via HTTP version:', stream.session.alpnProtocol); // 'h2'
});
```

---

## 🟠 Express.js Integration

```javascript
// Most Express apps rely on the infrastructure layer (nginx, CDN, load balancer,
// cloud provider's HTTPS termination) to handle HTTP/2 with clients, while
// the Express app itself continues using plain HTTP/1.1 internally — this is
// the PRAGMATIC, most common real-world setup since Express's core routing
// and middleware model doesn't need to change at all.

// What DOES matter for your Express app when HTTP/2 is used upstream:
// 1. Fewer artificial "connection limit" concerns — you can serve many
//    small resources (images, API calls) without worrying about browsers
//    capping concurrent connections
// 2. Server push is largely deprecated/removed in modern browsers (Chrome
//    removed support) — use <link rel="preload"> hints in HTML instead
// 3. Ensure your CDN/proxy config actually has "http2" enabled in its
//    listener directive — simply using HTTPS doesn't automatically mean HTTP/2

// If you want END-TO-END HTTP/2 (browser all the way to Node, no proxy),
// use Node's native http2 module or a library like 'spdy'/'http2-express-bridge'
// that adapts the http2 stream API to Express's req/res interface:
const http2Express = require('http2-express-bridge');
const express = require('express');
const http2 = require('http2');
const fs = require('fs');

const app = http2Express(express); // wraps Express for HTTP/2 compatibility

app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

const server = http2.createSecureServer({
  key: fs.readFileSync('./key.pem'),
  cert: fs.readFileSync('./cert.pem'),
  allowHTTP1: true, // fallback for clients that don't support HTTP/2
}, app);

server.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming enabling HTTPS automatically means HTTP/2 is active
```javascript
// WRONG assumption: "I use HTTPS, so I must be on HTTP/2"
// HTTPS and HTTP/2 are DIFFERENT, independent things — you can run plain
// HTTP/1.1 over TLS just fine. HTTP/2 must be EXPLICITLY negotiated via ALPN.

// CORRECT: explicitly configure your server/proxy/CDN for HTTP/2, and verify:
// curl -I --http2 https://yourapp.com   (look for "HTTP/2 200" in the response)
// or check in browser DevTools → Network tab → Protocol column shows "h2"
```

❌ Mistake 2: Still manually bundling/concatenating assets to reduce request count, as if still on HTTP/1.1
```javascript
// WRONG (HTTP/1.1-era optimization, often unnecessary on HTTP/2):
// combining all JS files into one giant bundle specifically to minimize
// request COUNT — this was crucial under HTTP/1.1's connection limits but
// can actually HURT caching efficiency under HTTP/2 (one small change
// invalidates the entire giant bundle's cache)

// BETTER under HTTP/2: smaller, more granular bundles/files are fine since
// multiplexing removes the per-request overhead penalty — this improves
// caching (unchanged files stay cached) without the old request-count tax
```

---

## 🧠 Tricky Interview Question

**Q: Does HTTP/2 make individual requests FASTER, or does it mainly help when making MANY requests?**
Answer: HTTP/2's main benefit is for scenarios with MANY concurrent requests to the same origin — multiplexing eliminates the HTTP/1.1 connection-limit bottleneck and head-of-line blocking, and HPACK reduces repeated header overhead across many requests. For a SINGLE isolated request, HTTP/2 doesn't inherently make the actual data transfer or server processing faster — the improvement comes from better utilization of one connection across MANY requests, not from speeding up any one request's core transfer. This is why HTTP/2's biggest wins show up on pages/APIs that fetch dozens of resources (typical web pages with many assets), and why a simple single-request API benchmark might show negligible difference between HTTP/1.1 and HTTP/2.

---

## ⚫ Interview Questions + Answers

Q1: What is multiplexing in HTTP/2 and what problem does it solve?
A1: Multiplexing allows multiple independent request/response "streams" to be interleaved over a SINGLE TCP connection simultaneously — a slow response on one stream doesn't block other streams from completing. This solves HTTP/1.1's limitations: browsers capping concurrent connections per domain (~6), and head-of-line blocking where one slow request could delay others queued behind it on the same connection.

Q2: What is HPACK and why does it matter?
A2: HPACK is HTTP/2's header compression algorithm. It maintains a shared compression context between client and server across the connection's lifetime, so repeated header fields (cookies, authorization tokens, user-agent strings that are identical across many requests) are sent as small references instead of full text every time — significantly reducing overhead for APIs/pages making many requests with similar headers.

Q3: Why has server push become less commonly used despite being part of the HTTP/2 spec?
A3: Server push lets the server proactively send resources before the client asks, but in practice it caused issues: servers often pushed resources the client ALREADY had cached (wasting bandwidth), and it was hard for servers to know precisely what the client needs. Chrome removed server push support, and most modern approaches prefer `<link rel="preload">` resource hints (client-driven, cache-aware) over server push for similar goals.

Q4: How do most production Node.js deployments actually implement HTTP/2?
A4: Most terminate HTTP/2 at the edge — a CDN, load balancer, or reverse proxy (nginx) that speaks HTTP/2 to clients but forwards requests to the Node.js app over plain HTTP/1.1 internally. This is simpler to operate since the Node/Express app code doesn't need to change at all, and the proxy layer is typically well-optimized for protocol negotiation. True end-to-end HTTP/2 (Node app speaking HTTP/2 directly to clients) is less common and used mainly when there's no intermediary proxy layer.

Q5: Does HTTP/2 require TLS/HTTPS?
A5: Not technically per the spec (an unencrypted variant called `h2c` exists), but in practice, ALL major browsers only support HTTP/2 over TLS — they refuse to negotiate HTTP/2 over plaintext connections. So for any browser-facing HTTP/2 deployment, TLS is effectively mandatory. `h2c` is sometimes used for server-to-server communication where TLS isn't needed for that specific hop.

---

## 🔷 When to Use + When Not to Use
✅ Use/enable HTTP/2 when:
- Serving pages/APIs that make many concurrent requests to the same domain (typical web apps with many assets)
- You want to reduce the overhead of repeated headers across many API calls (mobile apps polling frequently)
- Your CDN/proxy layer already supports it easily (often just a config flag away)

❌ Less critical when:
- Your API serves very few, large requests per client session (the multiplexing benefit is minimal with low request counts)
- You're optimizing a simple internal service-to-service call where connection reuse (keep-alive) under HTTP/1.1 already performs adequately

---

## 📊 Visual Diagram
```
HTTP/1.1 vs HTTP/2:
────────────────────────────────────────────────
HTTP/1.1 (limited parallel connections, ~6/domain):
  Connection 1: [Req A]────[Resp A]  [Req D]────[Resp D]
  Connection 2: [Req B]────[Resp B]
  Connection 3: [Req C]──────────────[Resp C]  (slow, blocks queue behind it)
  ... up to connection limit, others must WAIT

HTTP/2 (single connection, multiplexed streams):
  Connection 1 (ONE TCP+TLS connection):
    Stream 1: [Req A]──[Resp A]
    Stream 2: [Req B]────────[Resp B]
    Stream 3: [Req C]──────────────────[Resp C]  (slow, but doesn't block others!)
    Stream 4: [Req D]──[Resp D]
  All interleaved over the SAME connection, no artificial connection-count limit
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multiplexing | Many streams over one connection | एक connection पर कई streams |
| HPACK | HTTP/2's header compression | HTTP/2 का header compression |
| Stream | Independent request/response within a connection | Connection के अंदर independent request/response |
| Head-of-line blocking | One slow request delaying others queued behind it | एक slow request से बाकी delay होना |
| ALPN | TLS extension negotiating HTTP version | TLS में HTTP version negotiate करना |
| Server push | Server proactively sending resources | Server का proactively resources भेजना |

---

## ⚡ 3-Line Summary
English:
1. HTTP/2 multiplexes many requests over a single TCP connection, removing HTTP/1.1's connection-count limits and head-of-line blocking, with HPACK reducing repeated header overhead.
2. Its biggest benefit shows up for pages/APIs making MANY concurrent requests, not for speeding up a single isolated request.
3. Most production Node.js apps let a CDN/reverse proxy handle HTTP/2 with clients while the Express app continues speaking plain HTTP/1.1 internally — simpler and usually sufficient.

Hindi:
1. HTTP/2 एक single TCP connection पर कई requests multiplex करता है, HTTP/1.1 की connection-count limits और head-of-line blocking हटाता है, HPACK repeated header overhead कम करता है।
2. इसका सबसे बड़ा फायदा उन pages/APIs के लिए है जो कई concurrent requests बनाते हैं, एक isolated request को तेज़ करने के लिए नहीं।
3. ज़्यादातर production Node.js apps CDN/reverse proxy को clients के साथ HTTP/2 handle करने देते हैं जबकि Express app internally plain HTTP/1.1 बोलता रहता है — simpler और usually पर्याप्त।

---

## ➡️ Next Topic
**226. Cluster Mode — Multi Core** — Node.js के `cluster` module से सभी CPU cores use करना multiple worker processes चला कर।
