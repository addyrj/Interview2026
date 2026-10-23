# 22. Load Balancing Algorithms
# हिंदी में: Load Balancing Algorithms — Load Balancer किस नियम से तय करता है कि अगली request किस सर्वर पर जाए

---

## 🔵 Simple Definition (English)
A **load balancing algorithm** is the rule a load balancer uses to choose which server gets the next request. Common ones: **Round Robin, Weighted Round Robin, Least Connections, Least Response Time, IP Hash, Consistent Hashing, Random / Power of Two Choices**.

## 🔵 सरल परिभाषा (Hindi)
Load balancing algorithm वो नियम है जिससे LB चुनता है कि अगली request किस सर्वर पर भेजे — बारी-बारी (Round Robin), सबसे कम व्यस्त (Least Connections), या यूज़र के IP के हिसाब से (IP Hash) आदि।

---

## 🔴 Problem it Solves
"Just spread traffic" isn't enough:
- Servers may have **different capacity** (old 2-core + new 8-core).
- Requests have **different costs** (a 5 ms GET vs a 3 s report export).
- Some workloads need the **same user to hit the same server** (in-memory cache, WebSocket, sessions).
- When servers are **added/removed**, you don't want every user/cache key to move.

Different algorithms solve different versions of this problem.

## 🔴 यह क्यों बना? (Hindi)
सब सर्वर एक जैसे ताक़तवर नहीं होते, सब requests एक जैसी भारी नहीं होतीं, और कभी-कभी एक यूज़र को हमेशा एक ही सर्वर पर भेजना पड़ता है।
इसलिए अलग-अलग स्थितियों के लिए अलग नियम (algorithms) बने।

---

## 🟢 How it Works — Step by Step

### 1. Round Robin (default almost everywhere)
```
Requests: 1  2  3  4  5  6
Servers:  A  B  C  A  B  C
✅ simple, fair when servers & requests are similar
❌ ignores load; a slow request still gets the next one queued behind it
```

### 2. Weighted Round Robin
```
A (weight 3, 8-core)  B (weight 1, 2-core)
Order: A A A B A A A B ...
✅ mixed hardware, canary (new version weight 1 vs old weight 9 = 10% traffic)
```

### 3. Least Connections
```
A: 12 active   B: 3 active   C: 7 active   → next goes to B
✅ variable request durations, long-lived connections (WebSockets, file downloads)
❌ needs connection tracking; "connection" ≠ real CPU load
(Weighted least connections also exists.)
```

### 4. Least Response Time / Least Outstanding Requests
```
Pick server with fewest in-flight requests and/or lowest recent latency.
AWS ALB: "least outstanding requests" option.
✅ adapts to slow servers automatically (GC pause, noisy neighbor)
```

### 5. IP Hash / Source Hash (sticky without cookies)
```
server = hash(client_ip) % N
Same IP → same server (until N changes)
✅ simple stickiness (session affinity)
❌ uneven (many users behind one corporate/mobile carrier NAT IP → one hot server)
❌ when N changes, almost everyone is remapped
```

### 6. Consistent Hashing (Topic 52 in depth)
```
Servers and keys placed on a ring (0 … 2^32).
Key goes to the next server clockwise.

        A
     /     \
   key1     B        add server D between A and B →
    |       |        only keys between A and D move (≈ 1/N), not everything
     \     /
        C
✅ caches (Memcached/Redis client sharding), sticky routing at scale, CDNs, Maglev
✅ "virtual nodes" fix uneven distribution
```

### 7. Random & Power of Two Choices (P2C)
```
Random: pick any server — surprisingly OK at large scale.
P2C:   pick 2 random servers, send to the one with fewer active requests.
✅ near-optimal balance, no global state, avoids "herd" to the single least-loaded server
Used by: Envoy, Nginx (random two least_conn), Netflix, gRPC clients, HAProxy
```

### Cheat sheet

```
┌─────────────────────────────┬────────────────────────────────────────────┐
│ Situation                   │ Use                                        │
├─────────────────────────────┼────────────────────────────────────────────┤
│ Identical servers, short    │ Round Robin                                │
│ similar requests            │                                            │
│ Different server sizes /    │ Weighted Round Robin                       │
│ canary release              │                                            │
│ Long / variable requests,   │ Least Connections / Least Outstanding Req. │
│ WebSockets                  │                                            │
│ Need user → same server     │ Cookie stickiness (L7) > IP hash           │
│ Cache nodes, sharded data   │ Consistent hashing                         │
│ Huge scale, many LBs        │ Power of Two Choices                       │
│ Between regions             │ Geo / latency-based DNS                    │
└─────────────────────────────┴────────────────────────────────────────────┘
```

### Static vs Dynamic
```
Static  (no server state):  Round Robin, Weighted RR, IP Hash, Random
Dynamic (uses live load):   Least Connections, Least Response Time, P2C
```

## 🟢 कैसे काम करता है? (Hindi)
1. Round Robin: बारी-बारी A, B, C, A, B, C — आसान और सबसे आम।
2. Weighted: ताक़तवर सर्वर को ज़्यादा हिस्सा; canary में नए version को 10%।
3. Least Connections: जिसके पास अभी सबसे कम काम है, उसे भेजो — लंबी requests/WebSocket के लिए।
4. IP Hash / Consistent Hashing: एक यूज़र या key हमेशा एक ही सर्वर पर; consistent hashing में सर्वर जुड़ने पर कम keys हिलती हैं।
5. Power of Two: दो random सर्वर चुनो, जो कम व्यस्त हो उसे दो — बड़े स्केल पर बहुत अच्छा।

---

## 🟡 Real World Example

**Canary releases at Swiggy/Flipkart** — weighted routing sends 5% of traffic to the new version. If error rates stay normal, weights move 5 → 25 → 50 → 100%.

**Discord** — uses consistent hashing so all events for a given guild (server) go to the same process, which holds that guild's state in memory.

**Netflix Zuul / Envoy** — use Power of Two Choices with latency awareness, which avoids overloading a single "least loaded" server when thousands of LB instances make decisions independently.

**Memcached at Facebook** — client-side consistent hashing spreads billions of cache keys across thousands of cache servers. Adding a server moves only a small fraction of keys, so the database isn't flooded with misses.

## 🟡 Real Example Hindi में
Swiggy/Flipkart नया version पहले 5% ट्रैफ़िक पर चलाते हैं (weighted), सब ठीक रहा तो धीरे-धीरे 100%।
Discord में एक guild का सारा ट्रैफ़िक consistent hashing से एक ही process पर जाता है। Facebook के हज़ारों cache सर्वर consistent hashing से keys बाँटते हैं, ताकि नया सर्वर जुड़ने पर सब cache न बिगड़े।

---

## 🟠 My Stack Example

### Nginx — all main algorithms
```nginx
upstream rr        { server a:3000; server b:3000; }                     # round robin (default)
upstream weighted  { server a:3000 weight=3; server b:3000 weight=1; }   # 75% / 25%
upstream leastconn { least_conn; server a:3000; server b:3000; }
upstream iphash    { ip_hash; server a:3000; server b:3000; }            # sticky by IP
upstream consistent{ hash $request_uri consistent; server cache1:80; server cache2:80; } # ketama
upstream p2c       { random two least_conn; server a:3000; server b:3000; server c:3000; }
```

### Canary with Nginx split_clients (5% to v2)
```nginx
split_clients "${remote_addr}${http_user_agent}" $api_pool {
  5%   api_v2;
  *    api_v1;
}
upstream api_v1 { server api-v1:3000; }
upstream api_v2 { server api-v2:3000; }
location /api/ { proxy_pass http://$api_pool; }
```

### AWS ALB
```
Target group attribute: load_balancing.algorithm.type = round_robin | least_outstanding_requests
Weighted target groups on a listener rule: v1 = 95, v2 = 5  (canary)
Stickiness: lb_cookie, duration 1h (only if you really need it)
```

### Consistent hashing in Node (choose Redis shard for a key)
```js
import { createHash } from 'crypto';

class HashRing {
  constructor(nodes, vnodes = 100) {
    this.ring = [];
    for (const n of nodes)
      for (let i = 0; i < vnodes; i++) this.ring.push({ h: this.hash(`${n}#${i}`), n });
    this.ring.sort((a, b) => a.h - b.h);
  }
  hash(s) { return parseInt(createHash('md5').update(s).digest('hex').slice(0, 8), 16); }
  get(key) {
    const h = this.hash(key);
    let lo = 0, hi = this.ring.length;               // binary search first node >= h
    while (lo < hi) { const m = (lo + hi) >> 1; this.ring[m].h < h ? (lo = m + 1) : (hi = m); }
    return this.ring[lo % this.ring.length].n;
  }
}
const ring = new HashRing(['redis-1', 'redis-2', 'redis-3']);
ring.get('user:42');   // → always the same node for this key
```

### Socket.IO behind multiple servers
- Socket.IO's long-polling fallback needs **sticky sessions** (cookie or IP hash), or you force `transports: ['websocket']`. Use least connections for WebSocket gateways.

---

## ⚫ Interview Questions + Answers

**Q1: Name common load balancing algorithms and when you'd use each.**
A1: Round robin for identical servers and uniform requests. Weighted round robin for heterogeneous servers or canary traffic splits. Least connections or least outstanding requests for variable-duration or long-lived requests (WebSockets, uploads). IP hash or cookie affinity when a client must stick to a server. Consistent hashing for caches or sharded state, where minimal remapping matters. Power of two choices for large-scale distributed LBs needing good balance without global state.

**Q2: Why is round robin sometimes bad?**
A2: It ignores actual load. If requests vary in cost (some take 5 ms, others 5 s) or servers differ in capacity, some servers pile up work while others idle. A server stuck in a GC pause keeps receiving its share. Least outstanding requests or P2C adapt to real load.

**Q3: What's the problem with IP hash, and what's better?**
A3: Many users share one public IP (mobile carrier NAT, corporate proxies), so one server gets a disproportionate load. Also, plain `hash % N` remaps almost all clients when N changes. For stickiness, prefer L7 cookie-based affinity, or better, make servers stateless. For sharding, use consistent hashing with virtual nodes.

**Q4: Explain the "power of two choices" algorithm and why it works well.**
A4: For each request, randomly choose two servers and send the request to the less loaded one. Pure "least loaded" across many independent load balancers causes herding, because they all pick the same server at once. Pure random gives uneven load. Two random choices reduce the maximum load exponentially compared to one random choice, need only local information, and avoid herding. Envoy and Nginx's `random two` implement it.

**Q5: How would you do a canary release with a load balancer?**
A5: Deploy the new version as a separate target group or pool. Use weighted routing to send a small percentage (1–5%) of traffic to it, optionally by header or cookie for internal users first. Monitor error rate, latency and business metrics against the baseline. Increase the weight gradually, and roll back instantly by setting the weight to 0 if metrics degrade. Tools: ALB weighted target groups, Nginx `split_clients`, Argo Rollouts, Istio.

---

## 🔷 Trade-offs
✅ Static algorithms (RR, weighted, hash): simple, predictable, no state.
❌ Blind to real load.

✅ Dynamic algorithms (least conn, P2C, least time): adapt to real load and slow servers.
❌ Need tracking, more complex; metrics can be noisy.

✅ Sticky/hash algorithms: locality (cache hits, in-memory state).
❌ Uneven distribution, harder failover, users "stuck" on a bad server.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Round Robin | Take turns in order | बारी-बारी से |
| Weighted | Proportional to capacity | क्षमता के अनुपात में |
| Least Connections | Fewest active connections | सबसे कम व्यस्त |
| IP Hash | Same IP → same server | एक IP, एक सर्वर |
| Consistent Hashing | Ring-based, minimal remapping | रिंग पर hashing, कम बदलाव |
| Virtual nodes | Many ring points per server | एक सर्वर के कई बिंदु |
| Power of Two Choices | Pick 2 random, choose lighter | दो में से हल्का चुनो |
| Canary | Small % traffic to new version | नए version पर थोड़ा ट्रैफ़िक |
| Session affinity | Sticky routing | एक यूज़र को एक सर्वर से जोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. Round robin by default; weighted for mixed capacity or canary; least connections for long/variable requests.
2. Hash-based (IP hash, consistent hashing) when the same key must reach the same server; consistent hashing minimizes reshuffling.
3. Power of Two Choices gives near-optimal balance at scale; prefer stateless servers over sticky sessions.

**Hindi:**
1. आम तौर पर Round Robin; अलग क्षमता/canary के लिए Weighted; लंबी requests के लिए Least Connections।
2. एक key को एक सर्वर पर भेजना हो तो hashing; consistent hashing में कम उथल-पुथल।
3. बड़े स्केल पर Power of Two Choices; sticky sessions से बेहतर stateless सर्वर।

---

## ➡️ Next Topic Suggestion
**23. Stateless vs Stateful** — Sticky sessions keep coming up. Next: the core design idea behind easy scaling, stateless vs stateful services, and where state should live.
