# 116. Instagram Design
# हिंदी में: Instagram Design — फ़ोटो/वीडियो upload, followers, home feed, stories, likes-comments और करोड़ों images को CDN से तेज़ दिखाने वाले सिस्टम का backend

---

## 🔵 Simple Definition (English)
Design a photo/video sharing social network like **Instagram**: users **upload photos/videos** (with captions, tags, location), **follow** others, see a **home feed** of posts from people they follow (ranked), view **profiles**, **like/comment**, watch **stories** (24-hour ephemeral) and short videos (**reels**), get **notifications**, and **search/explore**. Core challenges: **media pipeline + storage + CDN**, **feed generation** (fan-out), **social graph**, **counters at scale**, and **read-heavy traffic**.

## 🔵 सरल परिभाषा (Hindi)
Instagram जैसा backend: फ़ोटो/वीडियो upload, follow, home feed (जिन्हें follow करते हो उनकी posts, ranking के साथ), profile, like/comment, 24 घंटे की stories, reels, notifications, explore।
मुख्य चुनौतियाँ: media pipeline + CDN, feed बनाना, followers का graph, करोड़ों likes की गिनती, और बहुत ज़्यादा reads।

---

## 🔴 Problem it Solves
At Instagram scale (2B+ monthly users), naive designs fail:
- Uploading 100M+ photos/day through app servers would crush bandwidth.
- Building every feed on request (`SELECT posts WHERE author IN (500 followees) ORDER BY time`) for millions of users per minute is too slow.
- Celebrity posts (600M followers) can't be written into 600M feeds instantly.
- Like counts on viral posts get thousands of updates per second (hot rows).
- Images must load fast on slow 3G/4G networks worldwide.

## 🔴 यह क्यों बना? (Hindi)
Instagram के स्केल पर सीधे तरीके फ़ेल होते हैं: रोज़ 10 करोड़+ फ़ोटो app servers से upload नहीं हो सकतीं; हर बार feed बनाना धीमा; 60 करोड़ followers वाले celebrity की post सबकी feed में तुरंत डालना नामुमकिन; वायरल post पर लाखों likes; और धीमे नेटवर्क पर images तेज़ खुलनी चाहिए।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional: upload photo/video (+caption, tags, location), follow/unfollow, home feed (ranked),
  profile grid, like/comment, stories (24h), notifications, explore/search (scope as needed)
Non-functional: highly available (AP for feed is fine — eventual consistency OK), feed load < 300 ms,
  image first paint < 1 s on 4G, durable media (never lose a photo), read-heavy (100:1)
Out of scope (say so): ads, DMs (see Topic 115), reels recommendation details
```

### 2. Estimation

```
DAU 500M; uploads 100M/day ≈ 1,150/s (peak ×3); avg photo 2 MB original → resized variants
Media storage/day: 100M × (2 MB + ~600 KB variants) ≈ 260 TB/day → ~95 PB/year (object storage!)
Feed reads: 500M DAU × 20 feed loads ≈ 10B/day ≈ 115k/s (peak 350k/s)
Likes: 4B/day ≈ 46k/s; comments 500M/day
Image egress: 10B feed loads × 10 images × 60 KB ≈ 6 PB/day → served by CDN (+ device caching)
```

### 3. Core APIs

```
POST /media/upload-url            → presigned URL(s) (multipart for video)
POST /posts { mediaIds[], caption, location } → 201 post
GET  /feed?cursor=                → ranked posts (cursor pagination)
GET  /users/{id}/posts?cursor=    → profile grid
POST /posts/{id}/likes  DELETE /posts/{id}/likes
POST /posts/{id}/comments         GET /posts/{id}/comments?cursor=
POST /users/{id}/follow           DELETE /users/{id}/follow
POST /stories   GET /stories/feed
```

### 4. High-level architecture

```
 📱 App ──► CDN (images/videos) ◄───────────────────────────────┐
   │                                                              │
   ├─(1) get presigned URL ─► Media svc                           │
   ├─(2) upload original ───► S3 (raw bucket)                     │
   │                               │ S3 event                     │
   │                               ▼                              │
   │                     Media processing workers (queue)         │
   │                     resize (150/320/640/1080 px), WebP/AVIF, │
   │                     video transcode (HLS), blurhash, NSFW/   │
   │                     safety scan → S3 (processed) ────────────┘
   │
   ├─(3) POST /posts ──► Post svc ──► Posts DB (sharded by post/user id)
   │                         └─ event "PostCreated" ──► Kafka
   │                                                     ├─► Feed fan-out workers ─► Feed cache (Redis lists per user)
   │                                                     ├─► Notification svc
   │                                                     ├─► Search/Explore indexer
   │                                                     └─► Counters / analytics
   ├─ GET /feed ──► Feed svc: read precomputed ids + merge celebrity posts + rank ──► hydrate posts (cache) 
   ├─ like/comment ─► Engagement svc ─► likes store + async counters (Redis → DB)
   └─ follow ───────► Graph svc ─► followers/following tables (sharded) + cache
```

### 5. Feed generation (the key deep dive)

```
Fan-out on WRITE (push model):
  When Alice posts → push post_id into each follower's feed list (Redis/Cassandra)
  ✅ feed read = 1 fast read   ❌ celebrities: 600M writes per post; wasted work for inactive users

Fan-out on READ (pull model):
  When Bob opens feed → fetch recent posts of everyone he follows → merge → rank
  ✅ cheap writes, celebs fine   ❌ slow reads (500 followees), heavy at 350k feed loads/s

HYBRID ⭐ (what Instagram/Twitter do):
  - Normal users (< ~10k–100k followers): fan-out on write to ACTIVE followers' feed caches
  - Celebrities: NOT fanned out; their recent posts pulled at read time and merged
  - Inactive users: no precomputed feed; built on demand when they return
  Feed svc: candidates = precomputed list ∪ celebrity posts ∪ (suggested posts) → RANKING model
           (engagement prediction: relationship, recency, interest, media type) → top N → hydrate
```

### 6. Data model

```
users(id, username UNIQUE, name, bio, avatar_key, is_private, follower_count, following_count)
posts(id [Snowflake: time-sortable + shard], user_id, caption, location, created_at, media[] → media_ids)
media(id, post_id, type, variants{150,320,640,1080 urls}, width, height, blurhash, duration)
follows: followers(user_id, follower_id, created_at) + following(user_id, followee_id) — both directions,
         sharded by user_id (graph store / Cassandra / sharded Postgres)
likes(post_id, user_id, created_at) PK (post_id, user_id)  ← "did I like it?" + list of likers
post_counters(post_id, likes, comments)  ← denormalized, async-updated (Topic 32)
comments(post_id, comment_id, user_id, text, created_at) partitioned by post_id
feed_cache: Redis list feed:{user_id} = [post_ids...] capped at ~500
stories: (user_id, story_id, media, expires_at) TTL 24h; story_views
```

### 7. Other deep dives

```
Media: originals in S3 (11 nines), processed variants, CDN with long cache (immutable keys);
       client requests size for its screen; progressive loading with blurhash placeholder
IDs: Snowflake-like (Instagram's: 41-bit ms + 13-bit shard + 10-bit seq) → sortable, shard-aware
Sharding: Postgres sharded by user_id (Instagram ran thousands of logical shards — Topic 42)
Counters: likes → write like row + Redis INCR → periodic flush to post_counters (write-back, Topic 47);
          show approximate counts; viral posts handled without hot-row contention
Caching: post objects, user objects (memcache/Redis), feed lists; CDN for media; app caches feed
Stories: write to each follower's "stories tray" lazily; TTL expiry; view lists for owner
Privacy: private accounts → feed/permalink checks; blocked users filtered at read
Consistency: eventual for feeds/counts (AP); strong for follow state & privacy checks
```

## 🟢 कैसे काम करता है? (Hindi)
1. Upload: ऐप presigned URL से फ़ोटो सीधे S3 पर डालता है → workers छोटे-बड़े sizes, WebP, video HLS, blurhash बनाते हैं → CDN से दिखती है।
2. Post बनते ही "PostCreated" event Kafka में → feed workers, notifications, search, counters सब अपना काम करते हैं।
3. Feed hybrid: सामान्य users की post उनके active followers की feed list (Redis) में डाली जाती है; celebrities की posts पढ़ते समय जोड़ी जाती हैं; फिर ranking।
4. Likes: like की row + Redis में गिनती, बाद में DB में flush — वायरल post पर भी hot row नहीं।
5. Posts DB user_id से sharded, Snowflake IDs; stories 24 घंटे TTL के साथ; feed और counts थोड़े पुराने चल सकते हैं (eventual)।

---

## 🟡 Real World Example

**Instagram's actual stack (public talks)** — Django + Python, PostgreSQL sharded into thousands of logical shards, Cassandra for feeds and activity, memcache, RabbitMQ/Celery for async tasks, S3 plus Facebook's CDN, and Snowflake-style IDs with the shard embedded. Instagram famously served 30M users with 13 engineers before the Facebook acquisition.

**Feed ranking (2016)** — Instagram moved from a chronological feed to a ranked one, because users missed ~70% of posts. Ranking uses ML predictions of interest, relationship and timeliness.

**Justin Bieber problem** — a single celebrity's posts caused hot shards and huge counter contention, which led to denormalized counters and special handling for high-follower accounts.

**Pinterest / Twitter** — similar hybrid fan-out designs, which are standard in interviews for feed systems.

## 🟡 Real Example Hindi में
Instagram ने Django + हज़ारों logical shards वाले PostgreSQL, Cassandra, memcache, Celery से शुरुआत की — 13 इंजीनियरों ने 3 करोड़ users चलाए। 2016 में chronological से ranked feed पर गए क्योंकि लोग 70% posts देख ही नहीं पाते थे।
Justin Bieber की posts से एक shard पर भारी बोझ और likes की गिनती में टकराव हुआ — तब denormalized counters और celebrities के लिए अलग तरीका आया।

---

## 🟠 My Stack Example

### Create post → event (Node)
```js
app.post('/api/v1/posts', authenticate, async (req, res) => {
  const { mediaIds, caption, location } = PostIn.parse(req.body);
  await assertMediaOwnedAndReady(mediaIds, req.user.id);
  const postId = snowflake(shardFor(req.user.id));
  await withTx(dbFor(req.user.id), async (tx) => {
    await tx.query('INSERT INTO posts(id, user_id, caption, location) VALUES ($1,$2,$3,$4)', [postId, req.user.id, caption, location]);
    await tx.query('UPDATE media SET post_id=$1 WHERE id = ANY($2)', [postId, mediaIds]);
    await tx.query("INSERT INTO outbox(event_type, payload) VALUES ('PostCreated', $1)", [{ postId, authorId: req.user.id, at: Date.now() }]);
  });
  res.status(201).json({ id: postId });
});
```

### Fan-out worker (hybrid)
```js
const CELEB_THRESHOLD = 100_000;
consumer.on('PostCreated', async ({ postId, authorId, at }) => {
  const followerCount = await graph.followerCount(authorId);
  if (followerCount > CELEB_THRESHOLD) {
    await redis.zAdd(`celeb_posts:${authorId}`, { score: at, value: String(postId) });   // pulled at read time
    await redis.zRemRangeByRank(`celeb_posts:${authorId}`, 0, -201);                      // keep latest 200
    return;
  }
  for await (const batch of graph.activeFollowersInBatches(authorId, 1000)) {           // skip inactive users
    const pipe = redis.multi();
    for (const f of batch) {
      pipe.zAdd(`feed:${f}`, { score: at, value: String(postId) });
      pipe.zRemRangeByRank(`feed:${f}`, 0, -501);                                          // cap 500
    }
    await pipe.exec();
  }
});
```

### Feed read: merge precomputed + celebrities, rank, hydrate
```js
app.get('/api/v1/feed', authenticate, async (req, res) => {
  const uid = req.user.id;
  const own = await redis.zRangeWithScores(`feed:${uid}`, 0, 199, { REV: true });
  const celebs = await graph.followedCelebrities(uid);                                    // cached small list
  const celebPosts = (await Promise.all(celebs.map((c) => redis.zRangeWithScores(`celeb_posts:${c}`, 0, 19, { REV: true })))).flat();
  const candidates = dedupe([...own, ...celebPosts]);
  const ranked = await ranker.score(uid, candidates);                                     // ML or heuristic (recency × affinity)
  const page = paginate(ranked, req.query.cursor, 20);
  const posts = await postCache.getMany(page.items.map((p) => p.value));                  // multi-get from cache, DB on miss
  const likedSet = await likes.didUserLike(uid, posts.map((p) => p.id));
  res.json({ items: posts.map((p) => ({ ...p, liked: likedSet.has(p.id) })), nextCursor: page.nextCursor });
});
```

### Media processing worker (Python, Pillow) triggered by S3 → SQS
```python
SIZES = [150, 320, 640, 1080]
def process(key: str):
    img = Image.open(io.BytesIO(s3.get_object(Bucket=RAW, Key=key)["Body"].read()))
    img = ImageOps.exif_transpose(img).convert("RGB")
    variants = {}
    for w in SIZES:
        v = img.copy(); v.thumbnail((w, w * 2))
        buf = io.BytesIO(); v.save(buf, "WEBP", quality=80)
        out = f"processed/{key}/{w}.webp"
        s3.put_object(Bucket=MEDIA, Key=out, Body=buf.getvalue(), ContentType="image/webp", CacheControl="public, max-age=31536000, immutable")
        variants[w] = f"https://cdn.myapp.com/{out}"
    update_media(key, variants, blurhash_of(img), img.size)
```

### React Native feed: right size image + placeholder
```tsx
<Image
  source={{ uri: pickVariant(post.media[0].variants, screenWidth * PixelRatio.get()) }}
  placeholder={{ blurhash: post.media[0].blurhash }}
  contentFit="cover" cachePolicy="memory-disk" style={{ width: screenWidth, aspectRatio: post.media[0].w / post.media[0].h }}
/>
// FlashList + prefetch next page images; optimistic like (Topic 67)
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you design Instagram's home feed?**
A1: A hybrid fan-out. When a regular user posts, a worker pushes the post ID into each active follower's precomputed feed (Redis sorted set or Cassandra), capped in size. Celebrities' posts aren't fanned out but fetched at read time from their recent-posts list. Reading the feed merges the precomputed IDs with followed celebrities' posts, applies a ranking model (affinity, recency, engagement prediction), paginates with a cursor, and hydrates posts and users from caches. Inactive users' feeds are built on demand when they return.

**Q2: How do you handle photo uploads at scale?**
A2: Clients upload directly to object storage via presigned (multipart) URLs, so app servers never handle the bytes. Upload events trigger async processing workers that validate and scan content, strip EXIF location if required, generate multiple resized variants in modern formats (WebP/AVIF), transcode video to HLS, and compute blurhash placeholders. Processed media is stored under immutable keys and served through a CDN with long cache lifetimes. The post is created only after media is processed, and clients request the right size for their screen.

**Q3: How do you store and count likes for viral posts?**
A3: Store individual likes as `(post_id, user_id)` rows for correctness and the "did I like this" check. Maintain counts separately and denormalized: increment in Redis (or sharded counters) and flush aggregated deltas to the posts' counter table periodically (write-back). This avoids hot-row lock contention when thousands of likes per second hit one post. Display approximate counts and reconcile periodically from the source rows.

**Q4: How would you shard the data?**
A4: Shard user-centric data (profile, posts, following lists) by user_id, so a user's posts and profile live together and profile grids are single-shard queries. Use time-sortable IDs that embed the shard ID (Snowflake-style) so any post ID can be routed. Followers lists for celebrities can be huge, so store them in a scalable wide-column store partitioned by user and bucket. Comments and likes are partitioned by post_id. Media lives in object storage, which scales on its own.

**Q5: What consistency guarantees would you provide?**
A5: Eventual consistency for feeds, counts and explore: a few seconds of delay is fine, and it favours availability and latency. Read-your-writes for the author, so their new post appears immediately on their own profile and feed (client inserts it optimistically, or reads from the primary). Strong checks for privacy and permission decisions (private accounts, blocks), which are evaluated at read time against an authoritative graph and cache.

---

## 🔷 Trade-offs
✅ Fan-out on write: fast feeds — ❌ write amplification, celebs problematic.
✅ Fan-out on read: cheap writes — ❌ slow/expensive reads.
✅ Hybrid + ranking: best UX at scale — ❌ complex, needs ML infra.
✅ Async counters: scalable — ❌ approximate/lagging counts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fan-out on write | Push post into followers' feeds | लिखते समय सबकी feed में डालना |
| Fan-out on read | Build feed when requested | पढ़ते समय feed बनाना |
| Hybrid fan-out | Push for most, pull for celebrities | दोनों का मिश्रण |
| Feed ranking | Ordering posts by predicted interest | रुचि के हिसाब से क्रम |
| Hydration | Fetching full objects for ids | ids से पूरा डेटा लाना |
| Media pipeline | Resize/transcode/scan after upload | upload के बाद प्रोसेसिंग |
| Blurhash | Tiny blurred placeholder | धुंधला placeholder |
| Snowflake ID | Time + shard + sequence id | समय + shard वाली id |
| Hot shard / key | Overloaded partition | ज़्यादा बोझ वाला हिस्सा |
| Social graph | Follow relationships | follow के रिश्ते |

---

## ⚡ 3-Line Summary
**English:**
1. Media: presigned direct-to-S3 upload → async processing (variants, WebP, HLS, blurhash) → CDN with immutable keys.
2. Feed: hybrid fan-out (push to active followers, pull celebrities) into Redis/Cassandra lists → rank → hydrate from caches.
3. Shard by user_id with Snowflake IDs; likes as rows + async counters; eventual consistency for feeds/counts, strong for privacy.

**Hindi:**
1. Media: सीधे S3 upload → प्रोसेसिंग (sizes, WebP, HLS, blurhash) → CDN।
2. Feed: hybrid — सामान्य users की posts followers की feed में, celebrities की पढ़ते समय; फिर ranking।
3. user_id से sharding, Snowflake IDs; likes rows + async गिनती; feed eventual, privacy strong।

---

## ➡️ Next Topic Suggestion
**117. Twitter / Feed System** — Instagram's feed is media-centric. Next: the classic text timeline (Twitter/X), with the celebrity fan-out problem, home vs user timelines, trending topics, search and real-time updates.
