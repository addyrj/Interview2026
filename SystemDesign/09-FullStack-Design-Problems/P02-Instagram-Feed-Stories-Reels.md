# P02. Instagram — Feed + Stories + Reels (End-to-End Design)
# हिंदी में: Instagram का पूरा डिज़ाइन — Feed (ranked posts), Stories (24 घंटे वाली), Reels (एक के बाद एक vertical videos) — mobile ऐप, web और backend मिलाकर: upload, ranking, fan-out, media preload, autoplay और तेज़ scrolling

---

## 🔵 Simple Definition (English)
Design Instagram's three core consumption surfaces end to end:
- **Feed**: a ranked list of posts (photos, carousels, videos) from people you follow, plus suggested posts and ads, with infinite scroll.
- **Stories**: ephemeral (24 h) full-screen photo/video sequences per user. A **tray** at the top orders users with unseen stories, and a viewer handles tap-to-advance, hold-to-pause and **seen state**.
- **Reels**: an infinite **vertical swipe** of short videos (≤ 90 s), mostly **recommended** (not just from followed accounts), with instant autoplay.
The full stack spans:
- **mobile clients** (React Native): virtualized lists, video players, **aggressive media preloading**, network-aware quality
- **web** (Next.js): SSR for public profiles and posts (SEO), client-side feed
- **backend**: upload and transcoding pipeline, feed generation (hybrid fan-out + ML ranking), story and reels services, counters, CDN

## 🔵 सरल परिभाषा (Hindi)
Instagram की तीन मुख्य चीज़ें: Feed — जिन्हें follow करते हो उनके posts (ranking के साथ) + suggested + ads, infinite scroll; Stories — 24 घंटे वाली full-screen फ़ोटो/वीडियो की कड़ी, ऊपर tray (बिना देखी stories पहले), tap से आगे, दबाकर रोकना, "देख लिया" याद रखना; Reels — ऊपर swipe करते ही अगला छोटा वीडियो, ज़्यादातर recommended, तुरंत autoplay।
पूरा stack: mobile (virtualized lists, video players, पहले से media लाना), web (Next.js — public profile/post SEO के लिए SSR), backend (upload + transcoding, feed fan-out + ML ranking, stories/reels services, counters, CDN)।

---

## 🔴 Problem it Solves
Media apps live or die by **perceived speed and engagement**:
- A feed that shows spinners, a story that buffers between taps, or a reel that takes 2 s to start makes users leave.
- Every user's feed is **different and ranked**, built from hundreds of followed accounts, including celebrities with hundreds of millions of followers (the fan-out problem).
- **Video at scale** is expensive: transcoding, storage, CDN egress and mobile data for users on prepaid plans.
- **Stories expire** and need per-viewer seen state for billions of views per day.
- **Reels need recommendation**: candidate retrieval plus ranking in under ~100 ms, and the client must preload the next videos without wasting data.
The question tests **media pipelines, feed architecture, client performance and data/network efficiency** together.

## 🔴 यह क्यों बना? (Hindi)
Media ऐप तेज़ी और engagement पर ही टिकते हैं: feed में spinner, story के बीच buffering, या reel शुरू होने में 2 सेकंड = यूज़र चला गया। हर यूज़र का feed अलग और ranked — सैकड़ों accounts से, जिनमें करोड़ों followers वाले celebrities (fan-out की समस्या); वीडियो महँगा (transcoding, storage, CDN, यूज़र का data); stories 24 घंटे में ख़त्म और हर देखने वाले का "देखा" याद रखना; reels के लिए ~100 ms में recommendation और client पर अगले वीडियो पहले से — बिना data बर्बाद किए।

---

## 🟢 How it Works — Step by Step

### 1. Requirements

```
Functional: post photo/video/carousel with caption; home feed (ranked, infinite); like/comment/save/share;
            stories (create, 24 h expiry, tray, viewer, seen state, reply via DM);
            reels (vertical infinite player, recommendations, like/comment, audio); web: profiles & posts
Non-functional: feed first content < 1 s (cached), story/reel start < 300 ms, 60 fps scroll,
            data-efficient on 3G/4G (India), high availability; eventual consistency OK for counts
Scale (assume): 500M DAU, 100M new posts/day, 500M story views/hour peak, reels: billions of plays/day
```

### 2. High-level architecture

```
Clients: RN app (iOS/Android) · Next.js web
   │ HTTPS (BFF / GraphQL)                    │ media (HLS/MP4/WebP) via CDN
   ▼                                          ▼
┌────────────────────────────── Backend ─────────────────────────────────────┐
│ Mobile/Web BFF (screen-shaped: /feed, /stories/tray, /reels)               │
│  ├─ Feed service: candidates (followed posts from fan-out cache + pull for  │
│  │   celebrities + suggested) → ranking service (ML) → mix ads → page       │
│  ├─ Stories service: active stories (TTL 24 h), tray ranking, seen-state    │
│  ├─ Reels service: retrieval (embeddings/ANN, trending, follow graph) →     │
│  │   ranking → dedupe already-watched → page of video manifests             │
│  ├─ Post service / Graph service (follows) / Counter service (likes)        │
│  └─ Media service: presigned uploads → processing queue                      │
│ Async: Kafka (post.created, like, view events) → fan-out workers, counters, │
│        feature store for ranking, analytics                                 │
│ Storage: Postgres/MySQL (sharded) posts & users, Cassandra/Redis feed       │
│          caches, object storage + CDN for media, Redis for seen/story TTL   │
└─────────────────────────────────────────────────────────────────────────────┘
Media pipeline: upload (M21) → transcode video to HLS/DASH ladder (240p…1080p) + MP4 preview,
                images to AVIF/WebP sizes + blurhash → CDN
```

### 3. Feed generation (hybrid fan-out, recap of Topic 116/117)

```
Post created by normal user (≤ ~10k followers) → FAN-OUT ON WRITE: push post id into each follower's
   feed cache (Redis/Cassandra list, capped ~500 ids)
Celebrity post (millions of followers) → NO fan-out; FAN-OUT ON READ: merged at request time
Request /feed: candidates = follower cache + recent celebrity posts + suggested/recommended
   → ranking model (engagement probability: like/comment/watch-time, recency, relationship)
   → insert ads at positions → return page (cursor) with media URLs, blurhash, dims, counts
Seen-post dedupe: bloom filter / recent-impressions set per user
```

### 4. Client: feed

```
FlashList with item types: post_image, post_carousel, post_video, suggested_users, ad
Image cells: sized CDN URLs + blurhash + recyclingKey (M12); carousels horizontal FlashList (fixed height)
Video in feed: autoplay MUTED only for the most-visible item (viewability ≥ 60%), pause others;
   one active player instance reused (pool of 1–2 players), poster frame first
Prefetch: next 5–10 posts' images into disk cache; next video's first segment on Wi-Fi
Optimistic like (double-tap heart animation on UI thread via Reanimated) + batched like events
Cold start: render cached first page (persisted query cache) instantly → refresh in background
Impressions: viewability tracking (item visible ≥ 1 s) batched to analytics → ranking feedback loop
```

### 5. Stories end to end

```
Create: capture → edit (stickers/text) → upload (eager) → story {user_id, media, created_at, expires_at=+24h}
Storage: active stories per user in Redis/Cassandra with TTL; archive for user's own "Archive"
Tray: GET /stories/tray → users with active stories, ordered by ranking (closeness, unseen first),
      each with has_unseen + first unseen item id + thumbnails
Viewer (client):
  - full-screen pager per user; within user: segments with progress bars (image 5 s, video = duration)
  - tap right/left = next/prev, hold = pause, swipe up/down = close/reply, swipe horizontal = next user (cube)
  - PRELOAD: current segment + next 2 segments + first segment of next user (images & video first chunk)
  - mark seen locally immediately; batch POST /stories/seen {story_ids[]} every few seconds/on close
Seen state server: per (viewer, story_owner) → last_seen_story_ts (compact: one value per owner, since
  stories are time-ordered) → tray computes has_unseen = owner_latest_ts > viewer_last_seen_ts
Viewer list for owner ("Seen by 1,234"): write viewer ids to story_views (story_id, viewer_id) async via Kafka
```

### 6. Reels end to end

```
Backend: retrieval (two-tower embeddings + ANN: Faiss/ScaNN), trending, audio/creator graphs →
         ranking (watch-time prediction, completion, shares) → filter watched (per-user recent set) →
         page of 10 reels: {id, hls_url, mp4_fallback, first_frame_url, duration, audio, creator, counts}
Client player:
  - vertical pager (FlashList pagingEnabled / react-native-pager-view), ONE item visible at a time
  - player pool of 3 (prev, current, next): current plays, next is PRELOADED (buffer first 1–2 s),
    prev kept paused for quick back-swipe; others released (memory!)
  - adaptive bitrate (HLS) starting low on cellular for fast start, then ramp up
  - show first-frame image instantly, swap to video when ready (no black screen)
  - preload depth adaptive: Wi-Fi → next 2–3 reels; cellular/data saver → next 1, low quality
  - watch-time events (25/50/75/100%, loops, skips) → ranking signals
```

### 7. Web (Next.js)

```
/[username], /p/[postId], /reel/[id] → SSR/ISR for SEO & link previews (OpenGraph), public data only
/ (home feed) → client-rendered behind login (React Query infinite, virtualized)
Stories/Reels on web: same APIs; HLS via hls.js; preload next segment with <link rel="preload"> / MSE
```

### 8. Counters & consistency

```
Likes/views: write events to Kafka → aggregate (Flink/streaming) → counter store (Redis + periodic DB)
Client shows optimistic count; server count eventually consistent ("1.2M likes" approximations)
User's own like state must be accurate → per-user like table (post_id, user_id) checked for "liked by me"
```

## 🟢 कैसे काम करता है? (Hindi)
1. Feed: आम यूज़र का post उसके followers की feed cache में डाला जाता है (fan-out on write); celebrity का post पढ़ते समय जोड़ा जाता है (fan-out on read); फिर ML ranking + ads + suggested → cursor वाला page।
2. Feed client: FlashList में अलग item types; images सही आकार + blurhash; सिर्फ़ सबसे ज़्यादा दिख रहा वीडियो muted autoplay (एक ही player दोबारा इस्तेमाल); अगले posts की images पहले से; double-tap like optimistic; खुलते ही cache वाला पहला page।
3. Stories: 24 घंटे TTL; tray में बिना देखी stories वाले पहले; viewer में progress bars, tap/hold/swipe; अभी वाला + अगले 2 segments + अगले यूज़र का पहला segment पहले से लोड; "देखा" पहले local, फिर batch में सर्वर; सर्वर पर हर owner के लिए सिर्फ़ last_seen_ts।
4. Reels: embeddings से उम्मीदवार → ranking → देखे हुए हटाओ; client पर 3 players (पिछला, अभी, अगला) — अगला पहले से buffer, बाक़ी release (memory); पहले first-frame image फिर वीडियो; Wi-Fi पर ज़्यादा preload, cellular पर कम और low quality; watch-time events ranking को।
5. Web: profile/post/reel pages SSR/ISR (SEO, link preview), home feed login के पीछे CSR; likes/views Kafka से aggregate — count थोड़ी देर बाद सही (eventual), पर "मैंने like किया" हमेशा सही।

---

## 🟡 Real World Example

**Instagram Stories (2016)** — launched in August 2016, reaching 500M daily users by 2019. Instagram engineers have described aggressive prefetching of upcoming stories so tapping through feels instant, plus batched seen-state updates.

**Instagram Reels in India (July 2020)** — after India banned TikTok on June 29, 2020, Instagram launched Reels in India in July 2020, ahead of the global launch in August. Indian short-video apps (Moj, Josh, MX TakaTak) also grew rapidly, and all compete on instant playback and recommendation quality on budget phones.

**Ranked feed (2016)** — Instagram moved from a chronological to a ranked feed in 2016, and later re-introduced a "Following" chronological option. Ranking uses many models predicting interactions.

**Video infrastructure** — Meta reports that video is a dominant share of Instagram time. Encoding ladders, ABR and CDN caching (and aggressive client prefetch with data-saver controls) are core to cost and UX.

## 🟡 Real Example Hindi में
Instagram Stories अगस्त 2016 में आईं और 2019 तक रोज़ 50 करोड़ यूज़र्स — अगली stories पहले से लोड करके tap तुरंत; 2016 में feed समय-क्रम से ranked हुआ।
भारत में TikTok पर 29 जून 2020 को बैन के बाद Instagram ने जुलाई 2020 में Reels भारत में पहले लॉन्च किया (global अगस्त में); Moj, Josh, MX TakaTak जैसे भारतीय ऐप भी तेज़ी से बढ़े — सब सस्ते फ़ोन पर तुरंत playback और अच्छे recommendation पर मुक़ाबला करते हैं।

---

## 🟠 My Stack Example

### BFF: reels page with network-aware payload (Node)
```js
app.get('/mobile/v1/reels', auth, async (req, res) => {
  const { cursor } = req.query; const net = req.get('X-Network-Type');           // wifi | 4g | 3g
  const candidates = await reelsRetrieval.candidates(req.user.id, { cursor, k: 200 });
  const ranked = (await ranker.score(req.user.id, candidates)).filter((r) => !watchedRecently(req.user.id, r.id)).slice(0, 10);
  res.json({
    items: ranked.map((r) => ({
      id: r.id, durationMs: r.durationMs,
      hls: `${CDN}/reels/${r.id}/master.m3u8`,
      mp4: `${CDN}/reels/${r.id}/${net === '3g' ? '360' : '720'}.mp4`,            // fallback/progressive
      firstFrame: `${CDN}/reels/${r.id}/ff.webp?w=720`, blurhash: r.blurhash,
      creator: { id: r.creatorId, name: r.creatorName, avatar: `${CDN}/u/${r.creatorId}.webp?w=96` },
      counts: { likes: r.likes, comments: r.comments }, likedByMe: r.likedByMe, audio: r.audio,
    })),
    nextCursor: ranked.at(-1)?.cursor ?? null,
    preload: net === 'wifi' ? 3 : 1,                                             // server hints preload depth
  });
});
```

### RN: reels pager with a 3-player window and preloading (react-native-video)
```tsx
import Video from 'react-native-video';
import { FlashList } from '@shopify/flash-list';

export function ReelsScreen() {
  const { data, fetchNextPage } = useInfiniteQuery({ queryKey: ['reels'], queryFn: ({ pageParam }) => api.reels(pageParam), initialPageParam: undefined, getNextPageParam: (l) => l.nextCursor });
  const reels = data?.pages.flatMap((p) => p.items) ?? [];
  const preload = data?.pages.at(-1)?.preload ?? 1;
  const [active, setActive] = useState(0);
  const { height } = useWindowDimensions();

  const onViewable = useRef(({ viewableItems }: any) => viewableItems[0] && setActive(viewableItems[0].index)).current;
  useEffect(() => { reels.slice(active + 1, active + 1 + preload).forEach((r) => Image.prefetch(r.firstFrame)); }, [active, reels.length]);

  return (
    <FlashList
      data={reels} pagingEnabled showsVerticalScrollIndicator={false} keyExtractor={(r) => r.id}
      onViewableItemsChanged={onViewable} viewabilityConfig={{ itemVisiblePercentThreshold: 80 }}
      onEndReached={() => fetchNextPage()} onEndReachedThreshold={3}
      renderItem={({ item, index }) => {
        const mounted = Math.abs(index - active) <= 1;                          // prev, current, next only
        return (
          <View style={{ height }}>
            <Image source={{ uri: item.firstFrame }} placeholder={{ blurhash: item.blurhash }} style={StyleSheet.absoluteFill} />
            {mounted && (
              <Video source={{ uri: item.hls }} style={StyleSheet.absoluteFill} resizeMode="cover" repeat
                     paused={index !== active}                                   // next is buffered but paused
                     bufferConfig={{ minBufferMs: 1500, maxBufferMs: 8000, bufferForPlaybackMs: 500 }}
                     onProgress={({ currentTime }) => trackWatch(item.id, currentTime, item.durationMs)} />
            )}
            <ReelOverlay reel={item} />
          </View>
        );
      }}
    />
  );
}
```

### Stories: seen state batching (client) + compact storage (server)
```ts
// client: mark seen instantly, flush in batches
const pendingSeen = new Set<string>();
export function markStorySeen(storyId: string, ownerId: string, createdAt: number) {
  storiesCache.setSeen(ownerId, createdAt);                              // tray updates immediately
  pendingSeen.add(`${ownerId}:${storyId}:${createdAt}`);
}
setInterval(() => { if (!pendingSeen.size) return; const batch = [...pendingSeen]; pendingSeen.clear();
  http.post('/stories/seen', { items: batch }).catch(() => batch.forEach((b) => pendingSeen.add(b))); }, 5000);
```
```python
# server (FastAPI + Redis): one timestamp per (viewer, owner) since stories are time-ordered
@app.post("/stories/seen")
async def seen(body: SeenBatch, user=Depends(current_user)):
    pipe = redis.pipeline()
    for owner_id, story_id, created_at in body.parsed():
        pipe.eval(MAX_SCRIPT, 1, f"seen:{user.id}", owner_id, created_at)   # HSET only if greater
        pipe.xadd("story_views", {"story": story_id, "viewer": user.id})    # → "Seen by" list via consumer
    await pipe.execute()
    return {"ok": True}

@app.get("/stories/tray")
async def tray(user=Depends(current_user)):
    owners = await following_with_active_stories(user.id)                  # owner_id → latest_ts
    seen = await redis.hgetall(f"seen:{user.id}")
    items = [{"ownerId": o, "hasUnseen": ts > int(seen.get(o, 0))} for o, ts in owners.items()]
    return rank_tray(user.id, items)                                       # unseen + closeness first
```

### Next.js public post page (SSR/ISR + OpenGraph)
```tsx
// app/p/[postId]/page.tsx
export const revalidate = 300;
export async function generateMetadata({ params }: { params: Promise<{ postId: string }> }) {
  const p = await getPublicPost((await params).postId);
  return { title: `${p.author.name} on Instagram`, description: p.caption?.slice(0, 150), openGraph: { images: [p.media[0].url] } };
}
export default async function PostPage({ params }: { params: Promise<{ postId: string }> }) {
  const p = await getPublicPost((await params).postId);
  return <PublicPost post={p} />;                                     // like/comment buttons prompt login (client island)
}
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you make Reels start instantly?**
A1: Return a page of ranked reels with HLS manifests, MP4 fallbacks, a first-frame image and a blurhash. On the client, keep a small player pool (previous, current, next): the next reel is preloaded and buffered for its first second or so while paused, the current one plays, and others are released to save memory. Show the first-frame image immediately and swap to video when ready. Start adaptive bitrate at a lower rendition on cellular for a fast first frame, adapt preload depth to the network (more on Wi-Fi, less on data saver), and serve video from a nearby CDN with segments cached at the edge.

**Q2: How do you implement story seen state at scale?**
A2: Stories for an owner are time-ordered and expire in 24 hours, so per viewer you only need the timestamp of the latest story seen per owner, not a row per story. The client marks seen locally for an instant UI and batches updates. The server keeps `seen:{viewer}` as a hash of owner → last_seen_ts (updated only if greater). The tray computes "has unseen" by comparing it with each owner's latest story timestamp. The owner's "Seen by" list is written asynchronously via a stream to a story_views store with TTL.

**Q3: How is the home feed generated for users who follow celebrities?**
A3: With a hybrid fan-out. Posts from normal accounts are fanned out on write into followers' feed caches. Posts from accounts with huge follower counts aren't fanned out; they're fetched at read time from those celebrities' recent posts and merged. The merged candidates, plus recommended and suggested content, go through ML ranking (predicted engagement, recency, relationship strength), already-seen posts are filtered, ads are inserted, and the result is returned as a cursor page with sized media URLs.

**Q4: How do you handle video autoplay in the feed efficiently?**
A4: Track viewability and play only the single most-visible video item (for example ≥ 60% visible), muted by default, pausing others immediately as they scroll out. Reuse one or two player instances instead of creating a player per cell. Show poster images and blurhash before playback. Prefetch only the first segment of the next video when on Wi-Fi. Respect data saver and the OS low-power mode by disabling autoplay. Release players when the screen is blurred or the app is backgrounded.

**Q5: How do you keep data usage reasonable for Indian users on prepaid plans?**
A5: Use network-aware policies: detect cellular generation or data-saver settings and request lower-resolution images and lower video renditions, reduce preload depth (next one reel only), disable feed video autoplay on cellular if the user chooses, and use efficient codecs and formats (HEVC/AV1 where supported, AVIF/WebP images). Cache aggressively on disk to avoid re-downloads, prefetch heavier content only on Wi-Fi, expose a "Data saver" toggle, and measure bytes per session as a product metric.

---

## 🔷 Trade-offs
✅ Fan-out on write: fast feed reads — ❌ write amplification for big accounts (hybrid fixes).
✅ Aggressive preloading: instant UX — ❌ wasted data/battery on skips → network-aware depth.
✅ Player pool of 3: smooth swipes — ❌ memory pressure on low-end devices (reduce to 2).
✅ Eventual counters: scalable — ❌ counts briefly inconsistent across views.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fan-out on write | Push post into followers' feeds | लिखते समय followers तक |
| Fan-out on read | Merge posts at read time | पढ़ते समय जोड़ना |
| Ranking | Ordering by predicted engagement | पसंद के अनुमान से क्रम |
| Story tray | Row of users with active stories | stories की पंक्ति |
| Seen state | What viewer has watched | क्या देख लिया |
| Player pool | Reused video player instances | दोबारा इस्तेमाल players |
| Preloading | Buffer upcoming media early | आगे का media पहले से |
| ABR (HLS) | Adaptive bitrate streaming | नेटवर्क के हिसाब से quality |
| Viewability | % of item visible on screen | कितना दिख रहा |
| First frame | Poster image of video | वीडियो का पहला दृश्य |

---

## ⚡ 3-Line Summary
**English:**
1. Backend: media pipeline (upload → transcode ladders → CDN), hybrid fan-out + ML ranking for feed, TTL stories with compact seen state, embedding-based retrieval + ranking for reels.
2. Client: FlashList feeds with sized images & single autoplay player; story viewer with segment preloading & batched seen; reels pager with 3-player window, first-frame, ABR and network-aware preload.
3. Web: SSR/ISR public pages for SEO, CSR feed; counters eventual via streaming; always design for data cost and low-end devices.

**Hindi:**
1. Backend: upload → transcoding → CDN, feed के लिए hybrid fan-out + ML ranking, TTL वाली stories और छोटा seen state, reels के लिए embeddings + ranking।
2. Client: FlashList feed (सही images, एक autoplay player), story viewer में preload + batch seen, reels में 3 players, first-frame, नेटवर्क के हिसाब से preload।
3. Web: public pages SSR/ISR, feed CSR; counts eventual; data ख़र्च और सस्ते फ़ोन का ध्यान।

---

## ➡️ Next Topic Suggestion
**P03. Uber/Ola — Rider app + Driver app + backend** — From media to the physical world: two different mobile apps coordinated in real time through location streams, dispatch, trip state machines and payments.
