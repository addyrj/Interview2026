# 52. Consistent Hashing
# हिंदी में: Consistent Hashing — keys को सर्वरों में ऐसे बाँटना कि सर्वर जुड़ने या हटने पर सिर्फ़ थोड़ी-सी keys ही इधर-उधर हों

---

## 🔵 Simple Definition (English)
**Consistent hashing** maps both **keys** and **servers** onto the same **hash ring** (0 … 2³²−1). Each key belongs to the **first server clockwise** from its position. When a server is **added or removed**, only the keys between it and its neighbour move, about **1/N of keys**, instead of nearly all keys as with `hash(key) % N`.
**Virtual nodes** (many positions per server) make the distribution even.

## 🔵 सरल परिभाषा (Hindi)
Consistent hashing में keys और सर्वर दोनों एक गोल रिंग पर रखे जाते हैं; हर key अपनी जगह से घड़ी की दिशा में पहले आने वाले सर्वर की होती है।
नया सर्वर जुड़े या कोई हटे, तो सिर्फ़ उसके पास की keys (लगभग 1/N) बदलती हैं — `hash % N` की तरह सारी keys नहीं।

---

## 🔴 Problem it Solves
Simple modulo hashing: `server = hash(key) % N`.
```
N = 4: key "user:42" → hash 1234567 % 4 = 3 → server 3
Add one server → N = 5: 1234567 % 5 = 2 → server 2   ← moved!
With % N, changing N moves ~ (N-1)/N of ALL keys:
  4 → 5 servers: ~80% of keys move
```
For a **cache cluster**, that means ~80% cache misses at once → **DB stampede**. For **sharded storage**, it means migrating 80% of the data.

Consistent hashing: **add/remove a node → only ~1/N keys move.** This is essential for elastic clusters (caches, Cassandra, DynamoDB, CDNs, load balancers).

## 🔴 यह क्यों बना? (Hindi)
`hash % N` में सर्वर 4 से 5 करो तो ~80% keys दूसरी जगह चली जाती हैं — cache में 80% misses और DB पर बाढ़, या 80% डेटा migrate करना।
Consistent hashing में सर्वर जोड़ने/हटाने पर सिर्फ़ ~1/N keys हिलती हैं — इसलिए cache cluster, Cassandra, DynamoDB, CDN सब इसे इस्तेमाल करते हैं।

---

## 🟢 How it Works — Step by Step

### The ring

```
                        0 / 2^32
                          │
                  ┌───────●───────┐
              S_A ●               │
               /                   \
     key k1 ●                        ● S_B
             │                       │
             │        RING           │
             │                       ● key k2
              \                     /
           S_D ●                   /
                  └──────●────────┘
                        S_C

Rule: walk CLOCKWISE from the key's hash → first server = owner
  k1 → S_B ... (whatever comes next clockwise)
```

### Adding a server

```
Before:  ... S_A ─────────────────────── S_B ...
               keys in (S_A, S_B] → S_B

Add S_E between S_A and S_B:
         ... S_A ──────── S_E ────────── S_B ...
               (S_A, S_E] → S_E   ← only THESE keys move (from S_B to S_E)
               (S_E, S_B] → S_B   (unchanged)
All other servers' keys: unchanged ✅
```

### Removing / failing a server
```
S_B dies → its keys go to the next server clockwise (S_C). Others unaffected.
(With replication, keys are already copied to the next 2 nodes → no data loss.)
```

### Problem: uneven distribution → Virtual nodes

```
With only 4 points on the ring, arcs are random sizes → one server might own 40% of keys.
Virtual nodes: each physical server gets 100–256 positions ("A#1", "A#2", ... hashed).
  - arcs average out → near-even load
  - when a server leaves, its load spreads across MANY servers, not just one neighbour
  - weights: bigger server = more vnodes
```

### Replication on the ring (Dynamo / Cassandra)

```
Replication factor 3: key stored on the first 3 DISTINCT physical nodes clockwise.
   key k → S_B (primary), S_C, S_D (replicas)
Read/write quorums (Topic 90) on those nodes.
```

### Lookup implementation
```
Sorted array of (hash, node) for all vnodes.
lookup(key): h = hash(key); binary search first entry with hash ≥ h (wrap to index 0).
O(log V) per lookup (V = total vnodes) — tiny.
```

### Alternatives worth knowing
```
Rendezvous (HRW) hashing: for each key, score = hash(key, node) for all nodes; pick max.
   minimal movement like consistent hashing, no ring, O(N) per lookup (fine for small N)
Jump consistent hash (Google): O(log N), no memory, but nodes must be numbered 0..N-1
Fixed slots: Redis Cluster uses 16,384 HASH SLOTS (CRC16(key) % 16384); slots are
   assigned/migrated between nodes → same goal (minimal movement), simpler bookkeeping
Maglev hashing (Google LB): lookup table, consistent + even + fast
```

### Where it's used
```
- Distributed caches: Memcached clients (ketama), Redis client-side sharding
- Databases: Cassandra, DynamoDB, Riak, ScyllaDB (token ring)
- CDNs / load balancers: route same URL/user to same cache server (Akamai, Maglev, Envoy ring hash)
- Chat/WebSocket: route a room/channel to the same server (Discord)
- Object storage / sharded queues
```

## 🟢 कैसे काम करता है? (Hindi)
1. Keys और सर्वर दोनों को hash करके 0 से 2³² की एक गोल रिंग पर रखते हैं।
2. हर key अपनी जगह से घड़ी की दिशा में पहले मिलने वाले सर्वर पर जाती है।
3. नया सर्वर जुड़ा तो सिर्फ़ उसके और पिछले सर्वर के बीच की keys उस पर आती हैं; बाक़ी जस की तस।
4. Virtual nodes: हर सर्वर को रिंग पर 100-200 जगह दो, ताकि load बराबर बँटे।
5. Replication: key अगले 3 अलग सर्वरों पर रखी जाती है (Cassandra/DynamoDB)। Redis Cluster इसी सोच से 16,384 slots इस्तेमाल करता है।

---

## 🟡 Real World Example

**Amazon Dynamo paper (2007)** — introduced consistent hashing with virtual nodes and replication to the next N nodes for Amazon's shopping cart. That's the foundation of DynamoDB, Cassandra and Riak.

**Akamai** — consistent hashing was invented (Karger et al., 1997) partly for web caching at Akamai, so the same URL maps to the same cache server and adding servers doesn't flush everything.

**Discord** — uses consistent hashing to route each guild (server) to a specific process ("guild servers"), keeping that guild's state in memory on one node.

**Google Maglev** — Google's load balancer uses a consistent hashing variant so that existing connections stay on the same backend even when backends change.

## 🟡 Real Example Hindi में
Amazon के Dynamo paper (2007) ने shopping cart के लिए consistent hashing + virtual nodes इस्तेमाल किए — यही DynamoDB और Cassandra की नींव है।
Akamai में एक ही URL हमेशा एक ही cache सर्वर पर जाए, इसके लिए consistent hashing बना। Discord हर guild को एक तय process पर भेजता है।

---

## 🟠 My Stack Example

### Consistent hash ring with virtual nodes (Node.js)
```js
import { createHash } from 'node:crypto';

const h32 = (s) => createHash('md5').update(s).digest().readUInt32BE(0);

export class ConsistentHashRing {
  constructor(nodes = [], vnodes = 160) {
    this.vnodes = vnodes;
    this.ring = [];                       // sorted [{ hash, node }]
    nodes.forEach((n) => this.add(n));
  }
  add(node, weight = 1) {
    for (let i = 0; i < this.vnodes * weight; i++) this.ring.push({ hash: h32(`${node}#${i}`), node });
    this.ring.sort((a, b) => a.hash - b.hash);
  }
  remove(node) { this.ring = this.ring.filter((e) => e.node !== node); }
  get(key) {
    if (!this.ring.length) return null;
    const h = h32(key);
    let lo = 0, hi = this.ring.length;
    while (lo < hi) { const mid = (lo + hi) >>> 1; this.ring[mid].hash < h ? (lo = mid + 1) : (hi = mid); }
    return this.ring[lo % this.ring.length].node;          // wrap around
  }
  getN(key, n) {                                           // replicas: n distinct physical nodes
    const out = new Set(); const h = h32(key);
    let i = this.ring.findIndex((e) => e.hash >= h); if (i < 0) i = 0;
    while (out.size < n && out.size < new Set(this.ring.map(e => e.node)).size) {
      out.add(this.ring[i % this.ring.length].node); i++;
    }
    return [...out];
  }
}

// Demo: how many keys move when adding a node?
const ring = new ConsistentHashRing(['cache-1', 'cache-2', 'cache-3', 'cache-4']);
const keys = Array.from({ length: 100_000 }, (_, i) => `user:${i}`);
const before = keys.map((k) => ring.get(k));
ring.add('cache-5');
const moved = keys.filter((k, i) => ring.get(k) !== before[i]).length;
console.log(`moved ${(moved / keys.length * 100).toFixed(1)}%`);   // ≈ 20% (1/5), vs ~80% with modulo
```

### Python (uhashring library or quick version)
```python
from uhashring import HashRing
ring = HashRing(nodes=["redis-a", "redis-b", "redis-c"])
node = ring.get_node("session:abc123")
```

### Nginx consistent upstream hashing (sticky cache servers)
```nginx
upstream image_cache {
  hash $request_uri consistent;     # ketama consistent hashing
  server cache1:80; server cache2:80; server cache3:80;
}
```

### Redis Cluster (hash slots, not a ring — same purpose)
```bash
redis-cli -c CLUSTER KEYSLOT user:42        # → slot number (0..16383)
# Hash tags {..} force related keys into the SAME slot (needed for multi-key ops):
SET {user:42}:profile ...   SET {user:42}:cart ...   # same slot → MULTI/Lua works
```

### Where you'll actually meet it
```
- Using Redis Cluster / ElastiCache cluster mode → slots handled for you; mind hash tags
- Envoy/Istio "ring_hash" or "maglev" LB policy for sticky routing
- Building a WebSocket gateway: route roomId → gateway node via ring
- Interview: "Design a distributed cache" → consistent hashing + vnodes + replication
```

---

## ⚫ Interview Questions + Answers

**Q1: What problem does consistent hashing solve?**
A1: Distributing keys across a changing set of nodes with minimal remapping. With `hash % N`, changing N remaps almost all keys, which causes mass cache misses or data migration. Consistent hashing places nodes and keys on a ring and assigns each key to the next node clockwise, so adding or removing a node moves only the keys in that node's arc, about K/N keys. That's essential for elastic caches and distributed databases.

**Q2: Why are virtual nodes needed?**
A2: With few physical nodes on the ring, their random positions create uneven arcs, so some nodes own much more data and traffic. Mapping each physical node to many virtual points (100–200+) evens out the distribution statistically, spreads a failed node's load across many nodes instead of one neighbour, and allows weighting (more vnodes for bigger servers).

**Q3: How does consistent hashing support replication?**
A3: A key is stored on its owner node plus the next R−1 distinct physical nodes clockwise (skipping vnodes of the same physical node, and ideally ones in the same rack or AZ). Dynamo, Cassandra and Riak use this "preference list". Reads and writes use quorums (R + W > N) across these replicas. When a node fails, its neighbours already have copies.

**Q4: How does Redis Cluster distribute keys? Is it consistent hashing?**
A4: Redis Cluster uses 16,384 fixed hash slots: slot = CRC16(key) mod 16384. Each master node owns a subset of slots, and adding a node migrates some slots to it. It achieves the same goal as consistent hashing (minimal key movement, even distribution) with explicit slot assignment instead of a ring. Hash tags (`{user:42}`) force related keys into the same slot so multi-key operations work.

**Q5: Design a distributed cache that can scale from 10 to 100 nodes without huge cache misses.**
A5: Client-side (or proxy) routing with consistent hashing and virtual nodes, so adding nodes moves only ~1/N of keys at a time, and scale gradually. Optionally replicate hot keys to two nodes. Keep membership in a coordination service (etcd/ZooKeeper) or use a proxy (Twemproxy, mcrouter), and refresh client rings. Add request coalescing and TTL jitter to absorb the misses that do occur, and warm new nodes before taking traffic. Alternatively use Redis Cluster's slot migration.

---

## 🔷 Trade-offs
✅ Advantages:
- Minimal key movement on membership change; elastic scaling; no central lookup table needed.
- Natural replication model; works for caches, DBs, LBs.

❌ Disadvantages:
- Uneven distribution without vnodes; hot keys still overload one node (need replication/splitting).
- More complex than modulo; ring membership must be consistent across clients.
- Range queries aren't possible (keys are scattered by hash).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Consistent hashing | Ring-based key distribution | रिंग पर keys का बँटवारा |
| Hash ring | Circular hash space | गोल hash जगह |
| Virtual node | Many ring positions per server | एक सर्वर की कई जगहें |
| Remapping | Keys moving to other nodes | keys का दूसरी जगह जाना |
| Preference list | Nodes holding a key's replicas | key की copies वाले सर्वर |
| Hash slot | Fixed bucket (Redis Cluster) | तय खाना |
| Hash tag | Force keys to same slot | keys को एक slot में रखना |
| Rendezvous hashing | Highest random weight method | सबसे ऊँचे score वाला सर्वर |

---

## ⚡ 3-Line Summary
**English:**
1. Consistent hashing puts keys and nodes on a ring; each key goes to the next node clockwise.
2. Adding/removing a node moves only ~1/N keys (vs ~all with `% N`); virtual nodes even out load.
3. Used in Dynamo/Cassandra, Memcached clients, CDNs, LBs; Redis Cluster uses 16,384 slots for the same goal.

**Hindi:**
1. Consistent hashing = keys और सर्वर एक रिंग पर; key अगले सर्वर पर जाती है।
2. सर्वर जोड़ने/हटाने पर सिर्फ़ ~1/N keys हिलती हैं; virtual nodes से load बराबर।
3. Dynamo, Cassandra, Memcached, CDN, LB में इस्तेमाल; Redis Cluster 16,384 slots से यही करता है।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Gaurav Sen — Consistent Hashing](https://www.youtube.com/results?search_query=consistent+hashing+gaurav+sen) | The ring, virtual nodes — best visual explanation |
| 📺 YouTube | [ByteByteGo — Consistent Hashing](https://www.youtube.com/results?search_query=consistent+hashing+bytebytego) | Why DynamoDB and Cassandra use it |
| 📝 Article | [Amazon DynamoDB — Consistent Hashing paper reference](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html) | The original Dynamo paper describing consistent hashing at scale |
| 📝 Article | [High Scalability — Consistent Hashing](http://highscalability.com/blog/2023/2/22/consistent-hashing-algorithmic-tradeoffs.html) | Virtual nodes, load imbalance, tradeoffs |
| 🐙 GitHub | [system-design-primer — Consistent Hashing](https://github.com/donnemartin/system-design-primer#consistent-hashing) | Ring diagram, adding/removing nodes |

---

## ➡️ Next Topic Suggestion
**53. Bloom Filters** — Another clever data structure used inside databases and caches: a tiny memory structure that can say "definitely not present" instantly. Next: how Bloom filters work and where they save huge amounts of disk and DB lookups.
