---

# Q234. Streaming response
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐

---

## ❓ Question
Return a large or slow response in chunks using `StreamingResponse`: an async generator producing lines, a CSV download via a sync generator with `Content-Disposition`, and a file-like object.

---

## 💡 Quick Concept (2 lines only)
`StreamingResponse` takes a generator and sends each chunk as it is produced, so memory stays flat and the client starts receiving early. No `Content-Length` -> chunked transfer.
हिंदी: `StreamingResponse` generator से chunk-by-chunk भेजता है — बड़ी file/CSV में memory बचती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # simulated I/O delay
import io  # in-memory file
from collections.abc import AsyncIterator, Iterator  # generator types
from fastapi import FastAPI  # app
from fastapi.responses import StreamingResponse  # streaming
from fastapi.testclient import TestClient  # client

app = FastAPI()  # app

async def number_stream(n: int) -> AsyncIterator[bytes]:  # async generator = chunks
    for i in range(n):  # produce n chunks
        await asyncio.sleep(0.01)  # simulate slow producer
        yield f"line {i}\n".encode()  # each yield is sent immediately

@app.get("/stream")  # route
async def stream(n: int = 3) -> StreamingResponse:  # returns streaming response
    return StreamingResponse(number_stream(n), media_type="text/plain")  # body is NOT built in memory

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client
with client.stream("GET", "/stream", params={"n": 3}) as r:  # stream on the client side too
    chunks = [c for c in r.iter_text()]  # read chunks as they arrive
    print(r.status_code, r.headers["content-type"])  # Expected: 200 text/plain; charset=utf-8
print("".join(chunks))  # Expected: line 0 / line 1 / line 2 (3 lines)
print(r.headers.get("content-length"))  # Expected: None (unknown length -> chunked)
```

---

## 🔍 Why This Works (3 lines max)
The generator is iterated by the server while writing the response; each `yield` is flushed to the client. Sync generators run in a threadpool, async ones on the event loop. With no known length, the response has no `Content-Length` header.
हिंदी: हर `yield` तुरंत client को जाता है; length पता न होने से `Content-Length` header नहीं होता।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: sync generator + file download with header ----
app2 = FastAPI()  # app

def csv_rows() -> Iterator[str]:  # plain generator (runs in threadpool)
    yield "id,name\n"  # header row
    for i in range(1, 4):  # data rows
        yield f"{i},user{i}\n"  # one row at a time

@app2.get("/export.csv")  # route
def export() -> StreamingResponse:  # sync route is fine for sync generator
    return StreamingResponse(  # build response
        csv_rows(), media_type="text/csv",  # csv type
        headers={"Content-Disposition": 'attachment; filename="users.csv"'},  # triggers download
    )

r2 = TestClient(app2).get("/export.csv")  # call
print(r2.headers["content-disposition"])  # Expected: attachment; filename="users.csv"
print(r2.text)  # Expected: id,name / 1,user1 / 2,user2 / 3,user3

# file-like object works too
app3 = FastAPI()  # app

@app3.get("/f")  # route
async def f() -> StreamingResponse:  # handler
    return StreamingResponse(io.BytesIO(b"abcdef"), media_type="application/octet-stream")  # file-like

print(TestClient(app3).get("/f").content)  # Expected: b'abcdef'
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: building the whole payload in a list/string first, then streaming it (defeats the purpose)
rows = [make_row(i) for i in range(10_000_000)]
return StreamingResponse(iter(rows))

# ❌ Wrong: time.sleep / blocking DB calls inside an async generator -> freezes the event loop
# ✅ Correct: yield rows lazily; use await asyncio.sleep / async drivers inside async generators
```

---

## 🎯 Interview Tip (1 line)
Say: "Stream generators for big exports or slow producers; mind blocking calls inside async generators and set Content-Disposition for downloads."

---

## 🔗 Related Questions
→ Q220 (async generators) | Q235 (SSE) | Q228 (file upload) | Q279 (generators vs lists)
