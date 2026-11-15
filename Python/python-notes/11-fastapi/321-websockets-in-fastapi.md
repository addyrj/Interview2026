---

# 321. WebSockets in FastAPI
# हिंदी में: FastAPI में WebSockets (दो-तरफ़ा real-time connection)

---

## 🔵 Simple Definition (English)
A WebSocket is a long-lived two-way connection between browser and server. After one HTTP handshake, both sides can send messages at any time. FastAPI supports it with `@app.websocket` and the `WebSocket` object.

## 🔵 सरल परिभाषा (Hindi)
WebSocket browser और server के बीच लंबा चलने वाला दो-तरफ़ा connection है। एक HTTP handshake के बाद दोनों तरफ़ से कभी भी message भेजा जा सकता है। FastAPI में `@app.websocket` और `WebSocket` object से यह चलता है।

---

## 🔴 Problem it Solves
Plain HTTP is request-response: the server cannot push data. Chat, live cricket score, stock prices and typing indicators need the server to send updates instantly. Polling every second wastes bandwidth and adds delay. WebSockets keep one connection open.

## 🔴 यह क्यों बना? (Hindi)
सादा HTTP request-response है: server अपने आप data नहीं भेज सकता। Chat, live cricket score, stock price और typing indicator में server को तुरंत update भेजना होता है। हर second polling से bandwidth बर्बाद होती है और देरी होती है। WebSocket एक connection खुला रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends an HTTP Upgrade request (ws:// or wss://)
Step 2 → Handler runs `await ws.accept()` to complete the handshake
Step 3 → Loop: `await ws.receive_text()` / `send_text()` / `receive_json()` / `send_json()`
Step 4 → Either side may send at any time (full duplex)
Step 5 → Client leaves → `WebSocketDisconnect` is raised in your loop
Step 6 → Clean up (remove from manager) and optionally `ws.close(code)`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client HTTP Upgrade request भेजता है (ws:// या wss://)
Step 2 → Handler में `await ws.accept()` से handshake पूरा होता है
Step 3 → Loop: `await ws.receive_text()` / `send_text()` / `receive_json()` / `send_json()`
Step 4 → कोई भी पक्ष कभी भी message भेज सकता है (full duplex)
Step 5 → Client चला जाए तो loop में `WebSocketDisconnect` raise होता है
Step 6 → Cleanup करें (manager से हटाएँ) और चाहें तो `ws.close(code)`
```

---

## 🟡 Real World Example
Zomato-style live order tracking: the delivery app pushes GPS points and the customer page shows the rider moving. A team chat (Slack clone), a collaborative whiteboard, a live auction with bids, and token-by-token LLM chat UIs also use WebSockets.

## 🟡 Real Example Hindi mein
Zomato जैसी live order tracking: delivery app GPS points भेजता है और customer page पर rider चलता दिखता है। Team chat (Slack clone), collaborative whiteboard, live auction और token-by-token LLM chat UI भी WebSocket इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
Echo server: accept, receive one message, reply, close.

```python
# Basic WebSocket echo - every line commented
from fastapi import FastAPI, WebSocket  # app and WebSocket type
from fastapi.testclient import TestClient  # supports websocket_connect

app: FastAPI = FastAPI()  # create app


@app.websocket("/ws")  # websocket route (not @app.get)
async def echo(ws: WebSocket) -> None:  # handler gets the connection
    await ws.accept()  # complete the handshake
    msg: str = await ws.receive_text()  # wait for a text message
    await ws.send_text(f"echo: {msg}")  # reply
    await ws.close()  # close the connection


client: TestClient = TestClient(app)  # client
with client.websocket_connect("/ws") as conn:  # open a ws connection
    conn.send_text("hello")  # send
    print(conn.receive_text())  # read reply
# Output: echo: hello
```

## 💻 Code Example — Advanced
Chat rooms with a ConnectionManager, path params, broadcast and proper disconnect cleanup.

```python
# Production style: chat room with a ConnectionManager and disconnect handling
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # tools
from fastapi.testclient import TestClient  # test client


class ConnectionManager:  # keeps track of connected clients
    def __init__(self) -> None:  # constructor
        self.rooms: dict[str, list[WebSocket]] = {}  # room name -> sockets

    async def connect(self, room: str, ws: WebSocket) -> None:  # add a client
        await ws.accept()  # accept first
        self.rooms.setdefault(room, []).append(ws)  # register

    def disconnect(self, room: str, ws: WebSocket) -> None:  # remove a client
        self.rooms[room].remove(ws)  # forget it

    async def broadcast(self, room: str, text: str) -> None:  # send to everyone in the room
        for ws in list(self.rooms.get(room, [])):  # copy list, it may change
            await ws.send_text(text)  # send


manager: ConnectionManager = ConnectionManager()  # one manager per process
app: FastAPI = FastAPI()  # app


@app.websocket("/ws/{room}/{user}")  # path params work in websockets
async def chat(ws: WebSocket, room: str, user: str) -> None:  # handler
    await manager.connect(room, ws)  # join
    await manager.broadcast(room, f"{user} joined")  # announce
    try:  # loop until client leaves
        while True:  # keep receiving
            text: str = await ws.receive_text()  # wait for message
            await manager.broadcast(room, f"{user}: {text}")  # fan out
    except WebSocketDisconnect:  # client closed
        manager.disconnect(room, ws)  # cleanup
        await manager.broadcast(room, f"{user} left")  # tell others


client: TestClient = TestClient(app)  # client
with client.websocket_connect("/ws/dev/asha") as a:  # first user joins
    print(a.receive_text())  # own join message
    # Output: asha joined
    with client.websocket_connect("/ws/dev/ravi") as b:  # second user joins
        print(a.receive_text(), "|", b.receive_text())  # both see ravi joined
        # Output: ravi joined | ravi joined
        b.send_text("hi")  # ravi talks
        print(a.receive_text(), "|", b.receive_text())  # both get it
        # Output: ravi: hi | ravi: hi
    print(a.receive_text())  # ravi disconnected
    # Output: ravi left
print(manager.rooms)  # all cleaned up
# Output: {'dev': []}
```

---

## 🟠 JavaScript vs Python Comparison

```python
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    async for text in ws.iter_text():   # ends on disconnect
        await ws.send_text(text)
```

```javascript
// Node 'ws' library
const wss = new WebSocketServer({ port: 8080 });
wss.on('connection', (socket) => {
  socket.on('message', (msg) => socket.send(msg.toString()));
});
// browser: const s = new WebSocket('ws://localhost:8000/ws');
```

Node uses event callbacks (`on('message')`); FastAPI uses an `async` loop with `await`. The browser client code (`new WebSocket(...)`) is the same for both servers. In FastAPI, a normal `async for` over `iter_text()` ends cleanly on disconnect.

---

## 🟠 FastAPI Connection
WebSocket routes support path/query params and `Depends`, but not `response_model` or HTTP status codes. Browsers cannot send an `Authorization` header from `new WebSocket()`, so pass a token in the query string or first message and validate it before `accept()`. Each worker process has its own connection list: for many workers use Redis pub/sub to broadcast.

```python
from fastapi import FastAPI, Query, WebSocket, WebSocketException, status

app: FastAPI = FastAPI()


@app.websocket("/ws/orders/{order_id}")
async def track(ws: WebSocket, order_id: int, token: str = Query(...)) -> None:
    if token != "valid-token":  # check BEFORE accept
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    await ws.accept()
    async for text in ws.iter_text():  # loop ends on disconnect
        await ws.send_json({"order": order_id, "echo": text})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `accept()`
```python
@app.websocket('/ws')
async def w(ws: WebSocket):
    await ws.send_text('hi')  # RuntimeError
```
✅ Correct:
```python
await ws.accept()
await ws.send_text('hi')
```

❌ Mistake 2: Not handling disconnect
```python
while True:
    text = await ws.receive_text()  # crashes with WebSocketDisconnect, no cleanup
```
✅ Correct:
```python
try:
    while True:
        text = await ws.receive_text()
except WebSocketDisconnect:
    manager.disconnect(ws)
```

❌ Mistake 3: Blocking calls inside the handler
```python
async def w(ws):
    time.sleep(5)  # freezes every connection
```
✅ Correct:
```python
await asyncio.sleep(5)  # or asyncio.to_thread(blocking_fn)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.send_text("hi")

c = TestClient(app)
try:
    with c.websocket_connect("/ws") as conn:
        print(conn.receive_text())
except Exception as e:
    print(type(e).__name__, e)
```

**Answer**:
```
RuntimeError Expected ASGI message "websocket.accept", "websocket.close" or "websocket.http.response.start", but got 'websocket.send'
```
Sending before `accept()` breaks the protocol, so Starlette raises `RuntimeError` complaining it expected accept/close. The handshake is not complete until you call `await websocket.accept()`.

---

## ⚫ Interview Questions + Answers

Q1: WebSocket vs HTTP polling?
A1: Polling repeats requests and wastes bandwidth/latency. WebSocket keeps one connection, with messages both ways in real time.

Q2: WebSocket vs SSE?
A2: SSE is one-way (server to client) over plain HTTP with auto-reconnect. WebSocket is two-way and binary-capable. Pick SSE if only the server talks.

Q3: How do you authenticate a WebSocket?
A3: Browsers cannot set custom headers. Send a short-lived token in the query string, a cookie, or the first message, and verify before `accept()` (raise `WebSocketException`).

Q4: How do you scale to many servers?
A4: Each process knows only its own sockets. Use Redis pub/sub (or a broker) so a message published on one worker is delivered to clients on all workers.

Q5: What happens when the client disconnects?
A5: `receive_*` raises `WebSocketDisconnect` (`iter_text()` just ends). Catch it and clean up.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Chat, live tracking, collaborative editing
- Both sides send frequent small messages
- Live dashboards needing sub-second latency

❌ Avoid when:
- Server-only push (SSE is simpler)
- Rare updates (plain HTTP is fine)
- When proxies/load balancers are not configured for upgrades

---

## 📊 Visual Diagram

```
Client                           FastAPI
  | GET /ws  Upgrade: websocket   |
  | ----------------------------> |
  | <---------------------------- |  101 Switching Protocols (accept)
  | <==== text / json frames ====> |  full duplex, any time
  | close frame / network drop     |
  | ----------------------------> |  WebSocketDisconnect -> cleanup
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebSocket | Persistent two-way connection | स्थायी दो-तरफ़ा connection |
| Handshake | HTTP upgrade step | शुरुआती upgrade चरण |
| accept() | Finish the handshake | handshake पूरा करना |
| Broadcast | Send to many clients | कई clients को भेजना |
| WebSocketDisconnect | Raised when client leaves | client जाने पर आने वाला error |
| Pub/Sub | Publish-subscribe messaging | प्रकाशित-सदस्यता messaging |

---

## ⚡ 3-Line Summary
English: WebSockets give a long-lived, two-way connection: `accept()`, then receive/send in a loop. Always handle `WebSocketDisconnect` and keep a manager for rooms. Scale across workers with Redis pub/sub.
Hindi: WebSocket लंबा, दो-तरफ़ा connection देता है: `accept()` फिर loop में receive/send। `WebSocketDisconnect` ज़रूर संभालें और rooms के लिए manager रखें। कई workers के लिए Redis pub/sub इस्तेमाल करें।

---

## ➡️ Next Topic
**322. Server-Sent Events** — simpler one-way streaming from server to browser.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output. WebSocket tests ran through TestClient.websocket_connect, not a real browser or network.
