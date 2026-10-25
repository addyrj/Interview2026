# 290. Build URL Shortener API
# हिंदी में: URL Shortener API कैसे बनायें

---

## 🔵 Simple Definition (English)
A **URL shortener** (like bit.ly) takes a long URL and generates a short unique code (e.g., `abc123`) that redirects to the original URL. It needs a fast lookup store, a collision-free code generation strategy, and a high-throughput redirect endpoint.

## 🔵 सरल परिभाषा (Hindi)
**URL shortener** (bit.ly जैसा) एक long URL लेकर एक short unique code (जैसे `abc123`) बनाता है जो original URL पर redirect करता है। इसके लिए fast lookup store, collision-free code generation strategy, और high-throughput redirect endpoint चाहिए।

---

## 🔴 Problem it Solves
Long URLs (with tracking params, deep paths) are ugly to share on SMS, Twitter (char limits), or print media/QR codes. A shortener gives a compact, memorable, trackable link, and also enables click analytics, link expiry, and custom branded domains.

## 🔴 यह क्यों बना? (Hindi)
Long URLs (tracking params, deep paths के साथ) SMS, Twitter (character limit) या print/QR code पर share करने में ugly होते हैं। Shortener एक compact, memorable, trackable link देता है, साथ ही click analytics, link expiry, custom branded domain भी possible बनाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Client POSTs a long URL to `/shorten`.
Step 2 → Server generates a unique short code — either by hashing the URL (base62 of MD5/CRC) + collision check, or by using an auto-increment ID converted to base62.
Step 3 → Server stores `{shortCode -> longUrl, createdAt, expiresAt, clicks}` in DB (and warms a cache).
Step 4 → Server returns `https://short.ly/abc123` to client.
Step 5 → When someone visits `/abc123`, server looks up `abc123` in cache (Redis) first, falls back to DB, increments click count asynchronously, then issues a 301/302 redirect.
Step 6 → Expired/deleted codes return 404 or a "link expired" page.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client `/shorten` पर long URL POST करता है।
Step 2 → Server unique short code बनाता है — या तो URL hash (MD5/CRC का base62) + collision check से, या auto-increment ID को base62 में convert करके।
Step 3 → Server `{shortCode -> longUrl, createdAt, expiresAt, clicks}` DB में store करता है (और cache warm करता है)।
Step 4 → Server client को `https://short.ly/abc123` return करता है।
Step 5 → कोई `/abc123` visit करे तो server पहले cache (Redis) check करता है, फिर DB, click count async increment करता है, फिर 301/302 redirect भेजता है।
Step 6 → Expired/deleted codes पर 404 या "link expired" page आता है।

---

## 🟡 Real World Example
**Zomato** shares short tracked links in SMS/WhatsApp for order status (`zmt.link/xk29A`) instead of a 200-character deep link with UTM params. Each click is logged for marketing analytics (which campaign drove the click), and links can expire after the promo ends — all powered by a URL shortener microservice backed by Redis for fast redirects at massive scale.

## 🟡 Real Example Hindi mein
**Zomato** SMS/WhatsApp में order status के लिए short tracked link (`zmt.link/xk29A`) भेजता है, 200-character वाले deep link के बजाय। हर click marketing analytics के लिए log होता है (कौनसी campaign से click आया), और promo खत्म होने पर link expire हो सकता है — यह सब एक URL shortener microservice करता है जो Redis के साथ massive scale पर fast redirects देता है।

---

## 💻 Code Example — Basic

```javascript
// shortener-basic.js
// In-memory URL shortener using base62 counter encoding. Run: node shortener-basic.js

const BASE62 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

// In-memory store: shortCode -> longUrl (would be a DB table in real app)
const store = new Map();
let counter = 1000; // start away from 0 so codes aren't too short initially

// Convert a number to base62 string — compact, URL-safe encoding
function toBase62(num) {
  let result = '';
  while (num > 0) {
    result = BASE62[num % 62] + result;
    num = Math.floor(num / 62);
  }
  return result || '0';
}

// Create a short URL for a given long URL
function shorten(longUrl) {
  const code = toBase62(counter++);          // unique, collision-free (counter never repeats)
  store.set(code, { longUrl, clicks: 0, createdAt: Date.now() });
  return code;
}

// Resolve a short code back to the long URL, tracking clicks
function resolve(code) {
  const entry = store.get(code);
  if (!entry) return null;
  entry.clicks++;               // analytics
  return entry.longUrl;
}

// --- Demo ---
const code1 = shorten('https://www.zomato.com/mumbai/restaurant/123?utm_source=sms&utm_campaign=promo');
console.log('Short code:', code1);                 // e.g. "g8"
console.log('Resolved:', resolve(code1));           // original long URL
console.log('Resolved again:', resolve(code1));     // clicks incremented
console.log('Unknown code:', resolve('zzzz'));       // null -> 404 in real API
```

## 💻 Code Example — Advanced

```javascript
// shortener-advanced.js
// Production-style shortener: Express + Redis cache + Postgres-like store simulation + collision-safe hashing
// npm i express ioredis crypto (crypto is built-in)
const crypto = require('crypto');
const Redis = require('ioredis');

const redis = new Redis(); // Redis cache layer for hot reads

// Simulated DB (replace with real Postgres/Mongo calls in production)
const db = {
  rows: new Map(), // shortCode -> { longUrl, expiresAt, clicks }
  async insert(code, longUrl, expiresAt) {
    this.rows.set(code, { longUrl, expiresAt, clicks: 0 });
  },
  async find(code) {
    return this.rows.get(code) || null;
  },
  async incrementClicks(code) {
    const row = this.rows.get(code);
    if (row) row.clicks++;
  },
};

// Generate a short code from the URL hash, base62-encoded, with collision retry
function hashToBase62(input, length = 7) {
  const hash = crypto.createHash('sha256').update(input).digest('hex');
  // Take hex digest, convert a slice to a big int, then to base62-ish via base36 for simplicity
  const num = BigInt('0x' + hash.slice(0, 12));
  return num.toString(36).slice(0, length); // base36 keeps it URL-safe and short
}

async function createShortUrl(longUrl, ttlDays = 365) {
  let code = hashToBase62(longUrl + Date.now()); // salt with timestamp to reduce collisions on re-shorten
  let attempt = 0;

  // Collision check loop — extremely rare with sha256 + timestamp salt, but must be handled
  while (await db.find(code)) {
    attempt++;
    code = hashToBase62(longUrl + Date.now() + attempt);
    if (attempt > 5) throw new Error('Could not generate unique code, try again');
  }

  const expiresAt = Date.now() + ttlDays * 24 * 60 * 60 * 1000;
  await db.insert(code, longUrl, expiresAt);

  // Pre-warm cache so first redirect is also fast
  await redis.set(`url:${code}`, longUrl, 'EX', ttlDays * 86400);

  return code;
}

async function resolveShortUrl(code) {
  // 1. Try cache first (hot path — most redirects hit this)
  const cached = await redis.get(`url:${code}`);
  if (cached) {
    db.incrementClicks(code); // fire-and-forget, don't block redirect on analytics write
    return cached;
  }

  // 2. Cache miss -> fall back to DB
  const row = await db.find(code);
  if (!row) return null; // 404
  if (row.expiresAt < Date.now()) return null; // expired -> treat as not found

  // 3. Repopulate cache for next time
  await redis.set(`url:${code}`, row.longUrl, 'EX', 86400);
  db.incrementClicks(code);
  return row.longUrl;
}

module.exports = { createShortUrl, resolveShortUrl };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — full shortener API with Express
const express = require('express');
const { createShortUrl, resolveShortUrl } = require('./shortener-advanced');

const app = express();
app.use(express.json());

const BASE_DOMAIN = 'https://short.ly';

// POST /shorten — create a short link
app.post('/shorten', async (req, res) => {
  const { url } = req.body;

  // Basic validation — never trust client input
  try {
    new URL(url); // throws if invalid URL format
  } catch {
    return res.status(400).json({ error: 'Invalid URL' });
  }

  const code = await createShortUrl(url);
  res.status(201).json({ shortUrl: `${BASE_DOMAIN}/${code}`, code });
});

// GET /:code — redirect to the original URL (the hot path, must be fast)
app.get('/:code', async (req, res) => {
  const longUrl = await resolveShortUrl(req.params.code);
  if (!longUrl) return res.status(404).json({ error: 'Link not found or expired' });

  // 301 = permanent (SEO-friendly, browser caches it); 302 = temporary (lets you track every click)
  res.redirect(302, longUrl);
});

app.listen(3000, () => console.log('URL shortener on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using 301 (permanent) redirects when you need click analytics
✅ Correct: Use 302 so the browser hits your server every time instead of caching the redirect

```javascript
// Wrong — browser caches this forever, you lose click counts after first visit
res.redirect(301, longUrl);

// Right — browser re-checks with your server each time
res.redirect(302, longUrl);
```

❌ Mistake 2: Using a naive incrementing integer ID directly as the public code
✅ Correct: Base62-encode it (or hash it) so codes aren't guessable/sequential (security + avoids enumeration attacks)

```javascript
// Wrong — exposes total link count, easy to enumerate all short URLs
app.get(`/short/${id}`); // id = 1, 2, 3...

// Right
const code = toBase62(id); // "G8", "h2A" — compact and non-obvious
```

---

## 🧠 Tricky Interview Question

```javascript
// Two requests arrive at the exact same millisecond for the SAME long URL
createShortUrl('https://example.com/a');
createShortUrl('https://example.com/a');
```
Answer: If the hash function uses only `url + Date.now()` and both calls land in the same millisecond, they could generate the **same code**, causing a collision. The fix shown in the advanced example mitigates this with a `while (await db.find(code))` collision-retry loop plus an `attempt` salt — but a truly race-safe system should rely on a DB-level unique constraint on `shortCode` and catch the duplicate-key error to retry, since two concurrent requests could both pass the "not found" check before either insert completes (a classic TOCTOU race). The robust answer: use `INSERT ... ON CONFLICT` / unique index + retry, not just an application-level check.

---

## ⚫ Interview Questions + Answers

Q1: How do you choose between hash-based codes and auto-increment + base62 codes?
A1: Auto-increment + base62 guarantees no collisions and very short codes early on, but requires a centralized counter (or distributed ID generator like Snowflake) and can leak growth rate. Hash-based codes are stateless and parallelizable but need collision handling. Most production systems use a distributed unique ID (DB sequence, Snowflake ID, or UUID shortened) then base62-encode it.

Q2: How do you handle 10,000 redirects/second?
A2: Put a Redis (or CDN edge) cache in front of the DB for shortCode -> longUrl lookups since reads vastly outnumber writes. Use read replicas for DB fallback. Keep the redirect handler lightweight — no heavy middleware, async-log clicks instead of blocking on a DB write.

Q3: How would you add link expiry?
A3: Store `expiresAt` with each row; check it on resolve and treat expired as 404. Set Redis cache TTL to match expiry, so expired links auto-evict without a cleanup job. Optionally run a background job to purge expired rows from the DB.

Q4: How do you prevent abuse (e.g., shortening malicious/phishing URLs)?
A4: Validate URL scheme (http/https only), check against a blocklist/Google Safe Browsing API before creating the short link, rate-limit the `/shorten` endpoint per IP/API key, and allow reporting + disabling malicious codes.

Q5: Custom aliases — how do you support `short.ly/my-brand` instead of a random code?
A5: Allow an optional `customAlias` field in the request; check uniqueness in DB (unique constraint), fall back to auto-generated code if taken or not provided. Validate alias characters (alphanumeric + hyphen only) to avoid path-traversal or XSS-prone values.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Sharing links in SMS/social media with character limits
- You need click analytics/tracking per shared link
- Branded or memorable short domains improve trust/CTR

❌ Avoid when:
- Internal-only links where readability of the full URL matters more (e.g., internal admin tools)
- Extremely latency-sensitive paths where even a redirect hop isn't acceptable (link directly instead)

---

## 📊 Visual Diagram
```
 POST /shorten                         GET /abc123
 ┌────────────┐                        ┌────────────┐
 │ long URL   │                        │ short code │
 └─────┬──────┘                        └─────┬──────┘
       ▼                                     ▼
 generate code (hash/base62)           Redis cache lookup
       │                                     │ hit          miss
       ▼                                     ▼               ▼
 store in DB + warm cache             return longUrl     DB lookup → cache it
       │                                     │                     │
       ▼                                     ▼                     ▼
 return short URL                      302 Redirect ◀──────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Base62 | Encoding using [a-zA-Z0-9] (62 chars) | 62 characters वाला encoding |
| Collision | Two inputs producing same short code | दो inputs का same code बनना |
| TTL | Time-to-live, expiry duration | Expiry की अवधि |
| 301 vs 302 | Permanent vs temporary redirect | Permanent बनाम temporary redirect |
| Hot path | Most frequently executed code path | सबसे ज़्यादा चलने वाला code path |

---

## ⚡ 3-Line Summary
English: A URL shortener maps a long URL to a compact unique code via hashing or base62-encoded IDs, stores the mapping with cache-first reads, and redirects with 302 to preserve click analytics. Collision handling and cache warming are the key engineering concerns at scale.
Hindi: URL shortener long URL को hashing या base62-encoded ID से compact unique code में map करता है, cache-first reads के साथ mapping store करता है, और click analytics बचाने के लिए 302 redirect use करता है। Scale पर collision handling और cache warming मुख्य concerns हैं।

---

## ➡️ Next Topic
**291. Build Payment API (Stripe/Razorpay)** — webhook security, idempotency keys, and payment state machines.
