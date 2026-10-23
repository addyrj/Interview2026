# 97. Real-Time Systems
# हिंदी में: Real-Time Systems — ऐसे फ़ीचर जिनमें बदलाव यूज़र तक तुरंत (मिलीसेकंड-सेकंड में) पहुँचे — लाइव लोकेशन, चैट, typing indicator, लाइव स्कोर, collaborative editing

---

## 🔵 Simple Definition (English)
A **real-time system** (in web/mobile product terms, "soft real-time") delivers data changes to users **within a tight latency budget** (typically under 100 ms to a few seconds) without them refreshing. Examples: live order and rider tracking, chat, presence ("online"), typing indicators, live scores and stock tickers, notifications, live dashboards, multiplayer games, and collaborative editing (Google Docs, Figma).
Designing one means choosing the right **transport** (polling, long polling, SSE, WebSocket, MQTT, WebRTC, push notifications), the **data flow** (event streams, pub/sub) and **consistency/ordering** rules for the latency target.

(*Hard real-time*, used in aircraft, medical devices and industrial control, means guaranteed deadlines. That's a different field.)

## 🔵 सरल परिभाषा (Hindi)
Real-time सिस्टम में बदलाव बिना refresh किए यूज़र तक तुरंत पहुँचते हैं — डिलीवरी बॉय की लाइव लोकेशन, चैट, "typing…", लाइव स्कोर, Google Docs में साथ-साथ editing।
इसे बनाने के लिए सही तरीका चुनना पड़ता है — polling, SSE, WebSocket, MQTT, WebRTC या push notification — और latency का लक्ष्य तय करना पड़ता है।

---

## 🔴 Problem it Solves
Users expect live experiences:
- "Where's my food?" should update the rider's position on the map **every few seconds**.
- Chat messages should appear **instantly**, with "seen" and "typing…".
- Traders need prices **within milliseconds**; sports fans want the score **before the TV broadcast** (which lags).
- Refresh-based UIs feel broken, and naive polling wastes battery, data and servers.

A real-time design meets the **latency target at acceptable cost**, at scale, and on unreliable mobile networks.

## 🔴 यह क्यों बना? (Hindi)
यूज़र लाइव अनुभव चाहते हैं — मैप पर डिलीवरी बॉय हर कुछ सेकंड में हिले, चैट तुरंत दिखे, trader को कीमत milliseconds में मिले। Refresh वाला ऐप टूटा हुआ लगता है, और बेवजह की polling बैटरी, डेटा और सर्वर बर्बाद करती है।
Real-time design तय latency को सही ख़र्च पर, बड़े स्केल पर, और कमज़ोर mobile नेटवर्क पर भी पूरा करता है।

---

## 🟢 How it Works — Step by Step

### 1. Choose the transport

```
┌───────────────────┬────────────────┬──────────────────────────────┬──────────────────────────────┐
│ Transport         │ Direction      │ Latency / cost               │ Use for                      │
├───────────────────┼────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Short polling     │ client pull    │ = interval; wasteful         │ low-frequency status (every  │
│                   │                │                              │ 30–60 s), simplest MVP       │
│ Long polling      │ client pull    │ near real-time; HTTP overhead│ fallback when WS blocked     │
│ SSE               │ server → client│ low; simple; auto-reconnect  │ notifications, live feeds,   │
│                   │                │                              │ scores, LLM token streaming  │
│ WebSocket         │ both ways      │ lowest overhead; stateful    │ chat, typing, collaboration, │
│                   │                │                              │ games, trading               │
│ MQTT              │ pub/sub (TCP)  │ tiny packets, QoS levels,    │ IoT, rider/driver GPS apps,  │
│                   │                │ battery friendly             │ messaging on poor networks   │
│ WebRTC            │ peer-to-peer   │ lowest (UDP media)           │ voice/video calls, screen    │
│                   │ (+ servers)    │                              │ share, P2P data              │
│ Push (FCM/APNs)   │ server → device│ seconds; works in background │ app closed / background      │
│                   │                │ / killed app                 │ alerts                       │
└───────────────────┴────────────────┴──────────────────────────────┴──────────────────────────────┘
Rule: start with the simplest transport that meets the latency need.
```

### 2. Set a latency budget (end-to-end)

```
Rider GPS → customer map (target ≤ 3–5 s):
  rider app sends every 3 s ─► ingest API/MQTT (50 ms) ─► Kafka (20 ms) ─► tracking service
  (map-match, ETA, 30 ms) ─► Redis pub/sub (5 ms) ─► WS gateway ─► customer app (100 ms on 4G)
  Total ≈ sampling interval + ~200 ms
Chat (target ≤ 300 ms p95):  sender WS → chat svc → persist (5 ms) → fan-out → receiver WS
Collaborative editing (target ≤ 100–200 ms for local echo; remote ≤ 500 ms): optimistic local apply
```

### 3. Typical real-time pipeline

```
 Producers (apps, devices, services)
    │ high-frequency events
    ▼
 Ingest (WS/MQTT/HTTP batch) → Stream (Kafka/Kinesis/Redis Streams)
    ▼
 Processing (stream processors / services): filter, enrich, aggregate, compute state
    ▼
 Hot state store (Redis: latest location, presence, counters)    + durable store (DB/S3) for history
    ▼
 Fan-out (pub/sub → WS gateways / SSE / push)  ──► Clients render incrementally
```

### 4. Patterns per feature

```
Live location:   send deltas at adaptive frequency (moving fast → 2–3 s; stopped → 30 s);
                 store only LATEST in Redis (GEOADD/HSET), history batched to Cassandra/S3;
                 client interpolates/animates between points (smooth marker)
Presence:        heartbeat TTL keys (presence:user = online, EX 60); publish on change only;
                 "last seen" written lazily; for big friend lists, fetch on demand
Typing indicator:ephemeral, never persisted; throttle (send "typing" at most every 3 s);
                 auto-expire after 5 s
Live counters:   aggregate in memory/stream, push every 1–2 s (not every event)
Live dashboards: pre-aggregate with stream processing (Flink/ksqlDB/ClickHouse materialized views);
                 push snapshots/deltas via SSE
Collaboration:   OT (Google Docs) or CRDTs (Figma-like, Yjs/Automerge); operations broadcast via WS;
                 server orders/merges; periodic snapshots
Notifications:   in-app (WS/SSE when online) + push (FCM/APNs) when offline; dedupe both
```

### 5. Reliability and correctness in real time

```
- Ordering: sequence numbers per stream/entity; drop stale updates (older timestamp than current)
- Idempotency: clients dedupe by event id
- Gaps: resync from durable store on reconnect (lastSeq / lastUpdatedAt)
- Backpressure: coalesce or drop intermediate updates for slow clients (latest-value-wins)
- Degradation: fall back from WS → SSE → polling; reduce update frequency under load
- Mobile: background → push only; battery/data → adaptive frequency, batching
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले latency का लक्ष्य तय करो (चैट 300 ms, लोकेशन 3-5 सेकंड, dashboard 2 सेकंड)।
2. सबसे आसान तरीका चुनो जो लक्ष्य पूरा करे: कभी-कभी के update के लिए polling, सर्वर से एक तरफ़ा के लिए SSE, दोनों तरफ़ के लिए WebSocket, IoT/GPS के लिए MQTT, वीडियो कॉल के लिए WebRTC, ऐप बंद हो तो push।
3. Pipeline: events → Kafka/stream → प्रोसेसिंग → Redis (ताज़ा हालत) + DB (इतिहास) → pub/sub → clients।
4. लोकेशन में सिर्फ़ latest Redis में, client पर marker smooth चलाओ; typing indicator सेव मत करो, throttle करो; counters हर 1-2 सेकंड में भेजो।
5. Sequence नंबर से क्रम, event id से dedup, reconnect पर resync, भीड़ में updates मिलाओ या frequency घटाओ।

---

## 🟡 Real World Example

**Uber / Ola / Rapido** — driver apps send GPS every few seconds. Location is ingested into a streaming pipeline, matched to roads, stored as the latest state in in-memory geo indexes, and pushed to riders. Uber uses Kafka heavily for this, and its H3 hexagonal grid powers fast geo lookups for nearby drivers and surge pricing.

**Google Docs / Figma** — Google Docs uses Operational Transformation to merge concurrent edits. Figma built a custom multiplayer system (CRDT-inspired) over WebSockets, so cursor moves and edits appear within milliseconds.

**Hotstar / JioCinema** — live scorecards and "key moments" update for tens of millions of viewers through aggregation and CDN-friendly distribution rather than per-user sockets.

**Zerodha / Groww** — market data is streamed over WebSocket in binary to traders at market open. Order updates are pushed in real time, and latency is critical.

**Facebook Messenger** — used MQTT for its mobile apps to reduce battery and data use on poor networks.

## 🟡 Real Example Hindi में
Uber/Ola में ड्राइवर का GPS हर कुछ सेकंड में Kafka pipeline से होकर Redis जैसी तेज़ जगह जाता है, फिर यात्री के ऐप तक; H3 grid से पास के ड्राइवर तुरंत मिलते हैं।
Google Docs और Figma में कई लोगों के बदलाव milliseconds में मिल जाते हैं (OT/CRDT)। Facebook Messenger ने बैटरी बचाने के लिए MQTT इस्तेमाल किया।

---

## 🟠 My Stack Example

### Rider location ingest + fan-out (Node)
```js
// Rider app → POST /rider/locations (batched every 3 s) or MQTT
app.post('/api/v1/rider/locations', authenticateRider, async (req, res) => {
  const points = req.body.points;                              // [{lat,lng,ts,speed}]
  const last = points.at(-1);
  await redis.multi()
    .geoAdd('riders:active', { longitude: last.lng, latitude: last.lat, member: `r:${req.rider.id}` })
    .hSet(`rider:${req.rider.id}`, { lat: last.lat, lng: last.lng, ts: last.ts, speed: last.speed })
    .exec();
  await producer.send({ topic: 'rider-locations', messages: points.map((p) => ({ key: String(req.rider.id), value: JSON.stringify(p) })) });
  const orderId = await redis.get(`rider:${req.rider.id}:active_order`);
  if (orderId) {
    const custId = await redis.get(`order:${orderId}:customer`);
    emitter.to(`user:${custId}`).emit('order:location', { orderId, lat: last.lat, lng: last.lng, ts: last.ts });
  }
  res.status(202).end();
});
// History: a Kafka consumer batches 'rider-locations' into Cassandra/S3 for analytics & disputes
```

### Client: drop stale updates, animate smoothly (React Native)
```tsx
const lastTs = useRef(0);
useEffect(() => socket.on('order:location', (p) => {
  if (p.ts <= lastTs.current) return;                          // out-of-order → ignore
  lastTs.current = p.ts;
  markerRef.current?.animateMarkerToCoordinate({ latitude: p.lat, longitude: p.lng }, 2500);  // react-native-maps
}), []);
```

### Adaptive location frequency (RN, battery-aware)
```ts
// expo-location: more frequent while moving fast, less when stopped
await Location.startLocationUpdatesAsync(TASK, {
  accuracy: Location.Accuracy.High,
  timeInterval: speed > 5 ? 3000 : 15000,
  distanceInterval: 20,                 // meters
  foregroundService: { notificationTitle: 'Delivering order', notificationBody: 'Sharing live location' },
});
```

### Typing indicator: throttled and ephemeral
```ts
const sendTyping = throttle(() => socket.emit('typing', { conversationId }), 3000);
// server: relay to other members only; never persist; clients auto-hide after 5 s
```

### SSE for a live dashboard (Next.js route handler)
```ts
export async function GET() {
  const stream = new ReadableStream({
    async start(controller) {
      const send = (d: unknown) => controller.enqueue(`data: ${JSON.stringify(d)}\n\n`);
      const sub = redis.duplicate(); await sub.connect();
      await sub.subscribe('dashboard:orders', (msg) => send(JSON.parse(msg)));   // pre-aggregated snapshots
    },
  });
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' } });
}
```

### FastAPI SSE (live order status)
```python
from sse_starlette.sse import EventSourceResponse

@app.get("/orders/{oid}/events")
async def order_events(oid: int, user=Depends(current_user)):
    async def gen():
        pubsub = r.pubsub(); await pubsub.subscribe(f"order:{oid}")
        async for m in pubsub.listen():
            if m["type"] == "message":
                yield {"event": "status", "data": m["data"]}
    return EventSourceResponse(gen())
```

### Collaborative editing (Yjs + WebSocket)
```ts
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
const doc = new Y.Doc();
const provider = new WebsocketProvider('wss://collab.myapp.com', `doc-${docId}`, doc);
const text = doc.getText('content');      // CRDT text: concurrent edits merge automatically
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you choose between polling, SSE, WebSockets and push notifications?**
A1: Start from the latency need, direction and client state. Infrequent updates (minutes) suit short polling. Server-to-client streams (notifications, scores, dashboards, LLM tokens) suit SSE: simple, works over plain HTTP, reconnects automatically. Bidirectional, high-frequency interaction (chat, typing, multiplayer, collaboration, trading) suits WebSockets, or MQTT for constrained devices and networks. Use push notifications when the app is backgrounded or closed, and WebRTC for audio and video. Keep fallbacks (WebSocket to SSE to polling).

**Q2: Design live delivery-partner tracking for a food app.**
A2: The rider app sends GPS points every 2–5 s (adaptive by speed, batched, over HTTP or MQTT) to an ingest service, which updates the latest position in Redis (geo plus hash) and appends points to Kafka for history and analytics (batched to Cassandra or S3). A tracking service map-matches the points and computes the ETA. The update is published to the customer's channel, and the WebSocket gateway pushes it to the app, which ignores out-of-order points and animates the marker. If the customer app is in the background, send only milestone push notifications. Under load, reduce frequency and coalesce updates.

**Q3: How do you implement presence ("online", "last seen") at scale?**
A3: Clients send heartbeats over their connection, and the gateway sets a Redis key with a TTL (e.g. 60 s). The user is online while the key exists. Publish changes only on transitions (online/offline), not on every heartbeat, to avoid fan-out storms. Write "last seen" lazily on disconnect. For large contact lists, fetch presence on demand when a chat screen opens rather than pushing it to everyone. Respect privacy settings.

**Q4: How do collaborative editors like Google Docs handle concurrent edits?**
A4: Each user applies edits locally immediately (optimistic) and sends operations to a server or peers. Operational Transformation (Google Docs) transforms concurrent operations against each other so all replicas converge in the same order, usually with a central server ordering operations. CRDTs (Yjs, Automerge, Figma-style approaches) use data structures whose merges are commutative and convergent without a central transform. Both broadcast operations via WebSocket, with snapshots and versioning for persistence and recovery.

**Q5: How do you keep a real-time feature working under massive load (e.g. an IPL final)?**
A5: Reduce per-user work: coalesce and throttle updates (latest-value-wins every 1–2 s), pre-aggregate in streams, and send small deltas. Serve read-only broadcasts through CDN-cacheable endpoints or SSE rather than per-user sockets. Pre-scale gateways and the backplane, shed non-critical real-time features (typing, presence) first, use jittered reconnects, and fall back to polling. Monitor end-to-end latency (event time to render time) as the key SLO.

---

## 🔷 Trade-offs
✅ Advantages:
- Engaging live UX, faster decisions (trading, ops), better trust (tracking).

❌ Disadvantages:
- Stateful connections and streaming infrastructure are complex and costly.
- Battery/data usage on mobile; ordering, duplication and gap handling.
- Harder to test and monitor; needs graceful fallbacks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Soft real-time | Low latency, no hard guarantee | तेज़, पर पक्की गारंटी नहीं |
| Latency budget | Max allowed end-to-end delay | अधिकतम देरी की सीमा |
| SSE | Server-sent events (one-way stream) | सर्वर से एक तरफ़ा stream |
| MQTT | Lightweight pub/sub protocol | हल्का pub/sub प्रोटोकॉल |
| WebRTC | Real-time media P2P | लाइव ऑडियो/वीडियो |
| Presence | Online status tracking | ऑनलाइन स्थिति |
| Coalescing | Merge updates, keep latest | updates मिलाकर latest भेजना |
| OT / CRDT | Concurrent edit merge techniques | साथ-साथ editing मिलाने के तरीके |
| Interpolation | Smooth movement between points | बिंदुओं के बीच smooth चाल |

---

## ⚡ 3-Line Summary
**English:**
1. Real-time = deliver changes within a latency budget; pick the simplest transport that fits (polling → SSE → WebSocket/MQTT → WebRTC; push when backgrounded).
2. Pipeline: ingest → stream → process → hot state (Redis) + durable history → pub/sub fan-out → incremental client rendering.
3. Handle ordering, dedup, resync, backpressure (coalesce), adaptive frequency for mobile, and graceful fallback under load.

**Hindi:**
1. Real-time = तय देरी में बदलाव पहुँचाना; सबसे आसान सही तरीका चुनो (polling → SSE → WebSocket/MQTT → WebRTC; background में push)।
2. Pipeline: ingest → stream → प्रोसेस → Redis (ताज़ा) + DB (इतिहास) → pub/sub → client।
3. क्रम, dedup, resync, updates मिलाना, mobile पर बदलती frequency और भीड़ में fallback।

---

## ➡️ Next Topic Suggestion
**98. Microservices Boundaries** — Before building many real-time and async services, decide where one service ends and another begins. Next: Domain-Driven Design, bounded contexts, and how to split a system the right way.
