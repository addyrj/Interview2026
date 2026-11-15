---

# 484. Build WebSocket Chat
# हिंदी में: WebSocket Chat बनाना (rooms + broadcast)

Full runnable solution: [main.py](main.py) (FastAPI + `TestClient.websocket_connect`, self-test included).

---

## 🔵 Simple Definition (English)
A WebSocket chat keeps one long-lived two-way connection per user. The server remembers who is in which room and pushes every new message to all of them instantly, without the client asking again.

## 🔵 सरल परिभाषा (Hindi)
WebSocket chat में हर user का एक लंबा, दो-तरफ़ा connection खुला रहता है। Server याद रखता है कि कौन किस room में है और हर नया message सब को तुरंत push कर देता है, client को बार-बार पूछना नहीं पड़ता।

---

## 🔴 Problem it Solves
HTTP is request/response: the server cannot talk first. Chat over HTTP needed polling every second, which wastes bandwidth, adds delay and loads the server. WebSockets keep one TCP connection open so either side can send at any time.

## 🔴 यह क्यों बना? (Hindi)
HTTP में पहले client माँगता है, तब server जवाब देता है; server खुद पहले नहीं बोल सकता। Chat के लिए हर सेकंड polling करनी पड़ती थी, जिससे bandwidth बर्बाद होती, देरी होती और server पर load बढ़ता। WebSocket एक connection खुला रखता है, इसलिए कोई भी तरफ़ कभी भी भेज सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends HTTP "Upgrade: websocket" request to /ws/{room}/{user}
Step 2 → Server calls ws.accept(): connection becomes a WebSocket
Step 3 → ConnectionManager stores socket in rooms[room][ws] = user
Step 4 → Server loops: text = await ws.receive_text()
Step 5 → manager.broadcast(room, message) -> await ws.send_json() for each socket
Step 6 → Client leaves -> WebSocketDisconnect -> remove socket, tell the room
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client /ws/{room}/{user} पर HTTP Upgrade request भेजता है
Step 2 → Server ws.accept() करता है, connection WebSocket बन जाता है
Step 3 → ConnectionManager socket को rooms[room][ws] = user में रखता है
Step 4 → Server loop में await ws.receive_text() से message का इंतज़ार करता है
Step 5 → broadcast() उस room के हर socket को send_json() करता है
Step 6 → Client निकले तो WebSocketDisconnect आता है, socket हटता है और room को बताया जाता है
```

---

## 🟡 Real World Example
Swiggy delivery chat between customer and rider, a Zerodha live-price ticker, or a support widget on a Razorpay dashboard. Each order id is a "room", so only the customer and the rider of that order see the messages. In production the room map moves to Redis pub/sub so several server processes can share rooms.

## 🟡 Real Example Hindi mein
Swiggy में customer और rider की chat, Zerodha का live price ticker या Razorpay dashboard का support widget। हर order id एक "room" होता है, इसलिए सिर्फ़ उसी order के customer और rider को messages दिखते हैं। Production में rooms की list Redis pub/sub में जाती है ताकि कई server processes room share कर सकें।

---

## 💻 Code Example — Basic
```python
# Minimal echo WebSocket, tested without a browser
from fastapi import FastAPI, WebSocket  # FastAPI app and the WebSocket type
from fastapi.testclient import TestClient  # in-process client, no real server

app = FastAPI()  # create the app

@app.websocket("/echo")  # a websocket route, not an HTTP route
async def echo(ws: WebSocket) -> None:  # ws is the live connection
    await ws.accept()  # finish the handshake
    text: str = await ws.receive_text()  # wait for one client message
    await ws.send_text(f"echo: {text}")  # send it back

with TestClient(app).websocket_connect("/echo") as client:  # open a socket
    client.send_text("hi")  # client -> server
    print(client.receive_text())  # server -> client
# Output: echo: hi
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: rooms + broadcast + cleanup (full file runs and asserts)
class ConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, dict[WebSocket, str]] = defaultdict(dict)  # room -> {socket: user}

    async def connect(self, room: str, user: str, ws: WebSocket) -> None:
        await ws.accept()  # handshake
        self.rooms[room][ws] = user  # register

    def disconnect(self, room: str, ws: WebSocket) -> str:
        user = self.rooms[room].pop(ws, "?")  # unregister
        if not self.rooms[room]:
            del self.rooms[room]  # drop empty room
        return user

    async def broadcast(self, room: str, message: dict[str, str]) -> None:
        for ws in list(self.rooms.get(room, {})):  # copy: dict can change during send
            try:
                await ws.send_json(message)  # push to one client
            except Exception:
                self.rooms[room].pop(ws, None)  # dead socket: remove it
```
Real run of `python main.py` (Python 3.13.3, FastAPI + Starlette TestClient):
```
{'type': 'join', 'user': 'asha', 'text': 'asha joined'}
{'type': 'join', 'user': 'ravi', 'text': 'ravi joined'}
{'type': 'join', 'user': 'ravi', 'text': 'ravi joined'}
{'type': 'msg', 'user': 'asha', 'text': 'hello ravi'}
{'type': 'leave', 'user': 'ravi', 'text': 'ravi left'}
{'type': 'msg', 'user': 'zoya', 'text': 'alone'}
all ok
```
(The Starlette version installed prints a `StarletteDeprecationWarning` about `httpx`; it is harmless.)

---

## 🟠 JavaScript vs Python Comparison
Same idea as `ws` / Socket.IO rooms. In JS you keep a `Map` of sets; in Python a dict of dicts. The key difference: Python needs `await` on every send, and disconnect arrives as an exception, not an event.

```python
# Python way: disconnect is an exception
try:
    while True:
        text = await ws.receive_text()
except WebSocketDisconnect:
    manager.disconnect(room, ws)
```
```javascript
// JavaScript way: disconnect is an event
wss.on("connection", (ws) => {
  ws.on("message", (text) => broadcast(room, text));
  ws.on("close", () => rooms.get(room).delete(ws));
});
```

---

## 🟠 FastAPI Connection
FastAPI exposes `@app.websocket(path)`. Path parameters work as in HTTP routes. Auth is usually a token in the query string (`?token=...`) validated before `accept()`; close with `await ws.close(code=1008)` if invalid.

```python
@app.websocket("/ws/{room}")
async def secured(ws: WebSocket, room: str, token: str = "") -> None:
    if token != "secret":  # real apps verify a JWT here
        await ws.close(code=1008)  # 1008 = policy violation
        return
    await ws.accept()
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to remove disconnected sockets, so broadcast keeps failing on dead ones and memory grows.
✅ Correct: catch `WebSocketDisconnect`, remove the socket, and wrap `send_json` in try/except.

❌ Mistake 2: Iterating the dict directly while sockets leave.
✅ Correct: iterate over a copy.

```python
# Wrong
for ws in self.rooms[room]:      # RuntimeError: dictionary changed size during iteration
    await ws.send_json(msg)
# Right
for ws in list(self.rooms[room]):
    await ws.send_json(msg)
```

❌ Mistake 3: Keeping the room map in process memory and running 4 workers. Users on different workers never see each other.
✅ Correct: Redis pub/sub (or a broker) between workers.

---

## 🧠 Tricky Interview Question
Your chat works with 1 uvicorn worker, but with `--workers 4` half the messages are "lost". Why?

```python
manager = ConnectionManager()  # module level object
# uvicorn app:app --workers 4  -> 4 separate processes, 4 separate managers
```
Answer: Each worker process has its own `manager`. A user connected to worker 1 is invisible to worker 3, so a broadcast only reaches sockets on the same worker. Fix with Redis pub/sub: every worker publishes messages and subscribes to the channel, then forwards to its local sockets.

---

## ⚫ Interview Questions + Answers

Q1: WebSocket vs HTTP polling vs SSE?
A1: Polling repeats HTTP requests (wasteful). SSE is one-way server-to-client over HTTP. WebSocket is full duplex on one connection; best for chat and games.

Q2: How do you authenticate a WebSocket?
A2: Browsers cannot set custom headers on `new WebSocket()`, so send a short-lived token in the query string or a cookie, verify before `accept()`.

Q3: How do you scale chat to many servers?
A3: Sticky sessions are not enough; use a pub/sub backbone (Redis, Kafka, NATS) so any server can deliver to any room.

Q4: What if one client is slow?
A4: `await ws.send_json` blocks the broadcast loop. Use a per-connection send queue with a size limit and drop or disconnect slow clients.

Q5: How do you detect dead connections?
A5: Ping/pong heartbeats with a timeout; Uvicorn does this by default (`--ws-ping-interval`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Real-time two-way updates: chat, live location, collaborative editing, trading ticks

❌ Avoid when:
- Updates are rare or one-way (use SSE or normal polling)
- You cannot keep many open connections (serverless with short timeouts)

---

## 📊 Visual Diagram
```
 asha (browser) ──ws──┐                       ┌── ws ── ravi (browser)
                      ▼                       ▲
              ┌─────────────────────────────────────┐
              │ FastAPI  ConnectionManager          │
              │ rooms = {"general": {ws1:asha,      │
              │                      ws2:ravi}}     │
              └─────────────────────────────────────┘
   asha: "hello" ─► receive_text ─► broadcast(room) ─► send_json to ws1, ws2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebSocket | Persistent two-way connection | स्थायी दो-तरफ़ा connection |
| Handshake | HTTP upgrade to WebSocket | HTTP से WebSocket में बदलना |
| Broadcast | Send to everyone in a room | room में सबको भेजना |
| Room | Group of connections | connections का समूह |
| Pub/Sub | Publish-subscribe message bus | संदेश बाँटने का तरीका |

---

## ⚡ 3-Line Summary
English: A WebSocket keeps one connection open for instant two-way messages.
The ConnectionManager maps rooms to sockets and broadcasts to each.
Scale beyond one process with Redis pub/sub.
Hindi: WebSocket एक connection खुला रखता है ताकि messages तुरंत दोनों तरफ़ जाएँ।
ConnectionManager rooms को sockets से जोड़ता है और हर socket को broadcast करता है।
एक process से ज़्यादा पर scale करने के लिए Redis pub/sub चाहिए।

---

## ➡️ Next Topic
485. Build Background Job System: chat is real-time; heavy work (emails, reports) should run later in the background through a queue.

---
