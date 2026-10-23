# 117. Twitter / News Feed System
# हिंदी में: Twitter Feed System — tweets लिखना, जिन्हें follow करते हो उनकी tweets की home timeline, trending topics और search — करोड़ों users के लिए तेज़ी से

---

## 🔵 Simple Definition (English)
Design a microblogging platform like **Twitter/X**: users **post short tweets** (text + optional media), **follow** others, read a **home timeline** (tweets from followees, chronological or ranked), a **user timeline** (one user's tweets), **like/retweet/reply**, **search** tweets, and see **trending topics**. The defining challenges are the **read-heavy timeline at massive scale**, the **celebrity fan-out problem**, **real-time freshness**, and **search/trends over a firehose** of tweets.

## 🔵 सरल परिभाषा (Hindi)
Twitter जैसा सिस्टम: छोटे tweets लिखना, follow करना, home timeline (जिन्हें follow करते हो उनकी tweets), किसी एक की timeline, like/retweet/reply, search और trending topics।
मुख्य चुनौती: करोड़ों लोग timeline पढ़ते हैं, celebrities के करोड़ों followers हैं, और हर सेकंड हज़ारों tweets की धारा पर search/trends।

---

## 🔴 Problem it Solves
- **Timeline reads ≫ writes** (~300k timeline reads/s vs ~6k tweets/s at Twitter scale): computing timelines on demand with joins is too slow.
- **Celebrities** (100M+ followers): pushing each tweet to every follower's timeline creates massive write bursts and delays.
- **Real-time events** (World Cup, elections) cause sudden 10× spikes; Twitter's "fail whale" era came from this.
- **Search and trends** must index every tweet within seconds and detect spikes in topics.

## 🔴 यह क्यों बना? (Hindi)
Timeline पढ़ना लिखने से 50 गुना ज़्यादा — हर बार joins से बनाना धीमा; 10 करोड़ followers वाले celebrity की हर tweet सबकी timeline में डालना भारी; World Cup जैसे events पर अचानक 10 गुना ट्रैफ़िक; और हर tweet सेकंडों में search और trends में आनी चाहिए।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional: post tweet (280 chars, media), follow, home timeline, user timeline, like/retweet/reply,
            search, trending topics, notifications (mentions)
Non-functional: timeline p99 < 200 ms, tweet visible to followers within ~5 s, highly available
               (eventual consistency OK), handle event spikes
```

### 2. Estimation

```
DAU 250M; tweets 500M/day ≈ 6k/s (peak 20k+/s)
Timeline reads: 250M × 30 = 7.5B/day ≈ 90k/s (peak ~300k/s)
Avg followers ~200 → fan-out writes: 6k × 200 = 1.2M timeline inserts/s (!!) → why fan-out is costly
Tweet storage: 500M × 300 B ≈ 150 GB/day (+ media in object storage)
Timeline cache: 250M users × 800 tweet ids × 8 B ≈ 1.6 TB in RAM (Redis cluster) — feasible
```

### 3. APIs

```
POST /tweets { text, mediaIds[], replyTo? }         GET /timeline/home?cursor=
GET  /users/{id}/tweets?cursor=                       POST /tweets/{id}/like | /retweet
GET  /search?q=&cursor=                               GET /trends?location=IN
```

### 4. Architecture

```
          📱/🌐 clients
               │
        API Gateway / BFF
   ┌───────────┼─────────────┬──────────────┬──────────────┐
   ▼           ▼             ▼              ▼              ▼
 Tweet svc   Timeline svc   Graph svc     Search svc     Trends svc
   │ write      │ read          │ follows      ▲              ▲
   ▼            │               ▼              │              │
 Tweet store    │          Graph store         │              │
 (sharded,      │          (followers/         │              │
  Manhattan/    │           following)         │              │
  MySQL/Cass.)  │                              │              │
   │ "TweetCreated" ──► Kafka ─────────────────┼──────────────┤
   │                     ├─► Fan-out svc ──► Timeline cache (Redis lists per user)
   │                     ├─► Search indexer (Earlybird/Lucene/Elastic, near-real-time)
   │                     ├─► Trends (stream processing: counts per term/window/location)
   │                     └─► Notifications (mentions), analytics
   ▼
 Media → S3 + CDN
```

### 5. Timelines: fan-out strategy (same core idea as Instagram, Twitter popularized it)

```
Home timeline = Redis list of tweet ids per user (latest ~800), built by fan-out on write.
Celebrity tweets: not fanned out; merged at read time from their user timelines.
Read path:
  ids = timeline_cache[user] (precomputed)
      + recent tweets of followed celebrities (pull)
  merge by time (or rank) → hydrate tweets & users from cache (multi-get) → return 20
Inactive users: timeline evicted from cache; rebuilt on login (pull from followees' user timelines)
User timeline: tweets_by_user(user_id, tweet_id DESC) — simple range query by author
```

### 6. Tweet IDs: Snowflake (Twitter invented it)
```
64-bit: 41 bits timestamp (ms) | 10 bits machine id | 12 bits sequence
→ unique without coordination, roughly time-ordered → sort timelines by id = by time
```

### 7. Search (near real-time)
```
Tweet events → indexer builds inverted index segments in memory (seconds) → searchable quickly
Partition index by time (recent tweets in fast RAM indexes; older in archive indexes)
Query fans out to partitions → merge top results by relevance/recency
(Twitter's Earlybird is a Lucene-based real-time engine; Elasticsearch works for smaller scale)
```

### 8. Trending topics
```
Stream processing (Flink/Kafka Streams/Storm/Heron):
  extract hashtags/entities → count in sliding windows (e.g. 5 min, 1 h) per location
  trend score = current rate vs historical baseline (spike detection), not raw count
  (#GoodMorning is always big → not trending; #INDvPAK spikes → trending)
  approximate counting: Count-Min Sketch + heavy hitters (top-K) to save memory
  filter spam/bots, apply policies → publish top N per region every minute → cache → /trends
```

### 9. Other deep dives
```
Likes/retweet counts: async counters (Topic 47); "did I like" via set membership/cache
Spikes: pre-scale for known events; queue fan-out (timelines eventually consistent);
        degrade (delay fan-out for less active users; prioritize active)
Hot tweets: cache hydrated tweet objects (memcache), CDN for media
Consistency: eventual; author sees own tweet immediately (read-your-writes)
Real-time updates: "N new tweets" banner via long-poll/SSE/WebSocket rather than pushing full tweets
```

## 🟢 कैसे काम करता है? (Hindi)
1. Tweet लिखा → Snowflake ID → Tweet store में सेव → "TweetCreated" Kafka में।
2. Fan-out service सामान्य users की tweet followers की home timeline (Redis list) में डालती है; celebrities की tweets पढ़ते समय जोड़ी जाती हैं।
3. Timeline पढ़ना: Redis से ids + followed celebrities की ताज़ा tweets → मिलाओ → cache से पूरी tweets → 20 लौटाओ।
4. Search: indexer हर tweet को सेकंडों में in-memory index में डालता है; trends: stream processing में hashtags की गिनती, सामान्य से अचानक बढ़ोतरी = trending।
5. Likes की गिनती async; events के समय pre-scale; author को अपनी tweet तुरंत दिखे।

---

## 🟡 Real World Example

**Twitter's timeline architecture (public talks, ~2013)** — Redis clusters holding home timelines (about 800 tweet IDs per active user), with a fan-out service delivering roughly 300k timeline writes per second and special handling for high-follower accounts. The Snowflake ID generator originated here.

**The "fail whale" (2008–2010)** — the Rails monolith with MySQL couldn't keep up during events like the World Cup. Twitter moved to JVM services (Scala, Finagle), queues and caching, eventually handling 140k+ tweets/s at peaks.

**Twitter search (Earlybird)** — a real-time Lucene-based index making tweets searchable within ~10 seconds.

**Facebook News Feed & LinkedIn feed** — use pull-heavy, ranking-centric approaches (aggregating candidates at read time with heavy caching and ML ranking), which is a good contrast to Twitter's push model.

## 🟡 Real Example Hindi में
Twitter हर active यूज़र की home timeline (~800 tweet ids) Redis में रखता था और fan-out service प्रति सेकंड लाखों writes करती थी; Snowflake ID भी Twitter ने बनाई।
2008-2010 में World Cup जैसे events पर "fail whale" दिखता था — फिर JVM services, queues, caching से पीक पर 1.4 लाख tweets/सेकंड संभाले। Facebook/LinkedIn feed पढ़ते समय candidates जोड़कर ML से ranking करते हैं।

---

## 🟠 My Stack Example

### Snowflake ID generator (Node, BigInt)
```js
const EPOCH = 1288834974657n;                 // Twitter's epoch (any fixed epoch works)
let seq = 0n, last = -1n;
const MACHINE = BigInt(process.env.MACHINE_ID ?? 1) & 1023n;
export function snowflake() {
  let ts = BigInt(Date.now());
  if (ts === last) { seq = (seq + 1n) & 4095n; if (seq === 0n) while ((ts = BigInt(Date.now())) <= last); }
  else seq = 0n;
  last = ts;
  return ((ts - EPOCH) << 22n) | (MACHINE << 12n) | seq;
}
```

### Post tweet + user timeline write (Cassandra-style table)
```sql
CREATE TABLE tweets (tweet_id bigint PRIMARY KEY, user_id bigint, text text, media list<text>, reply_to bigint, created_at timestamp);
CREATE TABLE user_timeline (user_id bigint, tweet_id bigint, PRIMARY KEY (user_id, tweet_id)) WITH CLUSTERING ORDER BY (tweet_id DESC);
```

### Home timeline read with celebrity merge (Node + Redis)
```js
app.get('/api/v1/timeline/home', authenticate, async (req, res) => {
  const uid = req.user.id;
  const maxId = req.query.cursor ? BigInt(req.query.cursor) : undefined;
  let ids = await redis.lRange(`home:${uid}`, 0, 799);                       // precomputed ids (newest first)
  if (!ids.length) ids = await rebuildTimeline(uid);                          // inactive user → pull & cache
  const celebIds = (await Promise.all((await graph.celebsFollowed(uid))
                      .map((c) => cassandra.recentTweetIds(c, 50)))).flat();
  const merged = [...new Set([...ids, ...celebIds])]
    .map(BigInt).filter((id) => !maxId || id < maxId)
    .sort((a, b) => (b > a ? 1 : -1)).slice(0, 20);                          // ids are time-ordered
  const tweets = await tweetCache.mget(merged);                               // hydrate
  res.json({ items: tweets, nextCursor: merged.at(-1)?.toString() });
});
```

### Trends with Kafka Streams-like logic (Python, simplified sliding counts in Redis)
```python
async def on_tweet(evt):
    for tag in extract_hashtags(evt["text"]):
        bucket = int(time.time() // 60)                                   # 1-minute buckets
        key = f"tag:{evt['country']}:{bucket}"
        await r.zincrby(key, 1, tag); await r.expire(key, 3 * 3600)

async def compute_trends(country="IN"):
    now = int(time.time() // 60)
    recent = await r.zunionstore(f"tmp:recent:{country}", [f"tag:{country}:{b}" for b in range(now - 15, now)])
    baseline = await r.zunionstore(f"tmp:base:{country}", [f"tag:{country}:{b}" for b in range(now - 180, now - 15)])
    # score = recent_rate / (baseline_rate + smoothing) → top 20 → cache as trends:IN
```

### Client: "new tweets" banner instead of auto-inserting
```ts
// poll lightweight endpoint or SSE: GET /timeline/home/new-count?sinceId=...
// show "12 new posts" pill; on tap, fetch and prepend (keeps scroll position stable)
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you design the home timeline for Twitter?**
A1: Precompute timelines with fan-out on write. When a user tweets, a fan-out service inserts the tweet ID into each (active) follower's timeline list in an in-memory store (Redis), capped around 800 entries. High-follower accounts are excluded from fan-out, and their recent tweets are merged at read time. Reading the timeline fetches the IDs, merges in celebrity tweets, sorts (Snowflake IDs are time-ordered) or ranks, and hydrates tweet and user objects from caches. Inactive users' timelines are rebuilt on demand.

**Q2: Explain the celebrity problem and how to solve it.**
A2: A celebrity with 100M followers would need 100M timeline writes per tweet, which creates bursts, delays and wasted work for inactive followers. Solve it with a hybrid approach: no fan-out for accounts above a follower threshold, with their tweets pulled and merged when followers read their timelines (cheap, since there are few celebrities per user). Optionally fan out only to the most active followers, or in deferred batches.

**Q3: How do you generate unique, sortable tweet IDs at scale?**
A3: Snowflake-style 64-bit IDs: a 41-bit millisecond timestamp, a 10-bit worker or machine ID and a 12-bit per-millisecond sequence. They're generated locally on each worker without coordination, are unique (given unique worker IDs), and are roughly time-sortable, so they double as timeline ordering keys and pagination cursors. Watch for clock skew (refuse to go backwards) and worker ID assignment (via config or ZooKeeper).

**Q4: How would you implement trending topics?**
A4: Consume the tweet stream with a stream processor. Extract hashtags and entities, and count occurrences per location in sliding time windows using memory-efficient structures (Count-Min Sketch, heavy-hitter top-K). Score terms by acceleration relative to their historical baseline rather than raw volume, filter spam, bot activity and policy-violating terms, and publish the top N per region every minute to a cache served by the trends API.

**Q5: How does search work for a real-time stream of tweets?**
A5: An ingestion pipeline consumes tweet events and adds them to in-memory inverted index segments within seconds (near real-time), partitioned by time and sharded by tweet ID. Recent partitions stay in fast memory, while older data moves to larger archive indexes. Queries fan out to relevant partitions, each returns top results scored by relevance plus recency plus engagement, and a broker merges them. Deletions and visibility filters are applied at query time.

---

## 🔷 Trade-offs
✅ Push timelines: very fast reads — ❌ write amplification, storage for cached timelines.
✅ Pull for celebs: avoids bursts — ❌ more read-time merging.
✅ Chronological: simple, real-time — ❌ users miss content (ranking improves engagement but adds ML complexity).
✅ Eventual consistency: scale — ❌ followers see tweets with seconds of delay.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Home timeline | Tweets from people you follow | follow किए लोगों की tweets |
| User timeline | One user's tweets | एक यूज़र की tweets |
| Fan-out | Distributing a tweet to followers | followers तक tweet पहुँचाना |
| Celebrity problem | Huge follower counts break fan-out | बहुत ज़्यादा followers की समस्या |
| Snowflake ID | Time-ordered distributed id | समय-क्रम वाली id |
| Hydration | Fetch full tweet objects by id | id से पूरी tweet लाना |
| Trending | Topics spiking above baseline | अचानक बढ़ते विषय |
| Count-Min Sketch | Approximate frequency counting | अनुमानित गिनती |
| Near real-time index | Searchable within seconds | सेकंडों में खोजने लायक |
| Firehose | Full stream of all tweets | सारी tweets की धारा |

---

## ⚡ 3-Line Summary
**English:**
1. Tweets get Snowflake IDs, are stored by id and per-user timeline, and published to Kafka.
2. Home timelines precomputed via fan-out on write in Redis (capped), celebrities pulled at read time and merged; hydrate from caches.
3. Search via near-real-time inverted indexes; trends via stream processing with spike detection; eventual consistency throughout.

**Hindi:**
1. Tweet → Snowflake ID → सेव → Kafka।
2. Home timeline Redis में पहले से (fan-out), celebrities की tweets पढ़ते समय जोड़ो; cache से पूरी tweets।
3. Search सेकंडों वाले index से, trends stream processing और अचानक बढ़ोतरी से; हर जगह eventual consistency।

---

## ➡️ Next Topic Suggestion
**118. E-Commerce Platform** — From social to commerce: design Amazon/Flipkart, with catalog, search, cart, inventory, checkout, orders, payments, flash sales, and how the services fit together.
