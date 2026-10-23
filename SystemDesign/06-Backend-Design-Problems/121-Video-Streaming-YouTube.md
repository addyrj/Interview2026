# 121. Video Streaming (YouTube / Netflix / Hotstar)
# हिंदी में: Video Streaming — वीडियो upload करना, उसे कई quality (240p–4K) में बदलना (transcoding), छोटे टुकड़ों में CDN से भेजना, और नेटवर्क के हिसाब से quality अपने आप बदलना (adaptive streaming)

---

## 🔵 Simple Definition (English)
Design a video platform like **YouTube** (user uploads at massive scale) or **Netflix/Hotstar** (curated catalog + live sports). Core pieces: a **resumable upload** service, an asynchronous **transcoding pipeline** (multiple resolutions/bitrates/codecs, segmented for **HLS/DASH**), **storage** in object stores, global delivery via **CDNs**, **adaptive bitrate (ABR)** playback on clients, **metadata/search/recommendations**, **view counting & analytics**, and optionally **live streaming** and **DRM**.

## 🔵 सरल परिभाषा (Hindi)
YouTube/Netflix/Hotstar जैसा सिस्टम: वीडियो upload (टूटे तो वहीं से), फिर उसे 240p से 4K तक कई quality में बदलना और 2-6 सेकंड के टुकड़ों (HLS/DASH) में काटना, S3 में रखना, CDN से दुनिया भर में भेजना, और player का नेटवर्क देखकर quality बदलना। साथ में views, search, recommendations, live streaming और DRM।

---

## 🔴 Problem it Solves
- Raw videos are huge (1 hour of 4K ≈ 20+ GB) and come in many formats; devices and networks vary from 2G phones to 4K TVs.
- Streaming the original file → constant buffering on slow networks, wasted bandwidth on small screens.
- Billions of views/day → **petabytes of egress**; impossible from origin servers alone.
- **Live events** (IPL: tens of millions concurrent) need low latency and massive fan-out.
- Content protection (DRM), copyright detection, moderation.

## 🔴 यह क्यों बना? (Hindi)
Raw वीडियो बहुत बड़े और अलग-अलग formats में; devices 2G फ़ोन से 4K TV तक। Original फ़ाइल सीधे भेजो तो धीमे नेटवर्क पर buffering और छोटी स्क्रीन पर डेटा बर्बाद। अरबों views = petabytes ट्रैफ़िक; IPL जैसा live करोड़ों लोग एक साथ; और copyright/DRM सुरक्षा भी।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional: upload video (+title, description, thumbnail), process/transcode, watch (seek, quality switch),
            search, recommendations, likes/comments, view counts, (live streaming), (subtitles)
Non-functional: smooth playback (startup < 2 s, rebuffer ratio < 1%), global low latency via CDN,
                durable storage, upload processing within minutes, massive read scale (watch ≫ upload)
```

### 2. Estimation (YouTube-like)

```
Uploads: 500 hours of video per minute ≈ 30k hours/hour
Raw size ~ 1 GB/hour (1080p) → 30 TB/hour raw; transcoded renditions ×(1.5–2) → ~50 TB/hour stored
Views: 1B hours watched/day; avg bitrate 2 Mbps → 1e9 h × 3600 s × 2 Mb = 7.2e15 Mb/day ≈ 900 PB/day egress
→ CDN + ISP-embedded caches (YouTube GGC, Netflix Open Connect) are mandatory
Live: 25M concurrent × 3 Mbps = 75 Tbps (Hotstar IPL scale)
```

### 3. Upload & processing pipeline

```
 📱 Creator ─1. init upload (metadata) ─► Upload svc ─► returns resumable upload URL (multipart)
          ─2. upload chunks directly ─► Object storage (raw bucket)    (resume on failure)
                                              │ 3. "VideoUploaded" event
                                              ▼
                             ┌──────────── Processing orchestrator (DAG / workflow) ──────────┐
                             │ validate/probe (ffprobe) → split into GOP-aligned segments      │
                             │ → PARALLEL transcode each segment × each rendition:            │
                             │    240p/360p/480p/720p/1080p/4K, H.264 / VP9 / AV1, audio AAC  │
                             │ → package into HLS (.m3u8 + .ts/.fmp4) and DASH (.mpd)          │
                             │ → thumbnails, preview sprites, captions (ASR), DRM encryption  │
                             │ → content checks: copyright (fingerprint), moderation (ML)     │
                             └───────────────────────────────┬────────────────────────────────┘
                                                             ▼
                                   Object storage (processed) → CDN origin
                                   Metadata DB: status=READY, renditions, duration → search index
 Creator notified "video is live" (push/email)
```

### 4. Adaptive bitrate streaming (ABR)

```
Master playlist (HLS master.m3u8):
  #EXT-X-STREAM-INF:BANDWIDTH=400000,RESOLUTION=426x240   → 240p/index.m3u8
  #EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=854x480  → 480p/index.m3u8
  #EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080→ 1080p/index.m3u8
Each rendition = list of 2–6 s segments (seg_0001.m4s ...)

Player loop: measure download speed & buffer → choose rendition for NEXT segment
  network drops → switch down to 480p (no stall); improves → switch up
Startup: begin with low/medium quality for fast start; seek = fetch segment at that time
Segments are small static files → cache perfectly on CDNs
```

### 5. Delivery: CDN & caching

```
Client → DNS/anycast → nearest CDN edge (or ISP-embedded cache) → hit: serve segment
                                         miss → regional shield → origin (object storage)
Popular videos: pre-positioned in edge caches (Netflix fills Open Connect boxes off-peak)
Long tail: served from regional caches/origin
Signed URLs/cookies for paid or private content (Topic 51); DRM (Widevine/FairPlay/PlayReady)
```

### 6. Metadata, views, recommendations

```
videos(id, channel_id, title, description, status, duration, renditions JSON, visibility, created_at)
  → relational/sharded DB + cache; search index (Elasticsearch)
View counting: player sends heartbeat/view events → Kafka → stream processing (dedupe bots, count
  "valid views") → counters in batches (write-back, Topic 47) → displayed counts lag (the "301" story)
Watch history & resume position: per user key-value store (Cassandra/Bigtable), updated every N seconds
Recommendations: offline ML (candidate generation + ranking) + real-time signals; precomputed per user
Comments/likes: like Topic 116 (async counters)
```

### 7. Live streaming (Hotstar / YouTube Live)

```
Broadcaster → RTMP/SRT ingest → live transcoder (real-time ABR ladder) → packager (HLS/DASH,
  low-latency HLS with partial segments) → origin → CDN → millions of viewers
Latency: standard HLS 15–30 s; LL-HLS/DASH 2–5 s; WebRTC < 1 s (for small audiences)
Scale tricks: pre-warm CDNs, multi-CDN, origin shielding, cap max bitrate during peaks,
  "panic mode" degrade non-essential features, client back-off on errors
```

## 🟢 कैसे काम करता है? (Hindi)
1. Creator टुकड़ों में resumable upload करता है, सीधे S3 में; "VideoUploaded" event से processing शुरू।
2. वीडियो को छोटे हिस्सों में काटकर parallel में हर quality (240p…4K) और codec (H.264/VP9/AV1) में बदला जाता है, फिर HLS/DASH segments + playlists, thumbnails, captions, DRM, copyright जाँच।
3. Player पहले master playlist लेता है, फिर हर अगले टुकड़े के लिए नेटवर्क देखकर quality चुनता है — नेटवर्क गिरे तो 480p, बिना रुके।
4. Segments छोटी static फ़ाइलें हैं, इसलिए CDN (और ISP के अंदर के caches) पर बढ़िया cache होती हैं — origin पर कम बोझ।
5. Views events Kafka से गिने जाते हैं (bots हटाकर, देर से दिखते हैं); live में RTMP ingest → real-time transcode → LL-HLS → CDN; IPL के लिए multi-CDN और pre-warm।

---

## 🟡 Real World Example

**YouTube** — 500+ hours uploaded per minute. Videos are transcoded in parallel on Google's infrastructure, VP9 and AV1 codecs save bandwidth, and Google Global Cache servers sit inside ISPs. The famous "301 views" freeze came from view validation, with counts updated in batches.

**Netflix** — per-title (and per-shot) encoding optimization, AV1 for mobile, Open Connect appliances inside ISPs serving 95%+ of traffic, and a client ABR algorithm tuned for each device.

**Disney+ Hotstar / JioCinema** — world records for concurrent viewers in IPL and cricket World Cup matches (25M+ on Hotstar, later even higher on JioCinema), using multi-CDN delivery, extensive pre-scaling and load testing, and "panic buttons" to switch off features under extreme load.

**Twitch** — live streaming with low-latency HLS, and transcoding offered selectively (not all channels get the full ladder) to control cost.

## 🟡 Real Example Hindi में
YouTube पर हर मिनट 500+ घंटे वीडियो आते हैं — parallel transcoding, VP9/AV1 से डेटा बचत, और ISPs के अंदर Google Global Cache। Netflix की Open Connect boxes 95% ट्रैफ़िक देती हैं।
Hotstar/JioCinema ने IPL और World Cup में करोड़ों लोगों को एक साथ live दिखाने का रिकॉर्ड बनाया — multi-CDN, पहले से scale और "panic button" से।

---

## 🟠 My Stack Example

### Init resumable upload + process on S3 event (Node)
```js
app.post('/api/v1/videos', authenticate, async (req, res) => {
  const { title, sizeBytes, contentType } = VideoIn.parse(req.body);
  const videoId = crypto.randomUUID();
  const key = `raw/${req.user.id}/${videoId}`;
  const { UploadId } = await s3.send(new CreateMultipartUploadCommand({ Bucket: RAW, Key: key, ContentType: contentType }));
  const parts = Math.ceil(sizeBytes / (16 * 1024 * 1024));                       // 16 MB parts
  const urls = await Promise.all(Array.from({ length: parts }, (_, i) =>
    getSignedUrl(s3, new UploadPartCommand({ Bucket: RAW, Key: key, UploadId, PartNumber: i + 1 }), { expiresIn: 3600 })));
  await db.query("INSERT INTO videos(id, owner_id, title, status, raw_key) VALUES ($1,$2,$3,'UPLOADING',$4)", [videoId, req.user.id, title, key]);
  res.status(201).json({ videoId, uploadId: UploadId, partUrls: urls });          // client uploads parts in parallel, resumable
});
// POST /videos/:id/complete → CompleteMultipartUpload → status PROCESSING → enqueue transcode job
```

### Transcoding worker (ffmpeg → HLS ladder)
```bash
# one rendition (run in parallel for 240p/480p/720p/1080p; or split into segments for parallelism)
ffmpeg -i input.mp4 -vf scale=-2:720 -c:v libx264 -preset veryfast -b:v 2800k -maxrate 3000k -bufsize 6000k \
  -g 48 -keyint_min 48 -sc_threshold 0 -c:a aac -b:a 128k \
  -f hls -hls_time 4 -hls_playlist_type vod -hls_segment_type fmp4 \
  -hls_segment_filename '720p/seg_%04d.m4s' 720p/index.m3u8
# then write master.m3u8 listing all renditions with BANDWIDTH/RESOLUTION
```
```python
# worker (FastAPI/Celery side): pick job → download raw → run ffmpeg per rendition → upload to processed/ → mark READY
@celery.task(bind=True, acks_late=True, max_retries=3)
def transcode(self, video_id):
    for r in LADDER:                      # [(240,400k),(480,1200k),(720,2800k),(1080,5000k)]
        run_ffmpeg(video_id, r)           # idempotent: output paths deterministic; skip if exists
    write_master_playlist(video_id)
    mark_ready(video_id)                  # → notify creator, index in search
```
Managed alternatives: AWS Elemental MediaConvert (VOD), MediaLive + MediaPackage (live), Mux, Cloudflare Stream.

### Serve playback (signed CloudFront cookies for the video path)
```js
app.get('/api/v1/videos/:id/playback', authenticateOptional, async (req, res) => {
  const v = await videos.get(req.params.id);
  if (!canWatch(req.user, v)) return res.sendStatus(403);
  const cookies = signer.getSignedCookies({ policy: policyFor(`https://cdn.myapp.com/videos/${v.id}/*`, 3600) });
  setCloudFrontCookies(res, cookies);
  res.json({ manifestUrl: `https://cdn.myapp.com/videos/${v.id}/master.m3u8`, resumeAt: await history.position(req.user?.id, v.id) });
});
```

### React Native player (expo-video / react-native-video handle ABR)
```tsx
import { useVideoPlayer, VideoView } from 'expo-video';
const player = useVideoPlayer(manifestUrl, (p) => { p.currentTime = resumeAt; p.play(); });
<VideoView player={player} style={{ width: '100%', aspectRatio: 16 / 9 }} allowsFullscreen allowsPictureInPicture />
// Every 10 s: POST /views/heartbeat { videoId, position } → Kafka → views + resume position
```

### Next.js web: hls.js for browsers without native HLS
```tsx
useEffect(() => { if (Hls.isSupported()) { const hls = new Hls(); hls.loadSource(manifestUrl); hls.attachMedia(ref.current!); return () => hls.destroy(); } }, [manifestUrl]);
```

---

## ⚫ Interview Questions + Answers

**Q1: Walk through what happens when a user uploads a video.**
A1: The client initiates an upload and gets resumable multipart presigned URLs, then uploads chunks directly to object storage. Completion triggers an event, and a processing workflow validates and probes the file, splits it into GOP-aligned segments, and transcodes them in parallel into a bitrate ladder (multiple resolutions and codecs). It packages them as HLS/DASH segments with playlists, generates thumbnails and captions, applies DRM, and runs copyright and moderation checks. Outputs go to object storage behind a CDN, metadata is set to READY and indexed for search, and the creator is notified.

**Q2: What is adaptive bitrate streaming and why is it essential?**
A2: The video is encoded at multiple bitrates and resolutions and cut into short segments described by playlists (HLS/DASH). The player continuously measures throughput and buffer level and picks the quality for each next segment, dropping quality when the network degrades (avoiding stalls) and raising it when bandwidth allows. It serves everything from 2G phones to 4K TVs from the same content, and segments cache efficiently on CDNs.

**Q3: How do you deliver video at petabyte-per-day scale?**
A3: Through CDNs and edge caches close to users, including ISP-embedded caches (Netflix Open Connect, YouTube GGC), with origin shielding and tiered caching. Pre-position popular content during off-peak hours, use multiple CDNs for redundancy and cost, and use efficient codecs (HEVC, VP9, AV1) and per-title encoding to cut bytes. Long cache TTLs on immutable segments. Origin object storage serves only cache misses.

**Q4: How would you count views accurately at scale?**
A4: Players emit view and heartbeat events (start, watched X seconds) to an ingestion pipeline (Kafka). Stream processing validates them (minimum watch time, deduplication per user and session, bot and fraud filtering) and aggregates counts in windows, then flushes to counter storage in batches. Public counts are eventually consistent and may freeze during validation spikes. Raw events also go to the warehouse for analytics and creator dashboards.

**Q5: What changes for live streaming of a major cricket match?**
A5: Ingest via RTMP or SRT with redundancy, then real-time transcoding into an ABR ladder and packaging into low-latency HLS or DASH (2–5 s target) with short segments or partial chunks. Use multi-CDN distribution with pre-warmed edges and origin shields, and plan capacity for the 10–20× surges at toss and key moments: pre-scale, load-test with simulated tens of millions of viewers, cap bitrates if needed, and degrade non-critical features. Monitor rebuffering and startup time in real time per CDN and region, and switch traffic between CDNs on issues.

---

## 🔷 Trade-offs
✅ More renditions/codecs: better quality per device — ❌ more transcoding cost & storage.
✅ AV1/VP9: 30–50% bandwidth savings — ❌ higher encode cost, device support varies.
✅ Short segments / LL-HLS: lower latency — ❌ more requests, less CDN efficiency.
✅ Own edge caches (Open Connect): cost & quality — ❌ huge investment; most use commercial CDNs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transcoding | Converting video into other formats/bitrates | वीडियो को दूसरे format/quality में बदलना |
| Bitrate ladder | Set of renditions (240p…4K) | quality की सीढ़ी |
| HLS / DASH | Segment-based streaming protocols | टुकड़ों वाले streaming तरीके |
| Segment | 2–6 s chunk of video | वीडियो का छोटा टुकड़ा |
| Manifest / playlist | List of renditions & segments | टुकड़ों की सूची |
| ABR | Adaptive bitrate selection | नेटवर्क के हिसाब से quality |
| Codec | Compression format (H.264, AV1) | compression का तरीका |
| DRM | Content protection (Widevine) | content सुरक्षा |
| Origin shield | Cache layer before origin | origin से पहले की cache परत |
| Rebuffering | Playback stalls to load | वीडियो रुककर लोड होना |

---

## ⚡ 3-Line Summary
**English:**
1. Upload resumably to object storage → async DAG: split, parallel transcode to a bitrate ladder, package HLS/DASH, thumbnails, DRM, checks.
2. Deliver segments via CDNs/ISP caches; players use adaptive bitrate per segment for smooth playback.
3. Views via event pipeline with validation and batched counters; live = real-time transcode + LL-HLS + multi-CDN + pre-scaling.

**Hindi:**
1. Resumable upload → processing: काटो, parallel में हर quality, HLS/DASH, thumbnails, DRM।
2. Segments CDN/ISP caches से; player हर टुकड़े पर नेटवर्क देखकर quality चुनता है।
3. Views events से (जाँच के साथ, batch में गिनती); live = real-time transcode + LL-HLS + multi-CDN।

---

## ➡️ Next Topic Suggestion
**122. Search System (Google)** — Next: a web-scale search engine, with crawling, indexing (inverted index at scale), ranking (PageRank and relevance), query serving and autocomplete.
