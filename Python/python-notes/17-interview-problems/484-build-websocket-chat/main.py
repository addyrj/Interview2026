"""Build WebSocket Chat: rooms + broadcast with FastAPI. Run: python main.py (self-test)."""
from __future__ import annotations

from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient


class ConnectionManager:
    """Keeps track of live sockets per room and broadcasts messages."""

    def __init__(self) -> None:
        self.rooms: dict[str, dict[WebSocket, str]] = defaultdict(dict)  # room -> {socket: username}

    async def connect(self, room: str, user: str, ws: WebSocket) -> None:
        await ws.accept()  # complete the WebSocket handshake
        self.rooms[room][ws] = user  # remember who is in the room

    def disconnect(self, room: str, ws: WebSocket) -> str:
        user = self.rooms[room].pop(ws, "?")  # forget the socket
        if not self.rooms[room]:
            del self.rooms[room]  # drop empty rooms
        return user

    async def broadcast(self, room: str, message: dict[str, str]) -> None:
        for ws in list(self.rooms.get(room, {})):  # copy: dict may change while sending
            try:
                await ws.send_json(message)  # push to one client
            except Exception:
                self.rooms[room].pop(ws, None)  # dead socket: remove it


app = FastAPI()
manager = ConnectionManager()


@app.websocket("/ws/{room}/{user}")
async def chat(ws: WebSocket, room: str, user: str) -> None:
    await manager.connect(room, user, ws)
    await manager.broadcast(room, {"type": "join", "user": user, "text": f"{user} joined"})
    try:
        while True:
            text = await ws.receive_text()  # wait for next client message
            await manager.broadcast(room, {"type": "msg", "user": user, "text": text})
    except WebSocketDisconnect:
        manager.disconnect(room, ws)
        await manager.broadcast(room, {"type": "leave", "user": user, "text": f"{user} left"})


def _self_test() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws/general/asha") as a:
        print(a.receive_json())  # asha's own join
        with client.websocket_connect("/ws/general/ravi") as b:
            print(a.receive_json())  # asha sees ravi join
            print(b.receive_json())  # ravi sees his join
            a.send_text("hello ravi")
            ma, mb = a.receive_json(), b.receive_json()
            print(ma)
            assert ma == mb == {"type": "msg", "user": "asha", "text": "hello ravi"}
        print(a.receive_json())  # ravi left
    with client.websocket_connect("/ws/other/zoya") as c:
        c.receive_json()
        c.send_text("alone")
        print(c.receive_json())  # rooms are isolated
    assert not manager.rooms or all(not r for r in manager.rooms.values())
    print("all ok")


if __name__ == "__main__":
    _self_test()
