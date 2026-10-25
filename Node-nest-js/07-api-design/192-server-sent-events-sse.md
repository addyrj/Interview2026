# 192. Server-Sent Events (SSE)
# हिंदी में: Server-Sent Events (SSE)

---

## 🔵 Simple Definition (English)
**Server-Sent Events (SSE)** is a standard that lets a server push a continuous stream of text updates to a browser over a single long-lived HTTP connection — one-way only (server → client). It's built directly on HTTP (no upgrade/handshake needed like WebSocket) and browsers have native support via the `EventSource` API with automatic reconnection.

## 🔵 सरल परिभाषा (Hindi)
**Server-Sent Events (SSE)** एक standard है जिससे server एक ही long-lived HTTP connection पर browser को continuous text updates push कर सकता है — सिर्फ एक तरफ (server → client)। यह सीधा HTTP पर बना है (WebSocket जैसी upgrade handshake नहीं चाहिए), browsers में native `EventSource` API से auto-reconnect मिलता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Sometimes you ONLY need server → client push, never client → server over the same channel
  WebSocket is overkill: needs its own protocol upgrade, proxies sometimes block it,
  you write extra code for reconnect logic
  Polling wastes bandwidth and adds latency

SSE SOLUTION:
  Plain HTTP response that never "finishes" — server keeps writing chunks
  Browser's EventSource auto-reconnects if connection drops (built-in, free)
  Works through normal HTTP infra (proxies, load balancers) without special config
  Simple text format: "data: {...}\n\n"
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: कभी-कभी सिर्फ server → client push चाहिए होता है, client → server नहीं
WebSocket overkill है — अपना protocol upgrade चाहिए, proxies कभी-कभी block करते हैं
SSE: plain HTTP response जो कभी खत्म नहीं होता, browser का EventSource auto-reconnect करता है
```

---

## 🟢 How it Works — Step by Step

Step 1 → Client opens connection: `new EventSource('/api/stream')` — a normal GET request
Step 2 → Server responds with header `Content-Type: text/event-stream` and KEEPS the connection open
Step 3 → Server writes events in the format `data: <payload>\n\n` whenever it has new data — browser parses each one as a `message` event
Step 4 → Browser's `EventSource` automatically reconnects (after a default ~3s) if the connection drops, resending the `Last-Event-ID` header so the server can resume from where it left off
Step 5 → Connection stays open indefinitely until the client closes it or the server ends the response

## 🟢 कैसे काम करता है? (Hindi)
```
1. Client EventSource से connect करता है — normal GET request
2. Server Content-Type: text/event-stream भेजता है, connection open रखता है
3. Server "data: ...\n\n" format में events लिखता है
4. Connection टूटे तो EventSource खुद reconnect कर लेता है
5. Connection open रहता है जब तक client/server बंद न करें
```

---

## 🟡 Real World Example
**Paytm live transaction status / stock-price-style ticker:** When Paytm shows you a "payment processing..." screen that updates live without you refreshing, SSE is a natural fit — the server only needs to push status changes ("initiated" → "processing" → "success") one-way, and the client never needs to send anything back over that same channel. Using SSE here avoids the overhead of a full WebSocket handshake for a purely one-directional, short-lived stream.

## 🟡 Real Example Hindi mein
**Paytm payment status screen:** "payment processing..." screen जो खुद update होती है, SSE से होता है — server सिर्फ status push करता है ("initiated" → "processing" → "success"), client को कुछ वापस भेजने की जरूरत नहीं। पूरी WebSocket handshake की जरूरत नहीं पड़ती यहाँ।

---

## 💻 Code Example — Basic

```javascript
// server.js
// Run: node server.js   then open http://localhost:3000/stream in browser dev console
const http = require('http');

const server = http.createServer((req, res) => {
  if (req.url === '/stream') {
    // These headers tell the browser this is an SSE stream, keep it open
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',  // required SSE mime type
      'Cache-Control': 'no-cache',           // don't let proxies cache the stream
      'Connection': 'keep-alive',             // keep TCP connection open
    });

    let count = 0;
    // Send a new event every second
    const interval = setInterval(() => {
      count++;
      // SSE format: "data: <text>\n\n" — the double newline marks end of event
      res.write(`data: Update number ${count}\n\n`);
      if (count === 5) {
        clearInterval(interval);
        res.end();  // close the stream after 5 updates
      }
    }, 1000);

    // Clean up if client disconnects early
    req.on('close', () => clearInterval(interval));
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(3000, () => console.log('SSE server on http://localhost:3000/stream'));
```

```html
<!-- client.html — open in a browser -->
<script>
  // EventSource is a native browser API for SSE
  const source = new EventSource('http://localhost:3000/stream');

  // Fires for every "data: ..." event received
  source.onmessage = (event) => {
    console.log('Received:', event.data);
  };

  // Fires if the connection breaks — EventSource auto-reconnects after this
  source.onerror = (err) => {
    console.log('Connection error, browser will auto-retry...');
  };
</script>
```

## 💻 Code Example — Advanced

```javascript
// advanced-sse-server.js
// Production pattern: named events, IDs for resume, heartbeat to keep proxies happy
const http = require('http');

const clients = new Set();  // track all currently connected SSE clients

const server = http.createServer((req, res) => {
  if (req.url !== '/stream') {
    res.writeHead(404);
    return res.end();
  }

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no',  // disables nginx buffering, crucial for real-time
  });

  // Resume support: client sends Last-Event-ID after a reconnect
  const lastEventId = req.headers['last-event-id'];
  if (lastEventId) {
    console.log(`Client resuming from event ${lastEventId}`);
    // In a real app: fetch missed events from DB/queue since this ID and replay them
  }

  let eventId = Number(lastEventId) || 0;
  clients.add(res);

  // Heartbeat comment line every 15s — prevents idle proxies from closing connection
  const heartbeat = setInterval(() => res.write(': heartbeat\n\n'), 15000);

  req.on('close', () => {
    clearInterval(heartbeat);
    clients.delete(res);  // stop tracking disconnected client
  });

  // Attach a helper so other code can push named events with an incrementing id
  res.sendEvent = (eventName, data) => {
    eventId++;
    // "id:" lets browser track position for resume; "event:" names the event type
    res.write(`id: ${eventId}\nevent: ${eventName}\ndata: ${JSON.stringify(data)}\n\n`);
  };
});

// Simulate a business event broadcasting to ALL connected clients
setInterval(() => {
  const payload = { status: 'processing', time: Date.now() };
  for (const client of clients) {
    client.sendEvent('orderStatus', payload);  // named event, not just generic 'data'
  }
}, 3000);

server.listen(3000, () => console.log('Advanced SSE server on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Express route streaming live order status via SSE
const express = require('express');
const app = express();

app.get('/api/orders/:id/stream', (req, res) => {
  // Required SSE headers
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });
  res.flushHeaders();  // send headers immediately, don't wait to buffer

  const orderId = req.params.id;
  // Simulate polling a DB/queue for status changes and pushing them
  const interval = setInterval(async () => {
    const status = await getOrderStatus(orderId);  // your DB lookup function
    res.write(`data: ${JSON.stringify({ orderId, status })}\n\n`);
    if (status === 'delivered') {
      clearInterval(interval);
      res.end();  // close stream once terminal state is reached
    }
  }, 2000);

  // Clean up the interval if the client navigates away / closes tab
  req.on('close', () => clearInterval(interval));
});

async function getOrderStatus(id) {
  // Placeholder — replace with real DB query
  return 'processing';
}

app.listen(3000, () => console.log('Express SSE on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting the double newline (`\n\n`) at the end of each SSE event — the browser never fires `onmessage` without it.
✅ Correct: Always terminate every event with exactly `\n\n`.

```javascript
// Wrong — browser buffers forever, never dispatches an event
res.write(`data: hello\n`);

// Right
res.write(`data: hello\n\n`);
```

❌ Mistake 2: Not disabling proxy buffering (e.g., nginx) — updates arrive in big delayed chunks instead of real-time.
✅ Correct: Set `X-Accel-Buffering: no` for nginx, and ensure `Content-Type: text/event-stream` with no `Content-Length` so the connection streams rather than buffers.

❌ Mistake 3: Forgetting to clean up `setInterval`/listeners on `req.on('close')`, leaking timers for every client that navigates away without the server noticing.
✅ Correct: Always register a `close` handler to stop background work tied to that connection.

---

## 🧠 Tricky Interview Question

```javascript
// Client-side
const es = new EventSource('/stream');
es.onmessage = (e) => console.log('A:', e.data);
es.addEventListener('ping', (e) => console.log('B:', e.data));

// Server sends:
// data: hello\n\n
// event: ping\ndata: pong\n\n
```
What logs on the client console?
Answer:
```
A: hello
B: pong
```
**Explanation:** `onmessage` only fires for events with NO explicit `event:` field (they default to type `"message"`). The second block explicitly sets `event: ping`, so it does NOT trigger `onmessage` — it only triggers listeners registered for that specific named event type via `addEventListener('ping', ...)`. This is a common SSE gotcha: forgetting that named events bypass `onmessage` entirely.

---

## ⚫ Interview Questions + Answers

Q1: How is SSE different from WebSocket?
A1: SSE is one-directional (server → client only) and built directly on HTTP — no special upgrade handshake, works over plain `fetch`/HTTP infra, and browsers get free auto-reconnect via `EventSource`. WebSocket is full-duplex (both directions) and requires a protocol upgrade from HTTP to a different framing protocol. Use SSE when you only need server push; use WebSocket when the client also needs to push data on the same channel.

Q2: Why doesn't SSE need special proxy/firewall configuration like WebSocket sometimes does?
A2: Because SSE is just a regular, very long-lived HTTP GET response with `Content-Type: text/event-stream` — it looks like ordinary HTTP traffic to proxies, load balancers, and firewalls, so it "just works" through most existing infrastructure, unlike WebSocket's protocol upgrade which some older/strict proxies refuse to pass through.

Q3: How does automatic reconnection and resume work in SSE?
A3: The browser's native `EventSource` automatically retries the connection (default ~3 seconds, configurable server-side via a `retry:` field) if it drops. On retry, the browser sends a `Last-Event-ID` header with the ID of the last event it successfully received (set via the `id:` field in the event stream), letting the server resume sending from the correct point instead of restarting from scratch.

Q4: What are the limitations of SSE?
A4: One-directional only — client can't send data back over the same connection (you'd need a separate regular HTTP POST for that). Limited to text data (no binary, unlike WebSocket). Browsers (not all other HTTP clients) have a per-domain concurrent connection limit (historically 6 for HTTP/1.1) that can be hit if you open many SSE streams to the same host — mitigated by HTTP/2 multiplexing.

Q5: When would you pick SSE over polling or WebSocket?
A5: Pick SSE when you need real-time server push but never need the client to send data on that channel, when you want automatic reconnection "for free," and when your traffic needs to pass cleanly through standard HTTP infrastructure (CDNs, proxies) without special WebSocket support. Example: live order status, live notification feed, streaming AI model responses token-by-token.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Only server-to-client push is needed (status updates, notifications, live feeds, streaming LLM tokens)
- You want built-in reconnection without extra client libraries
- Traffic needs to work through standard HTTP infra without special config

❌ Avoid when:
- You need bidirectional communication (chat, multiplayer) — use WebSocket/Socket.io
- You need binary data streaming — SSE is text-only
- You're on HTTP/1.1 with many simultaneous streams per browser tab — risk of hitting the connection limit

---

## 📊 Visual Diagram
```
SSE FLOW
──────────────────────────────────────────
Client                         Server
  │  GET /stream                  │
  │ ─────────────────────────────▶│
  │  200 OK                       │
  │  Content-Type: text/event-    │
  │  stream (connection stays     │
  │  open)                        │
  │ ◀───────────────────────────  │
  │  data: update 1\n\n           │
  │ ◀───────────────────────────  │
  │  data: update 2\n\n           │
  │ ◀───────────────────────────  │
  │       (connection drops)      │
  │  auto-reconnect with          │
  │  Last-Event-ID header         │
  │ ─────────────────────────────▶│
  │  resumes from last event      │
  │ ◀───────────────────────────  │
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EventSource | Browser API for consuming SSE | SSE consume करने का browser API |
| text/event-stream | MIME type for SSE responses | SSE responses का MIME type |
| Last-Event-ID | Header to resume stream after reconnect | Reconnect के बाद resume करने का header |
| Named event | Event with explicit `event:` field | Explicit `event:` field वाला event |
| Heartbeat | Keep-alive comment to prevent timeout | Timeout रोकने के लिए keep-alive comment |

---

## ⚡ 3-Line Summary
English:
1. SSE is a one-way server-to-client streaming protocol built on plain HTTP, consumed natively via `EventSource`.
2. Every event must end with `\n\n`, and named events (`event: name`) only trigger matching `addEventListener`, not `onmessage`.
3. Use SSE for notifications/status streams; use WebSocket/Socket.io when the client also needs to push data back.

Hindi:
1. SSE plain HTTP पर बना one-way server-to-client streaming protocol है, `EventSource` से consume होता है।
2. हर event `\n\n` से खत्म होना चाहिए, named events सिर्फ matching listener पर ही fire होते हैं।
3. Notifications/status के लिए SSE, bidirectional चाहिए तो WebSocket/Socket.io use करो।

---

## ➡️ Next Topic
**193. API Documentation (Swagger/OpenAPI)** — Documenting REST and real-time APIs for consumers.
