# 46. Write-Through Pattern
# हिंदी में: Write-Through — हर write एक साथ cache और database दोनों में होता है, ताकि cache हमेशा ताज़ा रहे

---

## 🔵 Simple Definition (English)
In **write-through caching**, every write goes **through the cache to the database synchronously**: the data is written to the **cache and the DB in the same operation**, and the write is acknowledged only after **both** succeed. Reads always find fresh data in the cache.
Often paired with **read-through** (the cache layer loads from the DB on a miss).

## 🔵 सरल परिभाषा (Hindi)
Write-through में हर बार लिखते समय डेटा cache और DB दोनों में एक साथ जाता है, और दोनों में सफल होने पर ही "OK" मिलता है।
इसलिए पढ़ते समय cache में हमेशा ताज़ा डेटा मिलता है।

---

## 🔴 Problem it Solves
Cache-aside has two weaknesses:
1. **Cold misses** right after a write: the first read after every update goes to the DB.
2. **Stale data windows/races** between the DB update and the cache invalidation.

Write-through keeps the cache **always in sync** with the latest writes:
- Reads right after writes are **fast and fresh** (great for read-after-write).
- No invalidation logic scattered around.
- Useful when data is **written once and read very often soon after** (user profile/session after login, a newly created post, config).

## 🔴 यह क्यों बना? (Hindi)
Cache-aside में हर update के बाद पहली read DB पर जाती है, और DB-update और cache-delete के बीच पुराना डेटा दिख सकता है।
Write-through में cache हमेशा DB के साथ ताज़ा रहता है — लिखने के तुरंत बाद पढ़ो तो तेज़ और सही डेटा।

---

## 🟢 How it Works — Step by Step

```
           WRITE
 App ───────────────► Cache layer ──────────────► Database
  ▲                    1. write cache              2. write DB (sync)
  │                                                   │
  └───────────── 3. ACK only after BOTH succeed ◄─────┘

           READ
 App ──► Cache ── HIT (almost always, data is fresh) ──► return
                └─ MISS (evicted / never written) → load from DB (read-through), fill cache
```

### Implementation styles

```
1. Library/provider-managed:  the cache product writes to the DB for you
   (e.g. Hazelcast/Ignite MapStore, NCache, DAX for DynamoDB — DAX is write-through)

2. App-managed (most common with Redis):
   BEGIN DB txn → write DB → COMMIT → write cache (SET key value)
   → effectively "write DB then update cache" in one code path
```

### Order and failure handling (app-managed)

```
Recommended:  write DB (commit) → then SET cache
   - DB fails → nothing written, return error ✅
   - Cache SET fails → DB has the truth; delete key / retry / rely on TTL; log it
     (don't roll back the user's successful write)

❌ Cache first then DB:
   cache shows data that never reached DB if DB write fails → "phantom" data
```

### Concurrency caution

```
Two concurrent writers to the same key:
  W1: DB=100 ... (slow) ... SET cache=100
  W2: DB=200 → SET cache=200
  Final: cache=100 (W1's late SET), DB=200 ❌

Fixes:
  - Use version numbers: SET only if newer (Lua compare-and-set on version)
  - Serialize writes per key (row lock / single writer per entity)
  - Short TTL as a safety net
  - Or prefer delete-on-write (cache-aside) when concurrent writes are common
```

### Write-through vs cache-aside vs write-back

```
┌──────────────────┬──────────────────────┬────────────────────────┬────────────────────────┐
│                  │ Cache-aside          │ Write-through          │ Write-back             │
├──────────────────┼──────────────────────┼────────────────────────┼────────────────────────┤
│ Write goes to    │ DB, then DEL cache   │ Cache + DB (sync)      │ Cache now, DB later    │
│ Write latency    │ DB only              │ DB + cache (higher)    │ Cache only (lowest)    │
│ Read after write │ Miss → DB            │ Hit, fresh ✅           │ Hit, fresh             │
│ Consistency      │ Stale window possible│ Strong-ish (in sync)   │ DB lags; risk of loss  │
│ Data loss risk   │ None                 │ None                   │ Yes if cache dies      │
│ Cache pollution  │ Only read data       │ ALL written data cached│ All written data       │
│ Best for         │ Read-heavy, general  │ Read-soon-after-write  │ Write-heavy counters,  │
│                  │                      │ data, sessions, config │ metrics, analytics     │
└──────────────────┴──────────────────────┴────────────────────────┴────────────────────────┘
```

### Cache pollution
```
Write-through caches EVERYTHING written, even data never read again (e.g. old log entries).
→ Use TTLs, and only write-through for entities likely to be read soon (profiles, settings, hot items).
→ Combine: write-through for hot entities + cache-aside for everything else.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Write पर पहले DB में commit करो, फिर वही नया डेटा cache में SET करो — दोनों सफल तो "OK"।
2. पढ़ते समय cache में लगभग हमेशा ताज़ा डेटा मिलता है (HIT)।
3. DB फ़ेल → कुछ नहीं लिखा, error। Cache फ़ेल → DB सही है, key delete/retry करो, यूज़र का write मत बिगाड़ो।
4. दो writers एक साथ हों तो पुराना SET बाद में पहुँच सकता है — version check या TTL से बचाओ।
5. नुक़सान: write धीमा (दो जगह लिखना) और कभी न पढ़ा जाने वाला डेटा भी cache में (pollution) — TTL लगाओ।

---

## 🟡 Real World Example

**Amazon DynamoDB Accelerator (DAX)** — a managed write-through cache in front of DynamoDB. Writes go through DAX to DynamoDB, and reads get microsecond latency with fresh data for items written through it.

**Session stores** — on login, the session or user context is written to the DB/token store **and** Redis at the same time, because the very next request (milliseconds later) needs it. A cache-aside miss would add latency to every first request.

**Gaming profiles / player state** — player inventory and profile updates are written through to the cache so the next screen load (immediately after a purchase) shows the new item instantly.

**Feature flags / config services** — admin updates are written to the DB and pushed to the cache immediately, so all servers read the new config without waiting for TTLs.

## 🟡 Real Example Hindi में
Amazon का DAX, DynamoDB के आगे write-through cache है — लिखा हुआ डेटा तुरंत microseconds में पढ़ा जा सकता है।
Login पर session DB और Redis दोनों में एक साथ लिखा जाता है, क्योंकि अगली request तुरंत उसे माँगेगी। गेम में सामान ख़रीदते ही inventory cache में अपडेट होती है।

---

## 🟠 My Stack Example

### Node.js — write-through for user profile
```js
async function updateProfile(userId, patch) {
  // 1. write DB (source of truth) — returns the full new row incl. version
  const { rows: [u] } = await pool.query(
    `UPDATE users SET name = COALESCE($2, name), avatar = COALESCE($3, avatar), version = version + 1
     WHERE id = $1 RETURNING id, name, avatar, version`,
    [userId, patch.name, patch.avatar]);

  // 2. write cache — only if this version is newer (Lua compare-and-set)
  await redis.eval(
    `local cur = redis.call('HGET', KEYS[1], 'version')
     if (not cur) or tonumber(ARGV[1]) > tonumber(cur) then
       redis.call('HSET', KEYS[1], 'json', ARGV[2], 'version', ARGV[1])
       redis.call('EXPIRE', KEYS[1], ARGV[3])
     end
     return 1`,
    { keys: [`user:${userId}`], arguments: [String(u.version), JSON.stringify(u), '3600'] }
  ).catch((e) => { logger.warn({ e }, 'write-through cache failed'); return redis.del(`user:${userId}`).catch(() => {}); });

  return u;
}

async function getProfile(userId) {               // read path = read-through on miss
  const json = await redis.hGet(`user:${userId}`, 'json').catch(() => null);
  if (json) return JSON.parse(json);
  const { rows: [u] } = await pool.query('SELECT id, name, avatar, version FROM users WHERE id=$1', [userId]);
  if (u) await redis.hSet(`user:${userId}`, { json: JSON.stringify(u), version: String(u.version) }).catch(() => {});
  return u;
}
```

### FastAPI — session write-through at login
```python
@app.post("/auth/login")
async def login(body: LoginIn):
    user = await authenticate(body)
    sid = secrets.token_urlsafe(32)
    session = {"user_id": user.id, "role": user.role, "created_at": time.time()}
    await db.execute(insert(Sessions).values(id=sid, **session))         # durable
    await r.set(f"sess:{sid}", json.dumps(session), ex=7 * 86400)        # cache, immediately readable
    resp = JSONResponse({"ok": True})
    resp.set_cookie("sid", sid, httponly=True, secure=True, samesite="lax")
    return resp
```

### Config/feature flags: write-through + broadcast
```js
async function setFlag(name, value) {
  await pool.query('INSERT INTO flags(name, value) VALUES ($1,$2) ON CONFLICT (name) DO UPDATE SET value=$2', [name, value]);
  await redis.hSet('flags', name, JSON.stringify(value));
  await redis.publish('flags:changed', name);          // servers refresh in-process L1 cache
}
```

### Client-side analogue (React Query)
```ts
// "write-through" to the client cache: put the server's response directly into the cache
const m = useMutation({
  mutationFn: updateProfile,
  onSuccess: (user) => queryClient.setQueryData(['me'], user),   // no refetch needed
});
```

---

## ⚫ Interview Questions + Answers

**Q1: What is write-through caching?**
A1: A strategy where every write updates both the cache and the database synchronously, and success is returned only when both are done. The cache always holds the latest written data, so reads (especially right after writes) are fast and fresh. It's often combined with read-through loading for misses.

**Q2: Write-through vs cache-aside — when would you choose write-through?**
A2: When data is read soon and often after being written and stale or missed reads are costly: sessions, user profiles and settings, configuration, game state, recently created content. Cache-aside is better for general read-heavy data, where caching only what's read avoids polluting memory and writes stay cheaper. Many systems combine them: write-through for hot entities, cache-aside for the rest.

**Q3: What are the downsides of write-through?**
A3: Higher write latency, because every write hits two systems. Cache pollution, because data that's never read still takes memory, so use TTLs. Complexity in keeping the cache and DB in sync on partial failures and with concurrent writers (out-of-order sets). And if the cache is down, you must decide whether writes fail or degrade, usually degrading by writing the DB and invalidating.

**Q4: What should happen if the DB write succeeds but the cache write fails?**
A4: The DB is the source of truth, so the user's write is successful and shouldn't fail. Remove the possibly stale key (delete), or retry the set asynchronously, log or alert, and rely on TTL as the final safety net. Never write the cache first and then the DB, because if the DB fails you'd serve data that doesn't exist.

**Q5: How do you avoid stale data from concurrent write-through updates?**
A5: Include a monotonically increasing version (or updated_at) with each write, and make the cache update conditional, only if newer (an atomic compare-and-set via a Lua script). Or serialize writes per entity (row locks or a single writer per key), or fall back to delete-on-write. Short TTLs bound any inconsistency.

---

## 🔷 Trade-offs
✅ Advantages:
- Cache always fresh for written data; read-after-write is fast.
- Simpler read path; fewer misses; no invalidation scattered across code.

❌ Disadvantages:
- Slower writes (two systems); more failure modes.
- Cache pollution with rarely-read data.
- Concurrency ordering issues need versioning.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Write-through | Write cache + DB synchronously | cache और DB दोनों में एक साथ लिखना |
| Read-through | Cache loads DB on miss | miss पर cache ख़ुद DB से लाए |
| Synchronous | Wait for completion | पूरा होने का इंतज़ार |
| Cache pollution | Cache filled with unused data | बेकार डेटा से भरा cache |
| Compare-and-set | Update only if condition holds | शर्त पूरी हो तभी बदलो |
| Versioning | Monotonic counter per entity | हर बदलाव पर बढ़ता नंबर |
| DAX | DynamoDB write-through cache | DynamoDB का cache |

---

## ⚡ 3-Line Summary
**English:**
1. Write-through writes to DB and cache together; reads are fresh and fast, especially right after writes.
2. Do DB first, then cache; if cache fails, delete/retry — never fail the user's committed write.
3. Costs: slower writes, cache pollution, concurrency ordering — use TTLs and version checks.

**Hindi:**
1. Write-through = DB और cache दोनों में एक साथ लिखना; लिखने के बाद पढ़ना तेज़ और ताज़ा।
2. पहले DB, फिर cache; cache फ़ेल हो तो delete/retry, यूज़र का write फ़ेल मत करो।
3. क़ीमत: धीमे writes, बेकार डेटा cache में, और एक साथ writes में क्रम की दिक़्क़त — TTL और version रखो।

---

## ➡️ Next Topic Suggestion
**47. Write-Back Pattern** — What if writes are so frequent that even the DB can't keep up? Next: write-back (write-behind), where the cache absorbs writes and flushes them to the DB later, plus its data-loss risks.
