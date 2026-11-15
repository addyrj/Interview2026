---

# Q227. WebSocket chat example
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐

---

## ❓ Question
Build a tiny WebSocket chat: clients connect to `/ws/{name}`, everyone is told when someone joins, and every message is broadcast to all connected clients. Clean up on disconnect. Test it with `TestClient`.

---

## 💡 Quick Concept (2 lines only)
A WebSocket is one long-lived two-way connection. Keep a list of active sockets in a manager, `accept()` on join, loop on `receive_*`, and remove the socket when `WebSocketDisconnect` fires.
हिंदी: WebSocket में connection खुला रहता है — manager सब sockets याद रखता है और message सबको broadcast करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # websocket types
from fastapi.testclient import TestClient  # supports websocket_connect

class Manager:  # keeps track of connected clients
    def __init__(self) -> None:  # init
        self.active: list[WebSocket] = []  # connected sockets

    async def connect(self, ws: WebSocket) -> None:  # on join
        await ws.accept()  # must accept handshake first
        self.active.append(ws)  # remember it

    def disconnect(self, ws: WebSocket) -> None:  # on leave
        self.active.remove(ws)  # forget it

    async def broadcast(self, text: str) -> None:  # send to everyone
        for ws in list(self.active):  # copy list: safe while mutating
            await ws.send_text(text)  # push message

app = FastAPI()  # app
manager = Manager()  # one shared manager

@app.websocket("/ws/{name}")  # websocket route with path param
async def chat(ws: WebSocket, name: str) -> None:  # handler
    await manager.connect(ws)  # join room
    await manager.broadcast(f"{name} joined")  # tell everybody
    try:  # loop until client leaves
        while True:  # keep receiving
            text = await ws.receive_text()  # wait for a message
            await manager.broadcast(f"{name}: {text}")  # fan out
    except WebSocketDisconnect:  # client closed
        manager.disconnect(ws)  # cleanup (important!)

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client
with client.websocket_connect("/ws/ann") as ann:  # ann connects
    print(ann.receive_text())  # Expected: ann joined
    with client.websocket_connect("/ws/bob") as bob:  # bob connects
        print(bob.receive_text())  # Expected: bob joined
        print(ann.receive_text())  # Expected: bob joined (ann also sees it)
        bob.send_text("hi")  # bob speaks
        print(ann.receive_text())  # Expected: bob: hi
        print(bob.receive_text())  # Expected: bob: hi
print(len(manager.active))  # Expected: 0 (all cleaned up)
```

---

## 🔍 Why This Works (3 lines max)
`await ws.accept()` completes the handshake, then `receive_text()` waits for frames inside a loop. When the client leaves, Starlette raises `WebSocketDisconnect` — we catch it and drop the socket so we never write to a dead connection.
हिंदी: Client के जाने पर `WebSocketDisconnect` आता है — उसे पकड़कर socket हटाओ, वरना memory leak होगा।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: send_json / receive_json ----
app2 = FastAPI()  # app

@app2.websocket("/echo")  # echo route
async def echo(ws: WebSocket) -> None:  # handler
    await ws.accept()  # handshake
    data = await ws.receive_json()  # parse JSON frame
    await ws.send_json({"echo": data})  # reply as JSON
    await ws.close()  # close politely

with TestClient(app2).websocket_connect("/echo") as w:  # connect
    w.send_json({"a": 1})  # send
    print(w.receive_json())  # Expected: {'echo': {'a': 1}}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no try/except WebSocketDisconnect -> dead sockets stay in the list,
#    next broadcast raises an error and breaks the chat for everyone
while True:
    text = await ws.receive_text()
    await manager.broadcast(text)

# ✅ Correct: wrap loop in try/except WebSocketDisconnect and call manager.disconnect(ws)
# ❌ Also wrong: iterating self.active while another task removes from it -> iterate over list(self.active)
```

---

## 🎯 Interview Tip (1 line)
Say: "One process keeps connections in memory; to scale to many servers I'd fan out through Redis pub/sub."

---

## 🔗 Related Questions
→ Q235 (SSE alternative) | Q216 (asyncio.Queue) | Q187 (event bus) | Q172 (async internals)
