# 49. Cache Eviction (LRU / LFU)
# हिंदी में: Cache Eviction — cache की memory भर जाने पर कौन-सा डेटा हटाया जाए, यह तय करने के नियम (LRU, LFU आदि)

---

## 🔵 Simple Definition (English)
A cache has **limited memory**. When it's full and a new item must be stored, an **eviction policy** decides **which existing item to remove**:
- **LRU (Least Recently Used):** remove the item not accessed for the longest time.
- **LFU (Least Frequently Used):** remove the item accessed the fewest times.
- **FIFO:** remove the oldest inserted item.
- **TTL-based / volatile:** remove items that are expiring soonest.
- **Random:** remove a random item.

## 🔵 सरल परिभाषा (Hindi)
Cache की memory सीमित है। भर जाने पर नया डेटा रखने के लिए कुछ पुराना हटाना पड़ता है — eviction policy तय करती है कि क्या हटाना है।
LRU = जो सबसे लंबे समय से इस्तेमाल नहीं हुआ, उसे हटाओ; LFU = जो सबसे कम बार इस्तेमाल हुआ, उसे हटाओ।

---

## 🔴 Problem it Solves
RAM is expensive, and you can't cache everything. When memory is full:
- Without a policy → the cache **rejects writes** or **crashes (OOM)**.
- With a bad policy → it removes **hot** data and keeps cold data → **low hit ratio** → DB overload.

A good eviction policy keeps the **working set** (frequently or recently needed data) in memory, maximizing hit ratio for a given memory budget.

## 🔴 यह क्यों बना? (Hindi)
RAM महँगी है, सब कुछ cache नहीं कर सकते। memory भरने पर या तो cache writes मना करेगा/crash होगा, या ग़लत नियम से ज़रूरी (hot) डेटा हटेगा और DB पर बोझ बढ़ेगा।
सही eviction policy काम का डेटा memory में रखती है और hit ratio ऊँचा रखती है।

---

## 🟢 How it Works — Step by Step

### LRU — Least Recently Used

```
Capacity 3. Access sequence: A B C A D

[A]          get A
[B A]        get B         (most recent on left)
[C B A]      get C         full
[A C B]      get A         A moved to front (recently used)
[D A C]      put D → evict B (least recently used, at the right end)

Implementation: HashMap (key → node) + Doubly Linked List (order of use)
  get:  O(1) lookup in map, move node to head
  put:  O(1) insert at head; if over capacity, remove tail
```

### LFU — Least Frequently Used

```
Counts accesses:  A:5  B:1  C:3
New item D, full → evict B (freq 1)
✅ protects consistently popular items (home page config, top products)
❌ old items that WERE popular stay forever ("cache pollution") → needs aging/decay
❌ new items start at count 1 → evicted quickly before proving popularity
Implementation: map + frequency buckets (doubly linked lists per frequency) → O(1)
```

### When LRU fails — scan pollution

```
Hot set: 1,000 popular products accessed constantly.
A nightly job reads 1,000,000 products ONCE each (export/report).
LRU: each scanned item becomes "most recent" → flushes all hot items out → hit ratio crashes.
LFU / W-TinyLFU / LRU-K / 2Q / ARC resist this: one-time accesses don't displace frequent ones.
```

### Other policies

```
FIFO         → evict oldest inserted (simple, ignores usage)
Random       → surprisingly decent, O(1), no bookkeeping
TTL/volatile → evict keys with nearest expiry
LRU-K / 2Q   → need K accesses before "promotion" → scan resistant
ARC          → adapts between recency and frequency (ZFS)
W-TinyLFU    → frequency sketch + small LRU window (Caffeine for Java, Ristretto for Go) — near-optimal
```

### Redis maxmemory policies

```
maxmemory 2gb
maxmemory-policy <one of>:
  noeviction       → reject writes when full (errors!)  ← default; good when Redis is a DATA STORE (queues)
  allkeys-lru      → evict any key by approx LRU        ← most common for pure CACHE
  allkeys-lfu      → evict any key by approx LFU        ← great for skewed popularity
  volatile-lru     → LRU only among keys WITH TTL
  volatile-lfu     → LFU only among keys WITH TTL
  volatile-ttl     → keys with TTL, shortest TTL first
  allkeys-random / volatile-random

Redis LRU/LFU are APPROXIMATE: it samples N keys (maxmemory-samples 5–10) and evicts the best
candidate → no linked list overhead, close to true LRU.
LFU uses a logarithmic counter with decay (lfu-decay-time) so old popularity fades.
```

### Eviction vs Expiration

```
Expiration → key removed because its TTL passed (correctness/freshness)
Eviction   → key removed because memory is FULL (capacity)
A healthy cache: mostly expirations, few evictions. Many evictions → cache too small or no TTLs.
```

## 🟢 कैसे काम करता है? (Hindi)
1. LRU: हर इस्तेमाल पर item को "सबसे नया" बनाओ; memory भरे तो सबसे पुराना इस्तेमाल हुआ हटाओ (HashMap + Doubly Linked List, O(1))।
2. LFU: हर item कितनी बार इस्तेमाल हुआ गिनो; सबसे कम वाला हटाओ — लगातार popular चीज़ें बची रहती हैं।
3. LRU की कमज़ोरी: एक बड़ा scan (रिपोर्ट) सारे hot items बाहर कर देता है; LFU/TinyLFU इससे बचते हैं।
4. Redis में `maxmemory-policy`: pure cache के लिए `allkeys-lru` या `allkeys-lfu`; queue/data store के लिए `noeviction`।
5. Expiry (TTL पूरा) और eviction (memory भरी) अलग हैं — बहुत evictions = cache छोटा है।

---

## 🟡 Real World Example

**CDNs (Cloudflare, Akamai)** — edge servers have limited disk/RAM per location and use LRU/LFU-like policies so popular content (a trending video, the Hotstar homepage) stays at the edge while rarely requested files are evicted and fetched from origin when needed.

**Instagram / Facebook memcache** — use LRU with separate pools for different data types, so a flood of one type (e.g. low-value keys) can't evict high-value data. They split pools by access pattern.

**Netflix EVCache / Caffeine at many Java shops** — W-TinyLFU gives near-optimal hit ratios. Caffeine replaced Guava cache because it resists scan pollution.

**Browser cache** — your browser evicts old cached resources (LRU-ish) when it hits its disk quota.

## 🟡 Real Example Hindi में
CDN सर्वरों की memory सीमित है — trending वीडियो या Hotstar का homepage edge पर रहता है (LRU/LFU), और कम माँगी जाने वाली फ़ाइलें हट जाती हैं।
Facebook memcache में अलग-अलग तरह के डेटा के अलग pools हैं, ताकि एक तरह का डेटा दूसरे ज़रूरी डेटा को बाहर न कर दे।

---

## 🟠 My Stack Example

### LRU cache in JavaScript (classic interview coding question)
```js
// Map preserves insertion order → delete + set moves a key to the "most recent" end
class LRUCache {
  constructor(capacity) { this.cap = capacity; this.map = new Map(); }
  get(key) {
    if (!this.map.has(key)) return -1;
    const v = this.map.get(key);
    this.map.delete(key); this.map.set(key, v);   // mark as most recently used
    return v;
  }
  put(key, value) {
    if (this.map.has(key)) this.map.delete(key);
    this.map.set(key, value);
    if (this.map.size > this.cap) this.map.delete(this.map.keys().next().value); // evict LRU (oldest)
  }
}
```

### LRU with explicit doubly linked list (what interviewers expect to see understood)
```python
class Node:
    __slots__ = ("k", "v", "prev", "next")
    def __init__(self, k=None, v=None): self.k, self.v, self.prev, self.next = k, v, None, None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap, self.map = capacity, {}
        self.head, self.tail = Node(), Node()          # sentinels: head <-> ... <-> tail
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, n): n.prev.next, n.next.prev = n.next, n.prev
    def _add_front(self, n):
        n.next, n.prev = self.head.next, self.head
        self.head.next.prev = n; self.head.next = n

    def get(self, k):
        if k not in self.map: return -1
        n = self.map[k]; self._remove(n); self._add_front(n)
        return n.v

    def put(self, k, v):
        if k in self.map: self._remove(self.map[k])
        n = Node(k, v); self.map[k] = n; self._add_front(n)
        if len(self.map) > self.cap:
            lru = self.tail.prev; self._remove(lru); del self.map[lru.k]
```

### In-process L1 cache in Node (lru-cache package)
```js
import { LRUCache } from 'lru-cache';
const l1 = new LRUCache({ max: 10_000, ttl: 10_000, maxSize: 50_000_000, sizeCalculation: (v) => JSON.stringify(v).length });
```
```python
from functools import lru_cache
@lru_cache(maxsize=1024)
def get_tax_rate(state: str) -> float: ...   # tiny pure-function cache (per process)
```

### Redis configuration
```conf
# Pure cache instance
maxmemory 4gb
maxmemory-policy allkeys-lfu
maxmemory-samples 10

# Separate instance for queues / sessions / rate limits (must NOT lose data silently)
maxmemory-policy noeviction
```
```bash
redis-cli INFO stats | grep -E "evicted_keys|expired_keys|keyspace_(hits|misses)"
redis-cli INFO memory | grep used_memory_human
redis-cli OBJECT FREQ product:7      # LFU counter (with lfu policy)
```

> ⚠️ Don't put BullMQ queues and your cache in the **same** Redis with `allkeys-lru`. Under memory pressure Redis may evict **job data**. Use separate instances or databases with the right policy.

### Mobile
- `expo-image` / `react-native-fast-image` use LRU memory and disk caches for images. Set sane disk limits.
- React Query `gcTime`: unused query data is garbage-collected after N minutes. It's eviction for client state.

---

## ⚫ Interview Questions + Answers

**Q1: What is LRU and how would you implement it in O(1)?**
A1: Least Recently Used evicts the item that hasn't been accessed for the longest time. For O(1) get and put, combine a hash map (key → node) with a doubly linked list ordered by recency. On get, look up the node and move it to the head. On put, insert or update at the head, and if capacity is exceeded, remove the tail node and delete its key from the map. In JS, a `Map`'s insertion order can emulate this.

**Q2: LRU vs LFU — when is each better?**
A2: LRU adapts quickly to changing access patterns and is simple, good for workloads with temporal locality (recent items get reaccessed). But one-off scans can flush hot data. LFU keeps consistently popular items and resists scans, which suits skewed, stable popularity (top products, config). But it can keep formerly popular items too long without decay, and new items get evicted before building frequency. Modern caches (W-TinyLFU, Redis LFU with decay) combine both.

**Q3: Which Redis eviction policy would you use?**
A3: For a pure cache, `allkeys-lru`, or `allkeys-lfu` if popularity is skewed and stable. For Redis used as a data store (queues, sessions, rate limiter state) where silent data loss is unacceptable, use `noeviction` and monitor memory, so writes fail loudly rather than dropping data. `volatile-*` policies apply only to keys with TTLs, which is useful when mixing cache keys (with TTL) and persistent keys in one instance, though separate instances are cleaner.

**Q4: How do you know your cache is too small?**
A4: A high eviction rate (`evicted_keys` growing steadily), a falling hit ratio, memory constantly at `maxmemory`, and DB load rising even though data is cacheable. Compare the working set size to cache size. Fixes: add memory or shards, reduce value sizes (compression, fewer fields), set appropriate TTLs, stop caching low-value data, or switch to a policy that suits the access pattern (LFU).

**Q5: What's the difference between eviction and expiration?**
A5: Expiration removes a key because its TTL elapsed, which is a freshness and correctness decision you control per key. Eviction removes keys because memory is full, which is a capacity decision made by the cache's policy, regardless of TTL. In a healthy system most removals are expirations. Lots of evictions means memory pressure and probably a worse hit ratio.

---

## 🔷 Trade-offs
✅ LRU: simple, good general-purpose — ❌ scan pollution.
✅ LFU: keeps truly popular data — ❌ slow to adapt, needs decay, more bookkeeping.
✅ Approximate (sampling) policies: low overhead — ❌ not exact (usually fine).
✅ noeviction: no silent data loss — ❌ write errors when full.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Eviction | Removing items when cache is full | memory भरने पर हटाना |
| LRU | Least recently used | सबसे पुराना इस्तेमाल हुआ |
| LFU | Least frequently used | सबसे कम बार इस्तेमाल हुआ |
| FIFO | First in, first out | पहले आया, पहले गया |
| Working set | Data actively needed | अभी काम आने वाला डेटा |
| Scan pollution | One-time reads flushing hot data | एक बार की reads से hot डेटा बाहर |
| maxmemory-policy | Redis eviction setting | Redis का eviction नियम |
| Hit ratio | Fraction served from cache | cache से जवाब का अनुपात |

---

## ⚡ 3-Line Summary
**English:**
1. Eviction decides what to drop when cache memory is full: LRU (recency), LFU (frequency), FIFO, TTL, random.
2. LRU = HashMap + doubly linked list (O(1)); LFU/TinyLFU resist scans and keep popular items.
3. Redis: allkeys-lru/lfu for caches, noeviction for data stores; watch evicted_keys and hit ratio.

**Hindi:**
1. Eviction = memory भरने पर क्या हटाना है: LRU, LFU, FIFO, TTL, random।
2. LRU = HashMap + doubly linked list (O(1)); LFU बड़े scans से बचाता है।
3. Redis: cache के लिए allkeys-lru/lfu, data store के लिए noeviction; evictions और hit ratio देखो।

---

## ➡️ Next Topic Suggestion
**50. Cache Stampede + Thundering Herd** — What happens when a hot key expires and 10,000 requests miss at the same instant? Next: cache stampede, thundering herd, and the fixes (locking, request coalescing, early refresh, jitter).
