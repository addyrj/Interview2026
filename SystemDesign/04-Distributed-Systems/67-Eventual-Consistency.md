# 67. Eventual Consistency
# हिंदी में: Eventual Consistency — सारी copies तुरंत एक जैसी नहीं होतीं, पर नए बदलाव रुकने पर कुछ समय बाद सब एक जैसी हो जाती हैं

---

## 🔵 Simple Definition (English)
**Eventual consistency** guarantees that **if no new updates are made**, all replicas will **eventually converge** to the same value. Right after a write, different replicas (or caches, regions, services) may return **different, stale values** for a short time (milliseconds to seconds, sometimes longer).
It trades **immediate consistency** for **availability, low latency and scalability**.

## 🔵 सरल परिभाषा (Hindi)
Eventual consistency में write के तुरंत बाद अलग-अलग copies अलग डेटा दिखा सकती हैं, पर थोड़ी देर में सब एक जैसी हो जाती हैं।
इससे सिस्टम तेज़, हमेशा उपलब्ध और बड़े स्केल वाला बनता है — बदले में कुछ सेकंड पुराना डेटा दिख सकता है।

---

## 🔴 Problem it Solves
Strong consistency is **expensive** at global scale:
- Every write waits for cross-region coordination (100–300 ms+).
- During network partitions, parts of the system must **refuse** requests.
- Single leaders become **throughput bottlenecks**.

Most data **doesn't need** instant global agreement: like counts, follower counts, product views, feed contents, search indexes, analytics, delivery-partner location history, cache entries, DNS records.
Eventual consistency lets each replica **accept reads and writes locally**, replicate **asynchronously**, and **resolve conflicts** later, giving massive scale and always-on availability.

## 🔴 यह क्यों बना? (Hindi)
दुनिया भर में strong consistency महँगी है — हर write पर regions के बीच इंतज़ार, partition में requests मना, और एक leader पर बोझ।
ज़्यादातर डेटा (likes, followers, feed, search index, analytics) को तुरंत सब जगह एक जैसा होने की ज़रूरत नहीं — eventual consistency से हर जगह तेज़ी से पढ़ना-लिखना और बाद में मिलाना संभव होता है।

---

## 🟢 How it Works — Step by Step

### Async replication & convergence

```
t=0   User in Mumbai likes post → Mumbai replica: likes=101
t=0   User in London reads    → London replica: likes=100   (stale)
t=0.3s replication arrives     → London replica: likes=101   ✅ converged
"Inconsistency window" = time until all replicas agree (usually ms–seconds)
```

### Where you meet eventual consistency (even without NoSQL)

```
- Read replicas lagging the primary (Topic 40)
- Caches (Redis/CDN) until TTL or invalidation (Topic 48)
- Search index updated via CDC (Elasticsearch)
- Microservices syncing via events (order service → analytics, notifications)
- Multi-region databases (DynamoDB Global Tables, Cassandra multi-DC)
- DNS propagation (Topic 2)
- Mobile offline apps syncing later
```

### Conflicts — what if two replicas accept different writes?

```
Mumbai:    user sets name = "Aditya R"   at t=10.000
Singapore: user sets name = "Adi"        at t=10.002   (partition, both accepted)

Resolution strategies:
1. Last-Write-Wins (LWW): highest timestamp wins → "Adi"
   ✅ simple   ❌ silently loses a write; clock skew can pick the "wrong" one
2. Version vectors / vector clocks: detect concurrent writes (Topic 91) → keep BOTH (siblings)
   → app/user merges (Amazon cart: union of items)
3. CRDTs (Conflict-free Replicated Data Types): data types that merge automatically and
   deterministically: counters (G-Counter/PN-Counter), sets (OR-Set), text (Figma/Google Docs-like)
4. Application-level merge rules: "max(stock reservations)", "union of tags", "sum of deltas"
5. Avoid conflicts: route all writes for an entity to one "home" region (single-writer per key)
```

### Anti-entropy mechanisms (how replicas converge)
```
Read repair      → on read, compare replicas; fix stale ones
Hinted handoff   → if replica down, another node stores the write ("hint") and replays later
Merkle trees     → background comparison of data ranges to find & sync differences (Cassandra repair)
Gossip           → nodes share state peer-to-peer
```

### Session guarantees — making EC feel consistent to users

```
Read-your-writes   → user sees their own update immediately (route to primary/home region, or
                     update client cache optimistically)
Monotonic reads    → user never sees data go "back in time" (stick to one replica / version check)
Monotonic writes   → a user's writes applied in order
Consistent prefix  → you never see an answer before its question (causal order) → Topic 91
```

### Designing UX for eventual consistency
```
✓ Optimistic UI: show the user's change instantly (like ❤️ turns red), reconcile in background
✓ "Processing…" / "Updating…" states for derived data (search results may lag)
✓ Approximate numbers: "1.2K likes"
✓ Never use EC for: balance checks before debit, stock decrement of last items, uniqueness claims
```

## 🟢 कैसे काम करता है? (Hindi)
1. Write पास वाली replica पर तुरंत हो जाता है; बाक़ी replicas तक asynchronously (बाद में) पहुँचता है।
2. उस बीच दूसरी replica से पढ़ने वाले को पुराना डेटा दिख सकता है (inconsistency window)।
3. दो जगह एक साथ अलग writes हो जाएँ तो conflict: Last-Write-Wins, vector clocks, CRDTs या ऐप के merge नियम से सुलझाओ।
4. Read repair, hinted handoff, Merkle trees, gossip से replicas आख़िर में एक जैसी हो जाती हैं।
5. यूज़र को अपना बदलाव तुरंत दिखाओ (read-your-writes, optimistic UI); पैसे और आख़िरी stock के लिए EC कभी नहीं।

---

## 🟡 Real World Example

**Amazon DynamoDB / Dynamo** — eventually consistent reads by default (cheaper, faster). Strongly consistent reads are optional. Global Tables replicate across regions asynchronously with last-writer-wins.

**Facebook/Instagram** — after you post, friends in other regions may see it a second or so later. Your own view uses read-your-writes, so you see the post immediately.

**YouTube view counts, Twitter follower counts** — displayed numbers lag and jump. That's eventual convergence of aggregated counters.

**DNS** — the classic global eventually consistent system: record changes propagate according to TTLs over minutes to hours.

**Figma / Google Docs / Apple Notes** — use CRDT- or OT-style merging so concurrent edits from many users or devices converge without losing changes.

## 🟡 Real Example Hindi में
DynamoDB default में eventually consistent reads देता है; Instagram पर आपका post दूसरे region के दोस्तों को एक-दो सेकंड बाद दिखता है, पर आपको तुरंत (read-your-writes)।
YouTube के views और Twitter के followers झटकों में बढ़ते हैं। DNS भी eventual consistency का सबसे पुराना उदाहरण है। Google Docs/Figma में कई लोगों के बदलाव अपने आप मिल जाते हैं।

---

## 🟠 My Stack Example

### Event-driven sync between services (eventually consistent by design)
```js
// Order service (source of truth) commits + outbox event
await withTx(async (tx) => {
  await tx.query('UPDATE orders SET status=$1 WHERE id=$2', ['DELIVERED', id]);
  await tx.query("INSERT INTO outbox(topic, payload) VALUES ('order.delivered', $1)", [{ id, userId }]);
});
// Analytics, loyalty-points, search-index services consume the event seconds later.
// Their views are eventually consistent with the order DB.
```

### Read-your-writes on top of replicas/caches
```js
app.post('/api/v1/posts', authenticate, async (req, res) => {
  const post = await writer.query('INSERT INTO posts(...) VALUES (...) RETURNING *', [...]).then(r => r.rows[0]);
  await redis.set(`rw:${req.user.id}`, '1', { EX: 5 });    // next 5s: this user's reads → primary
  res.status(201).json(post);                              // client inserts it into its feed cache
});
```

### Conflict-free counter (CRDT-style) per region with Redis
```js
// Each region increments its OWN counter; total = sum → no lost increments, no conflicts (G-Counter)
await redis.hIncrBy(`likes:${postId}`, REGION, 1);         // likes:7 = { mumbai: 120, sgp: 45 }
const parts = await redis.hVals(`likes:${postId}`);
const total = parts.reduce((s, v) => s + Number(v), 0);
```

### Last-write-wins with version check (mobile sync)
```sql
-- client sends updated_at it last saw; server applies only if newer (else return conflict)
UPDATE notes SET body = $1, updated_at = $2
WHERE id = $3 AND updated_at < $2
RETURNING *;
```

### React Native: optimistic UI (embrace EC)
```ts
const like = useMutation({
  mutationFn: (id: string) => api.post(`/posts/${id}/like`),
  onMutate: async (id) => {
    await qc.cancelQueries({ queryKey: ['post', id] });
    const prev = qc.getQueryData<Post>(['post', id]);
    qc.setQueryData(['post', id], { ...prev!, liked: true, likeCount: prev!.likeCount + 1 });
    return { prev };
  },
  onError: (_e, id, ctx) => qc.setQueryData(['post', id], ctx!.prev),     // rollback
  onSettled: (_d, _e, id) => qc.invalidateQueries({ queryKey: ['post', id] }),  // converge with server
});
```

### DynamoDB Global Tables (multi-region AP)
```
Table in ap-south-1 + eu-west-1 → writes in either region, async replication (~1s), LWW conflicts.
Pattern: "home region" per user for writes to avoid conflicts; reads local.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is eventual consistency?**
A1: A consistency model where replicas may temporarily disagree after updates, but if writes stop, all replicas converge to the same value. Reads can return stale data during the inconsistency window. It enables local reads and writes, asynchronous replication, high availability during partitions and low latency at global scale.

**Q2: How are conflicts resolved in eventually consistent systems?**
A2: Last-write-wins by timestamp (simple, but can silently drop writes and is sensitive to clock skew); detecting concurrency with version vectors and keeping siblings for application or user merge (Amazon's cart union); CRDTs that merge deterministically (G-Counters, PN-Counters, OR-Sets, sequence CRDTs for text); domain-specific merge rules; or avoiding conflicts with single-writer-per-key (a home region or owner).

**Q3: How do you give users a consistent experience on an eventually consistent backend?**
A3: Provide session guarantees. Read-your-writes: route the user's reads to the primary or home region after a write, or update the client cache from the write response or optimistically. Monotonic reads: stick a session to one replica or track versions. Show pending or optimistic states, use approximate counts, and keep critical decisions (payment, final stock) on strongly consistent paths.

**Q4: Give examples where eventual consistency is acceptable and where it's not.**
A4: Acceptable: social feeds, like and view counts, follower lists, product catalogs and reviews, search indexes, recommendations, analytics dashboards, notifications, DNS, CDN caches, shopping carts (with merge). Not acceptable: account balances at debit time, payment authorization state, inventory for limited stock, booking unique seats or slots, unique username claims, permission revocation and security-sensitive settings, and leader election.

**Q5: What mechanisms help replicas converge in systems like Cassandra?**
A5: Hinted handoff (a coordinator stores writes for a down replica and replays them later), read repair (detect and fix divergent replicas during reads), anti-entropy repair using Merkle trees to compare and sync data ranges in the background, gossip for membership and state dissemination, and tombstones with grace periods to propagate deletes correctly.

---

## 🔷 Trade-offs
✅ Advantages:
- High availability (even during partitions), low latency, horizontal/global scale, simpler writes.

❌ Disadvantages:
- Stale reads; conflict resolution complexity; harder debugging and testing.
- Developers must reason about anomalies; wrong use for critical data causes real losses.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Eventual consistency | Replicas converge over time | समय के साथ copies एक जैसी |
| Inconsistency window | Time replicas disagree | copies के अलग रहने का समय |
| Stale read | Reading outdated value | पुराना डेटा पढ़ना |
| Last-Write-Wins | Latest timestamp wins | आख़िरी write जीतता है |
| CRDT | Auto-merging data type | अपने आप मिलने वाला डेटा ढाँचा |
| Read repair | Fix stale replica on read | पढ़ते समय सुधार |
| Hinted handoff | Store writes for down node | बंद node के लिए write रखना |
| Read-your-writes | See your own updates | अपना बदलाव तुरंत दिखे |
| Optimistic UI | Show change before confirm | पुष्टि से पहले बदलाव दिखाना |

---

## ⚡ 3-Line Summary
**English:**
1. Eventual consistency: replicas may differ briefly but converge when updates stop — gains availability, latency, scale.
2. Resolve conflicts with LWW, version vectors + merge, CRDTs, or single-writer-per-key; converge via read repair, hinted handoff, Merkle repair.
3. Add session guarantees (read-your-writes, monotonic reads) and optimistic UI; never use for money or scarce inventory.

**Hindi:**
1. Eventual consistency: copies कुछ देर अलग, फिर एक जैसी — उपलब्धता, तेज़ी और स्केल मिलते हैं।
2. Conflicts: LWW, vector clocks, CRDTs या एक writer प्रति key; read repair और Merkle repair से मिलान।
3. Read-your-writes और optimistic UI दो; पैसे और कम stock के लिए कभी नहीं।

---

## ➡️ Next Topic Suggestion
**68. Distributed Transactions** — What if one business operation must update data in several services or databases consistently? Next: the problem of distributed transactions and the approaches (2PC, Saga, outbox) at a high level.
