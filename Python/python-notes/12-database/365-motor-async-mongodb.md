---

# 365. Motor — Async MongoDB
# हिंदी में: Motor — Async MongoDB (asyncio driver)

---

## 🔵 Simple Definition (English)
Motor is an asynchronous MongoDB driver for asyncio. Its API mirrors PyMongo, but each database call is awaited, so the event loop keeps serving other requests while MongoDB works. It is the usual choice for FastAPI with MongoDB.

## 🔵 सरल परिभाषा (Hindi)
Motor, asyncio के लिए asynchronous MongoDB driver है। इसका API PyMongo जैसा है, पर हर database call पर `await` लगता है, इसलिए MongoDB के काम करते समय event loop दूसरे requests को serve करता रहता है। FastAPI + MongoDB के लिए यह आम पसंद है।

---

## 🔴 Problem it Solves
PyMongo blocks the thread while waiting for the database. In an `async def` FastAPI endpoint that freezes the whole event loop, so one slow query delays every other user. Motor gives awaitable calls, so thousands of requests can wait on MongoDB at the same time on a single thread.

## 🔴 यह क्यों बना? (Hindi)
PyMongo database का इंतज़ार करते समय thread को block कर देता है। `async def` FastAPI endpoint में यह पूरे event loop को रोक देता है, इसलिए एक धीमी query हर दूसरे user को धीमा कर देती है। Motor awaitable calls देता है, इसलिए एक ही thread पर हजारों requests एक साथ MongoDB का इंतज़ार कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → client = AsyncIOMotorClient(uri)      create once (inside the running loop / lifespan)
Step 2 → col = client["db"]["collection"]       handles are plain objects, no await
Step 3 → result = await col.insert_one(doc)     methods that talk to the server are coroutines
Step 4 → doc = await col.find_one(filter)       single document
Step 5 → async for doc in col.find(filter): ... cursors are async-iterable
         or  docs = await cursor.to_list(length=100)
Step 6 → await asyncio.gather(q1, q2)           run independent queries concurrently
Step 7 → client.close() on shutdown
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → client = AsyncIOMotorClient(uri)      एक बार बनाओ (चल रहे loop / lifespan के अंदर)
Step 2 → col = client["db"]["collection"]       handles साधारण objects हैं, await नहीं चाहिए
Step 3 → result = await col.insert_one(doc)     server से बात करने वाले methods coroutines हैं
Step 4 → doc = await col.find_one(filter)       एक document
Step 5 → async for doc in col.find(filter): ... cursors async-iterable हैं
         या  docs = await cursor.to_list(length=100)
Step 6 → await asyncio.gather(q1, q2)           independent queries एक साथ चलाओ
Step 7 → shutdown पर client.close()
```

---

## 🟡 Real World Example
A chat backend on FastAPI stores messages in MongoDB through Motor: 5,000 users send messages at once and the event loop never blocks. A notification service reads a user's preferences and recent alerts with `asyncio.gather` so both queries run in parallel. An inventory service reserves stock with one atomic `update_one` so two buyers cannot take the last item.

## 🟡 Real Example Hindi mein
FastAPI पर बना chat backend messages को Motor से MongoDB में रखता है: 5,000 users एक साथ message भेजते हैं और event loop कभी block नहीं होता। Notification service user की preferences और हाल के alerts `asyncio.gather` से एक साथ पढ़ती है। Inventory service एक atomic `update_one` से stock reserve करती है ताकि दो buyers आखिरी item न ले सकें।

---

## 💻 Code Example — Basic
```python
# Basic Motor (async MongoDB) usage
import asyncio                                    # event loop
from motor.motor_asyncio import AsyncIOMotorClient   # async client


async def main() -> None:
    client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://127.0.0.1:34201", serverSelectionTimeoutMS=3000)   # create client
    col = client["shop_demo"]["products"]         # database + collection handles
    await col.drop()                              # clean demo state
    res = await col.insert_one({"sku": "A1", "price": 100, "stock": 5})   # awaitable insert
    print(type(res.inserted_id).__name__)         # ObjectId
    await col.insert_many([{"sku": "B2", "price": 250, "stock": 0},
                           {"sku": "C3", "price": 40, "stock": 9}])   # insert many
    doc = await col.find_one({"sku": "B2"}, {"_id": 0})   # await single read
    print(doc)                                    # plain dict
    cheap = [d["sku"] async for d in col.find({"price": {"$lt": 200}}).sort("price", 1)]   # async iteration over cursor
    print(cheap)                                  # ['C3', 'A1']
    print(await col.count_documents({"stock": {"$gt": 0}}))   # count in stock
    client.close()                                # close (not awaited)


asyncio.run(main())                               # start the loop

# Output:
# ObjectId
# {'sku': 'B2', 'price': 250, 'stock': 0}
# ['C3', 'A1']
# 2
```

## 💻 Code Example — Advanced
```python
# Production style: lifespan-managed client, concurrent queries, atomic update, error handling
import asyncio                                    # gather
from typing import Any                            # typing
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection   # motor types
from pymongo.errors import PyMongoError           # base driver error


async def reserve_stock(col: AsyncIOMotorCollection, sku: str, qty: int) -> bool:
    """Atomically decrement stock only if enough is left (no race condition)."""
    res = await col.update_one({"sku": sku, "stock": {"$gte": qty}}, {"$inc": {"stock": -qty}})   # check + update in ONE operation
    return res.modified_count == 1                # True when reservation worked


async def dashboard(col: AsyncIOMotorCollection) -> dict[str, Any]:
    """Run independent queries concurrently."""
    total, in_stock = await asyncio.gather(       # both queries in flight at once
        col.count_documents({}),                  # total products
        col.count_documents({"stock": {"$gt": 0}}),   # available products
    )
    return {"total": total, "in_stock": in_stock} # combined answer


async def main() -> None:
    client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://127.0.0.1:34201", serverSelectionTimeoutMS=3000)   # one client per app
    col: AsyncIOMotorCollection = client["shop_demo"]["products_prod"]   # collection
    await col.drop()                              # clean demo state
    await col.insert_many([{"sku": "A1", "stock": 5}, {"sku": "B2", "stock": 0}])   # seed
    results = await asyncio.gather(*[reserve_stock(col, "A1", 2) for _ in range(4)])   # 4 parallel buyers for 5 items
    print(sorted(results, reverse=True))          # only 2 can succeed (2+2, third needs 2 but 1 left)
    print((await col.find_one({"sku": "A1"}))["stock"])   # remaining stock
    print(await dashboard(col))                   # concurrent counts
    try:                                          # error handling
        bad = AsyncIOMotorClient("mongodb://127.0.0.1:1", serverSelectionTimeoutMS=300)   # unreachable
        await bad.admin.command("ping")           # triggers connection
    except PyMongoError as e:                     # driver errors share this base
        print("Error:", type(e).__name__)         # which error
    client.close()                                # cleanup


asyncio.run(main())                               # run

# Output (server running on a local test port):
# [True, True, False, False]
# 1
# {'total': 2, 'in_stock': 1}
# Error: ServerSelectionTimeoutError
```



---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (Motor) | JavaScript (Node driver) |
|---------|----------------|-------------------------|
| Calls | `await col.find_one(...)` | `await col.findOne(...)` |
| Cursor | `async for d in cursor` | `for await (const d of cursor)` |
| To list | `await cursor.to_list(100)` | `await cursor.toArray()` |
| Parallel | `asyncio.gather(a, b)` | `Promise.all([a, b])` |
| Close | `client.close()` | `await client.close()` |

```python
# Python way — asyncio.gather runs both queries at the same time
import asyncio                                     # event loop
from motor.motor_asyncio import AsyncIOMotorClient   # async driver
async def main() -> None:
    c = AsyncIOMotorClient("mongodb://127.0.0.1:34201")
    col = c.shop_demo.js_cmp2
    a, b = await asyncio.gather(col.count_documents({}), col.count_documents({"x": 1}))
    print(a, b)
    c.close()
asyncio.run(main())
```
```javascript
// JavaScript way — Promise.all
const [a, b] = await Promise.all([
  col.countDocuments({}),
  col.countDocuments({ x: 1 }),
]);
```

Key difference: it is the same mental model as Node (`await` + `Promise.all` equals `await` + `asyncio.gather`). But in Python you must run inside an event loop (`asyncio.run` or FastAPI), and a forgotten `await` does not fail loudly: you get a coroutine/future object instead of data.

---

## 🟠 FastAPI Connection
Create the `AsyncIOMotorClient` once in the FastAPI `lifespan` (startup) and close it at shutdown; keep it on `app.state`. Endpoints are `async def` and `await` every call. Convert `ObjectId` with `str()`. For production use one client per process, set `serverSelectionTimeoutMS`, and add timeouts. Note: Motor is in maintenance mode and MongoDB recommends the PyMongo Async API (`pymongo.AsyncMongoClient`, PyMongo 4.9+) for new projects; the calls look almost the same.

```python
# FastAPI + Motor: async endpoints, one client created in lifespan
from contextlib import asynccontextmanager       # lifespan
from bson import ObjectId                         # ids
from fastapi import FastAPI, HTTPException        # web
from fastapi.testclient import TestClient         # demo client
from motor.motor_asyncio import AsyncIOMotorClient   # async driver


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = AsyncIOMotorClient("mongodb://127.0.0.1:34201", serverSelectionTimeoutMS=3000)   # startup
    app.state.col = app.state.client["shop_demo"]["fa_motor"]
    await app.state.col.drop()
    yield
    app.state.client.close()                      # shutdown


app = FastAPI(lifespan=lifespan)


@app.post("/notes", status_code=201)
async def create(text: str) -> dict[str, str]:
    res = await app.state.col.insert_one({"text": text})   # non-blocking
    return {"id": str(res.inserted_id)}


@app.get("/notes")
async def list_notes(limit: int = 10) -> list[str]:
    cur = app.state.col.find({}, {"_id": 0}).limit(limit)   # cursor (no await yet)
    return [d["text"] async for d in cur]         # async iteration


with TestClient(app) as c:                        # 'with' runs lifespan startup/shutdown
    c.post("/notes", params={"text": "hello"}); c.post("/notes", params={"text": "world"})
    print(c.get("/notes").json())

# Output:
# ['hello', 'world']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `await`
✅ Correct: `await` every call that talks to the server

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
async def main():
    col = AsyncIOMotorClient("mongodb://127.0.0.1:34201").shop_demo.m3
    await col.insert_one({"a": 1})
    # Wrong — x is a Future, not a document
    x = col.find_one({"a": 1})
    print(type(x).__name__)           # Future
    # Right
    print((await x)["a"])             # 1
asyncio.run(main())
```

❌ Mistake 2: Awaiting a cursor
✅ Correct: iterate with `async for` or `await cursor.to_list(n)`

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
async def main():
    col = AsyncIOMotorClient("mongodb://127.0.0.1:34201").shop_demo.m3
    cur = col.find({})
    print(type(cur).__name__)         # AsyncIOMotorCursor
    try:
        await cur                     # Wrong
    except TypeError as e:
        print("TypeError")            # object AsyncIOMotorCursor can't be used in 'await' expression
    docs = await cur.to_list(length=10)   # Right (or: async for d in cur)
    print(len(docs))                  # 1
asyncio.run(main())
```

❌ Mistake 3: Check-then-update (race condition) for stock or balances
✅ Correct: put the condition inside ONE atomic update

```python
# Wrong — two requests can both read stock=1, then both decrement
doc = await col.find_one({"sku": "A1"})
if doc["stock"] >= 1:
    await col.update_one({"sku": "A1"}, {"$inc": {"stock": -1}})
# Right — condition and change happen atomically on the server
res = await col.update_one({"sku": "A1", "stock": {"$gte": 1}}, {"$inc": {"stock": -1}})
ok = res.modified_count == 1
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    col = AsyncIOMotorClient("mongodb://127.0.0.1:34201").shop_demo.t2
    await col.drop()
    await col.insert_one({"a": 1})
    cur = col.find({})
    print(type(cur).__name__)
    x = col.find_one({"a": 1})
    print(type(x).__name__)
    print((await x)["a"])

asyncio.run(main())
```
Answer: `AsyncIOMotorCursor`, `Future`, `1`. `find()` is NOT a coroutine: it returns a cursor immediately and the query only runs when you iterate. `find_one()` returns a Future that you must await, otherwise you hold a Future, not the document. Verified with Motor 3.7 (the exact type name of the awaitable may differ in other versions).

---

## ⚫ Interview Questions + Answers

Q1: Motor vs PyMongo?
A1: Same query language. PyMongo blocks; Motor returns awaitables for asyncio. Motor actually runs PyMongo in a thread pool internally (3.x), while the newer PyMongo Async API is natively async.

Q2: Why one client for the whole app?
A2: The client owns a connection pool and background monitoring tasks. Creating many clients wastes sockets and slows startup. Create it in `lifespan`, close at shutdown.

Q3: How do you run several queries concurrently?
A3: `await asyncio.gather(q1(), q2())`. Each query is independent so total time is about the slowest one rather than the sum.

Q4: How do you read many documents?
A4: `async for doc in col.find(...)` streams in batches (low memory). `await cursor.to_list(length=N)` loads up to N into a list; always pass a limit for user-facing endpoints.

Q5: How do you avoid race conditions on counters/stock?
A5: Use atomic operators (`$inc`) and put the guard in the filter (`{"stock": {"$gte": qty}}`), then check `modified_count`. For multi-document work use a transaction (needs a replica set).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `async def` FastAPI / Starlette / aiohttp apps using MongoDB
- High concurrency with many slow I/O waits
- You want `asyncio.gather` over several queries

❌ Avoid when:
- Simple scripts or sync frameworks (Flask/Django) - plain PyMongo is simpler
- CPU-heavy work in the same loop (async does not speed up CPU)
- Brand new projects may prefer `pymongo.AsyncMongoClient` since Motor is in maintenance mode

---

## 📊 Visual Diagram
```
request A --await col.find_one--> [event loop] <--- free to run request B
request B --await col.insert_one-->      |
                                          v
                               Motor sends queries over pooled sockets
                                          |
                                      MongoDB server
when a reply arrives -> the matching coroutine resumes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coroutine | Function you must `await` | जिस function को `await` करना पड़ता है |
| Event loop | Scheduler of async tasks | Async tasks का scheduler |
| `gather` | Run awaitables concurrently | Awaitables को एक साथ चलाना |
| Async cursor | Iterate results with `async for` | `async for` से results पढ़ना |
| Lifespan | App startup/shutdown hook | App के start/stop का hook |
| Atomic update | Check + change in one step | Check और बदलाव एक ही step में |

---

## ⚡ 3-Line Summary
English: Motor gives PyMongo's API with `await`, so MongoDB calls do not block the event loop. Create one client in the FastAPI lifespan, `await` every call, use `async for` or `to_list` for cursors, `asyncio.gather` for parallel queries, and atomic updates for counters.
Hindi: Motor, PyMongo का API `await` के साथ देता है, इसलिए MongoDB calls event loop को block नहीं करतीं। FastAPI lifespan में एक client बनाएं, हर call पर `await` लगाएं, cursors के लिए `async for` या `to_list`, parallel queries के लिए `asyncio.gather`, और counters के लिए atomic updates इस्तेमाल करें।

---

## ➡️ Next Topic
**366. MongoEngine** — an ODM (object-document mapper) that gives MongoDB schema, validation and model classes.
