# 65. net Module
# हिंदी में: net Module — Raw TCP Sockets

---

## 🔵 Simple Definition (English)
The **`net`** module provides an asynchronous API for creating raw **TCP servers and clients**. It's the low-level networking primitive that Node's `http` module is built on top of. With `net`, you work directly with sockets, bytes, and streams — no HTTP headers, no request/response abstraction, just raw bidirectional data.

## 🔵 सरल परिभाषा (Hindi)
**`net`** module raw **TCP servers और clients** बनाने का async API देता है। Node का `http` module इसी के ऊपर बना है। `net` में आप directly sockets, bytes और streams के साथ काम करते हो — कोई HTTP headers नहीं, कोई request/response abstraction नहीं, सिर्फ raw bidirectional data।

---

## 🔴 Problem it Solves
```
BEFORE net MODULE:
  Node needed a way to do low-level network communication:
  - Custom protocols (not HTTP) — e.g. game servers, chat protocols, IoT devices
  - Database drivers (MySQL, PostgreSQL, Redis) — they speak their OWN binary protocol over TCP
  - Microservice-to-microservice RPC with custom lightweight protocols
  - Building your OWN HTTP server from scratch (how http module itself works)

WITH net MODULE:
  const server = net.createServer(socket => {
    socket.write('Hello, raw TCP client!');
  });
  server.listen(8124);
  → Full control over the wire protocol, no HTTP overhead
```

## 🔴 यह क्यों बना? (Hindi)
```
Node को low-level network communication चाहिए था:
- Custom protocols (HTTP नहीं) — game servers, chat, IoT
- DB drivers (MySQL, Postgres, Redis) अपने binary protocol में बात करते हैं TCP पर
- खुद का HTTP server बनाने के लिए (http module खुद net पर बना है)
net module ये सब control देता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → net.createServer(socket => {...}) creates a TCP server
Step 2 → server.listen(port) binds to a port, starts accepting connections
Step 3 → On each new connection, Node emits 'connection' event with a `socket` object
Step 4 → socket is a Duplex Stream — socket.write(data) sends bytes, socket.on('data') receives bytes
Step 5 → Client side: net.createConnection({ port, host }) opens a TCP connection
Step 6 → Both ends exchange raw data until socket.end() or socket.destroy() closes it
Step 7 → Events: 'connect', 'data', 'end', 'error', 'close' drive the lifecycle
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. net.createServer() से TCP server बनता है
2. server.listen(port) से port पर listening शुरू
3. हर नए connection पर 'connection' event, socket object मिलता है
4. socket.write()/socket.on('data') से raw bytes भेजना/पाना
5. Client: net.createConnection() से connection open
6. socket.end() या socket.destroy() से connection close
```

---

## 🟡 Real World Example
**Paytm's internal order-matching engine:** Instead of HTTP (which has header parsing overhead on every request), Paytm's high-frequency internal services use a custom lightweight binary protocol over raw TCP sockets via the `net` module for microsecond-level latency between the order service and the ledger service. Similarly, Redis clients (like `ioredis`) and MySQL drivers (`mysql2`) use `net.createConnection()` internally to speak their database's native wire protocol — that's why `require('mysql2')` doesn't use `http` at all.

## 🟡 Real Example Hindi mein
**Paytm:** High-frequency internal services HTTP की header-parsing overhead से बचने के लिए custom binary protocol raw TCP (net module) पर use करती हैं — microsecond latency के लिए। Redis client (`ioredis`) और MySQL driver (`mysql2`) भी अंदर `net.createConnection()` use करके अपने database का native protocol बोलते हैं।

---

## 💻 Code Example — Basic

```javascript
// net-basic-server.js
// Run: node net-basic-server.js, then in another terminal: nc localhost 8124 (or telnet)

const net = require('net');  // import core net module

// Create a TCP server — callback runs once PER new connection
const server = net.createServer((socket) => {
  console.log('Client connected:', socket.remoteAddress, socket.remotePort);

  // socket is a Duplex stream — write sends data to client
  socket.write('Welcome! Type something and press enter.\n');

  // 'data' event fires whenever bytes arrive from this client
  socket.on('data', (chunk) => {
    const message = chunk.toString().trim();  // Buffer -> string
    console.log('Received:', message);

    // Echo back to the client, uppercased
    socket.write(`ECHO: ${message.toUpperCase()}\n`);

    if (message === 'quit') {
      socket.end('Goodbye!\n');  // sends final data then closes
    }
  });

  // 'end' fires when the client closes their end of the connection
  socket.on('end', () => {
    console.log('Client disconnected');
  });

  // Always handle socket errors — unhandled errors crash the process!
  socket.on('error', (err) => {
    console.error('Socket error:', err.message);
  });
});

// Start listening on port 8124
server.listen(8124, () => {
  console.log('TCP server listening on port 8124');
});
```

## 💻 Code Example — Advanced

```javascript
// net-advanced.js — Production-style TCP server with framing + client

const net = require('net');

// ─── PROBLEM: TCP has no message boundaries — data can arrive split or merged ───
// SOLUTION: length-prefix framing — send 4-byte length header before each message

function createServer() {
  const server = net.createServer((socket) => {
    let buffer = Buffer.alloc(0);  // accumulate incoming bytes here

    socket.on('data', (chunk) => {
      buffer = Buffer.concat([buffer, chunk]);  // append new bytes

      // Process as many complete messages as are in the buffer
      while (buffer.length >= 4) {
        const msgLength = buffer.readUInt32BE(0);  // first 4 bytes = length
        if (buffer.length < 4 + msgLength) break;  // full message not arrived yet

        const message = buffer.slice(4, 4 + msgLength).toString('utf8');
        buffer = buffer.slice(4 + msgLength);  // remove processed message

        handleMessage(socket, message);
      }
    });

    socket.on('error', (err) => {
      console.error('Socket error:', err.message);  // e.g. ECONNRESET
    });

    // Set timeout — destroy idle connections to prevent resource leaks
    socket.setTimeout(30_000);  // 30 seconds of inactivity
    socket.on('timeout', () => {
      console.log('Socket timed out, closing');
      socket.end();
    });
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.error('Port already in use!');
      process.exit(1);
    }
  });

  return server;
}

function handleMessage(socket, message) {
  console.log('Received framed message:', message);
  const response = JSON.stringify({ status: 'ok', echo: message });
  sendFramed(socket, response);
}

// Helper: prefix a message with its byte-length before sending
function sendFramed(socket, message) {
  const payload = Buffer.from(message, 'utf8');
  const header = Buffer.alloc(4);
  header.writeUInt32BE(payload.length, 0);  // write length as 4-byte big-endian int
  socket.write(Buffer.concat([header, payload]));
}

const server = createServer();
server.listen(9000, () => console.log('Framed TCP server on 9000'));

// ─── CLIENT SIDE ──────────────────────────────────────────────────────────────
function connectClient() {
  const client = net.createConnection({ port: 9000, host: 'localhost' }, () => {
    console.log('Connected to server');
    sendFramed(client, JSON.stringify({ action: 'ping' }));
  });

  client.on('data', (data) => {
    console.log('Client received:', data.toString());
    client.end();  // close after one round trip
  });

  client.on('error', (err) => console.error('Client error:', err.message));
}

setTimeout(connectClient, 500);  // give server time to start
```

---

## 🟠 Express.js Integration

```javascript
// Express itself runs ON TOP of net/http — but you can run a raw TCP
// health-check or admin socket ALONGSIDE your Express app in the same process.

const express = require('express');
const net = require('net');

const app = express();
app.get('/', (req, res) => res.send('Main HTTP API'));

// Express's app.listen() internally creates an http.Server,
// which internally uses net.Server to bind to the TCP port.
const httpServer = app.listen(3000, () => {
  console.log('Express app on port 3000 (built on http -> net)');
});

// Example: a separate raw TCP admin socket for internal debugging/metrics
// (not exposed publicly — e.g., bound to localhost only, used by ops tooling)
const adminSocket = net.createServer((socket) => {
  socket.write(`Active connections: ${httpServer.connections || 'n/a'}\n`);
  socket.end();
});
adminSocket.listen(9229, '127.0.0.1', () => {
  console.log('Raw TCP admin socket on 127.0.0.1:9229');
});

// This pattern is common in production: HTTP for public API,
// raw TCP for internal metrics/debug ports, both in the same Node process.
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Assuming one `socket.write()` on the client = one `'data'` event on the server
```javascript
// WRONG assumption: TCP preserves message boundaries
socket.write('MSG1');
socket.write('MSG2');
// Server might receive ONE 'data' event with 'MSG1MSG2' concatenated!
// TCP is a byte STREAM, not a message protocol — no built-in framing.

// CORRECT: use length-prefix framing or a delimiter (like '\n') to split messages
// See the advanced example above using a 4-byte length header.
```

❌ **Mistake 2:** Not handling socket errors
```javascript
// WRONG: unhandled socket error crashes the entire process
const socket = net.createConnection({ port: 9000 });
socket.write('data');
// If connection refused (ECONNREFUSED) and no 'error' listener → process crashes!

// CORRECT: always attach an error handler
const socket = net.createConnection({ port: 9000 });
socket.on('error', (err) => {
  console.error('Connection failed:', err.message);  // handle gracefully
});
```

---

## 🧠 Tricky Interview Question

```javascript
const net = require('net');
const server = net.createServer((socket) => {
  socket.write('A');
  socket.write('B');
  socket.write('C');
  socket.end();
});
server.listen(7000, () => {
  const client = net.createConnection({ port: 7000 }, () => {});
  let received = '';
  client.on('data', (chunk) => { received += chunk; });
  client.on('end', () => console.log('Received:', received));
});
```

**Answer:** Output is `Received: ABC` — but it is NOT guaranteed to come as three separate `'data'` events. TCP may deliver `'A'`, `'B'`, `'C'` as ONE chunk `'ABC'`, or as multiple chunks in any split (`'AB'` + `'C'`, etc.), because TCP is a **byte stream with no message boundaries**. The Nagle algorithm and OS buffering can merge small writes. This is exactly why real protocols need framing (length-prefix, delimiters, or a well-known format like HTTP's `\r\n\r\n`).

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `net` and `http` modules?**
A1: `net` is the low-level TCP module — raw sockets, no concept of requests/responses/headers; you decide the wire protocol. `http` is built ON TOP of `net` — it adds HTTP-specific parsing (status lines, headers, chunked encoding) and gives you `req`/`res` objects. Use `net` for custom protocols, database-style connections, or performance-critical internal services; use `http` for anything that needs to speak the HTTP protocol (REST APIs, web servers).

**Q2: Why does TCP not preserve message boundaries, and how do you handle that in Node?**
A2: TCP is a byte-stream protocol — it guarantees ordered, reliable delivery of BYTES, not messages. The OS/network can merge or split your `write()` calls arbitrarily. To send discrete messages, you implement **application-level framing**: either a delimiter (like `\n` for line-based protocols) or a length-prefix header (send message length first, then read exactly that many bytes) — as shown in the advanced example's `sendFramed`/buffer-accumulation logic.

**Q3: What events does a `net.Socket` emit, and what do they mean?**
A3: `'connect'` — connection established (client side). `'data'` — bytes received (Buffer chunk). `'end'` — other side called `socket.end()` (no more data coming, but socket can still write). `'close'` — socket fully closed (fires after 'end' and local close). `'error'` — connection error (e.g., `ECONNRESET`, `ECONNREFUSED`, `ETIMEDOUT`) — MUST be handled or it can crash the process. `'timeout'` — fires if `socket.setTimeout(ms)` was set and no activity occurred.

**Q4: Why do database drivers like `mysql2` or `pg` use `net` instead of `http`?**
A4: Databases don't speak HTTP — they have their own optimized binary wire protocols (MySQL protocol, PostgreSQL protocol) designed for low latency and high throughput, with persistent connections, prepared statements, and binary row encoding. HTTP's text-based headers and request/response-per-call model would add unnecessary overhead for thousands of queries per second. So drivers use `net.createConnection()` to open a raw TCP socket and then implement the database's specific protocol on top of it.

**Q5: How would you detect and clean up idle/dead TCP connections in a Node server?**
A5: Use `socket.setTimeout(ms)` — if no data is sent/received within that window, Node emits a `'timeout'` event (note: this does NOT automatically close the socket, you must call `socket.end()` or `socket.destroy()` yourself). Also track connection count via `server.getConnections()` and consider implementing application-level heartbeats/pings for long-lived connections (common in WebSocket-like protocols) to detect half-open connections that the OS hasn't noticed yet.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Building custom binary/text protocols (chat servers, game servers, IoT)
- Writing a database driver or RPC client
- Need maximum performance without HTTP parsing overhead
- Building proxies, load balancers, or protocol gateways

❌ **Avoid when:**
- Building a standard REST API — use `http`/`express` instead
- You need built-in protocol semantics (caching, status codes, content negotiation) that HTTP already provides

---

## 📊 Visual Diagram

```
net MODULE — TCP SERVER LIFECYCLE:
──────────────────────────────────────────────────────

  net.createServer(socket => {...})
         │
         ▼
  server.listen(port) ──► OS binds to port, starts listening
         │
         ▼
  Client connects (TCP handshake: SYN, SYN-ACK, ACK)
         │
         ▼
  'connection' event fires → socket object created
         │
   ┌─────┴──────────────────────────────┐
   │                                     │
   ▼                                     ▼
socket.write(data)                socket.on('data', cb)
(send bytes to client)             (receive bytes from client)
   │                                     │
   └─────────────┬───────────────────────┘
                 ▼
         socket.end() / socket.destroy()
                 │
                 ▼
         'close' event → connection fully closed

  STACK:  http module
             │  (built on top of)
          net module
             │  (built on top of)
          OS TCP/IP sockets
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Socket | Bidirectional TCP connection endpoint | TCP connection का endpoint |
| `net.createServer()` | Creates a raw TCP server | Raw TCP server बनाता है |
| Byte Stream | Ordered bytes, no message boundary | Ordered bytes, कोई message boundary नहीं |
| Framing | App-level message boundary technique | Message boundary बनाने की technique |
| Duplex Stream | Readable + Writable combined | Read और Write दोनों |
| ECONNRESET | Connection abruptly reset error | Connection अचानक reset होने का error |
| Length-prefix | Framing technique using byte-length header | Length header से framing |

---

## ⚡ 3-Line Summary
English:
1. `net` is Node's low-level TCP module — raw sockets, no HTTP abstraction; `http` is built on top of it.
2. TCP is a byte stream with no message boundaries — you must implement your own framing (length-prefix or delimiter) to split messages reliably.
3. Use `net` for custom protocols, database drivers, or performance-critical internal services; use `http`/Express for standard REST APIs.

Hindi:
1. `net` Node का low-level TCP module है — raw sockets, कोई HTTP abstraction नहीं; `http` इसी के ऊपर बना है।
2. TCP byte stream है, message boundary नहीं देता — reliable messaging के लिए अपना framing (length-prefix/delimiter) बनाना पड़ता है।
3. Custom protocols, DB drivers, performance-critical internal services के लिए `net` use करो; standard REST API के लिए `http`/Express।

---

## ➡️ Next Topic
**66. Event Loop — Complete Guide** — How Node.js schedules and executes all this async I/O (including net sockets) via its single-threaded event loop।
