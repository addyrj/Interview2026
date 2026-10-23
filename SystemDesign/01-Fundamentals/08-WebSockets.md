# 08. WebSockets
# हिंदी में: WebSocket — क्लाइंट और सर्वर के बीच हमेशा खुला रहने वाला दो-तरफ़ा कनेक्शन, जिससे सर्वर ख़ुद डेटा भेज (push) सकता है

---

## 🔵 Simple Definition (English)
A **WebSocket** is a **persistent, full-duplex** connection between client and server over a single TCP connection. After one HTTP "upgrade" handshake, both sides can send messages **any time**, with very low overhead. Perfect for chat, live tracking, notifications, multiplayer and live dashboards.

## 🔵 सरल परिभाषा (Hindi)
WebSocket एक बार HTTP से शुरू होकर हमेशा खुला रहने वाला कनेक्शन बन जाता है।
इसमें क्लाइंट और सर्वर दोनों कभी भी एक-दूसरे को मैसेज भेज सकते हैं — बार-बार request करने की ज़रूरत नहीं। चैट, लाइव ट्रैकिंग के लिए सबसे अच्छा।

---

## 🔴 Problem it Solves
HTTP is **request-response**: the server can only answer, never start a conversation. For real-time features developers used hacks:

```
Short polling:   every 2s → "any new message?"  "no" "no" "no" "yes!"
                 ❌ wasted requests, battery, server load; up to 2s delay

Long polling:    request hangs open until server has data (or 30s timeout), then reconnect
                 ❌ better, but each message = new HTTP request + headers; complex at scale
```

WebSockets: **one connection, open for hours, server pushes instantly**, with tiny 2–14 byte frame headers instead of ~500–800 byte HTTP headers per message.

## 🔴 यह क्यों बना? (Hindi)
HTTP में सर्वर ख़ुद से कुछ नहीं भेज सकता — क्लाइंट को बार-बार पूछना पड़ता था "कोई नया मैसेज?" (polling), जिससे बैटरी, डेटा और सर्वर की ताक़त बर्बाद होती थी।
WebSocket में कनेक्शन खुला रहता है, और नया डेटा आते ही सर्वर तुरंत भेज देता है।

---

## 🟢 How it Works — Step by Step

### 1. Handshake (HTTP Upgrade)

```
Client → Server
  GET /ws HTTP/1.1
  Host: chat.myapp.com
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Key: dGhlIHNhbXBsZQ==
  Sec-WebSocket-Version: 13

Server → Client
  HTTP/1.1 101 Switching Protocols          ← no longer HTTP after this
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

URL scheme:  ws://  (plain)   wss://  (over TLS — always use this)
```

### 2. Full-duplex messaging

```
   Client                              Server
     │═══════ one TCP connection ════════│
     │ ──── {"type":"join","room":42} ──►│
     │ ◄─── {"type":"msg","text":"hi"} ──│  ← server pushes any time
     │ ──── {"type":"typing"} ─────────► │
     │ ◄─── {"type":"msg","text":"yo"} ──│
     │ ◄─── PING ────────────────────────│  ← heartbeat (keep alive, detect dead)
     │ ──── PONG ──────────────────────► │
     │           ...hours later...       │
     │ ──── CLOSE ─────────────────────► │
```

### 3. Comparison of real-time options

```
┌────────────────┬──────────────┬──────────────┬───────────────┬─────────────────┐
│                │ Short Poll   │ Long Poll    │ SSE           │ WebSocket       │
├────────────────┼──────────────┼──────────────┼───────────────┼─────────────────┤
│ Direction      │ Client pull  │ Client pull  │ Server → Client│ Both ways      │
│ Latency        │ High (interval)│ Low        │ Low           │ Lowest          │
│ Overhead       │ Very high    │ High         │ Low           │ Very low        │
│ Protocol       │ HTTP         │ HTTP         │ HTTP (text/   │ ws:// wss://    │
│                │              │              │ event-stream) │                 │
│ Auto reconnect │ n/a          │ manual       │ Built-in      │ Manual (library)│
│ Binary data    │ yes          │ yes          │ No (text)     │ Yes             │
│ Through proxies│ Easy         │ Easy         │ Easy          │ Needs Upgrade   │
│                │              │              │               │ support         │
│ Use when       │ rare updates │ fallback     │ live feed,    │ chat, games,    │
│                │ (every 5 min)│              │ notifications,│ collaboration,  │
│                │              │              │ LLM streaming │ live location   │
└────────────────┴──────────────┴──────────────┴───────────────┴─────────────────┘
Rule of thumb: server→client only? → SSE is simpler. Both ways, high frequency? → WebSocket.
```

### 4. The scaling problem (preview of Topic 96)

```
User A ── WS ──► Server 1          User B ── WS ──► Server 2
A sends "hi" to B. Server 1 doesn't have B's connection!

Fix: Pub/Sub backplane
   Server 1 ── PUBLISH room:42 "hi" ──► Redis Pub/Sub ──► Server 2 ──► User B

Other concerns:
- Stateful connections → load balancer needs sticky sessions or connection-aware routing
- Each connection = memory + file descriptor  (~10–50 KB each; 1M conns ≈ tens of GB)
- Deploys drop connections → clients must auto-reconnect with backoff + resync missed messages
```

### 5. Reliability rules
```
✓ Heartbeat ping/pong every 25–30s (NAT/LB kill idle connections at ~60s)
✓ Reconnect with exponential backoff + jitter (avoid thundering herd after deploy)
✓ After reconnect: fetch missed messages via REST using "last message id"
✓ Message IDs + ACKs for important events (WS itself doesn't guarantee app-level delivery)
✓ Authenticate during handshake (token in query/cookie/first message), re-check on expiry
```

## 🟢 कैसे काम करता है? (Hindi)
1. क्लाइंट एक HTTP request भेजता है "Upgrade: websocket"; सर्वर 101 Switching Protocols से हाँ कहता है।
2. अब वही TCP कनेक्शन खुला रहता है — दोनों तरफ़ से कभी भी मैसेज जा सकता है।
3. हर कुछ सेकंड में ping/pong होता है ताकि पता रहे कनेक्शन ज़िंदा है।
4. कनेक्शन टूटे तो क्लाइंट दोबारा जुड़ता है और छूटे मैसेज REST से ले लेता है।
5. कई सर्वर हों तो Redis Pub/Sub से मैसेज सही सर्वर तक पहुँचाया जाता है।

---

## 🟡 Real World Example

**Swiggy / Zomato live order tracking**
- When your order is out for delivery, the delivery partner's app sends GPS every few seconds. The backend pushes location updates to your app over a persistent connection (WebSocket/MQTT), and the map pin moves live.

**Slack**
- On launch, the client calls a REST API to get a WebSocket URL, then receives all messages, typing indicators and presence over WebSocket. Slack serves millions of concurrent WebSocket connections via a dedicated "gateway server" layer.

**Zerodha Kite (stock trading)**
- Live stock ticks stream over WebSocket (binary packets for efficiency), with thousands of price updates per second to each trader.

**ChatGPT / Claude web**
- Streaming answers use **SSE** (server → client only), not WebSocket, because the client only needs to receive tokens.

## 🟡 Real Example Hindi में
Swiggy में डिलीवरी बॉय की लोकेशन हर कुछ सेकंड में आपके ऐप तक WebSocket से पहुँचती है, इसलिए मैप पर बाइक चलती दिखती है।
Zerodha Kite में शेयर के दाम WebSocket से हर पल अपडेट होते हैं। ChatGPT जवाब SSE से भेजता है क्योंकि वहाँ सिर्फ़ सर्वर से क्लाइंट की तरफ़ डेटा जाता है।

---

## 🟠 My Stack Example

### Node.js — Socket.IO with Redis adapter (multi-server ready)
```js
import { createServer } from 'http';
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const httpServer = createServer(app);
const io = new Server(httpServer, { cors: { origin: 'https://myapp.com' }, pingInterval: 25000 });

const pub = createClient({ url: process.env.REDIS_URL });
const sub = pub.duplicate();
await Promise.all([pub.connect(), sub.connect()]);
io.adapter(createAdapter(pub, sub));                 // messages reach users on ANY server

io.use(async (socket, next) => {                      // auth at handshake
  try { socket.user = await verifyJwt(socket.handshake.auth.token); next(); }
  catch { next(new Error('unauthorized')); }
});

io.on('connection', (socket) => {
  socket.join(`user:${socket.user.id}`);

  socket.on('track-order', async (orderId) => {
    if (!(await canView(socket.user.id, orderId))) return;
    socket.join(`order:${orderId}`);
  });

  socket.on('chat:send', async (msg, ack) => {
    const saved = await Message.create({ ...msg, from: socket.user.id }); // persist FIRST
    io.to(`room:${msg.roomId}`).emit('chat:new', saved);
    ack({ ok: true, id: saved.id });                  // app-level ACK
  });
});

// Anywhere in your backend (e.g. order service / Kafka consumer):
io.to(`order:${orderId}`).emit('order:location', { lat, lng, eta });

httpServer.listen(3000);
```

### FastAPI — native WebSocket
```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/orders/{order_id}")
async def order_ws(ws: WebSocket, order_id: int):
    user = await auth_from_token(ws.query_params.get("token"))
    await ws.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"order:{order_id}")
    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await ws.send_text(msg["data"])
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"order:{order_id}")
```

### Nginx — must allow Upgrade + long timeouts
```nginx
location /socket.io/ {
  proxy_pass http://api_backend;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 3600s;           # default 60s would kill idle sockets
  proxy_set_header Host $host;
}
# AWS ALB supports WebSockets natively; set idle timeout > ping interval.
```

### React Native client — reconnect + resync
```ts
import { io } from 'socket.io-client';
import { AppState } from 'react-native';

const socket = io('wss://api.myapp.com', {
  auth: { token: await getAccessToken() },
  transports: ['websocket'],              // skip long-polling on mobile
  reconnectionDelay: 1000, reconnectionDelayMax: 10000, randomizationFactor: 0.5, // backoff + jitter
});

socket.on('connect', async () => {
  const missed = await api.get(`/rooms/42/messages?after=${lastMessageId}`); // resync gap
  store.addMany(missed.data);
});
socket.on('chat:new', (m) => store.add(m));

// Mobile: OS kills sockets in background → disconnect & rely on PUSH notifications
AppState.addEventListener('change', (s) => (s === 'active' ? socket.connect() : socket.disconnect()));
```

> 📱 **Mobile truth:** iOS/Android suspend your app in background; WebSockets die. Real apps use WebSocket **in foreground** and **push notifications (FCM/APNs)** in background (Topic M10).

### Next.js — note
Vercel serverless functions **can't hold WebSockets**. Use a separate Node server (EC2/ECS/Fly), or managed services (Pusher, Ably, AWS API Gateway WebSocket, Supabase Realtime). SSE works in Next.js route handlers for one-way streams.

---

## ⚫ Interview Questions + Answers

**Q1: How does a WebSocket connection get established?**
A1: The client sends an HTTP/1.1 GET with `Upgrade: websocket`, `Connection: Upgrade` and a random `Sec-WebSocket-Key`. The server replies `101 Switching Protocols` with `Sec-WebSocket-Accept` (a hash of the key) to prove it understood. From then on, the same TCP connection carries WebSocket frames in both directions. Use `wss://` (over TLS) in production.

**Q2: WebSocket vs SSE vs long polling — how do you choose?**
A2: SSE when only the server pushes (notifications, live scores, LLM token streaming): it's simple, works over normal HTTP, and reconnects automatically. WebSocket when you need bidirectional, low-latency, high-frequency messages (chat, multiplayer, collaborative editing, live location). Long polling is mainly a fallback for restrictive networks. Short polling is fine for rare updates (every minute or more).

**Q3: How do you scale WebSockets to millions of users across many servers?**
A3: Connections are stateful, so: (1) a connection/gateway tier of servers whose only job is to hold sockets; (2) a pub/sub backplane (Redis Pub/Sub, Kafka, NATS) so any service can publish to a user/room and the gateway holding that socket delivers it; (3) a presence registry (Redis: userId → gateway node); (4) a load balancer that supports Upgrade, with sticky sessions if needed; (5) tuned OS limits (file descriptors, memory), heartbeats, and graceful drain on deploy with client reconnect and jitter.

**Q4: What happens if a WebSocket disconnects in the middle of a chat? How do you avoid losing messages?**
A4: WebSocket gives no application-level delivery guarantee. Persist every message in the DB before fanning it out, give each a sequential ID per conversation, and have the client ACK. On reconnect, the client sends its last received ID and fetches missed messages via REST (or the server replays them). The client also retries unsent messages with a client-generated ID, so the server de-duplicates (idempotency).

**Q5: Why might WebSockets not work well for a mobile app in the background?**
A5: iOS and Android suspend background apps and kill network sockets to save battery, and mobile networks drop idle connections. So WebSockets are used only while the app is in the foreground. In the background, the server sends push notifications via FCM/APNs, and when the app reopens it reconnects and syncs. Heartbeats need to be tuned for mobile networks too.

---

## 🔷 Trade-offs
✅ Advantages:
- Real-time, bidirectional, very low latency and per-message overhead.
- Server push → no wasteful polling; saves bandwidth & battery when active.
- Supports binary (efficient for games/trading).

❌ Disadvantages:
- Stateful → harder to scale, load balance, and deploy (connection draining).
- Need your own reconnect, heartbeat, auth refresh, message ordering/ACK logic.
- Some proxies/firewalls block it; serverless platforms often don't support it.
- Background mobile apps can't keep it alive.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Full-duplex | Both sides send at the same time | दोनों तरफ़ एक साथ बातचीत |
| Persistent connection | Stays open for long time | लंबे समय तक खुला कनेक्शन |
| Upgrade (101) | Switch from HTTP to WebSocket | HTTP से WebSocket में बदलना |
| Polling | Client repeatedly asks for updates | बार-बार पूछना |
| SSE | One-way server push over HTTP | सर्वर से एक तरफ़ा स्ट्रीम |
| Heartbeat (ping/pong) | Keep-alive check | कनेक्शन ज़िंदा है या नहीं, जाँच |
| Pub/Sub | Publish/subscribe message bus | संदेश प्रसारण प्रणाली |
| Sticky session | Same client → same server | एक यूज़र हमेशा एक ही सर्वर पर |
| Backoff + Jitter | Spread out reconnect attempts | दोबारा जुड़ने में धीरे-धीरे देरी |

---

## ⚡ 3-Line Summary
**English:**
1. WebSocket = one HTTP upgrade → persistent, two-way connection; server can push instantly.
2. Use for chat, live tracking, trading, collaboration; use SSE for one-way streams.
3. Scaling needs pub/sub (Redis), heartbeats, reconnect + resync; mobile background needs push notifications.

**Hindi:**
1. WebSocket = एक बार upgrade, फिर हमेशा खुला दो-तरफ़ा कनेक्शन।
2. चैट, लाइव ट्रैकिंग के लिए WebSocket; सिर्फ़ सर्वर से भेजना हो तो SSE।
3. स्केल के लिए Redis Pub/Sub, reconnect और resync; मोबाइल background में push notification।

---

## ➡️ Next Topic Suggestion
**09. Client-Server Architecture** — You now know the protocols (HTTP, WebSocket). Next: zoom out to the architecture pattern itself — thin vs thick clients, 2-tier vs 3-tier vs n-tier, and how web and mobile clients fit in.
