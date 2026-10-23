# 20. Bandwidth
# हिंदी में: Bandwidth — नेटवर्क लाइन एक सेकंड में अधिकतम कितना डेटा ले जा सकती है (पाइप की चौड़ाई)

---

## 🔵 Simple Definition (English)
**Bandwidth** is the **maximum amount of data** that can be transferred over a network link per second, measured in bits per second (Mbps, Gbps). It's the **capacity** of the pipe. Actual achieved data rate is **throughput** (always ≤ bandwidth).

## 🔵 सरल परिभाषा (Hindi)
Bandwidth यानी नेटवर्क की अधिकतम क्षमता — एक सेकंड में कितना डेटा जा सकता है (जैसे 100 Mbps)।
जैसे सड़क में कितनी lanes हैं; असल में कितनी गाड़ियाँ निकलीं वो throughput है।

---

## 🔴 Problem it Solves
Bandwidth is a **constraint you must design around**:
- **Users:** a big part of India still has slow or unstable mobile internet. A 5 MB home screen on a 1 Mbps connection = 40 seconds.
- **Servers:** your VPS has a 1 Gbps NIC and maybe a monthly transfer cap. Serving videos/images directly from it saturates the link.
- **Cost:** cloud providers charge for **egress** (data out). AWS charges ~$0.09/GB for internet egress. 100 TB/month of images ≈ $9,000! CDNs and compression save real money.
- **Capacity planning:** "1M users × 2 MB per session per day = how many Gbps at peak?"

## 🔴 यह क्यों बना? (Hindi)
भारत में बहुत लोग धीमे मोबाइल इंटरनेट पर हैं — भारी ऐप स्क्रीन मिनटों में लोड होगी। सर्वर की नेटवर्क लाइन भी सीमित है, और AWS बाहर जाने वाले डेटा (egress) के पैसे लेता है।
इसलिए डेटा का आकार कम करना, CDN और compression ज़रूरी हैं।

---

## 🟢 How it Works — Step by Step

### Bandwidth vs throughput vs latency

```
Bandwidth  = width of the pipe            (max Mbps)
Throughput = water actually flowing        (actual Mbps, ≤ bandwidth)
Latency    = time for a drop to travel     (ms)

High bandwidth + high latency = satellite internet: big downloads OK, video calls laggy
Low bandwidth  + low latency  = old DSL: fast ping, slow downloads
```

### Units (common trap: bits vs bytes)

```
b = bit, B = byte (8 bits)
100 Mbps internet = 100 / 8 = 12.5 MB/s download
1 Gbps server NIC = 125 MB/s

Download time = size / throughput
  20 MB app bundle on 4 Mbps (real 4G in a crowded area) = 160 Mb / 4 = 40 s
```

### Why actual throughput < bandwidth

```
- Protocol overhead (TCP/IP headers, TLS, retransmissions)
- Latency + TCP window limits (bandwidth-delay product)
- Congestion / sharing with other users
- Packet loss on mobile networks → TCP slows down
- The slowest link on the path decides (your 1 Gbps server ≠ user's 3G)
```

### Bandwidth math for system design (back-of-envelope)

```
Video streaming app:
  1M concurrent viewers × 3 Mbps (720p) = 3 Tbps peak egress
  → impossible from your servers → must use CDN

Image feed (Instagram-like):
  10M daily users × 50 images × 200 KB = 100 TB/day ≈ 9.3 Gbps average
  peak ≈ 3× average ≈ 28 Gbps → CDN + WebP/AVIF + responsive sizes

API JSON:
  5,000 RPS × 20 KB response = 100 MB/s = 800 Mbps
  with gzip (~80% smaller)  → ~160 Mbps ✅
```

### How to save bandwidth

```
1. Compression       → gzip/brotli for text (JSON, HTML, JS, CSS): 70–90% smaller
2. Modern images     → WebP/AVIF, resize to device size, lazy-load
3. Video             → adaptive bitrate (HLS/DASH): quality matches user's bandwidth
4. CDN               → serve from edge, offload origin, cheaper egress
5. Caching           → Cache-Control, ETag/304 → don't resend unchanged data
6. Smaller payloads  → only needed fields, pagination, GraphQL, protobuf
7. Delta updates     → send changes, not full objects; OTA patch updates for apps
8. Code splitting    → ship less JavaScript (Next.js does per-route)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Bandwidth = पाइप की चौड़ाई (Mbps); throughput = असल में कितना डेटा गया; latency = कितनी देर लगी।
2. ध्यान रखो: 100 Mbps = 12.5 MB/s (bit और byte का फ़र्क़, 8 गुना)।
3. रास्ते की सबसे धीमी कड़ी तय करती है कि डेटा कितनी तेज़ी से पहुँचेगा — अक्सर यूज़र का मोबाइल नेटवर्क।
4. वीडियो/इमेज ऐप के लिए हिसाब लगाओ: users × size = कितने Gbps — आम तौर पर CDN ज़रूरी निकलता है।
5. बचत के तरीके: gzip/brotli, WebP इमेज, adaptive video, CDN, caching, छोटे API responses।

---

## 🟡 Real World Example

**YouTube / Netflix — adaptive bitrate streaming**
- The video is encoded at multiple qualities (144p…4K) in small 2–6 s chunks. The player measures your current bandwidth and picks the next chunk's quality. On a train with dropping 4G, the video becomes blurry instead of stopping. That's designing for variable bandwidth.

**Facebook Lite / YouTube Go / "Lite" apps for India**
- Built for 2G/3G networks and cheap phones: tiny APK, compressed images, text-first UI, data-saver modes. They became extremely popular in India and Africa.

**Jio effect (2016)** — data prices fell drastically, mobile video consumption in India exploded, and CDNs/ISPs had to massively increase capacity. Hotstar's IPL streaming peaks are now in the tens of Tbps, served almost entirely from CDNs and ISP-embedded caches.

## 🟡 Real Example Hindi में
YouTube वीडियो को कई quality में छोटे टुकड़ों में रखता है — नेटवर्क धीमा हो तो quality अपने आप कम हो जाती है, वीडियो रुकता नहीं। इसे adaptive bitrate कहते हैं।
Facebook Lite जैसे ऐप 2G/3G नेटवर्क के लिए बनाए गए — छोटा ऐप, कम डेटा। Jio के बाद भारत में वीडियो देखना इतना बढ़ा कि Hotstar का IPL ट्रैफ़िक Tbps में पहुँच गया।

---

## 🟠 My Stack Example

### Nginx: compression + caching headers
```nginx
gzip on;
gzip_comp_level 5;
gzip_min_length 1024;
gzip_types application/json application/javascript text/css image/svg+xml;
# brotli (if ngx_brotli module installed) — ~15–20% smaller than gzip
# brotli on; brotli_types application/json application/javascript text/css;

location /static/ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

### Node.js: don't send what the client doesn't need
```js
// ❌ returns 40 fields + nested objects (≈ 25 KB per item)
res.json(await Product.find());

// ✅ select fields + paginate (≈ 1 KB per item)
const rows = await db.query('SELECT id, name, price, thumb_url FROM products ORDER BY id LIMIT 20');
res.json({ data: rows.rows });

// ETag → 304 Not Modified (Express sets weak ETags by default on res.json/res.send)
app.set('etag', 'strong');
```

### Images: S3 + CloudFront + resize on the fly
```
Upload original → S3
Serve: https://cdn.myapp.com/img/abc.jpg?w=400&fm=webp
  CloudFront → Lambda@Edge / image service (or imgix / Cloudinary / Next.js Image)
  → resized WebP cached at edge
Result: 3 MB photo → 35 KB thumbnail
```

### Next.js — built-in bandwidth savers
```tsx
import Image from 'next/image';
<Image src={p.imageUrl} alt={p.name} width={400} height={300} sizes="(max-width: 768px) 100vw, 400px" />
// auto WebP/AVIF, responsive srcset, lazy loading
// + per-route code splitting, dynamic(() => import('./HeavyChart'), { ssr: false })
```

### React Native — mobile data matters
```tsx
import { Image } from 'expo-image';
import NetInfo from '@react-native-community/netinfo';

const net = await NetInfo.fetch();
const isSlow = net.type === 'cellular' && net.details?.cellularGeneration === '3g';
const width = isSlow ? 200 : 600;

<Image source={{ uri: `${CDN}/img/${id}.jpg?w=${width}&fm=webp` }} cachePolicy="memory-disk" />
```
- Use **OTA updates** (EAS Update) — users download a small JS bundle diff, not a whole app.
- Paginate lists, don't prefetch huge data on cellular, and offer a "data saver" setting.

### Upload big files directly to S3 (don't pipe through your server)
```
❌ RN app ──100 MB video──► Node server ──100 MB──► S3   (server bandwidth + memory used twice)
✅ RN app ── get presigned URL ──► Node
   RN app ──100 MB video (multipart, resumable)──► S3 directly
```

### Measure
```bash
iperf3 -c server-ip          # raw bandwidth between two machines
curl -o /dev/null -w "%{size_download} bytes, %{speed_download} B/s\n" https://cdn.myapp.com/big.jpg
# Chrome DevTools → Network → throttle "Slow 4G" to test your app like a real user
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between bandwidth, throughput and latency?**
A1: Bandwidth is the maximum data rate a link can carry (its capacity, Mbps). Throughput is the actual data rate achieved, which is less than or equal to bandwidth because of overhead, congestion and loss. Latency is the delay for data to travel (ms). High bandwidth doesn't fix high latency: a satellite link can have big bandwidth but 600 ms latency.

**Q2: How would you estimate bandwidth needs for a video streaming service?**
A2: Concurrent viewers × bitrate. For example, 500k concurrent × 3 Mbps = 1.5 Tbps peak. That's far beyond what origin servers can serve, so the design must use CDNs and ISP caches, adaptive bitrate streaming (HLS/DASH) to match each user's bandwidth, efficient codecs (H.265/AV1), and chunked segments that cache well at the edge. Also estimate egress cost.

**Q3: How do you design an app for users on slow or expensive mobile networks?**
A3: Minimize bytes: compress API responses (gzip/brotli), return only needed fields and paginate, serve responsive WebP/AVIF images via a CDN, lazy-load, and use code splitting and small bundles. Cache aggressively (HTTP caching, offline storage) and send deltas. Use adaptive quality for media, plus a data-saver mode. Avoid unnecessary polling (use push). Test with network throttling.

**Q4: Why should large file uploads go directly to object storage instead of through your API server?**
A4: Routing uploads through the API doubles bandwidth usage (client → server → S3), ties up server memory, connections and threads for a long time, limits throughput, and makes autoscaling harder. Presigned URLs (with multipart and resumable upload) let clients upload straight to S3, which scales without limit, while the server only issues short-lived signed URLs and processes the file asynchronously via events.

**Q5: Your AWS bill shows huge "data transfer out" costs. How do you reduce it?**
A5: Put a CDN (CloudFront) in front of static and media content. CloudFront egress is cheaper and caching reduces origin egress. Compress responses, optimize image formats and sizes, set long cache headers for versioned assets, and use ETag/304. Remove unnecessary payload fields and keep chatty service-to-service traffic within the same AZ/VPC (cross-AZ transfer also costs). Use VPC endpoints for S3 to avoid NAT gateway data charges.

---

## 🔷 Trade-offs
✅ Saving bandwidth (compression, smaller images, CDN):
- Faster for users (especially mobile), lower egress cost, higher capacity.

❌ Costs:
- Compression uses CPU (choose levels wisely; pre-compress static files).
- Lower image/video quality on slow networks.
- More complexity: image pipelines, multiple encodings, cache invalidation.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bandwidth | Max data per second of a link | नेटवर्क की अधिकतम क्षमता |
| Mbps / Gbps | Megabits / gigabits per second | प्रति सेकंड मेगाबिट/गीगाबिट |
| Egress | Data leaving your server/cloud | बाहर जाने वाला डेटा |
| Compression | Making data smaller (gzip/brotli) | डेटा को छोटा करना |
| Adaptive bitrate | Video quality adjusts to network | नेटवर्क के हिसाब से वीडियो quality |
| CDN | Edge servers near users | यूज़र के पास के सर्वर |
| Presigned URL | Temporary signed upload/download link | अस्थायी सुरक्षित लिंक |
| Payload | Data in request/response | भेजा गया डेटा |

---

## ⚡ 3-Line Summary
**English:**
1. Bandwidth = max capacity of a link (Mbps); throughput is what you actually get; latency is the delay.
2. Do bandwidth math for media-heavy systems — it usually proves you need a CDN.
3. Save bytes: compression, modern images, adaptive video, caching, smaller payloads, direct-to-S3 uploads.

**Hindi:**
1. Bandwidth = नेटवर्क की अधिकतम क्षमता; throughput = असल स्पीड; latency = देरी।
2. वीडियो/इमेज वाले सिस्टम में bandwidth का हिसाब लगाओ — CDN ज़रूरी निकलेगा।
3. बाइट बचाओ: gzip, WebP, adaptive video, cache, छोटे response, सीधा S3 upload।

---

## ➡️ Next Topic Suggestion
**21. Load Balancing Basics** — You've seen that we scale out with many servers. Next: the component that makes that work, the load balancer: L4 vs L7, health checks, and how traffic gets distributed.
