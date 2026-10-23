# M08. Networking on Mobile (Flaky Network, Retry, Batching)
# हिंदी में: Mobile पर Networking — टूटते, धीमे और बदलते (Wi-Fi ↔ 4G) नेटवर्क पर API calls को भरोसेमंद और किफ़ायती बनाना: timeout, retry, requests को इकट्ठा भेजना (batching), compression, और नेटवर्क की गुणवत्ता के हिसाब से ढलना

---

## 🔵 Simple Definition (English)
Mobile networking means designing client–server communication for **high latency, packet loss, frequent disconnects, network switches, metered data and battery cost**. Key techniques:
- **Timeouts** (connect, read, overall) so requests don't hang forever.
- **Retries with exponential backoff + jitter**, only for **idempotent** or idempotency-keyed requests, and only for retryable errors.
- **Batching and coalescing**: group many small requests or events into fewer calls, which matters because waking the **cellular radio** is expensive.
- **Request prioritization and cancellation**: user-visible requests first, cancel when the screen is left.
- **Deduplication** of identical in-flight requests.
- **Payload efficiency**: compression (gzip/brotli), smaller JSON or protobuf, device-sized images, delta sync.
- **Connection efficiency**: keep-alive, **HTTP/2** multiplexing, **HTTP/3/QUIC** (faster handshakes, **connection migration** across Wi-Fi ↔ 4G), TLS session resumption, DNS caching.
- **Network-aware behaviour**: detect offline or "lie-fi", adapt quality on 2G/3G, respect data saver, defer big transfers to Wi-Fi.

## 🔵 सरल परिभाषा (Hindi)
Mobile networking = ऐसे API calls बनाना जो ज़्यादा latency, packet loss, बार-बार टूटने, Wi-Fi ↔ 4G बदलने, महँगे data और battery के बावजूद काम करें: timeout (हमेशा अटके नहीं), backoff + jitter के साथ retry (सिर्फ़ safe requests), batching (कई छोटी requests एक साथ — radio जगाना महँगा है), priority और cancel, duplicate रोकना, compression और छोटा payload, HTTP/2–3 (QUIC नेटवर्क बदलने पर भी कनेक्शन बचाता है), और नेटवर्क की गुणवत्ता के हिसाब से ढलना।

---

## 🔴 Problem it Solves
Real mobile conditions (especially in India): crowded towers at peak hours, metro tunnels, 4G that drops to 2G/EDGE, Wi-Fi with captive portals, users switching from home Wi-Fi to mobile data mid-request, and prepaid data limits.
Naive networking causes:
- **Infinite spinners** (no timeouts) or **instant failures** (no retries) on a momentary drop.
- **Retry storms**: thousands of clients retrying in sync after an outage, which knocks the server down again.
- **Duplicate orders/payments** from retried non-idempotent POSTs.
- **Battery drain**: 50 tiny analytics requests keep the radio awake for minutes.
- **Slow screens**: 6 sequential requests × 400 ms RTT = 2.4 s before content shows.
- **Data cost**: uncompressed JSON and full-size images burn users' data packs.

## 🔴 यह क्यों बना? (Hindi)
भारत में असली हालत: peak पर भीड़ वाले towers, मेट्रो सुरंग, 4G से अचानक 2G, captive portal वाला Wi-Fi, request के बीच Wi-Fi से mobile data पर जाना, prepaid data की सीमा।
लापरवाह networking से: अंतहीन spinner (timeout नहीं) या तुरंत fail (retry नहीं); outage के बाद हज़ारों clients एक साथ retry करके सर्वर फिर गिरा दें; retry से duplicate order/payment; 50 छोटी analytics requests से radio मिनटों जगा रहे (battery ख़त्म); 6 requests एक के बाद एक = 2.4 सेकंड; बिना compression के JSON और बड़ी images से data pack ख़त्म।

---

## 🟢 How it Works — Step by Step

### The cellular radio & battery (why batching matters)

```
Radio states (simplified LTE): IDLE ──request──► CONNECTED (high power) ──tail timer (~5–10 s)──► IDLE
- Waking from IDLE adds latency (100s of ms on LTE, more on 3G) and costs energy
- After each transfer, radio stays high-power for a "tail" period
50 requests spread over 2 min → radio never sleeps → battery drain
Same 50 batched into 2 bursts → radio sleeps most of the time ✅
→ Batch analytics/logs, prefetch together, piggyback non-urgent calls on user-triggered ones
```

### Latency math

```
RTT on 4G India: often 50–150 ms (good) to 300–800 ms (congested/3G); TLS 1.3 handshake = 1 RTT, QUIC 0–1 RTT
Screen needs: /me, /banners, /restaurants, /offers, /cart sequentially → 5 × 400 ms = 2 s (+ server time)
Fix: one BFF call (M09/F11) or parallel requests over one HTTP/2 connection → ~1 RTT
```

### Timeouts & retries policy

```
Timeouts: connect 5–10 s, read 10–20 s (longer for uploads, per-chunk), overall deadline per user action
Retry ONLY if: request is idempotent (GET/PUT/DELETE) or has Idempotency-Key (POST), AND
               error is retryable: network error, timeout, 502/503/504, 429 (respect Retry-After)
Never retry: 400/401/403/404/409/422 (fix the cause instead; 401 → refresh token once)
Backoff: delay = min(cap, base × 2^attempt) × random(0.5, 1)   e.g., 1s, 2s, 4s, 8s … cap 30 s
Max attempts: 3–5 for user-visible; outbox items retry longer (minutes/hours) in background
Client circuit breaker: after N consecutive failures to a host, stop for a cool-down → show offline state
```

### Batching & coalescing

```
Analytics: buffer events in memory + MMKV; flush every 30 s or 20 events or on app background
Location: collect points every 5 s, upload every 15 s as one array (M20)
Reads: GET /products?ids=1,2,3 (batch) instead of 3 calls; GraphQL/BFF aggregation
Coalesce identical in-flight GETs (dedupe): 3 components asking /me → 1 request (React Query does this)
Debounce user input requests (search: 300 ms) and cancel stale ones (AbortController)
```

### Payload & connection efficiency

```
Compression: Accept-Encoding: gzip, br (OkHttp/NSURLSession handle gzip automatically); compress large uploads
Formats: JSON with only needed fields; protobuf/MessagePack for chatty/real-time channels
Images: request device-sized variants (?w=360&dpr=2), AVIF/WebP (M12)
Connections: reuse (keep-alive), HTTP/2 multiplexing, HTTP/3/QUIC: no head-of-line blocking, 0-RTT
             resumption, connection migration (Wi-Fi→4G keeps the same connection ID)
DNS: cache results, prefer resolvers close to user; avoid many different hostnames (each = DNS + TLS)
CDN for static/media; edge POPs in Indian metros reduce RTT
```

### Network-aware behaviour

```
Detect: NetInfo (type: wifi/cellular, details.cellularGeneration 2g/3g/4g/5g, isInternetReachable,
        isConnectionExpensive), plus measured throughput/latency of recent requests
Adapt: lower image quality & disable autoplay video on 2G/3G or data saver; smaller page sizes;
       defer media backup/large downloads to Wi-Fi (user setting); prefetch on Wi-Fi + charging
Offline: show offline banner, serve cached data, queue writes (M06)
"Lie-fi": connected but failing → rely on request timeouts/failures, not just NetInfo
```

### Prioritization

```
P0: user-blocking (tap "Place order", screen data) → immediately, highest priority
P1: likely-needed soon (prefetch next screen) → after P0 completes
P2: background (analytics, logs, sync) → batched, deferred, cancellable
Cancel requests for screens the user left (AbortController / React Query cancels on unmount)
```

## 🟢 कैसे काम करता है? (Hindi)
1. फ़ोन का radio जगाना महँगा और हर transfer के बाद कुछ सेकंड जागा रहता है — इसलिए छोटी-छोटी requests (analytics, location) इकट्ठा करके कभी-कभार भेजो, ताकि radio सो सके।
2. Timeout ज़रूर (connect 5–10 s, read 10–20 s); retry सिर्फ़ safe requests पर (GET/PUT या Idempotency-Key वाली POST) और सिर्फ़ नेटवर्क/timeout/5xx/429 पर; backoff + jitter (1s, 2s, 4s… random), 4xx पर कभी नहीं।
3. एक screen के लिए कई requests एक के बाद एक मत भेजो — BFF से एक call या HTTP/2 पर parallel; एक जैसी requests एक (dedupe); search में debounce + पुरानी request cancel।
4. Payload छोटा: gzip/brotli, सिर्फ़ ज़रूरी fields, device के आकार की images; कनेक्शन दोबारा इस्तेमाल, HTTP/3/QUIC (Wi-Fi से 4G जाने पर भी कनेक्शन बना रहे), CDN।
5. नेटवर्क देखकर ढलो: 2G/3G या data saver पर छोटी images और autoplay बंद, बड़ा backup सिर्फ़ Wi-Fi पर; offline में cache + queue; priority: पहले यूज़र का काम, फिर prefetch, फिर analytics।

---

## 🟡 Real World Example

**Uber and QUIC** — Uber's engineering team reported that moving its app traffic to QUIC reduced tail-end latencies significantly (tested in high-latency markets including India), thanks to better loss recovery and connection handling on lossy cellular networks.

**Facebook "2G Tuesdays" (2015)** — Facebook let employees opt into a simulated 2G connection on Tuesdays to feel what users in emerging markets experience. That fed into Facebook Lite and aggressive payload and image optimizations.

**WhatsApp** — uses a compact binary protocol (derived from XMPP, "FunXMPP") over a persistent connection, minimizing bytes and round trips so messaging works on 2G and in low-bandwidth regions.

**YouTube / Google** — pioneered QUIC (now standardized as HTTP/3) and adaptive bitrate streaming, adjusting video quality to measured bandwidth (Topic 121).

**Indian apps' data saver modes** — many offer "data saver" or "lite mode" settings (lower image quality, no autoplay), and some ship "Lite" app variants for low bandwidth and storage.

## 🟡 Real Example Hindi में
Uber ने QUIC अपनाकर tail latency काफ़ी घटाई (भारत जैसे ज़्यादा latency वाले बाज़ारों में जाँचा) — नुक़सान वाले cellular नेटवर्क पर बेहतर।
Facebook ने 2015 में "2G Tuesdays" शुरू किया ताकि कर्मचारी धीमे नेटवर्क का अनुभव करें — उसी से Facebook Lite और छोटी images आईं; WhatsApp का compact binary protocol 2G पर भी चलता है; कई भारतीय ऐप में "data saver" या "lite" mode।

---

## 🟠 My Stack Example

### Resilient fetch wrapper for React Native (timeout, retry, backoff, Retry-After, dedupe)
```ts
// src/shared/net.ts
const inflight = new Map<string, Promise<Response>>();

export async function request(url: string, init: RequestInit & { idempotencyKey?: string; retries?: number; timeoutMs?: number } = {}) {
  const method = (init.method ?? 'GET').toUpperCase();
  const key = method === 'GET' ? url : '';
  if (key && inflight.has(key)) return inflight.get(key)!.then((r) => r.clone());     // coalesce identical GETs

  const run = async () => {
    const retries = init.retries ?? 3;
    const safe = ['GET', 'PUT', 'DELETE', 'HEAD'].includes(method) || !!init.idempotencyKey;
    for (let attempt = 0; ; attempt++) {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), init.timeoutMs ?? 15_000);
      init.signal?.addEventListener('abort', () => ctrl.abort());                     // caller cancellation
      try {
        const res = await fetch(url, { ...init, signal: ctrl.signal, headers: {
          ...(init.headers as any), 'Accept-Encoding': 'gzip, br',
          ...(init.idempotencyKey ? { 'Idempotency-Key': init.idempotencyKey } : {}) } });
        const retryable = res.status === 429 || res.status === 502 || res.status === 503 || res.status === 504;
        if (!retryable || !safe || attempt >= retries) return res;
        const ra = Number(res.headers.get('Retry-After'));
        await sleep(ra ? ra * 1000 : backoff(attempt));
      } catch (e) {
        if (init.signal?.aborted || !safe || attempt >= retries) throw e;              // network error / timeout
        await sleep(backoff(attempt));
      } finally { clearTimeout(timer); }
    }
  };
  const p = run();
  if (key) { inflight.set(key, p); p.finally(() => inflight.delete(key)); }
  return p;
}
const backoff = (n: number) => Math.min(30_000, 1000 * 2 ** n) * (0.5 + Math.random() / 2);
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
```

### Batched analytics with persistence and flush on background
```ts
// src/shared/analytics.ts
import { MMKV } from 'react-native-mmkv';
const store = new MMKV({ id: 'analytics' });
let buffer: AnalyticsEvent[] = JSON.parse(store.getString('buf') ?? '[]');

export function track(name: string, props: Record<string, unknown> = {}) {
  buffer.push({ name, props, ts: Date.now(), id: uuid() });
  store.set('buf', JSON.stringify(buffer.slice(-500)));          // persist (cap size)
  if (buffer.length >= 20) flush();
}
export async function flush() {
  if (!buffer.length) return;
  const batch = buffer.splice(0, 100);
  try { await request(`${API}/events/batch`, { method: 'POST', body: JSON.stringify(batch), idempotencyKey: batch[0].id, retries: 2 }); }
  catch { buffer.unshift(...batch); }                             // try again later
  store.set('buf', JSON.stringify(buffer));
}
setInterval(flush, 30_000);
AppState.addEventListener('change', (s) => s === 'background' && flush());
```

### Network-aware image quality and Wi-Fi-only backup
```ts
import NetInfo from '@react-native-community/netinfo';
let quality: 'low' | 'high' = 'high';
NetInfo.addEventListener((s) => {
  const slow = s.type === 'cellular' && ['2g', '3g'].includes(s.details?.cellularGeneration ?? '');
  quality = slow || kv.getBoolean('settings.dataSaver') ? 'low' : 'high';
  if (s.type === 'wifi' && kv.getBoolean('backup.wifiOnly')) mediaBackup.resume(); else mediaBackup.pause();
});
export const imgUrl = (base: string, w: number) => `${base}?w=${quality === 'low' ? Math.round(w * 0.6) : w}&q=${quality === 'low' ? 50 : 75}`;
```

### Backend: batch endpoint + compression + Retry-After (Express)
```js
import compression from 'compression';
app.use(compression({ threshold: 1024 }));                     // gzip responses > 1 KB

app.post('/events/batch', express.json({ limit: '256kb' }), async (req, res) => {
  const events = Array.isArray(req.body) ? req.body.slice(0, 500) : [];
  await kafka.send({ topic: 'app-events', messages: events.map((e) => ({ key: e.id, value: JSON.stringify(e) })) });
  res.status(202).end();
});

// When overloaded: shed load politely so clients back off
app.use((req, res, next) => (overloaded() ? res.set('Retry-After', '10').status(503).end() : next()));
```

### Test on bad networks
```
Android emulator: Extended controls → Cellular → Network type EDGE/3G, signal strength poor
iOS: Network Link Conditioner (Settings → Developer) → "3G", "Very Bad Network", "100% Loss"
Proxy: Charles/Proxyman throttling; Toxiproxy for backend chaos
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you design retries for a mobile app?**
A1: Retry only idempotent requests (GET, PUT, DELETE) or POSTs carrying an idempotency key, and only on retryable failures (network errors, timeouts, 502/503/504, 429 honouring Retry-After). Use exponential backoff with jitter and a cap, with a small attempt limit for user-visible actions and longer schedules for background outbox items. Never retry 4xx validation or auth errors, except a single token refresh on 401. Add a client-side circuit breaker to stop hammering a failing host and show an offline or error state. Jitter prevents synchronized retry storms after outages.

**Q2: Why does batching matter on mobile?**
A2: Each network burst wakes the cellular radio into a high-power state, which then stays on for a tail period. Many small, spread-out requests keep the radio awake, draining battery and adding wake-up latency. Batching analytics, logs, location points and prefetches into fewer, larger requests lets the radio return to idle, reduces per-request overhead (headers, TLS, round trips) and server load, and improves throughput on high-latency links.

**Q3: How would you make a screen load fast on a high-latency 3G network?**
A3: Minimize round trips: one aggregated BFF or GraphQL request instead of sequential calls, parallelize the rest over a reused HTTP/2 or HTTP/3 connection, and avoid redirects. Show cached data immediately and refresh in the background. Shrink payloads (only needed fields, compression, device-sized images, pagination). Use a CDN near users, prefetch likely-next data when the network is good, and prioritize user-visible requests over background ones. Use skeletons rather than blocking spinners.

**Q4: What benefits does HTTP/3 (QUIC) bring to mobile apps?**
A4: QUIC runs over UDP with built-in TLS 1.3. Connection setup is faster (1-RTT, or 0-RTT on resumption), independent streams avoid TCP head-of-line blocking when packets are lost (common on cellular), and connection migration via connection IDs keeps the connection alive when the device switches from Wi-Fi to cellular or changes IP. Loss recovery and congestion control are also better and can evolve in user space. The result is lower tail latency on lossy mobile networks.

**Q5: How do you adapt behaviour to network quality?**
A5: Detect connection type, cellular generation, whether the connection is metered, and reachability (NetInfo), and combine that with measured latency and throughput of recent requests, since "connected" can still mean lie-fi. On poor or metered networks, reduce image quality, disable video autoplay and preloading, use smaller page sizes, and defer large uploads and backups to Wi-Fi or charging per user settings. Offline, serve cached data and queue writes. Expose a data saver setting and remember the user's preferences.

---

## 🔷 Trade-offs
✅ Retries improve success rates — ❌ risk duplicates (need idempotency) and storms (need jitter/limits).
✅ Batching saves battery & overhead — ❌ adds delay for non-urgent data; risk of losing buffered data (persist it).
✅ Aggressive prefetching speeds UX — ❌ wastes data/battery if unused (prefetch on Wi-Fi).
✅ Protobuf/binary: smaller & faster — ❌ harder debugging, schema tooling needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RTT | Round-trip time | आने-जाने का समय |
| Timeout | Max wait before failing | अधिकतम इंतज़ार |
| Exponential backoff | Doubling retry delay | दोगुना होता इंतज़ार |
| Jitter | Random variation in delay | इंतज़ार में random बदलाव |
| Retry storm | Synchronized mass retries | एक साथ भारी retries |
| Batching | Combining many requests | कई requests एक साथ |
| Coalescing / dedupe | Merge identical requests | एक जैसी requests एक |
| Radio tail time | Radio stays on after transfer | transfer के बाद radio जागा |
| QUIC / HTTP/3 | UDP-based fast transport | UDP वाला तेज़ protocol |
| Connection migration | Keep connection across networks | नेटवर्क बदलने पर भी कनेक्शन |

---

## ⚡ 3-Line Summary
**English:**
1. Assume flaky, high-latency networks: timeouts everywhere, retries only for safe/idempotent + retryable errors with backoff + jitter, client circuit breaker.
2. Save round trips, bytes and battery: aggregate (BFF), parallelize over HTTP/2-3, batch analytics/location, dedupe, compress, device-sized media.
3. Be network-aware: detect quality & lie-fi, adapt media and prefetching, defer big transfers to Wi-Fi, offline cache + queue, prioritize user-visible requests.

**Hindi:**
1. नेटवर्क कमज़ोर मानो: हर जगह timeout, retry सिर्फ़ safe requests पर backoff + jitter के साथ, circuit breaker।
2. Round trips, bytes और battery बचाओ: BFF, HTTP/2-3, batching, dedupe, compression, सही आकार की media।
3. नेटवर्क देखकर ढलो: 2G पर हल्का, बड़ा transfer Wi-Fi पर, offline में cache + queue, पहले यूज़र का काम।

---

## ➡️ Next Topic Suggestion
**M09. API Design for Mobile (Payload, Versioning, Backward Compatibility)** — Networking is half the story; the API contract is the other half. Next: designing APIs that stay fast for phones and never break the old app versions still in users' hands.
