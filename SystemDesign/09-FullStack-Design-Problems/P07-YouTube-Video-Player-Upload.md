# P07. YouTube — Video Player + Upload (End-to-End Design)
# हिंदी में: YouTube का पूरा डिज़ाइन — creator के फ़ोन/कंप्यूटर से video upload, सर्वर पर अलग-अलग quality में बदलना (transcoding), CDN से दुनिया भर में पहुँचाना, और web/mobile player जो नेटवर्क के हिसाब से quality बदले (adaptive streaming) — साथ में offline downloads, ads और view counting

---

## 🔵 Simple Definition (English)
Design a video platform's two critical paths end to end:
1. **Upload path (creator → platform)**:
   - **resumable upload** from mobile or web (chunked, survives drops)
   - processing: validation, **transcoding into a bitrate ladder** (144p…4K; H.264/VP9/AV1), **segmentation** into HLS/DASH, thumbnails, **auto-captions (ASR)**, copyright matching (Content ID-like), moderation
   - publishing to storage and **CDN**
2. **Playback path (viewer)**:
   - the client fetches video metadata and a **manifest**
   - the player (web: MSE + hls.js/dash.js/Shaka; Android: ExoPlayer/Media3; iOS: AVPlayer; RN: react-native-video) runs **adaptive bitrate (ABR)**, switching quality by bandwidth and buffer
   - fast start, seeking, captions, background/PiP play, **offline downloads**, DRM for premium content, ads
   - **QoE analytics**: startup time, rebuffering, bitrate
Plus view counting, watch history and recommendations. Backend internals are in **Topic 121 (Video Streaming)**. This file covers clients plus backend end to end.

## 🔵 सरल परिभाषा (Hindi)
Video platform के दो मुख्य रास्ते: (1) Upload — creator के फ़ोन/web से resumable (टुकड़ों में, टूटने पर आगे से) upload → सर्वर पर जाँच, अलग-अलग quality (144p से 4K) और codecs में बदलना, HLS/DASH के छोटे segments बनाना, thumbnails, अपने-आप captions, copyright जाँच, moderation → storage + CDN।
(2) Playback — client manifest लेता है, player (web पर MSE + hls.js, Android ExoPlayer, iOS AVPlayer) नेटवर्क और buffer देखकर quality बदलता है (ABR); जल्दी शुरू होना, seek, captions, background/PiP, offline download, premium के लिए DRM, ads, और QoE नाप (शुरू होने का समय, buffering)।

---

## 🔴 Problem it Solves
Video is the heaviest workload on the internet (the majority of consumer internet traffic):
- **Uploads**: large files (GBs) from phones on flaky networks, and creators expect processing in minutes.
- **Device and network diversity**: a ₹7,000 Android on 3G in a village and a 4K smart TV on fibre must both play smoothly. One file can't serve both.
- **Cost**: storage for many renditions and CDN egress dominate costs, so codec efficiency and caching close to users matter enormously.
- **Viewer patience**: start delay and rebuffering cause abandonment, and every second of startup time loses viewers.
- **Scale spikes**: viral videos and live events (cricket!) create sudden demand.
- **Indian specifics**: data costs (offline downloads, data saver), vernacular content, and huge concurrency on live cricket streams.

## 🔴 यह क्यों बना? (Hindi)
Video internet का सबसे भारी काम है: GBs की files flaky नेटवर्क पर phone से upload, और creators मिनटों में processing चाहते हैं; ₹7,000 का फ़ोन 3G पर और 4K TV fibre पर — दोनों smooth चलें, एक file से नहीं होगा; कई versions का storage और CDN ख़र्च सबसे बड़ा; शुरू होने में देर या buffering = दर्शक गए; viral video और live cricket पर अचानक भीड़; भारत में data ख़र्च (offline download, data saver), क्षेत्रीय भाषा content, live cricket पर करोड़ों दर्शक।

---

## 🟢 How it Works — Step by Step

### 1. Requirements & scale

```
Creator: upload (mobile/web, resumable), title/description/thumbnail, visibility, schedule, processing status
Viewer: watch (web/mobile/TV), adaptive quality, seek, captions & audio tracks, speed, PiP/background
        (premium), downloads for offline, comments/likes, history, recommendations
Non-functional: startup < 1–2 s p75, rebuffer ratio < 0.5%, upload processing minutes not hours,
        global availability, cost efficiency
Scale (public stat): ~500 hours of video uploaded per minute (YouTube, 2019);
        billions of views/day; peak egress in Tbps → CDN + ISP-embedded caches
```

### 2. Architecture

```
UPLOAD PATH
Creator app/web ──(1) POST /uploads (metadata) → resumable session URL
               ──(2) PUT chunks (Content-Range) → Upload service → raw object storage
               ──(3) finalize → Kafka "video.uploaded"
Processing (DAG of workers, autoscaled, often on spot/preemptible):
   validate/probe → split into GOP-aligned chunks → PARALLEL transcode per chunk × rendition
   (144p..2160p; H.264 for compat, VP9/AV1 for efficiency) → package (CMAF segments, HLS + DASH
   manifests) → thumbnails/storyboards (seek previews) → ASR captions → audio normalization →
   Content ID fingerprint → policy/moderation → publish (status READY) → notify creator
   (low renditions published FIRST so the video is watchable quickly; HD/4K follow)
Storage: segments in object storage (hot/cold tiers by popularity)

PLAYBACK PATH
Viewer → watch page/app → GET /videos/{id} (metadata, manifest URL, captions, ad cues, recommendations)
       → player fetches manifest → segments from CDN edge (ISP caches) → ABR adapts per segment
       → QoE + view events → analytics (Kafka) → view counts, recommendations, creator analytics
```

### 3. Adaptive bitrate (ABR) — how the player picks quality

```
Manifest lists renditions: 144p@100kbps, 240p@250k, 360p@600k, 480p@1.2M, 720p@2.5M, 1080p@5M, 4K@15M
Segments of 2–6 s each (shorter = faster switching, more requests)
Player loop per segment:
  measured throughput (EWMA of recent downloads) + current buffer level
  → choose highest rendition ≤ ~0.8 × throughput (throughput-based) and/or by buffer (BOLA, buffer-based)
  → low buffer → step down quickly; healthy buffer → step up gradually
Startup: begin with a low/medium rendition for fast first frame, prefetch init segment, then ramp up
Caps: never exceed screen resolution (no 4K on a 720p phone), user's data saver / quality setting
```

### 4. Client players

```
Web: <video> + Media Source Extensions → hls.js / dash.js / Shaka Player (DRM via EME: Widevine/PlayReady/FairPlay)
Android: ExoPlayer (Media3) — ABR, caching, offline downloads (DownloadManager), DRM
iOS: AVPlayer (native HLS), AVAssetDownloadTask for offline HLS
React Native: react-native-video (wraps ExoPlayer/AVPlayer); one active player, preload next (P02)
Features: captions (WebVTT/TTML), multiple audio tracks (languages), playback speed, PiP, background
audio (Premium), chromecast/AirPlay, keyboard shortcuts & a11y on web
Resume position: save watch progress every ~10 s (local + server) → "continue watching"
```

### 5. Offline downloads (India-first feature)

```
User picks quality (e.g., 360p ~ 150 MB/hr) → download segments + manifest + keys (DRM license with
expiry, e.g., 48 h re-check online) → stored in app sandbox (encrypted) → playable offline
Downloads respect Wi-Fi only setting, storage checks, resume on interruption (WorkManager / background session)
```

### 6. Ads (overview)

```
Client-side ad insertion (CSAI): player requests ads (VAST/VMAP via IMA SDK) at cue points → plays ad then content
Server-side ad insertion (SSAI): ads stitched into the stream (manifest manipulation) → harder to block,
smoother for live/TV; needs per-user manifests
```

### 7. View counting & integrity

```
Client sends heartbeats/events (start, 25/50/75/100%, seek, rebuffer) → Kafka → streaming dedupe & fraud
filtering (bots, refresh spam) → counts aggregated (approximate in real time, finalized later)
Why views "freeze" sometimes: validation before publishing counts
```

### 8. Live streaming (brief)

```
Ingest RTMP/SRT/WebRTC → real-time transcode → LL-HLS/LL-DASH (2–6 s latency) or WebRTC (< 1 s) → CDN
Cricket-scale concurrency: pre-provisioned CDN capacity, multi-CDN, ISP caches, ad slots planned
```

## 🟢 कैसे काम करता है? (Hindi)
1. Upload: metadata से resumable session → chunks में PUT (Content-Range) → raw storage → Kafka event; processing में file को GOP वाले टुकड़ों में बाँटकर हर टुकड़े और हर quality को साथ-साथ transcode → HLS/DASH packaging → thumbnails, ASR captions, Content ID, moderation → READY; पहले छोटी qualities publish ताकि video जल्दी दिखे।
2. Playback: `/videos/{id}` से metadata + manifest → player CDN (ISP के अंदर cache) से segments लेता है; हर segment पर ABR — नापा हुआ throughput और buffer देखकर quality; शुरुआत कम quality से (जल्दी पहला frame), फिर ऊपर; screen से बड़ी quality नहीं।
3. Players: web पर MSE + hls.js/Shaka (DRM के लिए EME), Android ExoPlayer, iOS AVPlayer, RN में react-native-video; captions, कई भाषाओं के audio, speed, PiP; हर 10 सेकंड watch position save ("continue watching")।
4. Offline download (भारत में पहले आया): quality चुनो, segments + DRM license (समय-सीमा के साथ) download, encrypted रखो, Wi-Fi-only और resume।
5. Ads: client-side (IMA SDK, cue points) या server-side stitching; views के events Kafka में, bots/spam हटाकर गिनती (इसलिए कभी views रुकते दिखते हैं); live के लिए LL-HLS और cricket जैसी भीड़ के लिए पहले से CDN capacity।

---

## 🟡 Real World Example

**YouTube scale** — YouTube reported about 500 hours of video uploaded every minute (2019). It uses parallel chunked transcoding, VP9 and AV1 codecs to cut bandwidth, and **Google Global Cache** servers placed inside ISPs (including Indian ISPs) so popular videos are served from within the user's network.

**YouTube Offline in India (2014)** — YouTube launched offline video downloads first in India and other emerging markets, followed by **YouTube Go** (2016–2022) designed for low data, low storage and preview-before-download. These are classic "next billion users" design choices.

**Netflix encoding** — Netflix pioneered per-title and later per-shot encoding (optimizing bitrate ladders per content) and the Open Connect CDN appliances in ISPs, cutting bandwidth significantly for the same quality.

**Live cricket in India (Hotstar / JioCinema)** — Indian OTT platforms have repeatedly reported world-record concurrency during cricket matches, in the multiple crores (tens of millions) of simultaneous viewers, using multi-CDN strategies, pre-scaling and aggressive ABR to keep streams smooth on mobile networks.

## 🟡 Real Example Hindi में
YouTube पर हर मिनट ~500 घंटे का video upload (2019); parallel chunked transcoding, VP9/AV1 से कम bandwidth, और भारतीय ISPs के अंदर **Google Global Cache** servers ताकि लोकप्रिय videos यूज़र के नेटवर्क के अंदर से ही आएँ।
2014 में YouTube Offline सबसे पहले भारत में आया, फिर **YouTube Go** (2016–2022) — कम data/storage के लिए; Hotstar/JioCinema ने cricket मैचों में करोड़ों एक साथ दर्शकों के रिकॉर्ड बताए — multi-CDN, पहले से scale और ABR से mobile नेटवर्क पर भी smooth।

---

## 🟠 My Stack Example

### Resumable upload session (Node/Express, S3 multipart under the hood)
```js
app.post('/videos/uploads', auth, async (req, res) => {
  const { title, sizeBytes, mime, clientId } = req.body;
  if (!['video/mp4', 'video/quicktime', 'video/webm'].includes(mime) || sizeBytes > 20 * 2 ** 30) return res.status(422).end();
  const video = await Videos.createDraft({ ownerId: req.user.id, title, clientId, status: 'UPLOADING' });   // idempotent by clientId
  const session = await uploads.startMultipart({ key: `raw/${video.id}`, size: sizeBytes, partSize: 16 * 2 ** 20 });
  res.status(201).json({ videoId: video.id, uploadId: session.id, partSize: session.partSize, partUrls: session.firstUrls });
});
app.post('/videos/:id/uploads/:uploadId/complete', auth, async (req, res) => {
  await uploads.complete(req.params.uploadId, req.body.parts);
  await Videos.update(req.params.id, { status: 'PROCESSING' });
  await kafka.send({ topic: 'video.uploaded', messages: [{ key: req.params.id, value: JSON.stringify({ videoId: req.params.id }) }] });
  res.json({ status: 'PROCESSING' });
});
// Mobile client reuses the resumable chunk uploader from M21 (persisted part ETags, background session)
```

### Processing worker: parallel transcode ladder with ffmpeg (Python sketch)
```python
LADDER = [(144, 120_000), (240, 300_000), (360, 700_000), (480, 1_200_000), (720, 2_800_000), (1080, 5_000_000)]

async def process(video_id: str):
    src = await s3_download(f"raw/{video_id}")
    info = ffprobe(src)                                            # duration, resolution, codecs, rotation
    rungs = [r for r in LADDER if r[0] <= info.height] or [LADDER[0]]
    # publish low rungs first for fast availability, then the rest
    low, rest = rungs[:2], rungs[2:]
    await asyncio.gather(*[transcode_rung(src, video_id, h, br) for h, br in low])
    await write_master_playlist(video_id, low)
    await videos.update(video_id, status="READY_LOW")                         # watchable now
    if rest:
        await asyncio.gather(*[transcode_rung(src, video_id, h, br) for h, br in rest])
        await write_master_playlist(video_id, rungs)                          # add HD renditions
    await make_thumbnails_and_storyboard(src, video_id)
    await enqueue("asr_captions", video_id); await enqueue("content_fingerprint", video_id)
    await videos.update(video_id, status="READY")

async def transcode_rung(src, vid, height, bitrate):
    out = f"/tmp/{vid}/{height}p"
    await run(["ffmpeg", "-i", src, "-vf", f"scale=-2:{height}", "-c:v", "libx264", "-b:v", str(bitrate),
               "-maxrate", str(int(bitrate * 1.2)), "-bufsize", str(bitrate * 2), "-g", "48", "-keyint_min", "48",
               "-c:a", "aac", "-b:a", "96k", "-f", "hls", "-hls_time", "4", "-hls_playlist_type", "vod",
               "-hls_segment_filename", f"{out}/seg_%05d.ts", f"{out}/index.m3u8"])
    await s3_upload_dir(out, f"hls/{vid}/{height}p/", cache_control="public, max-age=31536000, immutable")
```

### Web player (Next.js client component) with hls.js, resume and QoE events
```tsx
'use client';
import Hls from 'hls.js';
export function VideoPlayer({ video }: { video: { id: string; hls: string; poster: string; captions: { lang: string; url: string }[] } }) {
  const ref = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const el = ref.current!; const t0 = performance.now();
    let hls: Hls | undefined;
    if (Hls.isSupported()) { hls = new Hls({ capLevelToPlayerSize: true, startLevel: -1, abrEwmaDefaultEstimate: 1_000_000 }); hls.loadSource(video.hls); hls.attachMedia(el); }
    else el.src = video.hls;                                                      // Safari native HLS
    const saved = Number(localStorage.getItem(`pos:${video.id}`) ?? 0); if (saved > 5) el.currentTime = saved;
    const onPlaying = () => qoe('startup', { ms: Math.round(performance.now() - t0), level: hls?.currentLevel });
    const onWaiting = () => qoe('rebuffer_start', { t: el.currentTime });
    const save = setInterval(() => { localStorage.setItem(`pos:${video.id}`, String(el.currentTime)); progress(video.id, el.currentTime); }, 10_000);
    el.addEventListener('playing', onPlaying, { once: true }); el.addEventListener('waiting', onWaiting);
    return () => { clearInterval(save); el.removeEventListener('waiting', onWaiting); hls?.destroy(); };
  }, [video.id]);
  return (
    <video ref={ref} controls playsInline poster={video.poster} preload="metadata" style={{ width: '100%', aspectRatio: '16/9' }}>
      {video.captions.map((c) => <track key={c.lang} kind="captions" srcLang={c.lang} src={c.url} label={c.lang} />)}
    </video>
  );
}
```

### React Native player with quality cap & data saver
```tsx
<Video source={{ uri: video.hls }} style={{ width: '100%', aspectRatio: 16 / 9 }} controls
       poster={video.poster} resizeMode="contain" playInBackground={isPremium} pictureInPicture
       maxBitRate={dataSaver ? 700_000 : 0}                                     // cap ~360p on data saver (0 = no cap)
       selectedTextTrack={{ type: 'language', value: i18n.language }}
       onProgress={({ currentTime }) => throttledSaveProgress(video.id, currentTime)}
       onBuffer={({ isBuffering }) => isBuffering && qoe('rebuffer')} />
```

### View/QoE events → analytics
```json
{ "event": "video_heartbeat", "videoId": "v_9f2", "sessionId": "s_77", "position": 182.4, "bitrateKbps": 1200,
  "rebufferMs": 0, "network": "4g", "device": "android", "ts": "2026-10-18T14:02:11Z" }
```

---

## ⚫ Interview Questions + Answers

**Q1: How does adaptive bitrate streaming work?**
A1: The video is transcoded into multiple renditions (resolutions and bitrates) and split into short segments, with an HLS or DASH manifest listing them. The player downloads segments sequentially and, before each one, picks a rendition based on measured throughput (a moving average of recent downloads) and buffer health, preferring the highest quality it can sustain without stalling. It drops quickly when the buffer is low and climbs gradually when healthy, caps quality at screen size and user preferences, and starts at a modest rendition for a fast first frame.

**Q2: How do you make video processing fast for creators?**
A2: Split the source into GOP-aligned chunks and transcode chunks and renditions in parallel across an autoscaled worker fleet (often spot instances), orchestrated as a DAG with retries. Publish the lowest renditions first so the video is watchable within minutes, then add HD, 4K and efficient codecs (VP9, AV1) later. Run thumbnails, captions and fingerprinting concurrently, and cache intermediate outputs to avoid recomputation. Prioritize popular creators or short videos in queues, and notify creators of each stage.

**Q3: How do you reduce video startup time?**
A3: Return the manifest URL with the metadata (or even inline the master playlist), preconnect to the CDN, start with a lower rendition and short initial segments, prefetch the init segment and first segment (for likely-next videos in feeds), serve from edge or ISP caches close to users, use HTTP/2 or HTTP/3, show a poster or first frame immediately, and avoid blocking playback on non-critical calls like ads, recommendations or comments. Measure startup time as a QoE metric per network type.

**Q4: How would you design offline downloads?**
A4: Let the user choose a quality with a size estimate, then download the manifest, segments and captions via a background-capable downloader (Android WorkManager or ExoPlayer DownloadManager, iOS AVAssetDownloadTask) with resume support and Wi-Fi-only options. Store them encrypted in the app sandbox. For protected content, acquire offline DRM licenses with expiry that need periodic online renewal, and enforce download limits per account. Track storage usage, allow deletion and auto-cleanup, and sync watch progress when back online.

**Q5: How are views counted accurately at scale?**
A5: Clients send playback events (start, heartbeats, quartiles) with session IDs to an ingestion pipeline (Kafka). Streaming jobs dedupe, apply validity rules (minimum watch time, one view per session or time window) and filter fraud (bot patterns, abnormal IP or device rates, refresh spam). Real-time counters are approximate and are finalized by batch reconciliation. Public counts may be delayed or frozen during validation, while creator analytics come from the same validated stream aggregated in an OLAP store.

---

## 🔷 Trade-offs
✅ More renditions & modern codecs: better QoE and bandwidth — ❌ processing & storage cost (AV1 encode is slow).
✅ Short segments: faster adaptation & startup — ❌ more requests & overhead.
✅ ISP-embedded caches: low latency, low cost — ❌ partnership/ops complexity.
✅ SSAI ads: seamless — ❌ per-user manifests reduce CDN cacheability.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transcoding | Convert to other formats/bitrates | दूसरी quality में बदलना |
| Bitrate ladder | Set of renditions | qualities की सीढ़ी |
| HLS / DASH | Segment-based streaming protocols | टुकड़ों वाली streaming |
| Manifest | Playlist of renditions & segments | segments की सूची |
| ABR | Adaptive bitrate selection | नेटवर्क के हिसाब से quality |
| Segment | Few-second video chunk | कुछ सेकंड का टुकड़ा |
| MSE / EME | Browser media/DRM APIs | browser के media/DRM API |
| DRM | Content protection | content सुरक्षा |
| QoE | Quality of experience metrics | देखने के अनुभव का नाप |
| SSAI / CSAI | Server/client ad insertion | सर्वर/client पर ads |

---

## ⚡ 3-Line Summary
**English:**
1. Upload: resumable chunked upload → event → parallel chunked transcoding into a bitrate ladder → HLS/DASH packaging, thumbnails, captions, fingerprinting → publish low renditions first.
2. Playback: metadata + manifest → CDN/ISP caches → ABR player (hls.js/ExoPlayer/AVPlayer) choosing quality by throughput & buffer; fast start, captions, resume, PiP, offline downloads with DRM.
3. Measure QoE (startup, rebuffer, bitrate) and validated views through a streaming pipeline; plan live events with multi-CDN and pre-scaling.

**Hindi:**
1. Upload: resumable टुकड़े → event → parallel transcoding → HLS/DASH, thumbnails, captions → पहले कम quality publish।
2. Playback: manifest → CDN/ISP cache → ABR player throughput और buffer देखकर quality; जल्दी शुरू, captions, resume, offline + DRM।
3. QoE (startup, buffering) और सही views pipeline से नापो; live के लिए multi-CDN और पहले से scale।

---

## ➡️ Next Topic Suggestion
**P08. Amazon/Flipkart — Product Page + Cart + Checkout** — From media to money: the e-commerce funnel where milliseconds and correctness both matter. Next: a fast SEO-friendly product page, multi-device carts and a safe checkout during flash sales.
