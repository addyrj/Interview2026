# 163. WebSockets in JavaScript
# हिंदी में: JavaScript में WebSockets

---

## 🔵 Simple Definition (English)
A WebSocket is a single, long-lived connection between a browser (or any client) and a server. After a short HTTP handshake, both sides can send messages at any time, without making a new request each time. The browser API is `new WebSocket(url)`, and the URL starts with `ws://` (or `wss://` for TLS).

## 🔵 सरल परिभाषा (Hindi)
WebSocket browser (या कोई client) और server के बीच एक लंबे समय तक खुला रहने वाला connection है। एक छोटे HTTP handshake के बाद दोनों तरफ़ से कभी भी messages भेजे जा सकते हैं, हर बार नई request भेजने की ज़रूरत नहीं होती। Browser API `new WebSocket(url)` है, और URL `ws://` (या TLS के लिए `wss://`) से शुरू होता है।

---

## 🔴 Problem it Solves
HTTP is request-response: the client must ask first, and the server cannot speak up on its own. Before WebSockets, apps used polling (asking every few seconds) or long polling (holding a request open). Polling wastes bandwidth and adds delay, and it floods the server with empty requests. Live cricket scores, delivery partner location, stock prices, and chat all need the server to push updates the moment they happen. WebSockets give a full-duplex channel with low overhead after the first handshake.

## 🔴 यह क्यों बना? (Hindi)
HTTP में client पहले पूछता है, और server अपने-आप कुछ नहीं कह सकता। WebSockets से पहले apps polling (हर कुछ सेकंड में पूछना) या long polling (request को खुला रखना) करते थे। Polling में bandwidth बर्बाद होती है, delay आता है, और server पर खाली requests की बाढ़ आ जाती है। Live cricket score, delivery partner की location, stock prices और chat को तुरंत server से update चाहिए। WebSocket पहले handshake के बाद कम overhead पर दोनों तरफ़ का channel देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → The client calls `new WebSocket("ws://host/path")`. The state is `CONNECTING` (0).
Step 2 → The browser sends an HTTP GET with `Upgrade: websocket` headers.
Step 3 → The server replies `101 Switching Protocols`. The state becomes `OPEN` (1) and the `open` event fires.
Step 4 → Either side sends frames with `send()` or `ws.send()`. Messages arrive as `message` events.
Step 5 → When one side is done, `close()` starts the closing handshake (`CLOSING` 2, then `CLOSED` 3). The `close` event fires with a code, such as 1000 for normal.
Step 6 → The browser does NOT reconnect on its own. Your code must listen to `close` and create a new `WebSocket` if needed.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client `new WebSocket("ws://host/path")` call करता है। State `CONNECTING` (0) होती है।
Step 2 → Browser HTTP GET भेजता है, जिसमें `Upgrade: websocket` header होता है।
Step 3 → Server `101 Switching Protocols` देता है। State `OPEN` (1) हो जाती है और `open` event चलता है।
Step 4 → कोई भी side `send()` से frames भेजती है। Messages `message` event में आते हैं।
Step 5 → जब कोई side बंद करना चाहे, तो `close()` closing handshake शुरू करता है (`CLOSING` 2, फिर `CLOSED` 3)। `close` event एक code के साथ चलता है, जैसे normal बंद होने पर 1000।
Step 6 → Browser अपने-आप reconnect नहीं करता। अगर ज़रूरत हो, तो आपका code `close` सुनकर नया `WebSocket` बनाए।

---

## 🟡 Real World Example
Swiggy's live order tracking shows the delivery partner moving on the map. The server pushes a location update every few seconds over one open socket, instead of the app polling every five seconds. Zerodha-style trading screens push price ticks the same way. A chat feature in an e-commerce app, such as a Flipkart seller chat, sends each message over the open socket and gets delivery acknowledgements back on the same connection. If the train goes through a tunnel and the connection drops, the app reconnects and asks the server for missed updates.

## 🟡 Real Example Hindi mein
Swiggy की live order tracking में delivery partner का map पर चलना दिखता है। Server हर कुछ सेकंड में location update एक खुले socket पर push करता है, app हर पाँच सेकंड में poll नहीं करती। Zerodha जैसी trading screens भी इसी तरह price ticks push करती हैं। Flipkart के seller chat जैसे feature में हर message खुले socket से जाता है, और delivery acknowledgement उसी connection पर लौटता है। अगर connection टूट जाए, जैसे ट्रेन सुरंग से गुज़रे, तो app reconnect करके छूटे हुए updates माँगता है।

---

## 💻 Code Example — Basic
Node.js 22 or newer has a global `WebSocket` client, the same class browsers use. The server needs the `ws` package. Run: `npm install ws`, then `node websocket-basic.js`

```javascript
// websocket-basic.js — npm install ws; run: node websocket-basic.js
const { WebSocketServer } = require("ws");                  // WebSocket server class from the ws package
const wss = new WebSocketServer({ port: 8080 });            // server listens on port 8080

wss.on("connection", (socket) => {                          // runs for every new client connection
  console.log("server: client connected");                  // log the new connection
  socket.on("message", (data) => {                          // runs when this client sends a message
    const text = data.toString();                           // data is a Buffer, so convert to text
    console.log("server got:", text);                       // log what arrived
    socket.send(`echo: ${text}`);                           // reply to the same client
  });
  socket.on("close", () => console.log("server: client left")); // runs when this client disconnects
});

// Client: the same API that runs in the browser
const client = new WebSocket("ws://localhost:8080");        // starts the handshake (CONNECTING)

client.onopen = () => {                                     // fires once the handshake succeeds
  console.log("client: open, readyState =", client.readyState); // 1 means OPEN
  client.send("Hello server");                              // sending is safe only after onopen
};

client.onmessage = (event) => {                             // fires for each incoming message
  console.log("client got:", event.data);                   // prints "echo: Hello server"
  client.close();                                           // close our side politely
  wss.close();                                              // stop accepting new connections
};
```

## 💻 Code Example — Advanced
Browser-only page. Save it as `public/index.html`, then run the Express server from the Express section and open `http://localhost:3000`. The `ReconnectingSocket` class has no DOM code, so it can also be tested with Node 22+. It reconnects with exponential backoff, queues messages while offline, and flushes the queue in order after reconnecting.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                    <!-- text encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1"> <!-- phone width -->
  <title>Reconnecting WebSocket</title>
  <style>
    body { font-family: sans-serif; margin: 16px; }        /* page spacing */
    #log { border: 1px solid #ccc; height: 180px; overflow: auto; padding: 8px; } /* scrollable log */
  </style>
</head>
<body>
  <p>Status: <strong id="status">starting</strong></p>    <!-- connection state text -->
  <div id="log"></div>                                      <!-- received messages go here -->
  <input id="msg" placeholder="type a message">             <!-- message input -->
  <button id="send">Send</button>                           <!-- send button -->

  <script>
    // ---- Reusable class: no DOM code above the marker, so Node can test it ----
    class ReconnectingSocket {                              // wraps WebSocket with retries and a queue
      constructor(url, { onMessage, onStatus, maxDelay = 10000 } = {}) { // options object
        this.url = url;                                     // where to connect
        this.onMessage = onMessage || (() => {});           // callback for incoming data
        this.onStatus = onStatus || (() => {});             // callback for status text
        this.maxDelay = maxDelay;                           // upper limit for the wait time
        this.attempts = 0;                                  // failed attempts in a row
        this.queue = [];                                    // messages waiting while offline
        this.closedByUser = false;                          // true once close() is called
        this.connect();                                     // start the first attempt now
      }

      connect() {                                           // creates one socket for one attempt
        this.onStatus("connecting");                        // show progress
        this.ws = new WebSocket(this.url);                  // new socket each time
        this.ws.onopen = () => {                            // handshake succeeded
          this.attempts = 0;                                // reset the backoff counter
          this.onStatus("open");                            // show connected
          while (this.queue.length > 0) {                   // flush messages that waited offline
            this.ws.send(this.queue.shift());               // send the oldest first
          }
        };
        this.ws.onmessage = (event) => this.onMessage(event.data); // pass data to the app
        this.ws.onclose = () => {                           // connection ended for any reason
          if (this.closedByUser) return this.onStatus("closed"); // user chose to stop
          const delay = Math.min(this.maxDelay, 500 * 2 ** this.attempts); // 500, 1000, 2000... capped
          this.attempts++;                                  // one more failed attempt
          this.onStatus(`reconnecting in ${delay} ms`);     // show the wait time
          setTimeout(() => this.connect(), delay);          // try again later
        };
      }

      send(text) {                                          // public send method
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(text);                               // open: send immediately
        } else {
          this.queue.push(text);                            // not open: keep it for later
        }
      }

      close() {                                             // stop for good
        this.closedByUser = true;                           // stop reconnecting
        this.ws.close();                                    // close the current socket
      }
    }
    // ---- DOM part (browser only) below this line ----
    const statusEl = document.getElementById("status");     // status text element
    const log = document.getElementById("log");            // message log element
    const input = document.getElementById("msg");           // input element

    const socket = new ReconnectingSocket(                  // one socket for the whole page
      `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`, // same host, /ws path
      {
        onMessage: (text) => {                              // a message arrived
          const p = document.createElement("p");            // new paragraph element
          p.textContent = text;                             // textContent is safe from HTML injection
          log.appendChild(p);                               // add it to the log
          log.scrollTop = log.scrollHeight;                 // scroll to the newest line
        },
        onStatus: (text) => (statusEl.textContent = text),  // show status in the page
      }
    );

    document.getElementById("send").addEventListener("click", () => { // click handler
      if (input.value.trim() === "") return;                // ignore empty messages
      socket.send(input.value);                             // send or queue
      input.value = "";                                     // clear the input
    });
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Express and `ws` can share one HTTP server and one port. Express serves the page, and `ws` upgrades only the `/ws` path. The server also runs a heartbeat, which removes clients that stop answering pings. This is the server for the advanced page above.

```javascript
// server.js — npm install express ws; put the page in public/index.html; run: node server.js
const express = require("express");                         // web framework for HTTP routes
const http = require("http");                               // needed to share one server with ws
const path = require("path");                               // path helper
const { WebSocketServer, WebSocket } = require("ws");       // ws server and its constants

const app = express();                                      // create the express app
app.use(express.static(path.join(__dirname, "public")));    // serve public/index.html
app.get("/health", (req, res) => res.json({ ok: true, clients: wss.clients.size })); // quick status route

const server = http.createServer(app);                      // one HTTP server for express and ws
const wss = new WebSocketServer({ server, path: "/ws" });   // accept websocket upgrades only on /ws

wss.on("connection", (socket, req) => {                     // runs for each new browser connection
  socket.isAlive = true;                                    // heartbeat flag: true means it answered
  socket.on("pong", () => (socket.isAlive = true));         // a pong proves the client is still there
  console.log("client connected:", req.socket.remoteAddress); // log the address

  socket.on("message", (data) => {                          // a client sent a message
    const text = data.toString().slice(0, 500);             // limit the size of each message
    for (const client of wss.clients) {                     // broadcast to every connected client
      if (client.readyState === WebSocket.OPEN) client.send(text); // skip sockets that are closing
    }
  });
});

const heartbeat = setInterval(() => {                       // runs every 30 seconds
  for (const socket of wss.clients) {                       // check each connected client
    if (!socket.isAlive) {                                  // no pong since the last check
      socket.terminate();                                   // drop the dead connection
      continue;                                             // move to the next client
    }
    socket.isAlive = false;                                 // require a new pong before next check
    socket.ping();                                          // ask the client to answer
  }
}, 30000);

wss.on("close", () => clearInterval(heartbeat));            // stop the timer when the server closes
server.listen(3000, () => console.log("http://localhost:3000")); // start listening
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Sending before the connection is open
✅ Correct: While `readyState` is `CONNECTING`, `send()` throws `InvalidStateError`. Send inside `onopen`, or use a queue like `ReconnectingSocket`.

```javascript
// Wrong — the socket is still CONNECTING, so send() throws
const ws = new WebSocket("ws://localhost:8080");
ws.send("hello");                                          // InvalidStateError

// Right — wait for the open event
const ws2 = new WebSocket("ws://localhost:8080");
ws2.onopen = () => ws2.send("hello");                      // safe: state is OPEN
```

❌ **Mistake 2:** Assuming the browser reconnects automatically
✅ Correct: After a drop, the `close` event fires and no new socket is created. Your code must reconnect, with a delay that grows each time.

```javascript
// Wrong — the app goes silent forever after one network drop
const ws3 = new WebSocket("ws://localhost:8080");

// Right — reconnect with a growing delay
function connect(attempt = 0) {
  const ws4 = new WebSocket("ws://localhost:8080");        // a new socket for each attempt
  ws4.onclose = () => setTimeout(() => connect(attempt + 1), Math.min(10000, 500 * 2 ** attempt)); // retry later
}
connect();
```

❌ **Mistake 3:** Treating each `message` event as JSON without checking
✅ Correct: `event.data` is a string for text frames and a `Blob` or `ArrayBuffer` for binary. Parse JSON inside a `try` block, because a bad message must not stop the app.

```javascript
// Wrong — one malformed message throws and breaks the handler
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);                           // throws on bad input
  render(msg);
};

// Right — guard the parse
ws.onmessage = (e) => {
  try {
    render(JSON.parse(e.data));                             // only valid JSON gets rendered
  } catch {
    console.warn("ignored a non-JSON message");             // log and move on
  }
};
function render(m) { console.log("render", m); }           // placeholder for the UI
```

---

## 🧠 Tricky Interview Question
Run this in Node 22+ (`node tricky-ws.js`). Nothing listens on port 1, so the connection fails.

```javascript
// tricky-ws.js — run with: node tricky-ws.js (Node 22+ has global WebSocket)
const ws = new WebSocket("ws://localhost:1");              // connection attempt starts now
console.log(ws.readyState, WebSocket.OPEN);                // 0 and 1
try {                                                       // catch errors from send
  ws.send("hi");                                            // called while CONNECTING
  console.log("sent");                                      // never printed
} catch (e) {
  console.log(e.name);                                      // InvalidStateError
}
ws.onerror = () => console.log("error event");              // fires when the connection fails
ws.onclose = () => console.log("close event");              // fires after the error
```

Answer: The output is:
```
0 1
InvalidStateError
error event
close event
```
Explanation: A new `WebSocket` starts in `CONNECTING` (state 0), not `OPEN` (state 1). Calling `send()` in that state throws an `InvalidStateError` synchronously, so `sent` is never printed. The connection then fails asynchronously, so the `error` event fires first, and the `close` event follows. The failure happens later on the event loop, which is why the handlers are attached without a problem. Browsers report the close code as 1006 (abnormal closure), and Node may report a different code, so do not depend on the number.

---

## ⚫ Interview Questions + Answers

Q1: How is a WebSocket different from HTTP?
A1: HTTP is request-response: the client must ask, then the server answers and the exchange ends. A WebSocket starts as an HTTP request, upgrades to a protocol that stays open, and lets both sides send messages at any time.

Q2: What does the `101 Switching Protocols` response mean?
A2: It is the server's agreement to upgrade the connection from HTTP to WebSocket. After this response, the same TCP connection carries WebSocket frames instead of HTTP messages.

Q3: What are the four `readyState` values?
A3: `CONNECTING` (0), `OPEN` (1), `CLOSING` (2), and `CLOSED` (3). Check `readyState === WebSocket.OPEN` before you send.

Q4: Does a WebSocket reconnect after the network drops?
A4: No. The browser API does not reconnect. You listen to `close` and create a new `WebSocket`, usually with exponential backoff, so that many clients do not reconnect at the same moment.

Q5: When would you choose Server-Sent Events or polling instead?
A5: Server-Sent Events are simpler when data flows only from server to client, such as a news ticker, because they use plain HTTP and reconnect automatically. Polling is fine for updates that come rarely, where a socket would be wasted.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The server must push updates many times per second, such as live tracking, scores, or prices
- Both sides send messages often, such as chat, collaborative editing, or games
- You need low latency and want to avoid a new HTTP request for each update

❌ Avoid when:
- Data comes once in a while; a plain `fetch` call or polling is simpler
- You only need one-way server to client updates; Server-Sent Events are easier to run behind proxies
- You have no plan for reconnect, heartbeat, and scaling across several server instances

---

## 📊 Visual Diagram
```
 Browser (client)                                  Server (Node + ws)
 ─────────────────                                 ──────────────────
 new WebSocket("ws://host/ws")
   │  GET /ws HTTP/1.1
   │  Upgrade: websocket ─────────────────────────►
   │                          ◄──── 101 Switching Protocols
   │  state = OPEN (1)                  state = OPEN
   │
   │  send("order: Paneer") ──────────────────────►  message event
   │                          ◄──────── send("ack: 101")
   │  message event (ack)
   │
   │          (network drops)
   │  close event (1006) ✕
   │  setTimeout(connect, 500 ms)
   │  new WebSocket(...)  ─────── new handshake ──►  connection event
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebSocket | Long-lived, two-way connection | लंबे समय तक खुला दो-तरफ़ा connection |
| Handshake | HTTP request that asks to upgrade | Upgrade माँगने वाली HTTP request |
| 101 Switching Protocols | Server agrees to the upgrade | Server का upgrade के लिए हामी भरना |
| Full-duplex | Both sides send at the same time | दोनों तरफ़ से एक साथ भेजना |
| readyState | Current state of the socket (0 to 3) | Socket की मौजूदा state (0 से 3) |
| Frame | One unit of data on the connection | Connection पर डेटा की एक इकाई |
| Heartbeat (ping/pong) | Checks that a client is still alive | Client ज़िंदा है यह जाँचना |
| Backoff | Waiting longer before each retry | हर retry से पहले ज़्यादा इंतज़ार |
| wss:// | WebSocket over TLS (encrypted) | TLS से encrypted WebSocket |

---

## ⚡ 3-Line Summary
**English:**
1. A WebSocket upgrades one HTTP request into a long-lived, two-way connection.
2. Wait for `open` before sending, and reconnect yourself after `close`, with backoff.
3. Use it for live, frequent, two-way updates, and use polling or Server-Sent Events when traffic is rare or one-way.

**Hindi:**
1. WebSocket एक HTTP request को लंबे समय तक चलने वाले दो-तरफ़ा connection में बदलता है।
2. भेजने से पहले `open` का इंतज़ार करें, और `close` के बाद backoff के साथ खुद reconnect करें।
3. Live और बार-बार होने वाले दो-तरफ़ा updates के लिए इसे चुनें; कम traffic या एक-तरफ़ा डेटा हो तो polling या Server-Sent Events चुनें।

---

## ➡️ Next Topic
**164. Canvas API Basics** — अब सीखेंगे कि browser में `<canvas>` पर pixels से drawing कैसे बनती है, जो charts, games और image editing की नींव है।
