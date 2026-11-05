# 110. Monitoring MongoDB (mongostat, Atlas metrics)
# हिंदी में: MongoDB Monitoring (mongostat, Atlas metrics)

---

## 🔵 Simple Definition (English)
**Monitoring** means continuously measuring the health and performance of MongoDB so you can detect problems before users do. Built-in tools: **`mongostat`** (per-second operation counters, cache, connections), **`mongotop`** (time spent reading/writing per collection), **`db.serverStatus()`**, **`db.currentOp()`**, **`db.collection.stats()`**, the **profiler** (`system.profile`) and the **slow-query log**. Managed tools: **Atlas metrics/Performance Advisor/alerts**, Ops Manager, Prometheus `mongodb_exporter` + Grafana. Key signals: **operations/sec, connections, query latency, WiredTiger cache usage, replication lag, disk/IOPS, page faults, queues, slow queries**.

## 🔵 सरल परिभाषा (Hindi)
**Monitoring** का मतलब MongoDB की health और performance को लगातार मापना ताकि users से पहले समस्या पकड़ी जा सके। Built-in tools: **`mongostat`** (प्रति सेकंड operation counters, cache, connections), **`mongotop`** (हर collection पर read/write का समय), **`db.serverStatus()`**, **`db.currentOp()`**, **`db.collection.stats()`**, **profiler** (`system.profile`) और **slow-query log**। Managed tools: **Atlas metrics/Performance Advisor/alerts**, Ops Manager, Prometheus `mongodb_exporter` + Grafana। मुख्य signals: **operations/sec, connections, query latency, WiredTiger cache usage, replication lag, disk/IOPS, page faults, queues, slow queries**।

---

## 🔴 Problem it Solves
Databases degrade quietly: a missing index makes a query 100x slower, a connection leak slowly exhausts the pool, the working set outgrows RAM, a secondary lags minutes behind. Without metrics you only learn from angry users or a crash. Monitoring gives early warning, capacity planning data, and evidence to debug incidents.

## 🔴 यह क्यों बना? (Hindi)
Databases चुपचाप खराब होते हैं: index न होने से query 100 गुना धीमी, connection leak से pool धीरे-धीरे खत्म, working set RAM से बड़ा, secondary मिनटों पीछे। Metrics के बिना पता गुस्साए users या crash से चलता है। Monitoring early warning, capacity planning data और incident debug के सबूत देती है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Collect:** `mongod` keeps internal counters (`serverStatus`): opcounters, connections, WiredTiger cache, network, memory, replication info.
Step 2 → **View live:** `mongostat` samples these every N seconds and prints the deltas: `insert query update delete getmore command | dirty used | vsize res | qrw arw | net_in net_out | conn`. `mongotop` shows read/write time per namespace.
Step 3 → **Find slow operations:** enable the profiler (`db.setProfilingLevel(1, { slowms: 100 })`) which writes slow ops into `system.profile`; check `db.currentOp()` for what is running now; `explain("executionStats")` for why.
Step 4 → **Replication:** `rs.status()` and `rs.printSecondaryReplicationInfo()` show lag; alert if lag > N seconds.
Step 5 → **Aggregate & alert:** export to Atlas / Prometheus + Grafana; set alerts (CPU > 80%, connections > 80% of limit, replication lag, cache dirty > 20%, disk < 20%).
Step 6 → **Act:** add indexes, fix queries, tune pool sizes, scale up/out.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Collect:** `mongod` अंदर counters रखता है (`serverStatus`): opcounters, connections, WiredTiger cache, network, memory, replication info।
Step 2 → **Live देखो:** `mongostat` हर N सेकंड पर इनके deltas छापता है: `insert query update delete getmore command | dirty used | vsize res | qrw arw | net_in net_out | conn`। `mongotop` हर namespace का read/write समय दिखाता है।
Step 3 → **Slow operations ढूँढो:** profiler चालू करो (`db.setProfilingLevel(1, { slowms: 100 })`), slow ops `system.profile` में लिखे जाते हैं; `db.currentOp()` से अभी क्या चल रहा है; `explain("executionStats")` से क्यों।
Step 4 → **Replication:** `rs.status()` और `rs.printSecondaryReplicationInfo()` lag दिखाते हैं; lag > N सेकंड पर alert।
Step 5 → **Aggregate और alert:** Atlas / Prometheus + Grafana; alerts (CPU > 80%, connections limit का 80%, replication lag, dirty cache > 20%, disk < 20%)।
Step 6 → **Action:** index जोड़ो, queries सुधारो, pool tune करो, scale करो।

---

## 🟡 Real World Example
During a **Zomato** dinner rush (8 PM), the Atlas dashboard alerts: connections at 85% and query p95 latency doubled. The on-call engineer opens **Performance Advisor**, which flags `restaurants.find({city, cuisine}).sort({rating})` doing a collection scan and suggests index `{city:1, cuisine:1, rating:-1}`. After building the index (rolling, from the UI), latency drops back and `mongostat` shows `query` ops/sec steady with `res` memory flat. A connection leak in one microservice (new client per request) is found through the "connections by client IP" chart.

## 🟡 Real Example Hindi mein
**Zomato** में रात 8 बजे dinner rush के दौरान Atlas dashboard alert देता है: connections 85% और query p95 latency दोगुनी। On-call engineer **Performance Advisor** खोलता है जो बताता है कि `restaurants.find({city, cuisine}).sort({rating})` collection scan कर रही है और index `{city:1, cuisine:1, rating:-1}` सुझाता है। Index बनने के बाद latency वापस सामान्य और `mongostat` में `query` ops/sec स्थिर। "connections by client IP" chart से एक microservice में connection leak (हर request पर नया client) मिलता है।

---

## 💻 Code Example — Basic

```bash
# mongostat: 2 samples, 1 second apart (mongod 8.0.4, port 27131, idle server)
mongostat --port 27131 -n 2
# insert query update delete getmore command dirty used flushes vsize   res qrw arw net_in net_out conn  time
#     *0    *0     *0     *0       0     0|0  0.0% 0.0%       0  443G 39.0M 0|0 0|0   111b   83.6k    3  <timestamp>
# (*0 = operation replicated, not issued locally. Exact numbers differ on your machine.)

# mongotop: per-collection read/write time, refresh every 1 second
mongotop --port 27131 1
#                     ns    total    read    write   <timestamp>
#   admin.system.version      0ms     0ms      0ms
#  config.system.sessions      0ms     0ms      0ms
# (Press Ctrl+C to stop)
```

```javascript
// mongosh — raw counters (verified on 8.0.4)
printjson(db.serverStatus().connections);
// Output (values vary):
// { current: 8, available: 838852, totalCreated: 84, rejected: 0, active: 4, threaded: 8, ... }
printjson(Object.keys(db.serverStatus().opcounters));
// Output: [ 'insert', 'query', 'update', 'delete', 'getmore', 'command' ]
db.getSiblingDB("shop").orders.stats().size   // Output: 116  (bytes for 3 tiny docs)
db.hello().maxBsonObjectSize                  // Output: 16777216  (16 MB document limit)
```

## 💻 Code Example — Advanced

```javascript
// profiler.js — find slow queries (mongosh)
db = db.getSiblingDB("shop");
db.setProfilingLevel(1, { slowms: 100 });      // level 1: log only ops slower than 100 ms
// ... application runs ...
db.system.profile
  .find({ millis: { $gt: 100 } })               // slow ops recorded by the profiler
  .sort({ ts: -1 }).limit(5)                    // newest first
  .forEach(p => print(p.ns, p.op, p.millis + 'ms', p.planSummary)); // planSummary COLLSCAN = missing index!
db.setProfilingLevel(0);                        // turn it off when done (profiler has a cost)

// What is running right now for > 5 s?
db.getSiblingDB("admin").aggregate([
  { $currentOp: { allUsers: true } },
  { $match: { active: true, secs_running: { $gt: 5 } } },
  { $project: { opid: 1, ns: 1, op: 1, secs_running: 1 } }
]);
// db.killOp(<opid>) to stop a runaway query.

// Replication lag (replica sets only)
rs.printSecondaryReplicationInfo();             // shows "X secs behind the primary" per secondary
```

```javascript
// metrics-endpoint.js — expose a tiny health endpoint from Node using serverStatus
const { MongoClient } = require('mongodb');
async function health(client) {
  const s = await client.db('admin').command({ serverStatus: 1 });
  return {
    connections: s.connections.current,                       // current open connections
    available: s.connections.available,                       // headroom before the limit
    opsInsert: s.opcounters.insert,                           // cumulative since start (graph the rate)
    cacheUsedGB: s.wiredTiger.cache['bytes currently in the cache'] / 1e9,
  };
}
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// /healthz + Prometheus-style metrics from an Express app using Mongoose
const express = require('express');
const mongoose = require('mongoose');
const app = express();

app.get('/healthz', async (req, res) => {
  try {
    await mongoose.connection.db.admin().ping();       // cheap liveness check against MongoDB
    res.json({ db: 'up', readyState: mongoose.connection.readyState }); // 1 = connected
  } catch { res.status(503).json({ db: 'down' }); }
});

app.get('/metrics', async (req, res) => {
  const s = await mongoose.connection.db.admin().serverStatus();
  res.type('text/plain').send(
    `mongo_connections_current ${s.connections.current}\nmongo_opcounters_insert ${s.opcounters.insert}\n`
  );
});
// In production prefer percona/mongodb_exporter + Prometheus + Grafana alerts.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Leaving the profiler at level 2 (logs everything) in production.
```javascript
// Wrong: db.setProfilingLevel(2)   -> every operation written to system.profile, big overhead
// Right: db.setProfilingLevel(1, { slowms: 100 })  or rely on the slow-query log
```
❌ Mistake 2: Monitoring only CPU. ✅ Also watch cache dirty %, replication lag, connections, queue depth (`qrw/arw`), disk free, and slow queries.

❌ Mistake 3: Reading `opcounters` as a rate — they are cumulative since startup. Graph the **delta**.

❌ Mistake 4: No alert on disk space/oplog window. A full disk crashes mongod; a small oplog window breaks resyncs.

---

## 🧠 Tricky Interview Question
**Q:** `mongostat` shows `*0` under insert while the primary is idle but secondaries are applying writes. What does the asterisk mean, and why is it important?

**Answer:** An asterisk (`*`) before a number means that operation was **applied via replication** (executed from the oplog), not issued directly by a client. On a secondary you will see `*N` for inserts/updates, even though no client wrote there. It helps distinguish client load from replication apply load, and a secondary whose `*` counts lag far behind the primary's counts is falling behind (check `rs.printSecondaryReplicationInfo()`).

---

## ⚫ Interview Questions + Answers

Q1: Which `mongostat` columns would you look at first?
A1: `qrw`/`arw` (queued/active readers-writers: queueing means contention), `dirty`/`used` (WiredTiger cache pressure), `conn`, `res` memory, and the op counters for traffic shape.

Q2: How do you find slow queries?
A2: Profiler level 1 with `slowms`, the slow-query lines in the log, Atlas Performance Advisor/Query Profiler; then `explain('executionStats')` to compare `totalDocsExamined` vs `nReturned` and look for COLLSCAN.

Q3: What is replication lag and how do you measure it?
A3: Time a secondary's last applied oplog entry is behind the primary. `rs.printSecondaryReplicationInfo()` or `rs.status()` (`optimeDate` differences). Causes: slow disk, heavy writes, network, long-running ops.

Q4: What is the WiredTiger cache and why watch it?
A4: Internal cache (default 50% of (RAM-1GB)). If dirty bytes approach the limit, writes stall and eviction threads burn CPU; working set not fitting RAM leads to disk reads and latency spikes.

Q5: Which Atlas metrics matter most?
A5: Operation execution time, connections, replication lag, normalized CPU/memory, disk IOPS and free space, cache usage, and Query Targeting (scanned/returned ratio).

---

## 🔷 When to Use + When Not to Use
✅ Use mongostat/mongotop when:
- Quick live look at a self-hosted server during an incident

✅ Use Atlas/Prometheus+Grafana when:
- Always-on dashboards, history, alerting, capacity planning

❌ Avoid:
- Permanent full profiling, or treating a single snapshot as the trend

---

## 📊 Visual Diagram
```
MONITORING STACK
──────────────────────────────────────────────────────
 mongod ─┬─ serverStatus counters ──▶ mongostat (live)
         ├─ per-collection time ────▶ mongotop
         ├─ profiler / slow log ────▶ system.profile ─▶ explain() ─▶ add index
         └─ rs.status() ────────────▶ replication lag
              │
              ▼  exporter (mongodb_exporter) / Atlas agent
        Prometheus / Atlas ──▶ Grafana dashboards ──▶ Alerts (PagerDuty/Slack)
 Golden signals: ops/sec · latency · connections · cache · lag · disk
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| mongostat | Live per-second counters | Live counters tool |
| mongotop | Time per collection | Collection-wise समय |
| serverStatus | Internal metrics command | Internal metrics command |
| Profiler | Records slow ops | Slow ops record करता है |
| Replication lag | Secondary delay | Secondary की देरी |
| WiredTiger cache | In-memory data cache | Memory में data cache |
| Alert | Notification on threshold | Threshold पर सूचना |

---

## ⚡ 3-Line Summary
English:
1. Watch ops/sec, connections, latency, cache, replication lag and disk using `mongostat`, `serverStatus`, the profiler and Atlas/Prometheus.
2. Find slow queries with profiler level 1 and `explain`, then fix indexes.
3. Alert on thresholds; remember counters are cumulative and `*` in mongostat means replicated ops.

Hindi:
1. `mongostat`, `serverStatus`, profiler और Atlas/Prometheus से ops/sec, connections, latency, cache, replication lag और disk देखो।
2. Profiler level 1 और `explain` से slow queries खोजो, फिर index सुधारो।
3. Thresholds पर alert लगाओ; याद रखो counters cumulative हैं और mongostat में `*` का मतलब replicated ops है।

---

## ➡️ Next Topic
**111. Connection Pooling and Limits** — How the driver reuses connections and how to avoid exhausting them.
