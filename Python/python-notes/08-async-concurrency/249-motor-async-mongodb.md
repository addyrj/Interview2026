---

# 249. motor — Async MongoDB
# हिंदी में: motor — Async MongoDB Driver

---

## 🔵 Simple Definition (English)
`motor` is the async driver for MongoDB. It has the same style as PyMongo (collections, `find`, `insert_one`) but every database call is awaited, so the event loop is never blocked.
Version note: MongoDB has marked Motor as deprecated in favour of PyMongo's native async API (`pymongo.AsyncMongoClient`, PyMongo 4.9+ with stable support from 4.13). Motor 3.7.1 still works and is what existing FastAPI codebases use, so you must know both.

## 🔵 सरल परिभाषा (Hindi)
`motor` MongoDB का async driver है। इसका style PyMongo जैसा ही है (collections, `find`, `insert_one`), लेकिन हर database call पर `await` लगता है, इसलिए event loop कभी रुकता नहीं।
Version note: MongoDB ने Motor को deprecated घोषित किया है और उसकी जगह PyMongo का अपना async API (`pymongo.AsyncMongoClient`) लाया है। Motor 3.7.1 अभी भी चलता है और मौजूदा FastAPI projects में मिलता है, इसलिए दोनों जानना जरूरी है।

---

## 🔴 Problem it Solves
PyMongo is blocking: one slow `find()` freezes the whole async server. Running PyMongo in threads works but is clumsy. Motor wraps the driver so queries return awaitables and cursors can be used with `async for`, which fits naturally into FastAPI and asyncio.

## 🔴 यह क्यों बना? (Hindi)
PyMongo blocking है: एक धीमी `find()` पूरे async server को रोक देती है। PyMongo को threads में चलाना काम करता है पर बेढंगा है। Motor driver को ऐसे लपेटता है कि queries awaitable बनती हैं और cursors पर `async for` चलता है, जो FastAPI और asyncio में सहजता से बैठता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → AsyncIOMotorClient(uri) is created ONCE (it owns a connection pool)
Step 2 → db = client["shop"]; col = db["users"]   (no network call yet — lazy)
Step 3 → await col.insert_one(doc) sends the write, event loop stays free
Step 4 → col.find(filter) returns a cursor immediately (NOT awaited)
Step 5 → async for doc in cursor  OR  await cursor.to_list(length=N) fetches docs
Step 6 → await col.update_one / delete_one / aggregate for other operations
Step 7 → client.close() at shutdown
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → AsyncIOMotorClient(uri) सिर्फ एक बार बनता है (इसके पास connection pool है)
Step 2 → db = client["shop"]; col = db["users"]   (अभी network call नहीं — lazy)
Step 3 → await col.insert_one(doc) write भेजता है, event loop खाली रहता है
Step 4 → col.find(filter) तुरंत cursor देता है (इस पर await नहीं लगता)
Step 5 → async for doc in cursor  या  await cursor.to_list(length=N) से docs आते हैं
Step 6 → बाकी operations के लिए await col.update_one / delete_one / aggregate
Step 7 → Shutdown पर client.close()
```

---

## 🟡 Real World Example
A chat or notification service stores messages in MongoDB because each message has flexible fields. The FastAPI backend uses Motor to save new messages, list the last 50 for a user, and mark them as read, all without blocking other users. An analytics endpoint runs an `aggregate` pipeline (group by day, count) and returns the result.

## 🟡 Real Example Hindi mein
Chat या notification service messages MongoDB में रखती है क्योंकि हर message के fields अलग हो सकते हैं। FastAPI backend Motor से नए messages save करता है, किसी user के आखिरी 50 दिखाता है और उन्हें read mark करता है, सब बिना दूसरे users को रोके। Analytics endpoint `aggregate` pipeline (दिन के हिसाब से group, count) चलाकर नतीजा लौटाता है।

---

## 💻 Code Example — Basic
```python
# Basic motor example (verified against a local mongod 3.7.1 / Python 3.13)
# pip install motor
# Needs a running MongoDB at the URI below.
import asyncio                                           # event loop
from motor.motor_asyncio import AsyncIOMotorClient       # async client


async def main() -> None:
    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=3000)   # one client
    col = client["demo"]["users"]                        # database "demo", collection "users"
    await col.delete_many({})                            # start clean
    r = await col.insert_one({"name": "Asha", "age": 25})   # insert one document
    print(type(r.inserted_id).__name__)                  # the new _id type
    await col.insert_many([{"name": "Ravi", "age": 30}, {"name": "Meena", "age": 28}])   # many
    print(await col.find_one({"name": "Ravi"}, {"_id": 0}))   # one doc, hide _id
    names = [d["name"] async for d in col.find({"age": {"$gte": 28}}).sort("age", 1)]   # async for
    print(names)                                         # sorted by age
    res = await col.update_one({"name": "Asha"}, {"$inc": {"age": 1}})   # add 1 to age
    print(res.modified_count)                            # how many changed
    print(await col.count_documents({}))                 # total docs
    await client.drop_database("demo")                   # cleanup
    client.close()                                       # close the pool


asyncio.run(main())                                      # run

# Output:
# ObjectId
# {'name': 'Ravi', 'age': 30}
# ['Meena', 'Ravi']
# 1
# 3
```

## 💻 Code Example — Advanced
```python
# Production style: typed repository class, pagination, aggregate, error handling
import asyncio                                           # event loop
from typing import Any                                   # type hints
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection   # motor types
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError    # driver errors


class UserRepo:
    """Small data-access layer around the users collection."""

    def __init__(self, col: AsyncIOMotorCollection) -> None:
        self.col = col                                   # store the collection

    async def ensure_indexes(self) -> None:
        await self.col.create_index("email", unique=True)   # unique email, created once

    async def create(self, name: str, email: str, age: int) -> str:
        try:
            r = await self.col.insert_one({"name": name, "email": email, "age": age})   # insert
            return str(r.inserted_id)                    # ObjectId -> str for JSON
        except DuplicateKeyError:                        # unique index violated
            raise ValueError(f"email {email} already exists") from None   # clean business error

    async def list_page(self, skip: int, limit: int) -> list[dict[str, Any]]:
        cur = self.col.find({}, {"_id": 0}).sort("age", 1).skip(skip).limit(limit)   # cursor
        return await cur.to_list(length=limit)          # fetch at most `limit` docs

    async def avg_age(self) -> float:
        pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$age"}}}]   # aggregation
        out = [d async for d in self.col.aggregate(pipeline)]             # run + collect
        return out[0]["avg"] if out else 0.0             # handle empty collection


async def main() -> None:
    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=3000)   # client
    repo = UserRepo(client["demo"]["users"])             # repository
    try:
        await repo.col.delete_many({})                   # clean for the demo
        await repo.ensure_indexes()                      # unique index
        await repo.create("Asha", "a@x.com", 25)         # ok
        await repo.create("Ravi", "r@x.com", 30)         # ok
        try:
            await repo.create("Dup", "a@x.com", 40)      # same email
        except ValueError as e:
            print("Error:", e)                           # clean message
        print(await repo.list_page(0, 10))               # both docs, sorted by age
        print(await repo.avg_age())                      # average age
    except ServerSelectionTimeoutError:                  # mongod is down
        print("MongoDB not reachable")
    finally:
        await client.drop_database("demo")               # cleanup (demo only)
        client.close()                                   # close


asyncio.run(main())                                      # run

# Output (verified on a local mongod):
# Error: email a@x.com already exists
# [{'name': 'Asha', 'email': 'a@x.com', 'age': 25}, {'name': 'Ravi', 'email': 'r@x.com', 'age': 30}]
# 27.5
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (motor) | JavaScript (mongodb driver) |
|---------|----------------|----------------------------|
| Client | `AsyncIOMotorClient(uri)` | `new MongoClient(uri)` |
| Find many | `async for d in col.find()` | `await col.find().toArray()` |
| Find one | `await col.find_one()` | `await col.findOne()` |
| Insert | `insert_one` | `insertOne` |
| Cursor to list | `await cur.to_list(length=n)` | `.toArray()` |
| Naming | snake_case | camelCase |

```python
# Python way
docs = await col.find({"age": {"$gte": 18}}).to_list(length=100)   # list of dicts
```
```javascript
// JavaScript way
const docs = await col.find({ age: { $gte: 18 } }).limit(100).toArray();   // array of objects
```

Key difference: in Motor, `find()` itself is NOT awaited (it returns a cursor) but `find_one()` is. `to_list(length=None)` has no default limit, so always pass a length. Query documents are the same MongoDB JSON as JS.

---

## 🟠 FastAPI Connection
FastAPI + Motor is a very common stack. Create the client in `lifespan` and convert `ObjectId` to string before returning.

```python
# FastAPI example — Motor in lifespan
from contextlib import asynccontextmanager               # lifespan helper
from collections.abc import AsyncIterator                # type
from bson import ObjectId                                # id type
from bson.errors import InvalidId                        # bad id error
from fastapi import FastAPI, HTTPException, Request      # FastAPI
from motor.motor_asyncio import AsyncIOMotorClient       # driver


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")   # startup
    app.state.db = app.state.client["shop"]              # database handle
    yield                                                # run app
    app.state.client.close()                             # shutdown


app: FastAPI = FastAPI(lifespan=lifespan)                # app


@app.get("/users/{user_id}")                             # GET /users/<24-hex id>
async def get_user(user_id: str, request: Request) -> dict:
    try:
        oid = ObjectId(user_id)                          # validate the id format
    except InvalidId:
        raise HTTPException(422, "invalid id")           # bad input -> 422
    doc = await request.app.state.db.users.find_one({"_id": oid})   # query
    if doc is None:
        raise HTTPException(404, "not found")            # missing -> 404
    doc["id"] = str(doc.pop("_id"))                      # ObjectId is not JSON serializable
    return doc                                           # return dict
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Awaiting `find()` or forgetting to await `find_one()`
✅ Correct: `find()` returns a cursor (iterate it), `find_one()` is awaited

```python
# Wrong
docs = await col.find({})          # TypeError: object AsyncIOMotorCursor can't be used in 'await'
one = col.find_one({})             # a coroutine object, never runs
# Right
docs = await col.find({}).to_list(length=100)
one = await col.find_one({})
```

❌ Mistake 2: Returning `ObjectId` directly from FastAPI
✅ Correct: convert to `str` (or use a Pydantic model with a string id)

```python
# Wrong — fails with "ObjectId is not iterable / not serializable"
return await col.find_one({})
# Right
doc = await col.find_one({}); doc["_id"] = str(doc["_id"]); return doc
```

❌ Mistake 3: Creating a client per request
✅ Correct: one client per process; it manages the pool

```python
# Wrong
async def handler():
    client = AsyncIOMotorClient(uri)      # new pool every request
# Right: create in lifespan, share via app.state
```

---

## 🧠 Tricky Interview Question

```python
# What happens? (no mongod is running at this port)
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main() -> None:
    client = AsyncIOMotorClient("mongodb://127.0.0.1:1")   # line A
    print("client created")                                # line B
    await client.demo.users.find_one({})                   # line C

asyncio.run(main())
```
Answer: Line B prints `client created`, because creating the client is lazy: it does not connect. The error appears at line C when the first real operation runs, after `serverSelectionTimeoutMS` (default 30 seconds!) it raises `ServerSelectionTimeoutError`. In production set a small `serverSelectionTimeoutMS` so failures show up quickly.

---

## ⚫ Interview Questions + Answers

Q1: Is Motor truly async?
A1: Motor 3.x runs the PyMongo driver in a thread pool and exposes awaitable wrappers (this is why it is thread-pool bounded). The new PyMongo `AsyncMongoClient` is natively async (no thread pool). For most apps both are fine.

Q2: How do you fetch many documents?
A2: `async for d in col.find(q)` streams one by one (good for large results), or `await col.find(q).to_list(length=n)` loads up to n into memory.

Q3: How do you do pagination?
A3: `skip(n).limit(m)` is simple but slow for large skips. Better: range pagination on an indexed field, e.g. `find({"_id": {"$gt": last_id}}).sort("_id", 1).limit(m)`.

Q4: How do you run a transaction?
A4: `async with await client.start_session() as s: async with s.start_transaction(): await col.insert_one(doc, session=s)`. Transactions need a replica set (not a standalone mongod).

Q5: Motor or Beanie/ODM?
A5: Motor is the low-level driver. Beanie is an ODM built on top of Motor using Pydantic models. Use Motor for control, Beanie for less boilerplate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Async app (FastAPI/aiohttp) with MongoDB
- Flexible schema documents (chat, catalog, logs)
- Streaming large result sets with `async for`

❌ Avoid when:
- Data is strongly relational (use PostgreSQL + asyncpg)
- New greenfield project: prefer `pymongo.AsyncMongoClient` (Motor is deprecated)
- Sync scripts (plain PyMongo is simpler)

---

## 📊 Visual Diagram
```
FastAPI endpoint
     │ await
     ▼
AsyncIOMotorClient ── pool ──> MongoDB
     │
 db["shop"] ── col["users"]
     │
 col.find(q) ──> Cursor ──> async for doc ...   (lazy, batch by batch)
 col.find_one(q)  ──> await ──> dict | None
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Collection | Group of documents (like a table) | Documents का समूह (table जैसा) |
| Cursor | Lazy stream of results | Results की lazy धारा |
| ObjectId | Default 12-byte unique id | Default unique id |
| Aggregation pipeline | Multi-stage data processing | कई चरणों वाली data processing |
| Index | Structure to speed up lookups | तेज़ खोज के लिए structure |
| Lazy connection | Connects on first operation | पहले operation पर connect होना |

---

## ⚡ 3-Line Summary
English: Motor gives awaitable MongoDB operations. Create one client, `await` single-document calls, and iterate cursors with `async for` or `to_list`. It is deprecated in favour of PyMongo's native async client, but still widely used.
Hindi: Motor MongoDB के operations को awaitable बनाता है। एक client बनाएं, single-document calls पर `await` लगाएं, और cursors को `async for` या `to_list` से पढ़ें। यह PyMongo के native async client के पक्ष में deprecated है, फिर भी बहुत इस्तेमाल होता है।

---

## ➡️ Next Topic
**250. Concurrent.futures Module** — one simple API (`ThreadPoolExecutor`, `ProcessPoolExecutor`) to run functions in parallel.
