# 53. Bloom Filters
# हिंदी में: Bloom Filter — बहुत कम memory वाला एक ढाँचा जो बताता है "यह चीज़ पक्का नहीं है" या "शायद है" — कभी ग़लत "नहीं" नहीं कहता

---

## 🔵 Simple Definition (English)
A **Bloom filter** is a **space-efficient probabilistic data structure** that tests whether an element is in a set. It answers:
- **"Definitely NOT in the set"** (always correct), or
- **"PROBABLY in the set"** (it can be wrong: a **false positive**).
It **never gives false negatives**. It uses a **bit array + k hash functions**, needs only ~10 bits per element for a 1% false-positive rate, and classic Bloom filters **can't delete** items.

## 🔵 सरल परिभाषा (Hindi)
Bloom filter एक बहुत छोटा ढाँचा है जो बताता है कि कोई चीज़ set में "पक्का नहीं है" या "शायद है"।
"नहीं" हमेशा सही होता है; "शायद है" कभी-कभी ग़लत हो सकता है (false positive)। करोड़ों items के लिए भी बहुत कम memory लगती है।

---

## 🔴 Problem it Solves
Many systems do expensive lookups for things that **usually don't exist**:
- "Is this username taken?" → DB query for every keystroke.
- Cassandra/RocksDB: "Does this SSTable file contain key X?" → disk read of every file.
- "Has this user already seen this post/ad?" → huge set per user.
- "Is this URL malicious?" (Chrome Safe Browsing) → can't ship millions of URLs to every browser.
- Cache penetration: attackers request random non-existent IDs → every request misses cache and hits the DB.

A Bloom filter in memory answers **"definitely not"** instantly for most lookups, skipping the expensive check. Only the "maybe" cases go to the real store.

## 🔴 यह क्यों बना? (Hindi)
बहुत सारे lookups ऐसी चीज़ों के होते हैं जो मौजूद ही नहीं — username चेक, Cassandra में हर फ़ाइल पढ़ना, नक़ली IDs से cache miss का हमला।
Bloom filter memory में तुरंत बता देता है "पक्का नहीं है" — तो महँगा DB/disk lookup बच जाता है; सिर्फ़ "शायद" वाले मामलों में असली जाँच होती है।

---

## 🟢 How it Works — Step by Step

### Insert

```
Bit array m = 16 bits, all 0:      [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
k = 3 hash functions

add("aditya"):  h1=2, h2=7, h3=13 → set bits 2, 7, 13
                                   [0 0 1 0 0 0 0 1 0 0 0 0 0 1 0 0]
add("riya"):    h1=4, h2=7, h3=11 → set bits 4, 7, 11
                                   [0 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0]
```

### Query

```
contains("karan"): h1=2, h2=5, h3=11 → bit 5 is 0 → DEFINITELY NOT present ✅
contains("aditya"): bits 2, 7, 13 all 1 → PROBABLY present
contains("neha"):  h1=4, h2=11, h3=13 → all 1 (set by OTHER items!) → "probably" → FALSE POSITIVE ❌
                   (check the real DB to confirm)
```

### Why no false negatives?
Bits are only ever **set**, never cleared. If an item was added, its k bits are definitely 1.

### Sizing (formulas to know)

```
n = expected number of items, p = desired false positive rate
  bits m = -n × ln(p) / (ln 2)²
  hash functions k = (m / n) × ln 2

Rule of thumb: ~9.6 bits per item for 1% FP, ~14.4 bits for 0.1%
  10 million items @ 1%  → ~96 Mbit ≈ 12 MB, k ≈ 7
  (vs storing 10M strings ≈ hundreds of MB)
FP rate grows as you add more items than planned → resize/rebuild (Scalable Bloom filters)
```

### Limitations & variants

```
❌ Can't delete (clearing a bit may remove other items)
   → Counting Bloom filter (counters instead of bits) or Cuckoo filter (supports delete, often smaller)
❌ Can't list items, can't count exactly
❌ Must choose size upfront → Scalable Bloom filter (chain of filters)
Related probabilistic structures:
   HyperLogLog → count distinct (Topic 44)
   Count-Min Sketch → approximate frequency (top-K, heavy hitters)
```

### Where Bloom filters are used

```
- LSM-tree databases (Cassandra, RocksDB, LevelDB, HBase, ScyllaDB): one filter per SSTable
  → skip disk reads for files that don't contain the key  (huge read speedup)
- Postgres: bloom index extension; Postgres hash joins use bloom-like filtering
- CDNs (Akamai): "one-hit wonders" — only cache an object on its 2nd request (bloom tracks 1st)
- Browsers: Chrome Safe Browsing (historically) — local filter of malicious URL prefixes
- Medium: "already recommended/read" articles per user
- Bitcoin SPV clients: request relevant transactions via bloom filter
- Cache penetration protection: filter of all valid IDs in front of cache/DB
- Username/email availability pre-check, spell checkers, duplicate URL detection in crawlers
```

## 🟢 कैसे काम करता है? (Hindi)
1. एक bit array (सब 0) और k hash functions लो।
2. Add: item के k hash निकालो और उन k bits को 1 कर दो।
3. Check: k bits देखो — कोई भी 0 है तो item पक्का नहीं है; सब 1 हैं तो "शायद है" (असली DB से पक्का करो)।
4. False negative कभी नहीं, क्योंकि bits सिर्फ़ 1 होते हैं, कभी 0 नहीं होते।
5. 1% ग़लती के लिए ~10 bits प्रति item; delete नहीं कर सकते (उसके लिए Counting/Cuckoo filter)।

---

## 🟡 Real World Example

**Cassandra / RocksDB** — every SSTable has a Bloom filter in memory. A read for a key checks the filters and opens only files that "might" contain it. Without them, reads would touch many files on disk. This is a key part of why LSM-tree databases can be write-optimized and still read fast.

**Akamai one-hit wonders** — roughly 75% of objects requested from CDN caches were requested only once. Akamai used a Bloom filter to cache an object only on its **second** request, saving huge disk space.

**Medium** — used Bloom filters to avoid recommending articles a user has already read.

**Chrome Safe Browsing (older versions)** — the browser kept a compact local filter of malicious URL prefixes and contacted Google only on a "maybe" match, which kept browsing fast and private.

## 🟡 Real Example Hindi में
Cassandra/RocksDB में हर फ़ाइल का Bloom filter memory में होता है — key पढ़ते समय सिर्फ़ उन्हीं फ़ाइलों को खोला जाता है जिनमें key "शायद" हो।
Akamai ने पाया कि 75% objects सिर्फ़ एक बार माँगे जाते हैं — Bloom filter से object दूसरी बार माँगने पर ही cache किया, बहुत disk बची।

---

## 🟠 My Stack Example

### Redis Bloom (RedisBloom module / Redis Stack / Valkey bloom)
```bash
BF.RESERVE usernames 0.001 10000000      # 0.1% FP, 10M items
BF.ADD usernames "aditya_r"
BF.EXISTS usernames "aditya_r"            # 1 → maybe taken → check DB
BF.EXISTS usernames "new_user_99"         # 0 → definitely free → skip DB ✅
```

### Node.js — username availability check
```js
app.get('/api/v1/usernames/:name/available', async (req, res) => {
  const name = req.params.name.toLowerCase();
  const maybe = await redis.sendCommand(['BF.EXISTS', 'usernames', name]);
  if (maybe === 0) return res.json({ available: true });           // fast path, no DB
  const { rowCount } = await pool.query('SELECT 1 FROM users WHERE username = $1', [name]);
  res.json({ available: rowCount === 0 });                          // confirm on "maybe"
});
// on signup: INSERT user → BF.ADD usernames name
// (The DB UNIQUE constraint is still the real guarantee!)
```

### Cache penetration protection (only query DB for IDs that can exist)
```js
async function getProduct(id) {
  if (!(await redis.sendCommand(['BF.EXISTS', 'product_ids', String(id)]))) return null; // definitely not a real product
  return cached(`product:${id}`, 600, () => repo.getProduct(id));
}
```

### Pure JS Bloom filter (to understand / interview)
```js
import { createHash } from 'node:crypto';
class BloomFilter {
  constructor(n, p = 0.01) {
    this.m = Math.ceil(-(n * Math.log(p)) / Math.LN2 ** 2);
    this.k = Math.max(1, Math.round((this.m / n) * Math.LN2));
    this.bits = new Uint8Array(Math.ceil(this.m / 8));
  }
  #hashes(item) {                          // double hashing: h_i = h1 + i*h2
    const d = createHash('sha256').update(item).digest();
    const h1 = d.readUInt32BE(0), h2 = d.readUInt32BE(4);
    return Array.from({ length: this.k }, (_, i) => (h1 + i * h2) % this.m);
  }
  add(item) { for (const b of this.#hashes(item)) this.bits[b >> 3] |= 1 << (b & 7); }
  mightContain(item) { return this.#hashes(item).every((b) => this.bits[b >> 3] & (1 << (b & 7))); }
}
const bf = new BloomFilter(1_000_000, 0.01);   // ~1.2 MB
```

### Python
```python
from pybloom_live import ScalableBloomFilter
seen = ScalableBloomFilter(initial_capacity=100_000, error_rate=0.001)
if url not in seen:          # crawler: skip URLs already visited (approximately)
    seen.add(url); crawl(url)
```

### Postgres bloom index (multi-column equality on many columns)
```sql
CREATE EXTENSION bloom;
CREATE INDEX idx_attrs_bloom ON products USING bloom (color, size, brand, material) WITH (length = 80);
```

### Mobile / frontend use
- Ship a compact Bloom filter of blocked words or known-bad URLs to the app, so it can check locally without network calls (with server-side confirmation for "maybe").

---

## ⚫ Interview Questions + Answers

**Q1: What is a Bloom filter and what guarantees does it give?**
A1: A probabilistic set-membership structure made of a bit array and k hash functions. Adding an item sets k bits. Querying checks those k bits: if any is 0, the item is definitely not in the set (no false negatives). If all are 1, it's probably in the set, and false positives are possible because other items may have set those bits. It's extremely memory-efficient (~10 bits per item for 1% FP).

**Q2: Why can't you delete from a standard Bloom filter?**
A2: Bits are shared between items. Clearing an item's bits could clear bits that other items rely on, which would create false negatives and break the main guarantee. Counting Bloom filters (small counters instead of bits, decremented on delete) or Cuckoo filters (store fingerprints and support deletion) solve this at some extra cost.

**Q3: How do LSM-tree databases like Cassandra use Bloom filters?**
A3: Data is spread across many immutable SSTable files on disk. To read a key, the DB would otherwise check many files. Each SSTable has an in-memory Bloom filter of its keys. The read path checks the filters first and only reads files that might contain the key, skipping most disk I/O, especially for keys that don't exist. The FP rate is tunable per table (memory vs extra reads).

**Q4: How would you use a Bloom filter to protect against cache penetration?**
A4: Cache penetration is when requests for non-existent keys (often malicious random IDs) always miss the cache and hit the DB. Maintain a Bloom filter of all valid IDs (loaded at startup, updated on insert). Before querying cache or DB, check the filter. If it says "definitely not", return 404 immediately. Combine it with negative caching of misses and rate limiting.

**Q5: How do you size a Bloom filter?**
A5: Decide the expected item count n and the acceptable false-positive rate p. Bits m = −n·ln(p)/(ln 2)², and hash functions k = (m/n)·ln 2. For example, 10M items at 1% FP needs about 96 million bits (≈12 MB) with k ≈ 7. If the actual count grows beyond n, the FP rate rises, so rebuild larger or use a scalable Bloom filter.

---

## 🔷 Trade-offs
✅ Advantages:
- Tiny memory, O(k) constant-time operations, no false negatives.
- Saves huge numbers of disk/DB/network lookups.

❌ Disadvantages:
- False positives (must confirm with real store for "maybe").
- No deletes (classic), no enumeration; must size upfront.
- Not a source of truth — always back with the real data/constraints.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bloom filter | Probabilistic membership test | "शायद है / पक्का नहीं" बताने वाला ढाँचा |
| False positive | Says "maybe" but not present | ग़लत "शायद है" |
| False negative | Says "no" but present (never happens) | ग़लत "नहीं" (कभी नहीं होता) |
| Bit array | Array of 0/1 | 0/1 की सूची |
| Hash function | Maps item to number | item को संख्या में बदलना |
| Counting Bloom filter | Supports deletes via counters | delete वाला Bloom filter |
| Cuckoo filter | Alternative with deletes | delete वाला दूसरा filter |
| Cache penetration | Misses for non-existent keys | न होने वाली keys से DB पर हमला |
| SSTable | Immutable sorted file in LSM DB | LSM DB की फ़ाइल |

---

## ⚡ 3-Line Summary
**English:**
1. A Bloom filter (bit array + k hashes) answers "definitely not" or "probably yes" with tiny memory.
2. No false negatives, some false positives; ~10 bits/item for 1% FP; classic version can't delete.
3. Used in Cassandra/RocksDB reads, CDNs, cache-penetration protection, username checks — always confirm "maybe" with the real store.

**Hindi:**
1. Bloom filter (bit array + k hashes) बहुत कम memory में बताता है "पक्का नहीं" या "शायद है"।
2. False negative कभी नहीं, false positive कभी-कभी; 1% ग़लती के लिए ~10 bits/item।
3. Cassandra, CDN, cache सुरक्षा, username check में इस्तेमाल — "शायद" को असली DB से पक्का करो।

---

## ➡️ Next Topic Suggestion
**53a. Search Engines (Elasticsearch)** — The last data-store topic: when users type "biryani near me", SQL `LIKE` isn't enough. Next: inverted indexes, relevance scoring, Elasticsearch/OpenSearch architecture, and syncing it with your primary DB.
