# 23. Stateless vs Stateful
# हिंदी में: Stateless — सर्वर कुछ याद नहीं रखता, हर request अपने में पूरी; Stateful — सर्वर पिछली बातचीत/डेटा याद रखता है

---

## 🔵 Simple Definition (English)
- A **stateless** service doesn't keep any client-specific data in its own memory/disk between requests. Every request carries everything needed (token, IDs), and **any instance can handle any request**.
- A **stateful** service keeps data that later requests depend on: sessions in memory, open connections, database contents, game state. Requests must reach the **instance that holds that state**.

## 🔵 सरल परिभाषा (Hindi)
Stateless सर्वर कुछ याद नहीं रखता — हर request में token और ज़रूरी जानकारी आती है, इसलिए कोई भी सर्वर उसे संभाल सकता है।
Stateful सर्वर पिछला डेटा याद रखता है (session, कनेक्शन, DB) — इसलिए request उसी सर्वर तक पहुँचनी चाहिए।

---

## 🔴 Problem it Solves
If your app servers are stateful:
- **Scaling breaks:** user logs in on server A (session in A's memory), next request goes to B → "please log in again".
- **Failures lose data:** server A crashes → all sessions/carts in its memory are gone.
- **Deploys hurt:** restarting a server logs everyone out.
- **Auto-scaling is hard:** you can't freely remove a server that holds state.

The solution: **make compute stateless, push state into dedicated stateful systems** (DB, Redis, S3, Kafka) that are built for durability and replication.

## 🔴 यह क्यों बना? (Hindi)
अगर session सर्वर की memory में है, तो दूसरे सर्वर पर पहुँचते ही यूज़र logout, और सर्वर गिरा तो सारा डेटा ग़ायब।
हल: ऐप सर्वर को stateless रखो और state को DB, Redis, S3 जैसे सिस्टम में रखो जो डेटा सुरक्षित रखने के लिए ही बने हैं।

---

## 🟢 How it Works — Step by Step

### Stateful app server (problem)

```
Login → LB → Server A   (stores session in memory: sid=abc → user 42)
Cart  → LB → Server B   "sid=abc? I don't know you" → 401 ❌
Server A crashes → all its sessions lost ❌
```

### Stateless app server (solution)

```
                 ┌──► Server A ─┐
Request + token ─┼──► Server B ─┼──► Redis (sessions/cache)  ← state lives here
 (JWT/cookie)    └──► Server C ─┘    Postgres (data)
                                     S3 (files)
Any server can answer. Kill/add servers freely.
```

### Where state should live

```
┌──────────────────────┬───────────────────────────────┬──────────────────────────┐
│ State                │ ❌ Don't keep in app memory    │ ✅ Put it in              │
├──────────────────────┼───────────────────────────────┼──────────────────────────┤
│ Login session        │ express-session MemoryStore    │ Redis, or JWT (client)   │
│ Shopping cart        │ JS object/Map                  │ Redis / Postgres         │
│ Uploaded files       │ ./uploads on local disk        │ S3                       │
│ Cache                │ in-memory as source of truth   │ Redis (local cache only  │
│                      │                                │ as a short-lived copy)   │
│ Rate-limit counters  │ per-process counter            │ Redis INCR               │
│ Job progress         │ variable                       │ DB / queue               │
│ WebSocket rooms      │ in-memory only                 │ Redis pub/sub adapter    │
│ Scheduled jobs       │ setInterval on every instance  │ one scheduler/lock/queue │
└──────────────────────┴───────────────────────────────┴──────────────────────────┘
```

### Stateful systems are still needed — and are hard

```
Databases, caches, message brokers, search indexes, WebSocket gateways, game servers
are STATEFUL by nature. To scale/protect them:
  - Replication (copies on other nodes)       → availability, read scaling
  - Partitioning/sharding (split data)        → write scaling
  - Consensus/leader election                 → correctness (Raft in etcd, Kafka KRaft)
  - Persistent volumes (K8s StatefulSets)     → stable identity + storage
Rule: keep stateful parts FEW, managed (RDS, ElastiCache, MSK), and well understood.
```

### JWT vs server-side session (stateless auth)

```
Server-side session:  cookie sid=abc → server looks up Redis → user
                      ✅ easy revoke, small cookie   ❌ Redis lookup each request
JWT:                  Authorization: Bearer <signed token with userId, role, exp>
                      ✅ no lookup, truly stateless   ❌ hard to revoke before exp → short exp + refresh token
(Details: Topics 54, 57)
```

### Protocol level
```
HTTP     → stateless protocol (each request independent)
TCP      → stateful (connection state on both ends)
WebSocket→ stateful connection on top of a stateless-designed app
```

## 🟢 कैसे काम करता है? (Hindi)
1. Stateless में हर request के साथ token/cookie आती है; सर्वर उसी से यूज़र पहचानता है।
2. Session, cart, फ़ाइलें, counters — सब बाहर रखो: Redis, Postgres, S3।
3. अब कोई भी सर्वर कोई भी request संभाल सकता है — जोड़ो, हटाओ, restart करो, कोई फ़र्क़ नहीं।
4. DB, cache, queue जैसे stateful सिस्टम ज़रूरी हैं — उन्हें replication और sharding से सुरक्षित/स्केल करते हैं।
5. नियम: compute stateless, state कुछ ही managed सिस्टम में।

---

## 🟡 Real World Example

**The Twelve-Factor App (Heroku)** — factor VI says "execute the app as one or more stateless processes", because Heroku dynos restart at least daily and have ephemeral disks. This principle shaped modern cloud apps, Docker and Kubernetes.

**Netflix** — all edge/API services are stateless and auto-scale. State lives in Cassandra, EVCache (Memcached) and S3. Chaos Monkey can kill any instance with no user impact.

**Multiplayer games (BGMI, Fortnite)** — a match server **is** stateful: player positions live in memory. All players of a match are routed to the same game server, and matchmaking (stateless) assigns the match to a server. Stateful by necessity, but isolated.

**WhatsApp** — chat gateway servers hold millions of stateful TCP connections. Message storage and delivery state live in backend databases, so a gateway restart only means clients reconnect.

## 🟡 Real Example Hindi में
Heroku का "12-Factor App" नियम कहता है कि ऐप stateless processes में चलाओ — इसी सोच से Docker और Kubernetes बने।
BGMI का match server stateful होता है (खिलाड़ियों की लोकेशन memory में), इसलिए एक match के सब खिलाड़ी एक ही सर्वर पर भेजे जाते हैं। WhatsApp के gateway सर्वर कनेक्शन रखते हैं, पर मैसेज DB में सुरक्षित रहते हैं।

---

## 🟠 My Stack Example

### Express: MemoryStore → Redis (one-line change in idea)
```js
// ❌ default MemoryStore: breaks with 2+ instances, leaks memory, lost on restart
app.use(session({ secret: SECRET }));

// ✅ Redis-backed sessions
import { RedisStore } from 'connect-redis';
app.use(session({
  store: new RedisStore({ client: redis, prefix: 'sess:' }),
  secret: SECRET, resave: false, saveUninitialized: false,
  cookie: { httpOnly: true, secure: true, sameSite: 'lax', maxAge: 7 * 864e5 },
}));
```

### Or fully stateless with JWT
```js
const access = jwt.sign({ sub: user.id, role: user.role }, ACCESS_SECRET, { expiresIn: '15m' });
// Each request: verify signature only — no DB/Redis lookup
const payload = jwt.verify(req.headers.authorization.split(' ')[1], ACCESS_SECRET);
```

### Rate limiting must use shared state
```js
// ❌ per-process limiter: with 4 instances the real limit is 4× higher
// ✅ Redis-backed
import { RateLimiterRedis } from 'rate-limiter-flexible';
const limiter = new RateLimiterRedis({ storeClient: redis, points: 100, duration: 60 });
app.use(async (req, res, next) => {
  try { await limiter.consume(req.user?.id ?? req.ip); next(); }
  catch { res.status(429).set('Retry-After', '60').end(); }
});
```

### FastAPI: same principles
```python
# Don't do this (module-level dict = per-process state):
carts: dict[int, list] = {}

# Do this:
async def add_to_cart(user_id: int, item: Item):
    await redis.hset(f"cart:{user_id}", item.id, item.qty)
    await redis.expire(f"cart:{user_id}", 7 * 86400)
```

### Docker / Kubernetes
```yaml
# Stateless API → Deployment (any pod is interchangeable, scale freely)
kind: Deployment
spec: { replicas: 4 }
---
# Stateful DB → StatefulSet (stable name db-0, db-1 + its own persistent volume)
# In practice: prefer managed RDS/ElastiCache instead of running DBs in K8s yourself.
kind: StatefulSet
spec:
  volumeClaimTemplates: [{ metadata: { name: data }, spec: { resources: { requests: { storage: 50Gi } } } }]
```

### Frontend & mobile state (the client is stateful — that's fine)
```
Next.js / RN keep UI state, auth tokens (secure storage), cached server data (React Query).
Server stays stateless; the CLIENT sends the token every time.
Mobile: store refresh token in Keychain/Keystore (expo-secure-store), not AsyncStorage.
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between stateless and stateful services?**
A1: A stateless service keeps no client-specific data between requests. Each request is self-contained, so any instance can serve it, and instances can be added, removed or restarted freely. A stateful service retains data that affects future requests (sessions, connections, stored data), so requests depend on a specific instance, and scaling or failover requires replication, partitioning or affinity.

**Q2: Why are stateless services easier to scale?**
A2: All instances are interchangeable, so the load balancer can use any algorithm, auto-scaling can add or remove instances without migrating data, failures lose nothing (just retry on another instance), and deploys can replace instances one by one. The state is centralized in purpose-built stores that handle replication and durability.

**Q3: How do you make a legacy app with in-memory sessions horizontally scalable?**
A3: Quick fix: sticky sessions at the load balancer, but that gives uneven load and loses sessions when an instance dies. Proper fix: move sessions to a shared store (Redis) or switch to token-based auth (JWT with refresh tokens). Also move uploaded files to S3, in-memory caches to Redis, counters and locks to Redis, and cron jobs to a single scheduler or distributed locks.

**Q4: Can you avoid stateful components entirely?**
A4: No. Databases, caches, queues and search indexes hold state by definition, and some workloads are inherently stateful (WebSocket gateways, game servers, stream processing). The goal is to isolate state into a few well-managed systems (often managed cloud services) with replication and backups, and keep everything else stateless.

**Q5: JWT makes auth stateless — what's the downside?**
A5: You can't easily revoke a JWT before it expires, since the server doesn't look anything up. Logout, banning or a role change won't take effect until expiry. Mitigations: short-lived access tokens (5–15 min) with refresh tokens stored server-side (revocable), a small denylist in Redis for revoked token IDs, and a token version per user checked occasionally. JWTs are also bigger than session IDs and must not hold sensitive data, since the payload is only base64-encoded, not encrypted.

---

## 🔷 Trade-offs
✅ Stateless:
- Easy horizontal scaling, failover, deploys; simple load balancing.

❌ Stateless:
- External state store adds network latency (Redis ~1 ms) and a dependency.
- Larger requests (tokens).

✅ Stateful:
- Low latency (data in memory), natural for connections/games/streams.

❌ Stateful:
- Hard to scale and recover; needs replication, affinity, careful deploys.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stateless | No client data kept between requests | कुछ याद नहीं रखता |
| Stateful | Keeps data across requests | पिछला डेटा याद रखता है |
| Session | User's login/interaction data | यूज़र का session डेटा |
| Session affinity | Sticky routing to one server | एक सर्वर से चिपकना |
| JWT | Signed self-contained token | हस्ताक्षरित टोकन |
| Ephemeral | Temporary, lost on restart | अस्थायी |
| StatefulSet | K8s object for stateful apps | stateful ऐप के लिए K8s ढाँचा |
| 12-Factor App | Cloud app design principles | क्लाउड ऐप के 12 नियम |

---

## ⚡ 3-Line Summary
**English:**
1. Stateless services keep nothing between requests → any instance can serve any request → easy scaling.
2. Put sessions, carts, files, counters and locks in Redis/DB/S3, or use JWTs.
3. Stateful systems (DBs, caches, gateways) are necessary — keep them few, managed and replicated.

**Hindi:**
1. Stateless सर्वर कुछ याद नहीं रखता → कोई भी सर्वर request संभाल सकता है → आसान scaling।
2. Session, cart, फ़ाइलें, counters → Redis/DB/S3 में, या JWT इस्तेमाल करो।
3. DB, cache जैसे stateful सिस्टम ज़रूरी हैं — उन्हें कम, managed और replicated रखो।

---

## ➡️ Next Topic Suggestion
**24. Single Point of Failure (SPOF)** — The last fundamental. Next: how to find every component whose failure takes the whole system down, and how to eliminate it.
