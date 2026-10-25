# 189. WebSocket with Node.js (ws)
# हिंदी में: Node.js में WebSocket (ws library)

---

## 🔵 Simple Definition (English)
**WebSocket** is a protocol that opens a single TCP connection between client and server and keeps it open, so both sides can send messages to each other **anytime**, without the client having to ask first (unlike HTTP). The `ws` package is the most popular low-level WebSocket library for Node.js — it gives you a raw WebSocket server/client with no extra framework overhead.

## 🔵 सरल परिभाषा (Hindi)
**WebSocket** एक protocol है जो client और server के बीच एक TCP connection खोलता है और उसे open रखता है, ताकि दोनों sides कभी भी message भेज सकें — HTTP की तरह client को पहले request नहीं भेजनी पड़ती। `ws` package Node.js का सबसे popular low-level WebSocket library है — बिना किसी extra framework overhead के raw WebSocket server/client देता है।

---

## 🔴 Problem it Solves
```
HTTP PROBLEM (before WebSocket):
  Client wants live updates (chat, live price, order status)
  → Only way: POLLING — client asks server every 2 seconds "anything new?"
  → 1000 users × poll every 2s = 500 requests/sec, mostly "no, nothing new"
  → Wastes bandwidth, server CPU, adds latency (up to 2s delay)

WEBSOCKET SOLUTION:
  Open ONE persistent connection
  Server can PUSH data the moment it's ready
  No repeated handshakes, no wasted "nothing new" responses
  Real-time: delay is milliseconds, not seconds
```

## 🔴 यह क्यों बना? (Hindi)
```
HTTP में problem: client को live update चाहिए तो polling करनी पड़ती थी
हर 2 second poll = bandwidth waste, ज़्यादातर "कुछ नया नहीं" response
WebSocket: एक connection खोलो, server जब चाहे data push कर दे
Real-time delay milliseconds में, seconds में नहीं
```

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends an HTTP request with `Upgrade: websocket` header
Step 2 → Server responds with `101 Switching Protocols` — HTTP connection is "upgraded" to WebSocket
Step 3 → TCP connection stays open; now both sides can send frames (messages) anytime
Step 4 → `ws` library wraps this: `ws.send(data)` to send, `ws.on('message', cb)` to receive
Step 5 → Connection stays alive until either side closes it or the network drops (handled with ping/pong heartbeats)

## 🟢 कैसे काम करता है? (Hindi)
```
1. Client HTTP request भेजता है with Upgrade: websocket header
2. Server 101 Switching Protocols से respond करता है
3. TCP connection open रहता है — दोनों तरफ से कभी भी message भेज सकते हैं
4. ws.send() भेजने के लिए, ws.on('message') पाने के लिए
5. ping/pong से connection alive check होता रहता है
```

---

## 🟡 Real World Example
**Swiggy live order tracking:** Once you place an order, the delivery partner's live location needs to reach your app every few seconds. Instead of your app polling the server 10 times a minute, Swiggy's backend opens a WebSocket connection when you open the order-tracking screen. The moment the delivery partner's GPS updates, the server pushes the new lat/lng straight to your phone over the open socket — instant map movement, no polling delay.

## 🟡 Real Example Hindi mein
**Swiggy live order tracking:** Order place करने के बाद delivery partner की live location हर कुछ seconds में app तक पहुंचनी चाहिए। Polling की जगह, order-tracking screen खोलते ही एक WebSocket connection खुल जाता है। GPS update होते ही server नया lat/lng सीधे socket पर push कर देता है — instant map movement, कोई polling delay नहीं।

---

## 💻 Code Example — Basic

```javascript
// server.js
// Run: npm install ws  then  node server.js
const WebSocket = require('ws');

// Create a WebSocket server listening on port 8080
const wss = new WebSocket.Server({ port: 8080 });

// 'connection' fires every time a new client connects
wss.on('connection', (socket) => {
  console.log('Client connected');

  // Send a welcome message immediately after connecting
  socket.send('Welcome to the server!');

  // 'message' fires whenever this client sends data
  socket.on('message', (data) => {
    console.log('Received:', data.toString());
    // Echo the message back to the same client
    socket.send(`Echo: ${data}`);
  });

  // 'close' fires when the client disconnects
  socket.on('close', () => {
    console.log('Client disconnected');
  });
});

console.log('WebSocket server running on ws://localhost:8080');
```

```javascript
// client.js — run in another terminal: node client.js
const WebSocket = require('ws');

// Connect to the server
const socket = new WebSocket('ws://localhost:8080');

// Fires once connection is established
socket.on('open', () => {
  console.log('Connected to server');
  socket.send('Hello server!');  // send a message
});

// Fires whenever server sends data
socket.on('message', (data) => {
  console.log('Server says:', data.toString());
});
```

## 💻 Code Example — Advanced

```javascript
// advanced-server.js
// Production-ready WebSocket server with heartbeat + broadcast + error handling
const WebSocket = require('ws');
const http = require('http');

// Create an HTTP server so WebSocket can share the same port as REST APIs
const server = http.createServer();
const wss = new WebSocket.Server({ server });

// Broadcast a message to ALL connected clients except the sender
function broadcast(sender, message) {
  wss.clients.forEach((client) => {
    // Only send to clients that are OPEN and not the sender
    if (client !== sender && client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

wss.on('connection', (socket, req) => {
  socket.isAlive = true;  // flag used by heartbeat check
  console.log(`New client from ${req.socket.remoteAddress}`);

  // Client responds to our ping with a pong — mark it alive
  socket.on('pong', () => {
    socket.isAlive = true;
  });

  socket.on('message', (data) => {
    try {
      const parsed = JSON.parse(data);  // expect JSON messages
      broadcast(socket, JSON.stringify({ user: parsed.user, text: parsed.text }));
    } catch (err) {
      // Never crash the server on bad client input
      socket.send(JSON.stringify({ error: 'Invalid JSON' }));
    }
  });

  socket.on('error', (err) => {
    console.error('Socket error:', err.message);  // log, don't crash
  });
});

// Heartbeat: every 30s, ping all clients; terminate ones that didn't pong back
const interval = setInterval(() => {
  wss.clients.forEach((socket) => {
    if (socket.isAlive === false) return socket.terminate();  // dead connection
    socket.isAlive = false;
    socket.ping();  // expect a pong in response
  });
}, 30000);

wss.on('close', () => clearInterval(interval));  // cleanup on server shutdown

server.listen(8080, () => console.log('Server + WebSocket on port 8080'));
```

---

## 🟠 Express.js Integration

```javascript
// Combine Express (REST) + ws (WebSocket) on the SAME HTTP server/port
const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);       // wrap Express app in raw HTTP server
const wss = new WebSocket.Server({ server }); // attach WebSocket to the same server

// Normal REST route still works
app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

// WebSocket route for live notifications
wss.on('connection', (socket) => {
  socket.send(JSON.stringify({ type: 'welcome' }));

  socket.on('message', (msg) => {
    console.log('Client message:', msg.toString());
  });
});

// Trigger a push from a REST endpoint (e.g. order status update)
app.post('/api/orders/:id/status', express.json(), (req, res) => {
  const update = { orderId: req.params.id, status: req.body.status };
  // Push update to every connected client (in real apps, filter by user/order)
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) client.send(JSON.stringify(update));
  });
  res.json({ pushed: true });
});

server.listen(3000, () => console.log('Express + WebSocket on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sending to a socket that's already closed/closing
✅ Correct: Always check `readyState === WebSocket.OPEN` before `send()`

```javascript
// Wrong — throws if socket is closing
socket.send(data);

// Right
if (socket.readyState === WebSocket.OPEN) {
  socket.send(data);
}
```

❌ Mistake 2: No heartbeat — dead connections pile up silently (e.g. phone loses network without a proper close frame), leaking memory.
✅ Correct: Use `ping()`/`pong()` with `isAlive` flag and `terminate()` dead sockets (see Advanced example).

❌ Mistake 3: Not wrapping `JSON.parse(data)` in try/catch — a malformed client message crashes the whole server process.
✅ Correct: Always try/catch parsing of untrusted client input.

---

## 🧠 Tricky Interview Question

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 9000 });
let count = 0;

wss.on('connection', (socket) => {
  count++;
  console.log('Clients:', count);
  socket.on('close', () => {
    count--;
    console.log('Clients:', count);
  });
});
// If 3 clients connect then 1 disconnects abruptly (kills network, no close frame sent),
// does count go down immediately?
```
Answer: **No, not immediately.** A clean `socket.close()` fires the `'close'` event right away. But if a client's network dies abruptly (phone goes into a tunnel, laptop lid closes), no close frame is sent — the server has no idea the client is gone until either (a) a `send()` to that socket fails, or (b) the ping/pong heartbeat mechanism detects it (typically 30-60s later) and calls `terminate()`, which then fires `'close'`. This is exactly why production WebSocket servers MUST implement heartbeat — without it, "zombie" connections stay counted and consume memory for a long time.

---

## ⚫ Interview Questions + Answers

Q1: How is WebSocket different from HTTP?
A1: HTTP is request-response — client always initiates, connection typically closes after response (or is reused via keep-alive but still request-response). WebSocket upgrades an HTTP connection into a persistent, full-duplex TCP connection — either side can send data at any time without the other side asking first. HTTP is for "give me X"; WebSocket is for continuous two-way streams like chat, live tracking, live dashboards.

Q2: What is the WebSocket handshake?
A2: Client sends a normal HTTP GET request with headers `Upgrade: websocket`, `Connection: Upgrade`, and a `Sec-WebSocket-Key`. If the server supports WebSocket, it replies with `101 Switching Protocols` and a `Sec-WebSocket-Accept` header (a hash of the key, proving it understood the request). After this handshake, the same TCP socket is reused for WebSocket framing instead of HTTP.

Q3: Why do you need a heartbeat (ping/pong) mechanism?
A3: TCP connections can die silently — network drop, phone sleep, NAT timeout — without either side sending a proper close frame. Without heartbeat, the server keeps a "dead" socket open indefinitely, wasting memory and miscounting active users. Ping/pong periodically checks liveness: server pings, client's WebSocket implementation auto-pongs; if no pong comes back within a timeout, the server terminates the connection.

Q4: Can WebSocket and a REST API run on the same port?
A4: Yes. Both are built on top of HTTP's initial handshake, so you can create one `http.Server`, pass it to both Express (for REST routes) and `ws.Server({ server })` (for WebSocket upgrade requests). The server inspects whether a request has `Upgrade: websocket` header — if yes, `ws` handles it; otherwise Express's normal middleware chain handles it.

Q5: When would you choose raw `ws` over Socket.io?
A5: Choose `ws` when you want a lightweight, standards-compliant WebSocket with full control and minimal overhead (e.g., microservice-to-microservice real-time link, or a simple notification channel) and don't need automatic reconnection, fallback transports, or rooms/namespaces. Choose Socket.io when you need those higher-level features out of the box (browser compatibility fallback, auto-reconnect, rooms, broadcasting helpers) at the cost of a slightly heavier protocol that isn't plain WebSocket on the wire.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need true real-time, bidirectional communication (chat, live tracking, live dashboards, multiplayer games)
- You want a lightweight protocol with minimal overhead and full control over the wire format
- Both client and server are under your control (so you can implement heartbeat/reconnect yourself)

❌ Avoid when:
- You just need the server to occasionally push updates — Server-Sent Events (SSE) is simpler for one-way server→client streams
- Your infra (old proxies/load balancers) doesn't support connection upgrades well
- You need automatic reconnection/room management out of the box without extra code — consider Socket.io instead

---

## 📊 Visual Diagram
```
HTTP REQUEST-RESPONSE                  WEBSOCKET (after upgrade)
──────────────────────                 ──────────────────────────
Client ──request──▶ Server             Client ◀══════════▶ Server
Client ◀─response── Server                   (persistent TCP,
Client ──request──▶ Server                    both sides push
Client ◀─response── Server                    anytime, no new
     (connection closes/reused)                handshake needed)

HANDSHAKE:
Client: GET /chat HTTP/1.1
        Upgrade: websocket
        Sec-WebSocket-Key: xxxx
             │
             ▼
Server: HTTP/1.1 101 Switching Protocols
        Upgrade: websocket
        Sec-WebSocket-Accept: yyyy
             │
             ▼
   [ TCP socket now speaks WebSocket frames ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebSocket | Full-duplex persistent connection protocol | दोनों तरफ से data भेजने वाला persistent protocol |
| Upgrade handshake | HTTP request that switches protocol | HTTP request जो protocol बदलती है |
| Frame | A single WebSocket message unit | एक WebSocket message unit |
| Heartbeat (ping/pong) | Liveness check mechanism | Connection alive है या नहीं check करने का तरीका |
| readyState | Current state of the socket | Socket की current state |
| Broadcast | Sending to multiple clients | कई clients को एक साथ message भेजना |

---

## ⚡ 3-Line Summary
English:
1. WebSocket upgrades an HTTP connection into a persistent, full-duplex channel so both client and server can push data anytime.
2. The `ws` package is a lightweight, low-level WebSocket implementation for Node.js, usable standalone or attached to an Express HTTP server.
3. Always implement heartbeat (ping/pong) and guard `send()` with `readyState` checks to avoid leaking dead connections or crashing on closed sockets.

Hindi:
1. WebSocket HTTP connection को persistent, दोनों तरफ data भेजने वाले channel में upgrade करता है।
2. `ws` package Node.js का lightweight, low-level WebSocket implementation है, Express के साथ भी attach हो सकता है।
3. हमेशा heartbeat implement करो और `send()` से पहले `readyState` check करो।

---

## ➡️ Next Topic
**190. Socket.io — Complete Guide** — A higher-level real-time library built on WebSocket with auto-reconnect, rooms, and fallback transports.
