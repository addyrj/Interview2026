# 111. Connection Pooling and Limits
# हिंदी में: Connection Pooling और Limits

---

## 🔵 Simple Definition (English)
A **connection pool** is a set of already-open TCP connections to MongoDB that the driver **reuses** for many operations instead of opening a new connection each time. Each `MongoClient` owns one pool per server it talks to. Key options: **`maxPoolSize`** (default 100), **`minPoolSize`** (default 0), **`maxIdleTimeMS`**, **`waitQueueTimeoutMS`**, **`maxConnecting`** (default 2). The server also has a global limit (`net.maxIncomingConnections`, bounded by OS limits and RAM — each connection uses roughly 1 MB of stack/memory). Rule: **create ONE client per process, reuse it everywhere.**

## 🔵 सरल परिभाषा (Hindi)
**Connection pool** MongoDB से पहले से खुले TCP connections का समूह है जिसे driver हर बार नया connection खोलने की जगह कई operations के लिए **reuse** करता है। हर `MongoClient` जिस server से बात करता है उसके लिए एक pool रखता है। मुख्य options: **`maxPoolSize`** (default 100), **`minPoolSize`** (default 0), **`maxIdleTimeMS`**, **`waitQueueTimeoutMS`**, **`maxConnecting`** (default 2)। Server की भी global limit है (`net.maxIncomingConnections`, OS limits और RAM से बँधी — हर connection ~1 MB memory लेता है)। नियम: **हर process में एक client बनाओ, हर जगह reuse करो।**

---

## 🔴 Problem it Solves
Opening a connection costs a TCP handshake, TLS negotiation and authentication — tens of milliseconds. Doing it per request makes the app slow, and thousands of short-lived connections can overwhelm `mongod` (memory, file descriptors, "too many connections"). Pooling amortises the cost and **caps concurrency** so a traffic spike queues in the app instead of crashing the database. Serverless functions (Lambda) are a special trap: each cold start can create a new pool, multiplying connections.

## 🔴 यह क्यों बना? (Hindi)
Connection खोलने में TCP handshake, TLS negotiation और authentication लगता है — दसियों milliseconds। हर request पर यह करने से app धीमा होता है और हज़ारों छोटे connections `mongod` को दबा देते हैं (memory, file descriptors, "too many connections")। Pooling यह लागत बाँटती है और **concurrency सीमित** करती है ताकि traffic spike database की जगह app में queue हो। Serverless (Lambda) खास जाल है: हर cold start नया pool बना सकता है, connections गुणा हो जाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `new MongoClient(uri, { maxPoolSize: 20 })` + `connect()`; the driver opens `minPoolSize` connections and a monitoring connection per server.
Step 2 → An operation (`find`, `insertOne`) **checks out** an idle connection; if none is idle and the pool is below `maxPoolSize`, it opens a new one (at most `maxConnecting` at once).
Step 3 → If the pool is at `maxPoolSize`, the operation **waits in a queue**; after `waitQueueTimeoutMS` it fails with `MongoWaitQueueTimeoutError`.
Step 4 → When the operation finishes, the connection is **checked in** and reused. Cursors/transactions hold a connection until they close.
Step 5 → Idle connections beyond `minPoolSize` are closed after `maxIdleTimeMS`.
Step 6 → **Capacity math:** total server connections ≈ (#app instances × maxPoolSize) + monitoring. Keep it well below the server limit (e.g., 20 pods × 50 = 1000).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `new MongoClient(uri, { maxPoolSize: 20 })` + `connect()`; driver `minPoolSize` connections और हर server के लिए एक monitoring connection खोलता है।
Step 2 → Operation (`find`, `insertOne`) idle connection **check out** करता है; idle न हो और pool `maxPoolSize` से नीचे हो तो नया खोलता है (एक समय में अधिकतम `maxConnecting`)।
Step 3 → Pool `maxPoolSize` पर हो तो operation **queue में इंतज़ार** करता है; `waitQueueTimeoutMS` बाद `MongoWaitQueueTimeoutError` से fail।
Step 4 → Operation खत्म होने पर connection **check in** होकर reuse होता है। Cursors/transactions बंद होने तक connection पकड़े रखते हैं।
Step 5 → `minPoolSize` से ज़्यादा idle connections `maxIdleTimeMS` बाद बंद हो जाते हैं।
Step 6 → **Capacity गणित:** server पर कुल connections ≈ (app instances × maxPoolSize) + monitoring। इसे server limit से काफी नीचे रखो (जैसे 20 pods × 50 = 1000)।

---

## 🟡 Real World Example
**Swiggy** runs 40 Node pods of the order service, each with `maxPoolSize: 50`. That is up to 2000 connections to the cluster. After a deploy, a developer accidentally moves `new MongoClient()` inside the request handler; each request opens its own pool and connections spike to 12,000, Atlas hits its tier limit and new requests fail with "connection refused / too many connections". The fix: one shared client at module scope and a documented budget of `pods × maxPoolSize`. For the Lambda-based invoice generator they cache the client in a global variable so warm invocations reuse it, with `maxPoolSize: 1`.

## 🟡 Real Example Hindi mein
**Swiggy** की order service के 40 Node pods हैं, हर एक `maxPoolSize: 50` के साथ — cluster पर 2000 connections तक। Deploy के बाद developer गलती से `new MongoClient()` request handler के अंदर ले जाता है; हर request अपना pool बनाती है और connections 12,000 तक पहुँचते हैं, Atlas tier limit छू लेता है और नई requests "too many connections" से fail होती हैं। Fix: module स्तर पर एक shared client और `pods × maxPoolSize` का budget। Lambda आधारित invoice generator में client global variable में cache होता है ताकि warm invocations reuse करें, `maxPoolSize: 1` के साथ।

---

## 💻 Code Example — Basic

```javascript
// pool.js — executed against mongod 8.0.4 (port 27131)
const { MongoClient } = require('mongodb');
(async () => {
  const c = new MongoClient('mongodb://127.0.0.1:27131', {
    maxPoolSize: 3,          // at most 3 sockets to this server from THIS client
    minPoolSize: 1,          // keep 1 warm connection
    waitQueueTimeoutMS: 500, // fail fast if no connection frees up within 0.5 s
    maxIdleTimeMS: 30000,    // close idle sockets after 30 s
  });
  await c.connect();
  const col = c.db('shop').collection('orders');

  // 10 concurrent operations share only 3 pooled connections (others queue briefly)
  await Promise.all([...Array(10)].map(() => c.db('shop').command({ ping: 1 }).then(() => col.find().toArray())));

  const st = await c.db('admin').command({ serverStatus: 1 });
  console.log('server conns', st.connections.current);
  // Output: server conns 7   (3 pooled + monitoring sockets + the admin/shell connections; varies)
  await c.close();           // closes the pool
})();
```
Server side — see what the server thinks:
```javascript
// mongosh
db.serverStatus().connections
// { current: 8, available: 838852, totalCreated: 84, active: 4, ... }   (values vary)
// available = (OS/limit based maximum) - current
```

## 💻 Code Example — Advanced

```javascript
// db.js — singleton client (module cache makes this a process-wide singleton)
const { MongoClient } = require('mongodb');

const client = new MongoClient(process.env.MONGO_URI, {
  maxPoolSize: Number(process.env.POOL_MAX || 50),
  minPoolSize: 5,
  maxConnecting: 2,                 // limit connection-creation storms
  waitQueueTimeoutMS: 2000,         // surface saturation as an error instead of hanging
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 30000,
});

// Observe pool behaviour (CMAP events)
client.on('connectionPoolCreated', e => console.log('pool created', e.options.maxPoolSize));
client.on('connectionCheckOutFailed', e => console.warn('checkout failed:', e.reason)); // timeout/connectionError
client.on('connectionPoolCleared', () => console.warn('pool cleared (server error/failover)'));

let connecting;                      // memoize the connect() promise
const getDb = async () => { connecting ??= client.connect(); await connecting; return client.db('app'); };

// Serverless (AWS Lambda): cache across invocations, keep pool tiny
// let cached; exports.handler = async () => { cached ??= new MongoClient(uri, { maxPoolSize: 1 }).connect(); ... }

process.on('SIGTERM', async () => { await client.close(); process.exit(0); }); // graceful shutdown

module.exports = { getDb };
```

```yaml
# mongod.conf — server-side cap (default is effectively the OS limit ~ 838860)
net:
  maxIncomingConnections: 5000   # refuse beyond this; also raise ulimit -n (file descriptors)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose uses the driver pool underneath: set options in connect()
const mongoose = require('mongoose');
const express = require('express');

mongoose.connect(process.env.MONGO_URI, {
  maxPoolSize: 20,            // Mongoose >= 6 uses maxPoolSize (older: poolSize)
  minPoolSize: 2,
  waitQueueTimeoutMS: 3000,
  bufferCommands: false,      // fail immediately instead of buffering when disconnected
});

const app = express();
app.get('/pool', (req, res) => {
  // Expose how many sockets Mongoose's client is allowed
  res.json({ readyState: mongoose.connection.readyState, maxPoolSize: mongoose.connection.getClient().options.maxPoolSize });
});
// ONE mongoose.connect() per process; every model shares the same pool.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: New client per request
```javascript
// Wrong: opens a new pool each call and never closes it -> connection leak
app.get('/x', async (req, res) => { const c = await MongoClient.connect(uri); res.json(await c.db().collection('a').find().toArray()); });
// Right: module-level shared client
const c = new MongoClient(uri); const ready = c.connect();
app.get('/x', async (req, res) => { await ready; res.json(await c.db().collection('a').find().toArray()); });
```
❌ Mistake 2: Setting `maxPoolSize` huge ("more is faster"). More sockets than the server's CPU cores can serve only adds contention; size by concurrency actually needed.

❌ Mistake 3: Ignoring `pods × maxPoolSize` when autoscaling. 100 pods x 100 = 10,000 connections.

❌ Mistake 4: Calling `client.close()` after each request in a long-running server (defeats pooling) or never closing in scripts (process hangs).

---

## 🧠 Tricky Interview Question
**Q:** `maxPoolSize` is 10 and 50 requests arrive at once, each running a 100 ms query. Does the app fail? What changes if each request starts a transaction and awaits an external API for 2 s before committing?

**Answer:** No failure in the first case: 10 run in parallel, 40 wait in the queue, and all finish in roughly 5 rounds x 100 ms = ~500 ms (assuming `waitQueueTimeoutMS` is unset or larger than ~400 ms). In the second case a transaction/session **pins its connection** for the entire 2 s, so 10 transactions block the pool; the remaining 40 wait ~2 s per round (~8 s total) and any with `waitQueueTimeoutMS` shorter than that fail with `MongoWaitQueueTimeoutError`. Lesson: never hold a transaction (or an open cursor) across slow external I/O.

---

## ⚫ Interview Questions + Answers

Q1: What is the default `maxPoolSize`?
A1: 100 (driver default for most official drivers). `minPoolSize` default 0.

Q2: Why does each MongoClient also have extra connections?
A2: Monitoring connections (heartbeats, RTT) per server, separate from the operation pool, so server discovery isn't starved by busy operation sockets.

Q3: How to handle MongoDB in AWS Lambda?
A3: Create the client outside the handler (global scope) so warm invocations reuse it, small `maxPoolSize` (1-5), use Atlas serverless/RDS-proxy-like limits awareness, and set `maxIdleTimeMS`.

Q4: What error appears on pool exhaustion vs server limit?
A4: Pool: `MongoWaitQueueTimeoutError` (client-side). Server limit: connection refused / `too many open connections` (server `connections.available` 0).

Q5: How do you size the pool?
A5: Estimate concurrent in-flight operations (throughput x latency by Little's law: 1000 ops/s x 0.02 s = 20), add headroom, and ensure instances x pool < server limit.

---

## 🔷 When to Use + When Not to Use
✅ Tune the pool when:
- Under load tests you see waits/timeouts, or total connections near the server limit

✅ Keep defaults when:
- Small apps with modest traffic

❌ Avoid:
- Per-request clients, giant pool sizes, or long-held sessions across slow calls

---

## 📊 Visual Diagram
```
CONNECTION POOL (maxPoolSize = 3)
─────────────────────────────────────────────────
 requests:  R1 R2 R3 R4 R5 ...
              │  │  │   └──┐ wait queue (waitQueueTimeoutMS)
              ▼  ▼  ▼      │
          ┌─────────────┐  │
          │ conn1 conn2 │◀─┘ released ones are reused
          │ conn3       │
          └──────┬──────┘
                 ▼
            mongod  (connections.current ≈ pods × maxPoolSize + monitoring)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Connection pool | Reusable open connections | Reuse होने वाले खुले connections |
| maxPoolSize | Max sockets per client/server | अधिकतम sockets |
| minPoolSize | Warm connections kept | हमेशा तैयार connections |
| waitQueueTimeoutMS | Wait limit for a connection | Connection का इंतज़ार limit |
| maxConnecting | Parallel connection creations | एक साथ बनते connections |
| Check out/in | Borrow/return a connection | Connection लेना/लौटाना |
| Singleton client | One client per process | प्रति process एक client |

---

## ⚡ 3-Line Summary
English:
1. A pool reuses open connections; one `MongoClient` per process, shared everywhere.
2. Tune `maxPoolSize`, `minPoolSize`, `waitQueueTimeoutMS`; total server connections ≈ instances x maxPoolSize.
3. Never create clients per request and never hold transactions/cursors across slow external calls.

Hindi:
1. Pool खुले connections reuse करता है; प्रति process एक `MongoClient`, हर जगह shared।
2. `maxPoolSize`, `minPoolSize`, `waitQueueTimeoutMS` tune करो; server connections ≈ instances x maxPoolSize।
3. हर request पर client मत बनाओ और धीमी external calls के दौरान transactions/cursors मत पकड़ो।

---

## ➡️ Next Topic
**112. MongoDB with Docker and Docker Compose** — Running MongoDB in containers.
