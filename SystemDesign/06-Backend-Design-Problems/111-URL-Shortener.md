# 111. URL Shortener (bit.ly / TinyURL)
# हिंदी में: URL Shortener — लंबे URL को छोटे code (जैसे myapp.in/aZ3k9) में बदलना, और उस छोटे link पर क्लिक करते ही असली URL पर redirect करना

---

## 🔵 Simple Definition (English)
A **URL shortener** maps a long URL (`https://shop.com/products/123?utm_source=insta&...`) to a short, unique code (`sho.rt/aZ3k9`). Visiting the short link **redirects** (HTTP 301/302) to the original URL. Extras: custom aliases, expiry, click analytics, QR codes, abuse protection.
It's the classic system design interview warm-up: it tests **ID generation, read-heavy scaling, caching, database choice and analytics pipelines**.

## 🔵 सरल परिभाषा (Hindi)
URL shortener लंबे link को छोटे code में बदलता है (sho.rt/aZ3k9); छोटे link पर जाते ही सर्वर असली URL पर redirect कर देता है।
इंटरव्यू में यह ID बनाना, ज़्यादा पढ़ने वाले सिस्टम को स्केल करना, caching, DB चुनना और clicks की analytics परखता है।

---

## 🔴 Problem it Solves
- Long URLs are ugly, break in SMS/WhatsApp messages, and exceed character limits (SMS 160 chars).
- Marketers need **click tracking** (how many, from where, which device) per campaign.
- Links in printed material (QR codes) should be **changeable** later (dynamic links).
- Businesses want **branded short domains** (amzn.to, fkrt.it).

## 🔴 यह क्यों बना? (Hindi)
लंबे URL बदसूरत होते हैं, SMS/WhatsApp में टूट जाते हैं; marketing वालों को हर campaign के clicks (कितने, कहाँ से, कौन-सा device) चाहिए; छपे हुए QR code का link बाद में बदलना पड़ सकता है; कंपनियाँ अपना छोटा domain चाहती हैं (amzn.to)।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional:
  - POST long URL → get short URL (optional custom alias, optional expiry)
  - GET short URL → redirect to long URL (fast!)
  - Click analytics per link (count, time series, country, device, referrer)
  - (Optional) user accounts, link management, delete/disable link
Non-functional:
  - Very read-heavy (redirects ≫ creations, ~100:1)
  - Redirect latency p99 < 50 ms (it's in the user's critical path)
  - High availability (broken links = broken campaigns): 99.99% for redirects
  - Short codes unique, not easily guessable/enumerable (for private links)
  - Durable: links must work for years
```

### 2. Back-of-envelope estimation

```
New links: 100M/month ≈ 40/s average (peak ×5 = 200/s)
Redirects: 100:1 → 10B/month ≈ 4,000/s average, peak ~20,000/s
Storage: 100M/month × 12 × 5 years = 6B links × ~500 bytes ≈ 3 TB (+ indexes)
Code length: base62 (a–z A–Z 0–9) → 62^7 ≈ 3.5 trillion codes → 7 chars is plenty
Cache: 20% of links get 80% of traffic → cache hot links: e.g. 50M × 500 B ≈ 25 GB Redis
Analytics events: 10B clicks/month → stream to Kafka → OLAP (ClickHouse)
```

### 3. API

```
POST /api/v1/links           { "url": "https://...", "alias": "diwali-sale", "expiresAt": "..." }
   → 201 { "code": "aZ3k9Lp", "shortUrl": "https://sho.rt/aZ3k9Lp" }
GET  /{code}                 → 302 Location: https://long-url   (or 301)
GET  /api/v1/links/{code}/stats?from=&to=   → { clicks, byDay[], byCountry[], byDevice[] }
DELETE /api/v1/links/{code}  → disable
```

### 4. 301 vs 302 (classic question)

```
301 Moved Permanently → browsers/CDNs CACHE the redirect → fewer hits to us, faster for user,
                         but we LOSE analytics for repeat clicks and can't change the destination easily
302 Found (temporary) → every click hits our server → full analytics, editable destination
Most commercial shorteners use 301/302 deliberately; for analytics → 302 (or 301 with short cache).
```

### 5. Short code generation (the heart of the problem)

```
Option A: Hash the URL (MD5/SHA-256 → base62 → take 7 chars)
   ✅ same URL → same code (dedup)   ❌ collisions → must check & re-hash with salt; dedup not always wanted

Option B: Auto-increment ID → base62 encode  (id 125 → "21")
   ✅ no collisions, short   ❌ predictable/enumerable (scrapers can walk all links), single DB counter
   → scramble: encode(permute(id)) using a bijective function (e.g., Feistel cipher / Hashids / Sqids)

Option C: Pre-generated key ranges (Key Generation Service) ⭐ common answer
   KGS hands out RANGES of IDs (e.g. 1,000,000–1,999,999) to each app server; server encodes locally
   ✅ no coordination per request, no collisions, scales horizontally   ❌ unused range IDs lost on crash (fine)

Option D: Random 7-char base62 + uniqueness check (INSERT ... unique constraint, retry on conflict)
   ✅ unguessable, simple   ❌ collision probability rises as table fills (birthday problem) → use 8 chars

Option E: Snowflake-style 64-bit IDs → base62 (~11 chars) — unique without coordination, longer codes

Custom alias: check uniqueness, reserve list (admin, api, login), profanity filter.
```

### 6. Data model

```
links
  code         VARCHAR(10) PRIMARY KEY      -- or BIGINT id + derived code
  long_url     TEXT NOT NULL
  user_id      BIGINT NULL
  created_at   TIMESTAMPTZ
  expires_at   TIMESTAMPTZ NULL
  is_active    BOOLEAN DEFAULT true
Access pattern: get by code (key-value!) → DynamoDB / Cassandra / Postgres all fine
At 6B rows: key-value store (DynamoDB) or sharded Postgres by code hash

click_events (append-only, high volume) → Kafka → ClickHouse/BigQuery
  code, ts, ip_hash, country, device, browser, referrer
```

### 7. High-level architecture

```
                         ┌──────────────── CDN / Edge (optional caching of 301s, WAF, bot filter)
 User clicks sho.rt/aZ3k9│
                         ▼
                 ┌───────────────┐
                 │ Redirect svc  │──1. GET Redis "link:aZ3k9" ──► Redis cluster (hot links)
                 │ (stateless,   │◄─ hit → 302 Location (~1–5 ms)
                 │  many pods)   │──2. miss → DB lookup ──► DynamoDB / Postgres (sharded)
                 │               │──3. async: publish click event ──► Kafka ──► ClickHouse (analytics)
                 └───────────────┘                                    ▲
                                                                      └─ Stats API reads aggregates
 Creator ──POST /links──► Link API ──► KGS range / ID ──► DB write ──► (optionally warm cache)
```

### 8. Deep dives

```
Caching:       Redis cache-aside, TTL ~24h + LRU; negative cache for unknown codes (stop DB hammering)
               Bloom filter of existing codes to reject random probes (Topic 53)
Analytics:     NEVER update counters synchronously in the redirect path → fire-and-forget event
               to Kafka (or local buffer) → aggregate (per minute/day) in ClickHouse; approximate
               unique visitors with HyperLogLog
Expiry:        check expires_at on read; background job / TTL (DynamoDB TTL) for cleanup
Abuse:         scan long URLs against Safe Browsing/phishing lists; rate-limit creation per user/IP;
               disable reported links; don't allow redirect loops (short → short)
Availability:  multi-AZ, cache in front, read replicas; multi-region for redirects (global users)
Security:      private links → longer random codes; HTTPS; validate URL schemes (no javascript:)
```

## 🟢 कैसे काम करता है? (Hindi)
1. माँगें: छोटा link बनाना, तेज़ redirect (50 ms से कम), click analytics; पढ़ना लिखने से 100 गुना ज़्यादा।
2. अनुमान: 10 करोड़ नए links/महीना, 20,000 redirects/सेकंड peak; base62 के 7 अक्षर = 3.5 लाख करोड़ codes।
3. Code बनाना: hash (टकराव जाँचो), counter + base62 (अंदाज़ा लगने लायक — scramble करो), या Key Generation Service से IDs के ranges (सबसे आम जवाब)।
4. Redirect: पहले Redis, न मिले तो DB; 302 से हर click गिनी जाती है (301 browser cache करता है)।
5. Click analytics redirect को धीमा न करे — event Kafka में डालो, ClickHouse में गिनती; phishing links और abuse पर रोक।

---

## 🟡 Real World Example

**Bitly** — handles billions of clicks per month. Redirects are served from a highly cached tier, and click data flows into analytics pipelines for dashboards. Its branded domains (e.g. `amzn.to`, `nyti.ms`) are a major business feature.

**Twitter t.co** — wraps every link in tweets, to measure clicks and to check links against malware and phishing lists before redirecting.

**Indian SMS links (DLT rules)** — Indian telecom regulations (TRAI DLT) require whitelisted URLs and headers for promotional SMS. Companies use registered short domains, and banks and e-commerce use them to track campaign clicks.

**Firebase Dynamic Links (shut down in 2025)** — app-aware short links that opened the app or the store. Its shutdown forced teams to build their own deep-link and short-link services (Topic M11).

## 🟡 Real Example Hindi में
Bitly हर महीने अरबों clicks संभालता है — redirect cache से, clicks analytics pipeline में। Twitter का t.co हर link को malware/phishing के लिए जाँचता है।
भारत में TRAI DLT नियम के कारण promotional SMS में रजिस्टर्ड छोटे domains इस्तेमाल होते हैं, ताकि campaign clicks गिने जा सकें।

---

## 🟠 My Stack Example

### Base62 encoding + range-based ID allocation (Node)
```js
const ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
export function base62(n) {
  let s = ''; let x = BigInt(n);
  do { s = ALPHABET[Number(x % 62n)] + s; x /= 62n; } while (x > 0n);
  return s;
}

// Each instance reserves a block of 10,000 ids atomically (Redis INCRBY or a DB sequence)
let next = 0n, end = 0n;
async function nextId() {
  if (next >= end) {
    const hi = BigInt(await redis.incrBy('link:id_block', 10_000));
    next = hi - 10_000n; end = hi;
  }
  return next++;
}
// scramble so codes aren't sequential (simple bijective multiply-mod; use Sqids/Feistel in prod)
const P = 1_000_000_007n, M = 62n ** 7n;
const scramble = (id) => (id * P) % M;           // P coprime with M → bijection
```

### Create + redirect endpoints (Express)
```js
app.post('/api/v1/links', authenticateOptional, rateLimit('create', 30), async (req, res) => {
  const { url, alias, expiresAt } = LinkIn.parse(req.body);           // zod: http/https only
  if (await isMalicious(url)) return res.status(422).json({ error: 'URL_BLOCKED' });
  const code = alias ?? base62(scramble(await nextId())).padStart(7, '0');
  try {
    await db.query('INSERT INTO links(code, long_url, user_id, expires_at) VALUES ($1,$2,$3,$4)',
                   [code, url, req.user?.id ?? null, expiresAt ?? null]);
  } catch (e) {
    if (e.code === '23505') return res.status(409).json({ error: 'ALIAS_TAKEN' });
    throw e;
  }
  res.status(201).json({ code, shortUrl: `https://sho.rt/${code}` });
});

app.get('/:code([0-9a-zA-Z_-]{3,32})', async (req, res) => {
  const { code } = req.params;
  let target = await redis.get(`link:${code}`);
  if (target === null) {
    const { rows: [l] } = await reader.query(
      'SELECT long_url, expires_at, is_active FROM links WHERE code = $1', [code]);
    target = l && l.is_active && (!l.expires_at || l.expires_at > new Date()) ? l.long_url : '';
    await redis.set(`link:${code}`, target, { EX: target ? 86_400 : 300 });   // negative cache 5 min
  }
  if (!target) return res.status(404).send('Link not found');

  // fire-and-forget analytics (never block the redirect)
  clickBuffer.push({ code, ts: Date.now(), ua: req.get('user-agent'), ref: req.get('referer'),
                     country: req.get('cf-ipcountry'), ipHash: hashIp(req.ip) });
  res.set('Cache-Control', 'private, max-age=0').redirect(302, target);
});
setInterval(() => flushClicksToKafka(clickBuffer.splice(0)), 1000);   // batch every second
```

### ClickHouse analytics table
```sql
CREATE TABLE clicks (code String, ts DateTime, country LowCardinality(String), device LowCardinality(String), referrer String)
ENGINE = MergeTree PARTITION BY toYYYYMM(ts) ORDER BY (code, ts);
SELECT toDate(ts) d, count() FROM clicks WHERE code = 'aZ3k9Lp' GROUP BY d ORDER BY d;
```

### FastAPI variant (redirect service)
```python
@app.get("/{code}")
async def redirect(code: str):
    target = await r.get(f"link:{code}")
    if target is None:
        row = await db.fetch_one("SELECT long_url FROM links WHERE code=:c AND is_active", {"c": code})
        target = row["long_url"] if row else ""
        await r.set(f"link:{code}", target, ex=86400 if target else 300)
    if not target:
        raise HTTPException(404)
    asyncio.create_task(publish_click(code))
    return RedirectResponse(target, status_code=302)
```

### Mobile angle
- Short links shared in WhatsApp should open the **app** if installed, via Universal Links or App Links on the short domain (`apple-app-site-association`, `assetlinks.json`), and otherwise go to the web or app store. See M11 Deep Linking.

---

## ⚫ Interview Questions + Answers

**Q1: How would you generate unique short codes at scale?**
A1: Use a distributed ID source that avoids per-request coordination: a key generation service or counter handing out ID ranges to each app instance, or Snowflake-style IDs. Base62-encode the ID (7 characters cover about 3.5 trillion codes). To avoid enumerable sequential codes, apply a bijective scramble (Feistel or Sqids) before encoding. Alternatives are random codes with a unique constraint and retry on collision, or hashing the URL with collision handling. Custom aliases are checked for uniqueness and reserved words.

**Q2: 301 or 302 for redirects?**
A2: A 301 (permanent) lets browsers and proxies cache the redirect, which reduces load and latency, but repeat clicks bypass our servers (losing analytics) and changing the destination later is unreliable. A 302 (temporary) means every click reaches us, giving accurate analytics and editable destinations, at the cost of more traffic. Shorteners focused on analytics use 302, or 301 with care for static links.

**Q3: How do you make redirects fast and highly available?**
A3: A stateless redirect tier behind load balancers, with a Redis cache-aside layer for hot codes (sub-millisecond), negative caching and a Bloom filter for invalid codes, and a key-value store (DynamoDB, Cassandra or sharded Postgres) as the source of truth with replicas. Optionally cache at the CDN edge. Analytics are recorded asynchronously, never in the redirect's critical path. Deploy multi-AZ and multi-region with latency-based DNS for global users.

**Q4: How do you build click analytics without slowing redirects?**
A4: On each redirect, emit a lightweight event (code, timestamp, country, device, referrer, hashed IP) to a buffer or Kafka asynchronously. Stream processors or batch jobs aggregate per link per minute, hour and day into an OLAP store (ClickHouse, BigQuery, Druid), with HyperLogLog for unique visitors. The stats API reads the aggregates. Accept slight analytics lag in exchange for fast redirects.

**Q5: What abuse problems exist and how do you mitigate them?**
A5: Shorteners are used to hide phishing and malware links, spam, and redirect chains. Mitigations: check destination URLs against threat intelligence (Google Safe Browsing) at creation and periodically, rate-limit link creation per user, IP and API key, require accounts or CAPTCHA for bulk creation, block redirects to other shorteners (loops), show interstitial warnings for flagged links, provide abuse reporting and quick disabling, and allow only http/https schemes.

---

## 🔷 Trade-offs
✅ Range-based IDs: fast, collision-free — ❌ sequential (needs scrambling), lost ranges on crash.
✅ Random codes: unguessable — ❌ collision checks, longer codes as table grows.
✅ 302 + async analytics: accurate stats — ❌ more load than 301.
✅ Key-value store: simple scaling — ❌ fewer ad-hoc queries (use OLAP for analytics).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Short code | Unique identifier in short URL | छोटे link का code |
| Base62 | Encoding with 62 characters | 62 अक्षरों वाली encoding |
| Redirect (301/302) | Send browser to another URL | दूसरे URL पर भेजना |
| Key Generation Service | Pre-allocates unique ID ranges | IDs के range बाँटने वाली service |
| Collision | Two URLs get same code | दो URL का एक code |
| Hot key | Very frequently accessed link | बहुत ज़्यादा खुलने वाला link |
| Negative caching | Cache "not found" | "नहीं मिला" को cache करना |
| Click stream | Stream of click events | clicks की धारा |
| HyperLogLog | Approx unique counting | अनुमानित unique गिनती |
| Enumeration | Guessing codes sequentially | क्रम से code अंदाज़ा लगाना |

---

## ⚡ 3-Line Summary
**English:**
1. URL shortener = create (long → short code) + very read-heavy redirect path (target p99 < 50 ms) + analytics.
2. Generate codes via ID ranges/Snowflake + base62 (scramble to avoid enumeration) or random with uniqueness checks; store in a key-value DB.
3. Cache hot links in Redis, use 302 + async click events → Kafka → ClickHouse, and add abuse protection.

**Hindi:**
1. URL shortener = छोटा code बनाना + बहुत तेज़ redirect + clicks की analytics।
2. Code: ID range/Snowflake + base62 (scramble करके) या random + unique जाँच; key-value DB में रखो।
3. Hot links Redis में, 302 + async click events → Kafka → ClickHouse, और abuse से बचाव।

---

## ➡️ Next Topic Suggestion
**112. Rate Limiter Design** — Your shortener's create API needs abuse protection. Next: design a distributed rate limiter service end to end (algorithms, Redis, multi-region, rules config, headers, failure modes).
