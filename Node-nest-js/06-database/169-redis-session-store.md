# 169. Redis Session Store
# हिंदी में: Redis Session Store — User Sessions को Redis में Store करना

---

## 🔵 Simple Definition (English)
**Redis Session Store** means saving user login session data (session ID → user info) in Redis instead of server memory. Redis is fast (in-memory), supports TTL (auto-expiry), and is shared across multiple Node.js server instances — so any server can read any user's session.

## 🔵 सरल परिभाषा (Hindi)
**Redis Session Store** मतलब user के login session data (session ID → user info) को server memory की जगह Redis में save करना। Redis fast है (in-memory), TTL support करता है (auto-expiry), और multiple Node.js servers के बीच shared रहता है — कोई भी server किसी भी user का session read कर सकता है।

---

## 🔴 Problem it Solves
Default `express-session` stores sessions in **server memory** (`MemoryStore`). This breaks in production:
1. **Memory leak** — sessions never clear automatically, server RAM grows forever.
2. **Multiple servers (horizontal scaling)** — if Zomato runs 5 Node instances behind a load balancer, a user logs in on server-1 but their next request goes to server-2 → session not found → logged out!
3. **Server restart** — deploying new code restarts the server → all sessions wiped → everyone logged out.

Redis fixes all three: shared storage across servers, built-in TTL for auto-cleanup, survives individual Node process restarts.

## 🔴 यह क्यों बना? (Hindi)
Default `express-session` sessions को **server memory** में रखता है (`MemoryStore`), जो production में तीन problems देता है:
1. **Memory leak** — sessions auto-clear नहीं होते, RAM बढ़ता रहता है।
2. **Multiple servers** — Zomato के 5 Node instances हैं तो server-1 पर login किया user अगर next request server-2 पर जाए → session नहीं मिलेगा → logout हो जायेगा!
3. **Server restart** — नया code deploy करने से memory wipe → सब logged out।

Redis तीनों problems solve करता है: shared storage, auto-TTL cleanup, process restart से unaffected।

---

## 🟢 How it Works — Step by Step

Step 1 → User logs in → Express creates a session, generates a unique `sessionId` (signed cookie sent to browser).
Step 2 → `connect-redis` store saves `sessionId → { userId, cart, role, ... }` as a Redis key (e.g. `sess:abc123`) with a TTL (e.g. 86400s = 1 day).
Step 3 → Every subsequent request, browser sends the `sessionId` cookie → Express middleware reads it, fetches session data from Redis via `GET sess:abc123`.
Step 4 → `req.session` is populated from Redis data → routes use `req.session.userId` etc.
Step 5 → On logout or TTL expiry, the Redis key is deleted (`DEL sess:abc123`) → session is gone from ALL servers instantly.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User login करता है → Express session बनाता है, unique `sessionId` generate करता है (signed cookie browser को भेजा जाता है)।
Step 2 → `connect-redis` store `sessionId → { userId, cart, role, ... }` को Redis key (जैसे `sess:abc123`) के रूप में save करता है, TTL (जैसे 86400s) के साथ।
Step 3 → हर next request पर browser `sessionId` cookie भेजता है → middleware Redis से `GET sess:abc123` करके data fetch करता है।
Step 4 → `req.session` Redis data से भर जाता है → routes `req.session.userId` use करते हैं।
Step 5 → Logout या TTL expiry पर Redis key delete हो जाती है (`DEL sess:abc123`) → session सभी servers से एक साथ गायब।

---

## 🟡 Real World Example
**Swiggy's checkout flow:** User adds items to cart while browsing (session stores `cart` temporarily before login). Swiggy runs behind a load balancer with 8 Node.js instances for scale during lunch/dinner rush. Without Redis, a user's cart would randomly disappear if their request landed on a different server. With Redis session store, all 8 instances read/write the SAME Redis instance — cart and login state are consistent no matter which server handles the request. Sessions auto-expire after 24h of inactivity (Redis TTL), keeping Redis memory clean without a cron job.

## 🟡 Real Example Hindi mein
**Swiggy का checkout flow:** User browsing के दौरान cart में items add करता है (login से पहले session में `cart` temporarily store होता है)। Swiggy lunch/dinner rush में scale के लिए load balancer के पीछे 8 Node.js instances चलाता है। Redis के बिना, अगर request किसी अलग server पर जाए तो cart randomly गायब हो जाता। Redis session store के साथ, सभी 8 instances same Redis पढ़ते/लिखते हैं — login state consistent रहता है। Sessions 24h inactivity के बाद auto-expire (Redis TTL) हो जाते हैं, बिना cron job के Redis memory clean रहती है।

---

## 💻 Code Example — Basic

```javascript
// basic-redis-session.js
// Install: npm install express express-session connect-redis redis

const express = require('express');
const session = require('express-session');
const { createClient } = require('redis');
const RedisStore = require('connect-redis').default;

const app = express();

// Create Redis client and connect
const redisClient = createClient({ url: 'redis://localhost:6379' });
redisClient.connect().catch(console.error); // connect to Redis server

// Configure express-session to use Redis as the store
app.use(session({
  store: new RedisStore({ client: redisClient, prefix: 'sess:' }), // keys look like sess:<id>
  secret: 'super-secret-key',   // used to sign the session ID cookie
  resave: false,                // don't save session if unmodified
  saveUninitialized: false,     // don't create session until something stored
  cookie: {
    maxAge: 1000 * 60 * 60 * 24, // 1 day in ms -> also sets Redis TTL
    httpOnly: true,               // JS cannot read cookie (XSS protection)
    secure: false,                // true in production (HTTPS only)
  },
}));

// Login route: store user info in session
app.post('/login', (req, res) => {
  req.session.userId = 'user_42';     // saved into Redis automatically
  req.session.role = 'customer';
  res.json({ message: 'Logged in' });
});

// Protected route: read session
app.get('/profile', (req, res) => {
  if (!req.session.userId) return res.status(401).json({ error: 'Not logged in' });
  res.json({ userId: req.session.userId, role: req.session.role });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// advanced-redis-session.js — production patterns

const express = require('express');
const session = require('express-session');
const { createClient } = require('redis');
const RedisStore = require('connect-redis').default;

const app = express();

const redisClient = createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  socket: { reconnectStrategy: (retries) => Math.min(retries * 100, 3000) }, // retry with backoff
});

// Handle Redis connection errors gracefully — don't crash the app
redisClient.on('error', (err) => console.error('Redis Client Error:', err));
redisClient.on('connect', () => console.log('Redis connected for sessions'));

(async () => {
  await redisClient.connect();
})();

app.set('trust proxy', 1); // needed behind a load balancer/reverse proxy for secure cookies

app.use(session({
  store: new RedisStore({ client: redisClient, prefix: 'myapp:sess:', ttl: 86400 }), // explicit TTL in seconds
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  rolling: true, // reset TTL on every request (sliding expiration)
  cookie: {
    maxAge: 1000 * 60 * 60 * 24,
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production', // HTTPS only in prod
    sameSite: 'lax', // CSRF protection
  },
}));

// Logout: destroy session in Redis immediately
app.post('/logout', (req, res, next) => {
  req.session.destroy((err) => {
    if (err) return next(err);          // pass error to error-handling middleware
    res.clearCookie('connect.sid');     // also clear the cookie from browser
    res.json({ message: 'Logged out' });
  });
});

// Force-logout all sessions of a user (admin action) — requires scanning keys
async function destroyAllSessionsForUser(userId) {
  const keys = await redisClient.keys('myapp:sess:*'); // NOTE: KEYS is O(n), avoid in huge prod datasets, use SCAN instead
  for (const key of keys) {
    const raw = await redisClient.get(key);
    if (!raw) continue;
    const data = JSON.parse(raw);
    if (data.userId === userId) {
      await redisClient.del(key); // kick this session out immediately
    }
  }
}

module.exports = { app, redisClient, destroyAllSessionsForUser };
```

---

## 🟠 Express.js Integration

```javascript
// Checking session + role-based middleware using Redis-backed sessions
function requireAuth(req, res, next) {
  if (!req.session?.userId) {
    return res.status(401).json({ error: 'Please log in' });
  }
  next();
}

function requireRole(role) {
  return (req, res, next) => {
    if (req.session.role !== role) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
}

app.get('/admin/dashboard', requireAuth, requireRole('admin'), (req, res) => {
  res.json({ message: 'Welcome admin' });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using default `MemoryStore` in production
✅ Correct: Always configure `RedisStore` — Express even logs a warning that `MemoryStore` is not for production.

```javascript
// Wrong
app.use(session({ secret: 'x' })); // uses in-memory store, leaks + breaks scaling

// Right
app.use(session({ store: new RedisStore({ client: redisClient }), secret: 'x' }));
```

❌ Mistake 2: Forgetting to set `cookie.secure` correctly behind a proxy
✅ Correct: set `app.set('trust proxy', 1)` and `secure: true` in production, otherwise cookies won't be set over HTTPS behind a load balancer.

---

## 🧠 Tricky Interview Question

```javascript
// Two servers (A and B) share the same Redis instance.
// User logs in via server A, then their next request hits server B.
// Will req.session.userId be available on server B?
```
Answer: **Yes.** Because both servers use `RedisStore` pointing to the same Redis instance, the session cookie (`sessionId`) sent by the browser is used by server B's `express-session` middleware to fetch the SAME session data from Redis (`GET sess:<id>`). Session data isn't tied to any one Node process — it lives in Redis, making it "stateless" from the server's perspective. This is exactly why Redis session store is required for horizontally scaled apps.

---

## ⚫ Interview Questions + Answers

Q1: Why not just use JWT instead of Redis sessions?
A1: JWT is stateless (no server storage) but harder to revoke instantly — once issued, a JWT is valid until expiry unless you maintain a blocklist (which itself needs Redis). Redis sessions can be destroyed immediately (`session.destroy()`), support server-side data without bloating the token, and are easier to update (e.g. ban a user instantly). JWT is better for stateless microservices/mobile APIs; Redis sessions are better for traditional server-rendered or cookie-based web apps needing instant revocation.

Q2: What happens if Redis goes down while using Redis session store?
A2: All session reads/writes fail — `connect-redis` will error, and users effectively get logged out or requests may hang/error depending on error handling. Mitigate with Redis Sentinel/Cluster for high availability, connection retry strategies (`reconnectStrategy`), and graceful degradation (catch errors, show "service temporarily unavailable" instead of crashing the whole app).

Q3: How does session TTL relate to cookie `maxAge`?
A3: `cookie.maxAge` controls how long the browser keeps the cookie. `connect-redis`'s `ttl` option controls how long Redis keeps the key before auto-deleting it (via Redis `EXPIRE`). They should generally match; if Redis TTL is shorter than cookie maxAge, the browser may send a cookie pointing to an already-expired/missing session.

Q4: What is `rolling: true` in express-session config?
A4: It resets the session's expiration (both cookie `maxAge` and Redis TTL) on every request — a "sliding window" session. Without it, a session expires N hours after creation regardless of activity. With it, an active user's session keeps extending, while an idle user's session still expires on schedule.

Q5: How would you scale session storage further if a single Redis instance isn't enough?
A5: Use **Redis Cluster** (sharded across multiple nodes by key hash) or **Redis Sentinel** (for failover/HA, not sharding). For session data specifically, since each session is a single small key, Cluster mode scales well because sessions are naturally partition-friendly (no cross-key transactions needed).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Traditional cookie-based session auth with multiple Node.js server instances.
- Need instant session revocation (force logout, ban users).
- Storing non-trivial session data (cart, preferences) server-side.

❌ Avoid when:
- Building a fully stateless API/microservice architecture — prefer JWT.
- Single-server app with no scaling needs — simpler stores may suffice, though Redis is still recommended for restart-safety.

---

## 📊 Visual Diagram
```
BROWSER                  LOAD BALANCER            NODE SERVERS                REDIS
┌──────────┐                                     ┌───────────┐
│ Cookie:  │── request ──▶ ┌─────────┐ ──────────▶│ Server A  │──GET sess:id──▶┌────────────┐
│ sess=id  │               │  LB     │            └───────────┘                │ sess:id →  │
│          │── request ──▶ │         │──────────▶ ┌───────────┐──GET sess:id──▶│ {userId,   │
└──────────┘               └─────────┘            │ Server B  │                 │  role,...} │
                                                   └───────────┘                └────────────┘
     Any server can serve any request — session data lives centrally in Redis
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Session Store | Where session data is persisted | Session data कहाँ रहता है |
| connect-redis | npm package bridging express-session + Redis | Redis के साथ session जोड़ने वाला package |
| TTL | Time-to-live, auto-expiry duration | Auto-expire समय |
| sessionId cookie | Signed cookie identifying the session | Session को identify करने वाला cookie |
| Sliding expiration | TTL resets on activity | Activity पर TTL reset होना |
| Horizontal scaling | Multiple server instances | कई server instances |

---

## ⚡ 3-Line Summary
English:
1. Redis session store saves login sessions centrally so any of your Node.js server instances can read/write them.
2. It solves memory leaks, multi-server session loss, and server-restart logouts that plague the default in-memory session store.
3. Use `connect-redis` + `express-session`, set proper TTL/cookie options, and handle Redis connection errors gracefully in production.

Hindi:
1. Redis session store login sessions को centrally save करता है ताकि कोई भी Node.js server instance उन्हें read/write कर सके।
2. यह memory leaks, multi-server session loss, और restart पर logout जैसी problems solve करता है।
3. `connect-redis` + `express-session` use करो, proper TTL/cookie options set करो, और production में Redis connection errors gracefully handle करो।

---

## ➡️ Next Topic
**170. Redis Pub/Sub in Node** — Redis के publish/subscribe pattern से real-time messaging और cross-server communication।
