# F13. Real-Time on Frontend (Polling vs SSE vs WebSocket)
# हिंदी में: Frontend पर Real-Time — बिना refresh के नया डेटा स्क्रीन पर लाना: बार-बार पूछना (Polling), सर्वर का एक-तरफ़ा stream (SSE), या दोनों तरफ़ खुला कनेक्शन (WebSocket) — और टूटने पर दोबारा जुड़ना

---

## 🔵 Simple Definition (English)
Ways for a client to get **live updates** from the server:
- **Short polling**: the client asks every N seconds (`GET /orders/123`). Simple, but wasteful and delayed.
- **Long polling**: the client asks, the server **holds the request open** until there's news (or a timeout), then the client immediately asks again.
- **Server-Sent Events (SSE)**: one long-lived HTTP response where the **server streams events** (`text/event-stream`) to the client. **One-way (server → client)**, auto-reconnect built into `EventSource`, works over HTTP/2. Also used to stream AI/LLM tokens.
- **WebSocket**: a **full-duplex**, persistent connection (upgraded from HTTP) for **two-way, low-latency** messaging: chat, multiplayer, collaborative editing, live location.
- (Also **WebRTC** for peer-to-peer audio/video/data, and **push notifications** when the app is closed — M10.)
On the frontend, the challenges are **reconnects, missed messages, ordering, dedupe, battery/data use, and syncing with cached state**.

## 🔵 सरल परिभाषा (Hindi)
Live updates के तरीके: Short polling — हर कुछ सेकंड पूछो; Long polling — पूछो, सर्वर तब तक रोके रखे जब तक नई ख़बर न हो; SSE — सर्वर एक खुले HTTP कनेक्शन पर लगातार events भेजता है (सिर्फ़ सर्वर → client, अपने-आप reconnect, AI के जवाब stream करने में भी); WebSocket — दोनों तरफ़ से हमेशा खुला तेज़ कनेक्शन (chat, game, live location)।
Frontend की असली चुनौती: टूटने पर दोबारा जुड़ना, छूटे messages, क्रम, duplicate हटाना, battery/data बचाना, और cache के साथ मेल।

---

## 🔴 Problem it Solves
HTTP is request-response: the server **can't talk first**. But users expect:
- Chat messages appearing instantly (WhatsApp Web).
- Order status and rider location updating live (Swiggy/Zomato/Uber).
- Live cricket scores (Cricbuzz, Hotstar), stock prices (Zerodha Kite), notification badges.
- Collaborative cursors and edits (Google Docs, Figma).
- Streaming AI responses token by token (ChatGPT-style UIs).

Refreshing manually or polling every second **wastes battery, data and server capacity**. Choosing the right real-time transport and handling its failure modes is a core frontend design skill.

## 🔴 यह क्यों बना? (Hindi)
HTTP में client पूछता है तभी सर्वर बोलता है — सर्वर पहले नहीं बोल सकता। पर यूज़र चाहते हैं: chat तुरंत आए, order/rider location live बदले, live score और stock prices, Google Docs में साथ में editing, AI जवाब शब्द-दर-शब्द।
हर सेकंड polling से battery, data और सर्वर बर्बाद; इसलिए सही तरीका चुनना और कनेक्शन टूटने की स्थितियाँ संभालना ज़रूरी।

---

## 🟢 How it Works — Step by Step

### Transports side by side

```
Short polling   C ──GET──► S  (no news)   C ──GET──► S (no news)   C ──GET──► S (news!)
                latency up to interval; most requests empty

Long polling    C ──GET──────────────(held)──────────────► S responds when news/timeout
                C ──GET again immediately ...               near real-time over plain HTTP

SSE             C ──GET /events (Accept: text/event-stream)──► S
                ◄── event: order.updated  data: {...}
                ◄── event: order.updated  data: {...}  (one response, streamed forever)
                Browser EventSource auto-reconnects and sends Last-Event-ID

WebSocket       C ──HTTP Upgrade: websocket──► S  (101 Switching Protocols)
                ◄════════ full duplex frames both ways ════════►
                you implement heartbeat, reconnect, resume, acks
```

### Decision table

```
┌────────────────┬───────────────┬───────────────┬─────────────────┬────────────────────┐
│                │ Short polling │ Long polling  │ SSE             │ WebSocket          │
├────────────────┼───────────────┼───────────────┼─────────────────┼────────────────────┤
│ Direction      │ C→S pull      │ C→S pull      │ S→C push        │ Both ways          │
│ Latency        │ ≤ interval    │ Low           │ Low             │ Lowest             │
│ Complexity     │ Very low      │ Medium        │ Low             │ Higher             │
│ Reconnect      │ N/A           │ Manual        │ Built-in        │ Manual             │
│ Proxies/CDN    │ Works always  │ Usually       │ Works (HTTP)    │ Needs WS support   │
│ Binary data    │ Yes           │ Yes           │ Text only       │ Yes                │
│ Server cost    │ Many requests │ Held conns    │ Held conns      │ Held conns + state │
│ Use for        │ Low-frequency │ Fallback      │ Notifications,  │ Chat, games,       │
│                │ (every 30 s), │ (old infra)   │ feeds, scores,  │ collab editing,    │
│                │ admin jobs    │               │ order status,   │ live location,     │
│                │               │               │ LLM streaming   │ typing indicators  │
└────────────────┴───────────────┴───────────────┴─────────────────┴────────────────────┘
Rule of thumb: server→client only? SSE. Two-way, high-frequency? WebSocket. Rare updates? Polling.
```

### Reliable client connection (the part interviewers probe)

```
1. Connect after auth (token in first message or short-lived ticket in URL; not long-lived JWT in URL logs)
2. Heartbeat: ping/pong every ~25 s → detect dead connections (mobile networks drop silently)
3. Reconnect with exponential backoff + jitter (1s, 2s, 4s … max 30s) → avoid thundering herd after outage
4. Resume: send last received event id / sequence number → server replays missed events
   (or client refetches state via REST after reconnect: "sync on reconnect")
5. Dedupe & order: events carry id + sequence; ignore already-applied ids; buffer out-of-order
6. Visibility & network aware: pause/close when tab hidden or app backgrounded; reconnect on
   'online' / AppState 'active'; fall back to polling if WS blocked
7. Update the cache, not random component state: socket event → queryClient.setQueryData(...)
8. Show connection status ("Reconnecting…") and pending/failed states for outgoing messages
```

### Message flow for chat (client view)

```
User sends "Hi" → generate clientMsgId → show bubble with ⏱ (optimistic) → ws.send({type:'msg', clientMsgId, ...})
Server ack {clientMsgId, serverId, seq} → bubble ✓ (sent); delivery receipt ✓✓; read receipt (blue)
No ack in 10 s → retry (same clientMsgId → server dedupes) → after N failures mark ❗ "Tap to retry"
Incoming msg → if seq > lastSeq+1 → gap → fetch missing range via REST
```

### Scaling notes (frontend-relevant)

```
- One shared connection per app/tab (multiplex topics), not one per component
- Multiple tabs: share via BroadcastChannel / SharedWorker, or accept N connections
- Subscribe only to what's on screen (order:123, chat:abc); unsubscribe on unmount
- Throttle UI updates for high-frequency streams (stock ticks → render at most every 250 ms)
Backend side: sticky sessions or pub/sub fan-out (Redis), connection gateways (Topic 95)
```

## 🟢 कैसे काम करता है? (Hindi)
1. सिर्फ़ सर्वर से client (score, order status, notification, AI stream) → SSE; दोनों तरफ़, बार-बार (chat, game, live location) → WebSocket; कभी-कभार (हर 30 सेकंड) → polling।
2. कनेक्शन मज़बूत बनाओ: login के बाद जुड़ो, हर ~25 सेकंड heartbeat, टूटने पर backoff + jitter से दोबारा जुड़ो।
3. दोबारा जुड़ने पर आख़िरी event id/sequence भेजो ताकि छूटे events मिलें, या REST से ताज़ा state ले लो; id से duplicate हटाओ, sequence से क्रम।
4. Socket event से सीधे query cache update करो (setQueryData), ताकि हर जगह वही डेटा दिखे; tab छुपने/ऐप background पर कनेक्शन रोको।
5. Chat: clientMsgId के साथ भेजो, पहले ⏱ दिखाओ, ack पर ✓, न आए तो उसी id से retry (सर्वर duplicate हटाएगा); ऐप में एक ही shared कनेक्शन।

---

## 🟡 Real World Example

**WhatsApp Web / Slack / Discord** — persistent WebSocket connections carry messages, typing indicators and presence. Clients reconnect with backoff and resync missed messages using sequence numbers or cursors.

**Swiggy / Zomato / Uber order tracking** — rider location and status updates come over WebSocket/MQTT-style channels or SSE, with polling fallback. The map marker is interpolated smoothly between updates.

**Cricbuzz / Hotstar live scores** — server push (SSE or WebSocket) or short polling with CDN-cached score endpoints. For tens of millions of viewers, polling a CDN-cached JSON every few seconds is often cheaper and more robust than millions of open sockets.

**ChatGPT / Claude.ai UIs** — stream LLM tokens using SSE-style streaming over HTTP (`text/event-stream`), rendering text as it arrives (Topic 151).

**Zerodha Kite** — streams market ticks over WebSocket (binary packets for efficiency), and the UI throttles rendering of fast-changing prices.

## 🟡 Real Example Hindi में
WhatsApp Web/Slack में WebSocket से messages, typing और online status — टूटने पर backoff से जुड़ना और sequence से छूटे messages लाना।
Swiggy/Zomato में rider की location WebSocket/SSE से (polling fallback के साथ); Cricbuzz/Hotstar के करोड़ों दर्शकों के लिए कई बार CDN-cached score JSON की polling सस्ती पड़ती है; ChatGPT जैसे UI SSE से शब्द-दर-शब्द जवाब दिखाते हैं; Zerodha Kite WebSocket पर binary ticks।

---

## 🟠 My Stack Example

### SSE on the server (FastAPI) + client (React) for order status
```python
# FastAPI
from fastapi.responses import StreamingResponse
import asyncio, json

@app.get("/orders/{order_id}/events")
async def order_events(order_id: str, request: Request, user=Depends(auth)):
    async def stream():
        last_id = request.headers.get("last-event-id")
        async for evt in subscribe_order_updates(order_id, after=last_id):   # Redis pub/sub or stream
            if await request.is_disconnected(): break
            yield f"id: {evt['seq']}\nevent: order.updated\ndata: {json.dumps(evt)}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})  # disable nginx buffering
```
```tsx
// React hook: SSE → React Query cache
export function useOrderStream(orderId: string) {
  const qc = useQueryClient();
  useEffect(() => {
    const es = new EventSource(`/api/orders/${orderId}/events`, { withCredentials: true });   // cookie auth
    es.addEventListener('order.updated', (e) => {
      const evt = JSON.parse((e as MessageEvent).data);
      qc.setQueryData(['order', orderId], (old: any) => (old && evt.seq <= old.seq ? old : { ...old, ...evt }));  // ignore stale
    });
    es.onerror = () => { /* EventSource retries automatically; show "Reconnecting…" if needed */ };
    return () => es.close();
  }, [orderId, qc]);
}
```

### WebSocket client with heartbeat, backoff, resume, and a shared singleton
```ts
// shared/realtime.ts
type Handler = (data: any) => void;
class Realtime {
  private ws?: WebSocket; private attempts = 0; private lastSeq = 0;
  private handlers = new Map<string, Set<Handler>>(); private heartbeat?: ReturnType<typeof setInterval>;
  private outbox: any[] = []; private stopped = false;

  connect() {
    if (this.ws && this.ws.readyState <= WebSocket.OPEN) return;              // already connecting/open
    this.stopped = false;
    this.ws = new WebSocket(`${WS_URL}?ticket=${getShortLivedTicket()}`);    // ticket valid ~30 s
    this.ws.onopen = () => {
      this.attempts = 0;
      this.ws!.send(JSON.stringify({ type: 'resume', lastSeq: this.lastSeq, topics: [...this.handlers.keys()] }));
      this.outbox.splice(0).forEach((m) => this.ws!.send(JSON.stringify(m)));            // flush queued sends
      this.heartbeat = setInterval(() => this.ws?.send('{"type":"ping"}'), 25_000);
    };
    this.ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === 'pong') return;
      if (msg.seq && msg.seq <= this.lastSeq) return;                 // dedupe
      if (msg.seq) this.lastSeq = msg.seq;
      this.handlers.get(msg.topic)?.forEach((h) => h(msg.data));
    };
    this.ws.onclose = () => {
      clearInterval(this.heartbeat);
      if (this.stopped) return;                                       // closed on purpose (e.g. app backgrounded)
      const delay = Math.min(30_000, 1000 * 2 ** this.attempts++) * (0.5 + Math.random() / 2);  // backoff + jitter
      setTimeout(() => this.connect(), delay);
    };
  }
  close() { this.stopped = true; clearInterval(this.heartbeat); this.ws?.close(); }
  send(msg: any) { this.ws?.readyState === WebSocket.OPEN ? this.ws.send(JSON.stringify(msg)) : this.outbox.push(msg); }
  subscribe(topic: string, h: Handler) {
    if (!this.handlers.has(topic)) { this.handlers.set(topic, new Set()); this.send({ type: 'sub', topic }); }
    this.handlers.get(topic)!.add(h);
    return () => { this.handlers.get(topic)!.delete(h); if (!this.handlers.get(topic)!.size) { this.handlers.delete(topic); this.send({ type: 'unsub', topic }); } };
  }
}
export const realtime = new Realtime();
```

```tsx
// Chat screen: subscribe while mounted, write into cache
useEffect(() => realtime.subscribe(`chat:${chatId}`, (m) =>
  qc.setQueryData(['messages', chatId], (old: Message[] = []) =>
    old.some((x) => x.id === m.id || x.clientMsgId === m.clientMsgId) ? old.map((x) => (x.clientMsgId === m.clientMsgId ? m : x)) : [...old, m])
), [chatId]);
```

### React Native: pause when backgrounded, reconnect on network change
```ts
AppState.addEventListener('change', (s) => (s === 'active' ? realtime.connect() : realtime.close()));
NetInfo.addEventListener((s) => s.isConnected && realtime.connect());
// When app is backgrounded/killed, rely on push notifications (FCM/APNs — Topic M10) instead of sockets
```

### Polling done right (when it's enough)
```ts
useQuery({ queryKey: ['score', matchId], queryFn: getScore, refetchInterval: 10_000, refetchIntervalInBackground: false });
// Backend: GET /score/:matchId → Cache-Control: public, max-age=5 → CDN absorbs millions of polls
```

---

## ⚫ Interview Questions + Answers

**Q1: Compare polling, long polling, SSE and WebSockets.**
A1: Short polling repeatedly requests at intervals. It's simplest and works everywhere, but latency is bounded by the interval and most requests are wasted. Long polling holds the request until data is available, which gives near real-time over plain HTTP at the cost of held connections and reconnect logic. SSE is a one-way server-to-client stream over HTTP with built-in reconnection and `Last-Event-ID`, ideal for notifications, feeds, status and LLM streaming. WebSockets are full-duplex persistent connections with the lowest latency for bidirectional high-frequency messaging (chat, games, collaboration), but you must handle heartbeats, reconnects and scaling yourself.

**Q2: How do you handle WebSocket disconnections on mobile networks?**
A2: Detect dead connections with application-level heartbeats. Reconnect with exponential backoff plus jitter. Re-authenticate with a short-lived ticket. Resume by sending the last received sequence or event ID so the server replays missed events, or refetch current state via REST after reconnecting. Queue outgoing messages while offline with client IDs for idempotent retries. Pause the connection when the app is backgrounded and rely on push notifications. Show connection status in the UI.

**Q3: When would you choose SSE over WebSockets?**
A3: When updates flow only from server to client (notifications, live scores, order tracking, dashboards, AI token streaming). SSE runs over standard HTTP (works with existing auth cookies, proxies, HTTP/2 multiplexing and load balancers), has automatic reconnection and resume via `Last-Event-ID`, and is simpler to implement. Client-to-server actions can use normal HTTP requests. Choose WebSockets for bidirectional, high-frequency or binary messaging.

**Q4: How do real-time updates integrate with client-side caching?**
A4: Treat socket or SSE events as cache updates. Write them into the server-state cache (`setQueryData` or Apollo cache writes) keyed like the REST queries, using sequence numbers or timestamps to ignore stale or duplicate events, or invalidate queries to refetch. This keeps a single source of truth so every component showing that entity updates consistently. After reconnecting, refetch or replay to fill gaps.

**Q5: Live cricket score for 50 million users — WebSocket or polling?**
A5: Score updates are infrequent (every few seconds or per ball) and identical for everyone. Short polling a CDN-cached endpoint (`max-age` of a few seconds) is very cost-effective and resilient, because the CDN absorbs the load and the origin sees only a few requests per edge. Millions of persistent WebSockets need large connection-gateway fleets and fan-out infrastructure. SSE or WebSocket is worth it for lower latency or personalized streams (ball-by-ball commentary with interactions), often using pub/sub plus edge fan-out. A hybrid is common.

---

## 🔷 Trade-offs
✅ Polling: simplest, CDN-friendly — ❌ latency/waste for frequent updates.
✅ SSE: simple push over HTTP, auto-reconnect — ❌ one-way, text only, connection limits on HTTP/1.1 (6 per domain).
✅ WebSocket: two-way, lowest latency — ❌ stateful scaling, reconnect/resume logic, some proxies/firewalls.
✅ Real-time UX — ❌ battery/data usage on mobile → pause in background, use push.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Short polling | Ask at fixed intervals | तय समय पर पूछना |
| Long polling | Server holds request until news | ख़बर तक request रोकना |
| SSE | Server-Sent Events stream | सर्वर का एक-तरफ़ा stream |
| EventSource | Browser SSE client | ब्राउज़र का SSE client |
| WebSocket | Full-duplex persistent connection | दोनों तरफ़ खुला कनेक्शन |
| Heartbeat | Periodic ping to detect dead links | ज़िंदा होने की जाँच |
| Backoff + jitter | Increasing random retry delays | बढ़ता, थोड़ा random इंतज़ार |
| Resume / replay | Get missed events after reconnect | छूटे events दोबारा लेना |
| Sequence number | Ordering & dedupe id | क्रम संख्या |
| Fan-out | Delivering one event to many | एक event कई तक |

---

## ⚡ 3-Line Summary
**English:**
1. Polling for rare updates, SSE for server→client streams (status, notifications, LLM tokens), WebSocket for two-way low-latency (chat, collab, location).
2. Make connections reliable: heartbeat, backoff + jitter reconnect, resume via last seq/event id, dedupe & ordering, offline outbox.
3. Feed events into the server-state cache, share one connection, pause in background (push instead), and consider CDN polling at massive scale.

**Hindi:**
1. कभी-कभार → polling; सर्वर से stream → SSE; दोनों तरफ़ तेज़ → WebSocket।
2. मज़बूत कनेक्शन: heartbeat, backoff से reconnect, आख़िरी seq से resume, duplicate हटाओ, offline outbox।
3. Events को cache में डालो, एक ही कनेक्शन, background में push; बहुत बड़े पैमाने पर CDN polling सोचो।

---

## ➡️ Next Topic Suggestion
**F14. Frontend Security (XSS, CSRF, CSP)** — Real-time messages, comments and profiles are user-generated content, a classic attack vector. Next: XSS, CSRF, clickjacking and Content Security Policy, and how React helps and doesn't.
