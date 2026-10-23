# 96. WebSocket at Scale
# हिंदी में: WebSocket at Scale — लाखों-करोड़ों users के हमेशा खुले WebSocket कनेक्शन कई सर्वरों पर संभालना, और किसी भी user तक सही सर्वर से तुरंत message पहुँचाना

---

## 🔵 Simple Definition (English)
Scaling WebSockets means supporting **millions of concurrent, long-lived connections** across many servers and delivering messages to the right user or room **in real time**. The key ideas:
1. A dedicated, horizontally scaled **connection (gateway) tier** that only holds sockets.
2. A **pub/sub backplane** (Redis, Kafka, NATS) so any backend service can publish to any user, wherever their socket lives.
3. A **presence/routing registry** (userId → gateway node).
4. Robust **heartbeats, reconnect, resync and graceful deploys**.

## 🔵 सरल परिभाषा (Hindi)
लाखों users के WebSocket कनेक्शन हमेशा खुले रहते हैं और अलग-अलग सर्वरों पर बँटे होते हैं। किसी user को message भेजना हो तो पता होना चाहिए कि उसका कनेक्शन किस सर्वर पर है।
इसके लिए: सिर्फ़ कनेक्शन रखने वाले gateway सर्वर, सबको जोड़ने वाला pub/sub (Redis/Kafka), और "कौन user किस सर्वर पर" वाली registry।

---

## 🔴 Problem it Solves
A single WebSocket server works for a demo. At scale:
- **Memory and file-descriptor limits:** each connection costs memory (roughly 10–50 KB or more) and a file descriptor, so one server holds maybe 50k–500k connections.
- **Routing:** user A is on server 1 and messages user B on server 7. Server 1 doesn't have B's socket.
- **Fan-out:** a message to a group of 100,000 members (a live sports channel) must reach sockets on hundreds of servers.
- **Stateful connections** make **deploys, autoscaling and load balancing** hard. Restarting a server drops 100k users, who then all reconnect at once (thundering herd).
- **Mobile realities:** flaky networks, background suspension, and NAT timeouts that silently kill idle connections.

## 🔴 यह क्यों बना? (Hindi)
एक सर्वर पर demo चलता है, पर स्केल पर: हर कनेक्शन memory लेता है, A किसी और सर्वर पर और B किसी और पर, एक group में 1 लाख members तक message पहुँचाना, deploy पर 1 लाख users का एक साथ reconnect, और mobile नेटवर्क की दिक़्क़तें।
WebSocket at scale इन सबका ढाँचा है।

---

## 🟢 How it Works — Step by Step

### Architecture

```
  📱📱📱 millions of clients (wss://rt.myapp.com)
         │  L4/L7 LB (supports Upgrade; long idle timeouts; least-connections)
 ┌───────┴──────────────┬───────────────────────┬──────────────────────┐
 ▼                      ▼                       ▼                      ▼
Gateway-1            Gateway-2               Gateway-3             Gateway-N     ← stateless logic,
(250k sockets)       (250k sockets)          (250k)                (250k)          stateful sockets
 │  register: user:42 → gw-2 (Redis presence, TTL heartbeat)
 │  subscribe: channels of its connected users
 └──────────────┬───────┴───────────────────────┴──────────────────────┘
                ▼
      PUB/SUB BACKPLANE (Redis Pub/Sub / Redis Streams / Kafka / NATS)
                ▲
 ┌──────────────┴──────────────────────────────────────────────┐
 │ Backend services: chat, order tracking, notifications ...    │
 │ publish("user:42", msg) or publish("room:ipl-final", msg)    │
 └─────────────────────────────────────────────────────────────┘
```

### Delivery flow (user-to-user chat)
```
1. A sends {to: B, text} over the socket to gw-1
2. gw-1 → chat service (HTTP/gRPC/queue): validate, PERSIST the message (DB), assign msgId/seq
3. Chat service publishes to channel "user:B" (or looks up presence B → gw-7 and sends directly)
4. gw-7 (subscribed to user:B) pushes the frame to B's socket
5. B's client ACKs; if B is offline → push notification (FCM/APNs) + delivery on next sync
```

### Fan-out strategies for groups and rooms
```
Small rooms (up to a few thousand): publish once to "room:X"; every gateway with members subscribes
   and forwards to its local members.
Huge broadcasts (a live score to 5M): fan out hierarchically; push to gateways via a Kafka topic;
   gateways send to local sockets; coalesce updates (send the latest score every 1 s, not every event);
   consider SSE or HTTP polling behind a CDN for read-only broadcasts.
Avoid: per-user DB lookups during fan-out; N×M publishes.
```

### Connection management
```
Heartbeats:     ping/pong every 20–30 s (below LB/NAT idle timeouts, typically 60 s)
Auth:           token at handshake; re-authenticate or close when the token expires
Backpressure:   limit each socket's send buffer; drop or close slow consumers
Message order:  per-conversation sequence numbers; the client reorders and dedupes
Resync:         on reconnect the client sends lastSeq → server returns missed messages (from DB/stream)
Presence:       Redis key presence:user:42 with a TTL renewed by heartbeat; "last seen"
```

### Deploys and autoscaling (the stateful pain)
```
- Graceful drain: stop accepting new sockets, disconnect clients in batches over minutes
  (not all at once), then shut down
- Clients reconnect with exponential backoff + JITTER (Topic 75) → no thundering herd
- Autoscale on connections per node (not CPU alone); scale in slowly
- LB: least-connections; sticky sessions only needed for long-polling fallbacks
```

### Capacity math (back-of-envelope)
```
10M concurrent users ÷ 250k sockets per gateway = 40 gateways (+30% headroom ≈ 52)
Memory: 250k × 30 KB ≈ 7.5 GB per gateway (plus buffers)
Messages: 10M users × 1 msg/min ≈ 170k msgs/s inbound; outbound depends on group sizes
OS tuning: file descriptors ≥ 1M, TCP memory settings, ephemeral port range, epoll-based server
```

### Alternatives and managed options
```
Managed: AWS API Gateway WebSocket APIs, Ably, Pusher, PubNub, Firebase, Supabase Realtime
Protocols: MQTT (IoT and battery-friendly mobile; Facebook Messenger used it), SSE for one-way,
           WebTransport (emerging)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Gateway सर्वर सिर्फ़ WebSocket कनेक्शन रखते हैं (हर एक पर ~2.5 लाख); LB उन्हें बाँटता है।
2. हर gateway Redis में लिखता है "user:42 → gw-2" और अपने users के channels subscribe करता है।
3. Backend service (chat, order tracking) पहले message DB में सेव करती है, फिर pub/sub पर `user:B` channel में publish करती है; B वाला gateway उसे B तक पहुँचाता है।
4. Heartbeat (25-30 सेकंड), reconnect पर `lastSeq` से छूटे messages, offline user को push notification।
5. Deploy पर धीरे-धीरे drain करो, clients random देरी (jitter) से reconnect करें; बहुत बड़े broadcast में updates को मिलाकर (हर सेकंड latest) भेजो।

---

## 🟡 Real World Example

**WhatsApp** — famously held 2 million+ concurrent TCP connections per server using Erlang and FreeBSD tuning. Messages are routed between servers, stored until delivered, and then deleted from the servers.

**Slack** — runs a dedicated tier of gateway servers that hold WebSocket connections, plus "channel servers" that keep channel state and fan out messages to the gateways, using consistent hashing to map channels to servers. Slack engineering has written about reconnect storms and how they fixed them.

**Discord** — Elixir (BEAM) gateway servers handle millions of concurrent connections, and guild processes are spread across nodes with consistent hashing. Very large servers (millions of members) needed special fan-out optimizations (relays).

**Zerodha Kite ticker** — streams market ticks over WebSocket in a compact binary format to many concurrent traders at market open, with a per-connection list of subscribed instruments.

**Swiggy/Zomato tracking** — delivery partner location updates are published and fanned out to the customer's socket (or polled) every few seconds, with throttling and coalescing.

## 🟡 Real Example Hindi में
WhatsApp एक सर्वर पर 20 लाख से ज़्यादा कनेक्शन संभालता था (Erlang)। Slack के पास अलग gateway सर्वर और channel सर्वर हैं, और उन्होंने reconnect storms की समस्या भी हल की।
Discord लाखों कनेक्शन Elixir से संभालता है; Zerodha Kite बाज़ार खुलते ही हज़ारों traders को binary ticks भेजता है।

---

## 🟠 My Stack Example

### Gateway with Socket.IO + Redis adapter + presence (Node)
```js
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-streams-adapter';   // survives brief disconnects

const io = new Server(httpServer, {
  transports: ['websocket'], pingInterval: 25_000, pingTimeout: 20_000,
  maxHttpBufferSize: 64 * 1024,
  connectionStateRecovery: { maxDisconnectionDuration: 2 * 60_000 },     // resend missed packets
});
io.adapter(createAdapter(redis));

io.use(async (socket, next) => {
  try { socket.data.user = await verifyJwt(socket.handshake.auth.token); next(); }
  catch { next(new Error('UNAUTHORIZED')); }
});

io.on('connection', async (socket) => {
  const uid = socket.data.user.id;
  socket.join(`user:${uid}`);
  await redis.set(`presence:${uid}`, process.env.HOSTNAME, { EX: 60 });
  const hb = setInterval(() => redis.expire(`presence:${uid}`, 60), 30_000);

  socket.on('resync', async ({ conversationId, lastSeq }, ack) => {
    ack(await messages.after(conversationId, lastSeq, 200));            // fill gaps after reconnect
  });
  socket.on('disconnect', () => { clearInterval(hb); redis.del(`presence:${uid}`); });
});

// Graceful drain on SIGTERM: disconnect clients in batches so they spread over other gateways
process.on('SIGTERM', async () => {
  const sockets = await io.local.fetchSockets();
  for (let i = 0; i < sockets.length; i += 1000) {
    sockets.slice(i, i + 1000).forEach((s) => s.disconnect(true));
    await sleep(1000);
  }
  process.exit(0);
});
```

### Backend services publish without holding sockets (Socket.IO emitter)
```js
import { Emitter } from '@socket.io/redis-emitter';
const emitter = new Emitter(redis);
// order-tracking service, any instance:
emitter.to(`user:${order.userId}`).emit('order:location', { lat, lng, etaMin });
```

### Chat send path (persist first, then fan out)
```js
socket.on('chat:send', async ({ conversationId, clientMsgId, text }, ack) => {
  const msg = await messages.insertIdempotent({ conversationId, clientMsgId, from: uid, text });  // assigns seq
  const members = await conversations.members(conversationId);
  for (const m of members) emitter.to(`user:${m}`).emit('chat:new', msg);
  const offline = await offlineMembers(members);               // presence check
  if (offline.length) await pushQueue.add('push', { userIds: offline, msgId: msg.id });
  ack({ ok: true, seq: msg.seq });
});
```

### Nginx / ALB settings
```nginx
location /socket.io/ {
  proxy_pass http://gateways;          # upstream with least_conn
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 3600s;
}
# AWS ALB: idle timeout ≥ 60 s and longer than the ping interval; NLB for very high connection counts
```

### OS tuning (Linux gateway hosts / containers)
```bash
ulimit -n 1048576
sysctl -w net.core.somaxconn=65535 net.ipv4.ip_local_port_range="1024 65535" fs.file-max=2097152
```

### React Native client
```ts
const socket = io(RT_URL, {
  transports: ['websocket'],
  auth: async (cb) => cb({ token: await getAccessToken() }),
  reconnectionDelay: 1000, reconnectionDelayMax: 30_000, randomizationFactor: 0.5,
});
socket.on('connect', () =>
  socket.emit('resync', { conversationId, lastSeq: store.lastSeq(conversationId) }, store.merge));
// Background → disconnect and rely on push notifications; foreground → reconnect
AppState.addEventListener('change', (s) => (s === 'active' ? socket.connect() : socket.disconnect()));
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you scale WebSockets to millions of users?**
A1: Use a horizontally scaled gateway tier dedicated to holding connections, tuned for file descriptors and memory and built on an event loop, behind load balancers that support Upgrade and long idle timeouts. Keep business logic in backend services. Use a pub/sub backplane (Redis, Kafka, NATS) so any service can publish to user or room channels and whichever gateway holds the socket delivers it. Keep a presence registry (userId to gateway) with TTL heartbeats. Handle reconnects with resync, graceful drains and jittered backoff, and autoscale on connection count.

**Q2: How does a message reach a user connected to a different server?**
A2: The send path persists the message, then publishes it on the backplane to a channel keyed by the recipient (`user:B`) or the room. The gateway holding B's socket is subscribed to that channel and pushes the message down. At very large scale, a presence lookup finds B's gateway and the message is sent to that node directly, which is cheaper. If B is offline, a push notification goes out instead and the message is delivered on the next sync.

**Q3: How do you avoid losing messages when connections drop?**
A3: Persist messages before fanning them out, with per-conversation sequence numbers. Clients ACK what they receive and track the last sequence number. On reconnect, they request messages after `lastSeq`, resyncing from the DB or stream. Senders retry with client-generated IDs, so inserts are idempotent. Offline users get push notifications. For short disconnects, Socket.IO's connection-state recovery or a Redis Streams adapter helps.

**Q4: What happens during a deploy of WebSocket gateways, and how do you make it smooth?**
A4: Every socket on a restarting node disconnects. If all those clients reconnect instantly, the remaining nodes face a thundering herd. To smooth it: roll the deploy a few nodes at a time, drain gracefully (stop accepting new sockets and disconnect clients in batches over time, optionally with a "reconnect" hint), have clients use exponential backoff with jitter, keep spare capacity, and resync so nobody misses messages.

**Q5: How would you broadcast live cricket scores to 10 million users?**
A5: Don't push every event to every socket from one place. Publish score updates to a topic that all gateways consume (Kafka or NATS), shard by match, and have each gateway push to its own subscribers. Coalesce updates (send the latest state every 1–2 s with small deltas) and keep messages tiny. Viewers who only read can use SSE or poll a CDN-cached JSON every few seconds, which the CDN scales cheaply. Apps in the background get push notifications only for key events, such as wickets.

---

## 🔷 Trade-offs
✅ Advantages:
- True real-time push with low per-message overhead in both directions; scales horizontally with gateways and pub/sub.

❌ Disadvantages:
- Stateful connections complicate deploys, load balancing and autoscaling, and cause reconnect storms.
- Needs infrastructure for presence, the backplane, resync, ordering and push fallback.
- Mobile apps lose sockets in the background, and some corporate proxies block WebSockets (fallbacks needed).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Gateway / connection server | Holds client sockets | कनेक्शन रखने वाला सर्वर |
| Backplane | Pub/sub linking servers | सर्वरों को जोड़ने वाला pub/sub |
| Presence | Who's online and where | कौन ऑनलाइन, किस सर्वर पर |
| Fan-out | Delivering to many recipients | कई लोगों तक भेजना |
| Heartbeat | Keep-alive ping/pong | ज़िंदा होने की जाँच |
| Resync | Fetch missed messages after reconnect | छूटे messages लेना |
| Sequence number | Order within a conversation | बातचीत में क्रम संख्या |
| Graceful drain | Move clients off before shutdown | बंद करने से पहले clients हटाना |
| Reconnect storm | Mass simultaneous reconnects | एक साथ reconnect की भीड़ |
| Coalescing | Merging frequent updates | बार-बार के updates को मिलाना |

---

## ⚡ 3-Line Summary
**English:**
1. Scale WebSockets with a dedicated gateway tier, a pub/sub backplane and a presence registry: backend services publish, gateways deliver.
2. Persist, then fan out, with sequence numbers, ACKs and resync; send push notifications to offline users.
3. Keep heartbeats below idle timeouts, jitter reconnects, drain gracefully, autoscale on connections, and coalesce huge broadcasts.

**Hindi:**
1. Gateway सर्वर + pub/sub + presence registry; services publish करती हैं, gateways पहुँचाते हैं।
2. पहले सेव, फिर भेजो; sequence नंबर, ACK, resync; offline को push notification।
3. Heartbeat, jitter वाला reconnect, धीरे-धीरे drain, कनेक्शन के हिसाब से autoscale।

---

## ➡️ Next Topic Suggestion
**97. Real-Time Systems** — WebSockets are one tool. Next: designing real-time features in general (live tracking, presence, typing indicators, live dashboards, collaborative editing), choosing between polling, SSE, WebSockets, MQTT and WebRTC, and setting latency budgets.
